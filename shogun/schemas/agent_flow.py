"""Pydantic schemas for Agent Flow — request/response models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from shogun.schemas.common import ShogunBase


# ── Node Schemas ─────────────────────────────────────────────


class AgentFlowNodeCreate(BaseModel):
    """Payload for creating a single node."""

    id: str | None = None  # Optional client-generated ID for React Flow
    node_type: str
    label: str = "Untitled"
    position_x: float = 0.0
    position_y: float = 0.0
    config: dict[str, Any] = Field(default_factory=dict)


class AgentFlowNodeUpdate(BaseModel):
    """Partial update for a single node."""

    label: str | None = None
    position_x: float | None = None
    position_y: float | None = None
    config: dict[str, Any] | None = None


class AgentFlowNodeResponse(ShogunBase):
    """Response model for a node."""

    id: uuid.UUID
    flow_id: uuid.UUID
    node_type: str
    label: str
    position_x: float
    position_y: float
    config: dict[str, Any]
    created_at: datetime
    updated_at: datetime


# ── Edge Schemas ─────────────────────────────────────────────


class AgentFlowEdgeCreate(BaseModel):
    """Payload for creating a single edge."""

    id: str | None = None  # Optional client-generated ID
    source_node_id: str
    target_node_id: str
    source_handle: str | None = None
    target_handle: str | None = None
    label: str | None = None
    edge_type: str = "default"
    config: dict[str, Any] = Field(default_factory=dict)


class AgentFlowEdgeResponse(ShogunBase):
    """Response model for an edge."""

    id: uuid.UUID
    flow_id: uuid.UUID
    source_node_id: uuid.UUID
    target_node_id: uuid.UUID
    source_handle: str | None
    target_handle: str | None
    label: str | None
    edge_type: str
    config: dict[str, Any]
    created_at: datetime
    updated_at: datetime


# ── Flow Schemas ─────────────────────────────────────────────


class AgentFlowCreate(BaseModel):
    """Payload for creating a new Agent Flow."""

    name: str
    description: str | None = None
    trigger_type: str = "manual"
    schedule_config: dict[str, Any] = Field(default_factory=dict)


class AgentFlowUpdate(BaseModel):
    """Partial update for a flow."""

    name: str | None = None
    description: str | None = None
    trigger_type: str | None = None
    schedule_config: dict[str, Any] | None = None
    status: str | None = None
    viewport: dict[str, Any] | None = None


class AgentFlowResponse(ShogunBase):
    """Response model for a flow (with nested nodes and edges)."""

    id: uuid.UUID
    name: str
    description: str | None
    status: str
    trigger_type: str
    schedule_config: dict[str, Any]
    viewport: dict[str, Any]
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    created_by: str | None
    nodes: list[AgentFlowNodeResponse] = []
    edges: list[AgentFlowEdgeResponse] = []


class AgentFlowListItem(ShogunBase):
    """Lightweight response for flow list (without nodes/edges)."""

    id: uuid.UUID
    name: str
    description: str | None
    status: str
    trigger_type: str
    created_at: datetime
    updated_at: datetime


# ── Bulk Graph Save ──────────────────────────────────────────


class AgentFlowGraphSave(BaseModel):
    """Bulk save payload — replaces all nodes and edges for a flow."""

    nodes: list[AgentFlowNodeCreate] = []
    edges: list[AgentFlowEdgeCreate] = []
    viewport: dict[str, Any] = Field(default_factory=lambda: {"x": 0, "y": 0, "zoom": 1})


# ── Execution Run Schemas ────────────────────────────────────


class AgentFlowRunCreate(BaseModel):
    """Trigger a flow execution."""

    trigger_type: str = "manual"


class AgentFlowRunResponse(ShogunBase):
    """Full execution run with per-node states."""

    id: uuid.UUID
    flow_id: uuid.UUID
    status: str
    trigger_type: str
    node_states: dict[str, Any]
    result_summary: dict[str, Any]
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class AgentFlowRunListItem(ShogunBase):
    """Lightweight run for list views."""

    id: uuid.UUID
    flow_id: uuid.UUID
    status: str
    trigger_type: str
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None
    created_at: datetime

