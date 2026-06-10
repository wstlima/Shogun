"""Vision Controller — dual-mode screen interpretation.

1. OpenCV template matching — fast, deterministic, for known UI elements
2. Vision LLM call — uses agent's configured model for complex screen reading

Returns confidence score; refuses to act below threshold (default 0.8).
"""

from __future__ import annotations

import logging
from typing import Any

from shogun.ronin.desktop.image_matcher import match_template, MatchResult
from shogun.ronin.policies.ronin_policy_schema import (
    RoninAction,
    RoninActionStatus,
    RoninResult,
)

log = logging.getLogger("shogun.ronin.desktop.vision")

_DEFAULT_THRESHOLD = 0.8


async def locate_image(action: RoninAction) -> RoninResult:
    """Locate a UI element on screen using template matching.

    target: path to the template image file
    metadata.threshold: confidence threshold (default 0.8)
    """
    template_path = action.target
    if not template_path:
        return RoninResult(
            status=RoninActionStatus.FAILED,
            action_type="desktop.locate_image",
            error="No template image path provided in action.target",
        )

    threshold = action.metadata.get("threshold", _DEFAULT_THRESHOLD) if action.metadata else _DEFAULT_THRESHOLD

    # Take a fresh screenshot for matching
    try:
        from shogun.ronin.desktop.screenshot_controller import take_screenshot_raw
        screenshot_path = await take_screenshot_raw(prefix="vision")
        if not screenshot_path:
            return RoninResult(
                status=RoninActionStatus.FAILED,
                action_type="desktop.locate_image",
                error="Failed to capture screenshot for matching",
            )
    except Exception as exc:
        return RoninResult(
            status=RoninActionStatus.FAILED,
            action_type="desktop.locate_image",
            error=f"Screenshot failed: {exc}",
        )

    # Run template matching
    result = match_template(screenshot_path, template_path, threshold=threshold)

    if result.found:
        return RoninResult(
            status=RoninActionStatus.SUCCESS,
            action_type="desktop.locate_image",
            target=template_path,
            confidence=result.confidence,
            result_data={
                "found": True,
                "x": result.x,
                "y": result.y,
                "center_x": result.center_x,
                "center_y": result.center_y,
                "width": result.width,
                "height": result.height,
                "confidence": result.confidence,
                "screenshot": screenshot_path,
            },
        )

    return RoninResult(
        status=RoninActionStatus.LOW_CONFIDENCE if result.confidence > 0 else RoninActionStatus.TARGET_NOT_FOUND,
        action_type="desktop.locate_image",
        target=template_path,
        confidence=result.confidence,
        error=f"Template not found (best confidence: {result.confidence:.3f}, threshold: {threshold})",
        result_data={"screenshot": screenshot_path},
    )


async def read_screen(action: RoninAction) -> RoninResult:
    """Interpret screen contents using vision LLM.

    target: optional region as "x,y,w,h" or empty for full screen
    value: the question/prompt to ask about the screen content
    metadata.model: optional model override (uses agent's default if not set)
    """
    prompt = action.value or "Describe what you see on the screen."

    # Take a screenshot
    try:
        region = None
        if action.target and "," in action.target:
            parts = action.target.split(",")
            if len(parts) == 4:
                region = {
                    "left": int(parts[0]),
                    "top": int(parts[1]),
                    "width": int(parts[2]),
                    "height": int(parts[3]),
                }

        from shogun.ronin.desktop.screenshot_controller import take_screenshot_raw
        screenshot_path = await take_screenshot_raw(prefix="vision_read", region=region)
        if not screenshot_path:
            return RoninResult(
                status=RoninActionStatus.FAILED,
                action_type="desktop.read_screen",
                error="Failed to capture screenshot",
            )
    except Exception as exc:
        return RoninResult(
            status=RoninActionStatus.FAILED,
            action_type="desktop.read_screen",
            error=f"Screenshot failed: {exc}",
        )

    # Try vision LLM interpretation
    try:
        description = await _vision_llm_interpret(screenshot_path, prompt, action.metadata)
        if description:
            return RoninResult(
                status=RoninActionStatus.SUCCESS,
                action_type="desktop.read_screen",
                result_data={
                    "description": description,
                    "screenshot": screenshot_path,
                    "method": "vision_llm",
                },
            )
    except Exception as exc:
        log.warning("Ronin: vision LLM failed, returning screenshot only: %s", exc)

    # Fallback: return screenshot path without interpretation
    return RoninResult(
        status=RoninActionStatus.SUCCESS,
        action_type="desktop.read_screen",
        result_data={
            "description": "(Vision LLM unavailable — screenshot captured)",
            "screenshot": screenshot_path,
            "method": "screenshot_only",
        },
    )


async def _vision_llm_interpret(
    screenshot_path: str,
    prompt: str,
    metadata: dict[str, Any] | None = None,
) -> str | None:
    """Use the agent's vision-capable model to interpret a screenshot.

    This integrates with Shogun's model routing to find a vision-capable
    model and send the screenshot + prompt for analysis.
    """
    try:
        import base64
        from pathlib import Path

        # Read and encode the screenshot
        image_data = Path(screenshot_path).read_bytes()
        b64_image = base64.b64encode(image_data).decode("utf-8")

        # Try to use the Shogun model routing system
        from shogun.db.engine import async_session_factory
        from shogun.services.llm_router import route_llm_request

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"[Ronin Screen Reader] {prompt}"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{b64_image}"},
                    },
                ],
            }
        ]

        async with async_session_factory() as session:
            response = await route_llm_request(
                session=session,
                messages=messages,
                task_type="vision",
                max_tokens=500,
            )

        if response and hasattr(response, "content"):
            return response.content
        if isinstance(response, dict) and "content" in response:
            return response["content"]
        if isinstance(response, str):
            return response

        return None

    except ImportError:
        log.debug("Ronin: LLM router not available for vision")
        return None
    except Exception as exc:
        log.warning("Ronin: vision LLM interpretation failed: %s", exc)
        return None
