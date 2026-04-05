"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";
import type {
  AgentStatusEvent,
  AnalyzeResponse,
  DebateEvent,
  DecisionEvent,
  GraphStepEvent,
  LlmUsageEvent,
  PipelineTopologyEvent,
  StreamState,
  StreamStatus,
  ToolCallRecord,
} from "@/lib/types";
import {
  assertAbsoluteBackendStreamUrl,
  backendStreamUrl,
} from "@/lib/publicBackend";

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
  llmUsages: [],
  tokenUsageTotals: {
    input_tokens: 0,
    output_tokens: 0,
    estimated_usd: null,
  },
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
    llmUsages: (payload.llmUsages as StreamState["llmUsages"]) || [],
    tokenUsageTotals: (payload.tokenUsageTotals as StreamState["tokenUsageTotals"]) ?? {
      input_tokens: 0,
      output_tokens: 0,
      estimated_usd: null,
    },
  };
}

/** Live snapshot from server (`stream_bootstrap`); maps backend `status` to StreamStatus. */
function serverSnapshotToStreamState(
  payload: Record<string, unknown>,
): StreamState {
  const raw = payload.status as string | undefined;
  let status: StreamStatus = "streaming";
  if (raw === "done") status = "done";
  else if (raw === "error") status = "error";
  return {
    status,
    agents: (payload.agents as StreamState["agents"]) || {},
    reports: (payload.reports as StreamState["reports"]) || {},
    debates: (payload.debates as StreamState["debates"]) || [],
    decision: (payload.decision as StreamState["decision"]) ?? null,
    traceId: (payload.traceId as string | null) ?? null,
    runId: (payload.runId as string | null) ?? null,
    sessionId: (payload.sessionId as string | null) ?? null,
    activityLog: [],
    error: (payload.error as string | null) ?? null,
    pipelineTopology:
      (payload.pipelineTopology as StreamState["pipelineTopology"]) ?? null,
    lastGraphStep:
      (payload.lastGraphStep as StreamState["lastGraphStep"]) ?? null,
    toolCalls: (payload.toolCalls as StreamState["toolCalls"]) || [],
    llmUsages: (payload.llmUsages as StreamState["llmUsages"]) || [],
    tokenUsageTotals: (payload.tokenUsageTotals as StreamState["tokenUsageTotals"]) ?? {
      input_tokens: 0,
      output_tokens: 0,
      estimated_usd: null,
    },
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
  const intentionalCloseRef = useRef(false);
  const reconnectAttemptRef = useRef(0);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(
    null,
  );
  const streamStatusRef = useRef<StreamStatus>("idle");
  const openEventSourceRef = useRef<(resume: boolean) => void>(() => {});

  const traceParam = searchParams.get("trace");
  const runParam = searchParams.get("run");

  useEffect(() => {
    streamStatusRef.current = state.status;
  }, [state.status]);

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

  const clearReconnectTimer = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
  }, []);

  const pushLog = useCallback((message: string) => {
    const entry = { at: new Date().toISOString(), message };
    setState((s) => ({
      ...s,
      activityLog: [...s.activityLog.slice(-49), entry],
    }));
  }, []);

  const reset = useCallback(() => {
    clearReconnectTimer();
    intentionalCloseRef.current = false;
    reconnectAttemptRef.current = 0;
    if (sourceRef.current) {
      sourceRef.current.close();
      sourceRef.current = null;
    }
    runIdRef.current = null;
    traceIdRef.current = null;
    setRestoredRunContext(null);
    setState(INITIAL_STATE);
  }, [clearReconnectTimer]);

  const openEventSource = useCallback(
    (resume: boolean) => {
      const runId = runIdRef.current;
      if (!runId) return;

      clearReconnectTimer();
      if (sourceRef.current) {
        sourceRef.current.close();
        sourceRef.current = null;
      }

      const streamUrl = backendStreamUrl(runId, { resume });
      assertAbsoluteBackendStreamUrl(streamUrl);
      const source = new EventSource(streamUrl);
      sourceRef.current = source;

      source.onopen = () => {
        reconnectAttemptRef.current = 0;
        setState((s) => ({
          ...s,
          status: "streaming",
          error: null,
        }));
      };

      source.addEventListener("stream_bootstrap", (e) => {
        const raw = JSON.parse((e as MessageEvent).data) as Record<
          string,
          unknown
        >;
        const merged = serverSnapshotToStreamState(raw);
        setState((s) => {
          const entry = {
            at: new Date().toISOString(),
            message: "Restored stream state (reconnect)",
          };
          return {
            ...merged,
            status:
              merged.status === "done" || merged.status === "error"
                ? merged.status
                : "streaming",
            activityLog: [...s.activityLog.slice(-49), entry],
            runId: merged.runId ?? s.runId,
            traceId: merged.traceId ?? s.traceId,
            sessionId: merged.sessionId ?? s.sessionId,
          };
        });
        if (merged.status === "done" || merged.status === "error") {
          intentionalCloseRef.current = true;
        }
        if (merged.status === "done") {
          const tid = merged.traceId || traceIdRef.current || "";
          if (tid) {
            router.replace(`/?trace=${encodeURIComponent(tid)}`, {
              scroll: false,
            });
          } else if (runIdRef.current) {
            router.replace(`/?run=${encodeURIComponent(runIdRef.current)}`, {
              scroll: false,
            });
          }
        }
      });

      source.addEventListener("agent_status", (e) => {
        const event: AgentStatusEvent = JSON.parse((e as MessageEvent).data);
        setState((s) => ({
          ...s,
          agents: { ...s.agents, [event.agent]: event.status },
        }));
        const ts = event.time ? ` @ ${event.time}` : "";
        pushLog(`${event.agent}: ${event.status}${ts}`);
      });

      source.addEventListener("pipeline_topology", (e) => {
        const event: PipelineTopologyEvent = JSON.parse(
          (e as MessageEvent).data,
        );
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

      source.addEventListener("llm_usage", (e) => {
        const ev: LlmUsageEvent = JSON.parse((e as MessageEvent).data);
        setState((s) => ({
          ...s,
          llmUsages: [...s.llmUsages, ev],
          tokenUsageTotals: {
            input_tokens: ev.run_input_tokens,
            output_tokens: ev.run_output_tokens,
            estimated_usd:
              ev.estimated_usd_run !== undefined && ev.estimated_usd_run !== null
                ? ev.estimated_usd_run
                : s.tokenUsageTotals.estimated_usd,
          },
        }));
        pushLog(
          `LLM +${ev.input_tokens} in / +${ev.output_tokens} out (${ev.agent})`,
        );
      });

      source.addEventListener("report", (e) => {
        const event = JSON.parse((e as MessageEvent).data);
        setState((s) => ({
          ...s,
          reports: { ...s.reports, [event.section]: event.content },
        }));
        pushLog(`Report: ${event.section}`);
      });

      source.addEventListener("debate", (e) => {
        const event: DebateEvent = JSON.parse((e as MessageEvent).data);
        setState((s) => ({
          ...s,
          debates: [...s.debates, event],
        }));
        pushLog(`Debate: ${event.speaker} (${event.phase})`);
      });

      source.addEventListener("decision", (e) => {
        const event: DecisionEvent = JSON.parse((e as MessageEvent).data);
        setState((s) => ({ ...s, decision: event }));
        pushLog("Decision received");
      });

      source.addEventListener("error", (e) => {
        if (e instanceof MessageEvent) {
          const event = JSON.parse((e as MessageEvent).data);
          setState((s) => ({ ...s, error: event.message }));
          pushLog(`Error: ${event.message}`);
        }
      });

      source.addEventListener("done", (e) => {
        clearReconnectTimer();
        intentionalCloseRef.current = true;
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
        if (intentionalCloseRef.current) return;
        const rid = runIdRef.current;
        if (!rid) return;
        if (sourceRef.current === source) {
          sourceRef.current = null;
        }
        source.close();

        if (streamStatusRef.current === "done" || intentionalCloseRef.current)
          return;

        setState((s) => {
          if (s.status === "done") return s;
          return {
            ...s,
            status: "error",
            error: s.error || "Connection lost",
          };
        });
        pushLog("Connection lost");

        const attempt = reconnectAttemptRef.current + 1;
        reconnectAttemptRef.current = attempt;
        const delay = Math.min(
          1000 * 2 ** Math.min(attempt - 1, 5),
          30_000,
        );
        pushLog(`Reconnecting in ${Math.round(delay / 1000)}s…`);
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectTimeoutRef.current = null;
          if (intentionalCloseRef.current) return;
          if (runIdRef.current !== rid) return;
          if (streamStatusRef.current === "done") return;
          openEventSourceRef.current(true);
        }, delay);
      };
    },
    [clearReconnectTimer, pushLog, router],
  );

  openEventSourceRef.current = openEventSource;

  useEffect(() => {
    const onVis = () => {
      if (document.visibilityState !== "visible") return;
      if (intentionalCloseRef.current) return;
      if (!runIdRef.current || sourceRef.current) return;
      if (streamStatusRef.current !== "error") return;
      pushLog("Reconnecting after wake…");
      openEventSourceRef.current(true);
    };
    const onOnline = () => {
      if (intentionalCloseRef.current) return;
      if (!runIdRef.current || sourceRef.current) return;
      if (streamStatusRef.current !== "error") return;
      pushLog("Network back; reconnecting…");
      openEventSourceRef.current(true);
    };
    document.addEventListener("visibilitychange", onVis);
    window.addEventListener("online", onOnline);
    return () => {
      document.removeEventListener("visibilitychange", onVis);
      window.removeEventListener("online", onOnline);
    };
  }, [pushLog]);

  useEffect(() => {
    return () => {
      clearReconnectTimer();
      intentionalCloseRef.current = true;
      sourceRef.current?.close();
    };
  }, [clearReconnectTimer]);

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

        openEventSource(false);
      } catch (err) {
        setState((s) => ({
          ...s,
          status: "error",
          error: err instanceof Error ? err.message : "Unknown error",
        }));
        pushLog("Failed to start analysis");
      }
    },
    [reset, pushLog, openEventSource],
  );

  const cancel = useCallback(() => {
    intentionalCloseRef.current = true;
    clearReconnectTimer();
    reconnectAttemptRef.current = 0;
    if (sourceRef.current) {
      sourceRef.current.close();
      sourceRef.current = null;
    }
    setState((s) => ({ ...s, status: "done" }));
  }, [clearReconnectTimer]);

  return {
    ...state,
    startAnalysis,
    cancel,
    reset,
    restoredRunContext,
  };
}
