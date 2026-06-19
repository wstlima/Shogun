"""SQLAlchemy models for Nexus External Gateway."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from shogun.db.base import AuditMixin, Base, GUID, JSONType, SoftDeleteMixin, UUIDMixin


class ExternalAgentModel(Base, UUIDMixin, AuditMixin, SoftDeleteMixin):
    """Represents a registered external enterprise agent (e.g. Microsoft 365, Salesforce)."""
    
    __tablename__ = "nexus_external_agents"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    platform: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "microsoft_365", "salesforce", "google"
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)  # API token for authenticating calls
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class AgentCapabilityModel(Base, AuditMixin):
    """Represents a capability Shogun can execute on behalf of external systems."""
    
    __tablename__ = "nexus_agent_capabilities"

    name: Mapped[str] = mapped_column(String(100), primary_key=True)  # e.g. "document.summarize", "spreadsheet.analyze"
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "document", "spreadsheet", "desktop"
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class NexusTaskModel(Base, UUIDMixin, AuditMixin):
    """Normalized object representing a task requested by an external agent."""
    
    __tablename__ = "nexus_tasks"

    source_agent_id: Mapped[str] = mapped_column(String(255), nullable=False)
    source_platform: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "microsoft_365", "salesforce"
    source_protocol: Mapped[str] = mapped_column(String(50), nullable=False)   # e.g., "a2a", "webhook", "mcp"
    requested_action: Mapped[str] = mapped_column(String(100), nullable=False) # e.g. "spreadsheet.analyze"
    task_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    required_capabilities: Mapped[list] = mapped_column(JSONType(), nullable=False, default=list)
    input_context: Mapped[dict] = mapped_column(JSONType(), nullable=False, default=dict)
    data_sensitivity: Mapped[str] = mapped_column(String(50), nullable=False, default="internal") # low, internal, restricted, sensitive
    allowed_tools: Mapped[list] = mapped_column(JSONType(), nullable=False, default=list)
    approval_required: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    callback_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")  # pending, approved, executing, completed, failed, blocked
    result: Mapped[dict] = mapped_column(JSONType(), nullable=False, default=dict)
    audit_metadata: Mapped[dict] = mapped_column(JSONType(), nullable=False, default=dict)
