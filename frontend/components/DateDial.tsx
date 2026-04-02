"use client";

import { HISTORICAL_PRESETS } from "@/lib/presets";

interface Props {
  value: string;
  onChange: (date: string) => void;
  onPresetSelect: (date: string, ticker: string) => void;
}

export default function DateDial({ value, onChange, onPresetSelect }: Props) {
  const today = new Date().toISOString().split("T")[0];

  return (
    <div className="date-dial">
      <label className="field-label">TIME COORDINATES</label>
      <div className="preset-chips">
        {HISTORICAL_PRESETS.map((preset) => (
          <button
            key={preset.date}
            className={`preset-chip ${value === preset.date ? "preset-chip--active" : ""}`}
            onClick={() => onPresetSelect(preset.date, preset.ticker)}
            title={preset.description}
          >
            {preset.label}
          </button>
        ))}
      </div>
      <input
        type="date"
        className="date-input"
        value={value}
        max={today}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}
