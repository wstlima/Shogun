"""Minimal stdio MCP client used by Shogun agents.

The Katana stores MCP connector definitions today.  This bridge makes those
definitions executable for stdio JSON-RPC MCP servers.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select

from shogun.config import PROJECT_ROOT
from shogun.db.models.tool_connector import ToolConnector


class MCPBridgeError(RuntimeError):
    """Raised when an MCP connector cannot be launched or called."""


@dataclass
class MCPCallResult:
    connector: str
    tool: str | None
    response: dict[str, Any]


class MCPStdioSession:
    """One short-lived stdio MCP JSON-RPC session."""

    def __init__(self, connector: ToolConnector, *, timeout: float = 45.0):
        self.connector = connector
        self.timeout = timeout
        self._proc: asyncio.subprocess.Process | None = None
        self._next_id = 1

    async def __aenter__(self) -> "MCPStdioSession":
        command, args = self._command()
        env = os.environ.copy()
        env.update({str(k): str(v) for k, v in (self.connector.config or {}).get("env", {}).items() if v is not None})
        self._proc = await asyncio.create_subprocess_exec(
            command,
            *args,
            cwd=str(PROJECT_ROOT),
            env=env,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await self._initialize()
        return self

    async def __aexit__(self, *_args: Any) -> None:
        proc = self._proc
        if not proc:
            return
        if proc.returncode is None:
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), timeout=2)
            except TimeoutError:
                proc.kill()
                await proc.wait()
        self._proc = None

    def _command(self) -> tuple[str, list[str]]:
        config = self.connector.config or {}
        command = str(config.get("command") or "").strip()
        args = [str(arg) for arg in config.get("args") or []]
        if not command:
            raise MCPBridgeError(f"MCP connector '{self.connector.slug}' has no command configured.")
        if command in {"shogun-python", "python", "python.exe"}:
            command = sys.executable
        return command, args

    async def _send(self, message: dict[str, Any]) -> None:
        proc = self._require_process()
        assert proc.stdin is not None
        proc.stdin.write((json.dumps(message, separators=(",", ":")) + "\n").encode("utf-8"))
        await proc.stdin.drain()

    async def _receive(self) -> dict[str, Any]:
        proc = self._require_process()
        assert proc.stdout is not None
        try:
            raw = await asyncio.wait_for(proc.stdout.readline(), timeout=self.timeout)
        except TimeoutError as exc:
            err = await self._stderr_tail()
            raise MCPBridgeError(f"MCP connector timed out. {err}".strip()) from exc
        if not raw:
            err = await self._stderr_tail()
            raise MCPBridgeError(f"MCP connector exited before responding. {err}".strip())
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise MCPBridgeError(f"MCP connector returned invalid JSON: {raw[:200]!r}") from exc

    async def _request(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        request_id = self._next_id
        self._next_id += 1
        await self._send({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}})
        while True:
            response = await self._receive()
            if response.get("id") != request_id:
                continue
            if response.get("error"):
                error = response["error"]
                raise MCPBridgeError(str(error.get("message") or error))
            return response.get("result") or {}

    async def _notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        await self._send({"jsonrpc": "2.0", "method": method, "params": params or {}})

    async def _initialize(self) -> None:
        await self._request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "shogun", "version": "1.0"},
            },
        )
        await self._notify("notifications/initialized")

    async def list_tools(self) -> dict[str, Any]:
        return await self._request("tools/list")

    async def call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
        return await self._request("tools/call", {"name": tool_name, "arguments": arguments or {}})

    async def list_resources(self) -> dict[str, Any]:
        return await self._request("resources/list")

    async def read_resource(self, uri: str) -> dict[str, Any]:
        return await self._request("resources/read", {"uri": uri})

    def _require_process(self) -> asyncio.subprocess.Process:
        if not self._proc:
            raise MCPBridgeError("MCP process is not running.")
        return self._proc

    async def _stderr_tail(self) -> str:
        proc = self._proc
        if not proc or not proc.stderr:
            return ""
        try:
            raw = await asyncio.wait_for(proc.stderr.read(2000), timeout=0.2)
        except Exception:
            return ""
        text = raw.decode("utf-8", errors="replace").strip()
        return f"stderr: {text}" if text else ""


async def get_mcp_connector(db_session: Any, slug: str) -> ToolConnector:
    result = await db_session.execute(
        select(ToolConnector).where(
            ToolConnector.slug == slug,
            ToolConnector.connector_type == "mcp",
            ToolConnector.is_deleted == False,
            ToolConnector.status != "disabled",
        )
    )
    connector = result.scalars().first()
    if not connector:
        raise MCPBridgeError(f"MCP connector '{slug}' is not registered or is disabled.")
    transport = (connector.config or {}).get("transport", "stdio")
    if transport != "stdio":
        raise MCPBridgeError(f"MCP connector '{slug}' uses unsupported transport '{transport}'.")
    return connector


async def list_mcp_tools(db_session: Any, connector_slug: str) -> MCPCallResult:
    connector = await get_mcp_connector(db_session, connector_slug)
    async with MCPStdioSession(connector) as session:
        response = await session.list_tools()
    return MCPCallResult(connector=connector.slug, tool=None, response=response)


async def call_mcp_tool(
    db_session: Any,
    connector_slug: str,
    tool_name: str,
    arguments: dict[str, Any] | None = None,
) -> MCPCallResult:
    connector = await get_mcp_connector(db_session, connector_slug)
    async with MCPStdioSession(connector) as session:
        response = await session.call_tool(tool_name, arguments or {})
    return MCPCallResult(connector=connector.slug, tool=tool_name, response=response)


async def list_mcp_resources(db_session: Any, connector_slug: str) -> MCPCallResult:
    connector = await get_mcp_connector(db_session, connector_slug)
    async with MCPStdioSession(connector) as session:
        response = await session.list_resources()
    return MCPCallResult(connector=connector.slug, tool=None, response=response)


async def read_mcp_resource(db_session: Any, connector_slug: str, uri: str) -> MCPCallResult:
    connector = await get_mcp_connector(db_session, connector_slug)
    async with MCPStdioSession(connector) as session:
        response = await session.read_resource(uri)
    return MCPCallResult(connector=connector.slug, tool=None, response=response)

