"""Mado Browser Service — Playwright-based browser automation engine.

Provides secure, governed browser automation for Shogun agents and workflows.
All actions are validated against Torii posture and emitted as audit events.

Architecture:
    Shogun / Samurai → Torii Permission Layer → Mado → Playwright → Managed Chromium
"""

from __future__ import annotations

import asyncio
import concurrent.futures
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

# Single-thread executor: Playwright's sync API binds to the thread where
# sync_playwright().start() was called.  Every subsequent Playwright call
# must happen on that SAME thread, so we pin all work to one worker.
_pw_executor = concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="mado-pw")


async def _run_in_pw_thread(fn, *args, **kwargs):
    """Run *fn* on the dedicated Playwright thread."""
    loop = asyncio.get_event_loop()
    if kwargs:
        import functools
        fn = functools.partial(fn, *args, **kwargs)
        args = ()
    return await loop.run_in_executor(_pw_executor, fn, *args)


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
        steps = []

        # Step 1: Ensure playwright Python package is installed
        try:
            import playwright  # noqa: F401
            steps.append({"step": "pip_install", "status": "skipped", "message": "playwright already installed"})
        except ImportError:
            log.info("Mado: Installing playwright Python package...")
            pip_result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "playwright>=1.44.0"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if pip_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Failed to install playwright package: {pip_result.stderr[-500:]}",
                    "steps": [{"step": "pip_install", "status": "failed", "stderr": pip_result.stderr[-500:]}],
                }
            steps.append({"step": "pip_install", "status": "ok", "message": "playwright package installed"})

        # Step 2: Install Chromium browser
        log.info("Mado: Downloading and installing Chromium browser...")
        browser_result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            capture_output=True,
            text=True,
            timeout=300,
        )
        if browser_result.returncode != 0:
            steps.append({"step": "chromium_install", "status": "failed", "stderr": browser_result.stderr[-500:]})
            return {
                "success": False,
                "error": f"Chromium install failed: {browser_result.stderr[-500:]}",
                "steps": steps,
            }

        steps.append({"step": "chromium_install", "status": "ok", "message": "Chromium browser installed"})
        log.info("Mado: Chromium browser installed successfully")
        return {
            "success": True,
            "stdout": browser_result.stdout[-500:] if browser_result.stdout else "",
            "steps": steps,
        }

    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, _do_install)
        log.info("Mado: Install result — success=%s", result.get("success"))
        return result
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Installation timed out (5 minutes). Check your internet connection."}
    except Exception as exc:
        return {"success": False, "error": str(exc)[:500]}


# ═══════════════════════════════════════════════════════════════
# BROWSER LIFECYCLE  (sync Playwright in thread pool)
# ═══════════════════════════════════════════════════════════════


def _get_playwright_sync():
    """Get or create the global *sync* Playwright instance.

    Called from within the thread pool — never from the async event loop.
    On Windows + Python 3.14 the async Playwright API fails because
    SelectorEventLoop does not support ``subprocess_exec``.  The sync API
    uses plain ``subprocess.Popen`` which works everywhere.
    """
    global _playwright_instance
    if _playwright_instance is None:
        from playwright.sync_api import sync_playwright
        _playwright_instance = sync_playwright().start()
        log.info("Mado: sync Playwright instance started")
    return _playwright_instance


async def launch_browser(
    session_id: str,
    profile_name: str,
    mode: str = "headless",
) -> dict[str, Any]:
    """Launch a Playwright Chromium browser with an isolated profile.

    Uses the *sync* Playwright API inside a thread to work around the
    Windows / Python 3.14 asyncio subprocess limitation.
    """
    if session_id in _active_contexts:
        return {"status": "already_active", "session_id": session_id}

    def _do_launch():
        pw = _get_playwright_sync()
        profile_path = settings.mado_path / "profiles" / _sanitize_name(profile_name)
        profile_path.mkdir(parents=True, exist_ok=True)

        downloads_path = settings.mado_path / "downloads" / _sanitize_name(profile_name)
        downloads_path.mkdir(parents=True, exist_ok=True)

        headless = mode == "headless"

        context = pw.chromium.launch_persistent_context(
            user_data_dir=str(profile_path),
            headless=headless,
            accept_downloads=True,
            viewport={"width": 1280, "height": 720},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/136.0.0.0 Safari/537.36"
            ),
            ignore_https_errors=False,
            java_script_enabled=True,
            locale="en-US",
            timezone_id="America/New_York",
            geolocation={"latitude": 40.7128, "longitude": -74.0060},
            permissions=["geolocation"],
            args=[
                "--disable-blink-features=AutomationControlled",
            ],
        )

        pages = context.pages
        page = pages[0] if pages else context.new_page()

        _active_contexts[session_id] = context
        _active_pages[session_id] = page
        return True

    try:
        await _run_in_pw_thread(_do_launch)

        log.info("Mado: browser launched for session %s (profile=%s, mode=%s)",
                 session_id, profile_name, mode)

        await _emit_browser_event(
            "browser.launch",
            f"Browser session launched: {profile_name} ({mode})",
            detail={"session_id": session_id, "profile": profile_name, "mode": mode},
        )

        return {"status": "launched", "session_id": session_id, "mode": mode}

    except Exception as exc:
        log.error("Mado: failed to launch browser for session %s: %s", session_id, exc, exc_info=True)
        return {"status": "error", "error": str(exc)[:500]}


async def close_browser(session_id: str) -> dict[str, Any]:
    """Gracefully close a browser session."""
    context = _active_contexts.pop(session_id, None)
    _active_pages.pop(session_id, None)
    _active_browsers.pop(session_id, None)

    if context is None:
        return {"status": "not_found", "session_id": session_id}

    try:
        await _run_in_pw_thread(context.close)
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

    def _do_nav():
        response = page.goto(url, wait_until=wait_until, timeout=30000)
        status_code = response.status if response else None

        # Auto-handle Google/EU cookie consent walls
        current_url = page.url
        if "consent.google" in current_url or "consent.youtube" in current_url:
            log.info("Mado: Consent wall detected at %s — auto-accepting", current_url)
            try:
                # Try various consent button selectors
                for btn_selector in [
                    "button[aria-label*='Accept']",
                    "button:has-text('Accept all')",
                    "button:has-text('I agree')",
                    "form[action*='consent'] button",
                    "#L2AGLb",  # Google's "Accept all" button ID
                ]:
                    btn = page.query_selector(btn_selector)
                    if btn:
                        btn.click()
                        page.wait_for_load_state("domcontentloaded", timeout=15000)
                        log.info("Mado: Consent accepted, now at %s", page.url)
                        break
            except Exception as consent_exc:
                log.warning("Mado: Could not auto-accept consent: %s", consent_exc)

        title = page.title()
        return {"url": page.url, "title": title, "status_code": status_code}

    try:
        result = await _run_in_pw_thread(_do_nav)

        await _emit_browser_event(
            "browser.navigate",
            f"Navigated to {url}",
            detail={"session_id": session_id, "url": url,
                    "status": result["status_code"], "title": result["title"]},
        )

        return {"status": "ok", **result}
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

    def _do_extract():
        parts = []
        if selector:
            elements = page.query_selector_all(selector)
            if not elements:
                log.warning("Mado: selector '%s' matched 0 elements on %s, falling back to body",
                            selector, page.url)
                body_text = page.inner_text("body")
                body_text = body_text[:50000] if body_text else ""
                return {
                    "status": "fallback",
                    "content": body_text,
                    "length": len(body_text),
                    "url": page.url,
                    "extract_type": extract_type,
                    "note": f"Selector '{selector}' matched no elements; extracted full page body instead.",
                }

            for el in elements:
                try:
                    if extract_type == "html":
                        text = el.inner_html()
                    elif extract_type == "inner_text":
                        text = el.inner_text()
                    else:
                        text = el.text_content() or ""
                    text = text.strip()
                    if text:
                        parts.append(text)
                except Exception:
                    continue

            content = "\n".join(parts)
        else:
            if extract_type == "html":
                content = page.content()
            else:
                content = page.inner_text("body")

        content = content[:50000] if content else ""
        return {
            "status": "ok",
            "content": content,
            "length": len(content),
            "url": page.url,
            "extract_type": extract_type,
            "elements_found": len(parts) if selector else None,
        }

    try:
        result = await _run_in_pw_thread(_do_extract)

        await _emit_browser_event(
            "browser.extract",
            f"Extracted {extract_type} content ({result['length']} chars)",
            detail={"session_id": session_id, "selector": selector, "type": extract_type,
                    "length": result["length"], "elements_found": result.get("elements_found")},
        )

        return result
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:500]}


async def screenshot(
    session_id: str,
    full_page: bool = False,
    selector: str | None = None,
) -> dict[str, Any]:
    """Capture a screenshot of the current page."""
    page = _get_page(session_id)

    def _do_screenshot():
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"mado_{session_id[:8]}_{timestamp}.png"
        output_path = settings.mado_path / "screenshots" / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if selector:
            element = page.query_selector(selector)
            if element is None:
                return {"status": "not_found", "selector": selector}
            element.screenshot(path=str(output_path))
        else:
            page.screenshot(path=str(output_path), full_page=full_page)

        return {"status": "ok", "path": str(output_path), "filename": filename, "url": page.url}

    try:
        result = await _run_in_pw_thread(_do_screenshot)
        if result.get("status") == "ok":
            await _emit_browser_event(
                "browser.screenshot",
                f"Screenshot captured: {result['filename']}",
                detail={"session_id": session_id, "path": result["path"],
                        "full_page": full_page, "url": result.get("url")},
            )
        return result
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:500]}


async def generate_pdf(session_id: str) -> dict[str, Any]:
    """Generate a PDF of the current page (headless only)."""
    page = _get_page(session_id)

    def _do_pdf():
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"mado_{session_id[:8]}_{timestamp}.pdf"
        output_path = settings.mado_path / "downloads" / filename
        page.pdf(path=str(output_path), format="A4", print_background=True)
        return {"status": "ok", "path": str(output_path), "filename": filename}

    try:
        result = await _run_in_pw_thread(_do_pdf)
        await _emit_browser_event(
            "browser.pdf",
            f"PDF generated: {result['filename']}",
            detail={"session_id": session_id, "path": result["path"], "url": page.url},
        )
        return result
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:500]}


async def fill_form(
    session_id: str,
    fields: list[dict[str, str]],
) -> dict[str, Any]:
    """Fill form fields on the current page."""
    page = _get_page(session_id)

    def _do_fill():
        filled = 0
        errors = []
        for field in fields:
            sel = field.get("selector", "")
            value = field.get("value", "")
            field_type = field.get("type", "text")
            try:
                if field_type == "select":
                    page.select_option(sel, value)
                elif field_type == "checkbox":
                    if value.lower() in ("true", "1", "yes"):
                        page.check(sel)
                    else:
                        page.uncheck(sel)
                else:
                    page.fill(sel, value)
                filled += 1
            except Exception as exc:
                errors.append({"selector": sel, "error": str(exc)[:200]})
        return {"filled": filled, "errors": errors}

    try:
        result = await _run_in_pw_thread(_do_fill)
        await _emit_browser_event(
            "browser.form",
            f"Filled {result['filled']}/{len(fields)} form fields",
            detail={"session_id": session_id, "filled": result["filled"],
                    "total": len(fields), "errors": result["errors"], "url": page.url},
        )
        return {
            "status": "ok" if not result["errors"] else "partial",
            "filled": result["filled"],
            "total": len(fields),
            "errors": result["errors"],
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:500]}


async def click_element(session_id: str, selector: str) -> dict[str, Any]:
    """Click an element on the current page."""
    page = _get_page(session_id)

    def _do_click():
        page.click(selector, timeout=10000)
        return {"url": page.url}

    try:
        result = await _run_in_pw_thread(_do_click)
        await _emit_browser_event(
            "browser.click",
            f"Clicked element: {selector}",
            detail={"session_id": session_id, "selector": selector, "url": result["url"]},
        )
        return {"status": "ok", "selector": selector, "url": result["url"]}
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:500]}


async def execute_js(session_id: str, script: str) -> dict[str, Any]:
    """Execute JavaScript on the current page."""
    page = _get_page(session_id)

    def _do_eval():
        return page.evaluate(script)

    try:
        result = await _run_in_pw_thread(_do_eval)
        await _emit_browser_event(
            "browser.execute_js",
            f"Executed JavaScript ({len(script)} chars)",
            detail={"session_id": session_id, "script_length": len(script), "url": page.url},
        )
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
        await _run_in_pw_thread(page.wait_for_selector, selector, timeout=timeout, state=state)
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

    def _do_upload():
        file_input = page.query_selector(selector)
        if file_input is None:
            return {"status": "not_found", "selector": selector}
        file_input.set_input_files(file_path)
        return {"status": "ok", "file": Path(file_path).name}

    try:
        result = await _run_in_pw_thread(_do_upload)
        if result.get("status") == "ok":
            await _emit_browser_event(
                "browser.upload",
                f"Uploaded file: {result['file']}",
                detail={"session_id": session_id, "selector": selector,
                        "file": result["file"], "url": page.url},
            )
        return result
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

    def _do_download():
        with page.expect_download(timeout=30000) as download_info:
            pass
        download = download_info.value
        dest_dir = settings.mado_path / "downloads" / _sanitize_name(profile_name)
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / download.suggested_filename
        download.save_as(str(dest_path))
        return {
            "status": "ok",
            "filename": download.suggested_filename,
            "path": str(dest_path),
        }

    try:
        result = await _run_in_pw_thread(_do_download)
        await _emit_browser_event(
            "browser.download",
            f"Downloaded file: {result['filename']}",
            detail={"session_id": session_id, "filename": result["filename"],
                    "path": result["path"]},
        )
        return result
    except Exception as exc:
        return {"status": "error", "error": str(exc)[:500]}


async def get_page_info(session_id: str) -> dict[str, Any]:
    """Get current page metadata (URL, title, viewport)."""
    page = _get_page(session_id)

    def _do_info():
        return {"status": "ok", "url": page.url, "title": page.title()}

    try:
        return await _run_in_pw_thread(_do_info)
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
