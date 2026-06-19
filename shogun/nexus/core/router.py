"""Nexus capability router module."""

from __future__ import annotations

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from shogun.db.models.agent import Agent
from shogun.db.models.nexus import NexusTaskModel
from shogun.services.agent_service import AgentService

logger = logging.getLogger(__name__)


class NexusRouter:
    """Decides which Shogun/Samurai agent performs a task based on capabilities."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.agent_svc = AgentService(db)

    async def route_task(self, task: NexusTaskModel) -> Agent:
        """Match the task's requested capability to the best suited internal agent.
        
        Routing heuristics:
        1. Find active Samurai agents.
        2. Inspect their profiles, roles, and tags to match the capability/category:
           - E.g. category 'browser' maps to a Samurai with 'research' role or tag.
           - E.g. category 'spreadsheet' maps to a Samurai with 'analysis' or 'data' role.
        3. If no specific Samurai agent matches, route to the primary Shogun agent.
        4. If no primary Shogun exists, raise ValueError.
        """
        requested = task.requested_action.lower()
        category = requested.split(".")[0] if "." in requested else requested
        
        active_samurai = await self.agent_svc.get_active_samurai()
        
        # Look for a specific Samurai match
        for samurai in active_samurai:
            # 1. Match by tags
            tags = [t.lower() for t in (samurai.tags or [])]
            if category in tags or requested in tags:
                logger.info("Routed task %s to Samurai agent '%s' by tag match", task.id, samurai.name)
                return samurai
            
            # 2. Match by samurai profile / role
            profile = samurai.samurai_profile
            if profile:
                role_name = (profile.role or "").lower()
                if category in role_name or (category == "browser" and "research" in role_name) or (category == "spreadsheet" and "analysis" in role_name):
                    logger.info("Routed task %s to Samurai agent '%s' by role/profile match (%s)", task.id, samurai.name, role_name)
                    return samurai
                    
            # 3. Match by name or description
            name = samurai.name.lower()
            desc = (samurai.description or "").lower()
            if category in name or category in desc:
                logger.info("Routed task %s to Samurai agent '%s' by name/description match", task.id, samurai.name)
                return samurai
                
        # Fall back to the primary Shogun
        primary_shogun = await self.agent_svc.get_primary_shogun()
        if primary_shogun:
            logger.info("Routed task %s to primary Shogun agent '%s' as fallback", task.id, primary_shogun.name)
            return primary_shogun

        # Fall back to first available agent if no primary is designated
        from sqlalchemy import select
        all_shoguns = await self.db.execute(
            select(Agent).where(Agent.agent_type == "shogun", Agent.is_deleted == False)
        )
        first_shogun = all_shoguns.scalars().first()
        if first_shogun:
            logger.info("Routed task %s to Shogun agent '%s' as absolute fallback", task.id, first_shogun.name)
            return first_shogun
            
        raise ValueError("No active Shogun or Samurai agents available to handle the task.")
