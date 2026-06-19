"""Nexus capability to permission mapping module."""

from __future__ import annotations

# Map capabilities to internal tools they are allowed to execute
CAPABILITY_TOOL_MAP = {
    "spreadsheet.analyze": ["read_file", "write_file", "view_file", "analyze_spreadsheet"],
    "document.summarize": ["read_file", "view_file", "summarize_text"],
    "email.draft": ["draft_email", "get_contacts"],
    "crm.prepare_update": ["crm_read", "crm_write_draft"],
    "browser.research": ["open_browser_url", "read_browser_page"],
    "file.analyze": ["read_file", "view_file"]
}


class PermissionMapper:
    """Translates external capabilities to granular tool permissions and limits."""

    @staticmethod
    def get_allowed_tools(requested_action: str) -> list[str]:
        """Determine which tools are permitted for a given action.
        
        Returns:
            List of permitted tool names.
        """
        action = requested_action.lower()
        
        # Exact match
        if action in CAPABILITY_TOOL_MAP:
            return CAPABILITY_TOOL_MAP[action]
            
        # Prefix match
        category = action.split(".")[0] if "." in action else action
        for cap, tools in CAPABILITY_TOOL_MAP.items():
            if cap.startswith(category):
                return tools
                
        # Safe default: no tools allowed
        return []
