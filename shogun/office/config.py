"""Office App Mode configuration — JSON-based, matches existing Shogun config pattern.

Provides Pydantic models for the Office configuration and load/save
functions that read/write ``configs/office_config.json``.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

log = logging.getLogger("shogun.office.config")

# Resolve project root (this file is at shogun/office/config.py)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_PATH = _PROJECT_ROOT / "configs" / "office_config.json"


# ── Per-Application Config ───────────────────────────────────────────


class ExcelConfig(BaseModel):
    """Configuration for the Excel adapter."""

    enabled: bool = True
    visible: bool = False
    allow_macros: bool = False
    allow_external_links: bool = False
    overwrite_originals: bool = False
    timeout_seconds: int = 60


class WordConfig(BaseModel):
    """Configuration for the Word adapter."""

    enabled: bool = True
    visible: bool = False
    allow_macros: bool = False
    overwrite_originals: bool = False
    timeout_seconds: int = 60


class PowerPointConfig(BaseModel):
    """Configuration for the PowerPoint adapter."""

    enabled: bool = True
    visible: bool = False
    allow_macros: bool = False
    overwrite_originals: bool = False
    timeout_seconds: int = 90


class OutlookConfig(BaseModel):
    """Configuration for the Outlook adapter."""

    enabled: bool = True
    mode: Literal["draft_only", "confirmed_send", "approved_recipient_send"] = "draft_only"
    allow_send: bool = False
    require_confirmation: bool = True
    allow_external_recipients: bool = False
    allowed_recipient_domains: list[str] = Field(default_factory=list)
    timeout_seconds: int = 60


# ── Safety Config ────────────────────────────────────────────────────


class OfficeSafetyConfig(BaseModel):
    """Cross-cutting safety settings."""

    block_path_traversal: bool = True
    block_shortcuts: bool = True
    block_unc_paths: bool = True
    version_outputs: bool = True
    require_output_validation: bool = True
    max_file_size_mb: int = 100


# ── Folder Config ────────────────────────────────────────────────────


class OfficeFolderConfig(BaseModel):
    """Approved folder paths for Office file operations."""

    input: str = ""
    output: str = ""
    templates: str = ""
    temp: str = ""


# ── Logging Config ───────────────────────────────────────────────────


class OfficeLoggingConfig(BaseModel):
    """Office-specific logging settings."""

    enabled: bool = True
    level: Literal["minimal", "standard", "detailed"] = "detailed"


# ── Root Config ──────────────────────────────────────────────────────


class OfficeAppConfig(BaseModel):
    """Root configuration model for Office App Mode.

    Serialized to ``configs/office_config.json``.
    """

    enabled: bool = False
    minimum_posture: Literal["guarded", "tactical", "campaign", "ronin"] = "guarded"

    folders: OfficeFolderConfig = Field(default_factory=OfficeFolderConfig)

    excel: ExcelConfig = Field(default_factory=ExcelConfig)
    word: WordConfig = Field(default_factory=WordConfig)
    powerpoint: PowerPointConfig = Field(default_factory=PowerPointConfig)
    outlook: OutlookConfig = Field(default_factory=OutlookConfig)

    safety: OfficeSafetyConfig = Field(default_factory=OfficeSafetyConfig)
    logging: OfficeLoggingConfig = Field(default_factory=OfficeLoggingConfig)

    # Output retention
    output_retention_days: int = 30
    temp_cleanup_on_startup: bool = True


# ── Load / Save ──────────────────────────────────────────────────────


def load_office_config(config_path: Path | None = None) -> OfficeAppConfig:
    """Load Office config from JSON file, or return defaults if not found."""
    path = config_path or _CONFIG_PATH
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return OfficeAppConfig(**data)
    except Exception as exc:
        log.warning("Failed to load office config from %s: %s — using defaults", path, exc)

    return OfficeAppConfig()


def save_office_config(config: OfficeAppConfig, config_path: Path | None = None) -> None:
    """Save Office config to JSON file."""
    path = config_path or _CONFIG_PATH
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(config.model_dump(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        log.info("Office config saved to %s", path)
    except Exception as exc:
        log.error("Failed to save office config to %s: %s", path, exc)
        raise
