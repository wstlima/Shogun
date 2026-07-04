# Microsoft Teams troubleshooting

- **Bot does not receive messages:** verify the Azure Bot endpoint is public
  HTTPS, points to `/api/messages`, and the Teams app is installed in that scope.
- **Channel message ignored:** mention the bot directly and confirm the channel
  is allowed in Katana.
- **Tenant unauthorized:** copy the tenant ID from the activity/Entra tenant into
  Katana's allowed tenants list.
- **User can only read status:** new identities intentionally start as Viewer.
- **Manifest generation fails:** configure a valid Bot/App ID first.
- **Proactive message fails:** the app must already be installed and a
  conversation reference must have been captured.
- **Shogun unreachable:** check bridge health on port 3979, the internal API URL,
  private network route, and injected bridge credential.

Use Katana → Microsoft Teams → Diagnostics and export the redacted diagnostic
bundle. Correlation IDs connect the Teams response to the Katana audit record.
