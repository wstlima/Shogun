"""Command model — pending commands for Shogun instances to poll and execute."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from gensui.db.base import Base, UUIDMixin, GUID, JSONType


class Command(Base, UUIDMixin):
    """A pending command queued for a specific Shogun instance."""

    __tablename__ = "commands"

    # ── Target ───────────────────────────────────────────────
    shogun_id: Mapped[str] = mapped_column(GUID(), nullable=False, index=True)

    # ── Command ──────────────────────────────────────────────
    # posture_update | harakiri | policy_sync | credential_rotate | custom
    command_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload_json: Mapped[dict | None] = mapped_column(JSONType(), nullable=True)

    # ── Status ───────────────────────────────────────────────
    # pending | acknowledged | executing | completed | failed | expired
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    result_json: Mapped[dict | None] = mapped_column(JSONType(), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    # ── Timestamps ───────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
