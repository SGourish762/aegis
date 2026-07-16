import type {
  AgentRunResponse,
  AuditListResponse,
  AuditRecordDetail,
  ScreenResponse,
  StatsResponse,
} from "./types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!resp.ok) {
    const body = await resp.text();
    throw new Error(`${resp.status} ${resp.statusText}: ${body}`);
  }
  return resp.json() as Promise<T>;
}

export function screenText(text: string): Promise<ScreenResponse> {
  return request<ScreenResponse>("/screen", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export function runAgent(task: string): Promise<AgentRunResponse> {
  return request<AgentRunResponse>("/agent/run", {
    method: "POST",
    body: JSON.stringify({ task }),
  });
}

export interface AuditFilters {
  kind?: string;
  verdict?: string;
  category?: string;
  limit?: number;
  offset?: number;
}

export function listAudit(filters: AuditFilters = {}): Promise<AuditListResponse> {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== "") params.set(key, String(value));
  }
  const qs = params.toString();
  return request<AuditListResponse>(`/audit${qs ? `?${qs}` : ""}`);
}

export function getAuditRecord(id: number): Promise<AuditRecordDetail> {
  return request<AuditRecordDetail>(`/audit/${id}`);
}

export function getStats(): Promise<StatsResponse> {
  return request<StatsResponse>("/stats");
}
