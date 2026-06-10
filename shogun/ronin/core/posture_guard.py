"""Ronin Posture Guard — evaluates Agent + Posture + App Trust + Environment = Decision.

This is the inner posture guard specific to Ronin. The global Torii posture
(``shogun.services.posture_guard``) is checked first at the API layer, then
this guard applies Ronin-specific rules on top.
"""

from __future__ import annotations

import logging
from typing import Any

from shogun.ronin.policies.ronin_policy_schema import (
    AppTrustLevel,
    EnvironmentType,
    PostureDecision,
    RiskLevel,
    RoninPostureLevel,
)

log = logging.getLogger("shogun.ronin.posture_guard")


# ── Posture level ordering (for minimum-level checks) ────────────────

_POSTURE_ORDER: dict[RoninPostureLevel, int] = {
    RoninPostureLevel.DISABLED: 0,
    RoninPostureLevel.OBSERVE_ONLY: 1,
    RoninPostureLevel.BROWSER_ONLY: 2,
    RoninPostureLevel.DESKTOP_LIMITED: 3,
    RoninPostureLevel.DESKTOP_FULL: 4,
    RoninPostureLevel.ADMIN_APPROVAL_REQUIRED: 5,
}

_TRUST_ORDER: dict[AppTrustLevel, int] = {
    AppTrustLevel.TRUSTED: 0,
    AppTrustLevel.RESTRICTED: 1,
    AppTrustLevel.SENSITIVE: 2,
    AppTrustLevel.FORBIDDEN: 3,
}


def evaluate(
    *,
    action_type: str,
    agent_id: str,
    current_posture: str,
    posture_permissions: dict[str, Any],
    app_trust_level: AppTrustLevel | None = None,
    environment_type: EnvironmentType | None = None,
    capability_posture_min: str | None = None,
    capability_trust_min: str | None = None,
    capability_risk: str | None = None,
    capability_requires_approval: bool = False,
) -> PostureDecision:
    """Evaluate whether a Ronin action is allowed.

    This checks in order:
    1. Ronin enabled?
    2. FORBIDDEN app? (hard block, no override)
    3. Environment policy
    4. Posture level >= capability minimum
    5. App trust level meets capability minimum
    6. Specific permission checks (mouse, keyboard, etc.)
    7. Approval requirement

    Returns a PostureDecision with allowed/denied/approval_required.
    """
    ronin_enabled = posture_permissions.get("ronin_enabled", False)
    ronin_posture_str = posture_permissions.get("ronin_posture", "disabled")

    # ── 1. Ronin must be enabled ─────────────────────────────────
    if not ronin_enabled:
        return PostureDecision(
            allowed=False,
            reason=f"Ronin is disabled at current posture. Action '{action_type}' blocked.",
            risk_level=RiskLevel(capability_risk) if capability_risk else RiskLevel.LOW,
        )

    # ── 2. Parse posture level ───────────────────────────────────
    try:
        posture_level = RoninPostureLevel(ronin_posture_str)
    except ValueError:
        return PostureDecision(
            allowed=False,
            reason=f"Unknown Ronin posture level: '{ronin_posture_str}'",
        )

    if posture_level == RoninPostureLevel.DISABLED:
        return PostureDecision(
            allowed=False,
            reason="Ronin posture is DISABLED. No desktop control allowed.",
        )

    # ── 3. FORBIDDEN app — hard safety rail ──────────────────────
    if app_trust_level == AppTrustLevel.FORBIDDEN:
        return PostureDecision(
            allowed=False,
            reason="Application is FORBIDDEN. No posture can override this safety rail.",
            app_trust=app_trust_level,
            risk_level=RiskLevel.CRITICAL,
        )

    # ── 4. Environment policy ────────────────────────────────────
    env_policy = posture_permissions.get("ronin_environment_policy", "any")
    if environment_type and env_policy != "any":
        if env_policy == "vm_only" and environment_type not in (
            EnvironmentType.VM, EnvironmentType.SANDBOX
        ):
            return PostureDecision(
                allowed=False,
                reason=f"Environment policy requires VM/Sandbox. Current: {environment_type.value}",
                environment=environment_type,
            )
        if env_policy == "sandbox_only" and environment_type != EnvironmentType.SANDBOX:
            return PostureDecision(
                allowed=False,
                reason=f"Environment policy requires Sandbox. Current: {environment_type.value}",
                environment=environment_type,
            )

    # ── 5. Posture level >= capability minimum ───────────────────
    if capability_posture_min:
        try:
            required_level = RoninPostureLevel(capability_posture_min)
        except ValueError:
            required_level = RoninPostureLevel.DESKTOP_LIMITED

        if _POSTURE_ORDER.get(posture_level, 0) < _POSTURE_ORDER.get(required_level, 0):
            return PostureDecision(
                allowed=False,
                reason=(
                    f"Action '{action_type}' requires posture {required_level.value}. "
                    f"Current posture: {posture_level.value}."
                ),
                risk_level=RiskLevel(capability_risk) if capability_risk else RiskLevel.LOW,
            )

    # ── 6. App trust meets capability minimum ────────────────────
    if app_trust_level and capability_trust_min:
        try:
            required_trust = AppTrustLevel(capability_trust_min)
        except ValueError:
            required_trust = AppTrustLevel.TRUSTED

        if _TRUST_ORDER.get(app_trust_level, 1) > _TRUST_ORDER.get(required_trust, 0):
            # SENSITIVE apps with non-approval posture → need approval
            if app_trust_level == AppTrustLevel.SENSITIVE:
                return PostureDecision(
                    allowed=False,
                    approval_required=True,
                    reason=(
                        f"App trust level is SENSITIVE. Action '{action_type}' "
                        f"requires approval for this application."
                    ),
                    app_trust=app_trust_level,
                    risk_level=RiskLevel.HIGH,
                )
            # RESTRICTED app trying to do something beyond its trust
            return PostureDecision(
                allowed=False,
                reason=(
                    f"App trust level '{app_trust_level.value}' does not meet "
                    f"minimum '{required_trust.value}' for action '{action_type}'."
                ),
                app_trust=app_trust_level,
            )

    # ── 7. Specific permission checks ────────────────────────────
    action_prefix = action_type.split(".")[0] if "." in action_type else action_type
    action_suffix = action_type.split(".", 1)[1] if "." in action_type else ""

    if action_prefix == "desktop":
        if action_suffix in ("move_mouse", "click", "double_click", "right_click", "drag"):
            if not posture_permissions.get("ronin_mouse_enabled", False):
                return PostureDecision(
                    allowed=False,
                    reason=f"Mouse control is disabled at current posture.",
                )
        if action_suffix in ("type", "hotkey"):
            if not posture_permissions.get("ronin_keyboard_enabled", False):
                return PostureDecision(
                    allowed=False,
                    reason=f"Keyboard control is disabled at current posture.",
                )
        if action_suffix == "screenshot":
            if not posture_permissions.get("ronin_screenshots_enabled", False):
                return PostureDecision(
                    allowed=False,
                    reason=f"Screenshots are disabled at current posture.",
                )

    # ── 8. Check if approval is required ─────────────────────────
    risk = RiskLevel(capability_risk) if capability_risk else RiskLevel.LOW

    if capability_requires_approval:
        return PostureDecision(
            allowed=False,
            approval_required=True,
            reason=f"Action '{action_type}' requires operator approval (risk: {risk.value}).",
            risk_level=risk,
            app_trust=app_trust_level,
            environment=environment_type,
        )

    # ── Check high-risk permission gates ─────────────────────────
    if action_type in ("os.app_launch",) or risk in (RiskLevel.HIGH, RiskLevel.CRITICAL):
        tri_state_checks = {
            "credential_entry": posture_permissions.get("ronin_credential_entry", "blocked"),
            "file_deletion": posture_permissions.get("ronin_file_deletion", "blocked"),
            "external_uploads": posture_permissions.get("ronin_external_uploads", "blocked"),
            "install_software": posture_permissions.get("ronin_install_software", "blocked"),
        }
        # If any relevant gate is "blocked" or "approval_required"
        for gate_name, gate_value in tri_state_checks.items():
            if gate_value == "approval_required":
                return PostureDecision(
                    allowed=False,
                    approval_required=True,
                    reason=f"Action '{action_type}' requires approval ({gate_name}).",
                    risk_level=risk,
                )

    # ── All checks passed ────────────────────────────────────────
    return PostureDecision(
        allowed=True,
        reason="Action permitted by posture, trust, and environment.",
        risk_level=risk,
        app_trust=app_trust_level,
        environment=environment_type,
    )
