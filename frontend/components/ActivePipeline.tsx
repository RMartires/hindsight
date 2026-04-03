"use client";

import type {
  AgentStatus,
  PipelineTopologyEvent,
  StreamStatus,
  ToolCallRecord,
} from "@/lib/types";
import type { PipelineAnalystKey } from "@/lib/pipelineGraph";
import AgentReactFlow from "./AgentReactFlow";

interface Props {
  agents: Record<string, AgentStatus>;
  status: StreamStatus;
  selectedAnalystKeys: PipelineAnalystKey[];
  pipelineTopology: PipelineTopologyEvent | null;
  selectedAgentId: string | null;
  onSelectAgent: (agentId: string | null) => void;
  toolCalls: ToolCallRecord[];
}

const SUBTITLE = "Forensic Analysis of Liquidity Cascades";

export default function ActivePipeline({
  agents,
  status,
  selectedAnalystKeys,
  pipelineTopology,
  selectedAgentId,
  onSelectAgent,
  toolCalls,
}: Props) {
  return (
    <section className="panel panel--center pipeline-panel">
      <AgentReactFlow
        agents={agents}
        selectedAnalystKeys={selectedAnalystKeys}
        subtitle={SUBTITLE}
        streamStatus={status}
        pipelineTopology={pipelineTopology}
        selectedAgentId={selectedAgentId}
        onSelectAgent={onSelectAgent}
        toolCalls={toolCalls}
      />
    </section>
  );
}
