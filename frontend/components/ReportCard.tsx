"use client";

interface Props {
  title: string;
  subtitle?: string;
  content: string;
  /** Controlled: matches focused graph node id */
  expanded: boolean;
  /** Header click: parent syncs selection with graph */
  onHeaderClick?: () => void;
}

export default function ReportCard({
  title,
  subtitle,
  content,
  expanded,
  onHeaderClick,
}: Props) {
  return (
    <div className="report-card">
      <button
        type="button"
        className="report-card-header"
        onClick={onHeaderClick}
        aria-expanded={expanded}
      >
        <span className="report-card-header-text">
          <span className="report-card-title">{title}</span>
          {subtitle ? (
            <span className="report-card-subtitle">{subtitle}</span>
          ) : null}
        </span>
        <span className="report-card-chevron" aria-hidden>
          {expanded ? "\u25B2" : "\u25BC"}
        </span>
      </button>
      {expanded && (
        <div className="report-card-body">
          <pre className="report-content">{content || "—"}</pre>
        </div>
      )}
    </div>
  );
}
