"""Mado Session CRUD Service — database operations for browser sessions."""

from __future__ import annotations

import logging
import uuid
from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shogun.db.models.mado_session import MadoSession
from shogun.services.base_service import BaseService

log = logging.getLogger(__name__)


class MadoSessionService(BaseService[MadoSession]):
    """CRUD service for MadoSession records."""

    def __init__(self, session: AsyncSession):
        super().__init__(MadoSession, session)

    async def list_sessions(
        self,
        *,
        status: str | None = None,
        agent_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[MadoSession], int]:
        """List sessions with optional filters, excluding soft-deleted."""
        filters = [MadoSession.is_deleted == False]
        if status:
            filters.append(MadoSession.status == status)
        if agent_id:
            filters.append(MadoSession.agent_id == agent_id)
        return await self.get_all(offset=offset, limit=limit, filters=filters)

    async def get_by_profile_name(self, profile_name: str) -> MadoSession | None:
        """Fetch a session by its filesystem profile name."""
        result = await self.session.execute(
            select(MadoSession).where(
                MadoSession.profile_name == profile_name,
                MadoSession.is_deleted == False,
            )
        )
        return result.scalars().first()

    async def update_status(
        self,
        session_id: uuid.UUID,
        status: str,
        **extra: Any,
    ) -> MadoSession | None:
        """Update session status and optional extra fields."""
        record = await self.get_by_id(session_id)
        if record is None or record.is_deleted:
            return None
        record.status = status
        for key, value in extra.items():
            if hasattr(record, key) and value is not None:
                setattr(record, key, value)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def count_active(self) -> int:
        """Count non-deleted sessions that are active or idle."""
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count()).select_from(MadoSession).where(
                MadoSession.is_deleted == False,
                MadoSession.status.in_(["idle", "active"]),
            )
        )
        return result.scalar() or 0
