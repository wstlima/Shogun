"""Capability registry module."""

from __future__ import annotations

from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shogun.db.models.nexus import AgentCapabilityModel


DEFAULT_CAPABILITIES = [
    {"name": "browser.research", "category": "browser", "description": "Browse the web to gather research on a topic"},
    {"name": "desktop.execute", "category": "desktop", "description": "Execute local desktop commands and tasks (blocked by default)"},
    {"name": "file.analyze", "category": "file", "description": "Inspect and extract data from local files"},
    {"name": "crm.prepare_update", "category": "crm", "description": "Draft customer relationship update instructions"},
    {"name": "document.summarize", "category": "document", "description": "Summarize text or PDF files"},
    {"name": "email.draft", "category": "email", "description": "Draft client or internal emails"},
    {"name": "spreadsheet.analyze", "category": "spreadsheet", "description": "Analyze Excel or CSV spreadsheets locally"},
    {"name": "local_model.reasoning", "category": "local_model", "description": "Run reasoning tasks against local models"},
    {"name": "workflow.execute", "category": "workflow", "description": "Execute sequential workflows/agent flows"},
]


class CapabilityRegistry:
    """Manages Shogun capabilities exposed through the Nexus External Gateway."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def seed_capabilities(self) -> None:
        """Seed the default set of capabilities if they do not exist."""
        for cap in DEFAULT_CAPABILITIES:
            existing = await self.db.get(AgentCapabilityModel, cap["name"])
            if not existing:
                new_cap = AgentCapabilityModel(
                    name=cap["name"],
                    category=cap["category"],
                    description=cap["description"],
                    is_custom=False
                )
                self.db.add(new_cap)
        await self.db.commit()

    async def get_capability(self, name: str) -> AgentCapabilityModel | None:
        """Fetch a capability by its unique name identifier."""
        return await self.db.get(AgentCapabilityModel, name)

    async def list_capabilities(self) -> Sequence[AgentCapabilityModel]:
        """List all registered capabilities, seeding defaults first if database is empty."""
        result = await self.db.execute(select(AgentCapabilityModel))
        records = result.scalars().all()
        if not records:
            await self.seed_capabilities()
            result = await self.db.execute(select(AgentCapabilityModel))
            records = result.scalars().all()
        return records

    async def register_custom_capability(self, name: str, category: str, description: str | None = None) -> AgentCapabilityModel:
        """Allow custom skills/capabilities to register at runtime."""
        existing = await self.db.get(AgentCapabilityModel, name)
        if existing:
            existing.category = category
            existing.description = description
            existing.is_custom = True
        else:
            existing = AgentCapabilityModel(
                name=name,
                category=category,
                description=description,
                is_custom=True
            )
            self.db.add(existing)
        await self.db.commit()
        await self.db.refresh(existing)
        return existing
