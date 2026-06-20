"""Service account model — machine-to-machine identity for enterprise integrations.

Service accounts provide API key-based authentication for:
- CI/CD pipelines
- External monitoring systems
- SIEM integrations
- Custom automation scripts
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from gensui.db.base import Base, UUIDMixin, GUID, JSONType


class ServiceAccount(Base, UUIDMixin):
    """A service account for machine-to-machine API access."""

    __tablename__ = "service_accounts"

    # ── Identity ─────────────────────────────────────────────
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── API Key (hashed) ─────────────────────────────────────
    api_key_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    api_key_prefix: Mapped[str] = mapped_column(String(12), nullable=False)  # First 8 chars for display

    # ── Permissions ──────────────────────────────────────────
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="readonly")
    # Roles: readonly, auditor, operator, admin
    scopes_json: Mapped[dict | None] = mapped_column(JSONType(), nullable=True)
    # e.g. {"audit.read": true, "fleet.read": true, "telemetry.write": true}

    # ── Rate Limiting ────────────────────────────────────────
    rate_limit_rpm: Mapped[int] = mapped_column(Integer, nullable=False, default=60)

    # ── Lifecycle ────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_ip: Mapped[str | None] = mapped_column(String(50), nullable=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ── Metadata ─────────────────────────────────────────────
    created_by: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
