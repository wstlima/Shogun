"""Heartbeat API — receives heartbeats from member Shoguns."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from gensui.api.deps import get_db, get_shogun_identity
from gensui.services.member_service import MemberService
from gensui.services.posture_service import PostureService

router = APIRouter(prefix="/heartbeat", tags=["heartbeat"])


class HeartbeatRequest(BaseModel):
    shogun_id: str
    timestamp: str
    status: str = "online"
    version: str | None = None
    effective_posture: str | None = None
    harakiri_state: str = "none"
    active_samurai_count: int = 0
    active_workflow_count: int = 0
    active_mado_sessions: int = 0
    health: dict | None = None
    nexus_peers: list[str] | None = None  # List of peer Shogun IDs for topology
    external_agents: list[dict] | None = None  # External enterprise agents connected via Nexus Gateway


@router.post("")
async def heartbeat(
    req: HeartbeatRequest,
    db: AsyncSession = Depends(get_db),
    identity: dict = Depends(get_shogun_identity),
):
    """Receive a heartbeat from a member Shogun."""
    svc = MemberService(db)
    member = await svc.process_heartbeat(
        shogun_id=uuid.UUID(identity["shogun_id"]),
        version=req.version,
        effective_posture=req.effective_posture,
        harakiri_state=req.harakiri_state,
        samurai_count=req.active_samurai_count,
        active_workflow_count=req.active_workflow_count,
        active_mado_sessions=req.active_mado_sessions,
        health=req.health,
        nexus_peers=req.nexus_peers,
        external_agents=req.external_agents,
    )

    # Return current posture and pending commands info
    posture_svc = PostureService(db)
    posture_info = await posture_svc.get_effective_posture_with_explanation(
        uuid.UUID(identity["shogun_id"])
    )

    return {
        "status": "ok",
        "effective_posture": posture_info,
    }
