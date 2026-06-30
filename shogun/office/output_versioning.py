"""Output versioning and cleanup utilities.

Ensures Office outputs are never overwritten and always carry a unique
timestamp. Also handles temp folder cleanup and optional output retention.
"""

from __future__ import annotations

import logging
import os
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger("shogun.office.output_versioning")


def version_output_path(
    original_name: str,
    extension: str,
    output_folder: str | Path,
) -> Path:
    """Generate a versioned output file path.

    Format: ``{name}_shogun_{YYYYMMDD_HHMMSS}.{ext}``

    Args:
        original_name: Base name of the original file (without extension).
        extension: File extension including the dot (e.g. ``.xlsx``).
        output_folder: Path to the approved output folder.

    Returns:
        Full path to the versioned output file.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    # Sanitize the original name (remove any existing _shogun_ suffix)
    clean_name = original_name
    if "_shogun_" in clean_name:
        clean_name = clean_name[: clean_name.index("_shogun_")]

    # Ensure extension starts with a dot
    if extension and not extension.startswith("."):
        extension = f".{extension}"

    versioned_name = f"{clean_name}_shogun_{timestamp}{extension}"
    output_path = Path(output_folder) / versioned_name

    # Handle rare collision (same second)
    if output_path.exists():
        counter = 1
        while output_path.exists():
            versioned_name = f"{clean_name}_shogun_{timestamp}_{counter}{extension}"
            output_path = Path(output_folder) / versioned_name
            counter += 1

    log.debug("Versioned output path: %s", output_path)
    return output_path


def cleanup_temp_folder(temp_path: str | Path) -> int:
    """Remove all files from the temp folder.

    Args:
        temp_path: Path to the temporary working folder.

    Returns:
        Number of files removed.
    """
    temp_dir = Path(temp_path)
    if not temp_dir.exists() or not temp_dir.is_dir():
        return 0

    count = 0
    for item in temp_dir.iterdir():
        try:
            if item.is_file():
                item.unlink()
                count += 1
            elif item.is_dir():
                shutil.rmtree(item)
                count += 1
        except Exception as exc:
            log.warning("Failed to clean up temp item %s: %s", item, exc)

    if count:
        log.info("Cleaned up %d items from temp folder: %s", count, temp_dir)
    return count


def cleanup_old_outputs(
    output_path: str | Path,
    max_age_days: int = 30,
) -> int:
    """Remove output files older than the retention period.

    Only removes files matching the ``*_shogun_*`` naming pattern to
    avoid deleting user-placed files.

    Args:
        output_path: Path to the approved output folder.
        max_age_days: Maximum age in days. Files older than this are removed.

    Returns:
        Number of files removed.
    """
    output_dir = Path(output_path)
    if not output_dir.exists() or not output_dir.is_dir():
        return 0

    cutoff = time.time() - (max_age_days * 86400)
    count = 0

    for item in output_dir.iterdir():
        if not item.is_file():
            continue
        # Only clean up Shogun-generated outputs
        if "_shogun_" not in item.name:
            continue
        try:
            if item.stat().st_mtime < cutoff:
                item.unlink()
                count += 1
                log.debug("Removed expired output: %s", item)
        except Exception as exc:
            log.warning("Failed to remove expired output %s: %s", item, exc)

    if count:
        log.info("Cleaned up %d expired output files from %s (max age: %d days)", count, output_dir, max_age_days)
    return count
