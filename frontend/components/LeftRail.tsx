"use client";

import { useMemo, useState } from "react";
import DateDial from "./DateDial";
import TickerInput from "./TickerInput";
import type { StreamStatus } from "@/lib/types";
import { useBackendHealth } from "@/hooks/useBackendHealth";

type AnalystKey = "market" | "fundamentals" | "news" | "social";

interface Props {
  status: StreamStatus;
  onEngage: (ticker: string, date: string, analysts: AnalystKey[]) => void;
  onCancel: () => void;
  onContextChange?: (ticker: string, date: string) => void;
}

const ANALYST_OPTIONS: Array<{
 key: AnalystKey;
 label: string;
 icon: string;
}> = [
  { key: "market", label: "Market Analyst", icon: "◉" },
  { key: "fundamentals", label: "Fundamental", icon: "◇" },
  { key: "news", label: "Technical", icon: "◎" },
  { key: "social", label: "Sentiment", icon: "○" },
];

function LightningIcon() {
  return (
    <svg
      className="engage-button-icon-svg"
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="currentColor"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <path d="M11 21l1-8.5L7 10l10.5-9L17 9l5.5 4.5L11 21z" />
    </svg>
  );
}

export default function LeftRail({
  status,
  onEngage,
  onCancel,
  onContextChange,
}: Props) {
  const [date, setDate] = useState("");
  const [ticker, setTicker] = useState("");

  const [selected, setSelected] = useState<Record<AnalystKey, boolean>>({
    market: true,
    fundamentals: true,
    news: true,
    social: true,
  });

  const isRunning = status === "connecting" || status === "streaming";

  const selectedAnalysts = useMemo(
    () => ANALYST_OPTIONS.filter((o) => selected[o.key]).map((o) => o.key),
    [selected]
  );

  const health = useBackendHealth(15000);
  const healthy = health.status === "ok" && !health.error;

  const toggle = (key: AnalystKey) => {
    setSelected((s) => {
      const next = { ...s, [key]: !s[key] };
      const anySelected = Object.values(next).some(Boolean);
      return anySelected ? next : s;
    });
  };

  const handleEngage = () => {
    if (!ticker.trim() || !date) return;
    onEngage(ticker.trim(), date, selectedAnalysts);
  };

  const setDateAndNotify = (d: string) => {
    setDate(d);
    onContextChange?.(ticker, d);
  };

  const setTickerAndNotify = (t: string) => {
    setTicker(t);
    onContextChange?.(t, date);
  };

  return (
    <aside className="rail rail--left">
      <div className="rail-inner">
        <div className="left-title">
          <div className="left-title-top">Temporal Market Engine</div>
          <div className="left-title-sub">POST /api/analyze</div>
        </div>

        <div className="left-actions">
          <div className="left-cta-wrapper">
            <div className="left-cta" role="group" aria-label="Run controls">
              {isRunning ? (
                <button
                  className="engage-button engage-button--pill engage-button--active engage-button--icon"
                  onClick={onCancel}
                >
                  <span className="engage-pulse" />
                  <span className="engage-text">CANCEL</span>
                </button>
              ) : (
                <button
                  className="engage-button engage-button--pill engage-button--icon"
                  onClick={handleEngage}
                >
                  <span className="engage-glow" />
                  <LightningIcon />
                  <span className="engage-text">+ NEW ANALYSIS</span>
                </button>
              )}
            </div>
          </div>
        </div>

        <div className="left-controls">
          <DateDial
            value={date}
            onChange={setDateAndNotify}
            onPresetSelect={(d, t) => {
              setDateAndNotify(d);
              setTickerAndNotify(t);
            }}
          />
          <TickerInput value={ticker} onChange={setTickerAndNotify} />
        </div>

        <div className="left-section">
          <h3 className="section-title section-title--sm">Analysts</h3>
          <div className="analyst-nav-list" role="list">
            {ANALYST_OPTIONS.map((o) => {
              const active = selected[o.key];
              return (
                <button
                  key={o.key}
                  type="button"
                  role="listitem"
                  className={`analyst-nav-item ${active ? "analyst-nav-item--active" : ""}`}
                  onClick={() => toggle(o.key)}
                >
                  <span className="analyst-nav-icon" aria-hidden>
                    {o.icon}
                  </span>
                  {o.label}
                </button>
              );
            })}
          </div>
        </div>

        <div className="left-section">
          <div className="section-title-row">
            <h3 className="section-title section-title--sm">System Health</h3>
            <span
              className={`healthy-badge ${healthy ? "healthy-badge--ok" : "healthy-badge--bad"}`}
            >
              <span className="healthy-badge-dot" aria-hidden />
              {healthy ? "Healthy" : "Degraded"}
            </span>
          </div>
          <div className="health-block">
            <div className="health-row">
              <span className="health-label">ACTIVE RUNS</span>
              <span className="health-value">{health.activeRuns}</span>
            </div>
            <div className="health-row">
              <span className="health-label">STATUS</span>
              <span className="health-value">
                {health.status === "ok" ? "ONLINE" : "OFFLINE"}
              </span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
