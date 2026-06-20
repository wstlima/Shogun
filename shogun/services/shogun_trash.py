"""Shogun Trash — quarantine-based soft-delete for file operations.

Instead of permanently deleting files, this module moves them to a
`.shogun_trash/` directory at the project root. Files are timestamped
and can be recovered or permanently purged.

Usage:
    from shogun.services.shogun_trash import quarantine, recover, list_trash, purge

Architecture:
    .shogun_trash/
        2026-06-20T11-30-45__path__to__original__filename.txt
        2026-06-20T11-31-02__another_file.py
        manifest.json   ← maps trash filenames → original paths

    Manifest format:
    {
        "2026-06-20T11-30-45__path__to__original__filename.txt": {
            "original_path": "/path/to/original/filename.txt",
            "quarantined_at": "2026-06-20T11:30:45",
            "reason": "User-initiated deletion via Ronin",
            "size_bytes": 1234
        }
    }
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any

log = logging.getLogger("shogun.trash")

# Trash directory name (placed at project root or working directory)
TRASH_DIR_NAME = ".shogun_trash"
MANIFEST_NAME = "manifest.json"

# Maximum age for auto-purge (30 days)
AUTO_PURGE_DAYS = 30


def _get_trash_dir(base_dir: str | Path | None = None) -> Path:
    """Get or create the trash directory."""
    if base_dir is None:
        base_dir = Path.cwd()
    trash = Path(base_dir) / TRASH_DIR_NAME
    trash.mkdir(parents=True, exist_ok=True)
    return trash


def _load_manifest(trash_dir: Path) -> dict[str, Any]:
    """Load the manifest JSON."""
    manifest_path = trash_dir / MANIFEST_NAME
    if manifest_path.exists():
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            log.warning("Corrupt manifest at %s, starting fresh", manifest_path)
    return {}


def _save_manifest(trash_dir: Path, manifest: dict[str, Any]) -> None:
    """Save the manifest JSON."""
    manifest_path = trash_dir / MANIFEST_NAME
    manifest_path.write_text(
        json.dumps(manifest, indent=2, default=str),
        encoding="utf-8",
    )


def _make_trash_name(original_path: str | Path) -> str:
    """Create a unique trash filename from the original path."""
    ts = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    # Convert path separators to double underscores for flat storage
    safe_name = str(original_path).replace("\\", "__").replace("/", "__")
    # Remove drive letter colon
    safe_name = safe_name.replace(":", "")
    return f"{ts}__{safe_name}"


def quarantine(
    file_path: str | Path,
    reason: str = "Deleted via Shogun",
    base_dir: str | Path | None = None,
) -> dict[str, str]:
    """Move a file or directory to .shogun_trash/ instead of deleting it.

    Args:
        file_path: Path to the file or directory to quarantine.
        reason: Human-readable reason for the deletion.
        base_dir: Base directory for the trash folder (default: cwd).

    Returns:
        dict with 'status', 'trash_name', 'original_path', 'message'.

    Raises:
        FileNotFoundError: If the file doesn't exist.
    """
    source = Path(file_path).resolve()
    if not source.exists():
        raise FileNotFoundError(f"Cannot quarantine: '{file_path}' does not exist")

    trash_dir = _get_trash_dir(base_dir)
    trash_name = _make_trash_name(source)
    dest = trash_dir / trash_name

    # Get size before move
    if source.is_file():
        size_bytes = source.stat().st_size
    else:
        size_bytes = sum(f.stat().st_size for f in source.rglob("*") if f.is_file())

    # Move to trash
    shutil.move(str(source), str(dest))

    # Update manifest
    manifest = _load_manifest(trash_dir)
    manifest[trash_name] = {
        "original_path": str(source),
        "quarantined_at": datetime.now().isoformat(timespec="seconds"),
        "reason": reason,
        "size_bytes": size_bytes,
        "is_directory": source.is_dir() if dest.is_dir() else False,
    }
    _save_manifest(trash_dir, manifest)

    log.info("Quarantined '%s' → '%s' (%s)", source, trash_name, reason)

    return {
        "status": "quarantined",
        "trash_name": trash_name,
        "original_path": str(source),
        "message": f"Moved to .shogun_trash/ (recoverable). Reason: {reason}",
    }


def recover(
    trash_name: str,
    base_dir: str | Path | None = None,
    restore_to: str | Path | None = None,
) -> dict[str, str]:
    """Recover a file from .shogun_trash/ to its original location.

    Args:
        trash_name: The name of the item in trash.
        base_dir: Base directory for the trash folder.
        restore_to: Override restore path (default: original location from manifest).

    Returns:
        dict with 'status', 'restored_to', 'message'.
    """
    trash_dir = _get_trash_dir(base_dir)
    source = trash_dir / trash_name

    if not source.exists():
        return {
            "status": "error",
            "message": f"Trash item '{trash_name}' not found",
        }

    manifest = _load_manifest(trash_dir)
    entry = manifest.get(trash_name, {})

    if restore_to:
        dest = Path(restore_to)
    else:
        original = entry.get("original_path")
        if not original:
            return {
                "status": "error",
                "message": f"No original path recorded for '{trash_name}'. Specify restore_to.",
            }
        dest = Path(original)

    # Ensure parent exists
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Don't overwrite existing files
    if dest.exists():
        return {
            "status": "error",
            "message": f"Cannot restore: '{dest}' already exists. Move or rename it first.",
        }

    shutil.move(str(source), str(dest))

    # Remove from manifest
    manifest.pop(trash_name, None)
    _save_manifest(trash_dir, manifest)

    log.info("Recovered '%s' → '%s'", trash_name, dest)

    return {
        "status": "recovered",
        "restored_to": str(dest),
        "message": f"Restored to {dest}",
    }


def list_trash(
    base_dir: str | Path | None = None,
) -> list[dict[str, Any]]:
    """List all items in .shogun_trash/.

    Returns:
        List of dicts with 'trash_name', 'original_path', 'quarantined_at',
        'reason', 'size_bytes'.
    """
    trash_dir = _get_trash_dir(base_dir)
    manifest = _load_manifest(trash_dir)

    items = []
    for name, entry in manifest.items():
        exists = (trash_dir / name).exists()
        items.append({
            "trash_name": name,
            "original_path": entry.get("original_path", "unknown"),
            "quarantined_at": entry.get("quarantined_at", "unknown"),
            "reason": entry.get("reason", ""),
            "size_bytes": entry.get("size_bytes", 0),
            "exists": exists,
        })

    return sorted(items, key=lambda x: x["quarantined_at"], reverse=True)


def purge(
    trash_name: str | None = None,
    base_dir: str | Path | None = None,
    max_age_days: int = AUTO_PURGE_DAYS,
) -> dict[str, Any]:
    """Permanently delete items from .shogun_trash/.

    Args:
        trash_name: Specific item to purge (None = purge expired items).
        base_dir: Base directory for the trash folder.
        max_age_days: Max age in days for auto-purge (default: 30).

    Returns:
        dict with 'status', 'purged_count', 'items'.
    """
    trash_dir = _get_trash_dir(base_dir)
    manifest = _load_manifest(trash_dir)
    purged = []

    if trash_name:
        # Purge specific item
        target = trash_dir / trash_name
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
        manifest.pop(trash_name, None)
        purged.append(trash_name)
        log.info("Purged '%s' permanently", trash_name)
    else:
        # Auto-purge expired items
        now = time.time()
        cutoff = now - (max_age_days * 86400)

        for name, entry in list(manifest.items()):
            try:
                qt = datetime.fromisoformat(entry.get("quarantined_at", ""))
                if qt.timestamp() < cutoff:
                    target = trash_dir / name
                    if target.exists():
                        if target.is_dir():
                            shutil.rmtree(target)
                        else:
                            target.unlink()
                    manifest.pop(name, None)
                    purged.append(name)
                    log.info("Auto-purged expired item '%s'", name)
            except (ValueError, OSError):
                continue

    _save_manifest(trash_dir, manifest)

    return {
        "status": "purged",
        "purged_count": len(purged),
        "items": purged,
    }


def empty_trash(base_dir: str | Path | None = None) -> dict[str, Any]:
    """Permanently delete ALL items in .shogun_trash/.

    Returns:
        dict with 'status', 'purged_count'.
    """
    trash_dir = _get_trash_dir(base_dir)
    manifest = _load_manifest(trash_dir)
    count = len(manifest)

    for name in list(manifest.keys()):
        target = trash_dir / name
        if target.exists():
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()

    # Clear manifest
    _save_manifest(trash_dir, {})

    log.info("Emptied trash: %d items permanently deleted", count)

    return {
        "status": "emptied",
        "purged_count": count,
    }
