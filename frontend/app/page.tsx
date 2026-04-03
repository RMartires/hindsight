"use client";

import { useAgentStream } from "@/hooks/useAgentStream";
import { Suspense, useEffect, useState } from "react";
import AppHeader from "@/components/AppHeader";
import LeftRail from "@/components/LeftRail";
import ActivePipeline from "@/components/ActivePipeline";
import AgentDetailsPanel from "@/components/AgentDetailsPanel";
import {
  ANALYST_ORDER,
  type PipelineAnalystKey,
} from "@/lib/pipelineGraph";

/** Full analyst set for every run (sidebar selector removed). */
const ALL_ANALYSTS: PipelineAnalystKey[] = [...ANALYST_ORDER];

function HomeDashboard() {
  const {
    status,
    agents,
    reports,
    debates,
    decision,
    traceId,
    runId,
    sessionId,
    activityLog,
    error,
    pipelineTopology,
    toolCalls,
    startAnalysis,
    cancel,
    restoredRunContext,
  } = useAgentStream();

  const [draftTicker, setDraftTicker] = useState("");
  const [draftTradeDate, setDraftTradeDate] = useState("");
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);

  useEffect(() => {
    if (restoredRunContext) {
      setDraftTicker(restoredRunContext.ticker);
      setDraftTradeDate(restoredRunContext.tradeDate);
    }
  }, [restoredRunContext]);

  return (
    <>
      <AppHeader
        status={status}
        tradeDate={draftTradeDate}
        ticker={draftTicker}
      />

      <main className="main">
        <div className="dashboard-grid">
          <LeftRail
            status={status}
            onCancel={() => {
              setSelectedAgentId(null);
              cancel();
            }}
            onEngage={(ticker, date) => {
              setSelectedAgentId(null);
              startAnalysis(ticker, date, ALL_ANALYSTS);
            }}
            onContextChange={(t, d) => {
              setDraftTicker(t);
              setDraftTradeDate(d);
            }}
          />

          <div className="dashboard-main-column">
            <ActivePipeline
              agents={agents}
              status={status}
              selectedAnalystKeys={ALL_ANALYSTS}
              pipelineTopology={pipelineTopology}
              selectedAgentId={selectedAgentId}
              onSelectAgent={setSelectedAgentId}
              toolCalls={toolCalls}
            />

            <AgentDetailsPanel
              status={status}
              runId={runId}
              traceId={traceId}
              sessionId={sessionId}
              activityLog={activityLog}
              reports={reports}
              debates={debates}
              decision={decision}
              error={error}
              focusedAgentId={selectedAgentId}
              onClearFocus={() => setSelectedAgentId(null)}
            />
          </div>
        </div>
      </main>
    </>
  );
}

export default function Home() {
  return (
    <Suspense fallback={null}>
      <HomeDashboard />
    </Suspense>
  );
}
