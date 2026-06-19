"""A2A protocol adapter module."""

from __future__ import annotations

from pydantic import BaseModel, Field

from shogun.nexus.schemas.nexus_task import NexusTaskCreate


class A2ATaskRequest(BaseModel):
    """Pydantic schema representing the incoming external A2A task request."""
    
    from_agent_id: str = Field(..., description="The requesting agent identity")
    from_platform: str = Field(..., description="The source platform (microsoft_365, salesforce, etc.)")
    capability: str = Field(..., description="The capability requested, e.g. document.summarize")
    task_description: str | None = Field(None, description="Optional description of the task details")
    context: dict = Field(default_factory=dict, description="Payload/context containing paths, inputs, etc.")
    sensitivity: str = Field("internal", description="Data sensitivity level (low, internal, restricted, sensitive)")
    callback_url: str | None = Field(None, description="Callback URL for async notification")


class A2AAdapter:
    """Adapts external A2A requests to normalized Nexus task creations and vice-versa."""

    @staticmethod
    def to_normalized_task(req: A2ATaskRequest) -> NexusTaskCreate:
        """Translate raw A2A request to normalized task schema."""
        from shogun.nexus.security.permission_mapper import PermissionMapper

        # Determine tools allowed for the capability
        allowed_tools = PermissionMapper.get_allowed_tools(req.capability)
        
        # Decide if manual approval is required based on sensitivity/tools
        approval_required = req.sensitivity == "sensitive"

        return NexusTaskCreate(
            source_agent_id=req.from_agent_id,
            source_platform=req.from_platform,
            source_protocol="a2a",
            requested_action=req.capability,
            task_description=req.task_description or f"A2A execution of {req.capability}",
            required_capabilities=[req.capability],
            input_context=req.context,
            data_sensitivity=req.sensitivity,
            allowed_tools=allowed_tools,
            approval_required=approval_required,
            callback_url=req.callback_url,
            audit_metadata={"adapter": "a2a_adapter_v1"}
        )
