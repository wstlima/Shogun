"""Workspace API — REST endpoints for the File Explorer UI.

Routes:
  GET    /api/v1/workspace/tree          — full directory tree
  GET    /api/v1/workspace/read?path=... — read file content
  POST   /api/v1/workspace/write         — create/update file
  POST   /api/v1/workspace/mkdir         — create directory
  DELETE /api/v1/workspace/delete?path=...— delete file or empty dir
  POST   /api/v1/workspace/rename        — rename/move file or dir
  POST   /api/v1/workspace/upload        — upload files (multipart)
  GET    /api/v1/workspace/download?path= — download file (binary)
  GET    /api/v1/workspace/info          — workspace metadata
"""

from __future__ import annotations

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from pydantic import BaseModel

from shogun.config import settings

log = logging.getLogger("shogun.api.workspace")
router = APIRouter(prefix="/workspace", tags=["Workspace"])


# ── Helpers ──────────────────────────────────────────────────────────

def _get_workspace_root() -> Path:
    """Return the resolved workspace root, creating it if needed."""
    root = settings.workspace_path.resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def _validate_path(root: Path, relative: str) -> Path:
    """Resolve and validate a relative path against the workspace root."""
    if not relative or relative.strip() == "":
        return root

    rel = relative.strip()
    # Block traversal
    if ".." in rel:
        raise HTTPException(400, f"Path traversal blocked: '{rel}'")
    if rel.startswith("/") or rel.startswith("\\"):
        raise HTTPException(400, f"Absolute paths not allowed: '{rel}'")
    if rel.startswith("\\\\"):
        raise HTTPException(400, f"UNC paths not allowed: '{rel}'")

    target = (root / rel).resolve()
    try:
        target.relative_to(root)
    except ValueError:
        raise HTTPException(400, f"Path escapes workspace boundary: '{rel}'")
    return target


async def _check_posture() -> None:
    """Raise 403 if workspace is disabled (SHRINE posture)."""
    from shogun.api.security import _get_agent_posture
    posture = await _get_agent_posture()
    if not posture.get("workspace_enabled", True):
        tier = posture.get("active_tier", "tactical")
        raise HTTPException(
            403,
            f"Workspace access disabled at {tier.upper()} posture. "
            "Raise the security tier above SHRINE to use the workspace.",
        )


def _build_tree(path: Path, root: Path, max_depth: int = 10, depth: int = 0) -> list[dict]:
    """Recursively build a directory tree structure."""
    if depth > max_depth:
        return []

    entries: list[dict] = []
    try:
        items = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    except PermissionError:
        return []

    for item in items:
        rel = str(item.relative_to(root)).replace("\\", "/")
        entry: dict[str, Any] = {
            "name": item.name,
            "path": rel,
            "type": "directory" if item.is_dir() else "file",
        }
        try:
            item_stat = item.stat()
            entry["created_at"] = datetime.fromtimestamp(
                item_stat.st_ctime
            ).astimezone().isoformat()
            entry["modified_at"] = datetime.fromtimestamp(
                item_stat.st_mtime
            ).astimezone().isoformat()
        except OSError:
            item_stat = None
        if item.is_file():
            entry["size"] = item_stat.st_size if item_stat else 0
            entry["extension"] = item.suffix.lstrip(".")
        elif item.is_dir():
            entry["children"] = _build_tree(item, root, max_depth, depth + 1)
        entries.append(entry)

    return entries


# ── Schemas ──────────────────────────────────────────────────────────

class WriteRequest(BaseModel):
    path: str
    content: str

class MkdirRequest(BaseModel):
    path: str

class RenameRequest(BaseModel):
    old_path: str
    new_path: str


# ── Endpoints ────────────────────────────────────────────────────────

@router.get("/info")
async def workspace_info():
    """Get workspace metadata: path, enabled status, disk usage."""
    await _check_posture()
    root = _get_workspace_root()

    total_files = sum(1 for f in root.rglob("*") if f.is_file())
    total_dirs = sum(1 for f in root.rglob("*") if f.is_dir())
    total_size = sum(f.stat().st_size for f in root.rglob("*") if f.is_file())

    return {
        "success": True,
        "data": {
            "path": str(root),
            "enabled": True,
            "total_files": total_files,
            "total_directories": total_dirs,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        },
    }


@router.get("/tree")
async def workspace_tree():
    """Get the full directory tree of the workspace."""
    await _check_posture()
    root = _get_workspace_root()
    tree = _build_tree(root, root)
    return {"success": True, "data": {"root": str(root), "tree": tree}}


@router.get("/read")
async def read_file(path: str):
    """Read a text file from the workspace."""
    await _check_posture()
    root = _get_workspace_root()
    target = _validate_path(root, path)

    if not target.exists():
        raise HTTPException(404, f"File not found: {path}")
    if not target.is_file():
        raise HTTPException(400, f"Not a file: {path}")

    size = target.stat().st_size
    if size > 10 * 1024 * 1024:  # 10 MB limit for UI
        raise HTTPException(413, f"File too large to read in browser: {size} bytes")

    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise HTTPException(415, f"Cannot read as text (binary file): {path}")

    return {
        "success": True,
        "data": {
            "path": path,
            "content": content,
            "size": size,
            "extension": target.suffix.lstrip("."),
        },
    }


@router.post("/write")
async def write_file(req: WriteRequest):
    """Create or overwrite a text file."""
    await _check_posture()
    root = _get_workspace_root()
    target = _validate_path(root, req.path)

    target.parent.mkdir(parents=True, exist_ok=True)
    existed = target.exists()
    target.write_text(req.content, encoding="utf-8")
    size = target.stat().st_size

    log.info("Workspace write: %s (%d bytes, %s)", req.path, size, "overwritten" if existed else "created")
    return {
        "success": True,
        "data": {
            "path": req.path,
            "action": "overwritten" if existed else "created",
            "size": size,
        },
    }


@router.post("/mkdir")
async def make_directory(req: MkdirRequest):
    """Create a directory (with parents)."""
    await _check_posture()
    root = _get_workspace_root()
    target = _validate_path(root, req.path)

    existed = target.exists()
    target.mkdir(parents=True, exist_ok=True)

    return {
        "success": True,
        "data": {
            "path": req.path,
            "action": "already_exists" if existed else "created",
        },
    }


@router.delete("/delete")
async def delete_item(path: str):
    """Delete a file or empty directory."""
    await _check_posture()
    root = _get_workspace_root()
    target = _validate_path(root, path)

    if not target.exists():
        raise HTTPException(404, f"Not found: {path}")

    if target == root:
        raise HTTPException(400, "Cannot delete the workspace root")

    if target.is_file():
        target.unlink()
        log.info("Workspace delete file: %s", path)
    elif target.is_dir():
        # Allow deleting dirs (including non-empty)
        shutil.rmtree(str(target))
        log.info("Workspace delete directory: %s", path)

    return {"success": True, "data": {"path": path, "action": "deleted"}}


@router.post("/rename")
async def rename_item(req: RenameRequest):
    """Rename or move a file/directory."""
    await _check_posture()
    root = _get_workspace_root()
    old = _validate_path(root, req.old_path)
    new = _validate_path(root, req.new_path)

    if not old.exists():
        raise HTTPException(404, f"Not found: {req.old_path}")
    if new.exists():
        raise HTTPException(409, f"Already exists: {req.new_path}")

    new.parent.mkdir(parents=True, exist_ok=True)
    old.rename(new)

    log.info("Workspace rename: %s -> %s", req.old_path, req.new_path)
    return {
        "success": True,
        "data": {
            "old_path": req.old_path,
            "new_path": req.new_path,
        },
    }


@router.post("/upload")
async def upload_files(
    files: list[UploadFile] = File(...),
    path: str = Form(default=""),
):
    """Upload one or more files into the workspace via multipart form.

    - `files`: The file(s) to upload.
    - `path`: Relative directory inside the workspace to upload into.
              Defaults to workspace root.
    """
    await _check_posture()
    root = _get_workspace_root()

    target_dir = _validate_path(root, path) if path.strip() else root
    if not target_dir.is_dir():
        raise HTTPException(400, f"Not a directory: {path}")

    results = []
    for f in files:
        if not f.filename:
            continue

        # Validate the final file path
        safe_name = Path(f.filename).name  # Strip any directory components
        if not safe_name or safe_name.startswith("."):
            results.append({"name": f.filename, "status": "rejected", "reason": "Invalid filename"})
            continue

        dest = target_dir / safe_name
        # Ensure still inside workspace
        try:
            dest.resolve().relative_to(root)
        except ValueError:
            results.append({"name": safe_name, "status": "rejected", "reason": "Path escape"})
            continue

        content = await f.read()
        dest.write_bytes(content)
        size = dest.stat().st_size
        log.info("Workspace upload: %s (%d bytes)", safe_name, size)
        results.append({"name": safe_name, "status": "uploaded", "size": size})

    return {
        "success": True,
        "data": {
            "path": path or ".",
            "uploaded": len([r for r in results if r["status"] == "uploaded"]),
            "files": results,
        },
    }


@router.get("/download")
async def download_file(path: str):
    """Download a file from the workspace as binary."""
    await _check_posture()
    root = _get_workspace_root()
    target = _validate_path(root, path)

    if not target.is_file():
        raise HTTPException(404, f"File not found: {path}")

    return FileResponse(
        path=str(target),
        filename=target.name,
        media_type="application/octet-stream",
    )
