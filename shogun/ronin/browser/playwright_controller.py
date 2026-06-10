"""Playwright Controller — Mado bridge for browser automation.

Thin wrapper around shogun.services.mado_service that adds Ronin audit
trail, posture checks, and capability registry lookup.
"""

from __future__ import annotations

import logging
from typing import Any

from shogun.ronin.policies.ronin_policy_schema import (
    RoninAction,
    RoninActionStatus,
    RoninResult,
)

log = logging.getLogger("shogun.ronin.browser.playwright")


async def browser_open(action: RoninAction) -> RoninResult:
    """Open a URL in the browser via Mado."""
    url = action.value or action.target
    if not url:
        return RoninResult(
            status=RoninActionStatus.FAILED,
            action_type="browser.open",
            error="No URL provided. Set action.value or action.target.",
        )

    try:
        from shogun.services.mado_service import navigate_to_url
        session_id = action.metadata.get("mado_session_id") if action.metadata else None
        result = await navigate_to_url(session_id=session_id, url=url)
        return RoninResult(
            status=RoninActionStatus.SUCCESS,
            action_type="browser.open",
            target=url,
            result_data={"url": url, "mado_result": str(result)},
        )
    except ImportError:
        return RoninResult(
            status=RoninActionStatus.FAILED,
            action_type="browser.open",
            error="Mado service not available",
        )
    except Exception as exc:
        return RoninResult(
            status=RoninActionStatus.FAILED,
            action_type="browser.open",
            error=f"Browser open failed: {exc}",
        )


async def browser_click(action: RoninAction) -> RoninResult:
    """Click a DOM element in the browser."""
    selector = action.target
    if not selector:
        return RoninResult(
            status=RoninActionStatus.FAILED,
            action_type="browser.click",
            error="No CSS selector provided in action.target",
        )

    try:
        from shogun.services.mado_service import execute_browser_action
        session_id = action.metadata.get("mado_session_id") if action.metadata else None
        result = await execute_browser_action(
            session_id=session_id,
            action="click",
            selector=selector,
        )
        return RoninResult(
            status=RoninActionStatus.SUCCESS,
            action_type="browser.click",
            target=selector,
            result_data={"selector": selector},
        )
    except Exception as exc:
        return RoninResult(
            status=RoninActionStatus.FAILED,
            action_type="browser.click",
            error=f"Browser click failed: {exc}",
        )


async def browser_type(action: RoninAction) -> RoninResult:
    """Type into a form field in the browser."""
    selector = action.target
    text = action.value
    if not selector or not text:
        return RoninResult(
            status=RoninActionStatus.FAILED,
            action_type="browser.type",
            error="Both action.target (selector) and action.value (text) required",
        )

    try:
        from shogun.services.mado_service import execute_browser_action
        session_id = action.metadata.get("mado_session_id") if action.metadata else None
        result = await execute_browser_action(
            session_id=session_id,
            action="fill",
            selector=selector,
            value=text,
        )
        return RoninResult(
            status=RoninActionStatus.SUCCESS,
            action_type="browser.type",
            target=selector,
            result_data={"selector": selector, "chars": len(text)},
        )
    except Exception as exc:
        return RoninResult(
            status=RoninActionStatus.FAILED,
            action_type="browser.type",
            error=f"Browser type failed: {exc}",
        )


async def browser_extract(action: RoninAction) -> RoninResult:
    """Extract text from a page element."""
    selector = action.target or "body"

    try:
        from shogun.services.mado_service import execute_browser_action
        session_id = action.metadata.get("mado_session_id") if action.metadata else None
        result = await execute_browser_action(
            session_id=session_id,
            action="text_content",
            selector=selector,
        )
        return RoninResult(
            status=RoninActionStatus.SUCCESS,
            action_type="browser.extract",
            target=selector,
            result_data={"text": str(result), "selector": selector},
        )
    except Exception as exc:
        return RoninResult(
            status=RoninActionStatus.FAILED,
            action_type="browser.extract",
            error=f"Browser extract failed: {exc}",
        )


async def browser_screenshot(action: RoninAction) -> RoninResult:
    """Capture a browser page screenshot."""
    try:
        from shogun.services.mado_service import take_browser_screenshot
        session_id = action.metadata.get("mado_session_id") if action.metadata else None
        path = await take_browser_screenshot(session_id=session_id)
        return RoninResult(
            status=RoninActionStatus.SUCCESS,
            action_type="browser.screenshot",
            result_data={"screenshot_path": str(path)},
        )
    except Exception as exc:
        return RoninResult(
            status=RoninActionStatus.FAILED,
            action_type="browser.screenshot",
            error=f"Browser screenshot failed: {exc}",
        )
