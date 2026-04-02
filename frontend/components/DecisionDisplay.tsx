"use client";

import type { DecisionEvent } from "@/lib/types";

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
  if (!decision) return null;

  const color = getDecisionColor(decision.final);
  const label = getDecisionLabel(decision.final);

  return (
    <div className="decision-display">
      <div className="decision-verdict" style={{ color, textShadow: `0 0 30px ${color}40` }}>
        {label}
      </div>
      <div className="decision-reasoning">
        <pre className="report-content">{decision.full_text}</pre>
      </div>
      {traceId && (
        <div className="decision-trace">
          <span className="trace-label">Trace ID: {traceId.slice(0, 12)}...</span>
        </div>
      )}
    </div>
  );
}
