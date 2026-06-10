"""Ronin Controller — main entry point for all Ronin desktop actions.

Orchestrates the full action pipeline:
  Action Request → Environment Check → Posture Guard → App Trust Check →
  Capability Lookup → Approval Gate (if needed) → Action Router →
  Verification → Audit Logger → Gensui Telemetry
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Any

from shogun.ronin.core import app_trust_registry
from shogun.ronin.core import capabilities_registry
from shogun.ronin.core.action_router import route_action
from shogun.ronin.core.approval_gate import request_approval
from shogun.ronin.core.audit_logger import RoninAuditLogger
from shogun.ronin.core.environment_detector import detect_environment
from shogun.ronin.core.komainu import (
    get_status as get_komainu_status,
    is_paused as komainu_is_paused,
    start_komainu,
    stop_komainu,
)
from shogun.ronin.core.posture_guard import evaluate as evaluate_posture
from shogun.ronin.policies.ronin_policy_schema import (
    AppTrustLevel,
    EnvironmentInfo,
    RiskLevel,
    RoninAction,
    RoninActionStatus,
    RoninResult,
    RoninSessionStatus,
)

log = logging.getLogger("shogun.ronin.controller")

# ── In-memory session state ──────────────────────────────────────────

_sessions: dict[str, dict[str, Any]] = {}
_environment: EnvironmentInfo | None = None


class RoninController:
    """Main orchestrator for Ronin desktop control actions."""

    def __init__(self):
        self._initialized = False
        self._environment: EnvironmentInfo | None = None

    async def initialize(self) -> EnvironmentInfo:
        """Initialize Ronin — detect environment and prepare subsystems."""
        if not self._initialized:
            self._environment = detect_environment()
            global _environment
            _environment = self._environment
            self._initialized = True
            log.info(
                "Ronin initialized: environment=%s, os=%s, hostname=%s",
                self._environment.environment_type.value,
                self._environment.os_type,
                self._environment.hostname,
            )
        return self._environment

    async def execute(self, action: RoninAction) -> RoninResult:
        """Execute a Ronin action through the full pipeline.

        This is the single entry point for all Ronin desktop operations.
        """
        start_time = time.monotonic()
        action_type = action.action_type

        # ── 1. Ensure initialized ────────────────────────────────
        if not self._initialized:
            await self.initialize()

        # ── 2. Komainu check — is Ronin paused? ──────────────────
        if komainu_is_paused():
            return RoninResult(
                status=RoninActionStatus.KOMAINU_PAUSED,
                action_type=action_type,
                error="Ronin is paused by Komainu guardian. Resume or stop session first.",
            )

        # ── 3. Capability lookup ─────────────────────────────────
        capability = capabilities_registry.get_capability(action_type)
        cap_posture_min = capability.posture_minimum.value if capability else None
        cap_trust_min = capability.app_trust_minimum.value if capability else None
        cap_risk = capability.risk_level.value if capability else action.risk_level.value if action.risk_level else "high"
        cap_requires_approval = capability.requires_approval if capability else False

        if not capability:
            log.warning("Ronin: unknown capability '%s' — applying HIGH risk defaults", action_type)

        # ── 4. Get current foreground app and trust level ────────
        app_trust_level = AppTrustLevel.RESTRICTED
        current_app: str | None = None

        # Only check foreground app for desktop actions
        if action_type.startswith("desktop.") and action_type != "desktop.screenshot":
            try:
                from shogun.ronin.adapters.base_adapter import get_adapter
                adapter = get_adapter()
                if adapter:
                    fg_process = adapter.get_foreground_process()
                    if fg_process:
                        current_app = fg_process
                        app_trust_level = app_trust_registry.get_trust_level(fg_process)
            except Exception as exc:
                log.debug("Ronin: foreground app detection failed: %s", exc)

        # ── 5. Get posture permissions ───────────────────────────
        posture_permissions = await self._get_posture_permissions()

        # ── 6. Posture guard evaluation ──────────────────────────
        decision = evaluate_posture(
            action_type=action_type,
            agent_id=action.agent_id,
            current_posture=posture_permissions.get("ronin_posture", "disabled"),
            posture_permissions=posture_permissions,
            app_trust_level=app_trust_level,
            environment_type=self._environment.environment_type if self._environment else None,
            capability_posture_min=cap_posture_min,
            capability_trust_min=cap_trust_min,
            capability_risk=cap_risk,
            capability_requires_approval=cap_requires_approval,
        )

        # ── 7. Handle blocked / approval-required ────────────────
        if not decision.allowed and not decision.approval_required:
            await RoninAuditLogger.log_action_blocked(
                action_type=action_type,
                reason=decision.reason,
                agent_id=action.agent_id,
                session_id=action.session_id,
                app_trust=app_trust_level.value,
                risk_level=cap_risk,
            )
            return RoninResult(
                status=RoninActionStatus.POSTURE_DENIED if "posture" in decision.reason.lower()
                else RoninActionStatus.APP_FORBIDDEN if "FORBIDDEN" in decision.reason
                else RoninActionStatus.ENVIRONMENT_DENIED if "environment" in decision.reason.lower()
                else RoninActionStatus.BLOCKED,
                action_type=action_type,
                error=decision.reason,
            )

        if decision.approval_required:
            # ── Request operator approval via WebSocket modal ────
            try:
                from shogun.ronin.desktop.screenshot_controller import take_screenshot_raw
                screenshot_path = await take_screenshot_raw(prefix="approval")
            except Exception:
                screenshot_path = None

            approval = await request_approval(
                agent_id=action.agent_id,
                session_id=action.session_id,
                action_type=action_type,
                target=action.target,
                reason=decision.reason,
                risk_level=cap_risk,
                app_name=current_app,
                app_trust=app_trust_level.value,
                screenshot_path=screenshot_path,
            )

            if approval.status != "approved":
                return RoninResult(
                    status=RoninActionStatus.APPROVAL_REQUIRED,
                    action_type=action_type,
                    error=f"Action {approval.status}: {decision.reason}",
                    approval_id=approval.id,
                )

        # ── 8. Take before-screenshot ────────────────────────────
        screenshot_before: str | None = None
        if posture_permissions.get("ronin_screenshots_enabled", False):
            try:
                from shogun.ronin.desktop.screenshot_controller import take_screenshot_raw
                screenshot_before = await take_screenshot_raw(prefix="before")
            except Exception:
                pass

        # ── 9. Execute via action router ─────────────────────────
        result = await route_action(action)

        # ── 10. Take after-screenshot ────────────────────────────
        screenshot_after: str | None = None
        if posture_permissions.get("ronin_screenshots_enabled", False):
            try:
                from shogun.ronin.desktop.screenshot_controller import take_screenshot_raw
                screenshot_after = await take_screenshot_raw(prefix="after")
            except Exception:
                pass

        # ── 11. Record timing ────────────────────────────────────
        duration_ms = int((time.monotonic() - start_time) * 1000)
        result.screenshot_before = screenshot_before
        result.screenshot_after = screenshot_after
        result.duration_ms = duration_ms

        # ── 12. Audit log ────────────────────────────────────────
        await RoninAuditLogger.log_action(
            event_type=f"ronin.action.{action_type}",
            action=f"Ronin: {action_type} → {result.status.value}",
            agent_id=action.agent_id,
            session_id=action.session_id,
            action_type=action_type,
            target=action.target,
            result=result.status.value,
            severity="info" if result.status == RoninActionStatus.SUCCESS else "warn",
            risk_level=cap_risk,
            app_trust=app_trust_level.value,
            environment_type=self._environment.environment_type.value if self._environment else None,
            screenshot_before=screenshot_before,
            screenshot_after=screenshot_after,
            confidence=result.confidence,
            verified=result.verified,
            duration_ms=duration_ms,
        )

        # ── 13. Gensui telemetry ─────────────────────────────────
        try:
            from shogun.ronin.telemetry.gensui_publisher import publish_action
            await publish_action(action_type, result.status.value, current_app)
        except Exception:
            pass

        return result

    async def _get_posture_permissions(self) -> dict[str, Any]:
        """Get the current Ronin posture permissions from the Shogun posture store."""
        try:
            from shogun.api.security import _get_agent_posture
            posture = await _get_agent_posture()
            return posture
        except Exception as exc:
            log.error("Ronin: failed to get posture: %s", exc)
            return {"ronin_enabled": False, "ronin_posture": "disabled"}

    def get_environment(self) -> EnvironmentInfo | None:
        """Get the detected environment info."""
        return self._environment


# ── Module-level singleton ───────────────────────────────────────────

_controller: RoninController | None = None


def get_controller() -> RoninController:
    """Get or create the singleton RoninController."""
    global _controller
    if _controller is None:
        _controller = RoninController()
    return _controller


async def execute_action(action: RoninAction) -> RoninResult:
    """Convenience function — execute a Ronin action through the controller."""
    controller = get_controller()
    return await controller.execute(action)
