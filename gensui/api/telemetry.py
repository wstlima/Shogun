"""Telemetry API — receives telemetry events from member Shoguns."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from gensui.api.deps import get_db, get_shogun_identity
from gensui.services.telemetry_service import TelemetryService

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


class TelemetryBatchRequest(BaseModel):
    events: list[dict]


@router.post("")
async def submit_telemetry(
    req: TelemetryBatchRequest,
    db: AsyncSession = Depends(get_db),
    identity: dict = Depends(get_shogun_identity),
):
    """Submit telemetry events from a member Shogun."""
    # Tag each event with the shogun_id
    for evt in req.events:
        evt["shogun_id"] = identity["shogun_id"]

    svc = TelemetryService(db)
    count = await svc.ingest(req.events)
    return {"ingested": count}


@router.post("/batch")
async def submit_telemetry_batch(
    req: TelemetryBatchRequest,
    db: AsyncSession = Depends(get_db),
    identity: dict = Depends(get_shogun_identity),
):
    """Submit a batch of telemetry events (alias)."""
    for evt in req.events:
        evt["shogun_id"] = identity["shogun_id"]

    svc = TelemetryService(db)
    count = await svc.ingest(req.events)
    return {"ingested": count}
