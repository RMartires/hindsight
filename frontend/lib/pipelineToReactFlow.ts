import type { Edge, Node } from "@xyflow/react";
import { MarkerType, Position } from "@xyflow/react";
import type { AgentStatus, ToolCallRecord } from "@/lib/types";
import type { PipelineAnalystKey } from "@/lib/pipelineGraph";
import {
  computePipelineBlockLayout,
  getDisplayName,
  getHubAndBranches,
  getRoleLabel,
  groupContiguousToolCalls,
  isVisibleOnCanvas,
  sortVisibleByPipeline,
} from "@/lib/pipelineGraph";

export const AGENT_NODE_WIDTH = 208;
export const AGENT_NODE_HEIGHT = 92;
export const TOOL_NODE_WIDTH = 210;
export const TOOL_NODE_HEIGHT = 74;

export type AgentPipelineNodeData = {
  agentId: string;
  displayName: string;
  roleLabel: string;
  status: AgentStatus;
  focused: boolean;
};

export type AgentPipelineRfNode = Node<AgentPipelineNodeData, "agentPipeline">;

export type ToolPipelineNodeData = {
  toolName: string;
  calls: ToolCallRecord[];
  focused: boolean;
};

export type ToolPipelineRfNode = Node<ToolPipelineNodeData, "toolPipeline">;

export type PipelineFlowNode = AgentPipelineRfNode | ToolPipelineRfNode;

const NEON = "#5fffb0";
const EDGE_DIM = "#52525e";

function edgeStyle(
  agents: Record<string, AgentStatus>,
  _sourceId: string,
  targetId: string
): { stroke: string; markerColor: string } {
  const st = agents[targetId];
  const glow =
    st === "in_progress" || st === "completed";
  return {
    stroke: glow ? "rgba(95, 255, 176, 0.45)" : EDGE_DIM,
    markerColor: glow ? NEON : EDGE_DIM,
  };
}

export function buildPipelineReactFlowElements(
  agents: Record<string, AgentStatus>,
  selectedAnalystKeys: PipelineAnalystKey[],
  focusedAgentId: string | null,
  toolCalls: ToolCallRecord[]
): { nodes: PipelineFlowNode[]; edges: Edge[] } {
  const { hub, branches } = getHubAndBranches(selectedAnalystKeys);

  const visibleIds = Object.entries(agents)
    .filter(([, st]) => isVisibleOnCanvas(st))
    .map(([id]) => id);

  const orderedVisibleIds = sortVisibleByPipeline(visibleIds, selectedAnalystKeys);
  const { positions, spineExitByAgent } = computePipelineBlockLayout(
    orderedVisibleIds,
    toolCalls
  );

  const agentHalfW = AGENT_NODE_WIDTH / 2;
  const agentHalfH = AGENT_NODE_HEIGHT / 2;
  const toolHalfW = TOOL_NODE_WIDTH / 2;
  const toolHalfH = TOOL_NODE_HEIGHT / 2;

  const nodes: PipelineFlowNode[] = [];

  for (const agentId of orderedVisibleIds) {
    const p = positions.get(agentId)!;
    const status = agents[agentId] ?? "pending";
    nodes.push({
      id: agentId,
      type: "agentPipeline" as const,
      position: {
        x: p.x - agentHalfW,
        y: p.y - agentHalfH,
      },
      width: AGENT_NODE_WIDTH,
      height: AGENT_NODE_HEIGHT,
      sourcePosition: Position.Bottom,
      targetPosition: Position.Top,
      data: {
        agentId,
        displayName: getDisplayName(agentId),
        roleLabel: getRoleLabel(agentId, status, hub, branches),
        status,
        focused: focusedAgentId === agentId,
      },
      zIndex: focusedAgentId === agentId ? 2 : 0,
    });

    const tools = toolCalls.filter((t) => t.agent === agentId);
    const toolGroups = groupContiguousToolCalls(agentId, tools);
    for (const g of toolGroups) {
      const nid = g.flowNodeId;
      const tp = positions.get(nid);
      if (!tp) continue;
      nodes.push({
        id: nid,
        type: "toolPipeline" as const,
        position: {
          x: tp.x - toolHalfW,
          y: tp.y - toolHalfH,
        },
        width: TOOL_NODE_WIDTH,
        height: TOOL_NODE_HEIGHT,
        sourcePosition: Position.Bottom,
        targetPosition: Position.Top,
        data: {
          toolName: g.tool_name,
          calls: g.calls,
          focused: focusedAgentId === nid,
        },
        zIndex: focusedAgentId === nid ? 2 : 0,
      });
    }
  }

  const edges: Edge[] = [];

  for (const agentId of orderedVisibleIds) {
    const tools = toolCalls.filter((t) => t.agent === agentId);
    const toolGroups = groupContiguousToolCalls(agentId, tools);
    for (const g of toolGroups) {
      const nid = g.flowNodeId;
      if (!positions.has(nid)) continue;
      const es = edgeStyle(agents, "", agentId);
      edges.push({
        id: `at-${agentId}-${g.calls[0]!.id}`,
        source: agentId,
        target: nid,
        sourceHandle: "tools-out",
        targetHandle: "from-agent",
        type: "smoothstep",
        animated: false,
        style: { stroke: es.stroke, strokeWidth: 1.5 },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: es.markerColor,
          width: 16,
          height: 16,
        },
      });
    }
  }

  for (let i = 0; i < orderedVisibleIds.length - 1; i++) {
    const fromAgent = orderedVisibleIds[i];
    const toAgent = orderedVisibleIds[i + 1];
    if (
      !isVisibleOnCanvas(agents[fromAgent]) ||
      !isVisibleOnCanvas(agents[toAgent])
    ) {
      continue;
    }
    const exitId = spineExitByAgent.get(fromAgent) ?? fromAgent;
    const es = edgeStyle(agents, exitId, toAgent);
    edges.push({
      id: `spine-${fromAgent}-${toAgent}`,
      source: exitId,
      target: toAgent,
      sourceHandle: "spine-out",
      targetHandle: "spine-in",
      type: "smoothstep",
      animated: agents[toAgent] === "in_progress",
      style: { stroke: es.stroke, strokeWidth: 1.5 },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: es.markerColor,
        width: 18,
        height: 18,
      },
    });
  }

  return { nodes, edges };
}
