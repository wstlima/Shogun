"""Enrollment token model — one-time tokens for Shogun registration."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, Boolean, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from gensui.db.base import Base, UUIDMixin, AuditMixin


class EnrollmentToken(Base, UUIDMixin, AuditMixin):
    """A one-time-use token for enrolling a Shogun instance."""

    __tablename__ = "enrollment_tokens"

    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Who created it
    created_by_admin_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Usage constraints
    max_uses: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    use_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # Expiry
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
