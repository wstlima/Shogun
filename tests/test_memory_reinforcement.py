from __future__ import annotations

import uuid

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from shogun.db.models.memory_record import MemoryRecord
from shogun.services.memory_service import MemoryService


@pytest.mark.asyncio
async def test_memory_access_and_successful_use_are_persisted_separately():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    agent_id = uuid.uuid4()
    memory_id = uuid.uuid4()

    async with engine.begin() as connection:
        await connection.run_sync(
            lambda sync_connection: MemoryRecord.__table__.create(sync_connection)
        )

    async with sessions() as session:
        session.add(
            MemoryRecord(
                id=memory_id,
                agent_id=agent_id,
                memory_type="semantic",
                title="Persistent fact",
                content="A fact that should survive sessions.",
                relevance_score=0.5,
                importance_score=0.7,
                confidence_score=0.8,
                decay_class="slow",
            )
        )
        await session.commit()

        service = MemoryService(session)
        await service.record_access(memory_id)
        await session.commit()
        accessed = await service.get_by_id(memory_id)
        assert accessed.access_count == 1
        assert accessed.successful_use_count == 0

        await service.reinforce(memory_id, "retrieved_and_used")
        await session.commit()

    async with sessions() as fresh_session:
        persisted = await fresh_session.get(MemoryRecord, memory_id)
        assert persisted is not None
        assert persisted.access_count == 1
        assert persisted.successful_use_count == 1
        assert persisted.relevance_score > 0.5
        assert persisted.last_confirmed_at is not None

    await engine.dispose()
