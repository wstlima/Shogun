"""macOS OS Adapter — v1: basic get_foreground_process via subprocess.

Full PyObjC/AppleScript integration deferred to v2.
"""

from __future__ import annotations

import logging
import subprocess
from typing import Any

from shogun.ronin.adapters.base_adapter import BaseOSAdapter

log = logging.getLogger("shogun.ronin.adapters.macos")


class MacOSAdapter(BaseOSAdapter):
    """macOS-specific OS adapter."""

    def list_windows(self) -> list[dict[str, Any]]:
        """List windows (stub)."""
        return []

    def get_active_window(self) -> dict[str, Any] | None:
        """Get the active window using AppleScript."""
        try:
            script = 'tell application "System Events" to get {name, unix id} of first process whose frontmost is true'
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                return {"title": result.stdout.strip(), "process": self.get_foreground_process()}
        except Exception as exc:
            log.debug("macOS: get_active_window failed: %s", exc)
        return None

    def focus_window(self, title_or_id: str) -> bool:
        """Focus window (stub)."""
        return False

    def get_foreground_process(self) -> str | None:
        """Get the foreground app name using AppleScript."""
        try:
            script = 'tell application "System Events" to get name of first process whose frontmost is true'
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip() or None
        except Exception as exc:
            log.debug("macOS: get_foreground_process failed: %s", exc)
        return None

    def get_window_controls(self, title_or_id: str) -> list[dict[str, Any]]:
        """Get UI controls (stub — deferred to v2)."""
        return []
