"""Email and Calendar account settings ORM model."""

from __future__ import annotations

from datetime import datetime
from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from shogun.db.base import AuditMixin, Base, JSONType, UUIDMixin


class EmailAccount(Base, UUIDMixin, AuditMixin):
    __tablename__ = "email_accounts"

    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # 'gmail', 'outlook', 'proton', 'other'
    display_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email_address: Mapped[str] = mapped_column(String(255), nullable=False)
    protocol: Mapped[str] = mapped_column(String(10), default="imap", nullable=False)  # 'imap' or 'pop3'

    imap_host: Mapped[str] = mapped_column(String(255), nullable=False)
    imap_port: Mapped[int] = mapped_column(Integer, nullable=False)
    imap_use_ssl: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    smtp_host: Mapped[str] = mapped_column(String(255), nullable=False)
    smtp_port: Mapped[int] = mapped_column(Integer, nullable=False)
    smtp_use_ssl: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    username: Mapped[str] = mapped_column(String(255), nullable=False)
    encrypted_password: Mapped[str] = mapped_column(String(500), nullable=False)

    caldav_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    calendar_provider: Mapped[str] = mapped_column(String(50), default="none", nullable=False)  # 'caldav', 'google_api', 'microsoft_graph', 'none'
    calendar_credentials: Mapped[dict | None] = mapped_column(JSONType(), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Permission toggles
    perm_read_mail: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    perm_send_mail: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    perm_delete_mail: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    perm_read_calendar: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    perm_create_events: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    perm_edit_events: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    perm_delete_events: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
