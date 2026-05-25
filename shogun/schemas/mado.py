"""Mado schemas — request/response models for browser automation API."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import Field

from shogun.schemas.common import ShogunBase


# ═══════════════════════════════════════════════════════════════
# SESSION SCHEMAS
# ═══════════════════════════════════════════════════════════════


class MadoSessionCreate(ShogunBase):
    """Request body for creating a new browser session."""

    name: str = Field(..., min_length=1, max_length=255, description="Display name for the session")
    profile_name: str = Field(..., min_length=1, max_length=255, description="Unique filesystem profile name")
    agent_id: uuid.UUID | None = Field(None, description="Optional Samurai agent to link")
    browser_mode: str = Field("headless", description="Browser mode: 'headless' or 'visible'")
    domain_allowlist: list[str] = Field(default_factory=list, description="Allowed domains for this session")


class MadoSessionResponse(ShogunBase):
    """Response model for a browser session."""

    id: uuid.UUID
    name: str
    profile_name: str
    agent_id: uuid.UUID | None = None
    status: str
    browser_mode: str
    last_url: str | None = None
    domain_allowlist: list[str] = Field(default_factory=list)
    session_data: dict[str, Any] = Field(default_factory=dict)
    last_active_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class MadoSessionListItem(ShogunBase):
    """Lightweight session list item."""

    id: uuid.UUID
    name: str
    profile_name: str
    agent_id: uuid.UUID | None = None
    status: str
    browser_mode: str
    last_url: str | None = None
    last_active_at: datetime | None = None
    created_at: datetime


# ═══════════════════════════════════════════════════════════════
# ACTION SCHEMAS
# ═══════════════════════════════════════════════════════════════


class MadoNavigateRequest(ShogunBase):
    """Navigate to a URL."""

    url: str = Field(..., description="URL to navigate to")
    wait_until: str = Field("domcontentloaded", description="Wait strategy: 'load', 'domcontentloaded', 'networkidle'")


class MadoExtractRequest(ShogunBase):
    """Extract content from the page."""

    selector: str | None = Field(None, description="CSS selector (None for entire body)")
    extract_type: str = Field("text", description="'text', 'html', 'inner_text'")


class MadoScreenshotRequest(ShogunBase):
    """Capture a screenshot."""

    full_page: bool = Field(False, description="Capture full page or just viewport")
    selector: str | None = Field(None, description="CSS selector for element screenshot")


class MadoFillFormRequest(ShogunBase):
    """Fill form fields."""

    fields: list[dict[str, str]] = Field(
        ...,
        description="List of {selector, value, type?} dicts",
    )


class MadoClickRequest(ShogunBase):
    """Click an element."""

    selector: str = Field(..., description="CSS selector of element to click")


class MadoExecuteJsRequest(ShogunBase):
    """Execute JavaScript."""

    script: str = Field(..., description="JavaScript code to execute on the page")


class MadoUploadRequest(ShogunBase):
    """Upload a file to a form input."""

    selector: str = Field(..., description="CSS selector of file input")
    file_path: str = Field(..., description="Path to file to upload")


class MadoWaitRequest(ShogunBase):
    """Wait for a selector to appear."""

    selector: str = Field(..., description="CSS selector to wait for")
    timeout: int = Field(10000, description="Timeout in milliseconds")
    state: str = Field("visible", description="'visible', 'attached', 'detached', 'hidden'")


# ═══════════════════════════════════════════════════════════════
# STATUS SCHEMAS
# ═══════════════════════════════════════════════════════════════


class MadoStatusResponse(ShogunBase):
    """Mado subsystem status."""

    installed: bool
    version: str | None = None
    active_sessions: int = 0
    mado_path: str
    profiles_path: str
    screenshots_path: str
    downloads_path: str


class MadoActionResult(ShogunBase):
    """Generic action result wrapper."""

    status: str
    url: str | None = None
    title: str | None = None
    content: str | None = None
    path: str | None = None
    filename: str | None = None
    error: str | None = None
    detail: dict[str, Any] | None = None
