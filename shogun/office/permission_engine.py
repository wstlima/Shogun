"""Permission Engine — posture-aware action gating for Office operations.

Checks whether the current Shogun security posture allows a requested
Office action. This sits between the agent's tool call and the adapter
execution, ensuring that sensitive operations are blocked or require
approval at the appropriate posture levels.

The action permission matrix follows Build Paper §10.3.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

log = logging.getLogger("shogun.office.permission_engine")


# ── Action Types ─────────────────────────────────────────────────────


class OfficeAction(str, Enum):
    """Actions that can be performed through Office adapters."""

    OPEN_FILE = "open_file"
    READ_CONTENT = "read_content"
    WRITE_CONTENT = "write_content"
    SAVE_AS_NEW = "save_as_new"
    OVERWRITE_ORIGINAL = "overwrite_original"
    EXPORT_PDF = "export_pdf"
    RUN_MACRO = "run_macro"
    CREATE_SHEET = "create_sheet"
    DELETE_SHEET = "delete_sheet"
    DUPLICATE_SLIDE = "duplicate_slide"
    DELETE_SLIDE = "delete_slide"
    INSERT_IMAGE = "insert_image"
    APPLY_FORMATTING = "apply_formatting"
    CALCULATE = "calculate"
    CREATE_DRAFT = "create_draft"
    SET_RECIPIENTS = "set_recipients"
    ATTACH_FILE = "attach_file"
    SEND_EMAIL = "send_email"
    READ_MAILBOX = "read_mailbox"
    OPEN_EXTERNAL_LINK = "open_external_link"
    REFRESH_EXTERNAL_DATA = "refresh_external_data"


# ── Permission Decision ──────────────────────────────────────────────


@dataclass
class PermissionDecision:
    """Result of a permission check."""

    allowed: bool
    requires_approval: bool = False
    reason: str = ""

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "requires_approval": self.requires_approval,
            "reason": self.reason,
        }


# ── Permission Matrix ───────────────────────────────────────────────
# Maps (action) → {posture → decision}
# Postures: guarded, tactical (maps to "supervised"), campaign, ronin

_PERMISSION_MATRIX: dict[OfficeAction, dict[str, str]] = {
    # Basic file operations — allowed at all levels
    OfficeAction.OPEN_FILE:          {"guarded": "allow", "tactical": "allow", "campaign": "allow", "ronin": "allow"},
    OfficeAction.READ_CONTENT:       {"guarded": "allow", "tactical": "allow", "campaign": "allow", "ronin": "allow"},
    OfficeAction.WRITE_CONTENT:      {"guarded": "allow", "tactical": "allow", "campaign": "allow", "ronin": "allow"},
    OfficeAction.SAVE_AS_NEW:        {"guarded": "allow", "tactical": "allow", "campaign": "allow", "ronin": "allow"},
    OfficeAction.EXPORT_PDF:         {"guarded": "allow", "tactical": "allow", "campaign": "allow", "ronin": "allow"},
    OfficeAction.CREATE_SHEET:       {"guarded": "allow", "tactical": "allow", "campaign": "allow", "ronin": "allow"},
    OfficeAction.DUPLICATE_SLIDE:    {"guarded": "allow", "tactical": "allow", "campaign": "allow", "ronin": "allow"},
    OfficeAction.INSERT_IMAGE:       {"guarded": "allow", "tactical": "allow", "campaign": "allow", "ronin": "allow"},
    OfficeAction.APPLY_FORMATTING:   {"guarded": "allow", "tactical": "allow", "campaign": "allow", "ronin": "allow"},
    OfficeAction.CALCULATE:          {"guarded": "allow", "tactical": "allow", "campaign": "allow", "ronin": "allow"},

    # Destructive or sensitive operations
    OfficeAction.OVERWRITE_ORIGINAL: {"guarded": "block", "tactical": "approval", "campaign": "approval", "ronin": "allow"},
    OfficeAction.DELETE_SHEET:       {"guarded": "block", "tactical": "approval", "campaign": "allow",   "ronin": "allow"},
    OfficeAction.DELETE_SLIDE:       {"guarded": "block", "tactical": "approval", "campaign": "allow",   "ronin": "allow"},
    OfficeAction.RUN_MACRO:          {"guarded": "block", "tactical": "approval", "campaign": "approval", "ronin": "approval"},

    # External interactions
    OfficeAction.OPEN_EXTERNAL_LINK:    {"guarded": "block", "tactical": "approval", "campaign": "approval", "ronin": "approval"},
    OfficeAction.REFRESH_EXTERNAL_DATA: {"guarded": "block", "tactical": "approval", "campaign": "approval", "ronin": "approval"},

    # Outlook operations
    OfficeAction.CREATE_DRAFT:    {"guarded": "allow",    "tactical": "allow",    "campaign": "allow",    "ronin": "allow"},
    OfficeAction.SET_RECIPIENTS:  {"guarded": "allow",    "tactical": "allow",    "campaign": "allow",    "ronin": "allow"},
    OfficeAction.ATTACH_FILE:     {"guarded": "approval", "tactical": "allow",    "campaign": "allow",    "ronin": "allow"},
    OfficeAction.SEND_EMAIL:      {"guarded": "block",    "tactical": "approval", "campaign": "approval", "ronin": "approval"},
    OfficeAction.READ_MAILBOX:    {"guarded": "block",    "tactical": "block",    "campaign": "approval", "ronin": "allow"},
}


# ── Core Check Function ─────────────────────────────────────────────


def check_office_permission(
    action: OfficeAction,
    app_name: str,
    posture_tier: str,
    office_config: Any = None,
) -> PermissionDecision:
    """Check whether the current posture allows an Office action.

    Args:
        action: The action being requested.
        app_name: The Office application (excel, word, powerpoint, outlook).
        posture_tier: Current security tier (guarded, tactical, campaign, ronin).
        office_config: OfficeAppConfig instance for additional checks.

    Returns:
        PermissionDecision with allowed/requires_approval/reason.
    """
    tier = posture_tier.lower()

    # Shrine tier blocks everything
    if tier == "shrine":
        return PermissionDecision(
            allowed=False,
            reason=f"Office App Mode is disabled at SHRINE tier.",
        )

    # Check the permission matrix
    action_perms = _PERMISSION_MATRIX.get(action)
    if action_perms is None:
        # Unknown action — default to approval required
        log.warning("Unknown Office action: %s — defaulting to approval", action)
        return PermissionDecision(
            allowed=True,
            requires_approval=True,
            reason=f"Unknown action '{action.value}' — requires human approval.",
        )

    decision_str = action_perms.get(tier, "block")

    if decision_str == "allow":
        return PermissionDecision(
            allowed=True,
            reason=f"Action '{action.value}' is allowed at {tier.upper()} posture.",
        )
    elif decision_str == "approval":
        return PermissionDecision(
            allowed=True,
            requires_approval=True,
            reason=f"Action '{action.value}' requires human approval at {tier.upper()} posture.",
        )
    elif decision_str == "block":
        return PermissionDecision(
            allowed=False,
            reason=f"Action '{action.value}' is blocked at {tier.upper()} posture.",
        )
    else:
        return PermissionDecision(
            allowed=False,
            reason=f"Unknown permission decision '{decision_str}' for action '{action.value}'.",
        )


async def get_current_posture_tier() -> str:
    """Read the current security posture tier from Shogun's posture store."""
    try:
        from shogun.api.security import _get_agent_posture
        posture = await _get_agent_posture()
        return posture.get("active_tier", "tactical")
    except Exception:
        return "tactical"
