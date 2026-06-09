"""Mado Policy Guard — per-session security policy enforcement.

Each MadoSession can carry a ``security_policy`` JSON object that restricts
what operations the browser session may perform.  This guard is the **inner**
layer: the global Torii posture (``posture_guard.py``) is checked first, then
the per-session policy is applied on top.

Policy values
─────────────
  "allowed"            → action proceeds normally
  "blocked"            → action is denied with HTTP 403
  "approval_required"  → action is denied with HTTP 403 + "pending approval" note
                          (Phase 2 will add real-time WebSocket approval flow)
"""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

from fastapi import HTTPException

log = logging.getLogger("shogun.mado_policy_guard")

# Default policy (permissive) — matches the DB column default
DEFAULT_POLICY: dict[str, Any] = {
    "https_only": False,
    "downloads": "allowed",
    "uploads": "allowed",
    "form_submit": "allowed",
    "external_navigation": "allowed",
    "js_execution": "allowed",
    "max_page_loads": 0,
}


def _get_policy(session_record: Any) -> dict[str, Any]:
    """Safely extract the security_policy dict from a session ORM record."""
    raw = getattr(session_record, "security_policy", None)
    if not raw or not isinstance(raw, dict):
        return DEFAULT_POLICY.copy()
    # Merge with defaults so missing keys don't cause KeyErrors
    merged = DEFAULT_POLICY.copy()
    merged.update(raw)
    return merged


def _check_tri_state(policy_value: str, action_label: str) -> None:
    """Check a tri-state policy field (allowed / blocked / approval_required)."""
    if policy_value == "blocked":
        log.warning("[MadoPolicyGuard] %s BLOCKED by session policy", action_label)
        raise HTTPException(
            status_code=403,
            detail=f"Session security policy blocks {action_label}.",
        )
    elif policy_value == "approval_required":
        log.warning("[MadoPolicyGuard] %s requires approval (session policy)", action_label)
        raise HTTPException(
            status_code=403,
            detail=f"Session security policy requires approval for {action_label}. "
                   "This action has been logged. Approval workflows are coming in a future update.",
        )


def check_navigate_policy(session_record: Any, url: str) -> None:
    """Enforce navigation-related policies (HTTPS-only, external nav, page load cap)."""
    policy = _get_policy(session_record)

    # ── HTTPS-only ──
    if policy.get("https_only", False):
        parsed = urlparse(url)
        if parsed.scheme and parsed.scheme != "https":
            log.warning("[MadoPolicyGuard] HTTP blocked (https_only): %s", url)
            raise HTTPException(
                status_code=403,
                detail=f"Session policy enforces HTTPS-only. Cannot navigate to: {url}",
            )

    # ── External navigation ──
    if policy.get("external_navigation") == "blocked":
        allowlist = getattr(session_record, "domain_allowlist", None) or []
        if allowlist:
            parsed = urlparse(url)
            domain = parsed.hostname or ""
            if not any(
                domain == d or domain.endswith(f".{d}")
                for d in allowlist
            ):
                log.warning(
                    "[MadoPolicyGuard] External navigation blocked: %s not in %s",
                    domain, allowlist,
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"Session policy blocks external navigation. "
                           f"Domain '{domain}' is not in the session allowlist: {', '.join(allowlist)}",
                )

    # ── Page load cap ──
    max_loads = policy.get("max_page_loads", 0)
    if max_loads > 0:
        session_data = getattr(session_record, "session_data", None) or {}
        current_loads = session_data.get("page_load_count", 0)
        if current_loads >= max_loads:
            log.warning(
                "[MadoPolicyGuard] Page load limit reached: %d/%d",
                current_loads, max_loads,
            )
            raise HTTPException(
                status_code=403,
                detail=f"Session has reached its page load limit ({current_loads}/{max_loads}). "
                       "Create a new session or increase the limit.",
            )


def check_download_policy(session_record: Any) -> None:
    """Enforce download policy."""
    policy = _get_policy(session_record)
    _check_tri_state(policy.get("downloads", "allowed"), "file downloads")


def check_upload_policy(session_record: Any) -> None:
    """Enforce upload policy."""
    policy = _get_policy(session_record)
    _check_tri_state(policy.get("uploads", "allowed"), "file uploads")


def check_form_submit_policy(session_record: Any) -> None:
    """Enforce form submission policy."""
    policy = _get_policy(session_record)
    _check_tri_state(policy.get("form_submit", "allowed"), "form submission")


def check_js_execution_policy(session_record: Any) -> None:
    """Enforce JavaScript execution policy."""
    policy = _get_policy(session_record)
    if policy.get("js_execution") == "blocked":
        log.warning("[MadoPolicyGuard] JS execution BLOCKED by session policy")
        raise HTTPException(
            status_code=403,
            detail="Session security policy blocks JavaScript execution.",
        )


async def increment_page_load_count(session_record: Any, svc: Any) -> None:
    """Increment the page_load_count in session_data after a successful navigation."""
    try:
        session_data = dict(session_record.session_data or {})
        session_data["page_load_count"] = session_data.get("page_load_count", 0) + 1
        await svc.update_status(
            session_record.id,
            session_record.status,
            session_data=session_data,
        )
    except Exception:
        log.debug("Failed to increment page load counter", exc_info=True)
