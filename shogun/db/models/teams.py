"""Persistent state for the Microsoft Teams Katana adapter."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from shogun.db.base import AuditMixin, Base, JSONType, UUIDMixin


class TeamsConfig(Base, UUIDMixin, AuditMixin):
    __tablename__ = "katana_teams_config"

    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deployment_mode: Mapped[str] = mapped_column(String(30), nullable=False, default="dev")
    tenant_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="single")
    allowed_tenant_ids: Mapped[list] = mapped_column(JSONType(), nullable=False, default=list)
    bot_app_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    bot_name: Mapped[str] = mapped_column(String(100), nullable=False, default="Shogun")
    client_secret_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    public_messaging_endpoint: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    valid_domains: Mapped[list] = mapped_column(JSONType(), nullable=False, default=list)
    graph_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    proactive_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sso_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allowed_commands: Mapped[list] = mapped_column(JSONType(), nullable=False, default=list)
    allowed_channels: Mapped[list] = mapped_column(JSONType(), nullable=False, default=list)
    destructive_commands_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    dual_approval_fleet: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    approval_ttl_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=900)
    last_inbound_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_outbound_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(String(1000), nullable=True)


class TeamsUserMap(Base, UUIDMixin, AuditMixin):
    __tablename__ = "katana_teams_user_map"
    __table_args__ = (UniqueConstraint("tenant_id", "teams_user_id", name="uq_teams_user_tenant"),)

    tenant_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    teams_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    aad_object_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    user_principal_name: Mapped[str | None] = mapped_column(String(320), nullable=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False, default="Unknown Teams user")
    shogun_user_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    shogun_role: Mapped[str] = mapped_column(String(30), nullable=False, default="viewer")
    allowed_command_groups: Mapped[list] = mapped_column(JSONType(), nullable=False, default=list)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TeamsConversation(Base, UUIDMixin, AuditMixin):
    __tablename__ = "katana_teams_conversations"
    __table_args__ = (UniqueConstraint("tenant_id", "conversation_id", name="uq_teams_conversation"),)

    tenant_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    conversation_id: Mapped[str] = mapped_column(String(255), nullable=False)
    conversation_type: Mapped[str] = mapped_column(String(30), nullable=False)
    team_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    channel_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    chat_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    conversation_reference: Mapped[dict] = mapped_column(JSONType(), nullable=False, default=dict)
    service_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    bot_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_activity_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    installed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    proactive_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class TeamsCommandLog(Base, UUIDMixin):
    __tablename__ = "katana_teams_command_log"

    correlation_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    aad_object_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    conversation_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_text: Mapped[str] = mapped_column(Text, nullable=False)
    command_name: Mapped[str] = mapped_column(String(50), nullable=False)
    arguments: Mapped[dict] = mapped_column(JSONType(), nullable=False, default=dict)
    risk_level: Mapped[str] = mapped_column(String(2), nullable=False)
    authorization_result: Mapped[str] = mapped_column(String(50), nullable=False)
    gensui_command_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    response_type: Mapped[str] = mapped_column(String(30), nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class TeamsApprovalRequest(Base, UUIDMixin, AuditMixin):
    __tablename__ = "katana_teams_approval_requests"

    approval_request_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    teams_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    conversation_id: Mapped[str] = mapped_column(String(255), nullable=False)
    requested_by_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    required_role: Mapped[str] = mapped_column(String(30), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(2), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    approved_by_user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rejected_by_user_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    action_payload: Mapped[dict] = mapped_column(JSONType(), nullable=False, default=dict)
    confirmation_code_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)


class TeamsNotificationRoute(Base, UUIDMixin, AuditMixin):
    __tablename__ = "katana_teams_notification_routes"

    route_name: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(30), nullable=False, default="info")
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    target_type: Mapped[str] = mapped_column(String(30), nullable=False)
    target_conversation_id: Mapped[str] = mapped_column(String(255), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    quiet_hours: Mapped[dict] = mapped_column(JSONType(), nullable=False, default=dict)
