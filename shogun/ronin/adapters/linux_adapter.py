"""Linux OS Adapter — v1: basic get_foreground_process via xdotool/proc.

Detects X11 vs Wayland. Full xdotool/wmctrl integration deferred to v2.
"""

from __future__ import annotations

import logging
import os
import subprocess
from typing import Any

from shogun.ronin.adapters.base_adapter import BaseOSAdapter

log = logging.getLogger("shogun.ronin.adapters.linux")


class LinuxAdapter(BaseOSAdapter):
    """Linux-specific OS adapter."""

    def __init__(self):
        self._display_server = self._detect_display_server()

    def _detect_display_server(self) -> str:
        """Detect X11 vs Wayland."""
        if os.environ.get("WAYLAND_DISPLAY"):
            return "wayland"
        if os.environ.get("DISPLAY"):
            return "x11"
        return "unknown"

    def list_windows(self) -> list[dict[str, Any]]:
        """List windows (stub)."""
        return []

    def get_active_window(self) -> dict[str, Any] | None:
        """Get the active window."""
        try:
            if self._display_server == "x11":
                result = subprocess.run(
                    ["xdotool", "getactivewindow", "getwindowname"],
                    capture_output=True, text=True, timeout=5,
                )
                if result.returncode == 0:
                    return {"title": result.stdout.strip(), "process": self.get_foreground_process()}
        except Exception as exc:
            log.debug("Linux: get_active_window failed: %s", exc)
        return None

    def focus_window(self, title_or_id: str) -> bool:
        """Focus window (stub)."""
        return False

    def get_foreground_process(self) -> str | None:
        """Get the foreground process name."""
        try:
            if self._display_server == "x11":
                # Get window PID
                result = subprocess.run(
                    ["xdotool", "getactivewindow", "getwindowpid"],
                    capture_output=True, text=True, timeout=5,
                )
                if result.returncode == 0:
                    pid = result.stdout.strip()
                    if pid:
                        # Read process name from /proc
                        comm_path = f"/proc/{pid}/comm"
                        if os.path.exists(comm_path):
                            with open(comm_path) as f:
                                return f.read().strip()
            # Wayland fallback — limited without compositor support
            log.debug("Linux: foreground process detection limited on %s", self._display_server)
        except Exception as exc:
            log.debug("Linux: get_foreground_process failed: %s", exc)
        return None

    def get_window_controls(self, title_or_id: str) -> list[dict[str, Any]]:
        """Get UI controls (stub — deferred to v2)."""
        return []
