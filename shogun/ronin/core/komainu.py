"""Komainu (狛犬) — Guardian Lion-Dog Override.

Named after the stone guardian lion-dogs at the gates of Japanese shrines.
The Komainu stands guard while Ronin controls the desktop — the moment
the operator physically intervenes, the Komainu responds.

Three-Tier Response:
  Level 1: PAUSE   — Pause Ronin session, ask operator what to do
  Level 2: TERMINATE — Kill the active session (others survive)
  Level 3: HARAKIRI — Full global shutdown (Escape x3 only)

Mechanism:
  - pynput listeners on keyboard + mouse run in daemon threads
  - Thread-safe _ronin_acting flag distinguishes Ronin input from human input
  - Position tracker with ±3px jitter tolerance for mouse
  - Triple-Escape fires Harakiri regardless of configuration
"""

from __future__ import annotations

import asyncio
import logging
import math
import threading
import time
from typing import Any, Callable

log = logging.getLogger("shogun.ronin.komainu")

# ── Thread-safe state ────────────────────────────────────────────────

_lock = threading.Lock()
_ronin_acting: bool = False
_expected_mouse_pos: tuple[int, int] | None = None
_active: bool = False
_paused: bool = False
_komainu_level: int = 1  # Default response level
_mouse_listener: Any = None
_keyboard_listener: Any = None

# Escape rapid-press tracking for Level 3
_escape_times: list[float] = []
_ESCAPE_WINDOW = 1.5  # seconds — 3 Escapes within this window = Harakiri
_JITTER_TOLERANCE = 3  # pixels

# Callbacks — set by RoninController
_on_pause: Callable | None = None
_on_terminate: Callable | None = None
_on_harakiri: Callable | None = None


# ── Context manager for Ronin actions ────────────────────────────────


class ronin_acting:
    """Context manager to mark Ronin-generated input.

    Usage:
        with ronin_acting(expected_pos=(100, 200)):
            pyautogui.click(100, 200)
    """

    def __init__(self, expected_pos: tuple[int, int] | None = None):
        self._expected_pos = expected_pos

    def __enter__(self):
        global _ronin_acting, _expected_mouse_pos
        with _lock:
            _ronin_acting = True
            if self._expected_pos:
                _expected_mouse_pos = self._expected_pos
        return self

    def __exit__(self, *args):
        global _ronin_acting
        with _lock:
            _ronin_acting = False


def set_expected_position(x: int, y: int) -> None:
    """Update the expected mouse position after a Ronin move."""
    global _expected_mouse_pos
    with _lock:
        _expected_mouse_pos = (x, y)


# ── Listener callbacks ──────────────────────────────────────────────


def _on_mouse_move(x: int, y: int) -> None:
    """Called by pynput on every mouse move event."""
    if not _active or _paused:
        return

    with _lock:
        if _ronin_acting:
            return  # Ronin is mid-action — ignore
        # Check jitter tolerance
        if _expected_mouse_pos:
            dx = abs(x - _expected_mouse_pos[0])
            dy = abs(y - _expected_mouse_pos[1])
            if dx <= _JITTER_TOLERANCE and dy <= _JITTER_TOLERANCE:
                return  # Within jitter tolerance — likely OS smoothing

    # This is human input
    log.warning("Komainu: human mouse movement detected at (%d, %d)", x, y)
    _trigger_response("mouse_movement")


def _on_mouse_click(x: int, y: int, button: Any, pressed: bool) -> None:
    """Called by pynput on mouse click events."""
    if not _active or _paused or not pressed:
        return

    with _lock:
        if _ronin_acting:
            return

    log.warning("Komainu: human mouse click detected at (%d, %d)", x, y)
    _trigger_response("mouse_click")


def _on_key_press(key: Any) -> None:
    """Called by pynput on every key press."""
    if not _active:
        return

    # ── Triple-Escape detection (always active, even when paused) ──
    now = time.monotonic()
    key_name = _get_key_name(key)

    if key_name == "escape":
        _escape_times.append(now)
        # Keep only recent presses
        while _escape_times and now - _escape_times[0] > _ESCAPE_WINDOW:
            _escape_times.pop(0)
        if len(_escape_times) >= 3:
            log.critical("Komainu: Triple-Escape detected — firing HARAKIRI!")
            _escape_times.clear()
            _trigger_level3_harakiri("triple_escape")
            return

    if _paused:
        return  # Non-escape keys ignored when paused

    with _lock:
        if _ronin_acting:
            return

    log.warning("Komainu: human keypress detected — key=%s", key_name)
    _trigger_response("keypress")


def _get_key_name(key: Any) -> str:
    """Extract a readable name from a pynput key object."""
    try:
        if hasattr(key, "name"):
            return key.name
        if hasattr(key, "char") and key.char:
            return key.char
    except Exception:
        pass
    return str(key)


# ── Response logic ───────────────────────────────────────────────────


def _trigger_response(trigger: str) -> None:
    """Execute the configured Komainu response level."""
    level = _komainu_level
    if level == 1:
        _trigger_level1_pause(trigger)
    elif level == 2:
        _trigger_level2_terminate(trigger)
    else:
        _trigger_level3_harakiri(trigger)


def _trigger_level1_pause(trigger: str) -> None:
    """Level 1: Pause the current Ronin session."""
    global _paused
    _paused = True
    log.warning("Komainu Level 1: PAUSE — trigger=%s", trigger)

    # Fire callback in a thread-safe way
    if _on_pause:
        try:
            _on_pause(trigger)
        except Exception as exc:
            log.error("Komainu: pause callback failed: %s", exc)

    # Emit audit event (fire-and-forget)
    _emit_komainu_event_sync(1, f"Operator input detected: {trigger}")


def _trigger_level2_terminate(trigger: str) -> None:
    """Level 2: Terminate the active Ronin session."""
    global _paused
    _paused = True
    log.warning("Komainu Level 2: TERMINATE SESSION — trigger=%s", trigger)

    if _on_terminate:
        try:
            _on_terminate(trigger)
        except Exception as exc:
            log.error("Komainu: terminate callback failed: %s", exc)

    _emit_komainu_event_sync(2, f"Session terminated: {trigger}")


def _trigger_level3_harakiri(trigger: str) -> None:
    """Level 3: Global Harakiri — emergency stop everything."""
    global _active, _paused
    _active = False
    _paused = True
    log.critical("Komainu Level 3: GLOBAL HARAKIRI — trigger=%s", trigger)

    if _on_harakiri:
        try:
            _on_harakiri(trigger)
        except Exception as exc:
            log.error("Komainu: harakiri callback failed: %s", exc)

    _emit_komainu_event_sync(3, f"Harakiri triggered: {trigger}")

    # Fire the global kill switch via API
    _fire_kill_switch_async()


def _fire_kill_switch_async() -> None:
    """Fire the global Shogun kill switch from a background thread."""
    def _do_fire():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_activate_kill_switch())
            loop.close()
        except Exception as exc:
            log.error("Komainu: failed to fire kill switch: %s", exc)

    thread = threading.Thread(target=_do_fire, daemon=True, name="komainu-harakiri")
    thread.start()


async def _activate_kill_switch() -> None:
    """Activate the global Shogun kill switch."""
    try:
        from shogun.api.security import _get_agent_posture, _save_agent_posture, TIER_CONSTRAINTS
        posture = await _get_agent_posture()
        posture["active_tier"] = "shrine"
        posture.update(TIER_CONSTRAINTS["shrine"])
        posture["kill_switch_active"] = True
        await _save_agent_posture(posture)

        from shogun.services.event_logger import EventLogger
        await EventLogger.emit_incident_event(
            "incident.komainu_harakiri",
            "Komainu: Emergency Harakiri — operator physical input override",
            severity="critical",
            risk_score="critical",
            detail={"trigger": "komainu_level_3"},
        )
    except Exception as exc:
        log.error("Komainu: kill switch activation failed: %s", exc)


def _emit_komainu_event_sync(level: int, reason: str) -> None:
    """Fire-and-forget audit event from a potentially non-async context."""
    try:
        from shogun.ronin.core.audit_logger import RoninAuditLogger
        import asyncio

        async def _emit():
            await RoninAuditLogger.log_komainu_event(level, reason)

        # Try to get existing loop, or create new one
        try:
            loop = asyncio.get_running_loop()
            asyncio.ensure_future(_emit())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(_emit())
            loop.close()
    except Exception:
        pass  # Never let audit failure crash the guardian


# ── Lifecycle ────────────────────────────────────────────────────────


def start_komainu(
    level: int = 1,
    on_pause: Callable | None = None,
    on_terminate: Callable | None = None,
    on_harakiri: Callable | None = None,
) -> bool:
    """Start the Komainu guardian. Returns True if started successfully.

    Args:
        level: Default response level (1=Pause, 2=Terminate, 3=Harakiri)
        on_pause: Callback for Level 1 (receives trigger string)
        on_terminate: Callback for Level 2
        on_harakiri: Callback for Level 3
    """
    global _active, _paused, _komainu_level
    global _on_pause, _on_terminate, _on_harakiri
    global _mouse_listener, _keyboard_listener

    if _active:
        log.debug("Komainu: already active")
        return True

    try:
        from pynput import mouse, keyboard
    except ImportError:
        log.warning(
            "Komainu: pynput not installed — guardian disabled. "
            "Install with: pip install pynput"
        )
        return False

    _komainu_level = max(1, min(3, level))
    _on_pause = on_pause
    _on_terminate = on_terminate
    _on_harakiri = on_harakiri
    _paused = False
    _escape_times.clear()

    # Start listeners in daemon threads
    _mouse_listener = mouse.Listener(on_move=_on_mouse_move, on_click=_on_mouse_click)
    _keyboard_listener = keyboard.Listener(on_press=_on_key_press)

    _mouse_listener.daemon = True
    _keyboard_listener.daemon = True

    _mouse_listener.start()
    _keyboard_listener.start()
    _active = True

    log.info("Komainu: guardian started (level=%d)", _komainu_level)
    return True


def stop_komainu() -> None:
    """Stop the Komainu guardian. Releases all listeners."""
    global _active, _mouse_listener, _keyboard_listener

    _active = False

    if _mouse_listener:
        try:
            _mouse_listener.stop()
        except Exception:
            pass
        _mouse_listener = None

    if _keyboard_listener:
        try:
            _keyboard_listener.stop()
        except Exception:
            pass
        _keyboard_listener = None

    log.info("Komainu: guardian stopped")


def pause_komainu() -> None:
    """Temporarily suspend Komainu monitoring."""
    global _paused
    _paused = True
    log.info("Komainu: monitoring paused")


def resume_komainu() -> None:
    """Resume Komainu monitoring after a pause."""
    global _paused
    _paused = False
    _escape_times.clear()
    log.info("Komainu: monitoring resumed")


def is_active() -> bool:
    """Check if Komainu is currently active."""
    return _active


def is_paused() -> bool:
    """Check if Komainu is currently paused."""
    return _paused


def get_status() -> dict[str, Any]:
    """Get current Komainu status for telemetry/API."""
    return {
        "active": _active,
        "paused": _paused,
        "level": _komainu_level,
        "status": "paused" if _paused else ("active" if _active else "inactive"),
    }
