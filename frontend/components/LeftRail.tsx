"use client";

import { useState } from "react";
import DateDial from "./DateDial";
import TickerInput from "./TickerInput";
import type { StreamStatus } from "@/lib/types";
import { useBackendHealth } from "@/hooks/useBackendHealth";
interface Props {
  status: StreamStatus;
  onEngage: (ticker: string, date: string) => void;
  onCancel: () => void;
  onContextChange?: (ticker: string, date: string) => void;
}

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
  onEngage,
  onCancel,
  onContextChange,
}: Props) {
  const [date, setDate] = useState("");
  const [ticker, setTicker] = useState("");
  const isRunning = status === "connecting" || status === "streaming";
  const health = useBackendHealth(15000);
  const healthy = health.status === "ok" && !health.error;

  const handleEngage = () => {
    if (!ticker.trim() || !date) return;
    onEngage(ticker.trim(), date);
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
