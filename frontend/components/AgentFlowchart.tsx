"use client";

import { useCallback, useRef, useState } from "react";
import type { AgentStatus } from "@/lib/types";
import AgentNode from "./AgentNode";

interface Props {
  agents: Record<string, AgentStatus>;
  subtitle?: string;
  onNodeClick?: (agent: string) => void;
}

interface NodeDef {
  id: string;
  displayName: string;
  roleLabel: string;
  x: number;
  y: number;
}

interface EdgeDef {
  from: string;
  to: string;
}

const DEFAULT_SUBTITLE = "Forensic Analysis of Liquidity Cascades";

const NODES: NodeDef[] = [
  {
    id: "Market Analyst",
    displayName: "Market Analyst",
    roleLabel: "INGESTOR",
    x: 130,
    y: 130,
  },
  {
    id: "Fundamentals Analyst",
    displayName: "Fundamental Analyst",
    roleLabel: "ACTIVE ANALYSIS",
    x: 380,
    y: 130,
  },
  {
    id: "News Analyst",
    displayName: "Technical Analyst",
    roleLabel: "PROCESSING",
    x: 630,
    y: 130,
  },
];

const EDGES: EdgeDef[] = [
  { from: "Market Analyst", to: "Fundamentals Analyst" },
  { from: "Fundamentals Analyst", to: "News Analyst" },
];

const NEON = "#00e676";
const EDGE_DIM = "#27272a";

function getNodePos(id: string): NodeDef | undefined {
  return NODES.find((n) => n.id === id);
}

export default function AgentFlowchart({
  agents,
  subtitle = DEFAULT_SUBTITLE,
  onNodeClick,
}: Props) {
  const wrapRef = useRef<HTMLDivElement | null>(null);
  const [scale, setScale] = useState(1);

  const zoomIn = useCallback(() => {
    setScale((s) => Math.min(1.75, Math.round((s + 0.15) * 100) / 100));
  }, []);

  const zoomOut = useCallback(() => {
    setScale((s) => Math.max(0.7, Math.round((s - 0.15) * 100) / 100));
  }, []);

  const toggleFullscreen = useCallback(() => {
    const el = wrapRef.current;
    if (!el) return;
    if (!document.fullscreenElement) {
      void el.requestFullscreen?.();
    } else {
      void document.exitFullscreen?.();
    }
  }, []);

  return (
    <div className="flowchart-container" ref={wrapRef}>
      <div className="flowchart-header">
        <div className="flowchart-header-titles">
          <h3 className="flowchart-title">Active Pipeline</h3>
          <p className="flowchart-headline">{subtitle}</p>
        </div>
        <div className="pipeline-controls" role="toolbar" aria-label="Pipeline view">
          <button
            type="button"
            className="pipeline-control-btn"
            onClick={zoomIn}
            aria-label="Zoom in"
            title="Zoom in"
          >
            ⊕
          </button>
          <button
            type="button"
            className="pipeline-control-btn"
            onClick={zoomOut}
            aria-label="Zoom out"
            title="Zoom out"
          >
            ⊖
          </button>
          <button
            type="button"
            className="pipeline-control-btn"
            onClick={toggleFullscreen}
            aria-label="Fullscreen"
            title="Fullscreen"
          >
            ⛶
          </button>
        </div>
      </div>

      <div className="flowchart-body">
        <div
          style={{
            transform: `scale(${scale})`,
            transformOrigin: "top center",
            transition: "transform 0.2s ease",
          }}
        >
          <svg viewBox="0 0 760 220" className="flowchart-svg">
            <defs>
              <marker
                id="arrow"
                viewBox="0 0 10 6"
                refX="10"
                refY="3"
                markerWidth={8}
                markerHeight={6}
                orient="auto-start-reverse"
              >
                <path d="M 0 0 L 10 3 L 0 6 z" fill={EDGE_DIM} />
              </marker>
              <marker
                id="arrow-active"
                viewBox="0 0 10 6"
                refX="10"
                refY="3"
                markerWidth={8}
                markerHeight={6}
                orient="auto-start-reverse"
              >
                <path d="M 0 0 L 10 3 L 0 6 z" fill={NEON} />
              </marker>
            </defs>

            {EDGES.map((edge) => {
              const from = getNodePos(edge.from);
              const to = getNodePos(edge.to);
              if (!from || !to) return null;

              const halfW = 104;
              const fromStatus = agents[edge.from] || "pending";
              const isActive =
                fromStatus === "completed" || fromStatus === "in_progress";

              return (
                <line
                  key={`${edge.from}-${edge.to}`}
                  x1={from.x + halfW}
                  y1={from.y}
                  x2={to.x - halfW}
                  y2={to.y}
                  stroke={isActive ? "rgba(0,230,118,0.35)" : EDGE_DIM}
                  strokeWidth={1.5}
                  markerEnd={isActive ? "url(#arrow-active)" : "url(#arrow)"}
                />
              );
            })}

            {NODES.map((node) => (
              <AgentNode
                key={node.id}
                agentId={node.id}
                displayName={node.displayName}
                roleLabel={node.roleLabel}
                status={agents[node.id] || "pending"}
                x={node.x}
                y={node.y}
                onClick={onNodeClick ? () => onNodeClick(node.id) : undefined}
              />
            ))}
          </svg>
        </div>
      </div>
    </div>
  );
}
