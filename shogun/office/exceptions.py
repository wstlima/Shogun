"""Office Adapter exceptions — structured error hierarchy.

Every exception carries enough context for the agent to understand
what happened and suggest a next step to the user, and for the
error to be rendered as a clear, human-readable message (not a
raw COM error code).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OfficeErrorContext:
    """Structured context attached to every Office exception."""

    action: str = ""
    file: str = ""
    reason: str = ""
    mutation_occurred: bool = False
    suggested_next_step: str = ""

    def to_dict(self) -> dict:
        return {
            "action": self.action,
            "file": self.file,
            "reason": self.reason,
            "mutation_occurred": self.mutation_occurred,
            "suggested_next_step": self.suggested_next_step,
        }


class OfficeError(Exception):
    """Base exception for all Office Adapter errors."""

    def __init__(self, message: str, context: OfficeErrorContext | None = None):
        super().__init__(message)
        self.context = context or OfficeErrorContext()


class OfficeNotInstalledError(OfficeError):
    """Raised when the required Office application is not installed."""

    def __init__(self, app_name: str):
        ctx = OfficeErrorContext(
            action=f"detect_{app_name}",
            reason=f"Microsoft {app_name.title()} is not installed on this system.",
            suggested_next_step=f"Install Microsoft {app_name.title()} or disable {app_name} in the Office App Mode configuration.",
        )
        super().__init__(ctx.reason, ctx)


class OfficeNotAvailableError(OfficeError):
    """Raised when Office App Mode is unavailable (e.g. non-Windows OS)."""

    def __init__(self, reason: str = ""):
        ctx = OfficeErrorContext(
            action="check_platform",
            reason=reason or "Office App Mode requires Microsoft Windows with Office installed.",
            suggested_next_step="Office App Mode is only available on Windows. Document manipulation (without PDF export) may be available on other platforms in a future release.",
        )
        super().__init__(ctx.reason, ctx)


class PathValidationError(OfficeError):
    """Raised when a file path fails boundary validation."""

    def __init__(self, path: str, reason: str):
        ctx = OfficeErrorContext(
            action="validate_path",
            file=path,
            reason=reason,
            suggested_next_step="Ensure the file is located within an approved folder (input, output, templates, or temp).",
        )
        super().__init__(f"Path validation failed for '{path}': {reason}", ctx)


class PermissionDeniedError(OfficeError):
    """Raised when the current posture does not allow the requested action."""

    def __init__(self, action: str, posture: str, reason: str = ""):
        ctx = OfficeErrorContext(
            action=action,
            reason=reason or f"Action '{action}' is not permitted at posture level '{posture}'.",
            suggested_next_step=f"Change the security posture in the Torii, or request admin approval for this action.",
        )
        super().__init__(ctx.reason, ctx)


class FileLockedError(OfficeError):
    """Raised when a file is locked by another process."""

    def __init__(self, path: str):
        ctx = OfficeErrorContext(
            action="open_file",
            file=path,
            reason=f"The file '{path}' is locked by another process.",
            suggested_next_step="Close the file in any other application and try again.",
        )
        super().__init__(ctx.reason, ctx)


class OfficeTimeoutError(OfficeError):
    """Raised when an Office operation exceeds the configured timeout."""

    def __init__(self, app_name: str, action: str, timeout_seconds: int):
        ctx = OfficeErrorContext(
            action=action,
            reason=f"Microsoft {app_name.title()} did not respond within {timeout_seconds} seconds.",
            mutation_occurred=True,  # Assume the worst — partial writes may have occurred
            suggested_next_step="Check if the Office application is frozen or showing a dialog. The operation may have partially completed.",
        )
        super().__init__(ctx.reason, ctx)


class MacroBlockedError(OfficeError):
    """Raised when a macro-enabled file is blocked by policy."""

    def __init__(self, path: str):
        ctx = OfficeErrorContext(
            action="open_file",
            file=path,
            reason="Macro-enabled files (.xlsm, .docm, .pptm) are blocked by the current security policy.",
            suggested_next_step="Enable macro handling in the Office App Mode configuration if your organization permits it.",
        )
        super().__init__(ctx.reason, ctx)


class ExternalLinkBlockedError(OfficeError):
    """Raised when a document contains external links that are blocked."""

    def __init__(self, path: str, link_type: str = "external data connection"):
        ctx = OfficeErrorContext(
            action="open_file",
            file=path,
            reason=f"The document contains a {link_type} which is blocked by the current security policy.",
            suggested_next_step="Remove external links from the document, or enable external link access in the configuration.",
        )
        super().__init__(ctx.reason, ctx)


class PasswordProtectedError(OfficeError):
    """Raised when a file is password-protected."""

    def __init__(self, path: str):
        ctx = OfficeErrorContext(
            action="open_file",
            file=path,
            reason="The file is password-protected. Shogun cannot open password-protected Office files.",
            suggested_next_step="Remove the password protection from the file and place it in the approved input folder.",
        )
        super().__init__(ctx.reason, ctx)


class CorruptedFileError(OfficeError):
    """Raised when a file appears to be corrupted."""

    def __init__(self, path: str, detail: str = ""):
        ctx = OfficeErrorContext(
            action="open_file",
            file=path,
            reason=f"The file appears to be corrupted{': ' + detail if detail else ''}.",
            suggested_next_step="Replace the file with a clean copy in the approved input folder.",
        )
        super().__init__(ctx.reason, ctx)
