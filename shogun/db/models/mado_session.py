"""Mado Session ORM model — persistent browser session tracking.

Each MadoSession represents an isolated browser profile that can maintain
cookies, localStorage, and session state across multiple uses.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from shogun.db.base import AuditMixin, Base, GUID, JSONType, SoftDeleteMixin, UUIDMixin


class MadoSession(Base, UUIDMixin, AuditMixin, SoftDeleteMixin):
    """A persistent browser session/profile managed by Mado."""

    __tablename__ = "mado_sessions"

    # Display name ("Research Agent Browser", "Finance Scraper", etc.)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Filesystem profile directory name (sanitized, unique)
    profile_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    # Optional link to a Samurai agent
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(), ForeignKey("agents.id", ondelete="SET NULL"), nullable=True,
    )

    # Session status: idle | active | error | closed
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="idle")

    # Browser display mode: headless | visible
    browser_mode: Mapped[str] = mapped_column(String(50), nullable=False, default="headless")

    # Last visited URL
    last_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    # Per-session domain restrictions (list of allowed domains)
    domain_allowlist: Mapped[dict] = mapped_column(JSONType(), nullable=False, default=list)

    # Session metadata (cookies count, storage size, page title, etc.)
    session_data: Mapped[dict] = mapped_column(JSONType(), nullable=False, default=dict)

    # Per-session security policy (overrides are additive to Torii posture)
    security_policy: Mapped[dict] = mapped_column(JSONType(), nullable=False, default=lambda: {
        "https_only": False,
        "downloads": "allowed",
        "uploads": "allowed",
        "form_submit": "allowed",
        "external_navigation": "allowed",
        "js_execution": "allowed",
        "max_page_loads": 0,
    })

    # Last browser activity timestamp
    last_active_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None,
    )
