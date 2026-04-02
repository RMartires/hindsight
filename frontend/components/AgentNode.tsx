"use client";

import type { AgentStatus } from "@/lib/types";

interface Props {
  name: string;
  status: AgentStatus;
  x: number;
  y: number;
  onClick?: () => void;
}

const STATUS_COLORS: Record<AgentStatus, string> = {
  pending: "#3f3f46",
  in_progress: "#22c55e",
  completed: "#22c55e",
};

const STATUS_FILL: Record<AgentStatus, string> = {
  pending: "#18181b",
  in_progress: "#18181b",
  completed: "#052e16",
};

export default function AgentNode({ name, status, x, y, onClick }: Props) {
  const width = 130;
  const height = 40;
  const rx = x - width / 2;
  const ry = y - height / 2;

  return (
    <g
      className={`agent-node agent-node--${status}`}
      onClick={onClick}
      style={{ cursor: onClick ? "pointer" : "default" }}
    >
      <rect
        x={rx}
        y={ry}
        width={width}
        height={height}
        rx={8}
        fill={STATUS_FILL[status]}
        stroke={STATUS_COLORS[status]}
        strokeWidth={status === "pending" ? 1 : 2}
        strokeDasharray={status === "pending" ? "4 4" : undefined}
      />
      {status === "in_progress" && (
        <rect
          x={rx}
          y={ry}
          width={width}
          height={height}
          rx={8}
          fill="none"
          stroke="#22c55e"
          strokeWidth={2}
          className="node-pulse"
        />
      )}
      {status === "completed" && (
        <text
          x={rx + 12}
          y={y + 1}
          fill="#22c55e"
          fontSize={14}
          dominantBaseline="middle"
        >
          &#10003;
        </text>
      )}
      <text
        x={x + (status === "completed" ? 6 : 0)}
        y={y + 1}
        fill={status === "pending" ? "#71717a" : "#fafafa"}
        fontSize={11}
        textAnchor="middle"
        dominantBaseline="middle"
        fontFamily="inherit"
      >
        {name}
      </text>
    </g>
  );
}
