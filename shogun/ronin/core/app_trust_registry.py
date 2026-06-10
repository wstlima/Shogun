"""Application Trust Registry — controls what apps Ronin may interact with.

Four trust levels:
  TRUSTED    → Full interaction (VS Code, Notepad, Calculator)
  RESTRICTED → Monitored interaction (Chrome, Excel)
  SENSITIVE  → Requires approval (Outlook, SAP, Salesforce)
  FORBIDDEN  → Blocked always — hard safety rail (Password Managers, Banking)

The Posture Guard evaluates: Agent + Posture + App Trust Level = Decision
"""

from __future__ import annotations

import fnmatch
import logging
import os
import platform
from pathlib import Path
from typing import Any

from shogun.ronin.policies.ronin_policy_schema import AppTrustEntry, AppTrustLevel

log = logging.getLogger("shogun.ronin.app_trust")

# ── Registry ─────────────────────────────────────────────────────────

_trust_entries: list[AppTrustEntry] = []


# ── Built-in defaults ────────────────────────────────────────────────

_DEFAULT_TRUST: list[dict[str, Any]] = [
    # ── TRUSTED ──
    {"process": "code.exe", "name": "Visual Studio Code", "trust_level": "trusted", "platform": "windows"},
    {"process": "Code", "name": "Visual Studio Code", "trust_level": "trusted", "platform": "macos"},
    {"process": "code", "name": "Visual Studio Code", "trust_level": "trusted", "platform": "linux"},
    {"process": "notepad.exe", "name": "Notepad", "trust_level": "trusted", "platform": "windows"},
    {"process": "calc.exe", "name": "Calculator", "trust_level": "trusted", "platform": "windows"},
    {"process": "Calculator", "name": "Calculator", "trust_level": "trusted", "platform": "macos"},
    {"process": "gnome-calculator", "name": "Calculator", "trust_level": "trusted", "platform": "linux"},
    {"process": "explorer.exe", "name": "File Explorer", "trust_level": "trusted", "platform": "windows"},
    {"process": "Finder", "name": "Finder", "trust_level": "trusted", "platform": "macos"},
    {"process": "nautilus", "name": "Files", "trust_level": "trusted", "platform": "linux"},
    {"process": "Terminal", "name": "Terminal", "trust_level": "trusted", "platform": "macos"},
    {"process": "WindowsTerminal.exe", "name": "Windows Terminal", "trust_level": "trusted", "platform": "windows"},
    {"process": "gnome-terminal", "name": "Terminal", "trust_level": "trusted", "platform": "linux"},
    {"process": "python.exe", "name": "Python", "trust_level": "trusted", "platform": "windows"},
    {"process": "python3", "name": "Python", "trust_level": "trusted", "platform": "all"},

    # ── RESTRICTED ──
    {"process": "chrome.exe", "name": "Google Chrome", "trust_level": "restricted", "platform": "windows"},
    {"process": "Google Chrome", "name": "Google Chrome", "trust_level": "restricted", "platform": "macos"},
    {"process": "google-chrome", "name": "Google Chrome", "trust_level": "restricted", "platform": "linux"},
    {"process": "firefox.exe", "name": "Firefox", "trust_level": "restricted", "platform": "windows"},
    {"process": "firefox", "name": "Firefox", "trust_level": "restricted", "platform": "all"},
    {"process": "msedge.exe", "name": "Microsoft Edge", "trust_level": "restricted", "platform": "windows"},
    {"process": "EXCEL.EXE", "name": "Microsoft Excel", "trust_level": "restricted", "platform": "windows"},
    {"process": "POWERPNT.EXE", "name": "Microsoft PowerPoint", "trust_level": "restricted", "platform": "windows"},
    {"process": "WINWORD.EXE", "name": "Microsoft Word", "trust_level": "restricted", "platform": "windows"},
    {"process": "slack.exe", "name": "Slack", "trust_level": "restricted", "platform": "windows"},
    {"process": "Slack", "name": "Slack", "trust_level": "restricted", "platform": "macos"},
    {"process": "Discord.exe", "name": "Discord", "trust_level": "restricted", "platform": "windows"},

    # ── SENSITIVE ──
    {"process": "OUTLOOK.EXE", "name": "Microsoft Outlook", "trust_level": "sensitive", "platform": "windows"},
    {"process": "Microsoft Outlook", "name": "Microsoft Outlook", "trust_level": "sensitive", "platform": "macos"},
    {"process": "Teams.exe", "name": "Microsoft Teams", "trust_level": "sensitive", "platform": "windows"},
    {"process": "Microsoft Teams", "name": "Microsoft Teams", "trust_level": "sensitive", "platform": "macos"},
    {"process": "saplogon.exe", "name": "SAP Logon", "trust_level": "sensitive", "platform": "windows"},
    {"process_pattern": "*salesforce*", "name": "Salesforce", "trust_level": "sensitive", "platform": "all"},
    {"process_pattern": "*sap*", "name": "SAP Application", "trust_level": "sensitive", "platform": "all"},
    {"process_pattern": "*erp*", "name": "ERP Application", "trust_level": "sensitive", "platform": "all"},
    {"process_pattern": "*crm*", "name": "CRM Application", "trust_level": "sensitive", "platform": "all"},

    # ── FORBIDDEN ──
    {"process": "1Password.exe", "name": "1Password", "trust_level": "forbidden", "platform": "windows"},
    {"process": "1Password", "name": "1Password", "trust_level": "forbidden", "platform": "macos"},
    {"process": "Bitwarden.exe", "name": "Bitwarden", "trust_level": "forbidden", "platform": "windows"},
    {"process": "KeePass.exe", "name": "KeePass", "trust_level": "forbidden", "platform": "windows"},
    {"process": "KeePassXC", "name": "KeePassXC", "trust_level": "forbidden", "platform": "all"},
    {"process": "LastPass.exe", "name": "LastPass", "trust_level": "forbidden", "platform": "windows"},
    {"process": "Dashlane.exe", "name": "Dashlane", "trust_level": "forbidden", "platform": "windows"},
    {"process_pattern": "*wallet*", "name": "Crypto Wallet", "trust_level": "forbidden", "platform": "all"},
    {"process_pattern": "*banking*", "name": "Banking Application", "trust_level": "forbidden", "platform": "all"},
    {"process_pattern": "*keychain*", "name": "Keychain Access", "trust_level": "forbidden", "platform": "all"},
    {"process": "Keychain Access", "name": "Keychain Access", "trust_level": "forbidden", "platform": "macos"},
    {"process": "credentialmanager", "name": "Credential Manager", "trust_level": "forbidden", "platform": "windows"},
    {"process_pattern": "*password*", "name": "Password Manager", "trust_level": "forbidden", "platform": "all"},
]


def _seed_defaults() -> None:
    """Populate the registry with built-in defaults."""
    current_os = _current_platform()
    for entry_data in _DEFAULT_TRUST:
        entry_platform = entry_data.get("platform", "all")
        if entry_platform != "all" and entry_platform != current_os:
            continue  # Skip entries for other platforms
        _trust_entries.append(AppTrustEntry(
            process=entry_data.get("process"),
            process_pattern=entry_data.get("process_pattern"),
            name=entry_data["name"],
            trust_level=AppTrustLevel(entry_data["trust_level"]),
            platform=entry_platform,
        ))


def _current_platform() -> str:
    """Get current platform as windows/macos/linux."""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    if system == "windows":
        return "windows"
    return "linux"


# Seed on import
_seed_defaults()


# ── Public API ───────────────────────────────────────────────────────


def get_trust_level(process_name: str) -> AppTrustLevel:
    """Look up the trust level for a process name.

    Checks exact matches first, then glob patterns.
    Unknown processes default to RESTRICTED.
    """
    if not process_name:
        return AppTrustLevel.RESTRICTED

    process_lower = process_name.lower()

    # Pass 1: exact match
    for entry in _trust_entries:
        if entry.process and entry.process.lower() == process_lower:
            return entry.trust_level

    # Pass 2: glob pattern match
    for entry in _trust_entries:
        if entry.process_pattern and fnmatch.fnmatch(process_lower, entry.process_pattern.lower()):
            return entry.trust_level

    log.debug("Ronin: process '%s' not in trust registry — defaulting to RESTRICTED", process_name)
    return AppTrustLevel.RESTRICTED


def is_forbidden(process_name: str) -> bool:
    """Quick check: is this process FORBIDDEN?"""
    return get_trust_level(process_name) == AppTrustLevel.FORBIDDEN


def get_all_entries() -> list[AppTrustEntry]:
    """Return all trust registry entries."""
    return list(_trust_entries)


def get_entries_by_level(level: AppTrustLevel) -> list[AppTrustEntry]:
    """Return entries at a specific trust level."""
    return [e for e in _trust_entries if e.trust_level == level]


def add_entry(entry: AppTrustEntry) -> None:
    """Add a new entry to the trust registry."""
    _trust_entries.append(entry)
    log.info("Ronin: added app trust entry: %s → %s", entry.name, entry.trust_level.value)


def remove_entry(process: str) -> bool:
    """Remove an entry by process name. Returns True if found."""
    for i, entry in enumerate(_trust_entries):
        if entry.process and entry.process.lower() == process.lower():
            _trust_entries.pop(i)
            log.info("Ronin: removed app trust entry: %s", process)
            return True
    return False


def update_trust_level(process: str, level: AppTrustLevel) -> bool:
    """Update the trust level of an existing entry."""
    for entry in _trust_entries:
        if entry.process and entry.process.lower() == process.lower():
            old_level = entry.trust_level
            entry.trust_level = level
            log.info("Ronin: updated trust level for %s: %s → %s",
                     process, old_level.value, level.value)
            return True
    return False
