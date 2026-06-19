"""Nexus security policy hooks module."""

from __future__ import annotations

import logging
from shogun.db.models.nexus import ExternalAgentModel, NexusTaskModel
from shogun.services.gensui_client import gensui_client

logger = logging.getLogger(__name__)

# Hardcoded platform capability allowances based on build paper guidelines
PLATFORM_ALLOWANCES = {
    "microsoft_365": {
        "allowed": ["document.summarize", "spreadsheet.analyze", "email.draft", "file.analyze"],
        "blocked": ["desktop.execute", "browser.login", "finance.portal_access", "ronin.harakiri", "ronin.stop"]
    },
    "salesforce": {
        "allowed": ["crm.prepare_update", "customer.summary", "case.analysis", "document.summarize"],
        "blocked": ["local_file_access", "desktop.execute", "unrestricted_browser_control", "ronin.harakiri", "ronin.stop"]
    }
}


class PolicyHooks:
    """Enforces Shogun and Gensui policy rules for external gateway operations."""

    @staticmethod
    async def evaluate_task(task: NexusTaskModel, agent: ExternalAgentModel) -> tuple[bool, bool, str]:
        """Evaluate if the task is allowed, requires approval, or must be blocked.
        
        Returns:
            (allowed: bool, approval_required: bool, reason: str)
        """
        # 1. Verify agent active status
        if not agent.is_active or agent.is_deleted:
            return False, False, f"Agent '{agent.name}' is inactive or deleted."

        # 2. Traceability check
        if not task.source_agent_id or not task.source_platform:
            return False, False, "Task is missing mandatory trace identifiers (source_agent_id or source_platform)."

        action = task.requested_action.lower()

        # 3. Block desktop and direct Ronin control by default
        if action in ("desktop.execute", "unrestricted_browser_control", "ronin.stop", "ronin.harakiri"):
            return False, False, f"Direct access to '{action}' is strictly blocked for external agents."

        # 4. Check platform-specific rules
        platform = agent.platform.lower()
        if platform in PLATFORM_ALLOWANCES:
            rules = PLATFORM_ALLOWANCES[platform]
            # Explicitly blocked
            if action in rules["blocked"]:
                return False, False, f"Action '{action}' is explicitly forbidden for platform '{platform}'."
            # Explicitly allowed list check (if configured, restrict to it)
            if rules["allowed"] and action not in rules["allowed"]:
                return False, False, f"Action '{action}' is not in the allowed list for platform '{platform}'."

        # 5. Gensui Security Posture Check
        if gensui_client.enabled:
            # Check global Nexus communications posture
            if not gensui_client.is_action_allowed("NEXUS_MESSAGE"):
                return False, False, "Gensui posture currently disables all Nexus external communication."
            
            # Map request category to Gensui actions
            category = action.split(".")[0] if "." in action else action
            if category == "browser" and not gensui_client.is_action_allowed("MADO_SESSION"):
                return False, False, "Gensui posture blocks Mado browser automation."
            if category == "desktop" and not gensui_client.is_action_allowed("RONIN_SESSION"):
                return False, False, "Gensui posture blocks Ronin desktop automation."
            if category == "file" and not gensui_client.is_action_allowed("FILE_WRITE"):
                # Check write restriction if task modifies filesystem
                if task.input_context.get("write_operation", False) and not gensui_client.is_action_allowed("FILE_WRITE"):
                    return False, False, "Gensui posture blocks file writes."

        # 6. Determine human approval requirement (e.g. sensitive data classification or specific capability)
        approval_required = task.approval_required or task.data_sensitivity == "sensitive"
        if action == "email.draft" or action == "crm.prepare_update":
            # For MVP, certain side-effect draft capabilities may prompt approval or run directly
            pass

        return True, approval_required, "Task approved by security policies."
