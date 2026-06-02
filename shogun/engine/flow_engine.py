"""Flow Execution Engine — DAG-walking runtime for Agent Flow workflows.

Walks a flow's node graph in topological order, executing each node type:
- Input: provides initial context
- Samurai: delegates to LLM via agent's routing profile
- Shogun Approval: gate that checks approval policy
- Logic/Decision: evaluates condition to select branches
- Output: formats and stores final result

Supports parallel execution of independent sibling nodes.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shogun.db.engine import async_session_factory
from shogun.db.models.agent import Agent
from shogun.db.models.agent_flow import AgentFlow, AgentFlowNode, AgentFlowEdge
from shogun.db.models.agent_flow_run import AgentFlowRun
from shogun.db.models.model_provider import ModelProvider
from shogun.db.models.model_routing import ModelRoutingProfile

log = logging.getLogger("shogun.flow_engine")

# ── Active runs registry (for cancellation) ─────────────────
_active_runs: dict[str, asyncio.Task] = {}


# ═══════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════


async def start_flow_run(
    flow_id: uuid.UUID,
    trigger_type: str = "manual",
) -> uuid.UUID:
    """Create a FlowRun record and launch execution as a background task.

    Returns the run ID immediately. Execution proceeds asynchronously.
    """
    run_id = uuid.uuid4()

    async with async_session_factory() as session:
        # Verify flow exists and is not deleted
        result = await session.execute(
            select(AgentFlow).where(
                AgentFlow.id == flow_id,
                AgentFlow.is_deleted == False,
            )
        )
        flow = result.scalar_one_or_none()
        if not flow:
            raise ValueError(f"Agent Flow {flow_id} not found or deleted")

        run = AgentFlowRun(
            id=run_id,
            flow_id=flow_id,
            status="pending",
            trigger_type=trigger_type,
            node_states={},
            result_summary={},
        )
        session.add(run)
        await session.commit()

    # Launch as background task
    task = asyncio.create_task(_execute_flow(run_id, flow_id))
    _active_runs[str(run_id)] = task

    # Auto-cleanup when done
    def _cleanup(t: asyncio.Task):
        _active_runs.pop(str(run_id), None)

    task.add_done_callback(_cleanup)

    log.info("Flow run %s started for flow %s (trigger=%s)", run_id, flow_id, trigger_type)
    return run_id


async def cancel_flow_run(run_id: uuid.UUID) -> bool:
    """Cancel a running flow execution."""
    task = _active_runs.get(str(run_id))
    if task and not task.done():
        task.cancel()
        # Update DB status
        async with async_session_factory() as session:
            result = await session.execute(
                select(AgentFlowRun).where(AgentFlowRun.id == run_id)
            )
            run = result.scalar_one_or_none()
            if run:
                run.status = "cancelled"
                run.completed_at = datetime.now(timezone.utc)
                run.error_message = "Cancelled by user"
                await session.commit()
        log.info("Flow run %s cancelled", run_id)
        return True
    return False


# ═══════════════════════════════════════════════════════════════
# CORE EXECUTION LOOP
# ═══════════════════════════════════════════════════════════════


async def _execute_flow(run_id: uuid.UUID, flow_id: uuid.UUID) -> None:
    """Main execution loop — loads flow, walks DAG, executes nodes."""
    try:
        async with async_session_factory() as session:
            # ── 1. Load flow with nodes and edges ──────────────────
            result = await session.execute(
                select(AgentFlow)
                .where(AgentFlow.id == flow_id)
                .options(
                    selectinload(AgentFlow.nodes),
                    selectinload(AgentFlow.edges),
                )
            )
            flow = result.scalar_one_or_none()
            if not flow:
                await _fail_run(run_id, "Flow not found")
                return

            nodes = list(flow.nodes)
            edges = list(flow.edges)

            if not nodes:
                await _fail_run(run_id, "Flow has no nodes")
                return

            # ── 2. Mark run as running ─────────────────────────────
            run_result = await session.execute(
                select(AgentFlowRun).where(AgentFlowRun.id == run_id)
            )
            run = run_result.scalar_one()
            run.status = "running"
            run.started_at = datetime.now(timezone.utc)

            # Initialize node states
            node_states: dict[str, dict[str, Any]] = {}
            for node in nodes:
                node_states[str(node.id)] = {
                    "status": "pending",
                    "output": None,
                    "error": None,
                    "started_at": None,
                    "completed_at": None,
                }
            run.node_states = node_states
            await session.commit()

        # ── 3. Topological sort ────────────────────────────────
        try:
            execution_layers = _topological_sort(nodes, edges)
        except ValueError as e:
            await _fail_run(run_id, str(e))
            return

        # ── 4. Build lookup maps ───────────────────────────────
        node_map: dict[str, AgentFlowNode] = {str(n.id): n for n in nodes}
        edge_list = edges

        # Build predecessor map: node_id → [source_node_ids]
        predecessors: dict[str, list[str]] = defaultdict(list)
        for edge in edge_list:
            predecessors[str(edge.target_node_id)].append(str(edge.source_node_id))

        # Build edge map for logic nodes: source_node_id → [(target_node_id, source_handle)]
        edge_by_source: dict[str, list[tuple[str, str | None]]] = defaultdict(list)
        for edge in edge_list:
            edge_by_source[str(edge.source_node_id)].append(
                (str(edge.target_node_id), edge.source_handle)
            )

        # ── 5. Walk layers ─────────────────────────────────────
        # node_outputs stores the output of each completed node
        node_outputs: dict[str, Any] = {}
        # skipped_nodes tracks nodes that should be skipped (logic branch pruning)
        skipped_nodes: set[str] = set()

        for layer in execution_layers:
            # Filter out skipped nodes
            active_nodes = [nid for nid in layer if nid not in skipped_nodes]

            if not active_nodes:
                continue

            # Execute all nodes in this layer in parallel
            tasks = []
            for node_id in active_nodes:
                node = node_map[node_id]
                # Gather predecessor outputs as context
                pred_outputs = {}
                for pred_id in predecessors.get(node_id, []):
                    if pred_id in node_outputs:
                        pred_outputs[pred_id] = node_outputs[pred_id]

                tasks.append(
                    _execute_single_node(
                        run_id=run_id,
                        node=node,
                        predecessor_outputs=pred_outputs,
                        node_map=node_map,
                    )
                )

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for node_id, result in zip(active_nodes, results):
                node = node_map[node_id]
                if isinstance(result, Exception):
                    node_outputs[node_id] = None
                    await _update_node_state(
                        run_id, node_id, "failed", error=str(result)
                    )
                    # Check failure action
                    config = node.config or {}
                    failure_action = config.get("failure_action", "stop")
                    if failure_action == "stop":
                        await _fail_run(
                            run_id,
                            f"Node '{node.label}' failed: {result}",
                            node_states_override=True,
                        )
                        return
                    elif failure_action == "skip":
                        # Mark downstream nodes as skipped
                        _mark_downstream_skipped(
                            node_id, edge_by_source, skipped_nodes
                        )
                    # "retry" and "escalate" fall through (retry handled inside _execute_single_node)
                else:
                    node_outputs[node_id] = result
                    await _update_node_state(
                        run_id, node_id, "completed", output=result
                    )

                    # ── Logic/Decision branch pruning ──────────
                    if node.node_type == "logic":
                        # result is True/False — prune the non-taken branch
                        taken_handle = None if result else "false"
                        for target_id, handle in edge_by_source.get(node_id, []):
                            if handle != taken_handle:
                                # This branch was NOT taken — skip all downstream
                                skipped_nodes.add(target_id)
                                _mark_downstream_skipped(
                                    target_id, edge_by_source, skipped_nodes
                                )
                            else:
                                # Ensure the taken branch is NOT skipped
                                skipped_nodes.discard(target_id)

        # ── 6. Mark skipped nodes ──────────────────────────────
        for nid in skipped_nodes:
            await _update_node_state(run_id, nid, "skipped")

        # ── 7. Build result summary ────────────────────────────
        # Collect output node results
        output_results = {}
        for node in nodes:
            if node.node_type == "output" and str(node.id) in node_outputs:
                output_results[node.label] = node_outputs[str(node.id)]

        await _complete_run(run_id, output_results or node_outputs)

    except asyncio.CancelledError:
        log.info("Flow run %s was cancelled", run_id)
        raise
    except Exception as exc:
        log.exception("Flow run %s failed with unexpected error", run_id)
        await _fail_run(run_id, f"Unexpected error: {str(exc)[:500]}")


# ═══════════════════════════════════════════════════════════════
# NODE EXECUTORS
# ═══════════════════════════════════════════════════════════════


async def _execute_single_node(
    run_id: uuid.UUID,
    node: AgentFlowNode,
    predecessor_outputs: dict[str, Any],
    node_map: dict[str, AgentFlowNode],
) -> Any:
    """Execute a single node and return its output."""
    node_id = str(node.id)
    await _update_node_state(run_id, node_id, "running")

    config = node.config or {}
    node_type = node.node_type

    # Build context string from predecessor outputs
    context_parts = []
    for pred_id, output in predecessor_outputs.items():
        pred_node = node_map.get(pred_id)
        pred_label = pred_node.label if pred_node else pred_id
        if output is not None:
            context_parts.append(f"[Output from '{pred_label}']:\n{_truncate(str(output), 4000)}")
    context_str = "\n\n".join(context_parts) if context_parts else ""

    # Additional context injection from config
    if config.get("context_injection"):
        context_str += f"\n\n[Additional Context]:\n{config['context_injection']}"

    if node_type == "input":
        return await _exec_input(config, context_str)
    elif node_type == "samurai":
        return await _exec_samurai(config, context_str)
    elif node_type == "shogun_approval":
        return await _exec_approval(config, predecessor_outputs)
    elif node_type == "logic":
        return await _exec_logic(config, predecessor_outputs)
    elif node_type == "output":
        return await _exec_output(config, context_str, predecessor_outputs)
    elif node_type == "mado_browser":
        return await _exec_mado_browser(config, context_str)
    elif node_type == "email_send":
        return await _exec_email_send(config, context_str)
    else:
        raise ValueError(f"Unknown node type: {node_type}")


async def _exec_input(config: dict, context_str: str) -> str:
    """Input node — returns its configuration as initial context.

    Handles multiple input types:
    - manual: uses manual_input text or description
    - document: reads uploaded file content from disk
    - scheduled/api/event/nexus: uses description as context
    """
    from pathlib import Path
    import logging

    log = logging.getLogger("shogun.flow")
    description = config.get("description", "")
    input_type = config.get("input_type", "manual")

    output_parts = []

    # Always include description if present
    if description:
        output_parts.append(description)

    # Type-specific context
    if input_type == "manual":
        manual_input = config.get("manual_input", "")
        if manual_input:
            output_parts.append(manual_input)

    elif input_type == "document":
        uploaded = config.get("uploaded_file")
        if uploaded and uploaded.get("path"):
            file_path = Path(uploaded["path"])
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding="utf-8", errors="replace")
                    output_parts.append(f"[Document: {uploaded.get('filename', 'unknown')}]\n{content}")
                    log.info("[Flow] Input: read document %s (%d chars)", uploaded["filename"], len(content))
                except Exception as exc:
                    output_parts.append(f"[ERROR reading document: {exc}]")
            else:
                output_parts.append(f"[Document not found: {uploaded.get('filename', 'unknown')}]")
        else:
            output_parts.append("[No document uploaded yet]")

    # Add any context from upstream nodes
    if context_str:
        output_parts.append(context_str)

    if not output_parts:
        output_parts.append(f"Workflow triggered ({input_type})")

    return "\n\n".join(output_parts)


async def _exec_samurai(config: dict, context_str: str) -> str:
    """Samurai node — delegates task to LLM using agent's routing profile."""
    task_description = config.get("task_description", "")
    expected_output = config.get("expected_output", "")
    agent_id = config.get("agent_id")
    routing_profile_id = config.get("routing_profile_id")
    timeout = config.get("timeout", 300)
    retry_count = config.get("retry_count", 0)

    if not task_description:
        raise ValueError("Samurai node has no task description")

    # Build the prompt
    user_message = task_description
    if context_str:
        user_message = f"{task_description}\n\n--- CONTEXT FROM PREVIOUS STEPS ---\n{context_str}"
    if expected_output:
        user_message += f"\n\n--- EXPECTED OUTPUT FORMAT ---\n{expected_output}"

    # Resolve agent persona
    agent_persona = "You are a Samurai agent executing a task in an automated workflow."
    async with async_session_factory() as session:
        if agent_id:
            agent_result = await session.execute(
                select(Agent).where(Agent.id == uuid.UUID(agent_id))
            )
            agent = agent_result.scalar_one_or_none()
            if agent:
                agent_persona = (
                    f"You are {agent.name}, a Samurai agent. "
                    f"{agent.description or ''}\n"
                    "You are executing a task as part of an automated Agent Flow workflow. "
                    "Respond with the requested output directly. Do not ask clarifying questions."
                )
                # Use agent's routing profile if not overridden
                if not routing_profile_id and agent.model_routing_profile_id:
                    routing_profile_id = str(agent.model_routing_profile_id)

        # Resolve LLM provider
        provider, model_name, base_url, headers = await _resolve_llm(
            session, routing_profile_id
        )

    if not provider:
        raise ValueError("No active LLM provider available for Samurai execution")

    messages = [
        {"role": "system", "content": agent_persona},
        {"role": "user", "content": user_message},
    ]

    # Execute with retries
    last_error = None
    for attempt in range(1 + retry_count):
        try:
            response = await _call_llm(messages, model_name, base_url, headers, timeout)
            return response
        except Exception as exc:
            last_error = exc
            if attempt < retry_count:
                log.warning(
                    "Samurai node LLM call failed (attempt %d/%d): %s",
                    attempt + 1, 1 + retry_count, exc,
                )
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    raise last_error or ValueError("Samurai execution failed")


async def _exec_approval(
    config: dict, predecessor_outputs: dict[str, Any]
) -> str:
    """Shogun Approval node — gate that checks approval policy."""
    approval_mode = config.get("approval_mode", "manual")
    confidence_threshold = config.get("confidence_threshold", 85)

    # Aggregate predecessor output for review
    review_content = "\n\n".join(
        str(v) for v in predecessor_outputs.values() if v is not None
    )

    if approval_mode == "manual":
        # In Phase 2, manual approval auto-approves with a note
        # Full human-in-the-loop requires WebSocket (future phase)
        return f"[AUTO-APPROVED — manual approval mode]\n{review_content}"

    elif approval_mode == "ai_assisted":
        # Use LLM to evaluate if the output is acceptable
        async with async_session_factory() as session:
            provider, model_name, base_url, headers = await _resolve_llm(session)

        if provider:
            judge_messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a quality assurance judge reviewing the output of an AI agent. "
                        "Evaluate the following output and respond with APPROVED if it meets quality standards, "
                        "or REJECTED with a brief reason if it does not."
                    ),
                },
                {"role": "user", "content": f"Review this output:\n\n{review_content[:3000]}"},
            ]
            verdict = await _call_llm(judge_messages, model_name, base_url, headers, 60)
            if "REJECTED" in verdict.upper():
                raise ValueError(f"AI review rejected: {verdict[:500]}")
            return f"[AI-APPROVED]\n{review_content}"

        return f"[AUTO-APPROVED — no LLM available for AI review]\n{review_content}"

    elif approval_mode == "confidence_threshold":
        # Auto-approve — threshold is informational in Phase 2
        return f"[AUTO-APPROVED — confidence threshold {confidence_threshold}%]\n{review_content}"

    elif approval_mode == "policy_based":
        # Check Torii posture for agentflow_execute permission
        try:
            from shogun.services.posture_guard import get_posture_permissions
            perms = await get_posture_permissions()
            if not perms.get("agentflow_execute", False):
                raise ValueError(
                    "Policy-based approval denied: agentflow_execute not permitted at current tier"
                )
        except ImportError:
            pass
        return f"[POLICY-APPROVED]\n{review_content}"

    return f"[APPROVED]\n{review_content}"


async def _exec_logic(
    config: dict, predecessor_outputs: dict[str, Any]
) -> bool:
    """Logic/Decision node — evaluates condition and returns True (right) or False (bottom)."""
    condition = config.get("condition_expression", "")

    if not condition:
        # No condition — always take the TRUE branch
        return True

    # Build context for evaluation
    context = "\n\n".join(
        str(v) for v in predecessor_outputs.values() if v is not None
    )

    # Use LLM to evaluate the condition
    async with async_session_factory() as session:
        provider, model_name, base_url, headers = await _resolve_llm(session)

    if not provider:
        # No LLM — default to True
        log.warning("Logic node: no LLM available, defaulting to TRUE branch")
        return True

    eval_messages = [
        {
            "role": "system",
            "content": (
                "You are a logic evaluator. Given a condition and context, "
                "evaluate whether the condition is TRUE or FALSE. "
                "Respond with exactly one word: TRUE or FALSE."
            ),
        },
        {
            "role": "user",
            "content": f"Condition: {condition}\n\nContext:\n{context[:3000]}",
        },
    ]

    try:
        result = await _call_llm(eval_messages, model_name, base_url, headers, 30)
        return "TRUE" in result.upper()
    except Exception:
        log.warning("Logic node evaluation failed, defaulting to TRUE")
        return True


async def _exec_output(
    config: dict, context_str: str, predecessor_outputs: dict[str, Any]
) -> str:
    """Output node — formats and returns the final result."""
    output_type = config.get("output_type", "artifact")
    fmt = config.get("format", "markdown")

    # Collect all predecessor outputs
    content = context_str or "\n\n".join(
        str(v) for v in predecessor_outputs.values() if v is not None
    )

    if fmt == "json":
        import json
        try:
            # Try to parse as JSON, otherwise wrap as JSON
            result = json.loads(content)
            return json.dumps(result, indent=2)
        except (json.JSONDecodeError, TypeError):
            return json.dumps({
                "output_type": output_type,
                "content": content,
            }, indent=2)
    elif fmt == "plain":
        # Strip markdown formatting
        import re
        return re.sub(r'[#*_`~\[\]]', '', content)

    # markdown or html — return as-is
    return content


async def _exec_mado_browser(config: dict, context_str: str) -> str:
    """Mado Browser node — executes browser automation actions.

    Supports: navigate, extract_content, screenshot, fill_form,
              click, execute_js, wait_for
    """
    from shogun.services import mado_service
    from shogun.services.posture_guard import get_posture_tool_filter

    action = config.get("action", "navigate")
    url = config.get("url", "")
    selector = config.get("selector")
    session_name = config.get("session_name", "flow_browser")
    browser_mode = config.get("browser_mode", "headless")

    # Check Torii permissions
    posture = await get_posture_tool_filter()
    if not posture.get("mado_enabled", False):
        return f"[BLOCKED] Browser automation is disabled at tier {posture.get('active_tier', 'unknown').upper()}"

    # Use a deterministic session ID for the flow to allow session reuse
    flow_session_id = f"flow_{session_name}"

    # Ensure browser is launched
    launch_result = await mado_service.launch_browser(
        session_id=flow_session_id,
        profile_name=f"flow_{session_name}",
        mode=browser_mode,
    )

    if launch_result.get("status") == "error":
        return f"[ERROR] Failed to launch browser: {launch_result.get('error', 'Unknown')}"

    try:
        if action == "navigate":
            # Use URL from config first; fall back to context string
            target_url = url or (context_str.strip().split("\n")[0] if context_str else "")
            if not target_url:
                return "[ERROR] No URL specified for navigation"

            log.info("[Mado/Flow] navigate → %s (session=%s)", target_url, flow_session_id)
            result = await mado_service.navigate(
                session_id=flow_session_id,
                url=target_url,
            )
            if result.get("status") == "error":
                log.error("[Mado/Flow] navigate FAILED: %s", result.get('error'))
                return f"[ERROR] Navigation failed: {result.get('error', 'Unknown')}"
            if result.get("status") == "blocked":
                return f"[BLOCKED] {result.get('reason', 'Domain not allowed')}"
            log.info("[Mado/Flow] navigate OK → %s", result.get('title', 'N/A'))
            return f"Navigated to: {result.get('url', target_url)}\nTitle: {result.get('title', 'N/A')}"

        elif action == "extract_content":
            extract_type = config.get("extract_type", "text")
            log.info("[Mado/Flow] extract '%s' (type=%s, session=%s)", selector, extract_type, flow_session_id)
            result = await mado_service.extract_content(
                session_id=flow_session_id,
                selector=selector,
                extract_type=extract_type,
            )
            content = result.get("content", "")
            status = result.get("status", "unknown")
            log.info("[Mado/Flow] extract result: status=%s, length=%d chars", status, len(content))
            if not content:
                return "[No content extracted — the page may not have matching elements]"
            return content

        elif action == "screenshot":
            full_page = config.get("full_page", False)
            result = await mado_service.screenshot(
                session_id=flow_session_id,
                full_page=full_page,
                selector=selector,
            )
            return f"Screenshot saved: {result.get('filename', 'unknown')}\nPath: {result.get('path', 'N/A')}"

        elif action == "fill_form":
            fields = config.get("fields", [])
            if not fields:
                return "[ERROR] No form fields specified"
            result = await mado_service.fill_form(
                session_id=flow_session_id,
                fields=fields,
            )
            return f"Filled {result.get('filled', 0)}/{result.get('total', 0)} fields"

        elif action == "click":
            if not selector:
                return "[ERROR] No selector specified for click"
            result = await mado_service.click_element(
                session_id=flow_session_id,
                selector=selector,
            )
            return f"Clicked: {selector}\nURL after click: {result.get('url', 'N/A')}"

        elif action == "execute_js":
            script = config.get("script", "")
            if not script:
                return "[ERROR] No JavaScript specified"
            result = await mado_service.execute_js(
                session_id=flow_session_id,
                script=script,
            )
            return f"JS result: {result.get('result', 'undefined')}"

        elif action == "wait_for":
            if not selector:
                return "[ERROR] No selector specified for wait"
            timeout = config.get("timeout", 10000)
            result = await mado_service.wait_for_selector(
                session_id=flow_session_id,
                selector=selector,
                timeout=timeout,
            )
            if result.get("status") == "timeout":
                return f"[TIMEOUT] Selector '{selector}' not found within {timeout}ms"
            return f"Element found: {selector}"

        else:
            return f"[ERROR] Unknown Mado action: {action}"

    except Exception as exc:
        return f"[ERROR] Browser action '{action}' failed: {str(exc)[:500]}"


async def _exec_email_send(config: dict, context_str: str) -> str:
    """Email Send node — sends an email via the configured SMTP account.

    Uses the existing EmailService infrastructure.  If no body_template is
    provided the full predecessor output is used as the email body.
    """
    from shogun.services.email_service import EmailService
    from shogun.schemas.channels import EmailComposeRequest

    to_address = config.get("to_address", "")
    if not to_address:
        raise ValueError("Email Send node has no recipient (to_address)")

    subject = config.get("subject", "Shogun Agent Flow — Email")
    body_template = config.get("body_template", "")
    cc_address = config.get("cc_address") or None
    bcc_address = config.get("bcc_address") or None

    # Build the email body
    if body_template:
        # Allow a simple {{context}} placeholder for predecessor output
        body = body_template.replace("{{context}}", context_str)
    else:
        # No template — use the raw predecessor output as the body
        body = context_str or "(No content from previous steps)"

    # Send via EmailService
    async with async_session_factory() as session:
        svc = EmailService(session)
        acc = await svc.get_account()
        if not acc:
            raise ValueError(
                "No email account configured. Set up an account in the Mail page first."
            )
        if not acc.perm_send_mail:
            raise ValueError(
                "Email sending permission is disabled. Enable perm_send_mail in the Mail settings."
            )

        compose = EmailComposeRequest(
            to_address=to_address,
            cc_address=cc_address,
            bcc_address=bcc_address,
            subject=subject,
            body=body,
        )
        result = await svc.send_email(compose)

    status = result.get("message", "Sent")
    log.info("Email sent to %s — %s", to_address, status)
    return f"Email sent to {to_address}\nSubject: {subject}\nStatus: {status}"


# ═══════════════════════════════════════════════════════════════
# LLM RESOLUTION & CALLING
# ═══════════════════════════════════════════════════════════════


PROVIDER_URLS = {
    "ollama": "http://localhost:11434",
    "lmstudio": "http://localhost:1234/v1",
    "local": "http://localhost:1234/v1",
    "openai": "https://api.openai.com/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "anthropic": "https://api.anthropic.com/v1",
    "google": "https://generativelanguage.googleapis.com/v1beta/openai",
    "custom": "https://api.openai.com/v1",
}


async def _resolve_llm(
    session: AsyncSession,
    routing_profile_id: str | None = None,
) -> tuple[ModelProvider | None, str, str, dict]:
    """Resolve the LLM provider, model name, base URL, and headers.

    Returns (provider, model_name, base_url, headers) or (None, "", "", {}).
    """
    provider = None
    model_name = ""

    # Try routing profile first
    if routing_profile_id:
        try:
            rp_result = await session.execute(
                select(ModelRoutingProfile).where(
                    ModelRoutingProfile.id == uuid.UUID(routing_profile_id)
                )
            )
            rp = rp_result.scalar_one_or_none()
            if rp and rp.primary_model_id:
                prov_result = await session.execute(
                    select(ModelProvider).where(
                        ModelProvider.id == rp.primary_model_id,
                        ModelProvider.status == "connected",
                    )
                )
                provider = prov_result.scalar_one_or_none()
                if provider and rp.primary_model_name:
                    model_name = rp.primary_model_name
        except Exception as exc:
            log.warning("Failed to resolve routing profile %s: %s", routing_profile_id, exc)

    # Fallback to any connected provider
    if not provider:
        result = await session.execute(
            select(ModelProvider)
            .where(ModelProvider.status == "connected")
            .order_by(ModelProvider.created_at)
            .limit(1)
        )
        provider = result.scalar_one_or_none()

    if not provider:
        return None, "", "", {}

    # Resolve model name
    if not model_name:
        model_name = (
            provider.config.get("model_id")
            or (provider.config.get("models") or [None])[0]
            or provider.name
        )

    # Resolve base URL
    base_url = provider.base_url or PROVIDER_URLS.get(
        provider.provider_type, "https://api.openai.com/v1"
    )
    if provider.provider_type == "ollama" and not base_url.rstrip("/").endswith("/v1"):
        base_url = base_url.rstrip("/") + "/v1"

    # Build headers
    api_key = provider.config.get("api_key") or provider.config.get("api-key")
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if provider.provider_type == "openrouter":
        headers["HTTP-Referer"] = "https://shogun.ai"
        headers["X-Title"] = "Shogun AgentFlow"

    return provider, model_name, base_url, headers


async def _call_llm(
    messages: list[dict],
    model_name: str,
    base_url: str,
    headers: dict,
    timeout: int = 120,
) -> str:
    """Make a non-streaming chat completion call and return the response text."""
    url = f"{base_url.rstrip('/')}/chat/completions"
    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False,
        "temperature": 0.3,  # Low temperature for task execution
    }

    async with httpx.AsyncClient(timeout=float(timeout)) as client:
        resp = await client.post(url, headers=headers, json=payload)

        if resp.status_code >= 400:
            body = resp.text[:500]
            raise ValueError(f"LLM API error {resp.status_code}: {body}")

        data = resp.json()
        choices = data.get("choices", [])
        if not choices:
            raise ValueError("LLM returned no choices")

        content = choices[0].get("message", {}).get("content", "")
        if not content:
            raise ValueError("LLM returned empty content")

        return content


# ═══════════════════════════════════════════════════════════════
# GRAPH UTILITIES
# ═══════════════════════════════════════════════════════════════


def _topological_sort(
    nodes: list[AgentFlowNode],
    edges: list[AgentFlowEdge],
) -> list[list[str]]:
    """Sort nodes into execution layers (Kahn's algorithm).

    Returns a list of layers, where each layer contains node IDs that can
    be executed in parallel.

    Raises ValueError if the graph contains a cycle.
    """
    node_ids = {str(n.id) for n in nodes}

    # Build adjacency and in-degree
    in_degree: dict[str, int] = {nid: 0 for nid in node_ids}
    adjacency: dict[str, list[str]] = {nid: [] for nid in node_ids}

    for edge in edges:
        src = str(edge.source_node_id)
        tgt = str(edge.target_node_id)
        if src in node_ids and tgt in node_ids:
            adjacency[src].append(tgt)
            in_degree[tgt] += 1

    # Kahn's algorithm with layer tracking
    queue: deque[str] = deque()
    for nid, deg in in_degree.items():
        if deg == 0:
            queue.append(nid)

    layers: list[list[str]] = []
    visited = 0

    while queue:
        # All nodes currently in the queue form one parallel layer
        layer = list(queue)
        queue.clear()
        layers.append(layer)
        visited += len(layer)

        for nid in layer:
            for neighbor in adjacency[nid]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

    if visited != len(node_ids):
        raise ValueError(
            "Agent Flow contains a cycle — cannot execute. "
            "Remove circular dependencies and try again."
        )

    return layers


def _mark_downstream_skipped(
    node_id: str,
    edge_by_source: dict[str, list[tuple[str, str | None]]],
    skipped: set[str],
) -> None:
    """Recursively mark all downstream nodes as skipped."""
    for target_id, _ in edge_by_source.get(node_id, []):
        if target_id not in skipped:
            skipped.add(target_id)
            _mark_downstream_skipped(target_id, edge_by_source, skipped)


# ═══════════════════════════════════════════════════════════════
# STATE MANAGEMENT HELPERS
# ═══════════════════════════════════════════════════════════════


async def _update_node_state(
    run_id: uuid.UUID,
    node_id: str,
    status: str,
    output: Any = None,
    error: str | None = None,
) -> None:
    """Update a single node's execution state in the run record."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(AgentFlowRun).where(AgentFlowRun.id == run_id)
        )
        run = result.scalar_one_or_none()
        if not run:
            return

        states = dict(run.node_states or {})
        now = datetime.now(timezone.utc).isoformat()

        node_state = states.get(node_id, {})
        node_state["status"] = status

        if status == "running":
            node_state["started_at"] = now
        elif status in ("completed", "failed", "skipped"):
            node_state["completed_at"] = now

        if output is not None:
            # Truncate large outputs for storage
            output_str = str(output)
            node_state["output"] = output_str[:10000] if len(output_str) > 10000 else output_str
        if error:
            node_state["error"] = error[:2000]

        states[node_id] = node_state
        run.node_states = states
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(run, "node_states")
        await session.commit()


async def _fail_run(
    run_id: uuid.UUID,
    error_message: str,
    node_states_override: bool = False,
) -> None:
    """Mark a run as failed."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(AgentFlowRun).where(AgentFlowRun.id == run_id)
        )
        run = result.scalar_one_or_none()
        if not run:
            return

        run.status = "failed"
        run.completed_at = datetime.now(timezone.utc)
        run.error_message = error_message[:2000]
        await session.commit()

    log.error("Flow run %s FAILED: %s", run_id, error_message)


async def _complete_run(
    run_id: uuid.UUID,
    result_summary: dict[str, Any],
) -> None:
    """Mark a run as completed with results."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(AgentFlowRun).where(AgentFlowRun.id == run_id)
        )
        run = result.scalar_one_or_none()
        if not run:
            return

        run.status = "completed"
        run.completed_at = datetime.now(timezone.utc)

        # Truncate result summary values for storage
        truncated = {}
        for k, v in result_summary.items():
            v_str = str(v)
            truncated[k] = v_str[:5000] if len(v_str) > 5000 else v_str
        run.result_summary = truncated
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(run, "result_summary")
        await session.commit()

    log.info("Flow run %s COMPLETED", run_id)


def _truncate(text: str, max_len: int) -> str:
    """Truncate text with an ellipsis marker."""
    if len(text) <= max_len:
        return text
    return text[:max_len - 20] + "\n\n[...truncated...]"
