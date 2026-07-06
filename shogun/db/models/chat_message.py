"""Shared Comms/Telegram conversation messages."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shogun.db.base import Base, JSONType, UUIDMixin


class ChatMessage(Base, UUIDMixin):
    __tablename__ = "chat_messages"

    channel: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    external_chat_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    client_message_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, unique=True, index=True
    )
    message_data: Mapped[dict] = mapped_column(JSONType(), nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )
