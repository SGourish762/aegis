export type Verdict = "allow" | "flag" | "block";
export type PolicyDecision = "allow" | "deny";

export interface ScreenResponse {
  verdict: Verdict;
  risk_score: number;
  categories: string[];
  reasons: string[];
}

export interface ProposedAction {
  tool: string;
  params: Record<string, unknown>;
}

export interface ActionResult {
  action: ProposedAction;
  decision: PolicyDecision;
  reason: string;
}

export interface AgentRunResponse {
  task: string;
  proposed_actions: ProposedAction[];
  results: ActionResult[];
}

export interface AuditRecordOut {
  id: number;
  created_at: string;
  kind: "screen" | "agent_run";
  verdict: string;
  risk_score: number | null;
  input_summary: string;
  categories: string[];
  reasons: string[];
}

export interface AuditRecordDetail extends AuditRecordOut {
  detail: Record<string, unknown>;
}

export interface AuditListResponse {
  items: AuditRecordOut[];
  total: number;
  limit: number;
  offset: number;
}

export interface StatsTimeSeriesPoint {
  date: string;
  count: number;
  blocked: number;
}

export interface StatsResponse {
  total: number;
  by_kind: Record<string, number>;
  by_verdict: Record<string, number>;
  block_rate: number;
  category_breakdown: Record<string, number>;
  time_series: StatsTimeSeriesPoint[];
}
