"""Alerts API — policy violations and system alerts."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from gensui.api.deps import get_db, get_current_admin
from gensui.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("")
async def list_alerts(
    status: str | None = None,
    severity: str | None = None,
    shogun_id: str | None = None,
    offset: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """List alerts with optional filters."""
    svc = AlertService(db)
    sid = uuid.UUID(shogun_id) if shogun_id else None
    alerts, total = await svc.list_alerts(
        status_filter=status, severity_filter=severity,
        shogun_id=sid, offset=offset, limit=limit,
    )
    return {
        "alerts": [
            {
                "id": str(a.id),
                "severity": a.severity,
                "event_type": a.event_type,
                "shogun_id": str(a.shogun_id) if a.shogun_id else None,
                "description": a.description,
                "recommended_action": a.recommended_action,
                "status": a.status,
                "timestamp": a.timestamp.isoformat() if a.timestamp else None,
            }
            for a in alerts
        ],
        "total": total,
    }


@router.post("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """Resolve an alert."""
    svc = AlertService(db)
    alert = await svc.resolve(alert_id, admin["id"])
    if alert is None:
        return {"status": "not_found"}
    return {"status": "resolved"}


@router.get("/summary")
async def alert_summary(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """Get alert count summary by severity."""
    svc = AlertService(db)
    return await svc.get_active_count()
