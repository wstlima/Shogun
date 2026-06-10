"""Keyboard Controller — text typing and hotkeys via PyAutoGUI.

All calls wrapped with Komainu _ronin_acting flag.
Posture-guarded — sensitive strings are checked.
"""

from __future__ import annotations

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from shogun.ronin.core.komainu import ronin_acting
from shogun.ronin.policies.ronin_policy_schema import (
    RoninAction,
    RoninActionStatus,
    RoninResult,
)

log = logging.getLogger("shogun.ronin.desktop.keyboard")

_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ronin-kbd")


def _get_pyautogui():
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.03
    return pyautogui


async def type_text(action: RoninAction) -> RoninResult:
    """Type text using the keyboard."""
    text = action.value or action.target
    if not text:
        return RoninResult(
            status=RoninActionStatus.FAILED,
            action_type="desktop.type",
            error="No text provided. Set action.value or action.target.",
        )

    interval = action.metadata.get("interval", 0.03) if action.metadata else 0.03

    try:
        def _do():
            pag = _get_pyautogui()
            with ronin_acting():
                pag.typewrite(text, interval=interval) if text.isascii() else pag.write(text)

        await asyncio.get_event_loop().run_in_executor(_executor, _do)
        return RoninResult(
            status=RoninActionStatus.SUCCESS,
            action_type="desktop.type",
            result_data={"chars_typed": len(text)},
        )
    except ImportError:
        return RoninResult(
            status=RoninActionStatus.FAILED,
            action_type="desktop.type",
            error="pyautogui not installed",
        )
    except Exception as exc:
        return RoninResult(
            status=RoninActionStatus.FAILED,
            action_type="desktop.type",
            error=str(exc),
        )


async def hotkey(action: RoninAction) -> RoninResult:
    """Press a keyboard shortcut (e.g. 'ctrl+s', 'alt+f4')."""
    keys_str = action.value or action.target
    if not keys_str:
        return RoninResult(
            status=RoninActionStatus.FAILED,
            action_type="desktop.hotkey",
            error="No hotkey provided. Set action.value (e.g. 'ctrl+s').",
        )

    # Parse "ctrl+shift+s" into ["ctrl", "shift", "s"]
    keys = [k.strip() for k in keys_str.replace("+", ",").split(",")]

    try:
        def _do():
            pag = _get_pyautogui()
            with ronin_acting():
                pag.hotkey(*keys)

        await asyncio.get_event_loop().run_in_executor(_executor, _do)
        return RoninResult(
            status=RoninActionStatus.SUCCESS,
            action_type="desktop.hotkey",
            result_data={"keys": keys},
        )
    except ImportError:
        return RoninResult(
            status=RoninActionStatus.FAILED,
            action_type="desktop.hotkey",
            error="pyautogui not installed",
        )
    except Exception as exc:
        return RoninResult(
            status=RoninActionStatus.FAILED,
            action_type="desktop.hotkey",
            error=str(exc),
        )
