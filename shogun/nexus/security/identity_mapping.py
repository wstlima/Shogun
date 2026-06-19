"""Nexus identity mapping module."""

from __future__ import annotations


class IdentityMapper:
    """Maps external enterprise agent identities to internal Shogun context attributes."""

    @staticmethod
    def map_identity(source_agent_id: str, platform: str) -> dict[str, str]:
        """Map external identities to internal ones.
        
        Returns:
            dict containing internal_operator_name and description.
        """
        platform_normalized = platform.lower()
        
        if platform_normalized == "microsoft_365":
            operator = f"M365 Agent ({source_agent_id[:8]})"
        elif platform_normalized == "salesforce":
            operator = f"SFDC Agent ({source_agent_id[:8]})"
        elif platform_normalized == "google":
            operator = f"Google Agent ({source_agent_id[:8]})"
        elif platform_normalized == "servicenow":
            operator = f"SNow Agent ({source_agent_id[:8]})"
        else:
            operator = f"External Agent ({source_agent_id[:8]})"

        return {
            "internal_operator_name": operator,
            "mapped_user_role": "external_service_account"
        }
