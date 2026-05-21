"""Calendar routes."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, Query

from shogun.api.deps import get_calendar_service
from shogun.schemas.channels import CalendarEventCreate, CalendarEventResponse
from shogun.schemas.common import ApiResponse
from shogun.services.calendar_service import CalendarService

router = APIRouter(prefix="/channels/calendar", tags=["Calendar"])


@router.get("/events", response_model=ApiResponse[list[CalendarEventResponse]])
async def get_events(
    start: datetime = Query(...),
    end: datetime = Query(...),
    calendar_svc: CalendarService = Depends(get_calendar_service),
):
    events = await calendar_svc.get_events(start_date=start, end_date=end)
    return ApiResponse(data=events)


@router.post("/events", response_model=ApiResponse[CalendarEventResponse])
async def create_event(
    body: CalendarEventCreate,
    calendar_svc: CalendarService = Depends(get_calendar_service),
):
    event = await calendar_svc.create_event(body)
    return ApiResponse(data=event)


@router.patch("/events/{event_id}", response_model=ApiResponse[CalendarEventResponse])
async def update_event(
    event_id: str,
    body: CalendarEventCreate,
    calendar_svc: CalendarService = Depends(get_calendar_service),
):
    event = await calendar_svc.update_event(event_id, body)
    return ApiResponse(data=event)


@router.delete("/events/{event_id}", response_model=ApiResponse[dict[str, Any]])
async def delete_event(
    event_id: str,
    calendar_svc: CalendarService = Depends(get_calendar_service),
):
    res = await calendar_svc.delete_event(event_id)
    return ApiResponse(data=res)
