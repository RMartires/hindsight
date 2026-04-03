import type { AgentStatus } from "@/lib/types";

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

/** Full edge list; filter with filterEdges + visible nodes */
export function buildAllEdges(selectedKeys: PipelineAnalystKey[]): EdgeDef[] {
  const edges: EdgeDef[] = [];
  const { hub, branches } = getHubAndBranches(selectedKeys);
  const lastA = getLastSelectedAnalystName(selectedKeys);

  if (hub && branches.length > 0) {
    for (const b of branches) {
      edges.push({ from: hub, to: b });
    }
  }

  if (lastA) {
    edges.push({ from: lastA, to: "Bull Researcher" });
    edges.push({ from: lastA, to: "Bear Researcher" });
  }

  edges.push({ from: "Bull Researcher", to: "Research Manager" });
  edges.push({ from: "Bear Researcher", to: "Research Manager" });
  edges.push({ from: "Research Manager", to: "Trader" });
  edges.push({ from: "Trader", to: "Aggressive Analyst" });
  edges.push({ from: "Trader", to: "Conservative Analyst" });
  edges.push({ from: "Trader", to: "Neutral Analyst" });
  edges.push({ from: "Aggressive Analyst", to: "Risk Judge" });
  edges.push({ from: "Conservative Analyst", to: "Risk Judge" });
  edges.push({ from: "Neutral Analyst", to: "Risk Judge" });

  return edges;
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

const COL_X = [140, 380, 600, 820, 1040, 1260, 1480];

/** Visible agent ids must include only in_progress | completed */
export function computeLayout(
  visibleIds: string[],
  hub: string | null,
  branches: string[]
): Map<string, LayoutPos> {
  const pos = new Map<string, LayoutPos>();
  const centerY = 200;

  if (hub && visibleIds.includes(hub)) {
    pos.set(hub, { x: COL_X[0], y: centerY });
  }

  const visBranches = branches.filter((id) => visibleIds.includes(id));
  const nB = visBranches.length;
  if (nB > 0) {
    const spacing = nB <= 1 ? 0 : 130;
    const startY = centerY - ((nB - 1) * spacing) / 2;
    visBranches.forEach((id, i) => {
      pos.set(id, { x: COL_X[1], y: nB === 1 ? centerY : startY + i * spacing });
    });
  }

  if (visibleIds.includes("Bull Researcher")) {
    pos.set("Bull Researcher", { x: COL_X[2], y: 110 });
  }
  if (visibleIds.includes("Bear Researcher")) {
    pos.set("Bear Researcher", { x: COL_X[2], y: 290 });
  }
  if (visibleIds.includes("Research Manager")) {
    pos.set("Research Manager", { x: COL_X[3], y: centerY });
  }
  if (visibleIds.includes("Trader")) {
    pos.set("Trader", { x: COL_X[4], y: centerY });
  }

  const riskIds = [
    "Aggressive Analyst",
    "Conservative Analyst",
    "Neutral Analyst",
  ];
  const visRisk = riskIds.filter((id) => visibleIds.includes(id));
  visRisk.forEach((id, i) => {
    pos.set(id, { x: COL_X[5], y: centerY - 90 + i * 90 });
  });

  if (visibleIds.includes("Risk Judge")) {
    pos.set("Risk Judge", { x: COL_X[6], y: centerY });
  }

  return pos;
}

export function computeViewBox(positions: Map<string, LayoutPos>): string {
  if (positions.size === 0) return "0 0 760 320";
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
  const w = Math.max(760, maxX - minX);
  const h = Math.max(320, maxY - minY);
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
