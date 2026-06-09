"""Alert service — creates and manages alerts for policy violations."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from gensui.db.models.alert import Alert


class AlertService:
    """Manages alerts triggered by policy violations or system events."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        severity: str,
        event_type: str,
        description: str,
        shogun_id: uuid.UUID | None = None,
        samurai_id: uuid.UUID | None = None,
        recommended_action: str | None = None,
        linked_policy_decision_id: uuid.UUID | None = None,
        linked_telemetry_event_id: uuid.UUID | None = None,
    ) -> Alert:
        """Create a new alert."""
        alert = Alert(
            severity=severity,
            event_type=event_type,
            description=description,
            shogun_id=shogun_id,
            samurai_id=samurai_id,
            recommended_action=recommended_action,
            linked_policy_decision_id=linked_policy_decision_id,
            linked_telemetry_event_id=linked_telemetry_event_id,
        )
        self.session.add(alert)
        await self.session.flush()
        await self.session.refresh(alert)
        return alert

    async def list_alerts(
        self,
        status_filter: str | None = None,
        severity_filter: str | None = None,
        shogun_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Alert], int]:
        """List alerts with filters."""
        query = select(Alert)
        count_query = select(func.count()).select_from(Alert)

        if status_filter:
            query = query.where(Alert.status == status_filter)
            count_query = count_query.where(Alert.status == status_filter)
        if severity_filter:
            query = query.where(Alert.severity == severity_filter)
            count_query = count_query.where(Alert.severity == severity_filter)
        if shogun_id:
            query = query.where(Alert.shogun_id == shogun_id)
            count_query = count_query.where(Alert.shogun_id == shogun_id)

        count_result = await self.session.execute(count_query)
        total = count_result.scalar() or 0

        query = query.order_by(Alert.timestamp.desc()).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all()), total

    async def resolve(
        self,
        alert_id: uuid.UUID,
        resolved_by: str,
    ) -> Alert | None:
        """Mark an alert as resolved."""
        result = await self.session.execute(
            select(Alert).where(Alert.id == alert_id)
        )
        alert = result.scalars().first()
        if alert is None:
            return None
        alert.status = "resolved"
        alert.resolved_by = resolved_by
        alert.resolved_at = datetime.now(timezone.utc)
        await self.session.flush()
        return alert

    async def get_active_count(self) -> dict:
        """Get counts of active alerts by severity."""
        result = await self.session.execute(
            select(Alert.severity, func.count())
            .where(Alert.status == "active")
            .group_by(Alert.severity)
        )
        counts = {row[0]: row[1] for row in result.all()}
        return {
            "total": sum(counts.values()),
            "critical": counts.get("CRITICAL", 0),
            "high": counts.get("HIGH", 0),
            "medium": counts.get("MEDIUM", 0),
            "low": counts.get("LOW", 0),
            "info": counts.get("INFO", 0),
        }
