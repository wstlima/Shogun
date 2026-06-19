"""Nexus gateway response handler module."""

from __future__ import annotations

import time
from typing import Any

from shogun.db.models.nexus import NexusTaskModel
from shogun.nexus.schemas.nexus_response import NexusResponse


class ResponseHandler:
    """Formats internal outcomes and errors into protocol-compliant responses."""

    @staticmethod
    def package_response(task: NexusTaskModel, audit_event_id: str | None = None) -> NexusResponse:
        """Create a standard response payload wrapper from a task record."""
        # Check if error is stored inside results dict
        error_msg = task.result.get("error") if isinstance(task.result, dict) else None
        
        # Strip internal error key from results if present
        cleaned_result = {k: v for k, v in task.result.items() if k != "error"} if isinstance(task.result, dict) else {}

        return NexusResponse(
            task_id=task.id,
            status=task.status,
            result=cleaned_result,
            error=error_msg,
            audit_event_id=audit_event_id,
            ts=time.time()
        )
