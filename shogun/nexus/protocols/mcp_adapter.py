"""MCP protocol adapter module."""

from __future__ import annotations

from shogun.nexus.schemas.nexus_task import NexusTaskCreate


class MCPAdapter:
    """Mock/base adapter structure for mapping MCP callTool requests to normalized NexusTasks."""

    @staticmethod
    def map_mcp_request(client_id: str, tool_name: str, arguments: dict) -> NexusTaskCreate:
        """Map Model Context Protocol (MCP) JSON-RPC request schemas to standard tasks."""
        from shogun.nexus.security.permission_mapper import PermissionMapper

        # Maps tool name to matching capability
        capability = f"mcp.{tool_name}"
        allowed_tools = PermissionMapper.get_allowed_tools(capability)

        return NexusTaskCreate(
            source_agent_id=client_id,
            source_platform="mcp_client",
            source_protocol="mcp",
            requested_action=capability,
            task_description=f"MCP remote tool execution: '{tool_name}'",
            required_capabilities=[capability],
            input_context=arguments,
            data_sensitivity="internal",
            allowed_tools=allowed_tools,
            approval_required=False,
            callback_url=None,
            audit_metadata={"adapter": "mcp_adapter_v1"}
        )
