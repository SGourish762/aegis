from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AuditRecord(Base):
    """One row per screened input or agent run.

    ``detail`` holds the full response payload (ScreenResponse or
    AgentRunResponse as a dict) so /audit/{id} can show a full drill-down
    without a second table per record kind.
    """

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    kind: Mapped[str] = mapped_column(String(20), index=True)  # "screen" | "agent_run"
    verdict: Mapped[str] = mapped_column(String(20), index=True)
    risk_score: Mapped[float] = mapped_column(Float, nullable=True)
    input_summary: Mapped[str] = mapped_column(String(500))
    categories: Mapped[list] = mapped_column(JSON, default=list)
    reasons: Mapped[list] = mapped_column(JSON, default=list)
    detail: Mapped[dict] = mapped_column(JSON, default=dict)
