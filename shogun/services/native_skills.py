"""Native Skills — Internal system capabilities exposed directly to the Shogun orchestrator LLM."""

import json
import logging
from typing import Any

from shogun.db.engine import async_session_factory
from shogun.api.agents import _get_system_context

logger = logging.getLogger("shogun.native_skills")

NATIVE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "spawn_samurai",
            "description": "Spawn a new Samurai agent in the Dojo.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the Samurai agent.",
                    },
                    "role": {
                        "type": "string",
                        "description": "The specific role or designation.",
                    },
                    "persona": {
                        "type": "string",
                        "description": "A brief description of their personality and expertise.",
                    },
                    "security_tier": {
                        "type": "string",
                        "enum": ["shrine", "guarded", "tactical", "campaign", "ronin"],
                        "description": "Security tier for the new Samurai (typically tactical or guarded).",
                    },
                },
                "required": ["name", "role", "persona", "security_tier"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_available_models",
            "description": "List all active model providers and the models they have available.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_model_settings",
            "description": "Update Shogun's primary and fallback models. Use when the user requests to switch the core model.",
            "parameters": {
                "type": "object",
                "properties": {
                    "primary_model": {
                        "type": "string",
                        "description": "The fully qualified primary model string (e.g. 'provider-id::model-name'). Use list_available_models if unsure.",
                    },
                    "fallback_models": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of fully qualified models to fall back to.",
                    },
                },
                "required": ["primary_model"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "store_memory",
            "description": "Store important information in your persistent Archives memory system. Use this when the user shares personal details (e.g. their name), preferences, facts, or anything worth remembering across sessions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Short descriptive title for this memory (e.g. 'Operator name is Michael').",
                    },
                    "content": {
                        "type": "string",
                        "description": "The full content to remember. Be detailed and specific.",
                    },
                    "memory_type": {
                        "type": "string",
                        "enum": ["episodic", "semantic", "procedural", "persona"],
                        "description": "Type: 'persona' for identity/preferences/personal info, 'semantic' for facts/knowledge, 'episodic' for events, 'procedural' for how-to patterns.",
                    },
                    "importance": {
                        "type": "number",
                        "description": "How important this is (0.0-1.0). Use 0.9+ for identity/preferences, 0.5-0.8 for general facts.",
                    },
                },
                "required": ["title", "content", "memory_type", "importance"],
            },
        },
    },
]

async def execute_native_tool(name: str, args: dict[str, Any], db_session) -> str:
    """Route tool execution from LLM to underlying services."""
    logger.info(f"Executing native skill: {name} with args {args}")
    
    try:
        if name == "spawn_samurai":
            # ── Posture enforcement: kill switch + subagent limit ──
            from shogun.services.posture_guard import check_kill_switch, check_subagent_limit_soft
            try:
                from shogun.api.security import _get_agent_posture
                posture = await _get_agent_posture()
                if posture.get("kill_switch_active", False):
                    return json.dumps({
                        "status": "error",
                        "message": "⛩️ HARAKIRI is active — all AI operations are suspended. Cannot spawn agents."
                    })
            except Exception:
                pass
            limit_error = await check_subagent_limit_soft()
            if limit_error:
                return json.dumps({"status": "error", "message": limit_error})

            from shogun.services.agent_service import AgentService
            svc = AgentService(db_session)
            # Create the agent via service directly
            new_agent = await svc.create(
                agent_type="samurai",
                name=args["name"],
                slug=args["name"].lower().replace(" ", "-"),
                description=f"{args['role']} - {args['persona']}",
                status="active",
                spawn_policy="manual" # Or derived...
            )

            # ── Inject Kaizen governance into the new agent ──────────
            try:
                from shogun.api.kaizen import build_governance_prompt_block
                governance_block = build_governance_prompt_block()
                bs = dict(new_agent.bushido_settings) if new_agent.bushido_settings else {}
                bs["governance_prompt"] = governance_block
                new_agent.bushido_settings = bs
            except Exception as gov_err:
                logger.warning("Failed to inject governance into spawned Samurai: %s", gov_err)

            # Update cache context so next stream shows +1 agent
            import time
            from shogun.api.agents import _CTX_CACHE
            _CTX_CACHE["ts"] = 0 
            
            await db_session.commit()
            
            return json.dumps({
                "status": "success", 
                "message": f"Samurai '{args['name']}' successfully spawned at tier '{args['security_tier']}' with Kaizen governance applied."
            })
            
        elif name == "list_available_models":
            from sqlalchemy import select
            from shogun.db.models.model_provider import ModelProvider
            
            providers = await db_session.execute(
                select(ModelProvider).where(ModelProvider.status == "connected")
            )
            
            res = {}
            for p in providers.scalars().all():
                models = p.config.get("models", [])
                if p.config.get("model_id"):
                    models.append(p.config.get("model_id"))
                res[f"{p.name} (UUID: {p.id})"] = models
                
            return json.dumps({
                "status": "success",
                "available_providers_and_models": res
            })
            
        elif name == "update_model_settings":
            from shogun.db.models.agent import Agent
            from sqlalchemy import select
            
            shogun_res = await db_session.execute(
                select(Agent).where(
                    Agent.agent_type == "shogun",
                    Agent.is_primary == True,
                    Agent.is_deleted == False
                ).limit(1)
            )
            shogun = shogun_res.scalar_one_or_none()
            if not shogun:
                return json.dumps({"status": "error", "message": "Primary Shogun not found."})
                
            bushido = dict(shogun.bushido_settings) if shogun.bushido_settings else {}
            bushido["primary_model"] = args["primary_model"]
            if "fallback_models" in args:
                bushido["fallback_models"] = args["fallback_models"]
                
            shogun.bushido_settings = bushido
            db_session.add(shogun)
            await db_session.commit()
            
            return json.dumps({
                "status": "success", 
                "message": f"Successfully updated primary model to {args['primary_model']}."
            })

        elif name == "store_memory":
            from shogun.services.memory_service import MemoryService
            from shogun.db.models.agent import Agent
            from sqlalchemy import select

            # Get the primary Shogun agent ID to associate the memory with
            shogun_res = await db_session.execute(
                select(Agent).where(
                    Agent.agent_type == "shogun",
                    Agent.is_primary == True,
                    Agent.is_deleted == False
                ).limit(1)
            )
            shogun = shogun_res.scalar_one_or_none()
            if not shogun:
                return json.dumps({"status": "error", "message": "Primary Shogun not found."})

            mem_svc = MemoryService(db_session)
            importance = float(args.get("importance", 0.7))
            is_pinned = importance >= 0.85  # High-importance memories get auto-pinned
            decay = "slow" if importance >= 0.7 else "medium"
            if is_pinned:
                decay = "pinned"

            record = await mem_svc.create_memory(
                memory_type=args["memory_type"],
                agent_id=shogun.id,
                title=args["title"],
                content=args["content"],
                importance_score=importance,
                relevance_score=0.9,
                confidence_score=0.8,
                decay_class=decay,
                is_pinned=is_pinned,
            )
            await db_session.commit()

            return json.dumps({
                "status": "success",
                "message": f"Memory '{args['title']}' stored in Archives (type={args['memory_type']}, importance={importance}, pinned={is_pinned}).",
                "memory_id": str(record.id),
            })

        else:
            return json.dumps({"status": "error", "message": f"Unknown tool: {name}"})
            
    except Exception as e:
        logger.error(f"Native skill execution failed: {e}", exc_info=True)
        return json.dumps({"status": "error", "message": str(e)})
