"""Pydantic schemas for the Office App Mode API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


# ── Detection / Status ───────────────────────────────────────────────


class OfficeAppInfoResponse(BaseModel):
    """Detection status for a single Office application."""

    name: str
    installed: bool = False
    version: str = ""
    build: str = ""
    path: str = ""
    error: str = ""


class OfficeStatusResponse(BaseModel):
    """Overall Office App Mode status."""

    enabled: bool = False
    platform_supported: bool = False
    platform_name: str = ""
    minimum_posture: str = "guarded"
    message: str = ""
    excel: OfficeAppInfoResponse = Field(default_factory=lambda: OfficeAppInfoResponse(name="Excel"))
    word: OfficeAppInfoResponse = Field(default_factory=lambda: OfficeAppInfoResponse(name="Word"))
    powerpoint: OfficeAppInfoResponse = Field(default_factory=lambda: OfficeAppInfoResponse(name="PowerPoint"))
    outlook: OfficeAppInfoResponse = Field(default_factory=lambda: OfficeAppInfoResponse(name="Outlook"))
    folders_configured: bool = False
    process_status: dict[str, Any] = Field(default_factory=dict)


# ── Configuration ────────────────────────────────────────────────────


class OfficeFolderConfigSchema(BaseModel):
    """Approved folder paths."""

    input: str = ""
    output: str = ""
    templates: str = ""
    temp: str = ""


class ExcelConfigSchema(BaseModel):
    enabled: bool = True
    visible: bool = False
    allow_macros: bool = False
    allow_external_links: bool = False
    overwrite_originals: bool = False
    timeout_seconds: int = 60


class WordConfigSchema(BaseModel):
    enabled: bool = True
    visible: bool = False
    allow_macros: bool = False
    overwrite_originals: bool = False
    timeout_seconds: int = 60


class PowerPointConfigSchema(BaseModel):
    enabled: bool = True
    visible: bool = False
    allow_macros: bool = False
    overwrite_originals: bool = False
    timeout_seconds: int = 90


class OutlookConfigSchema(BaseModel):
    enabled: bool = True
    mode: Literal["draft_only", "confirmed_send", "approved_recipient_send"] = "draft_only"
    allow_send: bool = False
    require_confirmation: bool = True
    allow_external_recipients: bool = False
    allowed_recipient_domains: list[str] = Field(default_factory=list)
    timeout_seconds: int = 60


class OfficeSafetyConfigSchema(BaseModel):
    block_path_traversal: bool = True
    block_shortcuts: bool = True
    block_unc_paths: bool = True
    version_outputs: bool = True
    require_output_validation: bool = True
    max_file_size_mb: int = 100


class OfficeLoggingConfigSchema(BaseModel):
    enabled: bool = True
    level: Literal["minimal", "standard", "detailed"] = "detailed"


class OfficeConfigResponse(BaseModel):
    """Full Office configuration response."""

    enabled: bool = False
    minimum_posture: str = "guarded"
    folders: OfficeFolderConfigSchema = Field(default_factory=OfficeFolderConfigSchema)
    excel: ExcelConfigSchema = Field(default_factory=ExcelConfigSchema)
    word: WordConfigSchema = Field(default_factory=WordConfigSchema)
    powerpoint: PowerPointConfigSchema = Field(default_factory=PowerPointConfigSchema)
    outlook: OutlookConfigSchema = Field(default_factory=OutlookConfigSchema)
    safety: OfficeSafetyConfigSchema = Field(default_factory=OfficeSafetyConfigSchema)
    logging: OfficeLoggingConfigSchema = Field(default_factory=OfficeLoggingConfigSchema)
    output_retention_days: int = 30
    temp_cleanup_on_startup: bool = True


class OfficeConfigUpdate(BaseModel):
    """Partial update for Office configuration."""

    enabled: bool | None = None
    minimum_posture: str | None = None
    folders: OfficeFolderConfigSchema | None = None
    excel: ExcelConfigSchema | None = None
    word: WordConfigSchema | None = None
    powerpoint: PowerPointConfigSchema | None = None
    outlook: OutlookConfigSchema | None = None
    safety: OfficeSafetyConfigSchema | None = None
    logging: OfficeLoggingConfigSchema | None = None
    output_retention_days: int | None = None
    temp_cleanup_on_startup: bool | None = None


# ── Path Validation ──────────────────────────────────────────────────


class PathValidationRequest(BaseModel):
    """Request to validate a file path."""

    file_path: str
    purpose: Literal["read", "write", "template", "temp", "output"]


class PathValidationResponse(BaseModel):
    """Result of a path validation check."""

    valid: bool
    resolved_path: str = ""
    folder_type: str = ""
    extension: str = ""
    error: str = ""


# ── Tool Results ─────────────────────────────────────────────────────


class OfficeToolResult(BaseModel):
    """Standard result schema for Office tool operations."""

    status: Literal["success", "error", "blocked", "approval_required"]
    application: str = ""
    action: str = ""
    input_file: str = ""
    output_file: str = ""
    audit_id: str = ""
    duration_ms: int = 0
    message: str = ""
    data: Any = None
    error: str = ""
    suggested_next_step: str = ""
