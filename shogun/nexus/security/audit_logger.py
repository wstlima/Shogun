"""Nexus security audit logger."""

from __future__ import annotations

import logging
from typing import Any
from shogun.db.models.nexus import ExternalAgentModel, NexusTaskModel
from shogun.services.event_logger import EventLogger

logger = logging.getLogger(__name__)


class NexusAuditLogger:
    """Provides structured auditing for Nexus External Gateway actions."""

    @staticmethod
    async def log_task_received(task: NexusTaskModel, agent: ExternalAgentModel) -> str:
        """Log when an external task is received at the gateway boundary."""
        return await EventLogger.emit(
            category="governance",
            event_type="nexus.task_received",
            action=f"Received Nexus Task {task.id} from {agent.name} ({agent.platform})",
            agent_id=str(task.source_agent_id),
            user_id="external_agent",
            data_classification=task.data_sensitivity,
            detail={
                "task_id": str(task.id),
                "requested_action": task.requested_action,
                "source_platform": task.source_platform,
                "source_protocol": task.source_protocol,
                "data_sensitivity": task.data_sensitivity,
            }
        )

    @staticmethod
    async def log_policy_decision(
        task: NexusTaskModel,
        agent: ExternalAgentModel,
        allowed: bool,
        reason: str,
        policy_ref: str = "nexus_gateway_policy_v1"
    ) -> str:
        """Log the result of evaluating security policy on the task."""
        decision = "ALLOW" if allowed else "BLOCK"
        severity = "info" if allowed else "warn"
        result = "success" if allowed else "blocked"
        
        return await EventLogger.emit_policy_event(
            event_type="nexus.policy_evaluation",
            action=f"Policy evaluation: {decision} for task {task.id}",
            policy_ref=policy_ref,
            policy_decision=decision,
            policy_reason=reason,
            risk_score="high" if not allowed else "low",
            severity=severity,
            result=result,
            agent_id=str(task.source_agent_id),
            detail={
                "task_id": str(task.id),
                "agent_name": agent.name,
                "requested_action": task.requested_action,
                "reason": reason,
            }
        )

    @staticmethod
    async def log_task_completion(
        task: NexusTaskModel,
        agent: ExternalAgentModel,
        status: str,
        latency_ms: int,
        error_msg: str | None = None
    ) -> str:
        """Log the final outcome and execution metrics of the task."""
        result = "success" if status == "completed" else "failed"
        severity = "info" if status == "completed" else "error"
        event_type = "nexus.task_completed" if status == "completed" else "nexus.task_failed"
        
        return await EventLogger.emit(
            category="governance",
            event_type=event_type,
            action=f"External task {task.id} execution {status}",
            result=result,
            severity=severity,
            agent_id=str(task.source_agent_id),
            duration_ms=latency_ms,
            detail={
                "task_id": str(task.id),
                "agent_name": agent.name,
                "status": status,
                "error": error_msg,
                "latency_ms": latency_ms,
            }
        )
