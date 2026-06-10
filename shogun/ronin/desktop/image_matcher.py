"""Image Matcher — OpenCV-based template matching utility.

Used by VisionController for finding UI elements on screen.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

log = logging.getLogger("shogun.ronin.desktop.image_matcher")


@dataclass
class MatchResult:
    """Result of a template matching operation."""
    found: bool = False
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    confidence: float = 0.0
    center_x: int = 0
    center_y: int = 0


def match_template(
    screenshot_path: str,
    template_path: str,
    threshold: float = 0.8,
) -> MatchResult:
    """Find a template image within a screenshot using OpenCV template matching.

    Args:
        screenshot_path: Path to the full screenshot image.
        template_path: Path to the template image to locate.
        threshold: Minimum confidence score (0.0-1.0).

    Returns a MatchResult with location and confidence.
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        log.warning("Ronin: opencv-python-headless not installed — image matching unavailable")
        return MatchResult()

    try:
        # Read images
        screenshot = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)

        if screenshot is None:
            log.error("Ronin: could not read screenshot: %s", screenshot_path)
            return MatchResult()
        if template is None:
            log.error("Ronin: could not read template: %s", template_path)
            return MatchResult()

        # Template matching
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        h, w = template.shape[:2]
        confidence = float(max_val)

        if confidence >= threshold:
            x, y = max_loc
            return MatchResult(
                found=True,
                x=x,
                y=y,
                width=w,
                height=h,
                confidence=confidence,
                center_x=x + w // 2,
                center_y=y + h // 2,
            )

        log.debug(
            "Ronin: template match below threshold — confidence=%.3f threshold=%.3f",
            confidence, threshold,
        )
        return MatchResult(confidence=confidence)

    except Exception as exc:
        log.error("Ronin: template matching failed: %s", exc)
        return MatchResult()


def match_all(
    screenshot_path: str,
    template_path: str,
    threshold: float = 0.8,
    max_results: int = 10,
) -> list[MatchResult]:
    """Find all occurrences of a template in a screenshot.

    Returns a list of MatchResults sorted by confidence (highest first).
    """
    try:
        import cv2
        import numpy as np
    except ImportError:
        return []

    try:
        screenshot = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)

        if screenshot is None or template is None:
            return []

        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        h, w = template.shape[:2]

        locations = np.where(result >= threshold)
        matches: list[MatchResult] = []

        for pt in zip(*locations[::-1]):
            x, y = int(pt[0]), int(pt[1])
            confidence = float(result[y, x])
            matches.append(MatchResult(
                found=True,
                x=x, y=y, width=w, height=h,
                confidence=confidence,
                center_x=x + w // 2,
                center_y=y + h // 2,
            ))

        # Deduplicate overlapping matches (NMS-like)
        matches = _non_max_suppression(matches, overlap_threshold=0.5)
        matches.sort(key=lambda m: m.confidence, reverse=True)
        return matches[:max_results]

    except Exception as exc:
        log.error("Ronin: multi-match failed: %s", exc)
        return []


def _non_max_suppression(
    matches: list[MatchResult],
    overlap_threshold: float = 0.5,
) -> list[MatchResult]:
    """Remove overlapping matches, keeping highest confidence."""
    if not matches:
        return []

    matches.sort(key=lambda m: m.confidence, reverse=True)
    kept: list[MatchResult] = []

    for match in matches:
        overlaps = False
        for existing in kept:
            # Check overlap
            dx = abs(match.center_x - existing.center_x)
            dy = abs(match.center_y - existing.center_y)
            if dx < match.width * overlap_threshold and dy < match.height * overlap_threshold:
                overlaps = True
                break
        if not overlaps:
            kept.append(match)

    return kept
