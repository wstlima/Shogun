"""Approval Gate — WebSocket-based real-time approval for high-risk Ronin actions.

When a Ronin action requires operator approval (based on posture, risk, or
app trust), the Approval Gate:
1. Creates an approval request with full context
2. Pushes it to the Tenshu UI via activity stream / WebSocket
3. Blocks the action until approved, denied, or timed out
4. Falls back to a queue if no WebSocket listener is connected
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

log = logging.getLogger("shogun.ronin.approval_gate")


@dataclass
class ApprovalRequest:
    """A pending approval request for a high-risk Ronin action."""

    id: str = field(default_factory=lambda: f"apr_{uuid.uuid4().hex[:12]}")
    agent_id: str | None = None
    session_id: str | None = None
    action_type: str = ""
    target: str | None = None
    reason: str = ""
    risk_level: str = "high"
    app_name: str | None = None
    app_trust: str | None = None
    screenshot_path: str | None = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    status: str = "pending"  # pending | approved | denied | timeout
    decision_by: str | None = None  # operator, gensui, timeout
    decision_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "action_type": self.action_type,
            "target": self.target,
            "reason": self.reason,
            "risk_level": self.risk_level,
            "app_name": self.app_name,
            "app_trust": self.app_trust,
            "screenshot_path": self.screenshot_path,
            "created_at": self.created_at,
            "status": self.status,
            "decision_by": self.decision_by,
            "decision_at": self.decision_at,
        }


# ── In-memory state ──────────────────────────────────────────────────

_pending: dict[str, ApprovalRequest] = {}
_waiters: dict[str, asyncio.Event] = {}
_history: list[ApprovalRequest] = []  # Last 100 decisions
_MAX_HISTORY = 100
_DEFAULT_TIMEOUT_SECONDS = 300  # 5 minutes


async def request_approval(
    *,
    agent_id: str | None = None,
    session_id: str | None = None,
    action_type: str,
    target: str | None = None,
    reason: str = "",
    risk_level: str = "high",
    app_name: str | None = None,
    app_trust: str | None = None,
    screenshot_path: str | None = None,
    timeout_seconds: int = _DEFAULT_TIMEOUT_SECONDS,
) -> ApprovalRequest:
    """Create an approval request and wait for operator response.

    Blocks until approved, denied, or timeout. The operator responds
    via the API (POST /ronin/approvals/{id}).

    Returns the completed ApprovalRequest with status set.
    """
    req = ApprovalRequest(
        agent_id=agent_id,
        session_id=session_id,
        action_type=action_type,
        target=target,
        reason=reason,
        risk_level=risk_level,
        app_name=app_name,
        app_trust=app_trust,
        screenshot_path=screenshot_path,
    )

    event = asyncio.Event()
    _pending[req.id] = req
    _waiters[req.id] = event

    log.info(
        "Ronin: approval requested — id=%s action=%s risk=%s app=%s",
        req.id, action_type, risk_level, app_name,
    )

    # Emit audit event
    try:
        from shogun.ronin.core.audit_logger import RoninAuditLogger
        await RoninAuditLogger.log_approval_requested(
            action_type=action_type,
            reason=reason,
            approval_id=req.id,
            agent_id=agent_id,
            session_id=session_id,
            risk_level=risk_level,
        )
    except Exception:
        pass

    # Wait for operator response or timeout
    try:
        await asyncio.wait_for(event.wait(), timeout=timeout_seconds)
    except asyncio.TimeoutError:
        req.status = "timeout"
        req.decision_by = "timeout"
        req.decision_at = datetime.now(timezone.utc).isoformat()
        log.warning("Ronin: approval timed out — id=%s action=%s", req.id, action_type)

    # Cleanup and archive
    _pending.pop(req.id, None)
    _waiters.pop(req.id, None)
    _history.append(req)
    if len(_history) > _MAX_HISTORY:
        _history.pop(0)

    return req


def respond_to_approval(approval_id: str, decision: str, decided_by: str = "operator") -> bool:
    """Approve or deny a pending request. Called from the API.

    Args:
        approval_id: The approval request ID.
        decision: "approved" or "denied".
        decided_by: Who made the decision ("operator", "gensui").

    Returns True if the request was found and responded to.
    """
    req = _pending.get(approval_id)
    if not req:
        log.warning("Ronin: approval response for unknown id=%s", approval_id)
        return False

    req.status = decision
    req.decision_by = decided_by
    req.decision_at = datetime.now(timezone.utc).isoformat()

    event = _waiters.get(approval_id)
    if event:
        event.set()

    log.info(
        "Ronin: approval %s — id=%s by=%s action=%s",
        decision, approval_id, decided_by, req.action_type,
    )
    return True


def get_pending() -> list[dict[str, Any]]:
    """Return all pending approval requests as dicts."""
    return [req.to_dict() for req in _pending.values()]


def get_history(limit: int = 50) -> list[dict[str, Any]]:
    """Return recent approval history."""
    return [req.to_dict() for req in _history[-limit:]]


def cancel_all(reason: str = "session_closed") -> int:
    """Cancel all pending approvals. Returns count cancelled."""
    count = 0
    for req_id in list(_pending.keys()):
        req = _pending[req_id]
        req.status = "denied"
        req.decision_by = reason
        req.decision_at = datetime.now(timezone.utc).isoformat()
        event = _waiters.get(req_id)
        if event:
            event.set()
        count += 1
    log.info("Ronin: cancelled %d pending approvals (%s)", count, reason)
    return count
