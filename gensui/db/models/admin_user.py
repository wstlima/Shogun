"""Admin user model — Gensui operators with role-based access."""

from __future__ import annotations

import uuid

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from gensui.db.base import Base, UUIDMixin, AuditMixin, GUID


class AdminUser(Base, UUIDMixin, AuditMixin):
    """A human operator who can access the Gensui Admin UI."""

    __tablename__ = "admin_users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False, default="Admin")
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Role: owner | admin | security_operator | observer | auditor
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="admin")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
