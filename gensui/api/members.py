"""Members API — fleet management for admin UI."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from gensui.api.deps import get_db, get_current_admin, require_role
from gensui.services.member_service import MemberService

router = APIRouter(prefix="/members", tags=["members"])


@router.get("")
async def list_members(
    status: str | None = None,
    enrollment: str | None = None,
    offset: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """List all registered Shogun members."""
    svc = MemberService(db)
    members, total = await svc.list_members(
        status_filter=status, enrollment_filter=enrollment,
        offset=offset, limit=limit,
    )
    return {
        "members": [
            {
                "id": str(m.id),
                "instance_name": m.instance_name,
                "hostname": m.hostname,
                "environment": m.environment,
                "organization": m.organization,
                "version": m.version,
                "status": m.status,
                "enrollment_status": m.enrollment_status,
                "harakiri_state": m.harakiri_state,
                "effective_posture_id": str(m.effective_posture_id) if m.effective_posture_id else None,
                "samurai_count": m.samurai_count,
                "active_workflow_count": m.active_workflow_count,
                "active_mado_sessions": m.active_mado_sessions,
                "last_seen_at": m.last_seen_at.isoformat() if m.last_seen_at else None,
                "created_at": m.created_at.isoformat() if m.created_at else None,
                "local_os": m.local_os,
                "deployment_type": m.deployment_type,
                "metadata": m.metadata_json,
            }
            for m in members
        ],
        "total": total,
    }


@router.get("/{member_id}")
async def get_member(
    member_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """Get detailed info about a Shogun member."""
    svc = MemberService(db)
    member = await svc.get_by_id(member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    from gensui.services.posture_service import PostureService
    from gensui.services.group_service import GroupService

    posture_svc = PostureService(db)
    posture_info = await posture_svc.get_effective_posture_with_explanation(member_id)

    group_svc = GroupService(db)
    groups = await group_svc.get_groups_for_member(member_id)

    return {
        "id": str(member.id),
        "instance_name": member.instance_name,
        "hostname": member.hostname,
        "environment": member.environment,
        "organization": member.organization,
        "owner": member.owner,
        "version": member.version,
        "build_hash": member.build_hash,
        "status": member.status,
        "enrollment_status": member.enrollment_status,
        "harakiri_state": member.harakiri_state,
        "local_os": member.local_os,
        "deployment_type": member.deployment_type,
        "samurai_count": member.samurai_count,
        "active_workflow_count": member.active_workflow_count,
        "active_mado_sessions": member.active_mado_sessions,
        "disconnect_behavior": member.disconnect_behavior,
        "last_seen_at": member.last_seen_at.isoformat() if member.last_seen_at else None,
        "created_at": member.created_at.isoformat() if member.created_at else None,
        "metadata": member.metadata_json,
        "effective_posture": posture_info,
        "groups": [{"id": str(g.id), "name": g.name} for g in groups],
    }


@router.post("/{member_id}/disable")
async def disable_member(
    member_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_role("owner", "admin")),
):
    """Disable a member Shogun."""
    svc = MemberService(db)
    member = await svc.disable(member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    return {"status": "disabled", "shogun_id": str(member.id)}


class AssignPostureRequest(BaseModel):
    posture_id: str | None = None  # None = unassign


@router.post("/{member_id}/posture")
async def assign_posture(
    member_id: uuid.UUID,
    req: AssignPostureRequest,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_role("owner", "admin")),
):
    """Assign a security posture to an individual Shogun member."""
    svc = MemberService(db)
    member = await svc.get_by_id(member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    posture_uuid = uuid.UUID(req.posture_id) if req.posture_id else None

    # Validate posture exists
    if posture_uuid:
        from gensui.services.posture_service import PostureService
        psvc = PostureService(db)
        posture = await psvc.get_by_id(posture_uuid)
        if posture is None:
            raise HTTPException(status_code=404, detail="Posture not found")

    member.individual_posture_id = posture_uuid
    member.effective_posture_id = posture_uuid
    await db.commit()
    return {
        "status": "ok",
        "member_id": str(member.id),
        "posture_id": str(posture_uuid) if posture_uuid else None,
    }
