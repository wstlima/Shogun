"""Environment Detector — identifies the execution environment type.

Determines whether Ronin is running on a physical machine, VM, sandbox,
remote desktop, Citrix session, or cloud workspace. This enables Gensui
policies like "Desktop Full allowed in VM only".
"""

from __future__ import annotations

import logging
import os
import platform
import subprocess
import uuid
from typing import Any

from shogun.ronin.policies.ronin_policy_schema import EnvironmentInfo, EnvironmentType

log = logging.getLogger("shogun.ronin.environment")


def detect_environment() -> EnvironmentInfo:
    """Detect the current execution environment.

    Returns an EnvironmentInfo with environment_type, OS details,
    hostname, machine_id, and any hypervisor information.
    """
    os_type = _detect_os_type()
    hostname = platform.node() or None
    machine_id = _get_machine_id()
    os_version = platform.version() or None

    env_type = EnvironmentType.PHYSICAL
    hypervisor: str | None = None
    is_disposable = False
    details: dict[str, Any] = {}

    # ── Check for Citrix (before VM — Citrix runs inside VMs but is a distinct env) ──
    if _check_citrix():
        env_type = EnvironmentType.CITRIX
        details["citrix"] = True

    # ── Check for Remote Desktop ──
    elif _check_remote_desktop(os_type):
        env_type = EnvironmentType.REMOTE_DESKTOP
        details["remote_session"] = True

    # ── Check for Cloud Workspace ──
    elif _check_cloud_workspace():
        env_type = EnvironmentType.CLOUD_WORKSPACE
        details["cloud_provider"] = _detect_cloud_provider()

    # ── Check for Sandbox ──
    elif _check_sandbox(os_type):
        env_type = EnvironmentType.SANDBOX
        is_disposable = True
        details["sandbox"] = True

    # ── Check for VM ──
    elif _check_vm(os_type):
        env_type = EnvironmentType.VM
        hypervisor = _detect_hypervisor(os_type)
        details["hypervisor"] = hypervisor
        # VMs without persistent storage are disposable
        is_disposable = _is_disposable_vm()

    info = EnvironmentInfo(
        environment_type=env_type,
        os_type=os_type,
        os_version=os_version,
        hostname=hostname,
        machine_id=machine_id,
        is_disposable=is_disposable,
        hypervisor=hypervisor,
        details=details,
    )
    log.info(
        "Ronin: environment detected — type=%s, os=%s, hostname=%s, disposable=%s",
        env_type.value, os_type, hostname, is_disposable,
    )
    return info


# ── OS Detection ─────────────────────────────────────────────────────


def _detect_os_type() -> str:
    """Return 'windows', 'macos', or 'linux'."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    if system == "windows":
        return "windows"
    return "linux"


def _get_machine_id() -> str | None:
    """Get a stable machine identifier."""
    try:
        if platform.system() == "Windows":
            # Windows: use MachineGuid from registry
            result = subprocess.run(
                ["reg", "query", r"HKLM\SOFTWARE\Microsoft\Cryptography", "/v", "MachineGuid"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split("\n"):
                    if "MachineGuid" in line:
                        return line.split()[-1]
        elif platform.system() == "Linux":
            # Linux: /etc/machine-id
            machine_id_file = "/etc/machine-id"
            if os.path.exists(machine_id_file):
                with open(machine_id_file) as f:
                    return f.read().strip()
        elif platform.system() == "Darwin":
            # macOS: IOPlatformUUID
            result = subprocess.run(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if "IOPlatformUUID" in line:
                        return line.split('"')[-2]
    except Exception as exc:
        log.debug("Failed to get machine ID: %s", exc)
    # Fallback: generate from hostname + MAC
    try:
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, platform.node()))
    except Exception:
        return None


# ── VM Detection ─────────────────────────────────────────────────────


def _check_vm(os_type: str) -> bool:
    """Check if running inside a virtual machine."""
    vm_indicators: list[str] = []

    try:
        if os_type == "windows":
            # Check systeminfo for System Manufacturer
            result = subprocess.run(
                ["systeminfo"], capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                output_lower = result.stdout.lower()
                vm_indicators = [
                    "vmware", "virtualbox", "virtual machine",
                    "qemu", "hyper-v", "kvm", "xen", "parallels",
                    "microsoft corporation" if "virtual" in output_lower else "",
                ]
                for indicator in vm_indicators:
                    if indicator and indicator in output_lower:
                        return True

        elif os_type == "linux":
            # Check DMI / SMBIOS
            dmi_paths = [
                "/sys/class/dmi/id/product_name",
                "/sys/class/dmi/id/sys_vendor",
                "/sys/class/dmi/id/board_vendor",
            ]
            for path in dmi_paths:
                if os.path.exists(path):
                    with open(path) as f:
                        content = f.read().strip().lower()
                    for hint in ["vmware", "virtualbox", "qemu", "kvm", "hyper-v", "xen", "parallels"]:
                        if hint in content:
                            return True
            # Check /proc/cpuinfo for hypervisor flag
            if os.path.exists("/proc/cpuinfo"):
                with open("/proc/cpuinfo") as f:
                    if "hypervisor" in f.read().lower():
                        return True

        elif os_type == "macos":
            # macOS: check for known VM guest tools
            result = subprocess.run(
                ["system_profiler", "SPHardwareDataType"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                output_lower = result.stdout.lower()
                for hint in ["vmware", "virtualbox", "parallels", "qemu", "utm"]:
                    if hint in output_lower:
                        return True
    except Exception as exc:
        log.debug("VM detection error: %s", exc)

    return False


def _detect_hypervisor(os_type: str) -> str | None:
    """Identify which hypervisor is in use."""
    try:
        if os_type == "windows":
            result = subprocess.run(
                ["systeminfo"], capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                output_lower = result.stdout.lower()
                for name in ["vmware", "virtualbox", "hyper-v", "qemu", "kvm", "xen", "parallels"]:
                    if name in output_lower:
                        return name.title()

        elif os_type == "linux":
            for path in ["/sys/class/dmi/id/product_name", "/sys/class/dmi/id/sys_vendor"]:
                if os.path.exists(path):
                    with open(path) as f:
                        content = f.read().strip().lower()
                    for name in ["vmware", "virtualbox", "qemu", "kvm", "hyper-v", "xen", "parallels"]:
                        if name in content:
                            return name.title()
    except Exception:
        pass
    return None


def _is_disposable_vm() -> bool:
    """Heuristic: check if the VM appears disposable (no persistent user data)."""
    # Conservative: assume not disposable unless explicitly indicated
    return os.environ.get("RONIN_DISPOSABLE_ENV", "").lower() in ("1", "true", "yes")


# ── Sandbox Detection ────────────────────────────────────────────────


def _check_sandbox(os_type: str) -> bool:
    """Check if running inside a sandbox."""
    if os_type == "windows":
        # Windows Sandbox has a specific marker
        if os.environ.get("COMPUTERNAME", "").startswith("YOURPC"):
            return True
        # Check for AppContainer isolation
        if os.path.exists(r"C:\Users\WDAGUtilityAccount"):
            return True

    # Check for firejail on Linux
    if os_type == "linux":
        if os.path.exists("/proc/1/root/.firejail"):
            return True

    # General: environment variable override
    if os.environ.get("RONIN_SANDBOX", "").lower() in ("1", "true"):
        return True

    return False


# ── Remote Desktop Detection ────────────────────────────────────────


def _check_remote_desktop(os_type: str) -> bool:
    """Check if accessed via remote desktop."""
    try:
        if os_type == "windows":
            # SM_REMOTESESSION via ctypes
            import ctypes
            SM_REMOTESESSION = 0x1000
            return bool(ctypes.windll.user32.GetSystemMetrics(SM_REMOTESESSION))

        if os_type == "linux":
            # SSH connection
            if os.environ.get("SSH_CONNECTION") or os.environ.get("SSH_CLIENT"):
                return True

        if os_type == "macos":
            # Check for Screen Sharing
            result = subprocess.run(
                ["ps", "aux"], capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0 and "screensharingd" in result.stdout.lower():
                return True
    except Exception as exc:
        log.debug("Remote desktop detection error: %s", exc)

    return False


# ── Citrix Detection ─────────────────────────────────────────────────


def _check_citrix() -> bool:
    """Check if running in a Citrix session."""
    # Citrix environment variables
    citrix_vars = ["CITRIX_PRODUCT_ID", "CITRIX_SESSION_ID", "CLIENTNAME"]
    if any(os.environ.get(v) for v in citrix_vars):
        return True

    # Check for Citrix ICA client processes
    try:
        result = subprocess.run(
            ["tasklist"] if platform.system() == "Windows" else ["ps", "aux"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            output_lower = result.stdout.lower()
            if any(p in output_lower for p in ["wfica", "receiver", "citrix"]):
                return True
    except Exception:
        pass

    return False


# ── Cloud Workspace Detection ────────────────────────────────────────


def _check_cloud_workspace() -> bool:
    """Check if running in a cloud workspace."""
    provider = _detect_cloud_provider()
    return provider is not None


def _detect_cloud_provider() -> str | None:
    """Detect specific cloud workspace provider."""
    # AWS WorkSpaces
    if os.path.exists(r"C:\Program Files\Amazon\WorkSpacesConfig"):
        return "aws_workspaces"

    # Azure Virtual Desktop
    if os.environ.get("SESSIONNAME", "").startswith("RDP"):
        # Additional check for AVD-specific markers
        if os.environ.get("_AVD_"):
            return "azure_virtual_desktop"

    # Google Chrome Remote Desktop
    try:
        result = subprocess.run(
            ["tasklist"] if platform.system() == "Windows" else ["ps", "aux"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and "remoting_host" in result.stdout.lower():
            return "google_crd"
    except Exception:
        pass

    return None
