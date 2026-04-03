import type { Edge, Node } from "@xyflow/react";
import { MarkerType, Position } from "@xyflow/react";
import type { AgentStatus } from "@/lib/types";
import type { PipelineAnalystKey } from "@/lib/pipelineGraph";
import {
  buildSequentialEdges,
  computeLayout,
  filterEdges,
  getDisplayName,
  getHubAndBranches,
  getRoleLabel,
  isVisibleOnCanvas,
  sortVisibleByPipeline,
} from "@/lib/pipelineGraph";

export const AGENT_NODE_WIDTH = 208;
export const AGENT_NODE_HEIGHT = 92;

export type AgentPipelineNodeData = {
  agentId: string;
  displayName: string;
  roleLabel: string;
  status: AgentStatus;
  focused: boolean;
};

export type AgentPipelineRfNode = Node<AgentPipelineNodeData, "agentPipeline">;

const NEON = "#5fffb0";
const EDGE_DIM = "#52525e";

export function buildPipelineReactFlowElements(
  agents: Record<string, AgentStatus>,
  selectedAnalystKeys: PipelineAnalystKey[],
  focusedAgentId: string | null
): { nodes: AgentPipelineRfNode[]; edges: Edge[] } {
  const { hub, branches } = getHubAndBranches(selectedAnalystKeys);

  const visibleIds = Object.entries(agents)
    .filter(([, st]) => isVisibleOnCanvas(st))
    .map(([id]) => id);

  const orderedVisibleIds = sortVisibleByPipeline(visibleIds, selectedAnalystKeys);
  const positions = computeLayout(orderedVisibleIds);

  const halfW = AGENT_NODE_WIDTH / 2;
  const halfH = AGENT_NODE_HEIGHT / 2;

  const nodes: AgentPipelineRfNode[] = orderedVisibleIds.map((id) => {
    const p = positions.get(id)!;
    const status = agents[id] ?? "pending";
    return {
      id,
      type: "agentPipeline" as const,
      position: {
        x: p.x - halfW,
        y: p.y - halfH,
      },
      width: AGENT_NODE_WIDTH,
      height: AGENT_NODE_HEIGHT,
      sourcePosition: Position.Bottom,
      targetPosition: Position.Top,
      data: {
        agentId: id,
        displayName: getDisplayName(id),
        roleLabel: getRoleLabel(id, status, hub, branches),
        status,
        focused: focusedAgentId === id,
      },
      zIndex: focusedAgentId === id ? 2 : 0,
    };
  });

  const seqEdges = buildSequentialEdges(selectedAnalystKeys);
  const activeEdgeDefs = filterEdges(seqEdges, agents);

  const edges: Edge[] = activeEdgeDefs.map((e) => {
    const srcSt = agents[e.from] ?? "pending";
    const active =
      srcSt === "completed" || srcSt === "in_progress";
    return {
      id: `${e.from}-${e.to}`,
      source: e.from,
      target: e.to,
      type: "smoothstep",
      animated: agents[e.to] === "in_progress",
      style: {
        stroke: active ? "rgba(95, 255, 176, 0.45)" : EDGE_DIM,
        strokeWidth: 1.5,
      },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: active ? NEON : EDGE_DIM,
        width: 18,
        height: 18,
      },
    };
  });

  return { nodes, edges };
}
