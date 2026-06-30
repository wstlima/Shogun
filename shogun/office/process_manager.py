"""Office Process Manager — tracks and manages COM application instances.

Responsible for:
  - Opening Office apps when needed (via COM Dispatch)
  - Tracking opened instances per application
  - Closing files and quitting apps cleanly
  - Detecting zombie/hung processes
  - Timeout enforcement
  - Cleanup on Shogun shutdown
"""

from __future__ import annotations

import logging
import platform
import time
from dataclasses import dataclass, field
from typing import Any

log = logging.getLogger("shogun.office.process_manager")


@dataclass
class COMInstance:
    """Tracks a live COM application instance."""

    app_name: str
    com_object: Any = None
    opened_at: float = field(default_factory=time.time)
    opened_files: list[str] = field(default_factory=list)
    visible: bool = False

    @property
    def age_seconds(self) -> float:
        return time.time() - self.opened_at


# COM ProgIDs
_PROG_IDS = {
    "excel": "Excel.Application",
    "word": "Word.Application",
    "powerpoint": "PowerPoint.Application",
    "outlook": "Outlook.Application",
}


class OfficeProcessManager:
    """Manages Office COM application lifecycles.

    This class is NOT async — all methods are synchronous and must
    be called from the STA thread pool via ``run_com()``.
    """

    def __init__(self):
        self._instances: dict[str, COMInstance] = {}

    def open_app(self, app_name: str, visible: bool = False) -> Any:
        """Get or create a COM application instance.

        Args:
            app_name: One of "excel", "word", "powerpoint", "outlook".
            visible: Whether the Office window should be visible.

        Returns:
            The COM application object.
        """
        app_key = app_name.lower()

        # Return existing instance if still alive
        if app_key in self._instances:
            instance = self._instances[app_key]
            if self._is_alive(instance):
                return instance.com_object
            else:
                log.warning("Stale COM instance for '%s' — removing", app_name)
                self._force_cleanup(app_key)

        if platform.system() != "Windows":
            from shogun.office.exceptions import OfficeNotAvailableError
            raise OfficeNotAvailableError()

        prog_id = _PROG_IDS.get(app_key)
        if not prog_id:
            raise ValueError(f"Unknown Office application: {app_name}")

        try:
            import win32com.client
            com_obj = win32com.client.Dispatch(prog_id)

            # Configure visibility and alert suppression
            if app_key != "outlook":  # Outlook doesn't have Visible in the same way
                try:
                    com_obj.Visible = visible
                except Exception:
                    pass
                try:
                    com_obj.DisplayAlerts = False
                except Exception:
                    pass

            instance = COMInstance(
                app_name=app_key,
                com_object=com_obj,
                visible=visible,
            )
            self._instances[app_key] = instance
            log.info("Opened COM instance for '%s' (visible=%s)", app_name, visible)
            return com_obj

        except ImportError:
            from shogun.office.exceptions import OfficeNotAvailableError
            raise OfficeNotAvailableError("pywin32 is not installed.")
        except Exception as exc:
            from shogun.office.exceptions import OfficeNotInstalledError
            log.error("Failed to open %s: %s", app_name, exc)
            raise OfficeNotInstalledError(app_name) from exc

    def close_app(self, app_name: str) -> None:
        """Cleanly quit an Office application instance."""
        app_key = app_name.lower()
        instance = self._instances.pop(app_key, None)
        if instance is None:
            return

        try:
            com_obj = instance.com_object
            if com_obj is None:
                return

            # Close any open documents/workbooks first
            if app_key == "excel":
                try:
                    for wb in com_obj.Workbooks:
                        wb.Close(SaveChanges=False)
                except Exception:
                    pass
            elif app_key == "word":
                try:
                    for doc in com_obj.Documents:
                        doc.Close(SaveChanges=0)  # wdDoNotSaveChanges = 0
                except Exception:
                    pass
            elif app_key == "powerpoint":
                try:
                    for pres in com_obj.Presentations:
                        pres.Close()
                except Exception:
                    pass

            # Quit the application
            try:
                com_obj.Quit()
            except Exception:
                pass

            log.info("Closed COM instance for '%s'", app_name)

        except Exception as exc:
            log.warning("Error closing %s: %s — forcing cleanup", app_name, exc)
            self._force_cleanup_instance(instance)

    def close_all(self) -> int:
        """Close all tracked Office instances. Returns count closed."""
        app_names = list(self._instances.keys())
        count = 0
        for app_name in app_names:
            try:
                self.close_app(app_name)
                count += 1
            except Exception as exc:
                log.warning("Failed to close %s during shutdown: %s", app_name, exc)
        return count

    def track_file(self, app_name: str, file_path: str) -> None:
        """Record that a file has been opened in an Office instance."""
        app_key = app_name.lower()
        instance = self._instances.get(app_key)
        if instance:
            instance.opened_files.append(file_path)

    def untrack_file(self, app_name: str, file_path: str) -> None:
        """Record that a file has been closed in an Office instance."""
        app_key = app_name.lower()
        instance = self._instances.get(app_key)
        if instance and file_path in instance.opened_files:
            instance.opened_files.remove(file_path)

    def get_status(self) -> dict[str, dict]:
        """Return status information for all tracked instances."""
        return {
            name: {
                "alive": self._is_alive(inst),
                "visible": inst.visible,
                "age_seconds": round(inst.age_seconds),
                "opened_files": list(inst.opened_files),
            }
            for name, inst in self._instances.items()
        }

    def _is_alive(self, instance: COMInstance) -> bool:
        """Check if a COM instance is still responsive."""
        if instance.com_object is None:
            return False
        try:
            # Try to access a basic property — if it raises, the instance is dead
            _ = instance.com_object.Name
            return True
        except Exception:
            return False

    def _force_cleanup(self, app_key: str) -> None:
        """Force-remove a tracked instance without graceful cleanup."""
        instance = self._instances.pop(app_key, None)
        if instance:
            self._force_cleanup_instance(instance)

    def _force_cleanup_instance(self, instance: COMInstance) -> None:
        """Attempt to kill a hung Office process."""
        try:
            import psutil
            # Find the Office process and terminate it
            process_names = {
                "excel": "EXCEL.EXE",
                "word": "WINWORD.EXE",
                "powerpoint": "POWERPNT.EXE",
                "outlook": "OUTLOOK.EXE",
            }
            target = process_names.get(instance.app_name, "")
            if target:
                for proc in psutil.process_iter(["name"]):
                    if proc.info["name"] and proc.info["name"].upper() == target:
                        # Only kill if it was started after our instance
                        if proc.create_time() >= instance.opened_at - 5:
                            proc.terminate()
                            log.warning("Force-terminated %s (PID %d)", target, proc.pid)
                            break
        except ImportError:
            log.warning("psutil not available — cannot force-terminate %s", instance.app_name)
        except Exception as exc:
            log.warning("Force cleanup failed for %s: %s", instance.app_name, exc)


# ── Singleton Instance ───────────────────────────────────────────────

_manager: OfficeProcessManager | None = None


def get_process_manager() -> OfficeProcessManager:
    """Get or create the singleton process manager."""
    global _manager
    if _manager is None:
        _manager = OfficeProcessManager()
    return _manager
