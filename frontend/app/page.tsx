"use client";

import { useAgentStream } from "@/hooks/useAgentStream";
import ControlDeck from "@/components/ControlDeck";
import AgentFlowchart from "@/components/AgentFlowchart";
import ReportCard from "@/components/ReportCard";
import DecisionDisplay from "@/components/DecisionDisplay";
import ThoughtTrace from "@/components/ThoughtTrace";

const REPORT_LABELS: Record<string, string> = {
  market_report: "Market Analysis",
  fundamentals_report: "Fundamentals Analysis",
  news_report: "News Analysis",
  sentiment_report: "Social Sentiment",
  trader_investment_plan: "Trader Plan",
};

export default function Home() {
  const {
    status,
    agents,
    reports,
    debates,
    decision,
    traceId,
    error,
    startAnalysis,
    cancel,
  } = useAgentStream();

  const isActive = status !== "idle";

  return (
    <>
      <header className="header">
        <span className="header-title">HINDSIGHT 20/20</span>
        <span className="header-subtitle">
          Retro-Temporal Market Analysis Engine
        </span>
      </header>

      <main className="main">
        {/* Control Deck */}
        <ControlDeck
          status={status}
          onEngage={(ticker, date) => startAnalysis(ticker, date)}
          onCancel={cancel}
        />

        {/* Status */}
        {status === "connecting" && (
          <div className="status-bar status-bar--streaming">
            <span className="spinner" />
            Initializing agents...
          </div>
        )}
        {status === "streaming" && (
          <div className="status-bar status-bar--streaming">
            <span className="spinner" />
            Analysis in progress...
          </div>
        )}
        {error && (
          <div className="status-bar status-bar--error">Error: {error}</div>
        )}

        {/* Agent Flowchart */}
        {isActive && <AgentFlowchart agents={agents} />}

        {/* Reports */}
        {isActive && Object.keys(reports).length > 0 && (
          <div className="reports-section">
            <h3 className="section-title">Analysis Reports</h3>
            {Object.entries(reports).map(([key, content]) => (
              <ReportCard
                key={key}
                title={REPORT_LABELS[key] || key}
                content={content}
              />
            ))}
          </div>
        )}

        {/* Debates */}
        {isActive && debates.length > 0 && (
          <div className="debates-section">
            <h3 className="section-title">Agent Debates</h3>
            {debates.map((debate, i) => (
              <div key={i} className="debate-entry">
                <div className="debate-speaker">
                  {debate.speaker} ({debate.phase})
                </div>
                <div className="debate-content">{debate.content}</div>
              </div>
            ))}
          </div>
        )}

        {/* Decision */}
        {decision && (
          <DecisionDisplay decision={decision} traceId={traceId} />
        )}

        {/* Langfuse Thought Trace */}
        {status === "done" && traceId && <ThoughtTrace traceId={traceId} />}
      </main>
    </>
  );
}
