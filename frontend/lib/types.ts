export type AgentStatus = "pending" | "in_progress" | "completed";

export interface AgentStatusEvent {
  agent: string;
  status: AgentStatus;
  /** ISO-8601 timestamp from the server when status changed */
  time?: string;
}

export interface PipelineTopologyNode {
  id: string;
  label: string;
}

export interface PipelineTopologyEdge {
  from: string;
  to: string;
}

export interface PipelineTopologyEvent {
  nodes: PipelineTopologyNode[];
  edges: PipelineTopologyEdge[];
  source: string;
  raw_node_count?: number;
  raw_edge_count?: number;
}

export interface GraphStepEvent {
  node_id: string;
  time?: string;
}

/** One completed tool invocation (from SSE `tool_call`). */
export interface ToolCallRecord {
  id: string;
  agent: string;
  tool_name: string;
  input: string | null;
  output: string | null;
  time?: string;
}

/** One LLM completion with token counts (from SSE `llm_usage`). */
export interface LlmUsageEvent {
  agent: string;
  node_id?: string;
  input_tokens: number;
  output_tokens: number;
  time?: string;
  run_input_tokens: number;
  run_output_tokens: number;
  estimated_usd_delta?: number | null;
  estimated_usd_run?: number | null;
}

export interface TokenUsageTotals {
  input_tokens: number;
  output_tokens: number;
  estimated_usd: number | null;
}

export interface ReportEvent {
  section: string;
  content: string;
}

export interface DebateEvent {
  phase: "investment" | "risk";
  speaker: string;
  content: string;
}

export interface DecisionEvent {
  final: string;
  full_text: string;
  investment_plan: string;
}

export interface ErrorEvent {
  message: string;
}

export interface DoneEvent {
  trace_id: string;
}

export interface AnalyzeResponse {
  run_id: string;
  trace_id: string | null;
  session_id: string | null;
}

export type StreamStatus = "idle" | "connecting" | "streaming" | "done" | "error";

export interface ActivityLogEntry {
  at: string; // ISO timestamp (client-side)
  message: string;
}

export interface StreamState {
  status: StreamStatus;
  agents: Record<string, AgentStatus>;
  reports: Record<string, string>;
  debates: DebateEvent[];
  decision: DecisionEvent | null;
  traceId: string | null;
  runId: string | null;
  sessionId: string | null;
  activityLog: ActivityLogEntry[];
  error: string | null;
  /** LangGraph-derived edges for this run (normalized on the server). */
  pipelineTopology: PipelineTopologyEvent | null;
  /** Last single-node stream hint when the backend detects an isolated chunk key. */
  lastGraphStep: GraphStepEvent | null;
  /** Tool invocations attributed to an agent (for graph + drill-down). */
  toolCalls: ToolCallRecord[];
  /** Per-completion usage from the backend (deduped by message id when present). */
  llmUsages: LlmUsageEvent[];
  /** Running totals after the last `llm_usage` event (and restored from cache). */
  tokenUsageTotals: TokenUsageTotals;
}
