"""Harakiri API — emergency shutdown and containment controls."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from gensui.api.deps import get_db, require_role, get_shogun_identity
from gensui.services.harakiri_service import HarakiriService
from gensui.services.audit_service import AuditService

router = APIRouter(prefix="/harakiri", tags=["harakiri"])


class HarakiriRequest(BaseModel):
    target_id: str | None = None
    mode: str = "soft_freeze"
    reason: str | None = None
    confirmation_text: str | None = None
    incident_id: str | None = None


class ReleaseRequest(BaseModel):
    harakiri_event_id: str
    release_to_posture: str = "LOCKDOWN"


# ── Individual Harakiri ──────────────────────────────────────

@router.post("/individual")
async def trigger_individual(
    req: HarakiriRequest,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_role("owner", "admin", "security_operator")),
):
    """Trigger Harakiri on a single Shogun instance."""
    if req.confirmation_text != "CONFIRM HARAKIRI":
        raise HTTPException(status_code=400, detail="Invalid confirmation text. Must be: CONFIRM HARAKIRI")
    if not req.target_id:
        raise HTTPException(status_code=400, detail="target_id is required for individual Harakiri")

    svc = HarakiriService(db)
    event = await svc.trigger_individual(
        shogun_id=uuid.UUID(req.target_id),
        mode=req.mode,
        requested_by=admin["id"],
        reason=req.reason,
        confirmation_text=req.confirmation_text,
        incident_id=req.incident_id,
    )

    audit = AuditService(db)
    await audit.append(
        actor_type="admin", action="harakiri.individual",
        actor_id=admin["id"], target_type="shogun", target_id=req.target_id,
        metadata_json={"mode": req.mode, "reason": req.reason, "event_id": str(event.id)},
    )

    return {
        "event_id": str(event.id),
        "scope": event.scope,
        "mode": event.mode,
        "status": event.status,
        "affected_count": len(event.affected_shogun_ids or []),
    }


# ── Group Harakiri ───────────────────────────────────────────

@router.post("/group")
async def trigger_group(
    req: HarakiriRequest,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_role("owner", "admin")),
):
    """Trigger Harakiri on all Shoguns in a group."""
    if req.confirmation_text != "CONFIRM HARAKIRI":
        raise HTTPException(status_code=400, detail="Invalid confirmation text. Must be: CONFIRM HARAKIRI")
    if not req.target_id:
        raise HTTPException(status_code=400, detail="target_id (group_id) is required for group Harakiri")

    svc = HarakiriService(db)
    event = await svc.trigger_group(
        group_id=uuid.UUID(req.target_id),
        mode=req.mode,
        requested_by=admin["id"],
        reason=req.reason,
        confirmation_text=req.confirmation_text,
        incident_id=req.incident_id,
    )

    audit = AuditService(db)
    await audit.append(
        actor_type="admin", action="harakiri.group",
        actor_id=admin["id"], target_type="group", target_id=req.target_id,
        metadata_json={"mode": req.mode, "reason": req.reason, "affected": len(event.affected_shogun_ids or [])},
    )

    return {
        "event_id": str(event.id),
        "scope": event.scope,
        "mode": event.mode,
        "status": event.status,
        "affected_count": len(event.affected_shogun_ids or []),
    }


# ── Global Harakiri ──────────────────────────────────────────

@router.post("/global")
async def trigger_global(
    req: HarakiriRequest,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_role("owner")),
):
    """Trigger Harakiri on ALL member Shoguns. Requires Owner role."""
    if req.confirmation_text != "CONFIRM GLOBAL HARAKIRI":
        raise HTTPException(status_code=400, detail="Invalid confirmation text. Must be: CONFIRM GLOBAL HARAKIRI")

    svc = HarakiriService(db)
    event = await svc.trigger_global(
        mode=req.mode or "hard_stop",
        requested_by=admin["id"],
        reason=req.reason,
        confirmation_text=req.confirmation_text,
        incident_id=req.incident_id,
    )

    audit = AuditService(db)
    await audit.append(
        actor_type="admin", action="harakiri.global",
        actor_id=admin["id"], target_type="global",
        metadata_json={"mode": event.mode, "reason": req.reason, "affected": len(event.affected_shogun_ids or [])},
    )

    return {
        "event_id": str(event.id),
        "scope": event.scope,
        "mode": event.mode,
        "status": event.status,
        "affected_count": len(event.affected_shogun_ids or []),
    }


# ── Release ──────────────────────────────────────────────────

@router.post("/release")
async def release_harakiri(
    req: ReleaseRequest,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_role("owner", "admin")),
):
    """Release Shoguns from Harakiri state."""
    svc = HarakiriService(db)
    event = await svc.release(
        harakiri_event_id=uuid.UUID(req.harakiri_event_id),
        release_to_posture=req.release_to_posture,
        requested_by=admin["id"],
    )
    if event is None:
        raise HTTPException(status_code=404, detail="Harakiri event not found")

    audit = AuditService(db)
    await audit.append(
        actor_type="admin", action="harakiri.released",
        actor_id=admin["id"], target_type="harakiri_event", target_id=req.harakiri_event_id,
        metadata_json={"release_to": req.release_to_posture},
    )

    return {"status": "released", "release_to_posture": req.release_to_posture}


# ── Acknowledge (from Shogun client) ─────────────────────────

@router.post("/acknowledge/{event_id}")
async def acknowledge_harakiri(
    event_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    identity: dict = Depends(get_shogun_identity),
):
    """Acknowledge Harakiri execution from a Shogun instance."""
    svc = HarakiriService(db)
    event = await svc.acknowledge(event_id, uuid.UUID(identity["shogun_id"]))
    if event is None:
        return {"status": "not_found"}
    return {"status": event.status}


# ── List Events ──────────────────────────────────────────────

@router.get("/events")
async def list_harakiri_events(
    scope: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_role("owner", "admin", "security_operator", "auditor")),
):
    """List Harakiri events."""
    svc = HarakiriService(db)
    events = await svc.list_events(scope=scope, status=status)
    return [
        {
            "id": str(e.id),
            "scope": e.scope,
            "target_id": e.target_id,
            "target_type": e.target_type,
            "mode": e.mode,
            "requested_by": e.requested_by,
            "requested_at": e.requested_at.isoformat() if e.requested_at else None,
            "reason": e.reason,
            "status": e.status,
            "affected_count": len(e.affected_shogun_ids or []),
            "acknowledged_count": len(e.acknowledged_shogun_ids or []),
            "failed_count": len(e.failed_shogun_ids or []),
            "completed_at": e.completed_at.isoformat() if e.completed_at else None,
        }
        for e in events
    ]
