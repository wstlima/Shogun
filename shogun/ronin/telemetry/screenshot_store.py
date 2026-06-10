"""Screenshot Store — manages data/ronin/screenshots/ lifecycle."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

log = logging.getLogger("shogun.ronin.telemetry.screenshots")

# Default limits
MAX_SCREENSHOTS = 500
MAX_TOTAL_SIZE_MB = 200


def get_screenshots_dir() -> Path:
    """Get the screenshots directory."""
    try:
        from shogun.config import settings
        ronin_path = getattr(settings, "ronin_path", None)
        if ronin_path:
            d = Path(ronin_path) / "screenshots"
        else:
            from shogun.config import PROJECT_ROOT
            d = PROJECT_ROOT / "data" / "ronin" / "screenshots"
    except Exception:
        d = Path("data/ronin/screenshots")
    d.mkdir(parents=True, exist_ok=True)
    return d


def list_screenshots(limit: int = 50) -> list[dict[str, Any]]:
    """List recent screenshots sorted by modification time (newest first)."""
    d = get_screenshots_dir()
    files = sorted(d.glob("*.png"), key=lambda f: f.stat().st_mtime, reverse=True)
    return [
        {
            "filename": f.name,
            "path": str(f),
            "size_bytes": f.stat().st_size,
            "created": datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).isoformat(),
        }
        for f in files[:limit]
    ]


def cleanup(max_count: int = MAX_SCREENSHOTS, max_size_mb: int = MAX_TOTAL_SIZE_MB) -> int:
    """Remove old screenshots exceeding limits. Returns count removed."""
    d = get_screenshots_dir()
    files = sorted(d.glob("*.png"), key=lambda f: f.stat().st_mtime)
    removed = 0

    # Remove by count
    while len(files) > max_count:
        oldest = files.pop(0)
        try:
            oldest.unlink()
            removed += 1
        except Exception:
            pass

    # Remove by total size
    total_size = sum(f.stat().st_size for f in files)
    max_bytes = max_size_mb * 1024 * 1024
    while total_size > max_bytes and files:
        oldest = files.pop(0)
        try:
            size = oldest.stat().st_size
            oldest.unlink()
            total_size -= size
            removed += 1
        except Exception:
            pass

    if removed:
        log.info("Ronin: cleaned up %d old screenshots", removed)
    return removed
