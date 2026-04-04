"use client";

import { useCallback, useEffect, useLayoutEffect, useMemo, useRef } from "react";
import {
  Background,
  BackgroundVariant,
  Controls,
  type Edge,
  type NodeTypes,
  ReactFlow,
  useEdgesState,
  useNodesState,
  useReactFlow,
} from "@xyflow/react";
import type {
  AgentStatus,
  PipelineTopologyEvent,
  StreamStatus,
  ToolCallRecord,
} from "@/lib/types";
import type { PipelineAnalystKey } from "@/lib/pipelineGraph";
import {
  getAutoFitViewPipelineNodeIds,
  isVisibleOnCanvas,
  sortVisibleByPipeline,
} from "@/lib/pipelineGraph";
import { buildPipelineReactFlowElements } from "@/lib/pipelineToReactFlow";
import type { PipelineFlowNode } from "@/lib/pipelineToReactFlow";
import AgentPipelineNode from "@/components/nodes/AgentPipelineNode";
import ToolPipelineNode from "@/components/nodes/ToolPipelineNode";

/** Module scope so React Flow never sees a new `nodeTypes` object (dev warning #002). */
const PIPELINE_NODE_TYPES = {
  agentPipeline: AgentPipelineNode,
  toolPipeline: ToolPipelineNode,
} satisfies NodeTypes;

const DEFAULT_SUBTITLE = "Forensic Analysis of Liquidity Cascades";

const DEFAULT_VIEWPORT = { x: 0, y: 0, zoom: 1 } as const;

function FitViewOnGraphChange({
  nodeCount,
  layoutKey,
  refitSignal = 0,
  denseRowNodeIds = null,
}: {
  nodeCount: number;
  layoutKey: string;
  refitSignal?: number;
  /** When set, `fitView` frames this row (agent + tools); otherwise full graph. */
  denseRowNodeIds?: string[] | null;
}) {
  const { fitView } = useReactFlow();
  const fitViewRef = useRef(fitView);
  fitViewRef.current = fitView;

  const denseKey = denseRowNodeIds?.join("\0") ?? "";

  useLayoutEffect(() => {
    if (nodeCount === 0) return;
    const ids = denseRowNodeIds;
    const focusSubset = ids != null && ids.length > 0;

    let cancelled = false;
    const id1 = requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        if (cancelled) return;
        void fitViewRef.current({
          padding: focusSubset ? 0.08 : 0.2,
          duration: 200,
          maxZoom: focusSubset ? 1.65 : 1.35,
          ...(focusSubset && ids
            ? { nodes: ids.map((nid) => ({ id: nid })) }
            : {}),
        });
      });
    });
    return () => {
      cancelled = true;
      cancelAnimationFrame(id1);
    };
  }, [nodeCount, layoutKey, refitSignal, denseKey, denseRowNodeIds]);
  return null;
}

interface Props {
  agents: Record<string, AgentStatus>;
  selectedAnalystKeys: PipelineAnalystKey[];
  subtitle?: string;
  streamStatus: StreamStatus;
  pipelineTopology?: PipelineTopologyEvent | null;
  selectedAgentId: string | null;
  onSelectAgent: (agentId: string | null) => void;
  toolCalls: ToolCallRecord[];
  /** Bumped when the flow container becomes visible (e.g. mobile step) so fitView re-runs. */
  refitSignal?: number;
}

function SearchIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden>
      <circle cx="11" cy="11" r="7" />
      <path d="M21 21l-4.35-4.35" strokeLinecap="round" />
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

export default function AgentReactFlow({
  agents,
  selectedAnalystKeys,
  subtitle = DEFAULT_SUBTITLE,
  streamStatus,
  pipelineTopology = null,
  selectedAgentId,
  onSelectAgent,
  toolCalls,
  refitSignal = 0,
}: Props) {
  const wrapRef = useRef<HTMLDivElement | null>(null);
  const [nodes, setNodes, onNodesChange] = useNodesState<PipelineFlowNode>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  const { nodes: nextNodes, edges: nextEdges } = useMemo(
    () =>
      buildPipelineReactFlowElements(
        agents,
        selectedAnalystKeys,
        selectedAgentId,
        toolCalls
      ),
    [agents, selectedAnalystKeys, selectedAgentId, toolCalls]
  );

  useEffect(() => {
    setNodes(nextNodes);
    setEdges(nextEdges);
  }, [nextNodes, nextEdges, setNodes, setEdges]);

  const nodeCount = nodes.length;
  const layoutKey = useMemo(
    () =>
      nodes
        .map((n) => `${n.id}:${Math.round(n.position.x)}:${Math.round(n.position.y)}`)
        .join("|"),
    [nodes]
  );

  const denseRowFitNodeIds = useMemo(() => {
    const visibleIds = Object.entries(agents)
      .filter(([, st]) => isVisibleOnCanvas(st))
      .map(([id]) => id);
    const ordered = sortVisibleByPipeline(visibleIds, selectedAnalystKeys);
    return getAutoFitViewPipelineNodeIds(ordered, toolCalls);
  }, [agents, selectedAnalystKeys, toolCalls]);

  const toggleFullscreen = useCallback(() => {
    const el = wrapRef.current;
    if (!el) return;
    if (!document.fullscreenElement) {
      void el.requestFullscreen?.();
    } else {
      void document.exitFullscreen?.();
    }
  }, []);

  const waitingForNodes =
    streamStatus === "connecting" ||
    streamStatus === "streaming" ||
    streamStatus === "done";
  const showIdleEmpty = streamStatus === "idle" && nodeCount === 0;
  const showWaitingEmpty = waitingForNodes && nodeCount === 0;
  const empty = showIdleEmpty || showWaitingEmpty;

  return (
    <div
      className="flowchart-container"
      ref={wrapRef}
      data-topology-source={pipelineTopology?.source ?? ""}
    >
      <div className="flowchart-header">
        <div className="flowchart-header-titles">
          <h3 className="flowchart-title">Active Pipeline</h3>
          <p className="flowchart-headline">{subtitle}</p>
        </div>
        <div className="pipeline-controls" role="toolbar" aria-label="Pipeline view">
          <button
            type="button"
            className="pipeline-control-btn"
            aria-label="Search"
            title="Search"
            disabled
          >
            <SearchIcon />
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

      <div className="flowchart-body flowchart-body--reactflow">
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
            className="react-flow-pipeline flowchart-react-flow-wrap"
            style={{ width: "100%", height: 480, minHeight: 420 }}
          >
            <ReactFlow
              nodes={nodes}
              edges={edges}
              nodeTypes={PIPELINE_NODE_TYPES}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={(_, node) => onSelectAgent(node.id)}
              onPaneClick={() => onSelectAgent(null)}
              nodesDraggable={false}
              nodesConnectable={false}
              elementsSelectable
              deleteKeyCode={null}
              multiSelectionKeyCode={null}
              proOptions={{ hideAttribution: true }}
              fitView={false}
              minZoom={0.35}
              maxZoom={1.5}
              defaultViewport={DEFAULT_VIEWPORT}
            >
              <FitViewOnGraphChange
                nodeCount={nodeCount}
                layoutKey={layoutKey}
                refitSignal={refitSignal}
                denseRowNodeIds={denseRowFitNodeIds}
              />
              <Background
                id="pipeline-bg"
                variant={BackgroundVariant.Dots}
                gap={20}
                size={1}
                color="rgba(95, 255, 176, 0.12)"
              />
              <Controls position="bottom-right" showInteractive={false} />
            </ReactFlow>
          </div>
        )}
      </div>
    </div>
  );
}
