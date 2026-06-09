"""Group service — CRUD and membership management for Shogun groups."""

from __future__ import annotations

import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from gensui.db.models.member_group import MemberGroup
from gensui.db.models.group_membership import GroupMembership
from gensui.db.models.shogun_member import ShogunMember


class GroupService:
    """Manages groups and group memberships."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Group CRUD ───────────────────────────────────────────

    async def create(self, name: str, description: str | None = None) -> MemberGroup:
        """Create a new group."""
        group = MemberGroup(name=name, description=description)
        self.session.add(group)
        await self.session.flush()
        await self.session.refresh(group)
        return group

    async def get_by_id(self, group_id: uuid.UUID) -> MemberGroup | None:
        """Fetch a group by ID."""
        result = await self.session.execute(
            select(MemberGroup).where(MemberGroup.id == group_id)
        )
        return result.scalars().first()

    async def list_groups(self) -> list[MemberGroup]:
        """List all groups."""
        result = await self.session.execute(select(MemberGroup))
        return list(result.scalars().all())

    async def delete(self, group_id: uuid.UUID) -> bool:
        """Delete a group and its memberships."""
        group = await self.get_by_id(group_id)
        if group is None:
            return False
        # Remove all memberships
        memberships = await self.session.execute(
            select(GroupMembership).where(GroupMembership.group_id == group_id)
        )
        for m in memberships.scalars().all():
            await self.session.delete(m)
        await self.session.delete(group)
        await self.session.flush()
        return True

    # ── Group Membership ─────────────────────────────────────

    async def add_member(self, group_id: uuid.UUID, shogun_id: uuid.UUID) -> GroupMembership:
        """Add a Shogun to a group."""
        membership = GroupMembership(group_id=group_id, shogun_id=shogun_id)
        self.session.add(membership)
        # Update cached count
        group = await self.get_by_id(group_id)
        if group:
            count_result = await self.session.execute(
                select(func.count()).select_from(GroupMembership).where(
                    GroupMembership.group_id == group_id
                )
            )
            group.member_count = (count_result.scalar() or 0) + 1
        await self.session.flush()
        await self.session.refresh(membership)
        return membership

    async def remove_member(self, group_id: uuid.UUID, shogun_id: uuid.UUID) -> bool:
        """Remove a Shogun from a group."""
        result = await self.session.execute(
            select(GroupMembership).where(
                GroupMembership.group_id == group_id,
                GroupMembership.shogun_id == shogun_id,
            )
        )
        membership = result.scalars().first()
        if membership is None:
            return False
        await self.session.delete(membership)
        # Update cached count
        group = await self.get_by_id(group_id)
        if group and group.member_count > 0:
            group.member_count -= 1
        await self.session.flush()
        return True

    async def get_members(self, group_id: uuid.UUID) -> list[ShogunMember]:
        """Get all Shogun members of a group."""
        result = await self.session.execute(
            select(ShogunMember).join(
                GroupMembership,
                GroupMembership.shogun_id == ShogunMember.id,
            ).where(GroupMembership.group_id == group_id)
        )
        return list(result.scalars().all())

    async def get_groups_for_member(self, shogun_id: uuid.UUID) -> list[MemberGroup]:
        """Get all groups a Shogun belongs to."""
        result = await self.session.execute(
            select(MemberGroup).join(
                GroupMembership,
                GroupMembership.group_id == MemberGroup.id,
            ).where(GroupMembership.shogun_id == shogun_id)
        )
        return list(result.scalars().all())

    async def get_member_ids(self, group_id: uuid.UUID) -> list[uuid.UUID]:
        """Get all Shogun member IDs in a group."""
        result = await self.session.execute(
            select(GroupMembership.shogun_id).where(GroupMembership.group_id == group_id)
        )
        return [row[0] for row in result.all()]
