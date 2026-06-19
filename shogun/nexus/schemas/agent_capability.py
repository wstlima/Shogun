"""Pydantic schema for AgentCapability."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AgentCapabilityBase(BaseModel):
    name: str = Field(..., description="Action capability string, e.g. document.summarize")
    category: str = Field(..., description="Capability category, e.g. document, crm, desktop")
    description: str | None = Field(None, description="Detailed description of what the capability does")
    is_custom: bool = Field(False, description="True if custom configured capability")


class AgentCapabilityCreate(AgentCapabilityBase):
    pass


class AgentCapabilityResponse(AgentCapabilityBase):
    model_config = ConfigDict(from_attributes=True)
