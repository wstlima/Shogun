# Microsoft Teams setup guide

1. In Katana → Microsoft Teams → Setup Wizard, choose local development or the
   recommended customer-hosted bridge mode.
2. Register an application and Azure Bot in the customer's Microsoft Entra
   tenant. Record the tenant ID and application ID.
3. Put the client secret or certificate in the enterprise secret store. Enter
   only its reference in Katana.
4. Deploy `bridge/teams` behind public HTTPS. Configure the Azure Bot messaging
   endpoint as `https://<bridge-host>/api/messages`.
5. Add the tenant ID, App ID, public endpoint, and valid domain in Katana.
6. Enable SSO and Graph only after the corresponding Entra consent is complete.
7. Generate the Teams app package, upload it to the tenant app catalog, and
   install it in personal chat and the required teams/channels.
8. Promote verified identities from Viewer and run `help`, `status`, a channel
   mention, and the diagnostics checks.

For local development, use Microsoft 365 Agents Playground or a controlled dev
tunnel. Production should use an Azure-hosted or equivalent enterprise bridge.
