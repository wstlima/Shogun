"""Postures API — security posture definition management."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from gensui.api.deps import get_db, get_current_admin, require_role
from gensui.services.posture_service import PostureService

router = APIRouter(prefix="/postures", tags=["postures"])


class CreatePostureRequest(BaseModel):
    name: str
    description: str | None = None
    level: int = 10
    allow_external_models: bool = True
    allow_local_models: bool = True
    allow_tool_execution: bool = True
    allow_mado: bool = True
    allow_memory_write: bool = True
    allow_memory_read: bool = True
    allow_agent_flow: bool = True
    allow_nexus: bool = True
    allow_samurai_delegation: bool = True
    allow_scheduled_triggers: bool = True
    allow_autonomous_loops: bool = True
    allow_external_web: bool = True
    allow_file_write: bool = True
    allow_external_api: bool = True
    rules_json: dict | None = None


@router.get("")
async def list_postures(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """List all security postures."""
    svc = PostureService(db)
    postures = await svc.list_postures()
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "description": p.description,
            "level": p.level,
            "is_builtin": p.is_builtin,
            "allow_external_models": p.allow_external_models,
            "allow_local_models": p.allow_local_models,
            "allow_tool_execution": p.allow_tool_execution,
            "allow_mado": p.allow_mado,
            "allow_memory_write": p.allow_memory_write,
            "allow_memory_read": p.allow_memory_read,
            "allow_agent_flow": p.allow_agent_flow,
            "allow_nexus": p.allow_nexus,
            "allow_samurai_delegation": p.allow_samurai_delegation,
            "allow_scheduled_triggers": p.allow_scheduled_triggers,
            "allow_autonomous_loops": p.allow_autonomous_loops,
            "allow_external_web": p.allow_external_web,
            "allow_file_write": p.allow_file_write,
            "allow_external_api": p.allow_external_api,
        }
        for p in postures
    ]


@router.post("")
async def create_posture(
    req: CreatePostureRequest,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_role("owner", "admin")),
):
    """Create a new custom security posture."""
    svc = PostureService(db)
    posture = await svc.create(
        name=req.name,
        description=req.description,
        level=req.level,
        is_builtin=False,
        created_by=admin["id"],
        allow_external_models=req.allow_external_models,
        allow_local_models=req.allow_local_models,
        allow_tool_execution=req.allow_tool_execution,
        allow_mado=req.allow_mado,
        allow_memory_write=req.allow_memory_write,
        allow_memory_read=req.allow_memory_read,
        allow_agent_flow=req.allow_agent_flow,
        allow_nexus=req.allow_nexus,
        allow_samurai_delegation=req.allow_samurai_delegation,
        allow_scheduled_triggers=req.allow_scheduled_triggers,
        allow_autonomous_loops=req.allow_autonomous_loops,
        allow_external_web=req.allow_external_web,
        allow_file_write=req.allow_file_write,
        allow_external_api=req.allow_external_api,
        rules_json=req.rules_json,
    )
    return {"id": str(posture.id), "name": posture.name}
