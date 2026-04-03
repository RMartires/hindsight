"use client";

import type { AgentStatus } from "@/lib/types";
import type { StreamStatus } from "@/lib/types";
import AgentFlowchart from "./AgentFlowchart";

interface Props {
  agents: Record<string, AgentStatus>;
  status: StreamStatus;
}

const SUBTITLE = "Forensic Analysis of Liquidity Cascades";

export default function ActivePipeline({ agents, status }: Props) {
  const idleAgents: Record<string, AgentStatus> = {
    "Market Analyst": "pending",
    "Fundamentals Analyst": "pending",
    "News Analyst": "pending",
  };

  const chartAgents = status === "idle" ? idleAgents : agents;

  return (
    <section className="panel panel--center pipeline-panel">
      <AgentFlowchart agents={chartAgents} subtitle={SUBTITLE} />
      <button
        type="button"
        className="pipeline-fab"
        aria-label="Quick action"
        title="Pipeline pulse"
      >
        ⚡
      </button>
    </section>
  );
}
