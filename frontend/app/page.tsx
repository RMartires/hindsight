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
import { DEFAULT_HOME_PRESET } from "@/lib/presets";

/** Full analyst set for every run (sidebar selector removed). */
const ALL_ANALYSTS: PipelineAnalystKey[] = [...ANALYST_ORDER];

function MobileBackChevron() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
      <path d="M15 18l-6-6 6-6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

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
    llmUsages,
    tokenUsageTotals,
    startAnalysis,
    cancel,
    restoredRunContext,
  } = useAgentStream();

  const [draftTicker, setDraftTicker] = useState(DEFAULT_HOME_PRESET.ticker);
  const [draftTradeDate, setDraftTradeDate] = useState(
    DEFAULT_HOME_PRESET.date
  );
  const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);
  const [mobileStep, setMobileStep] = useState<"engine" | "pipeline">("engine");
  const [pipelineRefitSignal, setPipelineRefitSignal] = useState(0);

  useEffect(() => {
    if (restoredRunContext) {
      setDraftTicker(restoredRunContext.ticker);
      setDraftTradeDate(restoredRunContext.tradeDate);
      setMobileStep("pipeline");
    }
  }, [restoredRunContext]);

  useEffect(() => {
    if (mobileStep === "pipeline") {
      setPipelineRefitSignal((n) => n + 1);
    }
  }, [mobileStep]);

  const dashboardGridClass =
    mobileStep === "engine"
      ? "dashboard-grid dashboard-grid--mobile-engine"
      : "dashboard-grid dashboard-grid--mobile-pipeline";

  return (
    <>
      <AppHeader tradeDate={draftTradeDate} ticker={draftTicker} />

      <main className="main">
        <div className={dashboardGridClass}>
          <LeftRail
            status={status}
            onCancel={() => {
              setSelectedAgentId(null);
              cancel();
            }}
            onEngage={(ticker, date) => {
              setSelectedAgentId(null);
              setMobileStep("pipeline");
              startAnalysis(ticker, date, ALL_ANALYSTS);
            }}
            onContextChange={(t, d) => {
              setDraftTicker(t);
              setDraftTradeDate(d);
            }}
          />

          <div className="dashboard-main-column">
            <div className="mobile-pipeline-back">
              <button
                type="button"
                className="mobile-pipeline-back-button"
                onClick={() => {
                  setSelectedAgentId(null);
                  setMobileStep("engine");
                }}
                aria-label="Back to Temporal Market Engine"
              >
                <MobileBackChevron />
                <span>Temporal Engine</span>
              </button>
            </div>
            <ActivePipeline
              agents={agents}
              status={status}
              selectedAnalystKeys={ALL_ANALYSTS}
              pipelineTopology={pipelineTopology}
              selectedAgentId={selectedAgentId}
              onSelectAgent={setSelectedAgentId}
              toolCalls={toolCalls}
              refitSignal={pipelineRefitSignal}
            />

            <AgentDetailsPanel
              status={status}
              runId={runId}
              traceId={traceId}
              sessionId={sessionId}
              activityLog={activityLog}
              agents={agents}
              toolCalls={toolCalls}
              llmUsages={llmUsages}
              tokenUsageTotals={tokenUsageTotals}
              selectedAnalystKeys={ALL_ANALYSTS}
              reports={reports}
              debates={debates}
              decision={decision}
              error={error}
              focusedAgentId={selectedAgentId}
              onClearFocus={() => setSelectedAgentId(null)}
              onFocusTile={setSelectedAgentId}
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
