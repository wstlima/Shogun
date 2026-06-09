"""Telemetry event model — structured events from member Shoguns."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from gensui.db.base import Base, UUIDMixin, GUID, JSONType


class TelemetryEvent(Base, UUIDMixin):
    """A telemetry event received from a member Shogun."""

    __tablename__ = "telemetry_events"

    # ── Source ───────────────────────────────────────────────
    shogun_id: Mapped[str] = mapped_column(GUID(), nullable=False, index=True)
    samurai_id: Mapped[str | None] = mapped_column(GUID(), nullable=True)
    workflow_id: Mapped[str | None] = mapped_column(GUID(), nullable=True)
    nexus_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ── Event Classification ─────────────────────────────────
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # info | warn | error | critical
    severity: Mapped[str] = mapped_column(String(20), nullable=False, default="info")

    # ── Payload ──────────────────────────────────────────────
    payload_json: Mapped[dict | None] = mapped_column(JSONType(), nullable=True)
    redacted_payload_json: Mapped[dict | None] = mapped_column(JSONType(), nullable=True)

    # ── Policy ───────────────────────────────────────────────
    policy_decision_id: Mapped[str | None] = mapped_column(GUID(), nullable=True)

    # ── Timestamps ───────────────────────────────────────────
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
