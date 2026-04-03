"use client";

import type { StreamStatus } from "@/lib/types";

interface Props {
  status: StreamStatus;
  tradeDate: string;
  ticker: string;
}

function formatHeaderDate(dateStr: string): string {
  if (!dateStr) return "SELECT DATE";
  const parts = dateStr.split("-");
  if (parts.length !== 3) return dateStr.toUpperCase();
  const [yyyy, mm, dd] = parts;
  const monthNames = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
  ];
  const monthIndex = Number(mm) - 1;
  const day = Number(dd);
  const year = Number(yyyy);
  if (!Number.isFinite(monthIndex) || !monthNames[monthIndex]) return dateStr;
  return `${monthNames[monthIndex].toUpperCase()} ${day}, ${year}`;
}

function HeaderSettingsIcon() {
  return (
    <svg
      className="header-settings-icon"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="currentColor"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <path d="M19.14 12.94c.04-.31.06-.63.06-.94 0-.31-.02-.63-.06-.94l2.03-1.58c.18-.14.23-.41.12-.64l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94L14.4 2.81a.506.506 0 00-.5-.44h-3.8c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.23-.07.5.12.64l2.03 1.58c-.05.31-.09.63-.09.94s.02.63.07.93l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z" />
    </svg>
  );
}

export default function AppHeader({ status, tradeDate, ticker }: Props) {
  const dateLabel = formatHeaderDate(tradeDate);
  const pipelineActive = status !== "idle";

  return (
    <header className="header">
      <div className="header-left">
        <span className="header-title">HINDSIGHT 20/20</span>
        <span className="header-subtitle">
          Retro-Temporal Market Analysis Engine
        </span>
      </div>

      <nav className="header-nav header-nav--center" aria-label="Primary">
        <button
          type="button"
          className={`header-nav-link ${!pipelineActive ? "header-nav-link--active" : ""}`}
        >
          Dashboard
        </button>
        <button
          type="button"
          className={`header-nav-link ${pipelineActive ? "header-nav-link--active" : ""}`}
        >
          Active Pipeline
        </button>
      </nav>

      <div className="header-right">
        <div
          className="header-date-pill"
          title={ticker ? `${ticker} · ${tradeDate}` : undefined}
        >
          <span className="header-date-dot" aria-hidden />
          <span>
            {tradeDate ? dateLabel : "SELECT COORDINATES"}
            {ticker ? ` · ${ticker.toUpperCase()}` : ""}
          </span>
          <span className="header-date-chevron" aria-hidden>
            ▾
          </span>
        </div>
        <span className="header-settings" title="Chronograph" aria-hidden>
          <HeaderSettingsIcon />
        </span>
      </div>
    </header>
  );
}
