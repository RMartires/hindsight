"use client";

import { useAgentStream } from "@/hooks/useAgentStream";
import { useState } from "react";
import AppHeader from "@/components/AppHeader";
import LeftRail from "@/components/LeftRail";
import ActivePipeline from "@/components/ActivePipeline";
import AgentDetailsPanel from "@/components/AgentDetailsPanel";

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
            onCancel={cancel}
            onEngage={(ticker, date, analysts) =>
              startAnalysis(ticker, date, analysts)
            }
            onContextChange={(t, d) => {
              setDraftTicker(t);
              setDraftTradeDate(d);
            }}
          />

          <ActivePipeline agents={agents} status={status} />

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
