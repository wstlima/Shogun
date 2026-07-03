"""File Boundary Validator — the most security-critical component of Office App Mode.

Ensures every file path used by Office adapters is inside an approved folder
and does not violate any safety boundary. This is the primary defense against
path traversal attacks, symlink escapes, and unauthorized file access.

Rules enforced:
  - Resolved absolute path must start with an approved folder root
  - No ``..`` traversal in the original path
  - No symlink escape (resolved path re-checked)
  - No Windows shortcut (``.lnk``) files
  - No UNC paths (``\\\\server\\share``) unless explicitly allowed
  - Extension must be on the allowlist
  - Macro-enabled extensions blocked unless config allows
  - File size must be within configured limit
"""

from __future__ import annotations

import logging
import os
import stat
from dataclasses import dataclass
from enum import Enum
from pathlib import Path, PureWindowsPath

from shogun.office.config import OfficeAppConfig
from shogun.office.exceptions import PathValidationError

log = logging.getLogger("shogun.office.path_validator")


# ── Enums & Data Classes ─────────────────────────────────────────────


class PathPurpose(str, Enum):
    """What the file path will be used for."""

    READ = "read"
    WRITE = "write"
    TEMPLATE = "template"
    TEMP = "temp"
    OUTPUT = "output"


@dataclass
class ValidatedPath:
    """Result of a path validation check."""

    resolved_path: Path
    folder_type: PathPurpose
    extension: str
    is_valid: bool
    error: str = ""

    def __str__(self) -> str:
        return str(self.resolved_path)


# ── Extension Lists ──────────────────────────────────────────────────

# Allowed extensions for Office files
ALLOWED_EXTENSIONS: set[str] = {
    ".xlsx", ".docx", ".pptx",
    ".csv", ".txt",
    ".pdf",  # output only
}

# Macro-enabled extensions — allowed only when macros are enabled
MACRO_EXTENSIONS: set[str] = {
    ".xlsm", ".docm", ".pptm",
    ".xltm", ".dotm", ".potm",
}

# Always blocked — executable and script extensions
BLOCKED_EXTENSIONS: set[str] = {
    ".exe", ".bat", ".cmd", ".ps1", ".vbs", ".js", ".com",
    ".scr", ".dll", ".reg", ".msi", ".wsf", ".wsh",
    ".pif", ".cpl", ".inf", ".hta",
}

# Optional extensions — allowed if the relevant adapter is enabled
OPTIONAL_EXTENSIONS: set[str] = {
    ".msg", ".eml",
}


# ── Core Validator ───────────────────────────────────────────────────


class FileBoundaryValidator:
    """Validates file paths against approved folder boundaries and safety rules."""

    def __init__(self, config: OfficeAppConfig):
        self.config = config

        # Auto-include workspace root when explicit folders are not configured
        from shogun.config import settings
        workspace_root = str(settings.workspace_path.resolve())

        self._approved_folders: dict[PathPurpose, Path | None] = {
            PathPurpose.READ: Path(config.folders.input) if config.folders.input else Path(workspace_root),
            PathPurpose.TEMPLATE: Path(config.folders.templates) if config.folders.templates else Path(workspace_root),
            PathPurpose.WRITE: Path(config.folders.output) if config.folders.output else Path(workspace_root),
            PathPurpose.OUTPUT: Path(config.folders.output) if config.folders.output else Path(workspace_root),
            PathPurpose.TEMP: Path(config.folders.temp) if config.folders.temp else Path(workspace_root),
        }

    def validate(self, file_path: str, purpose: PathPurpose) -> ValidatedPath:
        """Validate a file path for the given purpose.

        Raises PathValidationError if validation fails.
        Returns ValidatedPath on success.
        """
        raw_path = file_path.strip()

        # ── 1. Reject empty paths ──
        if not raw_path:
            raise PathValidationError(raw_path, "File path is empty.")

        # ── 2. Reject UNC paths ──
        if self.config.safety.block_unc_paths:
            if raw_path.startswith("\\\\") or raw_path.startswith("//"):
                raise PathValidationError(raw_path, "UNC paths (network paths) are blocked by security policy.")

        # ── 3. Reject path traversal in raw input ──
        if self.config.safety.block_path_traversal:
            # Check for traversal patterns before resolving
            normalized = raw_path.replace("\\", "/")
            if "/../" in normalized or normalized.startswith("../") or normalized.endswith("/..") or normalized == "..":
                raise PathValidationError(raw_path, "Path traversal detected (../ pattern). Access denied.")
            # Also check Windows-style
            win_normalized = raw_path.replace("/", "\\")
            if "\\..\\".encode() != b"" and ("\\..\\" in win_normalized or win_normalized.startswith("..\\") or win_normalized.endswith("\\..")):
                raise PathValidationError(raw_path, "Path traversal detected (..\\ pattern). Access denied.")

        # ── 4. Reject .lnk shortcut files ──
        if self.config.safety.block_shortcuts:
            if raw_path.lower().endswith(".lnk"):
                raise PathValidationError(raw_path, "Windows shortcut files (.lnk) are blocked by security policy.")

        # ── 5. Resolve absolute path ──
        try:
            path = Path(raw_path)
            if not path.is_absolute():
                # Try resolving relative to the approved folder for this purpose
                approved = self._approved_folders.get(purpose)
                if approved:
                    path = approved / path
                else:
                    raise PathValidationError(raw_path, "Relative paths require a configured approved folder.")
            resolved = path.resolve()
        except (OSError, ValueError) as exc:
            raise PathValidationError(raw_path, f"Cannot resolve path: {exc}")

        # ── 6. Check extension ──
        extension = resolved.suffix.lower()
        if not extension:
            raise PathValidationError(raw_path, "File has no extension.")

        if extension in BLOCKED_EXTENSIONS:
            raise PathValidationError(raw_path, f"Extension '{extension}' is blocked by security policy.")

        if extension in MACRO_EXTENSIONS:
            # Check per-app macro settings
            app_allows = False
            if extension in (".xlsm", ".xltm"):
                app_allows = self.config.excel.allow_macros
            elif extension in (".docm", ".dotm"):
                app_allows = self.config.word.allow_macros
            elif extension in (".pptm", ".potm"):
                app_allows = self.config.powerpoint.allow_macros

            if not app_allows:
                from shogun.office.exceptions import MacroBlockedError
                raise MacroBlockedError(raw_path)

        if extension not in ALLOWED_EXTENSIONS and extension not in MACRO_EXTENSIONS and extension not in OPTIONAL_EXTENSIONS:
            raise PathValidationError(raw_path, f"Extension '{extension}' is not in the allowed list.")

        # ── 7. Check approved folder containment ──
        approved_folder = self._approved_folders.get(purpose)
        if approved_folder is None:
            raise PathValidationError(
                raw_path,
                f"No approved folder configured for purpose '{purpose.value}'. "
                "Configure folders in the Office App Mode settings.",
            )

        approved_resolved = approved_folder.resolve()
        try:
            resolved.relative_to(approved_resolved)
        except ValueError:
            raise PathValidationError(
                raw_path,
                f"File is outside the approved {purpose.value} folder. "
                f"Expected path under: {approved_resolved}",
            )

        # ── 8. Post-resolve symlink check ──
        # Even after resolving, verify the result is still in bounds
        # (catches symlinks that resolve to outside the approved tree)
        if resolved != path.resolve():
            try:
                resolved.relative_to(approved_resolved)
            except ValueError:
                raise PathValidationError(
                    raw_path,
                    "Symlink resolves to a location outside the approved folder. Access denied.",
                )

        # ── 9. File size check (only for existing files) ──
        if resolved.exists() and resolved.is_file():
            size_mb = resolved.stat().st_size / (1024 * 1024)
            if size_mb > self.config.safety.max_file_size_mb:
                raise PathValidationError(
                    raw_path,
                    f"File size ({size_mb:.1f} MB) exceeds the maximum allowed "
                    f"({self.config.safety.max_file_size_mb} MB).",
                )

        # ── 10. File lock check (only for existing files being read) ──
        if purpose in (PathPurpose.READ, PathPurpose.TEMPLATE) and resolved.exists():
            if not self._can_read_file(resolved):
                from shogun.office.exceptions import FileLockedError
                raise FileLockedError(raw_path)

        log.debug("Path validated: %s → %s (purpose=%s)", raw_path, resolved, purpose.value)

        return ValidatedPath(
            resolved_path=resolved,
            folder_type=purpose,
            extension=extension,
            is_valid=True,
        )

    @staticmethod
    def _can_read_file(path: Path) -> bool:
        """Check if a file can be opened for reading (not locked)."""
        try:
            with open(path, "rb"):
                return True
        except (PermissionError, OSError):
            return False


def validate_path(
    file_path: str,
    purpose: PathPurpose,
    config: OfficeAppConfig,
) -> ValidatedPath:
    """Convenience function — creates a validator and validates in one call."""
    validator = FileBoundaryValidator(config)
    return validator.validate(file_path, purpose)
