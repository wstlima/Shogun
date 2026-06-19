"""Pydantic schemas for NexusTask."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class NexusTaskBase(BaseModel):
    source_agent_id: str = Field(..., description="ID of the external agent requesting the task")
    source_platform: str = Field(..., description="External platform requesting the task (e.g. microsoft_365)")
    source_protocol: str = Field("a2a", description="Protocol used (a2a, webhook, mcp)")
    requested_action: str = Field(..., description="The action/capability requested (e.g. document.summarize)")
    task_description: str | None = Field(None, description="Human readable description of the task")
    
    required_capabilities: list[str] = Field(default_factory=list, description="List of capabilities required")
    input_context: dict[str, Any] = Field(default_factory=dict, description="Context parameters for the task")
    data_sensitivity: str = Field("internal", description="Sensitivity level (low, internal, restricted, sensitive)")
    allowed_tools: list[str] = Field(default_factory=list, description="Specific tools allowed to be executed")
    approval_required: bool = Field(False, description="Whether manual approval is required")
    callback_url: str | None = Field(None, description="Optional URL to post callback updates")
    audit_metadata: dict[str, Any] = Field(default_factory=dict, description="Any audit tags or telemetry metadata")


class NexusTaskCreate(NexusTaskBase):
    """Schema for creating a new Nexus Task."""
    pass


class NexusTaskResponse(NexusTaskBase):
    """Schema representing a task response detail."""
    id: uuid.UUID
    status: str = Field("pending", description="Current execution status (pending, executing, completed, failed, blocked)")
    result: dict[str, Any] = Field(default_factory=dict, description="Result payload if completed or error info if failed")
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
