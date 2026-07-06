"""Persistence helpers for the conversation shared by Comms and Telegram."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shogun.db.models.chat_message import ChatMessage


def serialize_chat_message(message: ChatMessage) -> dict:
    return {
        "id": str(message.id),
        "channel": message.channel,
        "role": message.role,
        "content": message.content,
        "external_chat_id": message.external_chat_id,
        "message_data": message.message_data or {},
        "created_at": message.created_at.isoformat(),
    }


async def append_chat_message(
    session: AsyncSession,
    *,
    channel: str,
    role: str,
    content: str,
    external_chat_id: str | None = None,
    client_message_id: str | None = None,
    message_data: dict | None = None,
) -> ChatMessage:
    if client_message_id:
        existing = await session.scalar(
            select(ChatMessage).where(ChatMessage.client_message_id == client_message_id)
        )
        if existing:
            return existing

    message = ChatMessage(
        channel=channel,
        role=role,
        content=content,
        external_chat_id=external_chat_id,
        client_message_id=client_message_id,
        message_data=message_data or {},
    )
    session.add(message)
    await session.flush()
    return message


async def list_chat_messages(session: AsyncSession, *, limit: int = 200) -> list[ChatMessage]:
    result = await session.execute(
        select(ChatMessage).order_by(ChatMessage.created_at.desc()).limit(limit)
    )
    return list(reversed(result.scalars().all()))


async def get_chat_context(session: AsyncSession, *, limit: int = 20) -> list[dict[str, str]]:
    messages = await list_chat_messages(session, limit=limit)
    return [
        {
            "role": "assistant" if message.role in {"assistant", "shogun"} else "user",
            "content": message.content,
        }
        for message in messages
        if message.role in {"user", "assistant", "shogun"} and message.content.strip()
    ]
