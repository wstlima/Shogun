"""Channel-neutral command contracts and Teams adapter schemas."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


class ChannelUser(BaseModel):
    teams_user_id: str
    aad_object_id: str | None = None
    display_name: str = "Unknown Teams user"
    user_principal_name: str | None = None


class CommandEnvelope(BaseModel):
    source: Literal["microsoft_teams", "telegram"]
    adapter_version: str = "1.0.0"
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    tenant_id: str
    team_id: str | None = None
    channel_id: str | None = None
    chat_id: str | None = None
    conversation_reference_id: str | None = None
    conversation_type: Literal["personal", "channel", "groupchat"]
    message_id: str
    reply_to_id: str | None = None
    user: ChannelUser
    raw_text: str
    normalized_text: str = ""
    command_name: str = ""
    arguments: dict[str, Any] = Field(default_factory=dict)
    attachments: list[dict[str, Any]] = Field(default_factory=list)
    risk_level: Literal["L0", "L1", "L2", "L3", "L4"] = "L0"
    requires_approval: bool = False
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    conversation_reference: dict[str, Any] | None = None
    service_url: str | None = None

    @field_validator("raw_text")
    @classmethod
    def limit_message(cls, value: str) -> str:
        value = value.strip()
        if not value or len(value) > 8000:
            raise ValueError("Message must contain between 1 and 8000 characters")
        return value


class ResponseTarget(BaseModel):
    source: str = "microsoft_teams"
    conversation_reference_id: str | None = None
    reply_to_id: str | None = None


class ResponseEnvelope(BaseModel):
    correlation_id: str
    target: ResponseTarget
    response_type: Literal["text", "adaptive_card", "approval_card", "error", "status_card"]
    title: str | None = None
    text: str
    card_payload: dict[str, Any] = Field(default_factory=dict)
    severity: Literal["info", "success", "warning", "critical"] = "info"
    actions: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TeamsConfigUpdate(BaseModel):
    enabled: bool = False
    deployment_mode: Literal["dev", "bridge", "direct"] = "dev"
    tenant_mode: Literal["single", "multi"] = "single"
    allowed_tenant_ids: list[str] = Field(default_factory=list)
    bot_app_id: str | None = None
    bot_name: str = "Shogun"
    client_secret_ref: str | None = None
    public_messaging_endpoint: str | None = None
    valid_domains: list[str] = Field(default_factory=list)
    graph_enabled: bool = False
    proactive_enabled: bool = False
    sso_enabled: bool = False
    allowed_commands: list[str] = Field(default_factory=list)
    allowed_channels: list[str] = Field(default_factory=list)
    destructive_commands_enabled: bool = False
    dual_approval_fleet: bool = True
    approval_ttl_seconds: int = Field(default=900, ge=60, le=86400)


class TeamsRoleUpdate(BaseModel):
    shogun_role: Literal["viewer", "operator", "senior_operator", "admin", "security_admin"]
    allowed_command_groups: list[str] = Field(default_factory=list)
