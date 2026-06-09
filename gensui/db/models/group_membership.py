"""Group membership — M2M relationship between ShogunMember and MemberGroup."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from gensui.db.base import Base, UUIDMixin, AuditMixin, GUID


class GroupMembership(Base, UUIDMixin, AuditMixin):
    """Many-to-many link between Shogun instances and groups."""

    __tablename__ = "group_memberships"

    shogun_id: Mapped[str] = mapped_column(GUID(), nullable=False, index=True)
    group_id: Mapped[str] = mapped_column(GUID(), nullable=False, index=True)
