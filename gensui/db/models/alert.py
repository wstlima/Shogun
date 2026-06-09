"""Alert model — detected policy violations and system alerts."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from gensui.db.base import Base, UUIDMixin, GUID, JSONType


class Alert(Base, UUIDMixin):
    """An alert triggered by a policy violation or system event."""

    __tablename__ = "alerts"

    # ── Classification ───────────────────────────────────────
    # INFO | LOW | MEDIUM | HIGH | CRITICAL
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="MEDIUM")
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # ── Source ───────────────────────────────────────────────
    shogun_id: Mapped[str | None] = mapped_column(GUID(), nullable=True, index=True)
    samurai_id: Mapped[str | None] = mapped_column(GUID(), nullable=True)

    # ── Content ──────────────────────────────────────────────
    description: Mapped[str] = mapped_column(String(2000), nullable=False)
    recommended_action: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # ── Links ────────────────────────────────────────────────
    linked_policy_decision_id: Mapped[str | None] = mapped_column(GUID(), nullable=True)
    linked_telemetry_event_id: Mapped[str | None] = mapped_column(GUID(), nullable=True)

    # ── Status ───────────────────────────────────────────────
    # active | acknowledged | resolved | dismissed
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    resolved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # ── Timestamp ────────────────────────────────────────────
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
