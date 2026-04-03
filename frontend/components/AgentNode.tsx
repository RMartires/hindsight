"use client";

import { useMemo } from "react";
import type { AgentStatus } from "@/lib/types";

interface Props {
  agentId: string;
  displayName: string;
  roleLabel: string;
  status: AgentStatus;
  x: number;
  y: number;
  accentColor?: string;
  onClick?: () => void;
}

const DEFAULT_ACCENT = "#5fffb0";
const MUTED_STROKE = "#3f3f46";
const MUTED_TEXT = "#71717a";

function pseudoLatency(agentId: string, status: AgentStatus): string {
  if (status === "pending") return "—";
  let h = 0;
  for (let i = 0; i < agentId.length; i++) {
    h = (h << 5) - h + agentId.charCodeAt(i);
    h |= 0;
  }
  const base = 8 + Math.abs(h % 190);
  if (status === "in_progress") return `${base}ms`;
  return `${base + 20}ms`;
}

export default function AgentNode({
  agentId,
  displayName,
  roleLabel,
  status,
  x,
  y,
  accentColor = DEFAULT_ACCENT,
  onClick,
}: Props) {
  const width = 208;
  const height = 92;
  const rx = x - width / 2;
  const ry = y - height / 2;

  const latency = useMemo(
    () => pseudoLatency(agentId, status),
    [agentId, status]
  );

  const strokeActive = status !== "pending";
  const strokeColor = strokeActive ? accentColor : MUTED_STROKE;
  const fillRgba = (a: number) => {
    const hex = accentColor.replace("#", "");
    if (hex.length !== 6) return `rgba(95,255,176,${a})`;
    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    return `rgba(${r},${g},${b},${a})`;
  };
  const fillColor =
    status === "completed"
      ? fillRgba(0.1)
      : status === "in_progress"
        ? fillRgba(0.05)
        : "#0a0a0c";
  const dimmed = status === "pending";
  const groupOpacity = dimmed ? 0.55 : 1;

  return (
    <g
      className={`agent-node agent-node--${status}`}
      onClick={onClick}
      style={{ cursor: onClick ? "pointer" : "default", opacity: groupOpacity }}
    >
      <rect
        x={rx}
        y={ry}
        width={width}
        height={height}
        rx={10}
        fill={fillColor}
        stroke={strokeColor}
        strokeWidth={strokeActive ? 2 : 1}
        strokeDasharray={status === "pending" ? "5 4" : undefined}
      />
      {status === "in_progress" && (
        <rect
          x={rx}
          y={ry}
          width={width}
          height={height}
          rx={10}
          fill="none"
          stroke={accentColor}
          strokeWidth={2}
          className="node-pulse"
        />
      )}
      <circle
        cx={rx + width - 14}
        cy={ry + 14}
        r={4}
        fill={strokeActive ? accentColor : MUTED_STROKE}
        opacity={strokeActive ? 1 : 0.5}
      >
        <title>{status}</title>
      </circle>
      <text
        x={x}
        y={y - 26}
        fill={strokeActive ? accentColor : MUTED_TEXT}
        fontSize={9}
        fontWeight={700}
        textAnchor="middle"
        dominantBaseline="middle"
        letterSpacing="1.2px"
        style={{ fontFamily: "var(--font-inter), system-ui, sans-serif" }}
      >
        {roleLabel}
      </text>
      <text
        x={x}
        y={y - 2}
        fill={dimmed ? MUTED_TEXT : "#fafafa"}
        fontSize={12}
        fontWeight={600}
        textAnchor="middle"
        dominantBaseline="middle"
        style={{ fontFamily: "var(--font-inter), system-ui, sans-serif" }}
      >
        {displayName}
      </text>
      <text
        x={x}
        y={y + 22}
        fill={MUTED_TEXT}
        fontSize={10}
        textAnchor="middle"
        dominantBaseline="middle"
        letterSpacing="0.5px"
        style={{ fontFamily: "ui-monospace, monospace" }}
      >
        {status === "completed" || status === "in_progress"
          ? `LATENCY: ${latency}`
          : "LATENCY: —"}
      </text>
    </g>
  );
}
