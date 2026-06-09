"""AgentFlowRun ORM model — tracks a single execution of an Agent Flow."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from shogun.db.base import AuditMixin, Base, GUID, JSONType, UUIDMixin


class AgentFlowRun(Base, UUIDMixin, AuditMixin):
    """A single execution run of an Agent Flow."""

    __tablename__ = "agent_flow_runs"

    flow_id: Mapped[str] = mapped_column(
        GUID(), ForeignKey("agent_flows.id", ondelete="CASCADE"), nullable=False,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    trigger_type: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")

    # Per-node execution state: { node_id: { status, output, error, started_at, completed_at } }
    node_states: Mapped[dict] = mapped_column(JSONType(), nullable=False, default=dict)

    # Final aggregated results
    result_summary: Mapped[dict] = mapped_column(JSONType(), nullable=False, default=dict)

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Error info
    error_message: Mapped[str | None] = mapped_column(String(2000), nullable=True)
