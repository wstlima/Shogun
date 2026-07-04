# Microsoft Teams security model

All Teams text is untrusted. Katana validates the tenant, channel, identity,
enabled command group, role, and risk before any dispatch. Unknown users are
created as Viewer. Attachments are rejected by default.

Risk L0 is read-only; L1 creates low-risk tasks; L2 starts controlled workflows;
L3 needs elevated operation or approval; L4 is critical control. Pause, resume,
and Harakiri never execute from casual text. Gensui confirmation remains
mandatory, fleet Harakiri defaults to dual approval, and every decision is
audited with a correlation ID.

The database stores secret references, never Microsoft client-secret values.
Diagnostic exports omit secret references, raw messages, and user identifiers.
Production deployments must authenticate the bridge-to-Shogun API, use HTTPS,
verify Entra identities, restrict tenants/channels, and apply network controls.
