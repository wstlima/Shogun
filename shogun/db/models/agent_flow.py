"""Agent Flow ORM models — workflow orchestration for Samurai agents.

Three models:
  - AgentFlow:     a complete visual workflow definition
  - AgentFlowNode: a card/node on the canvas (Samurai, Approval, Logic, etc.)
  - AgentFlowEdge: an arrow/connection between two nodes
"""

from __future__ import annotations

import uuid
from typing import List

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shogun.db.base import AuditMixin, Base, GUID, JSONType, SoftDeleteMixin, UUIDMixin


class AgentFlow(Base, UUIDMixin, AuditMixin, SoftDeleteMixin):
    """A complete Agent Flow workflow definition."""

    __tablename__ = "agent_flows"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    trigger_type: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")
    schedule_config: Mapped[dict] = mapped_column(JSONType(), nullable=False, default=dict)
    viewport: Mapped[dict] = mapped_column(
        JSONType(), nullable=False,
        default=lambda: {"x": 0, "y": 0, "zoom": 1},
    )

    # Relationships
    nodes: Mapped[List["AgentFlowNode"]] = relationship(
        "AgentFlowNode",
        back_populates="flow",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    edges: Mapped[List["AgentFlowEdge"]] = relationship(
        "AgentFlowEdge",
        back_populates="flow",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class AgentFlowNode(Base, UUIDMixin, AuditMixin):
    """A single card/node on the Agent Flow canvas."""

    __tablename__ = "agent_flow_nodes"

    flow_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("agent_flows.id", ondelete="CASCADE"), nullable=False,
    )
    node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False, default="Untitled")
    position_x: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    position_y: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    config: Mapped[dict] = mapped_column(JSONType(), nullable=False, default=dict)

    # Relationships
    flow: Mapped["AgentFlow"] = relationship("AgentFlow", back_populates="nodes")


class AgentFlowEdge(Base, UUIDMixin, AuditMixin):
    """A connection/arrow between two nodes on the Agent Flow canvas."""

    __tablename__ = "agent_flow_edges"

    flow_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("agent_flows.id", ondelete="CASCADE"), nullable=False,
    )
    source_node_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("agent_flow_nodes.id", ondelete="CASCADE"), nullable=False,
    )
    target_node_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("agent_flow_nodes.id", ondelete="CASCADE"), nullable=False,
    )
    source_handle: Mapped[str | None] = mapped_column(String(100), nullable=True)
    target_handle: Mapped[str | None] = mapped_column(String(100), nullable=True)
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    edge_type: Mapped[str] = mapped_column(String(50), nullable=False, default="default")
    config: Mapped[dict] = mapped_column(JSONType(), nullable=False, default=dict)

    # Relationships
    flow: Mapped["AgentFlow"] = relationship("AgentFlow", back_populates="edges")
