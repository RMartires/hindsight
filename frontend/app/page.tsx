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
    startAnalysis,
    cancel,
  } = useAgentStream();

  const [draftTicker, setDraftTicker] = useState("");
  const [draftTradeDate, setDraftTradeDate] = useState("");
  const [selectedAnalystKeys, setSelectedAnalystKeys] =
    useState<PipelineAnalystKey[]>(DEFAULT_ANALYSTS);

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
            onCancel={cancel}
            onEngage={(ticker, date, analysts) =>
              startAnalysis(ticker, date, analysts)
            }
            onContextChange={(t, d) => {
              setDraftTicker(t);
              setDraftTradeDate(d);
            }}
          />

          <ActivePipeline
            agents={agents}
            status={status}
            selectedAnalystKeys={selectedAnalystKeys}
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
          />
        </div>
      </main>
    </>
  );
}
