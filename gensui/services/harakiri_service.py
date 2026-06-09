"""Harakiri service — emergency shutdown and containment control."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from gensui.db.models.harakiri_event import HarakiriEvent
from gensui.db.models.shogun_member import ShogunMember
from gensui.db.models.command import Command
from gensui.db.models.group_membership import GroupMembership


class HarakiriService:
    """Manages Harakiri operations at individual, group, and global scope."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Individual Harakiri ──────────────────────────────────

    async def trigger_individual(
        self,
        shogun_id: uuid.UUID,
        mode: str = "soft_freeze",
        requested_by: str = "admin",
        reason: str | None = None,
        confirmation_text: str | None = None,
        incident_id: str | None = None,
    ) -> HarakiriEvent:
        """Trigger Harakiri on a single Shogun instance."""
        event = HarakiriEvent(
            scope="individual",
            target_id=str(shogun_id),
            target_type="shogun",
            mode=mode,
            requested_by=requested_by,
            requested_at=datetime.now(timezone.utc),
            reason=reason,
            confirmation_text=confirmation_text,
            incident_id=incident_id,
            affected_shogun_ids=[str(shogun_id)],
            status="pending",
        )
        self.session.add(event)

        # Update member state
        result = await self.session.execute(
            select(ShogunMember).where(ShogunMember.id == shogun_id)
        )
        member = result.scalars().first()
        if member:
            member.harakiri_state = mode

        # Queue command
        cmd = Command(
            shogun_id=shogun_id,
            command_type="harakiri",
            payload_json={"mode": mode, "harakiri_event_id": str(event.id)},
            status="pending",
        )
        self.session.add(cmd)

        await self.session.flush()
        await self.session.refresh(event)
        return event

    # ── Group Harakiri ───────────────────────────────────────

    async def trigger_group(
        self,
        group_id: uuid.UUID,
        mode: str = "soft_freeze",
        requested_by: str = "admin",
        reason: str | None = None,
        confirmation_text: str | None = None,
        incident_id: str | None = None,
    ) -> HarakiriEvent:
        """Trigger Harakiri on all Shoguns in a group."""
        # Get group members
        result = await self.session.execute(
            select(GroupMembership.shogun_id).where(GroupMembership.group_id == group_id)
        )
        member_ids = [row[0] for row in result.all()]
        member_id_strs = [str(mid) for mid in member_ids]

        event = HarakiriEvent(
            scope="group",
            target_id=str(group_id),
            target_type="group",
            mode=mode,
            requested_by=requested_by,
            requested_at=datetime.now(timezone.utc),
            reason=reason,
            confirmation_text=confirmation_text,
            incident_id=incident_id,
            affected_shogun_ids=member_id_strs,
            status="pending",
        )
        self.session.add(event)

        # Update members and queue commands
        for mid in member_ids:
            result = await self.session.execute(
                select(ShogunMember).where(ShogunMember.id == mid)
            )
            member = result.scalars().first()
            if member:
                member.harakiri_state = mode

            cmd = Command(
                shogun_id=mid,
                command_type="harakiri",
                payload_json={"mode": mode, "harakiri_event_id": str(event.id)},
                status="pending",
            )
            self.session.add(cmd)

        await self.session.flush()
        await self.session.refresh(event)
        return event

    # ── Global Harakiri ──────────────────────────────────────

    async def trigger_global(
        self,
        mode: str = "hard_stop",
        requested_by: str = "admin",
        reason: str | None = None,
        confirmation_text: str | None = None,
        incident_id: str | None = None,
    ) -> HarakiriEvent:
        """Trigger Harakiri on ALL member Shoguns."""
        # Get all active members
        result = await self.session.execute(
            select(ShogunMember).where(ShogunMember.enrollment_status == "active")
        )
        members = result.scalars().all()
        member_id_strs = [str(m.id) for m in members]

        event = HarakiriEvent(
            scope="global",
            target_id="global",
            target_type="global",
            mode=mode,
            requested_by=requested_by,
            requested_at=datetime.now(timezone.utc),
            reason=reason,
            confirmation_text=confirmation_text,
            incident_id=incident_id,
            affected_shogun_ids=member_id_strs,
            status="pending",
        )
        self.session.add(event)

        # Update all members and queue commands
        for member in members:
            member.harakiri_state = mode
            cmd = Command(
                shogun_id=member.id,
                command_type="harakiri",
                payload_json={"mode": mode, "harakiri_event_id": str(event.id)},
                status="pending",
            )
            self.session.add(cmd)

        await self.session.flush()
        await self.session.refresh(event)
        return event

    # ── Acknowledgement ──────────────────────────────────────

    async def acknowledge(
        self,
        harakiri_event_id: uuid.UUID,
        shogun_id: uuid.UUID,
    ) -> HarakiriEvent | None:
        """Record a Shogun's acknowledgement of a Harakiri command."""
        result = await self.session.execute(
            select(HarakiriEvent).where(HarakiriEvent.id == harakiri_event_id)
        )
        event = result.scalars().first()
        if event is None:
            return None

        # Add to acknowledged list
        acked = event.acknowledged_shogun_ids or []
        sid = str(shogun_id)
        if sid not in acked:
            acked.append(sid)
            event.acknowledged_shogun_ids = acked

        # Check if all affected have acknowledged
        affected = event.affected_shogun_ids or []
        if set(acked) >= set(affected):
            event.status = "completed"
            event.completed_at = datetime.now(timezone.utc)
        else:
            event.status = "executing"

        await self.session.flush()
        return event

    # ── Release ──────────────────────────────────────────────

    async def release(
        self,
        harakiri_event_id: uuid.UUID,
        release_to_posture: str = "LOCKDOWN",
        requested_by: str = "admin",
    ) -> HarakiriEvent | None:
        """Release Shoguns from Harakiri state."""
        result = await self.session.execute(
            select(HarakiriEvent).where(HarakiriEvent.id == harakiri_event_id)
        )
        event = result.scalars().first()
        if event is None:
            return None

        event.status = "released"
        event.completed_at = datetime.now(timezone.utc)

        # Reset harakiri state on all affected members
        affected = event.affected_shogun_ids or []
        for sid in affected:
            try:
                mid = uuid.UUID(sid)
                member_result = await self.session.execute(
                    select(ShogunMember).where(ShogunMember.id == mid)
                )
                member = member_result.scalars().first()
                if member:
                    member.harakiri_state = "none"
                    # Queue posture update command
                    cmd = Command(
                        shogun_id=mid,
                        command_type="posture_update",
                        payload_json={"posture_name": release_to_posture},
                        status="pending",
                    )
                    self.session.add(cmd)
            except ValueError:
                continue

        await self.session.flush()
        return event

    # ── Queries ──────────────────────────────────────────────

    async def list_events(
        self,
        scope: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[HarakiriEvent]:
        """List Harakiri events with optional filters."""
        query = select(HarakiriEvent).order_by(HarakiriEvent.requested_at.desc())
        if scope:
            query = query.where(HarakiriEvent.scope == scope)
        if status:
            query = query.where(HarakiriEvent.status == status)
        query = query.limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_active_events(self) -> list[HarakiriEvent]:
        """Get all active (non-released, non-completed) Harakiri events."""
        result = await self.session.execute(
            select(HarakiriEvent).where(
                HarakiriEvent.status.in_(["pending", "executing"])
            ).order_by(HarakiriEvent.requested_at.desc())
        )
        return list(result.scalars().all())
