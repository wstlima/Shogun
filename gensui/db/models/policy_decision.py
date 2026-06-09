"""Policy decision model — every controlled action produces a policy decision."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column

from gensui.db.base import Base, UUIDMixin, GUID, JSONType


class PolicyDecision(Base, UUIDMixin):
    """A policy enforcement decision for an action at a member Shogun."""

    __tablename__ = "policy_decisions"

    # ── Source ───────────────────────────────────────────────
    shogun_id: Mapped[str] = mapped_column(GUID(), nullable=False, index=True)
    samurai_id: Mapped[str | None] = mapped_column(GUID(), nullable=True)

    # ── Action ───────────────────────────────────────────────
    action_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # ── Decision ─────────────────────────────────────────────
    posture_id: Mapped[str] = mapped_column(GUID(), nullable=False)
    # ALLOW | BLOCK | REQUIRE_APPROVAL | REDACT | ESCALATE
    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Matched rules from the posture's rules_json
    matched_rules: Mapped[dict | None] = mapped_column(JSONType(), nullable=True, default=list)

    # Risk assessment
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # ── Timestamp ────────────────────────────────────────────
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
