# Teams app manifest

Katana generates a ZIP containing `manifest.json`, `color.png`, and
`outline.png`. The manifest declares personal, team, and group-chat bot scopes;
commands for status, agents, approvals, and help; valid domains; identity
permission; and `webApplicationInfo` when SSO is enabled.

The generated icons are safe placeholders and should be replaced with approved
Shogun/customer artwork before production publication. Revalidate and regenerate
the package after changing the App ID, valid domains, scopes, or SSO settings.
