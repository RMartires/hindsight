"use client";

import { useAgentStream } from "@/hooks/useAgentStream";
import { useState } from "react";
import AppHeader from "@/components/AppHeader";
import LeftRail from "@/components/LeftRail";
import ActivePipeline from "@/components/ActivePipeline";
import AgentDetailsPanel from "@/components/AgentDetailsPanel";
import {
  ANALYST_ORDER,
  type PipelineAnalystKey,
} from "@/lib/pipelineGraph";

const DEFAULT_ANALYSTS = () =>
  [...ANALYST_ORDER] as PipelineAnalystKey[];

export default function Home() {
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
    startAnalysis,
    cancel,
  } = useAgentStream();

  const [draftTicker, setDraftTicker] = useState("");
  const [draftTradeDate, setDraftTradeDate] = useState("");
  const [selectedAnalystKeys, setSelectedAnalystKeys] =
    useState<PipelineAnalystKey[]>(DEFAULT_ANALYSTS);
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);

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
            selectedAnalystKeys={selectedAnalystKeys}
            onSelectedAnalystKeysChange={setSelectedAnalystKeys}
            onCancel={() => {
              setSelectedAgentId(null);
              cancel();
            }}
            onEngage={(ticker, date, analysts) => {
              setSelectedAgentId(null);
              startAnalysis(ticker, date, analysts);
            }}
            onContextChange={(t, d) => {
              setDraftTicker(t);
              setDraftTradeDate(d);
            }}
          />

          <ActivePipeline
            agents={agents}
            status={status}
            selectedAnalystKeys={selectedAnalystKeys}
            pipelineTopology={pipelineTopology}
            selectedAgentId={selectedAgentId}
            onSelectAgent={setSelectedAgentId}
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
      </main>
    </>
  );
}
