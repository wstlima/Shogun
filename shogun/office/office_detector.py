"""Office Installation Detector — probes Windows registry and COM for Office apps.

Detects installed Office applications, their versions, and availability.
On non-Windows platforms, returns all apps as unavailable with a clear message.
"""

from __future__ import annotations

import logging
import platform
from dataclasses import dataclass, field

log = logging.getLogger("shogun.office.office_detector")


@dataclass
class OfficeAppInfo:
    """Detection result for a single Office application."""

    name: str
    installed: bool = False
    version: str = ""
    build: str = ""
    path: str = ""
    com_prog_id: str = ""
    error: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "installed": self.installed,
            "version": self.version,
            "build": self.build,
            "path": self.path,
            "com_prog_id": self.com_prog_id,
            "error": self.error,
        }


@dataclass
class OfficeDetectionResult:
    """Aggregated detection results for all Office applications."""

    platform_supported: bool = False
    platform_name: str = ""
    excel: OfficeAppInfo = field(default_factory=lambda: OfficeAppInfo(name="Excel"))
    word: OfficeAppInfo = field(default_factory=lambda: OfficeAppInfo(name="Word"))
    powerpoint: OfficeAppInfo = field(default_factory=lambda: OfficeAppInfo(name="PowerPoint"))
    outlook: OfficeAppInfo = field(default_factory=lambda: OfficeAppInfo(name="Outlook"))
    message: str = ""

    def to_dict(self) -> dict:
        return {
            "platform_supported": self.platform_supported,
            "platform_name": self.platform_name,
            "excel": self.excel.to_dict(),
            "word": self.word.to_dict(),
            "powerpoint": self.powerpoint.to_dict(),
            "outlook": self.outlook.to_dict(),
            "message": self.message,
        }

    @property
    def any_installed(self) -> bool:
        return any([
            self.excel.installed,
            self.word.installed,
            self.powerpoint.installed,
            self.outlook.installed,
        ])


# COM ProgIDs for Office applications
_COM_PROG_IDS = {
    "excel": "Excel.Application",
    "word": "Word.Application",
    "powerpoint": "PowerPoint.Application",
    "outlook": "Outlook.Application",
}

# Registry paths for Office installation detection
_REGISTRY_PATHS = [
    r"SOFTWARE\Microsoft\Office\ClickToRun\Configuration",
    r"SOFTWARE\Microsoft\Office\16.0\Common\InstallRoot",
    r"SOFTWARE\Microsoft\Office\15.0\Common\InstallRoot",
]


def detect_office_applications() -> OfficeDetectionResult:
    """Detect installed Office applications.

    On Windows: probes COM class registration and optionally the registry.
    On non-Windows: returns all apps as unavailable.
    """
    result = OfficeDetectionResult(
        platform_name=platform.system(),
    )

    if platform.system() != "Windows":
        result.platform_supported = False
        result.message = (
            f"Office App Mode is not available on {platform.system()}. "
            "Microsoft Office COM automation requires Windows."
        )
        log.info("Office detection: %s — not a Windows platform", result.message)
        return result

    result.platform_supported = True

    # Detect each application via COM
    result.excel = _detect_via_com("excel", "Excel")
    result.word = _detect_via_com("word", "Word")
    result.powerpoint = _detect_via_com("powerpoint", "PowerPoint")
    result.outlook = _detect_via_com("outlook", "Outlook")

    # Try to get version from registry
    _enrich_from_registry(result)

    if result.any_installed:
        installed = [
            app.name for app in [result.excel, result.word, result.powerpoint, result.outlook]
            if app.installed
        ]
        result.message = f"Detected: {', '.join(installed)}"
    else:
        result.message = "No Microsoft Office applications detected."

    log.info("Office detection complete: %s", result.message)
    return result


def _detect_via_com(app_key: str, app_name: str) -> OfficeAppInfo:
    """Detect an Office application via registry probe (fast, non-blocking).

    Only checks COM class registration in the Windows registry — does NOT
    call ``win32com.client.Dispatch()`` which would actually *launch* the
    application.  Launching Office during startup can hang indefinitely if
    the app shows a dialog (activation, profile selection, first-launch
    setup) and blocks the entire async event loop.

    Version/path info is enriched later from the registry via
    ``_enrich_from_registry``.
    """
    info = OfficeAppInfo(name=app_name)
    prog_id = _COM_PROG_IDS.get(app_key, "")
    info.com_prog_id = prog_id

    try:
        # Lightweight CLSID check via the registry — never launches the app
        import winreg
        key_path = f"{prog_id}\\CLSID"
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, key_path):
                info.installed = True
                log.debug("COM ProgID '%s' found in registry", prog_id)
        except FileNotFoundError:
            info.installed = False
            info.error = f"COM class '{prog_id}' not registered"
    except ImportError:
        info.installed = False
        info.error = "winreg not available (non-Windows platform)"
    except Exception as exc:
        info.installed = False
        info.error = str(exc)
        log.warning("Failed to detect %s: %s", app_name, exc)

    return info


def _enrich_from_registry(result: OfficeDetectionResult) -> None:
    """Try to add version info from the Windows registry."""
    try:
        import winreg
    except ImportError:
        return

    for reg_path in _REGISTRY_PATHS:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                try:
                    version, _ = winreg.QueryValueEx(key, "VersionToReport")
                    # Apply to all apps that don't have a version yet
                    for app_info in [result.excel, result.word, result.powerpoint, result.outlook]:
                        if app_info.installed and not app_info.version:
                            app_info.version = str(version)
                except FileNotFoundError:
                    pass
                try:
                    path, _ = winreg.QueryValueEx(key, "InstallPath")
                    for app_info in [result.excel, result.word, result.powerpoint, result.outlook]:
                        if app_info.installed and not app_info.path:
                            app_info.path = str(path)
                except FileNotFoundError:
                    pass
                break  # Found a valid key, stop searching
        except FileNotFoundError:
            continue
        except Exception as exc:
            log.debug("Registry probe failed for %s: %s", reg_path, exc)
