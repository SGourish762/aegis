"""Audit log persistence. DB-agnostic: swap the backing store by changing
DB_URL (SQLite locally, Postgres in prod) — nothing above this module knows
or cares which one is in use.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.audit.models import AuditRecord, Base
from app.config import DB_URL as DEFAULT_DB_URL

_engine = None
_SessionLocal = None


def _make_engine(db_url: str):
    connect_args = {"check_same_thread": False} if db_url.startswith("sqlite") else {}
    return create_engine(db_url, connect_args=connect_args)


def init_db(db_url: Optional[str] = None) -> None:
    """Initialize (or re-initialize) the engine/session and create tables.

    Called once at app startup. Tests pass an isolated sqlite URL so they
    never touch the dev DB file.
    """
    global _engine, _SessionLocal
    _engine = _make_engine(db_url or DEFAULT_DB_URL)
    _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)
    Base.metadata.create_all(_engine)


def _session() -> Session:
    if _SessionLocal is None:
        init_db()
    return _SessionLocal()


def _summarize(text: str, limit: int = 300) -> str:
    text = text.strip()
    return text if len(text) <= limit else text[:limit] + "…"


def record_screen(text: str, response) -> AuditRecord:
    with _session() as s:
        rec = AuditRecord(
            kind="screen",
            verdict=response.verdict,
            risk_score=response.risk_score,
            input_summary=_summarize(text),
            categories=response.categories,
            reasons=response.reasons,
            detail=response.model_dump(),
        )
        s.add(rec)
        s.commit()
        s.refresh(rec)
        return rec


def _agent_verdict(results) -> str:
    decisions = {r.decision for r in results}
    if decisions == {"allow"}:
        return "allow"
    if decisions == {"deny"}:
        return "deny"
    return "mixed"


def record_agent_run(task: str, results) -> AuditRecord:
    categories = sorted({r.action.tool for r in results})
    reasons = [r.reason for r in results]
    with _session() as s:
        rec = AuditRecord(
            kind="agent_run",
            verdict=_agent_verdict(results),
            risk_score=None,
            input_summary=_summarize(task),
            categories=categories,
            reasons=reasons,
            detail={"task": task, "results": [r.model_dump() for r in results]},
        )
        s.add(rec)
        s.commit()
        s.refresh(rec)
        return rec


def list_audit(
    kind: Optional[str] = None,
    verdict: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[AuditRecord], int]:
    with _session() as s:
        stmt = select(AuditRecord).order_by(AuditRecord.created_at.desc())
        if kind:
            stmt = stmt.where(AuditRecord.kind == kind)
        if verdict:
            stmt = stmt.where(AuditRecord.verdict == verdict)
        rows = list(s.scalars(stmt))
        if category:
            rows = [r for r in rows if category in (r.categories or [])]
        total = len(rows)
        page = rows[offset : offset + limit]
        return page, total


def get_audit(record_id: int) -> Optional[AuditRecord]:
    with _session() as s:
        return s.get(AuditRecord, record_id)


def get_stats(days: int = 14) -> dict:
    with _session() as s:
        rows = list(s.scalars(select(AuditRecord)))

    total = len(rows)
    by_kind: dict[str, int] = {}
    by_verdict: dict[str, int] = {}
    category_counts: dict[str, int] = {}
    for r in rows:
        by_kind[r.kind] = by_kind.get(r.kind, 0) + 1
        by_verdict[r.verdict] = by_verdict.get(r.verdict, 0) + 1
        for c in r.categories or []:
            category_counts[c] = category_counts.get(c, 0) + 1

    screen_total = by_kind.get("screen", 0)
    blocked = by_verdict.get("block", 0)
    block_rate = (blocked / screen_total) if screen_total else 0.0

    since = datetime.now(timezone.utc) - timedelta(days=days)
    buckets: dict[str, dict[str, int]] = {}
    for r in rows:
        created = r.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        if created < since:
            continue
        day = created.date().isoformat()
        b = buckets.setdefault(day, {"count": 0, "blocked": 0})
        b["count"] += 1
        if r.verdict in ("block", "deny"):
            b["blocked"] += 1
    time_series = [
        {"date": day, "count": v["count"], "blocked": v["blocked"]}
        for day, v in sorted(buckets.items())
    ]

    return {
        "total": total,
        "by_kind": by_kind,
        "by_verdict": by_verdict,
        "block_rate": round(block_rate, 4),
        "category_breakdown": category_counts,
        "time_series": time_series,
    }
