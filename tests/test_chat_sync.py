from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from shogun.db.models.chat_message import ChatMessage
from shogun.services.chat_sync_service import (
    append_chat_message,
    get_chat_context,
    list_chat_messages,
)


async def _sessions():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(
            lambda sync_connection: ChatMessage.__table__.create(sync_connection)
        )
    return engine, async_sessionmaker(engine, expire_on_commit=False)


@pytest.mark.asyncio
async def test_comms_and_telegram_share_ordered_context():
    engine, sessions = await _sessions()
    async with sessions() as session:
        await append_chat_message(
            session,
            channel="comms",
            role="user",
            content="Plan the launch",
            client_message_id="web-1",
        )
        await append_chat_message(
            session,
            channel="telegram",
            role="assistant",
            content="I will draft it.",
            external_chat_id="123",
        )
        await session.commit()

        messages = await list_chat_messages(session)
        context = await get_chat_context(session)

    assert [message.channel for message in messages] == ["comms", "telegram"]
    assert context == [
        {"role": "user", "content": "Plan the launch"},
        {"role": "assistant", "content": "I will draft it."},
    ]
    await engine.dispose()


@pytest.mark.asyncio
async def test_client_message_id_makes_web_sync_idempotent():
    engine, sessions = await _sessions()
    async with sessions() as session:
        first = await append_chat_message(
            session,
            channel="comms",
            role="user",
            content="Hello",
            client_message_id="same-id",
        )
        second = await append_chat_message(
            session,
            channel="comms",
            role="user",
            content="Hello",
            client_message_id="same-id",
        )
        assert first.id == second.id
        assert len(await list_chat_messages(session)) == 1

    await engine.dispose()
