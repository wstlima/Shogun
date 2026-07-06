"""Bushido schemas — reflection, maintenance, and self-improvement."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import Field, field_validator, model_validator

from shogun.schemas.common import (
    BushidoFrequency,
    BushidoJobStatus,
    BushidoJobType,
    MemoryType,
    RiskLevel,
    ShogunBase,
    TriggerMode,
)

# ── Bushido Job ──────────────────────────────────────────────


class BushidoScope(ShogunBase):
    """Scope for a Bushido run."""

    agent_ids: list[uuid.UUID] = Field(default_factory=list)
    memory_types: list[MemoryType] = Field(default_factory=list)


class BushidoRunRequest(ShogunBase):
    """Request body for triggering a Bushido run."""

    job_type: BushidoJobType
    scope: BushidoScope = Field(default_factory=BushidoScope)
    trigger_mode: TriggerMode = TriggerMode.MANUAL
    priority: int = Field(default=50, ge=0, le=100)


class BushidoJobResponse(ShogunBase):
    """Response model for a Bushido job."""

    id: uuid.UUID
    job_type: BushidoJobType
    status: BushidoJobStatus
    scope: BushidoScope
    trigger_mode: TriggerMode
    started_at: datetime | None = None
    completed_at: datetime | None = None
    summary: dict[str, Any] = Field(default_factory=dict)
    output_ref: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


# ── Bushido Recommendation ───────────────────────────────────


class BushidoRecommendationResponse(ShogunBase):
    """Response model for a Bushido recommendation."""

    id: uuid.UUID
    job_id: uuid.UUID
    target_type: str
    target_id: uuid.UUID
    recommendation_type: str
    title: str
    description: str
    confidence: float
    risk_level: RiskLevel
    approval_required: bool
    status: str
    created_at: datetime
    updated_at: datetime


# ── Bushido Schedule ─────────────────────────────────────────


class BushidoScheduleCreate(ShogunBase):
    """Request body for creating a new Bushido schedule."""

    name: str
    job_type: BushidoJobType
    frequency: BushidoFrequency = BushidoFrequency.NIGHTLY
    schedule_time: str | None = "02:00"            # "HH:MM"
    schedule_days: list[str] | None = None          # ["mon", "wed"]
    schedule_day: int | None = None                 # day of month 1-28
    minute_offset: int = Field(default=0, ge=0, le=55)
    schedule_datetime: str | None = None            # ISO string for one-off
    scope: BushidoScope = Field(default_factory=BushidoScope)
    priority: int = Field(default=50, ge=0, le=100)
    all_agents: bool = True
    dry_run: bool = False
    auto_approve: bool = False
    task_instruction: str | None = None
    is_enabled: bool = True

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Job name is required")
        return value

    @field_validator("schedule_time")
    @classmethod
    def validate_schedule_time(cls, value: str | None) -> str | None:
        if value is None:
            return value
        try:
            hour_text, minute_text = value.split(":")
            hour, minute = int(hour_text), int(minute_text)
        except (ValueError, AttributeError):
            raise ValueError("Schedule time must use HH:MM format") from None
        if not 0 <= hour <= 23 or not 0 <= minute <= 59:
            raise ValueError("Schedule time must be a valid local time")
        return f"{hour:02d}:{minute:02d}"

    @model_validator(mode="after")
    def validate_frequency_details(self):
        if self.frequency == BushidoFrequency.WEEKLY and not self.schedule_days:
            raise ValueError("Weekly schedules require at least one active day")
        if self.frequency == BushidoFrequency.ONE_OFF:
            if not self.schedule_datetime:
                raise ValueError("One-off schedules require a future date and time")
            try:
                run_at = datetime.fromisoformat(self.schedule_datetime)
            except ValueError:
                raise ValueError("One-off schedule date is invalid") from None
            now = datetime.now(run_at.tzinfo) if run_at.tzinfo else datetime.now()
            if run_at <= now:
                raise ValueError("One-off schedule date must be in the future")
        if self.job_type == BushidoJobType.CUSTOM_TASK and not (self.task_instruction or "").strip():
            raise ValueError("Custom tasks require a task instruction")
        return self


class BushidoScheduleUpdate(ShogunBase):
    """Partial update for a Bushido schedule."""

    name: str | None = None
    frequency: BushidoFrequency | None = None
    schedule_time: str | None = None
    schedule_days: list[str] | None = None
    schedule_day: int | None = None
    minute_offset: int | None = None
    schedule_datetime: str | None = None
    scope: BushidoScope | None = None
    priority: int | None = None
    all_agents: bool | None = None
    dry_run: bool | None = None
    auto_approve: bool | None = None
    task_instruction: str | None = None
    is_enabled: bool | None = None

    # Legacy compat — keep the old flat-bool form for the PUT /schedule endpoint
    nightly_consolidation: bool | None = None
    weekly_performance_audit: bool | None = None
    skill_health_check: bool | None = None
    persona_drift_check: bool | None = None


class BushidoScheduleResponse(ShogunBase):
    """Response model for a Bushido schedule."""

    id: uuid.UUID
    name: str
    job_type: BushidoJobType
    frequency: BushidoFrequency
    schedule_time: str | None
    schedule_days: list[str] | None
    schedule_day: int | None
    minute_offset: int
    schedule_datetime: str | None
    scope: dict[str, Any]
    priority: int
    all_agents: bool
    dry_run: bool
    auto_approve: bool
    task_instruction: str | None
    is_enabled: bool
    is_preset: bool
    last_run_at: datetime | None
    next_run_at: datetime | None
    created_at: datetime
    updated_at: datetime
