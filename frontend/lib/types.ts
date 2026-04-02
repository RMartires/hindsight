export type AgentStatus = "pending" | "in_progress" | "completed";

export interface AgentStatusEvent {
  agent: string;
  status: AgentStatus;
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

export interface StreamState {
  status: StreamStatus;
  agents: Record<string, AgentStatus>;
  reports: Record<string, string>;
  debates: DebateEvent[];
  decision: DecisionEvent | null;
  traceId: string | null;
  error: string | null;
}
