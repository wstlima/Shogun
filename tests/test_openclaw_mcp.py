import asyncio
import json
import sys
from types import SimpleNamespace

import pytest

from shogun.services.mcp_bridge import MCPStdioSession


async def _request(proc, request_id: int, method: str, params: dict | None = None) -> dict:
    assert proc.stdin is not None
    assert proc.stdout is not None
    proc.stdin.write(
        (json.dumps({
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {},
        }) + "\n").encode("utf-8")
    )
    await proc.stdin.drain()
    raw = await asyncio.wait_for(proc.stdout.readline(), timeout=10)
    return json.loads(raw.decode("utf-8"))


@pytest.mark.asyncio
async def test_openclaw_dojo_mcp_lists_tools():
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "shogun.mcp.openclaw_dojo",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        init = await _request(proc, 1, "initialize")
        assert init["result"]["serverInfo"]["name"] == "openclaw-dojo"

        tools = await _request(proc, 2, "tools/list")
        names = {tool["name"] for tool in tools["result"]["tools"]}
        assert "openclaw_search_skills" in names
        assert "openclaw_get_achievements" in names
        assert "openclaw_take_exam" in names
    finally:
        proc.terminate()
        await proc.wait()


@pytest.mark.asyncio
async def test_mcp_bridge_lists_openclaw_tools():
    connector = SimpleNamespace(
        slug="openclaw-dojo",
        config={
            "command": "shogun-python",
            "args": ["-m", "shogun.mcp.openclaw_dojo"],
            "env": {},
            "transport": "stdio",
        },
    )
    async with MCPStdioSession(connector) as session:
        result = await session.list_tools()

    names = {tool["name"] for tool in result["tools"]}
    assert "openclaw_search_skills" in names
    assert "openclaw_list_installed" in names

