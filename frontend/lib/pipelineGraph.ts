import type { AgentStatus, ToolCallRecord } from "@/lib/types";

/** Mirrors backend/stream_handler.py ANALYST_ORDER */
export type PipelineAnalystKey = "market" | "fundamentals" | "news" | "social";

export const ANALYST_ORDER: PipelineAnalystKey[] = [
  "market",
  "social",
  "news",
  "fundamentals",
];

export const ANALYST_AGENT_NAMES: Record<PipelineAnalystKey, string> = {
  market: "Market Analyst",
  social: "Social Analyst",
  news: "News Analyst",
  fundamentals: "Fundamentals Analyst",
};

/** Card titles (design parity for News) */
export const PIPELINE_DISPLAY_NAMES: Record<string, string> = {
  "News Analyst": "Technical Analyst",
};

export const DOWNSTREAM_AGENT_IDS = [
  "Bull Researcher",
  "Bear Researcher",
  "Research Manager",
  "Trader",
  "Aggressive Analyst",
  "Conservative Analyst",
  "Neutral Analyst",
  "Risk Judge",
] as const;

/** Shown under SYNTHESIS PHASE (debate); skip duplicate agent tiles in LIVE REPORT once debates stream in. */
export const LIVE_REPORT_DEBATE_SYNTHESIS_AGENT_IDS: ReadonlySet<string> =
  new Set([
    "Bull Researcher",
    "Bear Researcher",
    "Research Manager",
    "Aggressive Analyst",
    "Conservative Analyst",
    "Neutral Analyst",
    "Risk Judge",
  ]);

export interface EdgeDef {
  from: string;
  to: string;
}

export function isVisibleOnCanvas(status: AgentStatus | undefined): boolean {
  return status === "in_progress" || status === "completed";
}

export function selectedToOrderedAnalysts(
  keys: PipelineAnalystKey[]
): PipelineAnalystKey[] {
  return ANALYST_ORDER.filter((k) => keys.includes(k));
}

export function getHubAndBranches(selectedKeys: PipelineAnalystKey[]): {
  hub: string | null;
  branches: string[];
} {
  const ordered = selectedToOrderedAnalysts(selectedKeys);
  if (ordered.length === 0) {
    return { hub: null, branches: [] };
  }
  const hubName = ANALYST_AGENT_NAMES[ordered[0]];
  const branches = ordered.slice(1).map((k) => ANALYST_AGENT_NAMES[k]);
  return { hub: hubName, branches };
}

export function getLastSelectedAnalystName(
  selectedKeys: PipelineAnalystKey[]
): string | null {
  const ordered = selectedToOrderedAnalysts(selectedKeys);
  if (ordered.length === 0) return null;
  return ANALYST_AGENT_NAMES[ordered[ordered.length - 1]];
}

export function getDisplayName(agentId: string): string {
  return PIPELINE_DISPLAY_NAMES[agentId] ?? agentId;
}

/**
 * Full ordered list of agents for this run (analysts in UI order, then fixed tail).
 * Used for sequential edges and vertical tree layout.
 */
export function getPipelineOrder(selectedKeys: PipelineAnalystKey[]): string[] {
  const analysts = selectedToOrderedAnalysts(selectedKeys).map(
    (k) => ANALYST_AGENT_NAMES[k]
  );
  return [...analysts, ...DOWNSTREAM_AGENT_IDS];
}

/** One edge per consecutive pair: 1→2→3→… (no hub/fan, no LangGraph crossings). */
export function buildSequentialEdges(selectedKeys: PipelineAnalystKey[]): EdgeDef[] {
  const order = getPipelineOrder(selectedKeys);
  const edges: EdgeDef[] = [];
  for (let i = 0; i < order.length - 1; i++) {
    edges.push({ from: order[i], to: order[i + 1] });
  }
  return edges;
}

/** @deprecated Prefer buildSequentialEdges; kept for any legacy imports */
export function buildAllEdges(selectedKeys: PipelineAnalystKey[]): EdgeDef[] {
  return buildSequentialEdges(selectedKeys);
}

/** Visible nodes ordered along the pipeline (stable top-to-bottom). */
export function sortVisibleByPipeline(
  visibleIds: string[],
  selectedKeys: PipelineAnalystKey[]
): string[] {
  const want = new Set(visibleIds);
  return getPipelineOrder(selectedKeys).filter((id) => want.has(id));
}

export function filterEdges(
  edges: EdgeDef[],
  agents: Record<string, AgentStatus>
): EdgeDef[] {
  return edges.filter(
    (e) =>
      isVisibleOnCanvas(agents[e.from]) && isVisibleOnCanvas(agents[e.to])
  );
}

export interface LayoutPos {
  x: number;
  y: number;
}

/** Horizontal center of the vertical spine */
const TREE_CENTER_X = 320;
/** Y of the first (root) node */
const TREE_START_Y = 90;
/** Vertical gap between node centers (node card ~92px tall) */
const TREE_STEP_Y = 128;

/**
 * Vertical tree spine: step 0 at the top, last step at the bottom.
 * `orderedVisibleIds` must already be sorted via sortVisibleByPipeline.
 */
export function computeLayout(orderedVisibleIds: string[]): Map<string, LayoutPos> {
  const pos = new Map<string, LayoutPos>();
  orderedVisibleIds.forEach((id, i) => {
    pos.set(id, {
      x: TREE_CENTER_X,
      y: TREE_START_Y + i * TREE_STEP_Y,
    });
  });
  return pos;
}

/** React Flow node id for a single tool row (legacy / non-grouped references). */
export function toolFlowNodeId(toolCallId: string): string {
  return `tool:${toolCallId}`;
}

/** One or more contiguous SSE tool calls with the same `tool_name` for one agent row. */
export interface ToolCallGroup {
  flowNodeId: string;
  agent: string;
  tool_name: string;
  calls: ToolCallRecord[];
}

export function toolGroupFlowNodeId(agentId: string, firstCallId: string): string {
  return `tool-group:${agentId}:${firstCallId}`;
}

/**
 * Merge consecutive tool calls that share the same `tool_name` (same agent row).
 * Order matches `toolCalls` stream order.
 */
export function groupContiguousToolCalls(
  agentId: string,
  calls: ToolCallRecord[]
): ToolCallGroup[] {
  const groups: ToolCallGroup[] = [];
  for (const t of calls) {
    const prev = groups[groups.length - 1];
    if (prev && prev.tool_name === t.tool_name) {
      prev.calls.push(t);
    } else {
      groups.push({
        flowNodeId: toolGroupFlowNodeId(agentId, t.id),
        agent: agentId,
        tool_name: t.tool_name,
        calls: [t],
      });
    }
  }
  return groups;
}

/** Match `pipelineToReactFlow` node widths (centers used in layout). */
const LAYOUT_AGENT_W = 208;
const LAYOUT_TOOL_W = 210;
const ROW_MARGIN_LEFT = 48;
const ROW_TOOL_GAP = 18;
/** Vertical distance between row centerlines (agent + tools share one rowY). */
const ROW_STEP_Y = 132;

/**
 * One row per agent: agent on the left, all its tool nodes to the right on the same Y.
 * Next agent (and its tools) starts on the row below.
 */
export function computePipelineBlockLayout(
  orderedVisibleAgentIds: string[],
  toolCalls: ToolCallRecord[]
): { positions: Map<string, LayoutPos>; spineExitByAgent: Map<string, string> } {
  const positions = new Map<string, LayoutPos>();
  const spineExitByAgent = new Map<string, string>();
  const visible = new Set(orderedVisibleAgentIds);

  let rowIndex = 0;
  for (const agentId of orderedVisibleAgentIds) {
    const rowY = TREE_START_Y + rowIndex * ROW_STEP_Y;

    const tools = toolCalls.filter(
      (t) => t.agent === agentId && visible.has(agentId)
    );
    const toolGroups = groupContiguousToolCalls(agentId, tools);

    const agentCx = ROW_MARGIN_LEFT + LAYOUT_AGENT_W / 2;
    positions.set(agentId, { x: agentCx, y: rowY });

    let cursorLeft = ROW_MARGIN_LEFT + LAYOUT_AGENT_W + ROW_TOOL_GAP;
    let exitId = agentId;

    for (const g of toolGroups) {
      const tcx = cursorLeft + LAYOUT_TOOL_W / 2;
      positions.set(g.flowNodeId, { x: tcx, y: rowY });
      cursorLeft += LAYOUT_TOOL_W + ROW_TOOL_GAP;
      exitId = g.flowNodeId;
    }

    spineExitByAgent.set(agentId, exitId);
    rowIndex += 1;
  }

  return { positions, spineExitByAgent };
}

export function computeViewBox(positions: Map<string, LayoutPos>): string {
  if (positions.size === 0) return "0 0 640 720";
  let minX = Infinity;
  let maxX = -Infinity;
  let minY = Infinity;
  let maxY = -Infinity;
  const halfW = 104;
  const halfH = 50;
  for (const p of positions.values()) {
    minX = Math.min(minX, p.x - halfW);
    maxX = Math.max(maxX, p.x + halfW);
    minY = Math.min(minY, p.y - halfH);
    maxY = Math.max(maxY, p.y + halfH);
  }
  const pad = 48;
  minX -= pad;
  maxX += pad;
  minY -= pad;
  maxY += pad;
  const w = Math.max(480, maxX - minX);
  const h = Math.max(400, maxY - minY);
  return `${minX} ${minY} ${w} ${h}`;
}

export function getRoleLabel(
  agentId: string,
  status: AgentStatus,
  hubId: string | null,
  branchIds: string[]
): string {
  if (agentId === hubId) return "INGESTOR";
  if (branchIds.includes(agentId)) {
    if (status === "in_progress") return "ACTIVE ANALYSIS";
    if (status === "completed") return "COMPLETE";
    return "PROCESSING";
  }
  if (
    agentId === "Bull Researcher" ||
    agentId === "Bear Researcher" ||
    agentId === "Research Manager"
  ) {
    if (status === "in_progress") return "ACTIVE ANALYSIS";
    if (status === "completed") return "COMPLETE";
    return "PROCESSING";
  }
  if (agentId === "Trader") {
    if (status === "in_progress") return "ACTIVE ANALYSIS";
    if (status === "completed") return "COMPLETE";
    return "PROCESSING";
  }
  if (
    agentId === "Aggressive Analyst" ||
    agentId === "Conservative Analyst" ||
    agentId === "Neutral Analyst"
  ) {
    if (status === "in_progress") return "RISK DEBATE";
    if (status === "completed") return "COMPLETE";
    return "PROCESSING";
  }
  if (agentId === "Risk Judge") {
    if (status === "in_progress") return "JUDGMENT";
    if (status === "completed") return "COMPLETE";
    return "PROCESSING";
  }
  if (status === "in_progress") return "ACTIVE ANALYSIS";
  if (status === "completed") return "COMPLETE";
  return "PROCESSING";
}
