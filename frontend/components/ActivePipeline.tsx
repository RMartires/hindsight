"use client";

import type { AgentStatus } from "@/lib/types";
import type { StreamStatus } from "@/lib/types";
import type { PipelineAnalystKey } from "@/lib/pipelineGraph";
import AgentFlowchart from "./AgentFlowchart";

interface Props {
  agents: Record<string, AgentStatus>;
  status: StreamStatus;
  selectedAnalystKeys: PipelineAnalystKey[];
}

const SUBTITLE = "Forensic Analysis of Liquidity Cascades";

export default function ActivePipeline({
  agents,
  status,
  selectedAnalystKeys,
}: Props) {
  return (
    <section className="panel panel--center pipeline-panel">
      <AgentFlowchart
        agents={agents}
        selectedAnalystKeys={selectedAnalystKeys}
        subtitle={SUBTITLE}
        streamStatus={status}
      />
      <button
        type="button"
        className="pipeline-fab"
        aria-label="Quick action"
        title="Pipeline pulse"
      >
        <span className="pipeline-fab-bolt">⚡</span>
      </button>
    </section>
  );
}
