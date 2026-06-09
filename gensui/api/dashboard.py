"""Dashboard API — aggregated fleet statistics for the admin overview."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from gensui.api.deps import get_db, get_current_admin
from gensui.services.member_service import MemberService
from gensui.services.posture_service import PostureService
from gensui.services.alert_service import AlertService
from gensui.services.telemetry_service import TelemetryService
from gensui.services.harakiri_service import HarakiriService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """Get aggregated dashboard statistics."""
    member_svc = MemberService(db)
    posture_svc = PostureService(db)
    alert_svc = AlertService(db)
    telemetry_svc = TelemetryService(db)
    harakiri_svc = HarakiriService(db)

    fleet_stats = await member_svc.get_stats()
    global_posture = await posture_svc.get_global_state()
    alert_counts = await alert_svc.get_active_count()
    telemetry_volume = await telemetry_svc.get_volume_stats()
    active_harakiri = await harakiri_svc.get_active_events()

    return {
        "fleet": fleet_stats,
        "global_posture": {
            "is_active": global_posture.is_active if global_posture else False,
            "posture_name": global_posture.posture_name if global_posture else None,
            "activated_by": global_posture.activated_by if global_posture else None,
            "reason": global_posture.reason if global_posture else None,
        },
        "alerts": alert_counts,
        "telemetry": telemetry_volume,
        "active_harakiri_count": len(active_harakiri),
    }
