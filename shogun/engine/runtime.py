"""Shogun runtime — agent orchestration engine placeholder.

DEPRECATED: Orchestration is handled by flow_engine.py (Agent Flows),
bushido_engine.py (scheduled jobs), and the chat pipeline in agents.py.
This module exists for backward compatibility only.
"""

from __future__ import annotations


class ShogunRuntime:
    """Deprecated placeholder for the Shogun agent orchestration runtime."""

    def __init__(self):
        self.status = "initialized"

    async def start(self):
        self.status = "running"

    async def stop(self):
        self.status = "stopped"
