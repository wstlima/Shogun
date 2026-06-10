"""RoninSession ORM model — persistent desktop session tracking.

Each RoninSession represents a governed desktop control session
with environment awareness, app trust tracking, and Gensui fleet fields.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from shogun.db.base import AuditMixin, Base, GUID, JSONType, SoftDeleteMixin, UUIDMixin


class RoninSession(Base, UUIDMixin, AuditMixin, SoftDeleteMixin):
    """A persistent Ronin desktop control session."""

    __tablename__ = "ronin_sessions"

    # Display name ("VS Code Automation", "SAP Data Entry", etc.)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Optional link to a Samurai agent
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True,
    )

    # Ronin posture level for this session
    posture: Mapped[str] = mapped_column(
        String(50), nullable=False, default="disabled",
    )

    # Session lifecycle status: idle | active | paused | error | closed
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="idle",
    )

    # ── Environment awareness ────────────────────────────────────
    # physical | vm | sandbox | remote_desktop | citrix | cloud_workspace
    environment_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="physical",
    )

    # windows | macos | linux
    os_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="unknown",
    )

    os_version: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
    )

    hostname: Mapped[str | None] = mapped_column(
        String(255), nullable=True,
    )

    machine_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True,
    )

    is_disposable: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False,
    )

    # ── Session state ────────────────────────────────────────────

    # Session metadata (capabilities used, config overrides, etc.)
    session_data: Mapped[dict] = mapped_column(
        JSONType(), nullable=False, default=dict,
    )

    # Last screenshot path
    last_screenshot_path: Mapped[str | None] = mapped_column(
        String(1000), nullable=True,
    )

    # Last action performed
    last_action: Mapped[str | None] = mapped_column(
        String(255), nullable=True,
    )

    # Last action timestamp
    last_action_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    # Current foreground application
    current_app: Mapped[str | None] = mapped_column(
        String(255), nullable=True,
    )

    # Current app trust level: trusted | restricted | sensitive | forbidden
    current_app_trust: Mapped[str | None] = mapped_column(
        String(50), nullable=True,
    )

    # Total actions executed in this session
    action_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
    )

    # Komainu (guardian) response level for this session
    komainu_level: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1,
    )
