"""Windows OS Adapter — v1: basic get_foreground_process via ctypes.

Full pywinauto integration deferred to v2.
"""

from __future__ import annotations

import logging
from typing import Any

from shogun.ronin.adapters.base_adapter import BaseOSAdapter

log = logging.getLogger("shogun.ronin.adapters.windows")


class WindowsAdapter(BaseOSAdapter):
    """Windows-specific OS adapter."""

    def list_windows(self) -> list[dict[str, Any]]:
        """List visible windows (stub — returns empty in v1)."""
        # TODO: implement via pywinauto or EnumWindows
        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32
            windows: list[dict[str, Any]] = []

            def _enum_callback(hwnd, _):
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buf = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buf, length + 1)
                        title = buf.value
                        if title.strip():
                            windows.append({
                                "hwnd": hwnd,
                                "title": title,
                                "process": self._get_process_name_for_hwnd(hwnd),
                            })
                return True

            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
            user32.EnumWindows(WNDENUMPROC(_enum_callback), 0)
            return windows
        except Exception as exc:
            log.debug("Windows: list_windows failed: %s", exc)
            return []

    def get_active_window(self) -> dict[str, Any] | None:
        """Get the currently focused window."""
        try:
            import ctypes
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if hwnd:
                length = user32.GetWindowTextLengthW(hwnd)
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                return {
                    "hwnd": hwnd,
                    "title": buf.value,
                    "process": self._get_process_name_for_hwnd(hwnd),
                }
        except Exception as exc:
            log.debug("Windows: get_active_window failed: %s", exc)
        return None

    def focus_window(self, title_or_id: str) -> bool:
        """Bring a window to the foreground (stub)."""
        # TODO: implement via SetForegroundWindow
        log.debug("Windows: focus_window stub called for '%s'", title_or_id)
        return False

    def get_foreground_process(self) -> str | None:
        """Get the process name of the foreground window."""
        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32

            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return None

            # Get PID
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))

            if not pid.value:
                return None

            # Open process and get name
            PROCESS_QUERY_INFORMATION = 0x0400
            PROCESS_VM_READ = 0x0010

            handle = kernel32.OpenProcess(
                PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                False, pid.value,
            )
            if not handle:
                return None

            try:
                # Try GetProcessImageFileName via psapi
                psapi = ctypes.windll.psapi
                buf = ctypes.create_unicode_buffer(260)
                psapi.GetProcessImageFileNameW(handle, buf, 260)
                path = buf.value
                if path:
                    # Extract filename from path (e.g. \Device\...\code.exe → code.exe)
                    return path.rsplit("\\", 1)[-1] if "\\" in path else path
            finally:
                kernel32.CloseHandle(handle)

        except Exception as exc:
            log.debug("Windows: get_foreground_process failed: %s", exc)
        return None

    def get_window_controls(self, title_or_id: str) -> list[dict[str, Any]]:
        """Get UI controls (stub — deferred to v2 with pywinauto)."""
        return []

    def _get_process_name_for_hwnd(self, hwnd: int) -> str | None:
        """Get process name for a window handle."""
        try:
            import ctypes
            from ctypes import wintypes

            pid = wintypes.DWORD()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if pid.value:
                handle = ctypes.windll.kernel32.OpenProcess(0x0410, False, pid.value)
                if handle:
                    try:
                        buf = ctypes.create_unicode_buffer(260)
                        ctypes.windll.psapi.GetProcessImageFileNameW(handle, buf, 260)
                        path = buf.value
                        if path:
                            return path.rsplit("\\", 1)[-1]
                    finally:
                        ctypes.windll.kernel32.CloseHandle(handle)
        except Exception:
            pass
        return None
