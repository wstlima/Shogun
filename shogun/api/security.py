"""Security routes — policies, assignments, simulation."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException

from shogun.api.deps import get_security_service, get_db
from shogun.schemas.common import ApiResponse
from shogun.schemas.security import (
    SecurityPolicyCreate,
    SecurityPolicyResponse,
    SecurityPolicyUpdate,
    PermissionSimulateRequest,
    PermissionSimulateResponse,
    SecurityAssignRequest,
    SecurityPostureResponse,
)
from shogun.services.security_service import SecurityService

router = APIRouter(prefix="/security", tags=["Security"])

# ── In-process posture store (persisted via Agent.bushido_settings) ──
_POSTURE_KEY = "security_posture"
_DEFAULT_POSTURE = {
    "active_tier": "tactical",
    "filesystem_mode": "scoped",
    "network_mode": "allowlist",
    "shell_enabled": False,
    "skill_auto_install": False,
    "max_active_subagents": 5,
    "kill_switch_enabled": True,
    "kill_switch_active": False,   # True when the kill switch has been triggered
    "comms_read_email": True,
    "comms_send_email": True,
    "comms_read_calendar": True,
    "comms_create_events": True,
    "comms_list_cron": True,
    "comms_manage_cron": True,
}

# Constraint values that each tier enforces when selected
TIER_CONSTRAINTS: dict[str, dict] = {
    "shrine": {
        "filesystem_mode": "disabled",
        "network_mode": "disabled",
        "shell_enabled": False,
        "skill_auto_install": False,
        "max_active_subagents": 0,
        "comms_read_email": False,
        "comms_send_email": False,
        "comms_read_calendar": False,
        "comms_create_events": False,
        "comms_list_cron": False,
        "comms_manage_cron": False,
    },
    "guarded": {
        "filesystem_mode": "allowlist",
        "network_mode": "allowlist",
        "shell_enabled": False,
        "skill_auto_install": False,
        "max_active_subagents": 2,
        "comms_read_email": True,
        "comms_send_email": False,
        "comms_read_calendar": True,
        "comms_create_events": False,
        "comms_list_cron": True,
        "comms_manage_cron": False,
    },
    "tactical": {
        "filesystem_mode": "scoped",
        "network_mode": "allowlist",
        "shell_enabled": False,
        "skill_auto_install": False,
        "max_active_subagents": 5,
        "comms_read_email": True,
        "comms_send_email": True,
        "comms_read_calendar": True,
        "comms_create_events": True,
        "comms_list_cron": True,
        "comms_manage_cron": True,
    },
    "campaign": {
        "filesystem_mode": "full",
        "network_mode": "full",
        "shell_enabled": True,
        "skill_auto_install": True,
        "max_active_subagents": 15,
        "comms_read_email": True,
        "comms_send_email": True,
        "comms_read_calendar": True,
        "comms_create_events": True,
        "comms_list_cron": True,
        "comms_manage_cron": True,
    },
    "ronin": {
        "filesystem_mode": "full",
        "network_mode": "full",
        "shell_enabled": True,
        "skill_auto_install": True,
        "max_active_subagents": 50,
        "comms_read_email": True,
        "comms_send_email": True,
        "comms_read_calendar": True,
        "comms_create_events": True,
        "comms_list_cron": True,
        "comms_manage_cron": True,
    },
}


async def _get_agent_posture() -> dict:
    """Read security posture from primary Shogun agent's bushido_settings."""
    from shogun.db.engine import async_session_factory
    from shogun.db.models.agent import Agent
    from sqlalchemy import select

    async with async_session_factory() as db:
        result = await db.execute(
            select(Agent).where(
                Agent.agent_type == "shogun",
                Agent.is_primary == True,
                Agent.is_deleted == False,
            ).limit(1)
        )
        agent = result.scalar_one_or_none()
        if not agent:
            return dict(_DEFAULT_POSTURE)
        bushido = agent.bushido_settings or {}
        stored = bushido.get(_POSTURE_KEY, {})
        return {**_DEFAULT_POSTURE, **stored}


async def _save_agent_posture(posture: dict) -> None:
    """Persist security posture into primary Shogun agent's bushido_settings."""
    from shogun.db.engine import async_session_factory
    from shogun.db.models.agent import Agent
    from sqlalchemy import select
    import json

    async with async_session_factory() as db:
        result = await db.execute(
            select(Agent).where(
                Agent.agent_type == "shogun",
                Agent.is_primary == True,
                Agent.is_deleted == False,
            ).limit(1)
        )
        agent = result.scalar_one_or_none()
        if not agent:
            return
        bushido = dict(agent.bushido_settings or {})
        bushido[_POSTURE_KEY] = posture
        agent.bushido_settings = bushido
        await db.commit()


# ── Posture endpoints ────────────────────────────────────────────────

@router.get("/posture", response_model=ApiResponse)
async def get_security_posture():
    posture = await _get_agent_posture()
    return ApiResponse(data=SecurityPostureResponse(**posture).model_dump())


@router.patch("/posture", response_model=ApiResponse)
async def update_security_posture(body: dict):
    """Update security posture fields. Persisted across restarts."""
    current = await _get_agent_posture()
    old_tier = current.get("active_tier", "tactical")
    allowed_fields = set(_DEFAULT_POSTURE.keys())
    updates = {k: v for k, v in body.items() if k in allowed_fields}
    current.update(updates)
    # ── Apply tier-specific constraints when active_tier changes ──
    new_tier = current.get("active_tier", "tactical")
    if new_tier != old_tier and new_tier in TIER_CONSTRAINTS:
        current.update(TIER_CONSTRAINTS[new_tier])
    await _save_agent_posture(current)
    # ── EVENT: Auth — Posture Changed ──────────────────
    try:
        from shogun.services.event_logger import EventLogger
        await EventLogger.emit_auth_event(
            "auth.posture_changed",
            f"Security posture changed: {old_tier.upper()} → {new_tier.upper()}",
            severity="warn" if new_tier in ("campaign", "ronin") else "info",
            detail={"old_tier": old_tier, "new_tier": new_tier, "updates": updates},
        )
    except Exception:
        pass
    return ApiResponse(data=SecurityPostureResponse(**current).model_dump())


# ── Policy endpoints ─────────────────────────────────────────────────

@router.get("/policies", response_model=ApiResponse)
async def list_policies(svc: SecurityService = Depends(get_security_service)):
    records, total = await svc.get_all()
    return ApiResponse(
        data=[SecurityPolicyResponse.model_validate(r) for r in records],
        meta={"total": total},
    )


@router.get("/policies/{policy_id}", response_model=ApiResponse)
async def get_policy(policy_id: uuid.UUID, svc: SecurityService = Depends(get_security_service)):
    record = await svc.get_by_id(policy_id)
    if not record:
        raise HTTPException(status_code=404, detail="Policy not found")
    return ApiResponse(data=SecurityPolicyResponse.model_validate(record))


@router.post("/policies", response_model=ApiResponse, status_code=201)
async def create_policy(
    body: SecurityPolicyCreate,
    svc: SecurityService = Depends(get_security_service),
):
    data = body.model_dump()
    data["permissions"] = data["permissions"] if isinstance(data["permissions"], dict) else data["permissions"].model_dump()
    record = await svc.create(**data)
    return ApiResponse(data=SecurityPolicyResponse.model_validate(record))


@router.patch("/policies/{policy_id}", response_model=ApiResponse)
async def update_policy(
    policy_id: uuid.UUID,
    body: SecurityPolicyUpdate,
    svc: SecurityService = Depends(get_security_service),
):
    update_data = body.model_dump(exclude_unset=True)
    if "permissions" in update_data and update_data["permissions"] is not None:
        update_data["permissions"] = update_data["permissions"].model_dump() if hasattr(update_data["permissions"], "model_dump") else update_data["permissions"]
    record = await svc.update(policy_id, **update_data)
    if not record:
        raise HTTPException(status_code=404, detail="Policy not found")
    return ApiResponse(data=SecurityPolicyResponse.model_validate(record))


@router.delete("/policies/{policy_id}", response_model=ApiResponse)
async def delete_policy(
    policy_id: uuid.UUID,
    svc: SecurityService = Depends(get_security_service),
):
    record = await svc.get_by_id(policy_id)
    if not record:
        raise HTTPException(status_code=404, detail="Policy not found")
    if record.is_builtin:
        raise HTTPException(status_code=403, detail="Cannot delete built-in policies")

    # ── Unassign from any agents that reference this policy ──────
    from shogun.db.models.agent import Agent
    from sqlalchemy import select
    result = await svc.session.execute(
        select(Agent).where(Agent.security_policy_id == str(policy_id))
    )
    agents = result.scalars().all()
    for agent in agents:
        agent.security_policy_id = None
        # Clear custom_permissions from bushido_settings if present
        if agent.bushido_settings and isinstance(agent.bushido_settings, dict):
            bs = dict(agent.bushido_settings)
            bs.pop("custom_permissions", None)
            agent.bushido_settings = bs

    await svc.delete(policy_id)
    return ApiResponse(data={"deleted": str(policy_id), "unassigned_agents": len(agents)})


@router.post("/simulate", response_model=ApiResponse)
async def simulate_permissions(body: PermissionSimulateRequest):
    return ApiResponse(
        data=PermissionSimulateResponse(allowed=True, warnings=["Simulation not yet implemented"], denials=[]).model_dump()
    )


@router.post("/kill-switch", response_model=ApiResponse)
async def activate_kill_switch():
    """Activate global kill switch — sets posture to shrine and disables shell. Persisted."""
    posture = await _get_agent_posture()
    posture["active_tier"] = "shrine"
    posture.update(TIER_CONSTRAINTS["shrine"])
    posture["kill_switch_active"] = True
    await _save_agent_posture(posture)
    try:
        from shogun.services.event_logger import EventLogger
        await EventLogger.emit_auth_event(
            "auth.kill_switch_activated",
            "HARAKIRI: Kill switch activated — all operations suspended",
            severity="critical",
            detail={"posture": "shrine", "kill_switch_active": True},
        )
        await EventLogger.emit_incident_event(
            "incident.kill_switch",
            "HARAKIRI: Emergency kill switch activated by operator",
            severity="critical", risk_score="critical",
            detail={"posture": "shrine", "trigger": "manual"},
        )
        await EventLogger.emit_oversight_event(
            "oversight.emergency_shutdown",
            "Operator initiated emergency shutdown of all AI operations",
            detail={"action": "kill_switch_activated", "new_posture": "shrine"},
        )
    except Exception:
        pass
    return ApiResponse(data={**posture, "message": "All agent activity suspended. Posture set to SHRINE."})


@router.delete("/kill-switch", response_model=ApiResponse)
async def reset_kill_switch():
    """Deactivate kill switch and restore tactical posture."""
    posture = await _get_agent_posture()
    posture["active_tier"] = "tactical"
    posture.update(TIER_CONSTRAINTS["tactical"])
    posture["kill_switch_active"] = False
    await _save_agent_posture(posture)
    try:
        from shogun.services.event_logger import EventLogger
        await EventLogger.emit_auth_event(
            "auth.kill_switch_reset",
            "Kill switch deactivated — posture restored to TACTICAL",
            severity="warn",
            detail={"posture": "tactical", "kill_switch_active": False},
        )
    except Exception:
        pass
    return ApiResponse(data={**posture, "message": "Kill switch reset. Posture restored to TACTICAL."})
