"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import type {
  AgentStatusEvent,
  AnalyzeResponse,
  DebateEvent,
  DecisionEvent,
  GraphStepEvent,
  PipelineTopologyEvent,
  StreamState,
  ToolCallRecord,
} from "@/lib/types";
import { backendStreamUrl } from "@/lib/publicBackend";

const INITIAL_STATE: StreamState = {
  status: "idle",
  agents: {},
  reports: {},
  debates: [],
  decision: null,
  traceId: null,
  runId: null,
  sessionId: null,
  activityLog: [],
  error: null,
  pipelineTopology: null,
  lastGraphStep: null,
  toolCalls: [],
};

interface RunSnapshotApi {
  hit: boolean;
  status?: string;
  payload?: Record<string, unknown>;
  ticker?: string | null;
  trade_date?: string | null;
}

function payloadToStreamState(payload: Record<string, unknown>): StreamState {
  return {
    status: "done",
    agents: (payload.agents as StreamState["agents"]) || {},
    reports: (payload.reports as StreamState["reports"]) || {},
    debates: (payload.debates as StreamState["debates"]) || [],
    decision: (payload.decision as StreamState["decision"]) ?? null,
    traceId: (payload.traceId as string | null) ?? null,
    runId: (payload.runId as string | null) ?? null,
    sessionId: (payload.sessionId as string | null) ?? null,
    activityLog: (payload.activityLog as StreamState["activityLog"]) || [],
    error: (payload.error as string | null) ?? null,
    pipelineTopology:
      (payload.pipelineTopology as StreamState["pipelineTopology"]) ?? null,
    lastGraphStep:
      (payload.lastGraphStep as StreamState["lastGraphStep"]) ?? null,
    toolCalls: (payload.toolCalls as StreamState["toolCalls"]) || [],
  };
}

export function useAgentStream() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [state, setState] = useState<StreamState>(INITIAL_STATE);
  const [restoredRunContext, setRestoredRunContext] = useState<{
    ticker: string;
    tradeDate: string;
  } | null>(null);
  const sourceRef = useRef<EventSource | null>(null);
  const runIdRef = useRef<string | null>(null);
  const traceIdRef = useRef<string | null>(null);

  const traceParam = searchParams.get("trace");
  const runParam = searchParams.get("run");

  useEffect(() => {
    if (!traceParam && !runParam) return;

    let cancelled = false;
    (async () => {
      try {
        const q = traceParam
          ? `trace_id=${encodeURIComponent(traceParam)}`
          : `run_id=${encodeURIComponent(runParam!)}`;
        const res = await fetch(`/api/run-snapshot?${q}`);
        if (!res.ok || cancelled) return;
        const data = (await res.json()) as RunSnapshotApi;
        if (
          cancelled ||
          !data.hit ||
          data.status !== "completed" ||
          !data.payload
        ) {
          return;
        }
        const payload = data.payload;
        setState(() => {
          const base = payloadToStreamState(payload);
          const entry = {
            at: new Date().toISOString(),
            message: "Restored completed run from cache",
          };
          return {
            ...base,
            activityLog: [...base.activityLog.slice(-49), entry],
          };
        });
        if (data.ticker != null && data.trade_date != null) {
          setRestoredRunContext({
            ticker: data.ticker,
            tradeDate: data.trade_date,
          });
        }
      } catch {
        /* normal flow */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [traceParam, runParam]);

  const reset = useCallback(() => {
    if (sourceRef.current) {
      sourceRef.current.close();
      sourceRef.current = null;
    }
    runIdRef.current = null;
    traceIdRef.current = null;
    setRestoredRunContext(null);
    setState(INITIAL_STATE);
  }, []);

  const pushLog = useCallback((message: string) => {
    const entry = { at: new Date().toISOString(), message };
    setState((s) => ({
      ...s,
      activityLog: [...s.activityLog.slice(-49), entry],
    }));
  }, []);

  const startAnalysis = useCallback(
    async (ticker: string, tradeDate: string, analysts?: string[]) => {
      reset();
      setState((s) => ({ ...s, status: "connecting" }));

      try {
        const res = await fetch("/api/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            ticker: ticker.toUpperCase(),
            trade_date: tradeDate,
            analysts: analysts || [
              "market",
              "fundamentals",
              "news",
              "social",
            ],
          }),
        });

        if (!res.ok) {
          throw new Error(`API error: ${res.status}`);
        }

        const data: AnalyzeResponse = await res.json();
        traceIdRef.current = data.trace_id ?? null;
        runIdRef.current = data.run_id;

        setState((s) => ({
          ...s,
          status: "streaming",
          traceId: data.trace_id,
          runId: data.run_id,
          sessionId: data.session_id,
        }));

        pushLog("Started analysis");

        const source = new EventSource(backendStreamUrl(data.run_id));
        sourceRef.current = source;

        source.addEventListener("agent_status", (e) => {
          const event: AgentStatusEvent = JSON.parse(e.data);
          setState((s) => ({
            ...s,
            agents: { ...s.agents, [event.agent]: event.status },
          }));
          const ts = event.time ? ` @ ${event.time}` : "";
          pushLog(`${event.agent}: ${event.status}${ts}`);
        });

        source.addEventListener("pipeline_topology", (e) => {
          const event: PipelineTopologyEvent = JSON.parse((e as MessageEvent).data);
          setState((s) => ({
            ...s,
            pipelineTopology: event,
          }));
          const ec = event.edges?.length ?? 0;
          pushLog(`Pipeline topology (${event.source}, ${ec} edges)`);
        });

        source.addEventListener("graph_step", (e) => {
          const event: GraphStepEvent = JSON.parse((e as MessageEvent).data);
          setState((s) => ({ ...s, lastGraphStep: event }));
        });

        source.addEventListener("tool_call", (e) => {
          const ev: ToolCallRecord = JSON.parse((e as MessageEvent).data);
          setState((s) => ({
            ...s,
            toolCalls: [...s.toolCalls, ev],
          }));
          pushLog(`Tool ${ev.tool_name} (${ev.agent})`);
        });

        source.addEventListener("report", (e) => {
          const event = JSON.parse(e.data);
          setState((s) => ({
            ...s,
            reports: { ...s.reports, [event.section]: event.content },
          }));
          pushLog(`Report: ${event.section}`);
        });

        source.addEventListener("debate", (e) => {
          const event: DebateEvent = JSON.parse(e.data);
          setState((s) => ({
            ...s,
            debates: [...s.debates, event],
          }));
          pushLog(`Debate: ${event.speaker} (${event.phase})`);
        });

        source.addEventListener("decision", (e) => {
          const event: DecisionEvent = JSON.parse(e.data);
          setState((s) => ({ ...s, decision: event }));
          pushLog("Decision received");
        });

        source.addEventListener("error", (e) => {
          if (e instanceof MessageEvent) {
            const event = JSON.parse(e.data);
            setState((s) => ({ ...s, error: event.message }));
            pushLog(`Error: ${event.message}`);
          }
        });

        source.addEventListener("done", (e) => {
          const event = JSON.parse((e as MessageEvent).data) as {
            trace_id?: string;
          };
          const tid = event.trace_id || traceIdRef.current || "";
          if (tid) {
            router.replace(`/?trace=${encodeURIComponent(tid)}`, {
              scroll: false,
            });
          } else if (runIdRef.current) {
            router.replace(`/?run=${encodeURIComponent(runIdRef.current)}`, {
              scroll: false,
            });
          }
          setState((s) => ({
            ...s,
            status: "done",
            traceId: event.trace_id || s.traceId,
          }));
          pushLog("Stream done");
          source.close();
          sourceRef.current = null;
        });

        source.onerror = () => {
          setState((s) => ({
            ...s,
            status: "error",
            error: s.error || "Connection lost",
          }));
          pushLog("Connection lost");
          source.close();
          sourceRef.current = null;
        };
      } catch (err) {
        setState((s) => ({
          ...s,
          status: "error",
          error: err instanceof Error ? err.message : "Unknown error",
        }));
        pushLog("Failed to start analysis");
      }
    },
    [reset, pushLog, router]
  );

  const cancel = useCallback(() => {
    if (sourceRef.current) {
      sourceRef.current.close();
      sourceRef.current = null;
    }
    setState((s) => ({ ...s, status: "done" }));
  }, []);

  return {
    ...state,
    startAnalysis,
    cancel,
    reset,
    restoredRunContext,
  };
}
