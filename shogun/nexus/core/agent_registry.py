"""External agent registry module."""

from __future__ import annotations

import secrets
import uuid
from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shogun.db.models.nexus import ExternalAgentModel
from shogun.nexus.schemas.external_agent import ExternalAgentRegister


class AgentRegistry:
    """Manages external enterprise agents registered with Shogun."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_agent(self, req: ExternalAgentRegister) -> ExternalAgentModel:
        """Register a new trusted external enterprise agent."""
        token = req.token or secrets.token_hex(32)
        
        # Verify token uniqueness
        existing = await self.get_agent_by_token(token)
        if existing:
            raise ValueError("An agent with this token is already registered.")

        agent = ExternalAgentModel(
            name=req.name,
            platform=req.platform,
            token=token,
            endpoint_url=req.endpoint_url,
            direction=req.direction,
            is_active=True
        )
        self.db.add(agent)
        await self.db.commit()
        await self.db.refresh(agent)
        return agent

    async def get_agent_by_id(self, agent_id: uuid.UUID) -> ExternalAgentModel | None:
        """Get an external agent by database UUID."""
        return await self.db.get(ExternalAgentModel, agent_id)

    async def get_agent_by_token(self, token: str) -> ExternalAgentModel | None:
        """Authenticate and retrieve an external agent by token."""
        result = await self.db.execute(
            select(ExternalAgentModel).where(
                ExternalAgentModel.token == token,
                ExternalAgentModel.is_deleted == False
            )
        )
        return result.scalars().first()

    async def list_agents(self) -> Sequence[ExternalAgentModel]:
        """List all active registered external agents."""
        result = await self.db.execute(
            select(ExternalAgentModel).where(
                ExternalAgentModel.is_deleted == False
            )
        )
        return result.scalars().all()
