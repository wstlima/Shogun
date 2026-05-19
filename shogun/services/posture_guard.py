"""Posture Guard — runtime enforcement of Security Posture constraints.

Every AI operation entry point (chat, agent creation, Telegram) calls into
this module before proceeding.  The guard reads the **live** posture from the
database (via ``_get_agent_posture``) and raises or returns enforcement
decisions.

Enforcement matrix
──────────────────
  kill_switch_active  →  block ALL AI operations (chat, spawn, Telegram)
  max_active_subagents →  block Samurai creation when limit reached
  skill_auto_install   →  strip model-management tools from LLM tool list
  shell_enabled        →  (reserved for future shell tools)
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import HTTPException

log = logging.getLogger("shogun.posture_guard")


# ── Kill-switch gate ─────────────────────────────────────────────────

async def check_kill_switch() -> None:
    """Raise HTTP 503 if the global kill switch (HARAKIRI) is active.

    Call this at the top of every AI-facing entry point.
    """
    from shogun.api.security import _get_agent_posture

    posture = await _get_agent_posture()
    if posture.get("kill_switch_active", False):
        log.warning("[PostureGuard] Kill switch is ACTIVE — blocking operation")
        _emit_block_event("kill_switch", "Operation blocked: HARAKIRI kill switch is active")
        raise HTTPException(
            status_code=503,
            detail="⛩️ HARAKIRI active — all AI operations are suspended. "
                   "Deactivate the kill switch via the Torii to resume.",
        )


# ── Subagent limit gate ─────────────────────────────────────────────

async def check_subagent_limit() -> None:
    """Raise HTTP 403 if creating another Samurai would exceed the tier limit.

    Call this before any Samurai agent creation (API endpoint + native skill).
    """
    from shogun.api.security import _get_agent_posture
    from shogun.db.engine import async_session_factory
    from shogun.db.models.agent import Agent
    from sqlalchemy import select, func

    posture = await _get_agent_posture()
    max_agents = posture.get("max_active_subagents", 5)
    tier = posture.get("active_tier", "tactical")

    async with async_session_factory() as db:
        result = await db.execute(
            select(func.count()).select_from(Agent).where(
                Agent.agent_type == "samurai",
                Agent.status.in_(["active", "idle", "running"]),
                Agent.is_deleted == False,
            )
        )
        current_count = result.scalar() or 0

    if current_count >= max_agents:
        log.warning(
            "[PostureGuard] Subagent limit reached: %d/%d (tier=%s)",
            current_count, max_agents, tier,
        )
        _emit_block_event(
            "subagent_limit",
            f"Samurai creation blocked: {current_count}/{max_agents} active "
            f"(tier {tier.upper()} allows max {max_agents})",
        )
        raise HTTPException(
            status_code=403,
            detail=f"Security posture [{tier.upper()}] allows a maximum of "
                   f"{max_agents} active Samurai agents. Currently {current_count} "
                   f"are active. Change the security tier in the Torii to allow more.",
        )


async def check_subagent_limit_soft() -> str | None:
    """Non-raising variant for native skill execution — returns error string or None."""
    try:
        await check_subagent_limit()
        return None
    except HTTPException as exc:
        return exc.detail


# ── Tool filtering based on posture ──────────────────────────────────

async def get_posture_tool_filter() -> dict[str, Any]:
    """Return the current posture constraints relevant to tool gating.

    Returns a dict with:
        - kill_switch_active: bool
        - skill_auto_install: bool
        - shell_enabled: bool
        - max_active_subagents: int
        - active_tier: str

    The caller uses these to strip tools from the LLM's available tool list.
    """
    from shogun.api.security import _get_agent_posture

    posture = await _get_agent_posture()
    return {
        "kill_switch_active": posture.get("kill_switch_active", False),
        "skill_auto_install": posture.get("skill_auto_install", False),
        "shell_enabled": posture.get("shell_enabled", False),
        "max_active_subagents": posture.get("max_active_subagents", 5),
        "active_tier": posture.get("active_tier", "tactical"),
    }


def filter_tools_by_posture(tools: list[dict], posture: dict) -> tuple[list[dict], list[str]]:
    """Filter a tool list based on posture constraints.

    Returns (allowed_tools, denied_tool_names).
    """
    allowed = []
    denied = []

    for tool in tools:
        name = tool["function"]["name"]

        # spawn_samurai blocked when max_active_subagents == 0 (SHRINE)
        if name == "spawn_samurai" and posture.get("max_active_subagents", 5) == 0:
            denied.append(name)
            continue

        # Model management tools blocked when skill_auto_install is False
        if name in ("list_available_models", "update_model_settings"):
            if not posture.get("skill_auto_install", False):
                denied.append(name)
                continue

        allowed.append(tool)

    return allowed, denied


# ── Event emission helper ────────────────────────────────────────────

def _emit_block_event(block_type: str, message: str) -> None:
    """Fire-and-forget compliance event for blocked operations."""
    try:
        import asyncio
        from shogun.services.event_logger import EventLogger

        asyncio.ensure_future(EventLogger.emit_policy_event(
            f"policy.posture_blocked",
            message,
            severity="warn",
            policy_ref=f"posture_guard:{block_type}",
            policy_decision="denied",
            policy_reason=message,
        ))
        asyncio.ensure_future(EventLogger.emit_risk_event(
            f"risk.posture_enforcement",
            message,
            severity="warn",
            risk_score="medium",
            detail={"block_type": block_type},
        ))
    except Exception:
        pass
