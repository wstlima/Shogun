"""Webhook protocol adapter module."""

from __future__ import annotations

from shogun.nexus.schemas.nexus_task import NexusTaskCreate


class WebhookAdapter:
    """Mock/base adapter structure for mapping external webhooks to normalized NexusTasks."""

    @staticmethod
    def map_webhook_payload(payload: dict) -> NexusTaskCreate:
        """Parse raw webhook data and convert into a normalized task request schema."""
        from shogun.nexus.security.permission_mapper import PermissionMapper

        event_type = payload.get("event", "default.task")
        sender = payload.get("sender_id", "webhook_trigger")
        platform = payload.get("platform", "generic_webhook")
        data = payload.get("data", {})

        allowed_tools = PermissionMapper.get_allowed_tools(event_type)

        return NexusTaskCreate(
            source_agent_id=sender,
            source_platform=platform,
            source_protocol="webhook",
            requested_action=event_type,
            task_description=f"Webhook-triggered action for event '{event_type}'",
            required_capabilities=[event_type],
            input_context=data,
            data_sensitivity="internal",
            allowed_tools=allowed_tools,
            approval_required=False,
            callback_url=payload.get("reply_to"),
            audit_metadata={"adapter": "webhook_adapter_v1"}
        )
