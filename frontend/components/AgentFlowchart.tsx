"use client";

import { useCallback, useMemo, useRef } from "react";
import type { AgentStatus } from "@/lib/types";
import type { StreamStatus } from "@/lib/types";
import type { PipelineAnalystKey } from "@/lib/pipelineGraph";
import {
  buildAllEdges,
  computeLayout,
  computeViewBox,
  filterEdges,
  getDisplayName,
  getHubAndBranches,
  getRoleLabel,
  isVisibleOnCanvas,
} from "@/lib/pipelineGraph";
import AgentNode from "./AgentNode";

interface Props {
  agents: Record<string, AgentStatus>;
  selectedAnalystKeys: PipelineAnalystKey[];
  subtitle?: string;
  streamStatus: StreamStatus;
  onNodeClick?: (agent: string) => void;
}

const DEFAULT_SUBTITLE = "Forensic Analysis of Liquidity Cascades";
const NEON = "#5fffb0";
const EDGE_DIM = "#27272a";

function SearchIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
      <circle cx="11" cy="11" r="7" />
      <path d="M21 21l-4.35-4.35" strokeLinecap="round" />
    </svg>
  );
}

function ZoomOutIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
      <circle cx="11" cy="11" r="7" />
      <path d="M8 11h6M21 21l-4.35-4.35" strokeLinecap="round" />
    </svg>
  );
}

function ExpandIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
      <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export default function AgentFlowchart({
  agents,
  selectedAnalystKeys,
  subtitle = DEFAULT_SUBTITLE,
  streamStatus,
  onNodeClick,
}: Props) {
  const wrapRef = useRef<HTMLDivElement | null>(null);

  const { hub, branches } = useMemo(
    () => getHubAndBranches(selectedAnalystKeys),
    [selectedAnalystKeys]
  );

  const allEdges = useMemo(
    () => buildAllEdges(selectedAnalystKeys),
    [selectedAnalystKeys]
  );

  const visibleIds = useMemo(() => {
    return Object.entries(agents)
      .filter(([, st]) => isVisibleOnCanvas(st))
      .map(([id]) => id);
  }, [agents]);

  const positions = useMemo(
    () => computeLayout(visibleIds, hub, branches),
    [visibleIds, hub, branches]
  );

  const activeEdges = useMemo(
    () => filterEdges(allEdges, agents),
    [allEdges, agents]
  );

  const viewBox = useMemo(() => computeViewBox(positions), [positions]);

  const toggleFullscreen = useCallback(() => {
    const el = wrapRef.current;
    if (!el) return;
    if (!document.fullscreenElement) {
      void el.requestFullscreen?.();
    } else {
      void document.exitFullscreen?.();
    }
  }, []);

  const onSearchClick = useCallback(() => {
    /* reserved: filter/highlight nodes */
  }, []);

  const halfW = 104;

  const getPos = (id: string): { x: number; y: number } | undefined => {
    const p = positions.get(id);
    return p ? { x: p.x, y: p.y } : undefined;
  };

  const waitingForNodes =
    streamStatus === "connecting" ||
    streamStatus === "streaming" ||
    streamStatus === "done";
  const showIdleEmpty = streamStatus === "idle" && visibleIds.length === 0;
  const showWaitingEmpty =
    waitingForNodes && visibleIds.length === 0;
  const empty = showIdleEmpty || showWaitingEmpty;

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
            onClick={onSearchClick}
            aria-label="Search"
            title="Search"
          >
            <SearchIcon />
          </button>
          <button
            type="button"
            className="pipeline-control-btn"
            onClick={() => {
              const el = wrapRef.current?.querySelector(".flowchart-svg-wrap");
              if (el instanceof HTMLElement) {
                const next = Math.max(0.7, parseFloat(el.dataset.zoom || "1") - 0.15);
                el.dataset.zoom = String(next);
                el.style.transform = `scale(${next})`;
                el.style.transformOrigin = "top left";
              }
            }}
            aria-label="Zoom out"
            title="Zoom out"
          >
            <ZoomOutIcon />
          </button>
          <button
            type="button"
            className="pipeline-control-btn"
            onClick={toggleFullscreen}
            aria-label="Fullscreen"
            title="Fullscreen"
          >
            <ExpandIcon />
          </button>
        </div>
      </div>

      <div className="flowchart-body">
        {empty ? (
          <div className="flowchart-empty">
            <p className="flowchart-empty-title">
              {showIdleEmpty ? "Pipeline idle" : "Connecting to stream…"}
            </p>
            <p className="flowchart-empty-hint">
              {showIdleEmpty ? (
                <>
                  Configure time coordinates and run <strong>New Analysis</strong> to stream agent
                  status into this graph.
                </>
              ) : (
                <>Waiting for the first <code>agent_status</code> event…</>
              )}
            </p>
          </div>
        ) : (
          <div
            className="flowchart-svg-wrap"
            data-zoom="1"
            style={{
              transform: "scale(1)",
              transformOrigin: "top left",
              transition: "transform 0.2s ease",
            }}
          >
            <svg viewBox={viewBox} className="flowchart-svg flowchart-svg--dynamic">
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

              {activeEdges.map((edge) => {
                const from = getPos(edge.from);
                const to = getPos(edge.to);
                if (!from || !to) return null;

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
                    stroke={isActive ? "rgba(95,255,176,0.4)" : EDGE_DIM}
                    strokeWidth={1.5}
                    markerEnd={isActive ? "url(#arrow-active)" : "url(#arrow)"}
                  />
                );
              })}

              {visibleIds.map((id) => {
                const p = positions.get(id);
                if (!p) return null;
                const status = agents[id] || "pending";
                const role = getRoleLabel(id, status, hub, branches);
                const displayName = getDisplayName(id);
                return (
                  <AgentNode
                    key={id}
                    agentId={id}
                    displayName={displayName}
                    roleLabel={role}
                    status={status}
                    x={p.x}
                    y={p.y}
                    accentColor={NEON}
                    onClick={onNodeClick ? () => onNodeClick(id) : undefined}
                  />
                );
              })}
            </svg>
          </div>
        )}
      </div>
    </div>
  );
}
