from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

Verdict = Literal["allow", "flag", "block"]
PolicyDecision = Literal["allow", "deny"]


class ScreenRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=20000)
    context: Optional[str] = None


class ScreenResponse(BaseModel):
    verdict: Verdict
    risk_score: float
    categories: list[str]
    reasons: list[str]


class ProposedAction(BaseModel):
    tool: str
    params: dict[str, Any] = Field(default_factory=dict)


class ActionResult(BaseModel):
    action: ProposedAction
    decision: PolicyDecision
    reason: str


class AgentRunRequest(BaseModel):
    task: str = Field(..., min_length=1, max_length=2000)


class AgentRunResponse(BaseModel):
    task: str
    proposed_actions: list[ProposedAction]
    results: list[ActionResult]


class AuditRecordOut(BaseModel):
    id: int
    created_at: datetime
    kind: Literal["screen", "agent_run"]
    verdict: str
    risk_score: Optional[float]
    input_summary: str
    categories: list[str]
    reasons: list[str]

    model_config = {"from_attributes": True}


class AuditRecordDetail(AuditRecordOut):
    detail: dict[str, Any]


class AuditListResponse(BaseModel):
    items: list[AuditRecordOut]
    total: int
    limit: int
    offset: int


class StatsTimeSeriesPoint(BaseModel):
    date: str
    count: int
    blocked: int


class StatsResponse(BaseModel):
    total: int
    by_kind: dict[str, int]
    by_verdict: dict[str, int]
    block_rate: float
    category_breakdown: dict[str, int]
    time_series: list[StatsTimeSeriesPoint]
