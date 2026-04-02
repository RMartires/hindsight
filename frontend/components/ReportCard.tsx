"use client";

import { useState } from "react";

interface Props {
  title: string;
  content: string;
}

export default function ReportCard({ title, content }: Props) {
  const [expanded, setExpanded] = useState(false);

  if (!content) return null;

  return (
    <div className="report-card">
      <button
        className="report-card-header"
        onClick={() => setExpanded(!expanded)}
      >
        <span className="report-card-title">{title}</span>
        <span className="report-card-chevron">
          {expanded ? "\u25B2" : "\u25BC"}
        </span>
      </button>
      {expanded && (
        <div className="report-card-body">
          <pre className="report-content">{content}</pre>
        </div>
      )}
    </div>
  );
}
