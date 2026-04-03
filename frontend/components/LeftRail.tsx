"use client";

import { useState } from "react";
import DateDial from "./DateDial";
import TickerInput from "./TickerInput";
import type { StreamStatus } from "@/lib/types";
import { useBackendHealth } from "@/hooks/useBackendHealth";
import {
  ANALYST_ORDER,
  type PipelineAnalystKey,
} from "@/lib/pipelineGraph";

interface Props {
  status: StreamStatus;
  selectedAnalystKeys: PipelineAnalystKey[];
  onSelectedAnalystKeysChange: (keys: PipelineAnalystKey[]) => void;
  onEngage: (ticker: string, date: string, analysts: PipelineAnalystKey[]) => void;
  onCancel: () => void;
  onContextChange?: (ticker: string, date: string) => void;
}

const ANALYST_OPTIONS: Array<{
  key: PipelineAnalystKey;
  label: string;
  icon: string;
}> = [
  { key: "market", label: "Market Analyst", icon: "◉" },
  { key: "fundamentals", label: "Fundamental", icon: "◇" },
  { key: "news", label: "Technical", icon: "◎" },
  { key: "social", label: "Sentiment", icon: "○" },
];

function BarChartIcon() {
  return (
    <svg
      className="engage-button-icon-svg"
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden
    >
      <path
        d="M4 19V5M4 19H20M8 15V9M12 13V7M16 11V5"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default function LeftRail({
  status,
  selectedAnalystKeys,
  onSelectedAnalystKeysChange,
  onEngage,
  onCancel,
  onContextChange,
}: Props) {
  const [date, setDate] = useState("");
  const [ticker, setTicker] = useState("");
  const isRunning = status === "connecting" || status === "streaming";
  const health = useBackendHealth(15000);
  const healthy = health.status === "ok" && !health.error;

  const toggle = (key: PipelineAnalystKey) => {
    const next = new Set(selectedAnalystKeys);
    if (next.has(key)) {
      if (next.size <= 1) return;
      next.delete(key);
    } else {
      next.add(key);
    }
    onSelectedAnalystKeysChange(
      ANALYST_ORDER.filter((k) => next.has(k)) as PipelineAnalystKey[]
    );
  };

  const handleEngage = () => {
    if (!ticker.trim() || !date) return;
    onEngage(ticker.trim(), date, selectedAnalystKeys);
  };

  const setDateAndNotify = (d: string) => {
    setDate(d);
    onContextChange?.(ticker, d);
  };

  const setTickerAndNotify = (t: string) => {
    setTicker(t);
    onContextChange?.(t, date);
  };

  const navItems = ANALYST_ORDER.map((key) =>
    ANALYST_OPTIONS.find((o) => o.key === key)
  ).filter(Boolean) as typeof ANALYST_OPTIONS;

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
                  <BarChartIcon />
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
            {navItems.map((o) => {
              const active = selectedAnalystKeys.includes(o.key);
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
