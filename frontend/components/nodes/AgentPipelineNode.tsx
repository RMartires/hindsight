"use client";

import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { AgentPipelineRfNode } from "@/lib/pipelineToReactFlow";

const DEFAULT_ACCENT = "#5fffb0";
const MUTED_STROKE = "#3f3f46";
const MUTED_TEXT = "#71717a";
const COMPLETE_STROKE = "#64748b";
const COMPLETE_FILL = "rgba(30, 41, 59, 0.65)";

export default function AgentPipelineNode({
  data,
  selected,
}: NodeProps<AgentPipelineRfNode>) {
  const { displayName, roleLabel, status, focused } = data;
  const accentColor = DEFAULT_ACCENT;

  const fillRgba = (a: number) => {
    const hex = accentColor.replace("#", "");
    if (hex.length !== 6) return `rgba(95,255,176,${a})`;
    const r = parseInt(hex.slice(0, 2), 16);
    const g = parseInt(hex.slice(2, 4), 16);
    const b = parseInt(hex.slice(4, 6), 16);
    return `rgba(${r},${g},${b},${a})`;
  };

  const dimmed = status === "pending";
  const opacity = dimmed ? 0.55 : 1;

  let strokeColor: string;
  let fillColor: string;
  let strokeWidth: number;
  if (status === "pending") {
    strokeColor = MUTED_STROKE;
    fillColor = "#0a0a0c";
    strokeWidth = 1;
  } else if (status === "completed") {
    strokeColor = COMPLETE_STROKE;
    fillColor = COMPLETE_FILL;
    strokeWidth = 1.5;
  } else {
    strokeColor = accentColor;
    fillColor = fillRgba(0.2);
    strokeWidth = 2.75;
  }

  const roleFill =
    status === "in_progress"
      ? accentColor
      : status === "completed"
        ? "#94a3b8"
        : MUTED_TEXT;
  const titleFill =
    status === "in_progress"
      ? "#fafafa"
      : status === "completed"
        ? "#e2e8f0"
        : MUTED_TEXT;

  const emphasis = focused || selected;

  return (
    <>
      <Handle
        id="spine-in"
        type="target"
        position={Position.Top}
        style={{
          left: "50%",
          top: 0,
          transform: "translate(-50%, -30%)",
          background: "#52525b",
          border: "1px solid var(--border)",
          width: 8,
          height: 8,
        }}
      />
      <div
        className={`agent-pipeline-node agent-node agent-node--${status} ${emphasis ? "agent-pipeline-node--focused" : ""}`}
        style={{
          position: "relative",
          width: "100%",
          height: "100%",
          boxSizing: "border-box",
          borderRadius: 10,
          border: `${strokeWidth}px solid ${strokeColor}`,
          background: fillColor,
          padding: "10px 14px",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 2,
          opacity,
          cursor: "pointer",
          boxShadow: emphasis
            ? `0 0 0 2px ${accentColor}, 0 0 24px rgba(95, 255, 176, 0.22)`
            : undefined,
          outline: "none",
        }}
      >
        {status === "in_progress" && (
          <span
            className="node-pulse agent-pipeline-node__pulse"
            style={{
              position: "absolute",
              inset: 0,
              borderRadius: 10,
              border: `3px solid ${accentColor}`,
              pointerEvents: "none",
              zIndex: 0,
            }}
          />
        )}
        <div
          style={{
            position: "absolute",
            top: 10,
            right: 10,
            width: status === "in_progress" ? 10 : 8,
            height: status === "in_progress" ? 10 : 8,
            borderRadius: "50%",
            background:
              status === "in_progress"
                ? accentColor
                : status === "completed"
                  ? "#475569"
                  : MUTED_STROKE,
            opacity: status === "pending" ? 0.5 : 1,
            zIndex: 1,
          }}
          className={status === "in_progress" ? "node-status-dot--live" : undefined}
          title={status}
        />
        <span
          style={{
            position: "relative",
            zIndex: 1,
            fontFamily: "var(--font-inter), system-ui, sans-serif",
            fontSize: 9,
            fontWeight: 700,
            letterSpacing: "1.2px",
            color: roleFill,
            lineHeight: 1.2,
          }}
        >
          {roleLabel}
        </span>
        <span
          style={{
            position: "relative",
            zIndex: 1,
            fontFamily: "var(--font-inter), system-ui, sans-serif",
            fontSize: 12,
            fontWeight: 600,
            color: dimmed ? MUTED_TEXT : titleFill,
            lineHeight: 1.25,
            textAlign: "center",
          }}
        >
          {displayName}
        </span>
      </div>
      <Handle
        id="tools-out"
        type="source"
        position={Position.Right}
        style={{
          right: 0,
          top: "50%",
          transform: "translate(30%, -50%)",
          background: "#52525b",
          border: "1px solid var(--border)",
          width: 8,
          height: 8,
        }}
      />
      <Handle
        id="spine-out"
        type="source"
        position={Position.Bottom}
        style={{
          left: "50%",
          bottom: 0,
          transform: "translate(-50%, 30%)",
          background: "#52525b",
          border: "1px solid var(--border)",
          width: 8,
          height: 8,
        }}
      />
    </>
  );
}
