"""Member group model — logical grouping of Shogun instances for policy management."""

from __future__ import annotations

from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from gensui.db.base import Base, UUIDMixin, AuditMixin, GUID, JSONType


class MemberGroup(Base, UUIDMixin, AuditMixin):
    """A group of Shogun instances for collective policy management."""

    __tablename__ = "member_groups"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Assigned group posture
    posture_id: Mapped[str | None] = mapped_column(GUID(), nullable=True)

    # Cached member count
    member_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Metadata
    metadata_json: Mapped[dict | None] = mapped_column(JSONType(), nullable=True, default=dict)
