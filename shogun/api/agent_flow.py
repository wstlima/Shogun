"""Agent Flow API routes — CRUD, graph operations, and execution for visual workflows."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
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


# ── Document Upload for Input Nodes ──────────────────────────


@router.post("/{flow_id}/upload", response_model=ApiResponse)
async def upload_flow_document(
    flow_id: uuid.UUID,
    file: UploadFile = File(...),
    svc: AgentFlowService = Depends(get_agent_flow_service),
):
    """Upload a document file for a Document Upload input node.

    The file is stored under ``{shogun_data}/flows/{flow_id}/uploads/``
    and can be read by the flow engine at execution time.
    """
    from pathlib import Path
    from shogun.config import settings

    # Verify flow exists
    flow = await svc.get_by_id(flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail="Agent Flow not found")

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    allowed_extensions = {".pdf", ".txt", ".csv", ".json", ".md", ".docx", ".xlsx"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Accepted: {', '.join(sorted(allowed_extensions))}",
        )

    # Save file
    upload_dir = Path(settings.data_dir) / "flows" / str(flow_id) / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Use a safe filename
    safe_name = file.filename.replace("..", "_").replace("/", "_").replace("\\", "_")
    dest_path = upload_dir / safe_name

    content = await file.read()
    dest_path.write_bytes(content)

    return ApiResponse(data={
        "filename": safe_name,
        "size": len(content),
        "path": str(dest_path),
    })


# ═══════════════════════════════════════════════════════════════
# TEMPLATE GALLERY ENDPOINTS
# ═══════════════════════════════════════════════════════════════

import json
from pathlib import Path as _Path

_TEMPLATE_CACHE: dict | None = None


def _load_templates() -> dict:
    """Load and cache the template catalog from JSON."""
    global _TEMPLATE_CACHE
    if _TEMPLATE_CACHE is not None:
        return _TEMPLATE_CACHE
    tpl_path = _Path(__file__).resolve().parent.parent / "data" / "flow_templates.json"
    if not tpl_path.exists():
        _TEMPLATE_CACHE = {"version": "1.0", "total_templates": 0, "categories": [], "templates": []}
        return _TEMPLATE_CACHE
    _TEMPLATE_CACHE = json.loads(tpl_path.read_text(encoding="utf-8"))
    return _TEMPLATE_CACHE


@router.get("/templates", response_model=ApiResponse)
async def list_templates():
    """Return the full template catalog (categories + lightweight template list)."""
    catalog = _load_templates()
    # Return lightweight version (without full node/edge data)
    lightweight = []
    for t in catalog.get("templates", []):
        lightweight.append({
            "id": t["id"],
            "name": t["name"],
            "description": t["description"],
            "category": t["category"],
            "icon": t["icon"],
            "difficulty": t["difficulty"],
            "trigger_type": t["trigger_type"],
            "node_count": t.get("node_count", len(t.get("nodes", []))),
        })
    return ApiResponse(data={
        "total": catalog.get("total_templates", len(lightweight)),
        "categories": catalog.get("categories", []),
        "templates": lightweight,
    })


@router.post("/from-template", response_model=ApiResponse, status_code=201)
async def create_from_template(
    body: dict,
    svc: AgentFlowService = Depends(get_agent_flow_service),
):
    """Create a new Agent Flow from a template ID.

    Body: ``{ "template_id": "translate-en-da", "name": "Optional override" }``
    """
    template_id = body.get("template_id")
    if not template_id:
        raise HTTPException(400, "template_id is required")

    catalog = _load_templates()
    template = None
    for t in catalog.get("templates", []):
        if t["id"] == template_id:
            template = t
            break

    if not template:
        raise HTTPException(404, f"Template not found: {template_id}")

    # Create the flow
    flow_name = body.get("name") or template["name"]
    flow = await svc.create(
        name=flow_name,
        description=template.get("description", ""),
        trigger_type=template.get("trigger_type", "manual"),
        status="draft",
    )

    # Save the graph (nodes + edges) from the template
    nodes_data = template.get("nodes", [])
    edges_data = template.get("edges", [])
    if nodes_data:
        saved = await svc.save_flow_graph(
            flow_id=flow.id,
            nodes_data=nodes_data,
            edges_data=edges_data,
            viewport={"x": 50, "y": 100, "zoom": 0.85},
        )
        if saved:
            flow = saved

    return ApiResponse(data=AgentFlowResponse.model_validate(flow))


# ═══════════════════════════════════════════════════════════════
# EXAMPLE FLOW SEEDING
# ═══════════════════════════════════════════════════════════════


@router.post("/seed-examples", response_model=ApiResponse, status_code=201)
async def seed_example_flows(
    svc: AgentFlowService = Depends(get_agent_flow_service),
    db: AsyncSession = Depends(get_db),
):
    """Create pre-built example flows to showcase Shogun capabilities.

    Currently seeds:
      - **AI News Digest** — Mado browses AI news sites, Samurai compiles
        a newsletter, and the result is emailed to Michael@alphahorizon.io.
      - Also creates the "News Editor" Samurai agent used by the flow.
    """
    from shogun.services.agent_service import AgentService

    created = []

    # ── 1. Create or find the "News Editor" Samurai agent ───────
    from shogun.db.models.agent import Agent as AgentModel

    agent_svc = AgentService(db)

    # Check if agent already exists (including soft-deleted — slug has unique constraint)
    existing = await db.execute(
        select(AgentModel).where(AgentModel.slug == "news-editor").limit(1)
    )
    editor_agent = existing.scalar_one_or_none()

    if editor_agent:
        # Reactivate if soft-deleted
        if editor_agent.is_deleted:
            editor_agent.is_deleted = False
            editor_agent.deleted_at = None
            editor_agent.status = "draft"
            await db.flush()
    else:
        editor_agent = await agent_svc.create(
            agent_type="samurai",
            name="News Editor",
            slug="news-editor",
            description=(
                "A specialist Samurai agent that compiles raw news data into "
                "polished, well-structured newsletter digests. Expert at "
                "summarising articles, categorising by source, and writing "
                "professional yet approachable email copy."
            ),
            memory_scope={
                "episodic": True,
                "semantic": True,
                "procedural": True,
                "persona": True,
                "skills": True,
            },
            spawn_policy="manual",
            avatar_url="/shogun-avatar.png",
            tags=["news", "editor", "newsletter", "ai-digest"],
        )

    editor_agent_id = str(editor_agent.id)

    # ── 2. AI News Digest Flow ─────────────────────────────────
    flow = await svc.create(
        name="AI News Digest",
        description=(
            "Automated AI news pipeline: Mado scans TechCrunch and The Verge "
            "for the latest AI stories, a Samurai agent compiles the findings "
            "into a polished newsletter, and sends it to Michael@alphahorizon.io."
        ),
        trigger_type="scheduled",
        status="draft",
    )

    # Node IDs (client-side, will be remapped by save_flow_graph)
    n_trigger   = "node-trigger"
    n_nav_gn    = "node-nav-google-news"
    n_nav_ai    = "node-nav-ai-news"
    n_ext_gn    = "node-extract-google-news"
    n_ext_ai    = "node-extract-ai-news"
    n_compiler  = "node-compiler"
    n_email     = "node-email"
    n_output    = "node-output"

    nodes_data = [
        {
            "id": n_trigger,
            "node_type": "input",
            "label": "Daily Trigger",
            "position_x": 0,
            "position_y": 200,
            "config": {
                "input_type": "scheduled",
                "description": "Daily AI news scan — triggers the Mado browser agents to scrape the latest AI articles from top tech publications.",
            },
        },
        {
            "id": n_nav_gn,
            "node_type": "mado_browser",
            "label": "Browse Google News AI",
            "position_x": 320,
            "position_y": 80,
            "config": {
                "action": "navigate",
                "url": "https://news.google.com/search?q=artificial+intelligence&hl=en-US&gl=US&ceid=US:en",
                "session_name": "news_google",
                "browser_mode": "headless",
            },
        },
        {
            "id": n_nav_ai,
            "node_type": "mado_browser",
            "label": "Browse AI News",
            "position_x": 320,
            "position_y": 320,
            "config": {
                "action": "navigate",
                "url": "https://www.artificialintelligence-news.com/",
                "session_name": "news_ainews",
                "browser_mode": "headless",
            },
        },
        {
            "id": n_ext_gn,
            "node_type": "mado_browser",
            "label": "Extract Google News Headlines",
            "position_x": 620,
            "position_y": 80,
            "config": {
                "action": "extract_content",
                "selector": "article a, [data-n-tid] a, c-wiz article, [jslog] h3, [jslog] h4",
                "extract_type": "text",
                "session_name": "news_google",
            },
        },
        {
            "id": n_ext_ai,
            "node_type": "mado_browser",
            "label": "Extract AI News Articles",
            "position_x": 620,
            "position_y": 320,
            "config": {
                "action": "extract_content",
                "selector": "h2 a, h3 a, .post-title a, .entry-title a, article h2, article h3",
                "extract_type": "text",
                "session_name": "news_ainews",
            },
        },
        {
            "id": n_compiler,
            "node_type": "samurai",
            "label": "Compile Newsletter",
            "position_x": 940,
            "position_y": 200,
            "config": {
                "agent_id": editor_agent_id,
                "task_description": (
                    "You are an AI news editor. From the scraped article headlines and "
                    "summaries provided by the previous steps, compile a professional, "
                    "concise AI news digest email.\n\n"
                    "Format the email with:\n"
                    "- A friendly greeting to Michael\n"
                    "- Sections for each source (Google News, AI News)\n"
                    "- Bullet points with brief 1-2 sentence summaries per story\n"
                    "- A closing note from the Shogun AI team\n\n"
                    "Keep it scannable and informative. Use markdown formatting."
                ),
                "expected_output": "A formatted newsletter-style email body in markdown",
                "timeout": 120,
                "retry_count": 1,
                "failure_action": "retry",
            },
        },
        {
            "id": n_email,
            "node_type": "email_send",
            "label": "Send to Michael",
            "position_x": 1260,
            "position_y": 200,
            "config": {
                "to_address": "Michael@alphahorizon.io",
                "subject": "🤖 Your Daily AI News Digest — Shogun",
                "body_template": "",
            },
        },
        {
            "id": n_output,
            "node_type": "output",
            "label": "Delivery Log",
            "position_x": 1540,
            "position_y": 200,
            "config": {
                "output_type": "artifact",
                "format": "markdown",
            },
        },
    ]

    edges_data = [
        # Trigger → both navigation nodes (parallel)
        {
            "source_node_id": n_trigger,
            "target_node_id": n_nav_gn,
            "edge_type": "default",
            "label": None,
            "config": {},
        },
        {
            "source_node_id": n_trigger,
            "target_node_id": n_nav_ai,
            "edge_type": "default",
            "label": None,
            "config": {},
        },
        # Navigate → Extract (each branch)
        {
            "source_node_id": n_nav_gn,
            "target_node_id": n_ext_gn,
            "edge_type": "default",
            "label": None,
            "config": {},
        },
        {
            "source_node_id": n_nav_ai,
            "target_node_id": n_ext_ai,
            "edge_type": "default",
            "label": None,
            "config": {},
        },
        # Both extractions → Compiler (merge)
        {
            "source_node_id": n_ext_gn,
            "target_node_id": n_compiler,
            "edge_type": "default",
            "label": None,
            "config": {},
        },
        {
            "source_node_id": n_ext_ai,
            "target_node_id": n_compiler,
            "edge_type": "default",
            "label": None,
            "config": {},
        },
        # Compiler → Email
        {
            "source_node_id": n_compiler,
            "target_node_id": n_email,
            "edge_type": "default",
            "label": None,
            "config": {},
        },
        # Email → Output
        {
            "source_node_id": n_email,
            "target_node_id": n_output,
            "edge_type": "default",
            "label": None,
            "config": {},
        },
    ]

    saved = await svc.save_flow_graph(
        flow_id=flow.id,
        nodes_data=nodes_data,
        edges_data=edges_data,
        viewport={"x": 50, "y": 50, "zoom": 0.75},
    )
    created.append(AgentFlowListItem.model_validate(saved))

    return ApiResponse(
        data=created,
        meta={"message": f"Seeded {len(created)} example flow(s)"},
    )
