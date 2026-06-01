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
            "name": "echo_tool",
            "description": "A debug tool that echoes back exactly what you send it. Use this to verify that the tool execution pipeline is working.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to echo back.",
                    },
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "tool_list_debug",
            "description": "A debug tool that returns a list of all tools available to the current mission context.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
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
    {
        "type": "function",
        "function": {
            "name": "fetch_inbox",
            "description": "Fetch a list of emails from a mail folder. Returns message summaries with UID, sender, subject, date, and a short body preview. Use this to check the inbox or any folder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "folder": {
                        "type": "string",
                        "description": "The mail folder to fetch from (e.g. 'INBOX', 'Sent', 'Drafts'). Defaults to 'INBOX'.",
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination (1-based). Defaults to 1.",
                    },
                    "per_page": {
                        "type": "integer",
                        "description": "Number of messages per page. Defaults to 10.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_email",
            "description": "Read the full contents of a specific email by its UID. Returns the complete body text, HTML, sender, subject, date, and attachments list. Use this after fetch_inbox to read a specific message.",
            "parameters": {
                "type": "object",
                "properties": {
                    "uid": {
                        "type": "string",
                        "description": "The UID of the email message to read (obtained from fetch_inbox results).",
                    },
                    "folder": {
                        "type": "string",
                        "description": "The mail folder the message is in. Defaults to 'INBOX'.",
                    },
                },
                "required": ["uid"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email via the configured SMTP account. Use this to compose new emails or reply to messages. For replies, include the original context in the body.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_address": {
                        "type": "string",
                        "description": "Recipient email address.",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject line.",
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body text (plain text).",
                    },
                    "cc_address": {
                        "type": "string",
                        "description": "Optional CC recipients (comma-separated).",
                    },
                    "bcc_address": {
                        "type": "string",
                        "description": "Optional BCC recipients (comma-separated).",
                    },
                },
                "required": ["to_address", "subject", "body"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_calendar_events",
            "description": "List calendar events within a date range. Returns event titles, times, locations, and descriptions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in ISO format (e.g. '2026-05-22T00:00:00'). Defaults to today.",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in ISO format (e.g. '2026-05-29T23:59:59'). Defaults to 7 days from start.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_calendar_event",
            "description": "Create a new calendar event.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Event title.",
                    },
                    "start": {
                        "type": "string",
                        "description": "Event start time in ISO format (e.g. '2026-05-22T14:00:00').",
                    },
                    "end": {
                        "type": "string",
                        "description": "Event end time in ISO format (e.g. '2026-05-22T15:00:00').",
                    },
                    "location": {
                        "type": "string",
                        "description": "Optional event location.",
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional event description or notes.",
                    },
                    "all_day": {
                        "type": "boolean",
                        "description": "Whether this is an all-day event. Defaults to false.",
                    },
                },
                "required": ["title", "start", "end"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_cron_jobs",
            "description": "List all Bushido schedules (cron jobs). Returns each job's name, type, frequency, schedule time, enabled status, and next run time.",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_cron_job",
            "description": "Create a new custom Bushido schedule (cron job). Specify the job type, frequency, schedule time, and optional task instruction.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Display name for this schedule (e.g. 'Nightly Memory Consolidation').",
                    },
                    "job_type": {
                        "type": "string",
                        "enum": ["consolidation", "reflection", "pruning", "calibration", "health_check", "custom"],
                        "description": "Type of job to schedule.",
                    },
                    "frequency": {
                        "type": "string",
                        "enum": ["hourly", "nightly", "weekly", "monthly", "one_off"],
                        "description": "How often the job runs. Defaults to 'nightly'.",
                    },
                    "schedule_time": {
                        "type": "string",
                        "description": "Time of day to run in HH:MM format (e.g. '02:00'). Used for nightly/weekly/monthly.",
                    },
                    "task_instruction": {
                        "type": "string",
                        "description": "Optional custom instruction text for the job to execute.",
                    },
                    "is_enabled": {
                        "type": "boolean",
                        "description": "Whether to enable the job immediately. Defaults to true.",
                    },
                },
                "required": ["name", "job_type"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_cron_job",
            "description": "Delete a custom Bushido schedule (cron job) by its ID. Preset schedules cannot be deleted, only disabled.",
            "parameters": {
                "type": "object",
                "properties": {
                    "schedule_id": {
                        "type": "string",
                        "description": "The UUID of the schedule to delete.",
                    },
                },
                "required": ["schedule_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_agent_flow",
            "description": "Create a new Agent Flow workflow with nodes and edges. Use this when the user asks you to build, design, or create a workflow or pipeline for orchestrating AI agents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name of the workflow (e.g. 'Research Pipeline', 'Content Review Flow').",
                    },
                    "description": {
                        "type": "string",
                        "description": "Brief description of the workflow's purpose.",
                    },
                    "nodes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "Unique node ID (e.g. 'node-1', 'node-2')."},
                                "node_type": {"type": "string", "enum": ["input", "samurai", "shogun_approval", "logic", "output", "mado_browser"], "description": "Type of node."},
                                "label": {"type": "string", "description": "Display label for the node."},
                                "position_x": {"type": "number", "description": "X position on canvas (start at 100, space 300 apart)."},
                                "position_y": {"type": "number", "description": "Y position on canvas (start at 200, space 150 apart)."},
                                "config": {"type": "object", "description": "Node-specific config (task_description, approval_mode, condition_expression, etc.)."},
                            },
                            "required": ["id", "node_type", "label"],
                        },
                        "description": "Array of workflow nodes.",
                    },
                    "edges": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "source_node_id": {"type": "string", "description": "ID of the source node."},
                                "target_node_id": {"type": "string", "description": "ID of the target node."},
                                "label": {"type": "string", "description": "Optional edge label."},
                            },
                            "required": ["source_node_id", "target_node_id"],
                        },
                        "description": "Array of connections between nodes.",
                    },
                },
                "required": ["name", "nodes", "edges"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "browse_web",
            "description": "Browse a web page using Mado browser automation. Navigate to a URL and extract content. Requires Mado to be enabled in the Torii security settings.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to navigate to.",
                    },
                    "extract_type": {
                        "type": "string",
                        "enum": ["text", "html"],
                        "description": "What to extract from the page: 'text' for readable content, 'html' for raw HTML.",
                    },
                    "selector": {
                        "type": "string",
                        "description": "Optional CSS selector to extract content from a specific element.",
                    },
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "take_screenshot",
            "description": "Take a screenshot of the current browser page. Must have navigated to a URL first using browse_web.",
            "parameters": {
                "type": "object",
                "properties": {
                    "full_page": {
                        "type": "boolean",
                        "description": "If true, capture the full scrollable page. Default: false (viewport only).",
                    },
                },
            },
        },
    },
]


def generate_tool_prompt(tools: list[dict]) -> str:
    """Generate a human-readable tool description block for prompt injection.

    When a model does not support the OpenAI structured `tools` API parameter,
    we inject this text block into the system prompt instead. The model is
    instructed to output tool calls in a parseable `<tool_call>` format.
    """
    lines = [
        "## Available Tools",
        "",
        "You have access to the following tools. When you decide to call a tool, you must execute it by writing the tool call in one of the following formats.",
        "Prefer writing it exactly in the `<tool_call>` tag format:",
        "",
        "<tool_call>",
        "tool_name(param1=\"value1\", param2=\"value2\")",
        "</tool_call>",
        "",
        "For example, to list available models, output exactly:",
        "<tool_call>",
        "list_available_models()",
        "</tool_call>",
        "",
        "CRITICAL RULES:",
        "- You MUST output the tool call exactly as defined. Do not modify the tool name.",
        "- Output ONLY ONE tool call at a time, then STOP and wait for the result.",
        "- Do NOT hallucinate or fabricate tool results. The system will execute the tool and provide the real output.",
        "- After receiving a tool result, continue with your next action or provide the final answer.",
        "- For tools with no required parameters, call them with empty parentheses: tool_name()",
        "",
        "### Tool Definitions",
        "",
    ]

    for tool in tools:
        func = tool["function"]
        name = func["name"]
        desc = func["description"]
        params = func.get("parameters", {}).get("properties", {})
        required = func.get("parameters", {}).get("required", [])

        # Build parameter signature
        param_parts = []
        for pname, pdef in params.items():
            ptype = pdef.get("type", "string")
            is_req = pname in required
            marker = " [REQUIRED]" if is_req else ""
            param_parts.append(f'{pname}: {ptype}{marker}')

        sig = ", ".join(param_parts) if param_parts else ""
        lines.append(f"**{name}**({sig})")
        lines.append(f"  {desc}")

        # Parameter details
        if params:
            for pname, pdef in params.items():
                pdesc = pdef.get("description", "")
                is_req = pname in required
                enum = pdef.get("enum")
                enum_str = f" (one of: {', '.join(enum)})" if enum else ""
                req_str = " ⚠️ required" if is_req else ""
                lines.append(f"  - `{pname}`: {pdesc}{enum_str}{req_str}")
        lines.append("")

    return "\n".join(lines)


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
            
        elif name == "echo_tool":
            return json.dumps({
                "status": "success",
                "echoed_text": args.get("text", "")
            })
            
        elif name == "tool_list_debug":
            return json.dumps({
                "status": "success",
                "available_tools": [t["function"]["name"] for t in NATIVE_TOOLS]
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

        elif name == "fetch_inbox":
            from shogun.services.email_service import EmailService
            email_svc = EmailService(db_session)
            folder = args.get("folder", "INBOX")
            page = args.get("page", 1)
            per_page = args.get("per_page", 10)
            result = await email_svc.fetch_messages(folder=folder, page=page, per_page=per_page)
            # Trim to essential fields for token efficiency
            messages_summary = []
            for msg in result.get("messages", []):
                messages_summary.append({
                    "uid": msg["uid"],
                    "from": msg["from_address"],
                    "to": msg["to_address"],
                    "subject": msg["subject"],
                    "date": msg["date"],
                    "preview": msg.get("body_preview", "")[:120],
                    "is_read": msg["is_read"],
                })
            return json.dumps({
                "status": "success",
                "folder": folder,
                "total": result.get("total", 0),
                "page": page,
                "messages": messages_summary,
            })

        elif name == "read_email":
            from shogun.services.email_service import EmailService
            email_svc = EmailService(db_session)
            uid = args["uid"]
            folder = args.get("folder", "INBOX")
            result = await email_svc.fetch_message(uid=uid, folder=folder)
            return json.dumps({
                "status": "success",
                "uid": result["uid"],
                "from": result["from_address"],
                "to": result["to_address"],
                "subject": result["subject"],
                "date": result["date"],
                "body_text": result.get("body_text", "")[:3000],
                "has_attachments": result.get("has_attachments", False),
                "attachments": result.get("attachments", []),
            })

        elif name == "send_email":
            from shogun.services.email_service import EmailService
            from shogun.schemas.channels import EmailComposeRequest
            email_svc = EmailService(db_session)
            compose = EmailComposeRequest(
                to_address=args["to_address"],
                subject=args["subject"],
                body=args["body"],
                cc_address=args.get("cc_address"),
                bcc_address=args.get("bcc_address"),
            )
            result = await email_svc.send_email(compose)
            return json.dumps({
                "status": "success" if result.get("ok") else "error",
                "message": result.get("message", "Email operation completed."),
            })

        elif name == "list_calendar_events":
            from shogun.services.calendar_service import CalendarService
            from datetime import datetime, timedelta
            cal_svc = CalendarService(db_session)
            start_str = args.get("start_date")
            end_str = args.get("end_date")
            if start_str:
                start_dt = datetime.fromisoformat(start_str)
            else:
                start_dt = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if end_str:
                end_dt = datetime.fromisoformat(end_str)
            else:
                end_dt = start_dt + timedelta(days=7)
            events = await cal_svc.get_events(start_date=start_dt, end_date=end_dt)
            events_summary = []
            for ev in events:
                events_summary.append({
                    "id": ev.id,
                    "title": ev.title,
                    "start": str(ev.start),
                    "end": str(ev.end),
                    "location": ev.location,
                    "description": (ev.description or "")[:200],
                    "all_day": ev.all_day,
                })
            return json.dumps({
                "status": "success",
                "range": f"{start_dt.isoformat()} to {end_dt.isoformat()}",
                "count": len(events_summary),
                "events": events_summary,
            })

        elif name == "create_calendar_event":
            from shogun.services.calendar_service import CalendarService
            from shogun.schemas.channels import CalendarEventCreate
            from datetime import datetime
            cal_svc = CalendarService(db_session)
            event_data = CalendarEventCreate(
                title=args["title"],
                start=datetime.fromisoformat(args["start"]),
                end=datetime.fromisoformat(args["end"]),
                location=args.get("location"),
                description=args.get("description"),
                all_day=args.get("all_day", False),
            )
            result = await cal_svc.create_event(event_data)
            return json.dumps({
                "status": "success",
                "message": f"Calendar event '{args['title']}' created successfully.",
                "event_id": result.id,
            })

        elif name == "list_cron_jobs":
            from shogun.services.bushido_schedule_service import BushidoScheduleService
            sched_svc = BushidoScheduleService(db_session)
            records, total = await sched_svc.get_all(limit=200)
            jobs = []
            for r in records:
                jobs.append({
                    "id": str(r.id),
                    "name": r.name,
                    "job_type": r.job_type,
                    "frequency": r.frequency,
                    "schedule_time": r.schedule_time,
                    "is_enabled": r.is_enabled,
                    "is_preset": r.is_preset,
                    "next_run_at": str(r.next_run_at) if r.next_run_at else None,
                    "last_run_at": str(r.last_run_at) if r.last_run_at else None,
                })
            return json.dumps({
                "status": "success",
                "total": total,
                "schedules": jobs,
            })

        elif name == "create_cron_job":
            from shogun.services.bushido_schedule_service import BushidoScheduleService
            from shogun.schemas.bushido import BushidoScheduleCreate
            sched_svc = BushidoScheduleService(db_session)
            create_data = BushidoScheduleCreate(
                name=args["name"],
                job_type=args["job_type"],
                frequency=args.get("frequency", "nightly"),
                schedule_time=args.get("schedule_time", "02:00"),
                task_instruction=args.get("task_instruction"),
                is_enabled=args.get("is_enabled", True),
            )
            record = await sched_svc.create(**create_data.model_dump())
            # Register with APScheduler
            try:
                from shogun.scheduler import register_schedule
                await register_schedule(record)
            except Exception as exc:
                logger.warning("Scheduler registration failed: %s", exc)
            return json.dumps({
                "status": "success",
                "message": f"Cron job '{args['name']}' ({args['job_type']}) created and registered.",
                "schedule_id": str(record.id),
            })

        elif name == "delete_cron_job":
            from shogun.services.bushido_schedule_service import BushidoScheduleService
            import uuid as _uuid
            sched_svc = BushidoScheduleService(db_session)
            schedule_id = _uuid.UUID(args["schedule_id"])
            record = await sched_svc.get_by_id(schedule_id)
            if not record:
                return json.dumps({"status": "error", "message": "Schedule not found."})
            if record.is_preset:
                return json.dumps({"status": "error", "message": "Preset schedules cannot be deleted. Use toggle to disable them."})
            # Deregister from APScheduler
            try:
                from shogun.scheduler import deregister_schedule
                await deregister_schedule(schedule_id)
            except Exception as exc:
                logger.warning("Scheduler deregistration failed: %s", exc)
            await sched_svc.delete(schedule_id)
            return json.dumps({
                "status": "success",
                "message": f"Cron job '{record.name}' deleted successfully.",
            })

        elif name == "create_agent_flow":
            # ── Posture enforcement: requires agentflow_autonomous ──
            try:
                from shogun.services.posture_guard import get_posture_permissions
                perms = await get_posture_permissions()
                if not perms.get("agentflow_autonomous", False):
                    return json.dumps({
                        "status": "error",
                        "message": "Autonomous Agent Flow creation requires CAMPAIGN or RONIN security tier. Current tier does not permit agentflow_autonomous."
                    })
            except Exception:
                pass  # If posture guard unavailable, allow

            from shogun.services.agent_flow_service import AgentFlowService
            flow_svc = AgentFlowService(db_session)

            # Create the flow
            flow_name = args.get("name", "Untitled Flow")
            flow_desc = args.get("description", "Auto-generated by Shogun")
            flow = await flow_svc.create(
                name=flow_name,
                description=flow_desc,
                trigger_type="manual",
            )

            # Build node and edge payloads
            nodes_data = []
            for i, n in enumerate(args.get("nodes", [])):
                nodes_data.append({
                    "id": n.get("id", f"node-auto-{i}"),
                    "node_type": n.get("node_type", "samurai"),
                    "label": n.get("label", f"Node {i+1}"),
                    "position_x": n.get("position_x", 100 + i * 300),
                    "position_y": n.get("position_y", 200),
                    "config": n.get("config", {}),
                })

            edges_data = []
            for j, e in enumerate(args.get("edges", [])):
                edges_data.append({
                    "id": f"edge-auto-{j}",
                    "source_node_id": e.get("source_node_id", ""),
                    "target_node_id": e.get("target_node_id", ""),
                    "source_handle": e.get("source_handle"),
                    "target_handle": e.get("target_handle"),
                    "label": e.get("label"),
                    "edge_type": e.get("edge_type", "default"),
                    "config": {},
                })

            # Save the graph
            await flow_svc.save_flow_graph(
                flow_id=flow.id,
                nodes_data=nodes_data,
                edges_data=edges_data,
                viewport={"x": 0, "y": 0, "zoom": 0.8},
            )

            await db_session.commit()

            return json.dumps({
                "status": "success",
                "message": f"Agent Flow '{flow_name}' created with {len(nodes_data)} nodes and {len(edges_data)} edges. Open the Samurai Network → Agent Flow tab to view and run it.",
                "flow_id": str(flow.id),
            })

        elif name == "browse_web":
            # ── Mado browser automation ──────────────────────────
            from shogun.services.posture_guard import get_posture_tool_filter
            from shogun.services import mado_service

            posture = await get_posture_tool_filter()
            if not posture.get("mado_enabled", False):
                return json.dumps({
                    "status": "error",
                    "message": f"Browser automation is disabled at tier {posture.get('active_tier', 'unknown').upper()}. Enable Mado in the Torii.",
                })

            url = args.get("url", "")
            extract_type = args.get("extract_type", "text")
            selector = args.get("selector")

            # Use a persistent native-skill session
            session_id = "native_skill_browser"
            await mado_service.launch_browser(
                session_id=session_id,
                profile_name="native_skill",
                mode="headless",
            )

            # Navigate
            domain_allowlist = posture.get("mado_domain_allowlist", [])
            nav_result = await mado_service.navigate(
                session_id=session_id,
                url=url,
                domain_allowlist=domain_allowlist if domain_allowlist else None,
            )

            if nav_result.get("status") == "blocked":
                return json.dumps({
                    "status": "error",
                    "message": f"Navigation blocked: {nav_result.get('reason', 'Domain not allowed')}",
                })

            # Extract content
            extract_result = await mado_service.extract_content(
                session_id=session_id,
                selector=selector,
                extract_type=extract_type,
            )

            return json.dumps({
                "status": "success",
                "url": nav_result.get("url", url),
                "title": nav_result.get("title", ""),
                "content": extract_result.get("content", "")[:20000],
            })

        elif name == "take_screenshot":
            # ── Mado screenshot ──────────────────────────────────
            from shogun.services.posture_guard import get_posture_tool_filter
            from shogun.services import mado_service

            posture = await get_posture_tool_filter()
            if not posture.get("mado_enabled", False):
                return json.dumps({
                    "status": "error",
                    "message": "Browser automation is disabled. Enable Mado in the Torii.",
                })

            session_id = "native_skill_browser"
            full_page = args.get("full_page", False)

            result = await mado_service.screenshot(
                session_id=session_id,
                full_page=full_page,
            )

            if result.get("status") == "error":
                return json.dumps({
                    "status": "error",
                    "message": f"Screenshot failed: {result.get('error', 'No active browser session. Use browse_web first.')}",
                })

            return json.dumps({
                "status": "success",
                "message": f"Screenshot saved: {result.get('filename', 'unknown')}",
                "path": result.get("path", ""),
            })

        else:
            return json.dumps({"status": "error", "message": f"Unknown tool: {name}"})
            
    except Exception as e:
        logger.error(f"Native skill execution failed: {e}", exc_info=True)
        return json.dumps({"status": "error", "message": str(e)})


