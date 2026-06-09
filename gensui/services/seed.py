"""Seed service — creates built-in postures and initial admin on first startup."""

from __future__ import annotations

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from gensui.config import gensui_settings
from gensui.db.models.admin_user import AdminUser
from gensui.db.models.security_posture import SecurityPosture
from gensui.db.models.global_posture import GlobalPostureState
from gensui.services.auth_service import AuthService

log = logging.getLogger("gensui.seed")

# ── Built-in Posture Definitions ─────────────────────────────

BUILTIN_POSTURES = [
    {
        "name": "OPEN", "level": 0,
        "description": "Development or trusted local experimentation. All capabilities enabled.",
        "allow_external_models": True, "allow_local_models": True, "allow_tool_execution": True,
        "allow_mado": True, "allow_memory_write": True, "allow_memory_read": True,
        "allow_agent_flow": True, "allow_nexus": True, "allow_samurai_delegation": True,
        "allow_scheduled_triggers": True, "allow_autonomous_loops": True,
        "allow_external_web": True, "allow_file_write": True, "allow_external_api": True,
    },
    {
        "name": "STANDARD", "level": 10,
        "description": "Default operational mode. Approved providers and tools only.",
        "allow_external_models": True, "allow_local_models": True, "allow_tool_execution": True,
        "allow_mado": True, "allow_memory_write": True, "allow_memory_read": True,
        "allow_agent_flow": True, "allow_nexus": True, "allow_samurai_delegation": True,
        "allow_scheduled_triggers": True, "allow_autonomous_loops": True,
        "allow_external_web": True, "allow_file_write": True, "allow_external_api": True,
    },
    {
        "name": "RESTRICTED", "level": 30,
        "description": "Sensitive workflows. Limited external access, approved tools only.",
        "allow_external_models": True, "allow_local_models": True, "allow_tool_execution": True,
        "allow_mado": False, "allow_memory_write": True, "allow_memory_read": True,
        "allow_agent_flow": True, "allow_nexus": True, "allow_samurai_delegation": True,
        "allow_scheduled_triggers": False, "allow_autonomous_loops": False,
        "allow_external_web": False, "allow_file_write": False, "allow_external_api": False,
    },
    {
        "name": "LOCKDOWN", "level": 90,
        "description": "Emergency containment mode. Only heartbeat and policy sync allowed.",
        "allow_external_models": False, "allow_local_models": False, "allow_tool_execution": False,
        "allow_mado": False, "allow_memory_write": False, "allow_memory_read": True,
        "allow_agent_flow": False, "allow_nexus": False, "allow_samurai_delegation": False,
        "allow_scheduled_triggers": False, "allow_autonomous_loops": False,
        "allow_external_web": False, "allow_file_write": False, "allow_external_api": False,
    },
    {
        "name": "OBSERVE_ONLY", "level": 5,
        "description": "Normal local behavior. Gensui monitors only, no enforcement unless violations escalate.",
        "allow_external_models": True, "allow_local_models": True, "allow_tool_execution": True,
        "allow_mado": True, "allow_memory_write": True, "allow_memory_read": True,
        "allow_agent_flow": True, "allow_nexus": True, "allow_samurai_delegation": True,
        "allow_scheduled_triggers": True, "allow_autonomous_loops": True,
        "allow_external_web": True, "allow_file_write": True, "allow_external_api": True,
    },
    {
        "name": "LOCAL_ONLY", "level": 40,
        "description": "No external AI providers allowed. Local models and tools only.",
        "allow_external_models": False, "allow_local_models": True, "allow_tool_execution": True,
        "allow_mado": False, "allow_memory_write": True, "allow_memory_read": True,
        "allow_agent_flow": True, "allow_nexus": True, "allow_samurai_delegation": True,
        "allow_scheduled_triggers": True, "allow_autonomous_loops": True,
        "allow_external_web": False, "allow_file_write": True, "allow_external_api": False,
    },
    {
        "name": "NO_EXTERNAL_WEB", "level": 35,
        "description": "Blocks external browsing and web extraction.",
        "allow_external_models": True, "allow_local_models": True, "allow_tool_execution": True,
        "allow_mado": False, "allow_memory_write": True, "allow_memory_read": True,
        "allow_agent_flow": True, "allow_nexus": True, "allow_samurai_delegation": True,
        "allow_scheduled_triggers": True, "allow_autonomous_loops": True,
        "allow_external_web": False, "allow_file_write": True, "allow_external_api": True,
    },
    {
        "name": "NO_TOOL_EXECUTION", "level": 50,
        "description": "Blocks all tool use. Plain model responses only.",
        "allow_external_models": True, "allow_local_models": True, "allow_tool_execution": False,
        "allow_mado": False, "allow_memory_write": False, "allow_memory_read": True,
        "allow_agent_flow": False, "allow_nexus": True, "allow_samurai_delegation": False,
        "allow_scheduled_triggers": False, "allow_autonomous_loops": False,
        "allow_external_web": False, "allow_file_write": False, "allow_external_api": False,
    },
    {
        "name": "NO_MEMORY_WRITE", "level": 25,
        "description": "Blocks memory inscription. Read-only memory access.",
        "allow_external_models": True, "allow_local_models": True, "allow_tool_execution": True,
        "allow_mado": True, "allow_memory_write": False, "allow_memory_read": True,
        "allow_agent_flow": True, "allow_nexus": True, "allow_samurai_delegation": True,
        "allow_scheduled_triggers": True, "allow_autonomous_loops": True,
        "allow_external_web": True, "allow_file_write": True, "allow_external_api": True,
    },
    {
        "name": "NO_MADO", "level": 20,
        "description": "Blocks browser automation entirely.",
        "allow_external_models": True, "allow_local_models": True, "allow_tool_execution": True,
        "allow_mado": False, "allow_memory_write": True, "allow_memory_read": True,
        "allow_agent_flow": True, "allow_nexus": True, "allow_samurai_delegation": True,
        "allow_scheduled_triggers": True, "allow_autonomous_loops": True,
        "allow_external_web": True, "allow_file_write": True, "allow_external_api": True,
    },
    {
        "name": "NO_AUTONOMY", "level": 15,
        "description": "Only direct human-triggered actions. No scheduled or autonomous operations.",
        "allow_external_models": True, "allow_local_models": True, "allow_tool_execution": True,
        "allow_mado": True, "allow_memory_write": True, "allow_memory_read": True,
        "allow_agent_flow": True, "allow_nexus": True, "allow_samurai_delegation": True,
        "allow_scheduled_triggers": False, "allow_autonomous_loops": False,
        "allow_external_web": True, "allow_file_write": True, "allow_external_api": True,
    },
]


async def seed_database(session: AsyncSession) -> None:
    """Seed built-in postures and initial admin user on first startup."""

    # ── Seed Built-in Postures ───────────────────────────────
    for posture_def in BUILTIN_POSTURES:
        existing = await session.execute(
            select(SecurityPosture).where(SecurityPosture.name == posture_def["name"])
        )
        if existing.scalars().first() is None:
            posture = SecurityPosture(
                is_builtin=True,
                created_by="system",
                **posture_def,
            )
            session.add(posture)
            log.info("Seeded posture: %s", posture_def["name"])

    # ── Seed Global Posture State (inactive by default) ──────
    existing_global = await session.execute(select(GlobalPostureState))
    if existing_global.scalars().first() is None:
        state = GlobalPostureState(is_active=False)
        session.add(state)
        log.info("Seeded global posture state (inactive)")

    # ── Seed Initial Admin User ──────────────────────────────
    auth = AuthService(session)
    existing_admin = await auth.get_by_email(gensui_settings.gensui_admin_email)
    if existing_admin is None:
        await auth.create_admin(
            email=gensui_settings.gensui_admin_email,
            password=gensui_settings.gensui_admin_password,
            display_name="Gensui Admin",
            role="owner",
        )
        log.info("Seeded initial admin: %s", gensui_settings.gensui_admin_email)

    await session.commit()
    log.info("Database seeding complete")
