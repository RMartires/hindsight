import type {
  ActivityLogEntry,
  AgentStatus,
  DebateEvent,
  DecisionEvent,
  ToolCallRecord,
} from "@/lib/types";
import type { PipelineAnalystKey } from "@/lib/pipelineGraph";
import {
  getDisplayName,
  isVisibleOnCanvas,
  sortVisibleByPipeline,
  toolFlowNodeId,
} from "@/lib/pipelineGraph";

export type LiveTileKind = "agent" | "tool";

export interface LiveTile {
  id: string;
  kind: LiveTileKind;
  title: string;
  subtitle: string;
  body: string;
}

/** Analyst / Trader → streamed report section */
const AGENT_TO_REPORT: Record<string, string> = {
  "Market Analyst": "market_report",
  "Social Analyst": "sentiment_report",
  "News Analyst": "news_report",
  "Fundamentals Analyst": "fundamentals_report",
};

function formatToolCall(t: ToolCallRecord): string {
  const lines = [
    `Tool: ${t.tool_name}`,
    `Agent: ${t.agent}`,
    t.time ? `Time: ${t.time}` : "",
    "",
    "Input:",
    t.input ?? "—",
    "",
    "Output:",
    t.output ?? "—",
  ].filter(Boolean);
  return lines.join("\n");
}

function formatDebatesForSpeaker(
  speaker: string,
  debates: DebateEvent[]
): string {
  const rows = debates.filter((d) => d.speaker === speaker);
  if (!rows.length) return "";
  return rows
    .map(
      (d, i) =>
        `## ${d.phase} (${i + 1}/${rows.length})\n\n${d.content}`
    )
    .join("\n\n---\n\n");
}

function activityHint(
  agentId: string,
  activityLog: ActivityLogEntry[]
): string {
  const lines = activityLog.filter(
    (e) =>
      e.message.includes(agentId) || e.message.startsWith(`${agentId}:`)
  );
  if (!lines.length) return "";
  return lines.map((l) => `• ${l.message}`).join("\n");
}

function agentBody(
  agentId: string,
  status: AgentStatus,
  reports: Record<string, string>,
  debates: DebateEvent[],
  decision: DecisionEvent | null,
  activityLog: ActivityLogEntry[]
): string {
  const reportKey = AGENT_TO_REPORT[agentId];
  if (reportKey && reports[reportKey]?.trim()) {
    return reports[reportKey];
  }

  if (agentId === "Trader" && reports.trader_investment_plan?.trim()) {
    return reports.trader_investment_plan;
  }

  const debateText = formatDebatesForSpeaker(agentId, debates);
  if (debateText) {
    if (agentId === "Risk Judge" && decision?.full_text?.trim()) {
      return `${debateText}\n\n---\n\n## Final decision\n\n${decision.full_text}`;
    }
    return debateText;
  }

  if (agentId === "Risk Judge" && decision?.full_text?.trim()) {
    return decision.full_text;
  }

  const hint = activityHint(agentId, activityLog);
  if (hint) {
    return `Status: ${status}\n\nActivity:\n${hint}`;
  }

  return `Status: ${status}\n\nNo detailed output yet.`;
}

function agentSubtitle(status: AgentStatus): string {
  if (status === "in_progress") return "In progress";
  if (status === "completed") return "Complete";
  return "Pending";
}

function toolSubtitle(t: ToolCallRecord): string {
  const time = t.time ? t.time : "";
  return [t.agent, time].filter(Boolean).join(" · ");
}

/**
 * Tiles in the same order as the pipeline graph: each visible agent row,
 * then its tool calls left-to-right.
 */
export function buildLiveTiles(
  agents: Record<string, AgentStatus>,
  selectedKeys: PipelineAnalystKey[],
  toolCalls: ToolCallRecord[],
  reports: Record<string, string>,
  debates: DebateEvent[],
  decision: DecisionEvent | null,
  activityLog: ActivityLogEntry[]
): LiveTile[] {
  const visibleIds = Object.entries(agents)
    .filter(([, st]) => isVisibleOnCanvas(st))
    .map(([id]) => id);

  const orderedAgents = sortVisibleByPipeline(visibleIds, selectedKeys);
  const tiles: LiveTile[] = [];

  for (const agentId of orderedAgents) {
    const status = agents[agentId] ?? "pending";
    tiles.push({
      id: agentId,
      kind: "agent",
      title: getDisplayName(agentId),
      subtitle: agentSubtitle(status),
      body: agentBody(
        agentId,
        status,
        reports,
        debates,
        decision,
        activityLog
      ),
    });

    for (const t of toolCalls.filter((c) => c.agent === agentId)) {
      tiles.push({
        id: toolFlowNodeId(t.id),
        kind: "tool",
        title: t.tool_name,
        subtitle: toolSubtitle(t),
        body: formatToolCall(t),
      });
    }
  }

  return tiles;
}
