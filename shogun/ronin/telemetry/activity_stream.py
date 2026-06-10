"""Activity Stream — real-time Ronin activity push via WebSocket.

Pushes events to the Tenshu UI and via Gensui client.
"""

from __future__ import annotations

import json
import logging
from typing import Any

log = logging.getLogger("shogun.ronin.telemetry.activity")


async def push_event(event_type: str, data: dict[str, Any]) -> None:
    """Push a Ronin event to all connected WebSocket listeners."""
    payload = {
        "type": "ronin_event",
        "event": event_type,
        "data": data,
    }
    # TODO: integrate with Shogun's WebSocket broadcast system
    log.debug("Ronin activity: %s → %s", event_type, json.dumps(data, default=str)[:200])


async def push_approval_request(approval_data: dict[str, Any]) -> None:
    """Push an approval request to the UI — triggers the approval modal."""
    await push_event("ronin.approval_requested", approval_data)


async def push_komainu_alert(level: int, trigger: str) -> None:
    """Push a Komainu alert to the UI."""
    await push_event("ronin.komainu_alert", {
        "level": level,
        "trigger": trigger,
        "message": f"Komainu Level {level}: {trigger}",
    })


async def push_session_update(session_id: str, status: str, **kwargs: Any) -> None:
    """Push a session status update to the UI."""
    await push_event("ronin.session_update", {
        "session_id": session_id,
        "status": status,
        **kwargs,
    })
