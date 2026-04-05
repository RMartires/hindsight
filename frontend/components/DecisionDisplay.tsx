"use client";

import { useState } from "react";
import type { DecisionEvent } from "@/lib/types";
import MarkdownContent from "./MarkdownContent";

interface Props {
  decision: DecisionEvent | null;
  traceId: string | null;
}

function getDecisionColor(decision: string): string {
  const d = decision.toUpperCase().trim();
  if (d.includes("BUY")) return "var(--accent-blue)";
  if (d.includes("SELL")) return "var(--accent-red)";
  return "var(--accent-amber)";
}

function getDecisionLabel(decision: string): string {
  const d = decision.toUpperCase().trim();
  if (d.includes("BUY")) return "BUY";
  if (d.includes("SELL")) return "SELL";
  return "HOLD";
}

export default function DecisionDisplay({ decision, traceId }: Props) {
  const [expanded, setExpanded] = useState(true);

  if (!decision) return null;

  const color = getDecisionColor(decision.final);
  const label = getDecisionLabel(decision.final);

  return (
    <div className="report-card decision-display--collapsible">
      <button
        type="button"
        className="report-card-header decision-display__toggle"
        onClick={() => setExpanded((e) => !e)}
        aria-expanded={expanded}
      >
        <span className="report-card-header-text">
          <span
            className="decision-display__verdict-pill"
            style={{ color, textShadow: `0 0 12px ${color}55` }}
          >
            {label}
          </span>
          <span className="report-card-subtitle">Final decision rationale</span>
        </span>
        <span className="report-card-chevron" aria-hidden>
          {expanded ? "\u25B2" : "\u25BC"}
        </span>
      </button>
      {expanded && (
        <div className="report-card-body decision-display__body">
          <div
            className="decision-verdict decision-verdict--in-panel"
            style={{ color, textShadow: `0 0 30px ${color}40` }}
          >
            {label}
          </div>
          <div className="decision-reasoning">
            <MarkdownContent
              source={decision.full_text}
              className="report-content-md"
            />
          </div>
          {traceId && (
            <div className="decision-trace">
              <span className="trace-label">
                Trace ID: {traceId.slice(0, 12)}...
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
