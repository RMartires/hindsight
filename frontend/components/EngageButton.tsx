"use client";

import type { StreamStatus } from "@/lib/types";

interface Props {
  status: StreamStatus;
  onClick: () => void;
  onCancel: () => void;
}

export default function EngageButton({ status, onClick, onCancel }: Props) {
  const isRunning = status === "connecting" || status === "streaming";

  if (isRunning) {
    return (
      <button className="engage-button engage-button--active" onClick={onCancel}>
        <span className="engage-pulse" />
        <span className="engage-text">CANCEL</span>
      </button>
    );
  }

  return (
    <button
      className="engage-button"
      onClick={onClick}
      disabled={false}
    >
      <span className="engage-glow" />
      <span className="engage-text">ENGAGE</span>
    </button>
  );
}
