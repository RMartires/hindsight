"use client";

import { useState } from "react";
import DateDial from "./DateDial";
import TickerInput from "./TickerInput";
import EngageButton from "./EngageButton";
import type { StreamStatus } from "@/lib/types";

interface Props {
  status: StreamStatus;
  onEngage: (ticker: string, date: string) => void;
  onCancel: () => void;
}

export default function ControlDeck({ status, onEngage, onCancel }: Props) {
  const [date, setDate] = useState("");
  const [ticker, setTicker] = useState("");

  const handlePreset = (presetDate: string, presetTicker: string) => {
    setDate(presetDate);
    setTicker(presetTicker);
  };

  const handleEngage = () => {
    if (!ticker.trim() || !date) return;
    onEngage(ticker.trim(), date);
  };

  const isRunning = status === "connecting" || status === "streaming";

  return (
    <div className={`control-deck ${isRunning ? "control-deck--compact" : ""}`}>
      <div className="control-deck-inner">
        <DateDial
          value={date}
          onChange={setDate}
          onPresetSelect={handlePreset}
        />
        <div className="control-deck-actions">
          <TickerInput value={ticker} onChange={setTicker} />
          <EngageButton
            status={status}
            onClick={handleEngage}
            onCancel={onCancel}
          />
        </div>
      </div>
    </div>
  );
}
