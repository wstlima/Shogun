"""Telemetry service — intake and query of events from member Shoguns."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from gensui.db.models.telemetry_event import TelemetryEvent


class TelemetryService:
    """Manages telemetry event intake and querying."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def ingest(self, events: list[dict]) -> int:
        """Ingest a batch of telemetry events. Returns count of ingested events."""
        count = 0
        for evt in events:
            te = TelemetryEvent(
                shogun_id=evt.get("shogun_id"),
                samurai_id=evt.get("samurai_id"),
                workflow_id=evt.get("workflow_id"),
                nexus_message_id=evt.get("nexus_message_id"),
                event_type=evt.get("event_type", "unknown"),
                event_category=evt.get("event_category", "system"),
                severity=evt.get("severity", "info"),
                payload_json=evt.get("payload"),
                redacted_payload_json=evt.get("redacted_payload"),
                policy_decision_id=evt.get("policy_decision_id"),
                timestamp=datetime.fromisoformat(evt["timestamp"]) if evt.get("timestamp") else datetime.now(timezone.utc),
            )
            self.session.add(te)
            count += 1
        await self.session.flush()
        return count

    async def query(
        self,
        shogun_id: uuid.UUID | None = None,
        event_type: str | None = None,
        event_category: str | None = None,
        severity: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[TelemetryEvent], int]:
        """Query telemetry events with filters."""
        query = select(TelemetryEvent)
        count_query = select(func.count()).select_from(TelemetryEvent)

        if shogun_id:
            query = query.where(TelemetryEvent.shogun_id == shogun_id)
            count_query = count_query.where(TelemetryEvent.shogun_id == shogun_id)
        if event_type:
            query = query.where(TelemetryEvent.event_type == event_type)
            count_query = count_query.where(TelemetryEvent.event_type == event_type)
        if event_category:
            query = query.where(TelemetryEvent.event_category == event_category)
            count_query = count_query.where(TelemetryEvent.event_category == event_category)
        if severity:
            query = query.where(TelemetryEvent.severity == severity)
            count_query = count_query.where(TelemetryEvent.severity == severity)
        if since:
            query = query.where(TelemetryEvent.timestamp >= since)
            count_query = count_query.where(TelemetryEvent.timestamp >= since)
        if until:
            query = query.where(TelemetryEvent.timestamp <= until)
            count_query = count_query.where(TelemetryEvent.timestamp <= until)

        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        query = query.order_by(TelemetryEvent.timestamp.desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def get_volume_stats(self) -> dict:
        """Get telemetry volume statistics."""
        total_result = await self.session.execute(
            select(func.count()).select_from(TelemetryEvent)
        )
        total = total_result.scalar() or 0

        # Count by category
        cat_result = await self.session.execute(
            select(TelemetryEvent.event_category, func.count())
            .group_by(TelemetryEvent.event_category)
        )
        by_category = {row[0]: row[1] for row in cat_result.all()}

        return {
            "total_events": total,
            "by_category": by_category,
        }
