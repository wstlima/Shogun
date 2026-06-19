"""Nexus gateway request handler module."""

from __future__ import annotations

import logging
from typing import Any
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class RequestHandler:
    """Utility class to validate and extract raw request structures."""

    @staticmethod
    def validate_payload(payload: dict[str, Any], required_keys: list[str]) -> None:
        """Helper to ensure key parameters exist in a payload.
        
        Raises:
            HTTPException(400) if a required parameter is missing.
        """
        missing = [key for key in required_keys if key not in payload]
        if missing:
            err_msg = f"Missing required payload parameter(s): {', '.join(missing)}"
            logger.warning(err_msg)
            raise HTTPException(status_code=400, detail=err_msg)
            
    @staticmethod
    def sanitize_context(context: dict[str, Any]) -> dict[str, Any]:
        """Strip or sanitize variables if needed before processing."""
        # For security and safety, remove any hidden system arguments in context
        sanitized = {k: v for k, v in context.items() if not k.startswith("__")}
        return sanitized
