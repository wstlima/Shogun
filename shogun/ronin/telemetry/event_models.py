"""Ronin Telemetry Event Models — dataclasses for all Ronin events."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class RoninEvent:
    """Base event for all Ronin telemetry."""
    event_type: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    session_id: str | None = None
    agent_id: str | None = None
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionStartedEvent(RoninEvent):
    """Emitted when a Ronin action begins execution."""
    action_type: str = ""
    target: str | None = None
    risk_level: str = "low"
    app_trust: str | None = None


@dataclass
class ActionCompletedEvent(RoninEvent):
    """Emitted when a Ronin action completes."""
    action_type: str = ""
    status: str = "success"
    duration_ms: int = 0
    confidence: float | None = None


@dataclass
class ScreenshotCapturedEvent(RoninEvent):
    """Emitted when a screenshot is captured."""
    screenshot_path: str = ""
    purpose: str = ""  # "before", "after", "approval", "vision"


@dataclass
class ApprovalRequestedEvent(RoninEvent):
    """Emitted when operator approval is requested."""
    approval_id: str = ""
    action_type: str = ""
    risk_level: str = "high"


@dataclass
class KomainuEvent(RoninEvent):
    """Emitted on Komainu guardian intervention."""
    level: int = 1
    trigger: str = ""


@dataclass
class SessionEvent(RoninEvent):
    """Emitted on session lifecycle changes."""
    posture: str | None = None
    environment_type: str | None = None
    status: str = ""
