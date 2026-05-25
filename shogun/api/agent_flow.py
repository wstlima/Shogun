"""Agent Flow API routes — CRUD, graph operations, and execution for visual workflows."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shogun.api.deps import get_agent_flow_service, get_db
from shogun.schemas.agent_flow import (
    AgentFlowCreate,
    AgentFlowGraphSave,
    AgentFlowListItem,
    AgentFlowResponse,
    AgentFlowRunCreate,
    AgentFlowRunListItem,
    AgentFlowRunResponse,
    AgentFlowUpdate,
)
from shogun.schemas.common import ApiResponse
from shogun.services.agent_flow_service import AgentFlowService

router = APIRouter(prefix="/agent-flows", tags=["Agent Flows"])


# ── List all flows ───────────────────────────────────────────


@router.get("", response_model=ApiResponse)
async def list_flows(
    status: str | None = None,
    svc: AgentFlowService = Depends(get_agent_flow_service),
):
    """List all Agent Flows (lightweight, without nodes/edges)."""
    records, total = await svc.list_flows(status=status)
    return ApiResponse(
        data=[AgentFlowListItem.model_validate(r) for r in records],
        meta={"total": total},
    )


# ── Create a new flow ───────────────────────────────────────


@router.post("", response_model=ApiResponse, status_code=201)
async def create_flow(
    body: AgentFlowCreate,
    svc: AgentFlowService = Depends(get_agent_flow_service),
):
    """Create a new Agent Flow."""
    record = await svc.create(**body.model_dump())
    return ApiResponse(data=AgentFlowResponse.model_validate(record))


# ── Get a single flow (with nodes and edges) ────────────────


@router.get("/{flow_id}", response_model=ApiResponse)
async def get_flow(
    flow_id: uuid.UUID,
    svc: AgentFlowService = Depends(get_agent_flow_service),
):
    """Get a single Agent Flow with all nodes and edges."""
    record = await svc.get_flow_full(flow_id)
    if not record:
        raise HTTPException(status_code=404, detail="Agent Flow not found")
    return ApiResponse(data=AgentFlowResponse.model_validate(record))


# ── Update flow metadata ────────────────────────────────────


@router.patch("/{flow_id}", response_model=ApiResponse)
async def update_flow(
    flow_id: uuid.UUID,
    body: AgentFlowUpdate,
    svc: AgentFlowService = Depends(get_agent_flow_service),
):
    """Update Agent Flow metadata (name, description, trigger, status)."""
    update_data = body.model_dump(exclude_unset=True)
    record = await svc.update(flow_id, **update_data)
    if not record:
        raise HTTPException(status_code=404, detail="Agent Flow not found")
    # Reload full flow with nodes/edges
    full = await svc.get_flow_full(flow_id)
    return ApiResponse(data=AgentFlowResponse.model_validate(full))


# ── Delete a flow ────────────────────────────────────────────


@router.delete("/{flow_id}", response_model=ApiResponse)
async def delete_flow(
    flow_id: uuid.UUID,
    svc: AgentFlowService = Depends(get_agent_flow_service),
):
    """Soft-delete an Agent Flow."""
    success = await svc.delete(flow_id)
    if not success:
        raise HTTPException(status_code=404, detail="Agent Flow not found")
    return ApiResponse(data={"deleted": True})


# ── Bulk save graph (nodes + edges) ──────────────────────────


@router.put("/{flow_id}/graph", response_model=ApiResponse)
async def save_graph(
    flow_id: uuid.UUID,
    body: AgentFlowGraphSave,
    svc: AgentFlowService = Depends(get_agent_flow_service),
):
    """Atomically save the full canvas graph (all nodes and edges)."""
    record = await svc.save_flow_graph(
        flow_id=flow_id,
        nodes_data=[n.model_dump() for n in body.nodes],
        edges_data=[e.model_dump() for e in body.edges],
        viewport=body.viewport,
    )
    if not record:
        raise HTTPException(status_code=404, detail="Agent Flow not found")
    return ApiResponse(data=AgentFlowResponse.model_validate(record))


# ── Duplicate a flow ─────────────────────────────────────────


@router.post("/{flow_id}/duplicate", response_model=ApiResponse, status_code=201)
async def duplicate_flow(
    flow_id: uuid.UUID,
    svc: AgentFlowService = Depends(get_agent_flow_service),
):
    """Deep-copy an Agent Flow including all nodes and edges."""
    record = await svc.duplicate_flow(flow_id)
    if not record:
        raise HTTPException(status_code=404, detail="Agent Flow not found")
    return ApiResponse(data=AgentFlowResponse.model_validate(record))


# ── Activate / Pause ─────────────────────────────────────────


@router.post("/{flow_id}/activate", response_model=ApiResponse)
async def activate_flow(
    flow_id: uuid.UUID,
    svc: AgentFlowService = Depends(get_agent_flow_service),
):
    """Set flow status to active."""
    record = await svc.update_status(flow_id, "active")
    if not record:
        raise HTTPException(status_code=404, detail="Agent Flow not found")
    return ApiResponse(data=AgentFlowListItem.model_validate(record))


@router.post("/{flow_id}/pause", response_model=ApiResponse)
async def pause_flow(
    flow_id: uuid.UUID,
    svc: AgentFlowService = Depends(get_agent_flow_service),
):
    """Set flow status to paused."""
    record = await svc.update_status(flow_id, "paused")
    if not record:
        raise HTTPException(status_code=404, detail="Agent Flow not found")
    return ApiResponse(data=AgentFlowListItem.model_validate(record))


# ═══════════════════════════════════════════════════════════════
# EXECUTION RUN ENDPOINTS
# ═══════════════════════════════════════════════════════════════


@router.post("/{flow_id}/run", response_model=ApiResponse, status_code=202)
async def run_flow(
    flow_id: uuid.UUID,
    body: AgentFlowRunCreate | None = None,
):
    """Trigger execution of an Agent Flow. Returns the run ID immediately.

    The flow executes asynchronously in the background.
    Poll GET /agent-flows/runs/{run_id} for status.
    """
    from shogun.engine.flow_engine import start_flow_run

    trigger = body.trigger_type if body else "manual"
    try:
        run_id = await start_flow_run(flow_id, trigger_type=trigger)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return ApiResponse(
        data={"run_id": str(run_id), "status": "pending"},
        meta={"message": "Flow execution started"},
    )


@router.get("/{flow_id}/runs", response_model=ApiResponse)
async def list_flow_runs(
    flow_id: uuid.UUID,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """List execution history for a specific flow."""
    from shogun.db.models.agent_flow_run import AgentFlowRun

    result = await db.execute(
        select(AgentFlowRun)
        .where(AgentFlowRun.flow_id == flow_id)
        .order_by(AgentFlowRun.created_at.desc())
        .limit(limit)
    )
    runs = result.scalars().all()
    return ApiResponse(
        data=[AgentFlowRunListItem.model_validate(r) for r in runs],
        meta={"total": len(runs)},
    )


@router.get("/runs/{run_id}", response_model=ApiResponse)
async def get_flow_run(
    run_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get full execution run details including per-node states."""
    from shogun.db.models.agent_flow_run import AgentFlowRun

    result = await db.execute(
        select(AgentFlowRun).where(AgentFlowRun.id == run_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Flow run not found")
    return ApiResponse(data=AgentFlowRunResponse.model_validate(run))


@router.post("/runs/{run_id}/cancel", response_model=ApiResponse)
async def cancel_run(
    run_id: uuid.UUID,
):
    """Cancel a running flow execution."""
    from shogun.engine.flow_engine import cancel_flow_run

    cancelled = await cancel_flow_run(run_id)
    if not cancelled:
        raise HTTPException(
            status_code=404,
            detail="Run not found or already completed",
        )
    return ApiResponse(data={"cancelled": True})
