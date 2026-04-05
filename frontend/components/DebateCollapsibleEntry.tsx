"use client";

import { useState } from "react";
import MarkdownContent from "./MarkdownContent";

interface Props {
  speakerHandle: string;
  timestamp: string;
  phase: string;
  content: string;
  isFundamental: boolean;
}

export default function DebateCollapsibleEntry({
  speakerHandle,
  timestamp,
  phase,
  content,
  isFundamental,
}: Props) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="report-card debate-collapsible">
      <button
        type="button"
        className="report-card-header debate-collapsible__header"
        onClick={() => setExpanded((e) => !e)}
        aria-expanded={expanded}
      >
        <span className="report-card-header-text">
          <span
            className={`debate-handle debate-collapsible__speaker ${isFundamental ? "debate-handle--fundamental" : ""}`}
          >
            {speakerHandle}
          </span>
          <span className="report-card-subtitle debate-collapsible__meta">
            [{timestamp}] · {phase}
          </span>
        </span>
        <span className="report-card-chevron" aria-hidden>
          {expanded ? "\u25B2" : "\u25BC"}
        </span>
      </button>
      {expanded && (
        <div className="report-card-body debate-collapsible__body">
          <div
            className={`debate-bubble ${phase === "investment" ? "debate-bubble--investment" : ""}`}
          >
            <MarkdownContent source={content} />
          </div>
        </div>
      )}
    </div>
  );
}
