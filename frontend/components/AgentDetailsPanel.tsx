"use client";

import { useEffect, useMemo, useState } from "react";
import type {
  ActivityLogEntry,
  AgentStatus,
  DebateEvent,
  DecisionEvent,
  LlmUsageEvent,
  TokenUsageTotals,
  ToolCallRecord,
} from "@/lib/types";
import type { StreamStatus } from "@/lib/types";
import type { PipelineAnalystKey } from "@/lib/pipelineGraph";
import { buildLiveTiles } from "@/lib/liveTiles";
import ReportCard from "./ReportCard";
import DecisionDisplay from "./DecisionDisplay";
import DebateCollapsibleEntry from "./DebateCollapsibleEntry";

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
  agents: Record<string, AgentStatus>;
  toolCalls: ToolCallRecord[];
  llmUsages: LlmUsageEvent[];
  tokenUsageTotals: TokenUsageTotals;
  selectedAnalystKeys: PipelineAnalystKey[];
  reports: Record<string, string>;
  debates: DebateEvent[];
  decision: DecisionEvent | null;
  error: string | null;
  focusedAgentId?: string | null;
  onClearFocus?: () => void;
  /** Sync tile header clicks with graph selection */
  onFocusTile?: (nodeId: string | null) => void;
}

export default function AgentDetailsPanel({
  status,
  runId,
  traceId,
  sessionId,
  activityLog,
  agents,
  toolCalls,
  llmUsages,
  tokenUsageTotals,
  selectedAnalystKeys,
  reports,
  debates,
  decision,
  error,
  focusedAgentId = null,
  onClearFocus,
  onFocusTile,
}: Props) {
  const [traceLinkUrl, setTraceLinkUrl] = useState<string | null>(null);
  const [traceLinkLoading, setTraceLinkLoading] = useState(false);

  const hasTrace = Boolean(traceId);

  const liveTiles = useMemo(
    () =>
      buildLiveTiles(
        agents,
        selectedAnalystKeys,
        toolCalls,
        reports,
        debates,
        decision,
        activityLog
      ),
    [
      agents,
      selectedAnalystKeys,
      toolCalls,
      reports,
      debates,
      decision,
      activityLog,
    ]
  );

  const handleTileHeader = (tileId: string) => {
    if (!onFocusTile) return;
    if (focusedAgentId === tileId) {
      onFocusTile(null);
    } else {
      onFocusTile(tileId);
    }
  };

  const filteredActivityLog = useMemo(() => {
    if (!focusedAgentId) return activityLog;
    return activityLog.filter(
      (e) =>
        e.message.includes(focusedAgentId) ||
        e.message.startsWith(`${focusedAgentId}:`)
    );
  }, [activityLog, focusedAgentId]);

  const focusedTokenTotals = useMemo(() => {
    if (!focusedAgentId) return null;
    let input = 0;
    let output = 0;
    let usd = 0;
    for (const u of llmUsages) {
      if (u.agent === focusedAgentId) {
        input += u.input_tokens;
        output += u.output_tokens;
        if (u.estimated_usd_delta != null) usd += u.estimated_usd_delta;
      }
    }
    return { input, output, usd: usd > 0 ? usd : null };
  }, [focusedAgentId, llmUsages]);

  const filteredDebates = useMemo(() => {
    if (!focusedAgentId) return debates;
    return debates.filter((d) => d.speaker === focusedAgentId);
  }, [debates, focusedAgentId]);

  const debateTimestamps = useMemo(
    () =>
      activityLog
        .filter((e) => e.message.startsWith("Debate:"))
        .map((e) => formatLogTime(e.at)),
    [activityLog]
  );

  const debateTimestampsFiltered = useMemo(
    () =>
      filteredDebates.map((d) => {
        const idx = debates.indexOf(d);
        return idx >= 0 ? debateTimestamps[idx] ?? "—" : "—";
      }),
    [filteredDebates, debates, debateTimestamps]
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
    <section className="panel panel--details-below" aria-label="Agent details">
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
          <div className="compute-cost-label">LLM usage (this run)</div>
          <div className="compute-cost-tokens">
            {tokenUsageTotals.input_tokens > 0 ||
            tokenUsageTotals.output_tokens > 0 ? (
              <>
                <span>{tokenUsageTotals.input_tokens.toLocaleString()} in</span>
                <span aria-hidden> · </span>
                <span>{tokenUsageTotals.output_tokens.toLocaleString()} out</span>
              </>
            ) : (
              <span className="compute-cost-muted">Waiting for token metadata…</span>
            )}
          </div>
          <div className="compute-cost-value">
            {tokenUsageTotals.estimated_usd != null ? (
              <>
                ~${tokenUsageTotals.estimated_usd.toFixed(4)}
                <span className="compute-cost-unit"> est.</span>
              </>
            ) : tokenUsageTotals.input_tokens > 0 ||
              tokenUsageTotals.output_tokens > 0 ? (
              <span className="compute-cost-muted" title="Set LLM_PRICE_INPUT_PER_1M_TOKENS and LLM_PRICE_OUTPUT_PER_1M_TOKENS in backend .env">
                Add LLM_PRICE_* for $ estimate
              </span>
            ) : null}
          </div>
          {focusedTokenTotals &&
            (focusedTokenTotals.input > 0 || focusedTokenTotals.output > 0) && (
              <div className="compute-cost-focus" title="Sum of LLM events attributed to the focused agent">
                <span className="compute-cost-focus-label">Focused</span>
                <span>
                  {focusedTokenTotals.input.toLocaleString()} in ·{" "}
                  {focusedTokenTotals.output.toLocaleString()} out
                  {focusedTokenTotals.usd != null
                    ? ` · ~$${focusedTokenTotals.usd.toFixed(4)}`
                    : ""}
                </span>
              </div>
            )}
        </div>

        {error && <div className="agent-error">Error: {error}</div>}

        {focusedAgentId && onClearFocus && (
          <div className="agent-focus-banner">
            <span className="agent-focus-label">Focused</span>
            <span className="agent-focus-name">{focusedAgentId}</span>
            <button
              type="button"
              className="agent-focus-clear"
              onClick={onClearFocus}
            >
              Clear
            </button>
          </div>
        )}

        <div className="agent-section">
          <h3 className="section-title section-title--sm">AGENT STATUS FEED</h3>
          <div className="activity-log">
            {(focusedAgentId ? filteredActivityLog : activityLog).length === 0 ? (
              <div className="activity-log-empty">
                {focusedAgentId ? "No feed lines for this agent yet." : "Waiting for events…"}
              </div>
            ) : (
              (focusedAgentId ? filteredActivityLog : activityLog)
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
            {liveTiles.length === 0 ? (
              <div className="activity-log-empty">
                No pipeline activity yet. Run analysis to populate tiles.
              </div>
            ) : (
              liveTiles.map((tile) => (
                <ReportCard
                  key={tile.id}
                  title={tile.title}
                  subtitle={tile.subtitle}
                  content={tile.body}
                  expanded={focusedAgentId === tile.id}
                  onHeaderClick={
                    onFocusTile ? () => handleTileHeader(tile.id) : undefined
                  }
                />
              ))
            )}
          </div>
        </div>

        {(focusedAgentId ? filteredDebates : debates).length > 0 && (
          <div className="agent-section">
            <h3 className="section-title section-title--sm">
              SYNTHESIS PHASE (DEBATE)
            </h3>
            <div className="debates-section agent-debates">
              {(focusedAgentId ? filteredDebates : debates).map((debate, i) => {
                const ts =
                  (focusedAgentId ? debateTimestampsFiltered : debateTimestamps)[i] ??
                  "—";
                const handle = speakerHandle(debate.speaker);
                const isFundamental =
                  /fundamental/i.test(debate.speaker) ||
                  /fundamental/i.test(debate.content);
                return (
                  <DebateCollapsibleEntry
                    key={`${debate.speaker}-${debate.phase}-${i}`}
                    speakerHandle={handle}
                    timestamp={ts}
                    phase={debate.phase}
                    content={debate.content}
                    isFundamental={isFundamental}
                  />
                );
              })}
            </div>
          </div>
        )}

        {decision &&
          (!focusedAgentId || focusedAgentId === "Risk Judge") && (
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
    </section>
  );
}
