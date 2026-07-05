"""Exact emergency control commands shared by Telegram and Microsoft Teams."""

from __future__ import annotations

from typing import Literal

HarakiriAction = Literal["activate", "reset"]


def parse_harakiri_control(text: str) -> HarakiriAction | None:
    """Recognize only the two explicit, case-insensitive control messages."""
    normalized = text.strip().casefold()
    if normalized == "++harakiri":
        return "activate"
    if normalized == "--harakiri":
        return "reset"
    return None


async def execute_harakiri_control(
    action: HarakiriAction,
    *,
    source: str,
    actor: str,
) -> dict:
    """Apply the global kill switch and record channel-specific provenance."""
    from shogun.api.security import activate_kill_switch, reset_kill_switch

    if action == "activate":
        response = await activate_kill_switch()
    else:
        response = await reset_kill_switch()

    try:
        from shogun.services.event_logger import EventLogger

        await EventLogger.emit_oversight_event(
            "oversight.remote_harakiri_control",
            f"Remote Harakiri {action} command accepted from {source}",
            detail={
                "action": action,
                "source": source,
                "actor": actor,
                "exact_control_command": True,
            },
            severity="critical" if action == "activate" else "warn",
        )
    except Exception:
        pass

    return response.data or {}

