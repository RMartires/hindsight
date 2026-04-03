"use client";

import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { ToolPipelineRfNode } from "@/lib/pipelineToReactFlow";

const MUTED = "#71717a";
const ACCENT = "#5fffb0";

function preview(s: string, max: number): string {
  const t = s.trim();
  if (t.length <= max) return t || "—";
  return `${t.slice(0, max - 1)}…`;
}

export default function ToolPipelineNode({ data }: NodeProps<ToolPipelineRfNode>) {
  const { toolName, inputPreview, outputPreview, focused } = data;
  return (
    <>
      <Handle
        id="from-agent"
        type="target"
        position={Position.Left}
        style={{
          left: 0,
          top: "50%",
          transform: "translate(-30%, -50%)",
          background: "#52525b",
          border: "1px solid var(--border)",
          width: 7,
          height: 7,
        }}
      />
      <div
        className={`tool-pipeline-node ${focused ? "tool-pipeline-node--focused" : ""}`}
        style={{
          position: "relative",
          width: "100%",
          height: "100%",
          boxSizing: "border-box",
          borderRadius: 8,
          border: `1.5px solid ${focused ? ACCENT : "rgba(100, 116, 139, 0.65)"}`,
          background: "rgba(15, 23, 42, 0.75)",
          padding: "8px 10px",
          display: "flex",
          flexDirection: "column",
          gap: 4,
          cursor: "default",
          boxShadow: focused ? `0 0 0 1px ${ACCENT}, 0 0 16px rgba(95, 255, 176, 0.2)` : undefined,
        }}
      >
        <div
          style={{
            fontSize: 9,
            fontWeight: 700,
            letterSpacing: "0.12em",
            color: ACCENT,
            textTransform: "uppercase",
          }}
        >
          TOOL
        </div>
        <div
          style={{
            fontFamily: "var(--font-inter), system-ui, sans-serif",
            fontSize: 11,
            fontWeight: 600,
            color: "#e2e8f0",
            lineHeight: 1.25,
          }}
        >
          {toolName}
        </div>
        <div
          style={{
            fontFamily: "ui-monospace, monospace",
            fontSize: 9,
            color: MUTED,
            lineHeight: 1.35,
            maxHeight: 36,
            overflow: "hidden",
          }}
        >
          <span style={{ color: "#94a3b8" }}>in:</span> {preview(inputPreview, 80)}
        </div>
        <div
          style={{
            fontFamily: "ui-monospace, monospace",
            fontSize: 9,
            color: MUTED,
            lineHeight: 1.35,
            maxHeight: 36,
            overflow: "hidden",
          }}
        >
          <span style={{ color: "#94a3b8" }}>out:</span> {preview(outputPreview, 80)}
        </div>
      </div>
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
          width: 7,
          height: 7,
        }}
      />
    </>
  );
}
