"""Agent routes — CRUD for Shogun and Samurai agents."""

from __future__ import annotations

import json
import logging
import time
import uuid
import shutil
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Lazy import to avoid circular deps at module level
def _get_event_logger():
    from shogun.services.event_logger import EventLogger
    return EventLogger

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse

from shogun.api.deps import get_agent_service
from shogun.schemas.agents import (
    AgentCreate,
    AgentResponse,
    AgentUpdate,
    SamuraiProfileCreate,
    SamuraiProfileResponse,
)
from shogun.schemas.common import ApiResponse
from shogun.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["Agents"])

# ── System-context cache (90 s TTL) to avoid DB hits on every chat turn ──
_CTX_CACHE: dict = {"data": None, "ts": 0.0}
_CTX_TTL = 90  # seconds

async def _get_system_context() -> dict:
    """Return cached samurai/provider/tool counts, refreshed every 90 s."""
    if time.monotonic() - _CTX_CACHE["ts"] < _CTX_TTL and _CTX_CACHE["data"]:
        return _CTX_CACHE["data"]

    from shogun.db.engine import async_session_factory
    from shogun.db.models.model_provider import ModelProvider
    from shogun.db.models.agent import Agent as AgentModel
    from shogun.db.models.tool_connector import ToolConnector
    from sqlalchemy import select, func

    async with async_session_factory() as db:
        samurai_result = await db.execute(
            select(func.count()).select_from(AgentModel)
            .where(AgentModel.agent_type == "samurai", AgentModel.is_deleted == False)
        )
        samurai_count = samurai_result.scalar() or 0

        provider_result = await db.execute(
            select(ModelProvider).where(ModelProvider.status == "connected")
        )
        active_providers = provider_result.scalars().all()

        tool_result = await db.execute(
            select(func.count()).select_from(ToolConnector)
            .where(ToolConnector.is_deleted == False)
        )
        tool_count = tool_result.scalar() or 0

    ctx = {
        "samurai_count": samurai_count,
        "tool_count": tool_count,
        "provider_summary": ", ".join(
            f"{p.name} ({p.provider_type})" for p in active_providers
        ) or "none configured",
    }
    _CTX_CACHE["data"] = ctx
    _CTX_CACHE["ts"] = time.monotonic()
    return ctx


@router.get("/shogun", response_model=ApiResponse)
async def get_primary_shogun(svc: AgentService = Depends(get_agent_service)):
    from shogun.db.models.agent import Agent
    filters = [Agent.agent_type == "shogun", Agent.is_primary == True, Agent.is_deleted == False]
    records, _ = await svc.get_all(filters=filters)
    if not records:
        raise HTTPException(status_code=404, detail="Primary Shogun not found")
    return ApiResponse(data=AgentResponse.model_validate(records[0]))


@router.get("", response_model=ApiResponse)
async def list_agents(
    agent_type: str | None = None,
    status: str | None = None,
    svc: AgentService = Depends(get_agent_service),
):
    filters = []
    from shogun.db.models.agent import Agent

    filters.append(Agent.is_deleted == False)
    if agent_type:
        filters.append(Agent.agent_type == agent_type)
    if status:
        filters.append(Agent.status == status)

    records, total = await svc.get_all(filters=filters)
    return ApiResponse(
        data=[AgentResponse.model_validate(r) for r in records],
        meta={"total": total},
    )


@router.get("/{agent_id}", response_model=ApiResponse)
async def get_agent(
    agent_id: uuid.UUID,
    svc: AgentService = Depends(get_agent_service),
):
    record = await svc.get_by_id(agent_id)
    if not record or record.is_deleted:
        raise HTTPException(status_code=404, detail="Agent not found")
    return ApiResponse(data=AgentResponse.model_validate(record))


@router.post("", response_model=ApiResponse, status_code=201)
async def create_agent(
    body: AgentCreate,
    svc: AgentService = Depends(get_agent_service),
):
    data = body.model_dump()
    # ── Posture enforcement: subagent limit ──────────────────
    if data.get("agent_type") == "samurai":
        from shogun.services.posture_guard import check_kill_switch, check_subagent_limit
        await check_kill_switch()
        await check_subagent_limit()
    data["memory_scope"] = data["memory_scope"] if isinstance(data["memory_scope"], dict) else data["memory_scope"].model_dump()
    record = await svc.create(**data)

    # ── Inject Kaizen governance into Samurai agents ─────────
    if data.get("agent_type") == "samurai":
        try:
            from shogun.api.kaizen import build_governance_prompt_block
            governance_block = build_governance_prompt_block()
            bs = dict(record.bushido_settings) if record.bushido_settings else {}
            bs["governance_prompt"] = governance_block
            record.bushido_settings = bs
            await svc.session.flush()
        except Exception:
            pass  # Non-fatal — don't block agent creation

    return ApiResponse(data=AgentResponse.model_validate(record))


@router.patch("/{agent_id}", response_model=ApiResponse)
async def update_agent(
    agent_id: uuid.UUID,
    body: AgentUpdate,
    svc: AgentService = Depends(get_agent_service),
):
    update_data = body.model_dump(exclude_unset=True)
    if "memory_scope" in update_data and update_data["memory_scope"] is not None:
        update_data["memory_scope"] = update_data["memory_scope"].model_dump() if hasattr(update_data["memory_scope"], "model_dump") else update_data["memory_scope"]
    record = await svc.update(agent_id, **update_data)
    if not record:
        raise HTTPException(status_code=404, detail="Agent not found")
    return ApiResponse(data=AgentResponse.model_validate(record))


@router.post("/{agent_id}/suspend", response_model=ApiResponse)
async def suspend_agent(
    agent_id: uuid.UUID,
    svc: AgentService = Depends(get_agent_service),
):
    record = await svc.suspend(agent_id)
    if not record:
        raise HTTPException(status_code=404, detail="Agent not found")
    return ApiResponse(data=AgentResponse.model_validate(record))


@router.post("/{agent_id}/resume", response_model=ApiResponse)
async def resume_agent(
    agent_id: uuid.UUID,
    svc: AgentService = Depends(get_agent_service),
):
    record = await svc.resume(agent_id)
    if not record:
        raise HTTPException(status_code=404, detail="Agent not found")
    return ApiResponse(data=AgentResponse.model_validate(record))


@router.delete("/{agent_id}", response_model=ApiResponse)
async def delete_agent(
    agent_id: uuid.UUID,
    svc: AgentService = Depends(get_agent_service),
):
    deleted = await svc.delete(agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found")
    return ApiResponse(data={"deleted": True})


@router.post("/{agent_id}/avatar", response_model=ApiResponse)
async def upload_agent_avatar(
    agent_id: uuid.UUID,
    file: UploadFile = File(...),
    svc: AgentService = Depends(get_agent_service),
):
    """Upload a profile picture for an agent."""
    from shogun.config import settings
    
    # Verify agent exists
    agent = await svc.get_by_id(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Determine file extension and create unique filename
    ext = Path(file.filename).suffix or ".png"
    filename = f"avatar_{agent_id.hex}_{int(datetime.now().timestamp())}{ext}"
    
    # Ensure directory exists (redundant since settings.ensure_directories() is called on startup)
    upload_dir = Path(settings.uploads_path)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    dest_path = upload_dir / filename
    
    try:
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Update agent record with the new avatar URL
        avatar_url = f"/uploads/{filename}"
        await svc.update(agent_id, avatar_url=avatar_url)
        
        return ApiResponse(data={"avatar_url": avatar_url})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload avatar: {str(e)}")


@router.put("/{agent_id}/samurai-profile", response_model=ApiResponse)
async def update_samurai_profile(
    agent_id: uuid.UUID,
    body: SamuraiProfileCreate,
    svc: AgentService = Depends(get_agent_service),
):
    profile = await svc.update_samurai_profile(agent_id, **body.model_dump())
    return ApiResponse(data=SamuraiProfileResponse.model_validate(profile))


@router.post("/shogun/chat")
async def shogun_chat(
    body: dict,
    svc: AgentService = Depends(get_agent_service),
):
    """Stream chat tokens from the primary Shogun agent via SSE."""
    import httpx
    from shogun.db.models.agent import Agent
    user_msg: str = body.get("message", "").strip()
    history: list = body.get("history", [])

    if not user_msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    return await _shogun_chat_internal(user_msg, history, svc)


def _detect_task_type(message: str) -> str:
    """Simple heuristic to detect task intent. Future: use an LLM classifier."""
    triggers = (
        "search", "find", "look up", "lookup", "google",
        "latest", "current", "today", "right now", "news",
        "what happened", "who is", "what is", "where is",
        "when did", "when is", "how much", "price of",
        "weather", "score", "stock", "release", "announced",
        "recently", "2024", "2025", "live",
    )
    msg_lower = message.lower()
    if any(t in msg_lower for t in triggers):
        return "research"
    return "*"


async def _shogun_chat_internal(user_msg: str, history: list, svc: AgentService):
    import httpx
    from shogun.db.models.agent import Agent
    from shogun.db.models.model_provider import ModelProvider
    from shogun.db.models.model_definition import ModelDefinition
    from shogun.db.models.model_routing import ModelRoutingProfile
    from shogun.db.models.operator import Operator
    from shogun.api.deps import get_db
    from shogun.services.native_skills import NATIVE_TOOLS, execute_native_tool
    from shogun.services.posture_guard import check_kill_switch, get_posture_tool_filter, filter_tools_by_posture
    from sqlalchemy import select
    import uuid as _uuid

    # ── 0. Posture enforcement: kill switch gate ─────────────────
    try:
        await check_kill_switch()
    except HTTPException:
        async def _blocked():
            yield f"data: {json.dumps({'type': 'error', 'content': '⛩️ HARAKIRI is active — all AI operations are suspended. Deactivate the kill switch in the Torii to resume.'})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(_blocked(), media_type="text/event-stream")

    # ── 1. Load primary Shogun agent ──────────────────────────────
    filters = [Agent.agent_type == "shogun", Agent.is_primary == True, Agent.is_deleted == False]
    records, _ = await svc.get_all(filters=filters)
    if not records:
        raise HTTPException(status_code=404, detail="Primary Shogun agent not found")
    agent = records[0]

    # ── 2. Resolve primary model from settings ────────────────────
    bushido = agent.bushido_settings or {}

    # ── Bushido calibration parameters (from Bushido page sliders) ─
    _reflection_intensity = bushido.get("reflection_intensity", 70)
    _consolidation_rate = bushido.get("consolidation_rate", 45)
    _exploration_variance = bushido.get("exploration_variance", 24)
    # Map exploration_variance (0-100) to LLM temperature (0.3-1.2)
    _temperature = round(0.3 + (_exploration_variance / 100) * 0.9, 2)

    saved_primary: str = bushido.get("primary_model", "")
    saved_provider_id: str = saved_primary.split("::")[0] if "::" in saved_primary else ""
    saved_model_name: str = saved_primary.split("::")[1] if "::" in saved_primary else ""

    provider = None
    _model_supports_tools = None  # True/False/None — resolved below

    # ── 3. Resolve routing profiles and provider ──────────────────
    task_type = _detect_task_type(user_msg)
    _search_model: str | None = None
    provider_name: str | None = None
    res_reason = "primary_agent_model"

    async for db in get_db():
        # ── Step 0: Build Authorized Inventory ──
        authorized_keys = set()
        prov_res = await db.execute(select(ModelProvider).where(ModelProvider.status == "connected"))
        for p in prov_res.scalars().all():
            authorized_keys.add(p.name)
            m_id = p.config.get("model_id") or p.config.get("model")
            if m_id:
                authorized_keys.add(m_id)

        # Get active (default) routing profile
        res = await db.execute(
            select(ModelRoutingProfile).where(ModelRoutingProfile.is_default == True).limit(1)
        )
        profile = res.scalar_one_or_none()
        
        # If we have a special task (like research), check if there's a specific rule
        if profile and task_type != "*":
            rule = next((r for r in profile.rules if r.get("task_type") == task_type), None)
            if rule and rule.get("primary_model_id"):
                try:
                    # Look up the model definition
                    mid = _uuid.UUID(rule["primary_model_id"])
                    res = await db.execute(
                        select(ModelDefinition).where(ModelDefinition.id == mid)
                    )
                    mdef = res.scalar_one_or_none()
                    if mdef and mdef.provider and mdef.provider.status == "connected":
                        # Check if this specific model is authorized in Katana
                        if mdef.model_key in authorized_keys or mdef.display_name in authorized_keys:
                            # Success! Override provider and model
                            provider = mdef.provider
                            model_name = mdef.model_key
                            provider_name = mdef.display_name
                            _search_model = model_name
                            _model_supports_tools = mdef.supports_tools
                            res_reason = f"logic_routing_authorized ({task_type})"
                        else:
                            logger.warning(f"[Routing] Unauthorized model '{mdef.model_key}' blocked. Fallback to primary.")
                            res_reason = f"routing_blocked_unauthorized ({task_type})"
                    else:
                        logger.debug(f"Routing rule skipped: Provider {mdef.provider.name if mdef and mdef.provider else 'unknown'} is NOT connected.")
                except Exception:
                    pass # Fallback to default if anything goes wrong

        # If no routing override, use the saved primary or first connected
        if not provider:
            if saved_provider_id:
                try:
                    res = await db.execute(
                        select(ModelProvider).where(ModelProvider.id == _uuid.UUID(saved_provider_id))
                    )
                    provider = res.scalar_one_or_none()
                except Exception:
                    provider = None

            # If the saved UUID didn't match (e.g. stale frontend UUID from
            # setup wizard), try to find a provider whose models list
            # contains the saved model name.
            if not provider and saved_model_name:
                res = await db.execute(
                    select(ModelProvider).where(ModelProvider.status == "connected")
                )
                for p in res.scalars().all():
                    p_models = p.config.get("models") or []
                    if saved_model_name in p_models or saved_model_name == p.name:
                        provider = p
                        res_reason = "model_name_match_fallback"
                        break

            if not provider:
                res = await db.execute(
                    select(ModelProvider)
                    .where(ModelProvider.status == "connected")
                    .order_by(ModelProvider.created_at)
                    .limit(1)
                )
                provider = res.scalar_one_or_none()
                if provider:
                    res_reason = "auto_fallback_to_connected"
        break

    if not provider:
        async def _no_provider():
            yield f"data: {json.dumps({'type': 'error', 'content': '⚠️ No active model provider found. Go to The Katana → Model Providers and add one.'})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(_no_provider(), media_type="text/event-stream")

    # ── Generate trace_id for correlating all events in this chat turn ──
    _trace_id = f"trc_{uuid.uuid4().hex[:16]}"
    _agent_id_str = str(agent.id) if agent else None
    EL = _get_event_logger()

    # Endpoint resolve
    PROVIDER_URLS: dict[str, str] = {
        "ollama":     "http://localhost:11434",
        "lmstudio":   "http://localhost:1234/v1",
        "local":      "http://localhost:1234/v1",
        "openai":     "https://api.openai.com/v1",
        "openrouter": "https://openrouter.ai/api/v1",
        "anthropic":  "https://api.anthropic.com/v1",
        "google":     "https://generativelanguage.googleapis.com/v1beta/openai",
        "custom":     "https://api.openai.com/v1",
    }
    base_url: str = provider.base_url or PROVIDER_URLS.get(provider.provider_type, "https://api.openai.com/v1")
    if provider.provider_type == "ollama" and not base_url.rstrip("/").endswith("/v1"):
        base_url = base_url.rstrip("/") + "/v1"

    if not _search_model:
        model_name = (
            saved_model_name
            or provider.config.get("model_id")
            or (provider.config.get("models") or [None])[0]
            or provider.name
        )
        provider_name = provider.name
    else:
        model_name = model_name or saved_model_name or "unknown"

    # ── Provider-type heuristic for tool support ──────────────────
    # If not resolved from a ModelDefinition, infer from provider type.
    if _model_supports_tools is None and provider:
        _PROVIDER_TOOL_SUPPORT = {
            "openai": True, "openrouter": True, "anthropic": True,
            "google": True, "custom": True,
            "ollama": False, "lmstudio": False, "local": False,
        }
        _model_supports_tools = _PROVIDER_TOOL_SUPPORT.get(provider.provider_type, False)
    _model_supports_tools = _model_supports_tools or False
    logger.info(f"[Shogun] Model tool support: {_model_supports_tools} (provider: {provider.provider_type if provider else 'none'})")

    # ── EVENT: Model Selected ─────────────────────────────────
    try:
        import asyncio
        asyncio.ensure_future(EL.emit_model_event(
            "model.selected", f"Model resolved: {model_name} via {provider.provider_type}",
            model_used=model_name, provider_used=provider.provider_type,
            trace_id=_trace_id, agent_id=_agent_id_str, user_id=operator_name,
            detail={"reason": res_reason, "provider_id": str(provider.id), "base_url": base_url},
        ))
    except Exception:
        pass

    api_key = provider.config.get("api_key") or provider.config.get("api-key")
    req_headers: dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        req_headers["Authorization"] = f"Bearer {api_key}"
    if provider.provider_type == "openrouter":
        req_headers["HTTP-Referer"] = "https://shogun.ai"
        req_headers["X-Title"] = "Shogun"

    # ── 4. System context (90 s cache) ────────────────────────────
    ctx = await _get_system_context()

    # ── 4b. Governance context (constitution + mandate) ───────────
    try:
        from shogun.api.kaizen import get_governance_context
        gov = get_governance_context()
    except Exception:
        gov = {"rules_text": "  (not loaded)", "mandate_summary": ""}

    # ── 4c. Fetch Operator Identity ───────────────────────────────
    operator_name = "Daimyo"
    async for db in get_db():
        op_res = await db.execute(select(Operator).limit(1))
        op = op_res.scalar_one_or_none()
        if op and op.display_name:
            operator_name = op.display_name
        break

    # ── EVENT: Auth — Session Start ──────────────────────────
    try:
        import asyncio
        asyncio.ensure_future(EL.emit_auth_event(
            "auth.session", f"Chat session started by {operator_name}",
            user_id=operator_name, agent_id=_agent_id_str, trace_id=_trace_id,
            detail={"channel": "web", "operator": operator_name},
        ))
    except Exception:
        pass

    # ── 4d. Recall Relevant Memories from Archives ────────────────
    recalled_memories_text = ""
    try:
        from shogun.services.memory_service import MemoryService
        async for db in get_db():
            mem_svc = MemoryService(db)

            # 1. Semantic search for user-query-relevant memories
            relevant = await mem_svc.search(
                query=user_msg,
                agent_id=agent.id,
                limit=5,
            )

            # 2. Always include pinned memories (identity, preferences, etc.)
            pinned = await mem_svc.get_pinned(agent_id=agent.id)

            # Merge: pinned first, then relevant (deduplicated)
            seen: set[str] = set()
            memory_entries: list[str] = []

            for p in pinned:
                mid = str(p.id)
                if mid not in seen:
                    seen.add(mid)
                    memory_entries.append(f"[PINNED | {p.memory_type}] {p.title}\n{p.content}")

            for r in relevant:
                mid = r["memory_id"]
                if mid not in seen:
                    seen.add(mid)
                    score = r["scores"]["final"]
                    memory_entries.append(f"[{r['memory_type']} | salience:{score:.2f}] {r['title']}\n{r['content']}")

            if memory_entries:
                recalled_memories_text = "\n\n".join(memory_entries)

            # 3. Batch-update access tracking (single SQL UPDATE instead of N round-trips)
            recalled_ids = []
            if relevant:
                from shogun.db.models.memory_record import MemoryRecord
                from sqlalchemy import update
                recall_ids = [uuid.UUID(r["memory_id"]) for r in relevant]
                recalled_ids = [str(rid) for rid in recall_ids]
                await db.execute(
                    update(MemoryRecord)
                    .where(MemoryRecord.id.in_(recall_ids))
                    .values(
                        access_count=MemoryRecord.access_count + 1,
                        recall_count=MemoryRecord.recall_count + 1,
                        last_accessed_at=datetime.now(),
                        last_recalled_at=datetime.now(),
                    )
                )
                await db.commit()

            # ── EVENT: Memory Recalled (enhanced retrieval provenance) ──
            _retrieval_context = []
            if relevant:
                for r in relevant:
                    _retrieval_context.append({
                        "memory_id": r["memory_id"],
                        "title": r.get("title", "")[:100],
                        "memory_type": r.get("memory_type", "unknown"),
                        "relevance_score": round(r.get("scores", {}).get("final", 0), 3),
                    })
            if memory_entries:
                try:
                    import asyncio
                    asyncio.ensure_future(EL.emit_memory_event(
                        "memory.search", f"Recalled {len(memory_entries)} memories ({len(pinned)} pinned, {len(relevant)} semantic)",
                        trace_id=_trace_id, agent_id=_agent_id_str, user_id=operator_name,
                        memory_ids=recalled_ids,
                        detail={
                            "query": user_msg[:200],
                            "pinned_count": len(pinned),
                            "relevant_count": len(relevant),
                            "retrieval_context": _retrieval_context,
                        },
                    ))
                except Exception:
                    pass
            break
    except Exception as e:
        logger.debug("Memory recall skipped: %s", e)

    # ── 5. Build system prompt ────────────────────────────────────
    # Fetch posture for context injection and tool filtering
    _posture_filter = await get_posture_tool_filter()
    _active_tier = _posture_filter.get("active_tier", "tactical").upper()
    _max_subagents = _posture_filter.get("max_active_subagents", 5)

    persona_name = agent.name or "Shogun"
    system_prompt = f"""You are {persona_name}, the primary AI orchestrator of the Shogun platform.

YOUR OPERATOR:
You report exclusively to your Operator, whose preferred name is '{operator_name}'.
Address them respectfully by this name in your responses.

ABOUT THE SHOGUN PLATFORM:
Shogun is an AI agent orchestration framework. You are the master agent that coordinates everything.
The platform uses Japanese-themed naming:
- **Shogun** (you): The primary orchestrating AI. You reason, plan, and delegate.
- **Samurai**: Sub-agents you can spawn to handle specific tasks (research, coding, analysis, etc.).
- **Dojo**: The UI section where Samurai agents are created, configured, and managed.
- **Katana**: The configuration hub for model providers (Ollama, OpenAI, etc.) and API tools.
- **Comms**: The communications hub with three tabs:
  - **Chat**: The chat interface where the user talks directly to you.
  - **Mail**: A fully integrated email client. You can read, reply to, and compose emails.
  - **Calendar**: An integrated calendar. You can view events and create new ones.
- **Bushido**: The behavioral rules/directives that govern agent decisions.
- **Kaizen**: The continuous improvement and optimization system.
- **Torii**: The security and governance portal.

Note: You now have Native Skills (Tools) injected into your capabilities. If the user asks you to spawn a samurai, update models, read emails, send emails, check the calendar, etc. use the provided tools directly instead of redirecting them, IF the tools are available to you.

CONSTITUTIONAL DIRECTIVES (from Kaizen — you must follow these):
{gov['rules_text']}

YOUR MANDATE:
{gov['mandate_summary']}

ACTIVE SECURITY POSTURE (from the Torii — you MUST operate within these guardrails):
- Security Tier: {_active_tier}
- Filesystem Mode: {_posture_filter.get('filesystem_mode', 'scoped')}
- Network Mode: {_posture_filter.get('network_mode', 'allowlist')}
- Shell Execution: {'ALLOWED' if _posture_filter.get('shell_enabled') else 'DENIED'}
- Auto-Install Skills: {'ALLOWED' if _posture_filter.get('skill_auto_install') else 'DENIED'}
- Max Active Samurai: {_max_subagents} (currently {ctx['samurai_count']} deployed)
You must respect these constraints. If the user asks you to do something outside your current
security posture, inform them of the restriction and suggest changing the tier in the Torii.

BEHAVIORAL CALIBRATION (from Bushido — these shape how you think):
- Reflection Intensity: {_reflection_intensity}% (how deeply you self-evaluate before responding)
- Memory Consolidation Rate: {_consolidation_rate}/1000 per epoch (how aggressively you integrate new patterns)
- Exploration Variance: {_exploration_variance}% → temperature {_temperature} (creative deviation vs. proven patterns)
Apply these calibration settings to your reasoning: higher reflection = more thorough analysis before answering;
higher consolidation = weight recent interactions more heavily; higher exploration = more creative/novel responses.

CURRENT SYSTEM STATE:
- Active model providers: {ctx['provider_summary']}
- Your current model: {model_name} (Selection logic: {res_reason})
- Samurai agents deployed: {ctx['samurai_count']}
- Registered tools/API connectors: {ctx['tool_count']}

RECALLED MEMORIES (from your persistent Archives):
{recalled_memories_text or '(No relevant memories found for this query.)'}

YOUR CAPABILITIES:
- Answer questions and have natural conversations on any topic
- Help the user understand and configure their Shogun system
- Reason about tasks, suggest which Samurai agents would be best for a given workflow
- Help with code, analysis, writing, and general knowledge
- **Email**: Fetch inbox messages, read full email contents, compose and send emails, and reply to messages using the mail tools (fetch_inbox, read_email, send_email)
- **Calendar**: View upcoming events and create new calendar events using the calendar tools (list_calendar_events, create_calendar_event)
- **Cron Jobs**: List, create, and delete Bushido schedules (cron jobs) using the schedule tools (list_cron_jobs, create_cron_job, delete_cron_job)

IMPORTANT — EMAIL, CALENDAR & CRON JOB TOOLS:
You have DIRECT access to the operator's email inbox, calendar, and cron job schedules through your native tools.
When the user asks you to check their mail, read an email, reply to a message, send an email,
check the calendar, create an event, list schedules, or create/delete a cron job — USE YOUR TOOLS.
Do NOT say you cannot access email, calendar, or schedules. You DO have these tools. Use them.
- To reply to an email: first use read_email to get the full message, then use send_email with the sender's address and an appropriate subject (e.g. "Re: <original subject>").
- Always confirm with the user before sending an email on their behalf, unless they explicitly told you to send it.
- For cron jobs: use list_cron_jobs to show existing schedules, create_cron_job to add new ones, and delete_cron_job to remove custom ones.

BEHAVIOUR:
- Be conversational, warm, and genuinely helpful
- Use platform terminology naturally since the user knows the system
- When you don't know something about live system state, say so honestly
- Do NOT pretend you can directly execute actions
- Format responses with markdown when it improves readability
- You HAVE persistent memory via the Archives system (Qdrant vector store + SQLite).
  Information from recalled memories is injected above. Use it naturally — refer to
  stored knowledge, operator preferences, and past events when relevant.
  If asked where you store information, explain that you use the Archives for long-term
  memory which persists across sessions.
- When the user shares important personal details, preferences, or facts worth
  remembering, use the store_memory tool to save them to the Archives.
"""

    # ── 6. Build messages ─────────────────────────────────────────
    messages = [{"role": "system", "content": system_prompt}]
    for h in history[-10:]:
        if h.get("role") in ("user", "assistant") and h.get("content"):
            messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": user_msg})

    provider_name = provider_name or provider.name

    # ── 7. Native Skills Setup ────────────────────────────────────
    active_tools = []
    _policy_name = None
    async for db in get_db():
        if agent.security_policy_id:
            from shogun.db.models.security_policy import SecurityPolicy
            pol = await db.execute(select(SecurityPolicy).where(SecurityPolicy.id == agent.security_policy_id))
            policy = pol.scalar_one_or_none()
            if policy:
                _policy_name = policy.name if hasattr(policy, 'name') else str(agent.security_policy_id)
                perms = policy.permissions
                # Shogun can override the base Torii policy with custom permissions
                if agent.bushido_settings and agent.bushido_settings.get("custom_permissions"):
                    perms = agent.bushido_settings["custom_permissions"]
                
                # Determine which native skills are allowed based on policy limits
                allow_skills = not perms.get("skills", {}).get("require_approval", True)
                allow_auto_spawn = perms.get("subagents", {}).get("allow_auto_spawn", False)
                _denied_tools = []
                for tool in NATIVE_TOOLS:
                    if tool["function"]["name"] == "spawn_samurai" and not allow_auto_spawn:
                        _denied_tools.append(tool["function"]["name"])
                        continue
                    if tool["function"]["name"] in ["list_available_models", "update_model_settings"] and not allow_skills:
                        _denied_tools.append(tool["function"]["name"])
                        continue
                    active_tools.append(tool)

                try:
                    import asyncio
                    asyncio.ensure_future(EL.emit_policy_event(
                        "policy.evaluated",
                        f"Torii policy evaluated: {len(active_tools)} tools granted, {len(_denied_tools)} denied",
                        trace_id=_trace_id, agent_id=_agent_id_str, user_id=operator_name,
                        policy_ref=_policy_name,
                        policy_decision="allowed" if active_tools else "restricted",
                        policy_reason=f"Granted: {[t['function']['name'] for t in active_tools]}. Denied: {_denied_tools}",
                        detail={"allow_skills": allow_skills, "allow_auto_spawn": allow_auto_spawn},
                    ))
                    # ── EVENT: Risk — Tool Denied ──────────────────
                    if _denied_tools:
                        asyncio.ensure_future(EL.emit_risk_event(
                            "risk.tools_denied",
                            f"Policy denied {len(_denied_tools)} tools: {_denied_tools}",
                            severity="warn", risk_score="medium",
                            trace_id=_trace_id, agent_id=_agent_id_str, user_id=operator_name,
                            detail={"denied_tools": _denied_tools, "policy": _policy_name},
                        ))
                except Exception:
                    pass
        else:
            # No security policy — still grant core memory tool
            for tool in NATIVE_TOOLS:
                if tool["function"]["name"] == "store_memory":
                    active_tools.append(tool)
        break

    # ── 7b. Global posture enforcement layer ──────────────────────
    # The per-agent policy gating above checks the agent's assigned policy.
    # This additional layer enforces the GLOBAL posture tier constraints,
    # stripping tools that the current tier does not permit.
    active_tools, _posture_denied = filter_tools_by_posture(active_tools, _posture_filter)
    if _posture_denied:
        try:
            import asyncio
            asyncio.ensure_future(EL.emit_policy_event(
                "policy.posture_filtered",
                f"Posture [{_active_tier}] stripped {len(_posture_denied)} tools: {_posture_denied}",
                trace_id=_trace_id, agent_id=_agent_id_str, user_id=operator_name,
                policy_ref=f"posture:{_active_tier}",
                policy_decision="denied",
                policy_reason=f"Global posture filter denied: {_posture_denied}",
                detail={"posture_tier": _active_tier, "denied_tools": _posture_denied},
            ))
        except Exception:
            pass

    # ── 7c. Prompt injection for non-tool-calling models ──────────
    # When the model doesn't support the structured tools API, we inject
    # tool descriptions into the system prompt and rely on text-based parsing.
    _prompt_injected_tools = False
    if active_tools and not _model_supports_tools:
        from shogun.services.native_skills import generate_tool_prompt
        _tool_prompt = generate_tool_prompt(active_tools)
        # Inject into the system prompt (first message)
        messages[0]["content"] += "\n\n" + _tool_prompt
        _prompt_injected_tools = True
        logger.info(f"[Shogun] Prompt-injected {len(active_tools)} tools (model does not support structured tools)")
        # Clear active_tools so they're not sent via API — text parser will handle calls
        active_tools = []

    # ── EU AI Act: Derive use-case context ─────────────────
    _security_tier = "guarded"
    if _policy_name:
        _tier_map = {"shrine": "minimal", "guarded": "limited", "tactical": "limited", "campaign": "high", "ronin": "high"}
        for tier_key, risk_lvl in _tier_map.items():
            if tier_key in (_policy_name or "").lower():
                _security_tier = risk_lvl
                break

    _use_case_context = {
        "domain": "assistant",
        "purpose": task_type if task_type != "*" else "general_conversation",
        "risk_level": _security_tier,
        "human_oversight_required": False,
        "frameworks": ["SOC2", "NIS2", "EU_AI_ACT"],
    }

    # ── EVENT: Decision Context (EU AI Act) ───────────────
    try:
        import asyncio
        _safeguards = []
        if _policy_name:
            _safeguards.append(f"torii_policy:{_policy_name}")
        if recalled_memories_text:
            _safeguards.append("memory_grounding")

        asyncio.ensure_future(EL.emit_decision_event(
            "decision.context",
            f"Decision context assembled for chat turn",
            trace_id=_trace_id, agent_id=_agent_id_str, user_id=operator_name,
            model_used=model_name, provider_used=provider_name,
            use_case_context=_use_case_context,
            governance_flags={
                "human_oversight_required": False,
                "evidence_completeness": "full" if recalled_memories_text else "none",
            },
            detail={
                "inputs": {
                    "user_message_length": len(user_msg),
                    "history_messages": len(history),
                    "memories_recalled": len(memory_entries) if 'memory_entries' in dir() else 0,
                    "tools_available": [t["function"]["name"] for t in active_tools],
                },
                "safeguards_applied": _safeguards,
                "security_tier": _security_tier,
            },
        ))
        # ── EVENT: Risk — High Autonomy Mode ──────────────
        if _security_tier in ("high",):
            asyncio.ensure_future(EL.emit_risk_event(
                "risk.high_autonomy_mode",
                f"Operating in high-autonomy tier ({_policy_name or 'campaign/ronin'})",
                severity="warn", risk_score="high",
                trace_id=_trace_id, agent_id=_agent_id_str, user_id=operator_name,
                detail={"security_tier": _security_tier, "policy": _policy_name},
            ))
    except Exception:
        pass

    # Log user message for drift monitor
    _append_chat_log("user", user_msg)
    timestamp = datetime.now().isoformat()

    async def generate():
        nonlocal messages, active_tools
        # Metadata event: lets frontend show model badge immediately
        yield f"data: {json.dumps({'type': 'meta', 'model': model_name, 'provider': provider_name, 'timestamp': timestamp, 'reason': res_reason, 'search': bool(_search_model)})}\n\n"

        _tool_retry_used = False  # only retry once

        while True:
            assistant_tokens: list[str] = []
            tool_calls_buffer: dict = {}
            _retry_without_tools = False

            req_json = {
                "model": model_name,
                "messages": messages,
                "stream": True,
                "temperature": _temperature,
            }
            if active_tools:
                req_json["tools"] = active_tools

            try:
                async with httpx.AsyncClient(timeout=120.0) as client:
                    async with client.stream(
                        "POST",
                        f"{base_url.rstrip('/')}/chat/completions",
                        headers=req_headers,
                        json=req_json,
                    ) as resp:
                        if resp.status_code >= 400:
                            body_bytes = await resp.aread()
                            err = body_bytes.decode(errors="replace")[:300]

                            # ── Retry without tools on invalid tool call arguments ──
                            if resp.status_code == 400 and "invalid tool call" in err.lower() and not _tool_retry_used:
                                import logging as _logging
                                _logging.getLogger("shogun.agents").warning("[Shogun] 400 invalid tool call — retrying without tools")
                                active_tools = []
                                _tool_retry_used = True
                                _retry_without_tools = True
                                # Strip any tool-related messages so the model gets a clean conversation
                                messages = [m for m in messages if m.get("role") not in ("tool",) and "tool_calls" not in m]

                            if not _retry_without_tools:
                                # ── EVENT: Model Error ────────────────
                                try:
                                    await EL.emit_model_event(
                                        "model.error", f"LLM API error {resp.status_code}: {err[:100]}",
                                        result="error", severity="error",
                                        model_used=model_name, provider_used=provider_name,
                                        trace_id=_trace_id, agent_id=_agent_id_str,
                                        detail={"status_code": resp.status_code, "error": err},
                                    )
                                    # ── EVENT: Incident — Model API Error ───
                                    await EL.emit_incident_event(
                                        "incident.model_api_error",
                                        f"Model API returned HTTP {resp.status_code}",
                                        severity="error", risk_score="high",
                                        trace_id=_trace_id, agent_id=_agent_id_str,
                                        detail={"model": model_name, "provider": provider_name, "status_code": resp.status_code, "error": err[:200]},
                                    )
                                except Exception:
                                    pass
                                yield f"data: {json.dumps({'type': 'error', 'content': f'⚠️ LLM error ({resp.status_code}): {err}'})}\n\n"
                                yield "data: [DONE]\n\n"
                                return

                        if not _retry_without_tools:
                            _inside_think = False  # Track <think>...</think> blocks
                            async for line in resp.aiter_lines():
                                if not line.startswith("data: "):
                                    continue
                                data_str = line[6:].strip()
                                if data_str == "[DONE]":
                                    break
                                    
                                try:
                                    chunk = json.loads(data_str)
                                    delta = chunk["choices"][0]["delta"]
                                    
                                    # Process tool calls from streaming
                                    if "tool_calls" in delta:
                                        for tcall in delta["tool_calls"]:
                                            idx = tcall["index"]
                                            if idx not in tool_calls_buffer:
                                                tool_calls_buffer[idx] = {"id": tcall.get("id"), "type": "function", "function": {"name": tcall["function"].get("name", ""), "arguments": ""}}
                                            else:
                                                tool_calls_buffer[idx]["function"]["arguments"] += tcall["function"].get("arguments", "")
                                            
                                            # Yield action notice initially
                                            if tcall.get("id"):
                                                func_name = tool_calls_buffer[idx]["function"]["name"]
                                                yield f"data: {json.dumps({'type': 'action', 'content': f'Executing {func_name}...'})}\n\n"
                                    
                                    content = delta.get("content") or ""
                                    if content:
                                        # ── Handle <think> blocks ──
                                        # Some reasoning models output <think>...</think> blocks.
                                        # Track them in assistant_tokens but don't yield to frontend.
                                        if "<think>" in content:
                                            _inside_think = True
                                        if _inside_think:
                                            assistant_tokens.append(content)
                                            if "</think>" in content:
                                                _inside_think = False
                                            continue  # don't yield thinking tokens
                                        
                                        assistant_tokens.append(content)
                                        yield f"data: {json.dumps({'type': 'token', 'content': content})}\n\n"
                                except Exception:
                                    pass  # skip malformed chunks

            except httpx.ConnectError:
                yield f"data: {json.dumps({'type': 'error', 'content': f'⚠️ Cannot connect to {base_url}. Is {provider.provider_type} running?'})}\n\n"
                yield "data: [DONE]\n\n"
                return
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'content': f'⚠️ Unexpected error: {str(e)[:200]}'})}\n\n"
                yield "data: [DONE]\n\n"
                return

            # If we're retrying without tools, restart the loop immediately
            if _retry_without_tools:
                continue

            if assistant_tokens:
                full_text = "".join(assistant_tokens)
                _append_chat_log("assistant", full_text)
                messages.append({"role": "assistant", "content": full_text})

            # ── Structured tool calls (OpenAI format) ──
            if tool_calls_buffer:
                tool_calls_array = list(tool_calls_buffer.values())
                
                # We must append the assistant's tool_call intention
                if "content" not in messages[-1]:
                    messages.append({"role": "assistant", "content": None, "tool_calls": tool_calls_array})
                else: 
                     messages[-1]["tool_calls"] = tool_calls_array

                # Execute all tools
                async for db in get_db():
                    for tcall in tool_calls_array:
                        func_name = tcall["function"]["name"]
                        try:
                            args = json.loads(tcall["function"]["arguments"])
                        except json.JSONDecodeError:
                            args = {}
                            
                        # Execute
                        res_str = await execute_native_tool(func_name, args, db)
                        messages.append({"role": "tool", "tool_call_id": tcall["id"], "name": func_name, "content": res_str})

                        # ── EVENT: Tool Executed ──────────────
                        try:
                            _tool_result = json.loads(res_str)
                            _tool_status = _tool_result.get("status", "unknown")
                        except Exception:
                            _tool_status = "unknown"
                        try:
                            await EL.emit_tool_event(
                                "tool.executed", f"Native tool '{func_name}' executed",
                                tool_name=func_name,
                                result="success" if _tool_status == "success" else "error",
                                trace_id=_trace_id, agent_id=_agent_id_str, user_id=operator_name,
                                model_used=model_name, provider_used=provider_name,
                                detail={"args": {k: str(v)[:200] for k, v in args.items()}, "result_status": _tool_status},
                            )
                            # Also emit category-specific events for memory operations
                            if func_name == "store_memory" and _tool_status == "success":
                                _mem_id = None
                                try:
                                    _mem_id = json.loads(res_str).get("memory_id")
                                except Exception:
                                    pass
                                await EL.emit_memory_event(
                                    "memory.write", f"Memory inscribed: {args.get('title', 'untitled')[:80]}",
                                    trace_id=_trace_id, agent_id=_agent_id_str, user_id=operator_name,
                                    memory_ids=[_mem_id] if _mem_id else [],
                                    detail={
                                        "title": args.get("title", ""),
                                        "memory_type": args.get("memory_type", ""),
                                        "importance": args.get("importance", "0.7"),
                                        "content_length": len(args.get("content", "")),
                                    },
                                )
                        except Exception:
                            pass
                    break # Only one DB session needed

                # Continue the loop to hit LLM again with the tool results
                continue

            # ── Fallback: parse text-based <tool_call> blocks ──
            # Some models (e.g. Gemma4) output tool calls as text instead of
            # using the structured OpenAI format. Parse and execute them.
            full_text = "".join(assistant_tokens) if assistant_tokens else ""
            # Strip <think>...</think> blocks before parsing tool calls
            import re as _re
            full_text_clean = _re.sub(r"<think>.*?</think>", "", full_text, flags=_re.DOTALL).strip()
            if "<tool_call>" in full_text_clean and "</tool_call>" in full_text_clean:
                import logging as _logging
                _log = _logging.getLogger("shogun.agents")
                # Step 1: Extract each <tool_call>...</tool_call> block (non-greedy)
                _block_pattern = _re.compile(r"<tool_call>(.*?)</tool_call>", _re.DOTALL)
                _blocks = _block_pattern.findall(full_text_clean)
                # Step 2: Parse function name + args from each block
                _func_pattern = _re.compile(r"(\w+)\s*\(([\s\S]*)\)\s*$", _re.DOTALL)
                _tc_matches = []
                for _block in _blocks:
                    _m = _func_pattern.match(_block.strip())
                    if _m:
                        _tc_matches.append((_m.group(1), _m.group(2).strip()))
                _log.info(f"[Shogun] Text-mode tool calls found: {len(_tc_matches)} — {[m[0] for m in _tc_matches]}")
                if _tc_matches:
                    _text_tool_results = []
                    async for db in get_db():
                        for func_name, raw_args in _tc_matches:
                            # Parse arguments from various formats
                            args = {}
                            raw_args = raw_args.strip()
                            if raw_args:
                                try:
                                    # Try JSON first: func({"key": "val"})
                                    args = json.loads(raw_args)
                                except json.JSONDecodeError:
                                    # Try key=value pairs: func(key="val", key2="val2")
                                    # or func(folder={"INBOX"}, uid={"12345"})
                                    _kv_pattern = _re.compile(
                                        r'(\w+)\s*=\s*(?:'
                                        r'\{?"([^}]*?)"\}?'    # key={"value"} or key="value"
                                        r"|'([^']*?)'"         # key='value'
                                        r'|(\S+)'              # key=value (no quotes)
                                        r')',
                                    )
                                    for m in _kv_pattern.finditer(raw_args):
                                        k = m.group(1)
                                        v = m.group(2) or m.group(3) or m.group(4) or ""
                                        args[k] = v
                                _log.info(f"[Shogun] Text-mode tool '{func_name}' parsed args: {args}")

                            yield f"data: {json.dumps({'type': 'action', 'content': f'Executing {func_name}...'})}\n\n"
                            res_str = await execute_native_tool(func_name, args, db)
                            _text_tool_results.append((func_name, args, res_str))
                            _log.info(f"[Shogun] Text-mode tool '{func_name}' result: {res_str[:200]}")

                            try:
                                _tool_result = json.loads(res_str)
                                _tool_status = _tool_result.get("status", "unknown")
                            except Exception:
                                _tool_status = "unknown"
                            try:
                                await EL.emit_tool_event(
                                    "tool.executed", f"Native tool '{func_name}' executed (text-mode)",
                                    tool_name=func_name,
                                    result="success" if _tool_status == "success" else "error",
                                    trace_id=_trace_id, agent_id=_agent_id_str, user_id=operator_name,
                                    model_used=model_name, provider_used=provider_name,
                                    detail={"args": {k: str(v)[:200] for k, v in args.items()}, "result_status": _tool_status, "mode": "text_parse"},
                                )
                            except Exception:
                                pass
                        break  # Only one DB session needed

                    # Feed results back as a user message with tool outputs
                    _results_text = "\n\n".join(
                        f"Tool result for {fn}({json.dumps(a)}):\n{r}" for fn, a, r in _text_tool_results
                    )
                    messages.append({"role": "user", "content": f"[TOOL RESULTS — execute next steps based on these results]\n\n{_results_text}"})
                    continue
            
            # If no tool calls occurred or we are done, terminate loop
            break

        # ── EVENT: Response Complete ─────────────────────
        _tools_used_in_turn = []
        try:
            _last_content = messages[-1].get("content", "") or ""
            _resp_len = len(_last_content) if isinstance(_last_content, str) else 0
        except Exception:
            _resp_len = 0
        try:
            # Collect tool names used in this turn
            for msg in messages:
                if msg.get("role") == "tool" and msg.get("name"):
                    _tools_used_in_turn.append(msg["name"])

            await EL.emit_model_event(
                "model.response", f"Chat turn completed ({model_name})",
                model_used=model_name, provider_used=provider_name,
                trace_id=_trace_id, agent_id=_agent_id_str, user_id=operator_name,
                detail={"message_count": len(messages), "tools_used": len(_tools_used_in_turn)},
            )
        except Exception:
            pass

        # ── EVENT: Decision Influences (EU AI Act) ─────────
        try:
            await EL.emit_decision_event(
                "decision.influences",
                f"Decision influences for chat turn: {len(_tools_used_in_turn)} tools, {len(recalled_ids) if 'recalled_ids' in dir() else 0} memories",
                trace_id=_trace_id, agent_id=_agent_id_str, user_id=operator_name,
                model_used=model_name, provider_used=provider_name,
                use_case_context=_use_case_context,
                detail={
                    "inputs_used": recalled_ids if 'recalled_ids' in dir() else [],
                    "tools_used": _tools_used_in_turn,
                    "safeguards_applied": _safeguards if '_safeguards' in dir() else [],
                    "retrieval_context": _retrieval_context if '_retrieval_context' in dir() else [],
                    "decision_summary": f"Response generated via {model_name} with {len(_tools_used_in_turn)} tool invocations",
                },
            )
        except Exception:
            pass

        # ── EVENT: Oversight — Response Delivered ──────────
        try:
            await EL.emit_oversight_event(
                "oversight.response_delivered",
                f"AI response delivered for human review ({_resp_len} chars)",
                trace_id=_trace_id, agent_id=_agent_id_str, user_id=operator_name,
                detail={
                    "response_length": _resp_len,
                    "model": model_name,
                    "tools_used": _tools_used_in_turn,
                    "review_status": "implicit",
                },
            )
        except Exception:
            pass

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


def _append_chat_log(role: str, content: str) -> None:
    """Append a message to the chat log JSONL for drift monitoring.
    
    The file at logs/chat_log.jsonl stores the last N interactions
    for the Persona Drift Monitor to analyze.
    """
    import json as _json
    from datetime import datetime as _dt, timezone as _tz
    from pathlib import Path as _P
    from shogun.config import settings as _settings

    log_path = _P(_settings.log_path) / "chat_log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    entry = _json.dumps({
        "role": role,
        "content": content[:2000],  # cap to prevent huge entries
        "timestamp": _dt.now(_tz.utc).isoformat(),
    })
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except Exception:
        pass  # non-critical — don't break chat

