"""Global posture state — singleton record for network-wide enforcement."""

from __future__ import annotations

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from gensui.db.base import Base, UUIDMixin, AuditMixin, GUID


class GlobalPostureState(Base, UUIDMixin, AuditMixin):
    """Singleton record representing the current global posture state.

    When active, this overrides ALL individual and group postures.
    """

    __tablename__ = "global_posture_state"

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    posture_id: Mapped[str | None] = mapped_column(GUID(), nullable=True)
    posture_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Who activated it
    activated_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(1000), nullable=True)
