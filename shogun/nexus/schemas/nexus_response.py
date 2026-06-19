"""Pydantic schemas for NexusResponse."""

from __future__ import annotations

import uuid
from typing import Any
from pydantic import BaseModel, Field


class NexusResponse(BaseModel):
    """Normalized response envelope returned by the Nexus Gateway."""
    
    task_id: uuid.UUID
    status: str = Field(..., description="Task status (completed, failed, blocked, pending)")
    result: dict[str, Any] = Field(default_factory=dict, description="Successful output data or error detail")
    error: str | None = Field(None, description="Detailed error message if the task failed or was blocked")
    audit_event_id: str | None = Field(None, description="L1/L2 event trace ID for audit logging correlation")
    ts: float = Field(..., description="Epoch timestamp of response packaging")
