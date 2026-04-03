"use client";

import { useLayoutEffect, useState, type MouseEvent } from "react";
import {
  Handle,
  Position,
  type NodeProps,
  useReactFlow,
  useUpdateNodeInternals,
} from "@xyflow/react";
import {
  TOOL_NODE_HEIGHT,
  type ToolPipelineRfNode,
} from "@/lib/pipelineToReactFlow";

const MUTED = "#71717a";
const ACCENT = "#5fffb0";

function preview(s: string, max: number): string {
  const t = s.trim();
  if (t.length <= max) return t || "—";
  return `${t.slice(0, max - 1)}…`;
}

/** Room for multi-call list without clipping; center stays on pipeline row. */
const EXPANDED_TOOL_HEIGHT = 228;

export default function ToolPipelineNode({
  id,
  data,
}: NodeProps<ToolPipelineRfNode>) {
  const { toolName, calls, focused } = data;
  const multi = calls.length > 1;
  const [expanded, setExpanded] = useState(false);
  const { updateNode } = useReactFlow();
  const updateNodeInternals = useUpdateNodeInternals();

  useLayoutEffect(() => {
    if (!multi) return;
    const h = expanded ? EXPANDED_TOOL_HEIGHT : TOOL_NODE_HEIGHT;
    updateNode(id, (node) => {
      const prevH = node.height ?? TOOL_NODE_HEIGHT;
      if (prevH === h) return node;
      const deltaHalf = h / 2 - prevH / 2;
      return {
        ...node,
        height: h,
        position: { ...node.position, y: node.position.y - deltaHalf },
      };
    });
    queueMicrotask(() => updateNodeInternals(id));
  }, [multi, expanded, id, updateNode, updateNodeInternals]);

  const toggleExpand = (e: MouseEvent) => {
    e.stopPropagation();
    setExpanded((v) => !v);
  };

  const first = calls[0]!;

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
          cursor: "pointer",
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
            display: "flex",
            alignItems: "baseline",
            justifyContent: "space-between",
            gap: 6,
            minWidth: 0,
          }}
        >
          <div
            style={{
              fontFamily: "var(--font-inter), system-ui, sans-serif",
              fontSize: 11,
              fontWeight: 600,
              color: "#e2e8f0",
              lineHeight: 1.25,
              flex: 1,
              minWidth: 0,
            }}
          >
            {toolName}
            {multi ? (
              <span
                style={{
                  marginLeft: 6,
                  fontSize: 9,
                  fontWeight: 700,
                  color: ACCENT,
                  letterSpacing: "0.06em",
                }}
              >
                ×{calls.length}
              </span>
            ) : null}
          </div>
          {multi ? (
            <button
              type="button"
              onClick={toggleExpand}
              style={{
                flexShrink: 0,
                fontSize: 9,
                fontWeight: 600,
                letterSpacing: "0.04em",
                color: ACCENT,
                background: "rgba(95, 255, 176, 0.08)",
                border: "1px solid rgba(95, 255, 176, 0.35)",
                borderRadius: 4,
                padding: "2px 6px",
                cursor: "pointer",
              }}
            >
              {expanded ? "Less" : "All"}
            </button>
          ) : null}
        </div>

        {!multi || !expanded ? (
          <>
            <div
              style={{
                fontFamily: "ui-monospace, monospace",
                fontSize: 9,
                color: MUTED,
                lineHeight: 1.35,
                maxHeight: multi ? 22 : 36,
                overflow: "hidden",
              }}
            >
              <span style={{ color: "#94a3b8" }}>in:</span>{" "}
              {preview(first.input ?? "", 80)}
            </div>
            <div
              style={{
                fontFamily: "ui-monospace, monospace",
                fontSize: 9,
                color: MUTED,
                lineHeight: 1.35,
                maxHeight: multi ? 22 : 36,
                overflow: "hidden",
              }}
            >
              <span style={{ color: "#94a3b8" }}>out:</span>{" "}
              {preview(first.output ?? "", 80)}
            </div>
            {multi && !expanded ? (
              <div
                style={{
                  fontSize: 8,
                  color: "#64748b",
                  marginTop: -2,
                }}
              >
                +{calls.length - 1} call{calls.length - 1 === 1 ? "" : "s"} collapsed — use{" "}
                <span style={{ color: ACCENT }}>All</span>
              </div>
            ) : null}
          </>
        ) : (
          <div
            style={{
              maxHeight: 168,
              overflowY: "auto",
              marginRight: -4,
              paddingRight: 4,
              display: "flex",
              flexDirection: "column",
              gap: 6,
            }}
          >
            {calls.map((c, i) => (
              <div
                key={c.id}
                style={{
                  paddingTop: i ? 6 : 0,
                  borderTop:
                    i > 0 ? "1px solid rgba(100, 116, 139, 0.35)" : undefined,
                }}
              >
                <div
                  style={{
                    fontSize: 8,
                    fontWeight: 700,
                    color: "#94a3b8",
                    marginBottom: 3,
                    letterSpacing: "0.06em",
                  }}
                >
                  CALL {i + 1}/{calls.length}
                </div>
                <div
                  style={{
                    fontFamily: "ui-monospace, monospace",
                    fontSize: 9,
                    color: MUTED,
                    lineHeight: 1.35,
                  }}
                >
                  <span style={{ color: "#94a3b8" }}>in:</span>{" "}
                  {preview(c.input ?? "", 120)}
                </div>
                <div
                  style={{
                    fontFamily: "ui-monospace, monospace",
                    fontSize: 9,
                    color: MUTED,
                    lineHeight: 1.35,
                  }}
                >
                  <span style={{ color: "#94a3b8" }}>out:</span>{" "}
                  {preview(c.output ?? "", 120)}
                </div>
              </div>
            ))}
          </div>
        )}
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
