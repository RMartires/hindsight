"use client";

import { useEffect, useMemo, useState } from "react";
import type {
  ActivityLogEntry,
  DebateEvent,
  DecisionEvent,
} from "@/lib/types";
import type { StreamStatus } from "@/lib/types";
import ReportCard from "./ReportCard";
import DecisionDisplay from "./DecisionDisplay";

const REPORT_LABELS: Record<string, string> = {
  market_report: "Market Analysis",
  fundamentals_report: "Fundamentals Analysis",
  news_report: "News Analysis",
  sentiment_report: "Social Sentiment",
  trader_investment_plan: "Trader Plan",
};


function truncateId(id: string): string {
  if (id.length <= 12) return id;
  return `${id.slice(0, 8)}…${id.slice(-4)}`;
}

function speakerHandle(speaker: string): string {
  const slug = speaker.replace(/\s+/g, "_");
  return `@${slug}`;
}

function formatLogTime(iso: string): string {
  const t = iso.split("T")[1]?.split(".")[0] ?? iso;
  return t;
}

interface Props {
  status: StreamStatus;
  runId: string | null;
  traceId: string | null;
  sessionId: string | null;
  activityLog: ActivityLogEntry[];
  reports: Record<string, string>;
  debates: DebateEvent[];
  decision: DecisionEvent | null;
  error: string | null;
}

export default function AgentDetailsPanel({
  status,
  runId,
  traceId,
  sessionId,
  activityLog,
  reports,
  debates,
  decision,
  error,
}: Props) {
  const [traceLinkUrl, setTraceLinkUrl] = useState<string | null>(null);
  const [traceLinkLoading, setTraceLinkLoading] = useState(false);

  const hasTrace = Boolean(traceId);

  const reportEntries = useMemo(
    () => Object.entries(reports),
    [reports]
  );

  const debateTimestamps = useMemo(
    () =>
      activityLog
        .filter((e) => e.message.startsWith("Debate:"))
        .map((e) => formatLogTime(e.at)),
    [activityLog]
  );

  const online =
    status !== "error" &&
    (status === "streaming" ||
      status === "connecting" ||
      status === "done" ||
      status === "idle");

  useEffect(() => {
    setTraceLinkUrl(null);
  }, [traceId]);

  const handleViewExternalTrace = async () => {
    if (!traceId) return;
    setTraceLinkLoading(true);
    try {
      const res = await fetch(`/api/trace/${traceId}/link`);
      const data = await res.json();
      if (data?.url) setTraceLinkUrl(data.url);
      if (data?.url) window.open(data.url, "_blank", "noopener,noreferrer");
    } catch {
      // ignore
    } finally {
      setTraceLinkLoading(false);
    }
  };

  return (
    <aside className="panel panel--right">
      <div className="agent-details-inner">
        <div className="agent-title-row">
          <div className="agent-title">Agent Details</div>
          <span
            className={`agent-online-badge ${online ? "" : "agent-online-badge--off"}`}
          >
            {online ? "● ONLINE" : "● OFFLINE"}
          </span>
        </div>

        <div className="meta-block">
          <div className="meta-row">
            <span className="meta-label">RUN</span>
            <span className="meta-value">{runId ? truncateId(runId) : "--"}</span>
          </div>
          <div className="meta-row">
            <span className="meta-label">TRACE</span>
            <span className="meta-value">{traceId ? truncateId(traceId) : "--"}</span>
          </div>
          <div className="meta-row">
            <span className="meta-label">SESS</span>
            <span className="meta-value">
              {sessionId ? truncateId(sessionId) : "--"}
            </span>
          </div>
        </div>

        <div className="compute-cost-card">
          <div className="compute-cost-label">Compute cost</div>
          <div className="compute-cost-value">
            $0.042
            <span className="compute-cost-unit">/run</span>
          </div>
        </div>

        {error && <div className="agent-error">Error: {error}</div>}

        <div className="agent-section">
          <h3 className="section-title section-title--sm">AGENT STATUS FEED</h3>
          <div className="activity-log">
            {activityLog.length === 0 ? (
              <div className="activity-log-empty">Waiting for events…</div>
            ) : (
              activityLog
                .slice()
                .reverse()
                .slice(0, 12)
                .map((entry, idx) => (
                  <div key={`${entry.at}-${idx}`} className="activity-log-entry">
                    <span className="activity-log-bullet" aria-hidden>
                      ●
                    </span>
                    <span className="activity-log-time">
                      {formatLogTime(entry.at)}
                    </span>
                    <span className="activity-log-msg">{entry.message}</span>
                  </div>
                ))
            )}
          </div>
        </div>

        <div className="agent-section">
          <h3 className="section-title section-title--sm">LIVE REPORT</h3>
          <div className="reports-section">
            {reportEntries.length === 0 ? (
              <div className="activity-log-empty">No reports yet.</div>
            ) : (
              reportEntries.map(([key, content]) => (
                <ReportCard
                  key={key}
                  title={REPORT_LABELS[key] || key}
                  content={content}
                />
              ))
            )}
          </div>
        </div>

        {debates.length > 0 && (
          <div className="agent-section">
            <h3 className="section-title section-title--sm">
              SYNTHESIS PHASE (DEBATE)
            </h3>
            <div className="debates-section agent-debates">
              {debates.map((debate, i) => {
                const ts = debateTimestamps[i] ?? "—";
                const handle = speakerHandle(debate.speaker);
                const isFundamental =
                  /fundamental/i.test(debate.speaker) ||
                  /fundamental/i.test(debate.content);
                return (
                  <div key={`${debate.speaker}-${i}`} className="debate-entry">
                    <div className="debate-entry-header">
                      <span
                        className={`debate-handle ${isFundamental ? "debate-handle--fundamental" : ""}`}
                      >
                        {handle}
                      </span>
                      <span className="debate-timestamp">[{ts}]</span>
                    </div>
                    <div
                      className={`debate-bubble ${debate.phase === "investment" ? "debate-bubble--investment" : ""}`}
                    >
                      {debate.content}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {decision && (
          <div className="agent-section">
            <h3 className="section-title section-title--sm">FINAL DECISION</h3>
            <DecisionDisplay decision={decision} traceId={traceId} />
          </div>
        )}

        <div className="agent-section">
          <h3 className="section-title section-title--sm">EXTERNAL TRACE</h3>
          <div className="external-trace-actions">
            <button
              type="button"
              className={`external-trace-button ${hasTrace ? "" : "external-trace-button--disabled"}`}
              onClick={handleViewExternalTrace}
              disabled={!hasTrace || traceLinkLoading || status === "connecting"}
            >
              <span className="external-trace-icon" aria-hidden>
                ↗
              </span>
              {traceLinkLoading ? "LOADING…" : "VIEW EXTERNAL TRACE"}
            </button>
            {traceLinkUrl && (
              <div className="external-trace-hint">Opened in a new tab.</div>
            )}
          </div>
        </div>
      </div>
    </aside>
  );
}
