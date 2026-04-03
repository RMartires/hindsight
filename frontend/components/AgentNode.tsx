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
  onClick?: () => void;
}

const NEON = "#00e676";
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
  const strokeColor = strokeActive ? NEON : MUTED_STROKE;
  const fillColor =
    status === "completed"
      ? "rgba(0, 230, 118, 0.08)"
      : status === "in_progress"
        ? "rgba(0, 230, 118, 0.04)"
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
          stroke={NEON}
          strokeWidth={2}
          className="node-pulse"
        />
      )}
      <circle
        cx={rx + width - 14}
        cy={ry + 14}
        r={4}
        fill={strokeActive ? NEON : MUTED_STROKE}
        opacity={strokeActive ? 1 : 0.5}
      >
        <title>{status}</title>
      </circle>
      <text
        x={x}
        y={y - 26}
        fill={strokeActive ? "rgba(0,230,118,0.95)" : MUTED_TEXT}
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
        {`LATENCY: ${latency}`}
      </text>
    </g>
  );
}
