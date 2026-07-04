"""Security and normalization tests for the Katana Teams adapter."""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from shogun.db.base import Base
from shogun.db.models.teams import TeamsConfig, TeamsUserMap
from shogun.schemas.teams import ChannelUser, CommandEnvelope
from shogun.services.command_channel import SlidingWindowRateLimiter, authorize, parse_command, strip_teams_mention
from shogun.services.teams_service import DEFAULT_COMMANDS, TeamsService


def test_teams_mention_stripping():
    assert strip_teams_mention("<at>Shogun</at> status") == "status"
    assert strip_teams_mention("@Shogun: show active agents") == "show active agents"


@pytest.mark.parametrize(
    ("text", "name", "risk"),
    [
        ("status", "status", "L0"),
        ("ask samurai-02 summarize today", "ask", "L1"),
        ("run workflow weekly-report with period=this_week", "run", "L2"),
        ("pause agent samurai-02", "pause", "L4"),
        ("harakiri fleet", "harakiri", "L4"),
        ("approve REQ-12345", "approve", "L3"),
    ],
)
def test_command_parsing_and_risk(text: str, name: str, risk: str):
    parsed = parse_command(text)
    assert parsed.name == name
    assert parsed.risk_level == risk


def test_role_authorization_and_harakiri_gate():
    assert authorize("status", "viewer") == (True, "allowed")
    assert authorize("pause", "viewer")[0] is False
    assert authorize("harakiri", "admin", destructive_commands_enabled=False) == (
        False,
        "destructive_commands_disabled",
    )
    assert authorize("harakiri", "admin", destructive_commands_enabled=True) == (True, "allowed")


def test_rate_limit_is_enforced():
    limiter = SlidingWindowRateLimiter()
    assert limiter.allow("user:1", 2)
    assert limiter.allow("user:1", 2)
    assert not limiter.allow("user:1", 2)


def envelope(tenant_id: str, text: str, user_id: str = "teams-user-1") -> CommandEnvelope:
    return CommandEnvelope(
        source="microsoft_teams",
        tenant_id=tenant_id,
        conversation_type="personal",
        message_id=str(uuid4()),
        chat_id="chat-1",
        conversation_reference_id="chat-1",
        user=ChannelUser(teams_user_id=user_id, aad_object_id="aad-1", display_name="Test Admin"),
        raw_text=text,
    )


@pytest.mark.asyncio
async def test_unknown_tenant_rejected_and_audited():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        db.add(TeamsConfig(enabled=True, allowed_tenant_ids=["allowed"], allowed_commands=DEFAULT_COMMANDS))
        await db.flush()
        response = await TeamsService(db).dispatch(envelope("unknown", "status"))
        assert response.response_type == "error"
        assert "not authorized" in response.text
    await engine.dispose()


@pytest.mark.asyncio
async def test_harakiri_approval_is_single_use():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        db.add(
            TeamsConfig(
                enabled=True,
                allowed_tenant_ids=["tenant-1"],
                allowed_commands=DEFAULT_COMMANDS,
                destructive_commands_enabled=True,
                dual_approval_fleet=False,
            )
        )
        db.add(
            TeamsUserMap(
                tenant_id="tenant-1",
                teams_user_id="teams-user-1",
                display_name="Test Admin",
                shogun_role="admin",
            )
        )
        await db.flush()
        service = TeamsService(db)
        proposal = await service.dispatch(envelope("tenant-1", "harakiri fleet"))
        request_id = proposal.card_payload["actions"][0]["data"]["request_id"]
        approved = await service.dispatch(envelope("tenant-1", f"approve {request_id}"))
        reused = await service.dispatch(envelope("tenant-1", f"approve {request_id}"))
        assert approved.severity == "success"
        assert reused.response_type == "error"
        assert "already been used" in reused.text
    await engine.dispose()
