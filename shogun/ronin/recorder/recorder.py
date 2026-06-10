"""Ronin Recorder — RPA-style record-and-replay (stub for future).

Concept: Operator performs task once → Ronin records screens, clicks, keys,
windows, timing → converts recording into a Ronin workflow → Shogun Agent
can replay.

Full implementation is a separate build phase.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

log = logging.getLogger("shogun.ronin.recorder")


@dataclass
class RecordingEvent:
    """A single recorded event (click, keypress, screenshot, etc.)."""
    event_type: str  # "mouse_click", "key_press", "screenshot", "window_change"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class RoninRecording:
    """A complete recording session."""
    id: str = ""
    name: str = ""
    events: list[RecordingEvent] = field(default_factory=list)
    screenshots: list[str] = field(default_factory=list)
    started_at: str | None = None
    ended_at: str | None = None
    duration_seconds: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


async def start_recording(name: str = "Untitled Recording") -> str:
    """Start a new recording session. Returns the recording ID.

    STUB — not yet implemented.
    """
    log.info("Ronin Recorder: start_recording() called — not yet implemented")
    return ""


async def stop_recording(recording_id: str) -> RoninRecording | None:
    """Stop a recording and return the completed recording.

    STUB — not yet implemented.
    """
    log.info("Ronin Recorder: stop_recording() called — not yet implemented")
    return None


async def convert_to_workflow(recording: RoninRecording) -> dict[str, Any] | None:
    """Convert a recording into a Ronin workflow / AgentFlow.

    STUB — future integration with the AgentFlow system.
    """
    log.info("Ronin Recorder: convert_to_workflow() called — not yet implemented")
    return None
