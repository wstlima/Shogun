"""Mado Browser Service — Playwright-based browser automation engine.

Provides secure, governed browser automation for Shogun agents and workflows.
All actions are validated against Torii posture and emitted as audit events.

Architecture:
    Shogun / Samurai → Torii Permission Layer → Mado → Playwright → Managed Chromium
"""

from __future__ import annotations

import asyncio
import logging
import re
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from shogun.config import settings

log = logging.getLogger("shogun.mado")

# ── Active browser contexts (in-memory registry) ────────────────
_active_browsers: dict[str, Any] = {}       # session_id → Browser
_active_contexts: dict[str, Any] = {}       # session_id → BrowserContext
_active_pages: dict[str, Any] = {}          # session_id → Page
_playwright_instance: Any = None


# ═══════════════════════════════════════════════════════════════
# CHROMIUM MANAGEMENT
# ═══════════════════════════════════════════════════════════════


async def get_chromium_status() -> dict[str, Any]:
    """Check if managed Chromium is installed and return status info."""
    import os

    installed = False
    version = None

    try:
        # Playwright stores browsers in a well-known cache directory
        browsers_path_env = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
        if browsers_path_env:
            browsers_path = Path(browsers_path_env)
        elif os.name == "nt":
            browsers_path = Path(os.environ.get("USERPROFILE", "")) / "AppData" / "Local" / "ms-playwright"
        else:
            browsers_path = Path.home() / ".cache" / "ms-playwright"

        if browsers_path.exists():
            chromium_dirs = [
                d for d in browsers_path.iterdir()
                if d.is_dir() and "chromium" in d.name.lower()
            ]
            if chromium_dirs:
                installed = True
                version = chromium_dirs[0].name
    except Exception as exc:
        log.debug("Chromium status check error: %s", exc)

    active_count = len(_active_contexts)
    return {
        "installed": installed,
        "version": version,
        "active_sessions": active_count,
        "mado_path": str(settings.mado_path),
        "profiles_path": str(settings.mado_path / "profiles"),
        "screenshots_path": str(settings.mado_path / "screenshots"),
        "downloads_path": str(settings.mado_path / "downloads"),
    }


async def install_chromium() -> dict[str, Any]:
    """Trigger Playwright Chromium installation (runs in thread pool)."""
    import asyncio
    import subprocess
    import sys

    def _do_install():
        return subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium", "--with-deps"],
            capture_output=True,
            text=True,
            timeout=300,
        )

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _do_install)
        success = result.returncode == 0
        log.info("Mado: Chromium install %s (rc=%d)", "succeeded" if success else "failed", result.returncode)
        return {
            "success": success,
            "stdout": result.stdout[-1000:] if result.stdout else "",
            "stderr": result.stderr[-1000:] if result.stderr else "",
        }
    except FileNotFoundError:
        return {"success": False, "error": "Python executable not found"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Installation timed out after 300 seconds"}
    except Exception as exc:
        return {"success": False, "error": str(exc)[:500]}


# ═══════════════════════════════════════════════════════════════
# BROWSER LIFECYCLE
# ═══════════════════════════════════════════════════════════════


async def _get_playwright():
    """Get or create the global Playwright instance."""
    global _playwright_instance
    if _playwright_instance is None:
        from playwright.async_api import async_playwright
        _playwright_instance = await async_playwright().start()
    return _playwright_instance


async def launch_browser(
    session_id: str,
    profile_name: str,
    mode: str = "headless",
) -> dict[str, Any]:
    """Launch a Playwright Chromium browser with an isolated profile.

    Args:
        session_id: UUID string identifying this session.
        profile_name: Directory name under mado/profiles/ for persistence.
        mode: "headless" or "visible".

    Returns:
        Status dict with launch result.
    """
    if session_id in _active_contexts:
        return {"status": "already_active", "session_id": session_id}

    try:
        pw = await _get_playwright()
        profile_path = settings.mado_path / "profiles" / _sanitize_name(profile_name)
        profile_path.mkdir(parents=True, exist_ok=True)

        downloads_path = settings.mado_path / "downloads" / _sanitize_name(profile_name)
        downloads_path.mkdir(parents=True, exist_ok=True)

        headless = mode == "headless"

        # Launch browser with persistent context for session persistence
        context = await pw.chromium.launch_persistent_context(
            user_data_dir=str(profile_path),
            headless=headless,
            accept_downloads=True,
            viewport={"width": 1280, "height": 720},
            user_agent="Shogun-Mado/1.0 (Browser Automation)",
            ignore_https_errors=False,
            java_script_enabled=True,
            locale="en-US",
        )

        # Get or create first page
        pages = context.pages
        page = pages[0] if pages else await context.new_page()

        _active_contexts[session_id] = context
        _active_pages[session_id] = page

        log.info("Mado: browser launched for session %s (profile=%s, mode=%s)",
                 session_id, profile_name, mode)

        # Audit event
        await _emit_browser_event(
            "browser.launch",
            f"Browser session launched: {profile_name} ({mode})",
            detail={"session_id": session_id, "profile": profile_name, "mode": mode},
        )

        return {"status": "launched", "session_id": session_id, "mode": mode}

    except Exception as exc:
        log.error("Mado: failed to launch browser for session %s: %s", session_id, exc)
        return {"status": "error", "error": str(exc)[:500]}


async def close_browser(session_id: str) -> dict[str, Any]:
    """Gracefully close a browser session."""
    context = _active_contexts.pop(session_id, None)
    _active_pages.pop(session_id, None)
    _active_browsers.pop(session_id, None)

    if context is None:
        return {"status": "not_found", "session_id": session_id}

    try:
        await context.close()
        log.info("Mado: browser closed for session %s", session_id)

        await _emit_browser_event(
            "browser.close",
            f"Browser session closed: {session_id}",
            detail={"session_id": session_id},
        )
        return {"status": "closed", "session_id": session_id}
    except Exception as exc:
        log.error("Mado: error closing browser for session %s: %s", session_id, exc)
        return {"status": "error", "error": str(exc)[:500]}


async def close_all_browsers() -> int:
    """Close all active browser sessions. Returns count closed."""
    session_ids = list(_active_contexts.keys())
    for sid in session_ids:
        await close_browser(sid)
    return len(session_ids)


def _get_page(session_id: str):
    """Get the active page for a session, raising ValueError if not found."""
    page = _active_pages.get(session_id)
    if page is None:
        raise ValueError(f"No active browser session: {session_id}. Launch a browser first.")
    return page


# ═══════════════════════════════════════════════════════════════
# BROWSER ACTIONS
# ═══════════════════════════════════════════════════════════════


async def navigate(
    session_id: str,
    url: str,
    wait_until: str = "domcontentloaded",
    domain_allowlist: list[str] | None = None,
) -> dict[str, Any]:
    """Navigate to a URL with domain validation."""
    # Domain validation
    if domain_allowlist:
        parsed = urlparse(url)
        domain = parsed.hostname or ""
        if not _domain_matches(domain, domain_allowlist):
            await _emit_browser_event(
                "browser.navigate_blocked",
                f"Navigation blocked: {domain} not in allowlist",
                detail={"url": url, "domain": domain, "allowlist": domain_allowlist},
                severity="warn",
            )
            return {"status": "blocked", "reason": f"Domain '{domain}' is not in the allowlist"}

    page = _get_page(session_id)
    try:
        response = await page.goto(url, wait_until=wait_until, timeout=30000)
        status_code = response.status if response else None
        title = await page.title()

        await _emit_browser_event(
            "browser.navigate",
            f"Navigated to {url}",
            detail={"session_id": session_id, "url": url, "status": status_code, "title": title},
        )

        return {
            "status": "ok",
            "url": page.url,
            "title": title,
            "status_code": status_code,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:500]}


async def extract_content(
    session_id: str,
    selector: str | None = None,
    extract_type: str = "text",
) -> dict[str, Any]:
    """Extract content from the current page.

    Args:
        selector: CSS selector (None = full page body).
        extract_type: "text", "html", "inner_text", or "table".
    """
    page = _get_page(session_id)
    try:
        if selector:
            element = await page.query_selector(selector)
            if element is None:
                return {"status": "not_found", "selector": selector}

            if extract_type == "html":
                content = await element.inner_html()
            elif extract_type == "inner_text":
                content = await element.inner_text()
            else:
                content = await element.text_content() or ""
        else:
            if extract_type == "html":
                content = await page.content()
            else:
                content = await page.inner_text("body")

        # Truncate for safety
        content = content[:50000] if content else ""

        await _emit_browser_event(
            "browser.extract",
            f"Extracted {extract_type} content ({len(content)} chars)",
            detail={"session_id": session_id, "selector": selector, "type": extract_type,
                    "length": len(content)},
        )

        return {
            "status": "ok",
            "content": content,
            "length": len(content),
            "url": page.url,
            "extract_type": extract_type,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:500]}


async def screenshot(
    session_id: str,
    full_page: bool = False,
    selector: str | None = None,
) -> dict[str, Any]:
    """Capture a screenshot of the current page.

    Returns the path to the saved screenshot file.
    """
    page = _get_page(session_id)
    try:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"mado_{session_id[:8]}_{timestamp}.png"
        output_path = settings.mado_path / "screenshots" / filename

        if selector:
            element = await page.query_selector(selector)
            if element is None:
                return {"status": "not_found", "selector": selector}
            await element.screenshot(path=str(output_path))
        else:
            await page.screenshot(path=str(output_path), full_page=full_page)

        await _emit_browser_event(
            "browser.screenshot",
            f"Screenshot captured: {filename}",
            detail={"session_id": session_id, "path": str(output_path),
                    "full_page": full_page, "url": page.url},
        )

        return {
            "status": "ok",
            "path": str(output_path),
            "filename": filename,
            "url": page.url,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:500]}


async def generate_pdf(session_id: str) -> dict[str, Any]:
    """Generate a PDF of the current page (headless only)."""
    page = _get_page(session_id)
    try:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"mado_{session_id[:8]}_{timestamp}.pdf"
        output_path = settings.mado_path / "downloads" / filename

        await page.pdf(path=str(output_path), format="A4", print_background=True)

        await _emit_browser_event(
            "browser.pdf",
            f"PDF generated: {filename}",
            detail={"session_id": session_id, "path": str(output_path), "url": page.url},
        )

        return {"status": "ok", "path": str(output_path), "filename": filename}
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:500]}


async def fill_form(
    session_id: str,
    fields: list[dict[str, str]],
) -> dict[str, Any]:
    """Fill form fields on the current page.

    Each field dict should have: {"selector": "...", "value": "..."}.
    Optional: {"type": "select" | "checkbox"} for non-text inputs.
    """
    page = _get_page(session_id)
    filled = 0
    errors = []

    for field in fields:
        selector = field.get("selector", "")
        value = field.get("value", "")
        field_type = field.get("type", "text")

        try:
            if field_type == "select":
                await page.select_option(selector, value)
            elif field_type == "checkbox":
                if value.lower() in ("true", "1", "yes"):
                    await page.check(selector)
                else:
                    await page.uncheck(selector)
            else:
                await page.fill(selector, value)
            filled += 1
        except Exception as exc:
            errors.append({"selector": selector, "error": str(exc)[:200]})

    await _emit_browser_event(
        "browser.form",
        f"Filled {filled}/{len(fields)} form fields",
        detail={"session_id": session_id, "filled": filled, "total": len(fields),
                "errors": errors, "url": page.url},
    )

    return {
        "status": "ok" if not errors else "partial",
        "filled": filled,
        "total": len(fields),
        "errors": errors,
    }


async def click_element(session_id: str, selector: str) -> dict[str, Any]:
    """Click an element on the current page."""
    page = _get_page(session_id)
    try:
        await page.click(selector, timeout=10000)

        await _emit_browser_event(
            "browser.click",
            f"Clicked element: {selector}",
            detail={"session_id": session_id, "selector": selector, "url": page.url},
        )

        return {"status": "ok", "selector": selector, "url": page.url}
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:500]}


async def execute_js(session_id: str, script: str) -> dict[str, Any]:
    """Execute JavaScript on the current page."""
    page = _get_page(session_id)
    try:
        result = await page.evaluate(script)

        await _emit_browser_event(
            "browser.execute_js",
            f"Executed JavaScript ({len(script)} chars)",
            detail={"session_id": session_id, "script_length": len(script), "url": page.url},
        )

        # Serialize result
        result_str = str(result)[:10000] if result is not None else None
        return {"status": "ok", "result": result_str}
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:500]}


async def wait_for_selector(
    session_id: str,
    selector: str,
    timeout: int = 10000,
    state: str = "visible",
) -> dict[str, Any]:
    """Wait for an element to appear on the page."""
    page = _get_page(session_id)
    try:
        await page.wait_for_selector(selector, timeout=timeout, state=state)
        return {"status": "ok", "selector": selector, "state": state}
    except Exception as exc:
        return {"status": "timeout", "selector": selector, "error": str(exc)[:500]}


async def upload_file(
    session_id: str,
    selector: str,
    file_path: str,
) -> dict[str, Any]:
    """Upload a file to a file input element."""
    page = _get_page(session_id)
    try:
        file_input = await page.query_selector(selector)
        if file_input is None:
            return {"status": "not_found", "selector": selector}

        await file_input.set_input_files(file_path)

        await _emit_browser_event(
            "browser.upload",
            f"Uploaded file: {Path(file_path).name}",
            detail={"session_id": session_id, "selector": selector,
                    "file": Path(file_path).name, "url": page.url},
        )

        return {"status": "ok", "file": Path(file_path).name}
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:500]}


async def download_file(
    session_id: str,
    profile_name: str,
) -> dict[str, Any]:
    """Wait for and save a download triggered by a previous action."""
    context = _active_contexts.get(session_id)
    if context is None:
        return {"status": "error", "error": "No active session"}

    page = _get_page(session_id)
    try:
        async with page.expect_download(timeout=30000) as download_info:
            pass  # The download should have been triggered by a click
        download = await download_info.value

        dest_dir = settings.mado_path / "downloads" / _sanitize_name(profile_name)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / download.suggested_filename

        await download.save_as(str(dest_path))

        await _emit_browser_event(
            "browser.download",
            f"Downloaded file: {download.suggested_filename}",
            detail={"session_id": session_id, "filename": download.suggested_filename,
                    "path": str(dest_path)},
        )

        return {
            "status": "ok",
            "filename": download.suggested_filename,
            "path": str(dest_path),
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:500]}


async def get_page_info(session_id: str) -> dict[str, Any]:
    """Get current page metadata (URL, title, viewport)."""
    page = _get_page(session_id)
    try:
        return {
            "status": "ok",
            "url": page.url,
            "title": await page.title(),
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:500]}


# ═══════════════════════════════════════════════════════════════
# SESSION PROFILE MANAGEMENT
# ═══════════════════════════════════════════════════════════════


def list_profiles() -> list[dict[str, Any]]:
    """List all browser profiles on disk."""
    profiles_dir = settings.mado_path / "profiles"
    if not profiles_dir.exists():
        return []

    profiles = []
    for p in sorted(profiles_dir.iterdir()):
        if p.is_dir():
            size = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
            profiles.append({
                "name": p.name,
                "path": str(p),
                "size_bytes": size,
                "active": p.name in [_active_contexts.get(sid) for sid in _active_contexts],
            })
    return profiles


def delete_profile(profile_name: str) -> bool:
    """Delete a browser profile directory from disk."""
    profile_path = settings.mado_path / "profiles" / _sanitize_name(profile_name)
    if profile_path.exists() and profile_path.is_dir():
        shutil.rmtree(profile_path, ignore_errors=True)
        return True
    return False


def list_screenshots() -> list[dict[str, Any]]:
    """List all screenshots in the screenshots directory."""
    screenshots_dir = settings.mado_path / "screenshots"
    if not screenshots_dir.exists():
        return []

    screenshots = []
    for f in sorted(screenshots_dir.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
            screenshots.append({
                "filename": f.name,
                "path": str(f),
                "size_bytes": f.stat().st_size,
                "created_at": datetime.fromtimestamp(
                    f.stat().st_mtime, tz=timezone.utc
                ).isoformat(),
            })
    return screenshots


# ═══════════════════════════════════════════════════════════════
# DOMAIN VALIDATION
# ═══════════════════════════════════════════════════════════════


def _domain_matches(domain: str, allowlist: list[str]) -> bool:
    """Check if a domain matches any entry in the allowlist.

    Supports wildcard prefixes: "*.example.com" matches "sub.example.com".
    """
    if not allowlist:
        return True  # Empty allowlist = allow all

    for pattern in allowlist:
        pattern = pattern.lower().strip()
        domain_lower = domain.lower()

        if pattern.startswith("*."):
            # Wildcard: match the suffix
            suffix = pattern[2:]
            if domain_lower == suffix or domain_lower.endswith("." + suffix):
                return True
        else:
            if domain_lower == pattern:
                return True

    return False


# ═══════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════


def _sanitize_name(name: str) -> str:
    """Sanitize a name for use as a filesystem directory name."""
    sanitized = re.sub(r"[^\w\-]", "_", name.lower().strip())
    return sanitized[:64] or "default"


async def _emit_browser_event(
    event_type: str,
    action: str,
    detail: dict | None = None,
    severity: str = "info",
) -> None:
    """Emit a browser action audit event via EventLogger."""
    try:
        from shogun.services.event_logger import EventLogger
        await EventLogger.emit_tool_event(
            event_type,
            action,
            tool_name="mado_browser",
            severity=severity,
            detail=detail,
        )
    except Exception:
        pass  # Non-fatal — don't break browser operations for logging
