"""Audit log model — HMAC-chained append-only audit trail."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from gensui.db.base import Base, UUIDMixin, JSONType


class AuditLog(Base, UUIDMixin):
    """An append-only, HMAC-chained audit log entry."""

    __tablename__ = "audit_log"

    # ── Actor ────────────────────────────────────────────────
    # admin | shogun | system
    actor_type: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ── Action ───────────────────────────────────────────────
    action: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    target_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    target_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ── Context ──────────────────────────────────────────────
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # ── Before/After state snapshots ─────────────────────────
    before_json: Mapped[dict | None] = mapped_column(JSONType(), nullable=True)
    after_json: Mapped[dict | None] = mapped_column(JSONType(), nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONType(), nullable=True)

    # ── HMAC chain for tamper detection ──────────────────────
    hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    previous_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # ── Timestamp ────────────────────────────────────────────
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
