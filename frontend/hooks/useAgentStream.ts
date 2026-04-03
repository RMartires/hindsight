"use client";

import { useCallback, useRef, useState } from "react";
import type {
  AgentStatusEvent,
  AnalyzeResponse,
  DebateEvent,
  DecisionEvent,
  StreamState,
} from "@/lib/types";

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
};

export function useAgentStream() {
  const [state, setState] = useState<StreamState>(INITIAL_STATE);
  const sourceRef = useRef<EventSource | null>(null);

  const reset = useCallback(() => {
    if (sourceRef.current) {
      sourceRef.current.close();
      sourceRef.current = null;
    }
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

        setState((s) => ({
          ...s,
          status: "streaming",
          traceId: data.trace_id,
          runId: data.run_id,
          sessionId: data.session_id,
        }));

        pushLog("Started analysis");

        const source = new EventSource(`/api/stream/${data.run_id}`);
        sourceRef.current = source;

        source.addEventListener("agent_status", (e) => {
          const event: AgentStatusEvent = JSON.parse(e.data);
          setState((s) => ({
            ...s,
            agents: { ...s.agents, [event.agent]: event.status },
          }));
          pushLog(`${event.agent}: ${event.status}`);
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
          const event = JSON.parse((e as MessageEvent).data);
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
    [reset, pushLog]
  );

  const cancel = useCallback(() => {
    if (sourceRef.current) {
      sourceRef.current.close();
      sourceRef.current = null;
    }
    setState((s) => ({ ...s, status: "done" }));
  }, []);

  return { ...state, startAnalysis, cancel, reset };
}
