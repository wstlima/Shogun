"""Monitoring API — activity monitoring, telemetry queries, and groups management."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from gensui.api.deps import get_db, get_current_admin, require_role
from gensui.services.telemetry_service import TelemetryService
from gensui.services.group_service import GroupService

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


# ── Network Scan ─────────────────────────────────────────────

class NetworkScanRequest(BaseModel):
    subnets: list[str] | None = None
    port: int = 8000


@router.post("/network-scan")
async def network_scan(
    req: NetworkScanRequest | None = None,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_role("owner", "admin")),
):
    """Scan the local network for Shogun instances (enrolled and rogue)."""
    from gensui.services.network_scanner import scan_network

    body = req or NetworkScanRequest()
    result = await scan_network(
        session=db,
        subnets=body.subnets,
        port=body.port,
    )
    return result

# ── Activity Monitor ─────────────────────────────────────────

@router.get("/activity")
async def get_activity(
    shogun_id: str | None = None,
    event_type: str | None = None,
    event_category: str | None = None,
    severity: str | None = None,
    since: str | None = None,
    until: str | None = None,
    offset: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """Query telemetry events for the activity monitor."""
    svc = TelemetryService(db)
    sid = uuid.UUID(shogun_id) if shogun_id else None
    since_dt = datetime.fromisoformat(since) if since else None
    until_dt = datetime.fromisoformat(until) if until else None

    events, total = await svc.query(
        shogun_id=sid, event_type=event_type, event_category=event_category,
        severity=severity, since=since_dt, until=until_dt,
        offset=offset, limit=limit,
    )
    return {
        "events": [
            {
                "id": str(e.id),
                "shogun_id": str(e.shogun_id) if e.shogun_id else None,
                "event_type": e.event_type,
                "event_category": e.event_category,
                "severity": e.severity,
                "payload": e.payload_json,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
            }
            for e in events
        ],
        "total": total,
    }


# ── Groups Management ────────────────────────────────────────

class CreateGroupRequest(BaseModel):
    name: str
    description: str | None = None


class AddGroupMemberRequest(BaseModel):
    shogun_id: str


@router.get("/groups")
async def list_groups(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """List all groups."""
    svc = GroupService(db)
    groups = await svc.list_groups()
    return [
        {
            "id": str(g.id),
            "name": g.name,
            "description": g.description,
            "posture_id": str(g.posture_id) if g.posture_id else None,
            "member_count": g.member_count,
        }
        for g in groups
    ]


@router.post("/groups")
async def create_group(
    req: CreateGroupRequest,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_role("owner", "admin")),
):
    """Create a new group."""
    svc = GroupService(db)
    group = await svc.create(req.name, req.description)
    return {"id": str(group.id), "name": group.name}


@router.get("/groups/{group_id}/members")
async def get_group_members(
    group_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """Get all members of a group."""
    svc = GroupService(db)
    members = await svc.get_members(group_id)
    return [
        {
            "id": str(m.id),
            "instance_name": m.instance_name,
            "status": m.status,
            "harakiri_state": m.harakiri_state,
        }
        for m in members
    ]


@router.post("/groups/{group_id}/members")
async def add_group_member(
    group_id: uuid.UUID,
    req: AddGroupMemberRequest,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_role("owner", "admin")),
):
    """Add a Shogun to a group."""
    svc = GroupService(db)
    await svc.add_member(group_id, uuid.UUID(req.shogun_id))
    return {"status": "added"}


@router.delete("/groups/{group_id}/members/{shogun_id}")
async def remove_group_member(
    group_id: uuid.UUID,
    shogun_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_role("owner", "admin")),
):
    """Remove a Shogun from a group."""
    svc = GroupService(db)
    removed = await svc.remove_member(group_id, shogun_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Membership not found")
    return {"status": "removed"}


@router.delete("/groups/{group_id}")
async def delete_group(
    group_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_role("owner", "admin")),
):
    """Delete a group."""
    svc = GroupService(db)
    deleted = await svc.delete(group_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Group not found")
    return {"status": "deleted"}
