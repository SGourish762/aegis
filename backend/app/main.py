from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.agent.demo_agent import propose_actions
from app.audit import store as audit_store
from app.detection.engine import screen
from app.policy.engine import evaluate_all
from app.schemas import (
    AgentRunRequest,
    AgentRunResponse,
    AuditListResponse,
    AuditRecordDetail,
    AuditRecordOut,
    ScreenRequest,
    ScreenResponse,
    StatsResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    audit_store.init_db()
    yield


app = FastAPI(
    title="Aegis",
    description="AI-agent guardrail layer: prompt-injection screening and action policy enforcement.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/screen", response_model=ScreenResponse)
def screen_text(req: ScreenRequest) -> ScreenResponse:
    result = screen(req.text)
    audit_store.record_screen(req.text, result)
    return result


@app.post("/agent/run", response_model=AgentRunResponse)
def agent_run(req: AgentRunRequest) -> AgentRunResponse:
    actions = propose_actions(req.task)
    results = evaluate_all(actions)
    audit_store.record_agent_run(req.task, results)
    return AgentRunResponse(task=req.task, proposed_actions=actions, results=results)


@app.get("/audit", response_model=AuditListResponse)
def list_audit(
    kind: Optional[str] = None,
    verdict: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> AuditListResponse:
    rows, total = audit_store.list_audit(
        kind=kind, verdict=verdict, category=category, limit=limit, offset=offset
    )
    return AuditListResponse(
        items=[AuditRecordOut.model_validate(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@app.get("/audit/{record_id}", response_model=AuditRecordDetail)
def get_audit(record_id: int) -> AuditRecordDetail:
    record = audit_store.get_audit(record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Audit record not found")
    return AuditRecordDetail.model_validate(record)


@app.get("/stats", response_model=StatsResponse)
def stats() -> StatsResponse:
    return StatsResponse(**audit_store.get_stats())
