"""Audit API — searchable audit log and chain verification."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from gensui.api.deps import get_db, require_role
from gensui.services.audit_service import AuditService

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("")
async def query_audit_log(
    action: str | None = None,
    actor_type: str | None = None,
    target_type: str | None = None,
    since: str | None = None,
    until: str | None = None,
    offset: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_role("owner", "admin", "auditor")),
):
    """Query the audit log."""
    svc = AuditService(db)
    since_dt = datetime.fromisoformat(since) if since else None
    until_dt = datetime.fromisoformat(until) if until else None

    entries, total = await svc.query(
        action=action, actor_type=actor_type, target_type=target_type,
        since=since_dt, until=until_dt, offset=offset, limit=limit,
    )
    return {
        "entries": [
            {
                "id": str(e.id),
                "actor_type": e.actor_type,
                "actor_id": e.actor_id,
                "action": e.action,
                "target_type": e.target_type,
                "target_id": e.target_id,
                "reason": e.reason,
                "timestamp": e.timestamp.isoformat() if e.timestamp else None,
                "ip_address": e.ip_address,
                "metadata": e.metadata_json,
            }
            for e in entries
        ],
        "total": total,
    }


@router.get("/verify")
async def verify_chain(
    limit: int = 1000,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_role("owner", "auditor")),
):
    """Verify the HMAC chain integrity of the audit log."""
    svc = AuditService(db)
    return await svc.verify_chain(limit=limit)
