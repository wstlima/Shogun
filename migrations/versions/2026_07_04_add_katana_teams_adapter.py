"""add Katana Microsoft Teams adapter

Revision ID: 20260704teams
Revises: cb3060c69bea
Create Date: 2026-07-04
"""

from alembic import op
import sqlalchemy as sa

revision = "20260704teams"
down_revision = "cb3060c69bea"
branch_labels = None
depends_on = None


def _audit_columns():
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.String(255), nullable=True),
        sa.Column("updated_by", sa.String(255), nullable=True),
    ]


def _id():
    return sa.Column("id", sa.String(36), primary_key=True)


def upgrade() -> None:
    op.create_table(
        "katana_teams_config", _id(),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("deployment_mode", sa.String(30), nullable=False, server_default="dev"),
        sa.Column("tenant_mode", sa.String(20), nullable=False, server_default="single"),
        sa.Column("allowed_tenant_ids", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("bot_app_id", sa.String(100), nullable=True),
        sa.Column("bot_name", sa.String(100), nullable=False, server_default="Shogun"),
        sa.Column("client_secret_ref", sa.String(255), nullable=True),
        sa.Column("public_messaging_endpoint", sa.String(1000), nullable=True),
        sa.Column("valid_domains", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("graph_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("proactive_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("sso_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("allowed_commands", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("allowed_channels", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("destructive_commands_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("dual_approval_fleet", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("approval_ttl_seconds", sa.Integer(), nullable=False, server_default="900"),
        sa.Column("last_inbound_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_outbound_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.String(1000), nullable=True),
        *_audit_columns(),
    )
    op.create_table(
        "katana_teams_user_map", _id(),
        sa.Column("tenant_id", sa.String(100), nullable=False, index=True),
        sa.Column("teams_user_id", sa.String(255), nullable=False),
        sa.Column("aad_object_id", sa.String(100), nullable=True, index=True),
        sa.Column("user_principal_name", sa.String(320), nullable=True),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("shogun_user_id", sa.String(100), nullable=True),
        sa.Column("shogun_role", sa.String(30), nullable=False, server_default="viewer"),
        sa.Column("allowed_command_groups", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        *_audit_columns(),
        sa.UniqueConstraint("tenant_id", "teams_user_id", name="uq_teams_user_tenant"),
    )
    op.create_table(
        "katana_teams_conversations", _id(),
        sa.Column("tenant_id", sa.String(100), nullable=False, index=True),
        sa.Column("conversation_id", sa.String(255), nullable=False),
        sa.Column("conversation_type", sa.String(30), nullable=False),
        sa.Column("team_id", sa.String(255), nullable=True),
        sa.Column("channel_id", sa.String(255), nullable=True),
        sa.Column("chat_id", sa.String(255), nullable=True),
        sa.Column("conversation_reference", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("service_url", sa.String(1000), nullable=True),
        sa.Column("bot_id", sa.String(255), nullable=True),
        sa.Column("last_activity_id", sa.String(255), nullable=True),
        sa.Column("installed", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("proactive_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_audit_columns(),
        sa.UniqueConstraint("tenant_id", "conversation_id", name="uq_teams_conversation"),
    )
    op.create_table(
        "katana_teams_command_log", _id(),
        sa.Column("correlation_id", sa.String(36), nullable=False, unique=True, index=True),
        sa.Column("tenant_id", sa.String(100), nullable=False, index=True),
        sa.Column("user_id", sa.String(255), nullable=False),
        sa.Column("aad_object_id", sa.String(100), nullable=True),
        sa.Column("conversation_id", sa.String(255), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("normalized_text", sa.Text(), nullable=False),
        sa.Column("command_name", sa.String(50), nullable=False),
        sa.Column("arguments", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("risk_level", sa.String(2), nullable=False),
        sa.Column("authorization_result", sa.String(50), nullable=False),
        sa.Column("gensui_command_id", sa.String(100), nullable=True),
        sa.Column("response_type", sa.String(30), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("error_code", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "katana_teams_approval_requests", _id(),
        sa.Column("approval_request_id", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("teams_message_id", sa.String(255), nullable=True),
        sa.Column("conversation_id", sa.String(255), nullable=False),
        sa.Column("requested_by_user_id", sa.String(255), nullable=False),
        sa.Column("required_role", sa.String(30), nullable=False),
        sa.Column("risk_level", sa.String(2), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_by_user_id", sa.String(255), nullable=True),
        sa.Column("rejected_by_user_id", sa.String(255), nullable=True),
        sa.Column("action_payload", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("confirmation_code_hash", sa.String(128), nullable=True),
        *_audit_columns(),
    )
    op.create_table(
        "katana_teams_notification_routes", _id(),
        sa.Column("route_name", sa.String(255), nullable=False),
        sa.Column("severity", sa.String(30), nullable=False, server_default="info"),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("target_type", sa.String(30), nullable=False),
        sa.Column("target_conversation_id", sa.String(255), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("quiet_hours", sa.Text(), nullable=False, server_default="{}"),
        *_audit_columns(),
    )


def downgrade() -> None:
    for table in [
        "katana_teams_notification_routes", "katana_teams_approval_requests",
        "katana_teams_command_log", "katana_teams_conversations",
        "katana_teams_user_map", "katana_teams_config",
    ]:
        op.drop_table(table)
