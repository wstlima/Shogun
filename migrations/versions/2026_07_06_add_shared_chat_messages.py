"""add shared Comms and Telegram messages

Revision ID: 20260706chat
Revises: 20260704teams
Create Date: 2026-07-06
"""

from alembic import op
import sqlalchemy as sa

revision = "20260706chat"
down_revision = "20260704teams"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("channel", sa.String(30), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("external_chat_id", sa.String(255), nullable=True),
        sa.Column("client_message_id", sa.String(100), nullable=True),
        sa.Column("message_data", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("client_message_id", name="uq_chat_messages_client_message_id"),
    )
    op.create_index("ix_chat_messages_channel", "chat_messages", ["channel"])
    op.create_index("ix_chat_messages_client_message_id", "chat_messages", ["client_message_id"])
    op.create_index("ix_chat_messages_created_at", "chat_messages", ["created_at"])


def downgrade() -> None:
    op.drop_table("chat_messages")
