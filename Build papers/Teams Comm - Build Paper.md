Build Paper: Microsoft Teams Adapter for Shogun AFM Katana
1. Purpose

Build a full Microsoft Teams communication adapter for Shogun AFM, added as a new tab under Katana, parallel to the existing Telegram adapter.

The adapter must allow users to communicate with Shogun from Microsoft Teams, receive notifications, approve or reject agent actions, execute authorized commands, inspect fleet status, and interact with Gensui-controlled agent workflows from within Teams.

This is not an MVP. Build this as a production-grade enterprise adapter.

The feature should strengthen Shogun AFM as a governed agent fleet platform. This aligns directly with the Alpha Horizon principle that AI strategy should preserve organizational freedom and avoid dependency on a single model, provider, or architecture.

2. Product Concept
Feature name

Katana: Microsoft Teams Adapter

Product positioning

Microsoft Teams becomes an enterprise command channel for Shogun AFM.

The user can communicate with Shogun through Teams, but Teams must not become the core orchestration layer. Teams is only the collaboration and command surface.

Teams = communication channel
Katana = command channel management
Gensui = governance, authorization, policy, audit, and control
Shogun = agent execution and orchestration

3. Important Technical Decision

Do not implement this as a simple incoming webhook.

Incoming webhooks are acceptable only for very basic one-way alerts. This adapter must support two-way communication, user identity, commands, approvals, proactive notifications, channel routing, audit, and role-based control.

Build it as a proper Microsoft Teams Bot / Teams App integration.

Microsoft currently recommends the Microsoft 365 Agents Toolkit for Teams app and bot development. Microsoft’s own documentation also notes that the older Bot Framework SDK is no longer actively updated or maintained, and new agent/bot experiences should consider the Microsoft 365 Agents SDK / Teams SDK path.

Because Shogun’s backend is Python/FastAPI but Microsoft’s Teams SDK Python support is still less mature than JavaScript/C# options, the recommended architecture is:

A dedicated Teams Bridge service
built using the current Microsoft Teams / Microsoft 365 Agents Toolkit stack, talking to Shogun’s FastAPI backend through an internal authenticated API.

This keeps Shogun clean, avoids forcing Microsoft-specific bot plumbing into the core runtime, and preserves the future ability to add Slack, email, Discord, Telegram, or other channels through the same Katana adapter interface.

4. Required User Experience

A new tab must be added under Katana:

Existing:

Katana
Telegram Adapter

New:

Katana
Telegram Adapter
Microsoft Teams Adapter

The Teams Adapter tab must provide a full configuration and operations console.

Katana Teams tab sections

The tab must include:

Overview
Adapter enabled/disabled state
Connection health
Teams bot status
Tenant status
Last inbound message
Last outbound notification
Last proactive notification
Active approval requests
Error state
Setup Wizard
Step-by-step configuration
Tenant ID
Bot/App ID
Client secret / certificate reference
Public messaging endpoint
Manifest generation
Manifest download
Teams installation checklist
Test personal chat
Test channel mention
Test proactive notification
Microsoft Entra / SSO
Tenant configuration
Allowed tenants
Single-tenant or multi-tenant mode
SSO status
User identity mapping
Role mapping from Teams/Entra users to Shogun roles
Command Routing
Enable/disable supported command groups
Personal chat commands
Channel commands
Group chat commands
Agent routing rules
Default agent or fleet target
Allowed teams/channels
Notifications
Configure proactive notifications
Route alerts to personal chat, channel, or admin group
Configure severity thresholds
Configure Komainu watchdog alerts
Configure Harakiri confirmation alerts
Configure workflow completion alerts
Approval Cards
Configure approval policy
Configure approval roles
Configure dual approval requirements
Configure expiry time
Configure allowed actions
Security Policy
Allowed commands
Risk levels
Confirmation rules
Rate limits
Tenant restrictions
Channel restrictions
Disable destructive commands from Teams if needed
Audit Log
Inbound messages
Parsed commands
User identity
Authorization decision
Gensui command result
Teams response
Approval actions
Failed commands
Security denials
Diagnostics
Test Bot endpoint
Test Shogun backend
Test Gensui command router
Test Microsoft Graph credentials
Test proactive conversation reference
Test Adaptive Card submit
Validate Teams manifest
Export diagnostic bundle
5. Deployment Reality

The coding agent must handle this correctly.

A Microsoft Teams bot normally requires a public HTTPS messaging endpoint reachable by Microsoft’s cloud. A fully local Shogun instance behind a firewall cannot receive Teams bot callbacks unless one of the following exists:

Public reverse proxy
Customer-hosted Azure App Service / Container App
DMZ relay
Cloudflare Tunnel / enterprise tunnel
Development tunnel such as ngrok or Microsoft dev tunnel

Therefore the full build must support these modes:

Mode A: Local development

Used by developer.

Local Shogun backend
Local Teams Bridge
Public tunnel to Teams Bridge
Test tenant
Test Teams app package
Mode B: Customer-hosted enterprise bridge

Recommended production mode.

Teams Bridge hosted in the customer’s Microsoft/Azure tenant
Bridge communicates with local or hosted Shogun backend through secure outbound API
No direct Microsoft dependency inside Shogun core
Enterprise controls app registration, secrets, consent, and policies
Mode C: Direct Shogun callback

Allowed but not preferred.

Shogun exposes a public HTTPS endpoint directly
Teams calls Shogun backend
Simpler, but less clean architecturally

The build must support Mode A and Mode B. Mode C may be supported as an advanced deployment option.

6. Functional Requirements
6.1 Personal chat

Users must be able to open a direct Teams chat with Shogun and write commands such as:

status
agents
show active agents
run procurement analysis
ask samurai-02 to summarize today's activity
pause agent samurai-04
show pending approvals
help

The bot must respond with clean text or Adaptive Cards.

6.2 Channel and group chat

Users must be able to mention the bot in a Teams channel or group chat:

@Shogun status
@Shogun show active workflows
@Shogun run weekly sales analysis
@Shogun pause agent samurai-03
@Shogun summarize this workflow

In Teams channels and group chats, bots normally receive messages when the bot is directly mentioned with @botname. The adapter must therefore support mention parsing and remove the mention from the command text before command processing.

6.3 Proactive notifications

Gensui and Shogun must be able to push proactive messages into Teams.

Examples:

Komainu watchdog paused Samurai-04.
New Shogun instance discovered on the network.
Agent Samurai-02 requests approval to access an external website.
Workflow "Supplier Risk Analysis" completed successfully.
Harakiri command requested for agent group "Research Agents".

Microsoft Teams proactive messaging requires the app to be installed for the user, team, or chat context. Microsoft Graph can be used for app installation and proactive messaging setup where tenant policy allows it.

6.4 Approval workflows

The adapter must support Adaptive Card approvals.

Example card:

Agent Action Approval Required

Agent: Samurai-02
Requested action: Access external supplier portal
Risk level: Medium
Workflow: Supplier Risk Analysis
Requested by: Michael Peric
Expires: 15 minutes

[Approve] [Reject] [View Details]

Approval card actions must be single-use, time-limited, auditable, and linked to a Gensui approval request.

6.5 Harakiri / shutdown control

Teams may be used for shutdown and pause commands, but only under strict control.

Examples:

@Shogun pause agent samurai-02
@Shogun pause group research-agents
@Shogun harakiri agent samurai-02
@Shogun harakiri fleet

Rules:

Harakiri commands must never execute directly from a single casual message.
High-risk commands require confirmation.
Fleet-level shutdown requires admin role.
Fleet-level shutdown should support dual approval.
Confirmation must include an expiring confirmation code.
All shutdown commands must be audited.
The Teams adapter must never bypass Gensui policy.
7. Command Model

Build a unified command abstraction so Telegram and Teams can eventually use the same command router.

Create or extend a shared Katana command channel interface.

CommandEnvelope

Every inbound Teams message must be normalized into a command envelope:

{
  "source": "microsoft_teams",
  "adapter_version": "1.0.0",
  "correlation_id": "uuid",
  "tenant_id": "microsoft-tenant-id",
  "team_id": "teams-team-id-or-null",
  "channel_id": "teams-channel-id-or-null",
  "chat_id": "teams-chat-id-or-null",
  "conversation_type": "personal|channel|groupchat",
  "message_id": "teams-message-id",
  "reply_to_id": "teams-reply-id-or-null",
  "user": {
    "teams_user_id": "teams-user-id",
    "aad_object_id": "entra-object-id",
    "display_name": "user display name",
    "user_principal_name": "email-or-upn"
  },
  "raw_text": "original message",
  "normalized_text": "message without bot mention",
  "command_name": "status|agents|run|ask|pause|harakiri|approve|reject|help",
  "arguments": {},
  "attachments": [],
  "risk_level": "L0|L1|L2|L3|L4",
  "requires_approval": false,
  "received_at": "timestamp"
}
ResponseEnvelope

All Shogun/Gensui responses should be converted into a channel-neutral response envelope before being rendered into Teams:

{
  "correlation_id": "uuid",
  "target": {
    "source": "microsoft_teams",
    "conversation_reference_id": "id",
    "reply_to_id": "optional"
  },
  "response_type": "text|adaptive_card|approval_card|error|status_card",
  "title": "optional",
  "text": "message text",
  "card_payload": {},
  "severity": "info|success|warning|critical",
  "actions": [],
  "created_at": "timestamp"
}
8. Supported Commands

The full build must support at least the following command groups.

8.1 Help
help
help agents
help approvals
help security

Response must show available commands based on user role.

8.2 Fleet status
status
fleet status
show active agents
show agent samurai-02
show workflows

Must return:

Shogun instance status
Gensui status
Active agents
Active workflows
Paused agents
Failed workflows
Pending approvals
Komainu status
8.3 Agent interaction
ask samurai-02 <message>
ask default <message>
route to research-agent <message>

Must support:

Direct agent targeting
Default agent fallback
Agent group routing
Policy validation before sending to agent
8.4 Workflow execution
run workflow supplier-risk-analysis
run workflow weekly-report with period=this_week
start procurement-analysis

Must support:

Named workflow lookup
Parameter parsing
Confirmation if workflow is high-risk
Result delivery back to Teams
8.5 Pause / resume
pause agent samurai-02
resume agent samurai-02
pause group research-agents
resume group research-agents

Must require proper operator/admin role.

8.6 Harakiri
harakiri agent samurai-02
harakiri group research-agents
harakiri fleet

Must require:

Admin/security role
Explicit confirmation
Confirmation code
Audit trail
Optional dual approval for fleet-level action
8.7 Approvals
show pending approvals
approve REQ-12345
reject REQ-12345

Must also support Adaptive Card buttons.

8.8 Logs and summaries
summarize today
summarize agent samurai-02
show last 10 events
show errors

Must return clean operational summaries, not raw logs unless requested by an admin.

9. Risk Classification

Every command must be classified before execution.

L0 — Read-only

Examples:

status
help
show agents
summarize activity

Allowed for viewer role.

L1 — Low-risk task creation

Examples:

ask agent
create passive research task
summarize document

Allowed for standard operator role.

L2 — Controlled workflow execution

Examples:

run internal analysis workflow
start non-destructive automation

Requires operator role.

L3 — External action or system access

Examples:

access external website
use browser profile
call API
write file
send email draft
process sensitive data

Requires elevated operator role or approval.

L4 — Critical control

Examples:

pause agent group
Harakiri
shutdown fleet
credential-related action
system-level desktop action
Ronin-mode action

Requires admin/security role, confirmation, and audit. Some commands require dual approval.

10. Security Requirements
10.1 Tenant validation

The adapter must reject messages from unknown Microsoft tenants.

Store allowed tenant IDs in configuration.

10.2 User identity mapping

Teams users must be mapped to Shogun users/roles using Entra identity.

Required fields:

Entra object ID
Teams user ID
UPN/email
Display name
Shogun role
Last seen
Allowed command groups
10.3 Role-based access control

Minimum roles:

Viewer
Operator
Senior Operator
Admin
Security Admin

No destructive command may execute without proper role.

10.4 SSO

Use Microsoft Entra ID SSO for production. Microsoft Teams bot SSO requires configuration across Azure Bot Service, Entra App Registration, and the Teams app manifest.

Development mode may support manual pairing, but production must support SSO.

10.5 No credential leakage

Never expose:

API keys
Bot secrets
Client secrets
Refresh tokens
Browser profile cookies
Internal filesystem paths
Full prompt payloads unless admin explicitly requests debug export

Secrets must be stored through the existing Shogun secret-handling pattern. If no secure secret store exists, implement encrypted-at-rest storage and document the limitation.

10.6 Prompt injection control

Teams messages are untrusted input.

The Teams adapter must not allow free-form text to directly trigger high-risk tools.

Rules:

Commands are parsed deterministically first.
Natural language may create a proposed task.
Gensui must approve whether the proposed task can execute.
High-risk tool calls must pass through policy and approval.
Attachments must be disabled by default or handled in read-only mode until scanned.
10.7 Rate limiting

Implement:

Per-user rate limits
Per-channel rate limits
Per-command risk-level limits
Burst protection
Lockout after repeated unauthorized high-risk attempts
10.8 Audit

Every inbound and outbound Teams action must be audited.

Audit fields:

Timestamp
Tenant ID
User ID
Team/channel/chat ID
Raw command
Normalized command
Parsed intent
Risk level
Authorization result
Gensui command ID
Agent/workflow affected
Teams response ID
Approval ID
Error details
Correlation ID
11. Data Model

Add database migrations for the Teams adapter.

Use the existing Shogun persistence pattern. If Shogun currently uses SQLite locally and can later move to PostgreSQL, keep the schema portable.

Suggested tables
katana_teams_config

Stores adapter config.

Fields:

id
enabled
deployment_mode
tenant_mode
allowed_tenant_ids
bot_app_id
bot_name
public_messaging_endpoint
graph_enabled
proactive_enabled
sso_enabled
created_at
updated_at
katana_teams_secret_refs

Do not store raw secrets if a secret store exists.

Fields:

id
config_id
secret_name
secret_ref
created_at
updated_at
katana_teams_user_map

Maps Teams users to Shogun users.

Fields:

id
tenant_id
teams_user_id
aad_object_id
user_principal_name
display_name
shogun_user_id
shogun_role
allowed_command_groups
last_seen_at
created_at
updated_at
katana_teams_conversations

Stores conversation references for replies and proactive notifications.

Fields:

id
tenant_id
conversation_type
team_id
channel_id
chat_id
conversation_reference_json
service_url
bot_id
last_activity_id
installed
proactive_enabled
created_at
updated_at
katana_teams_command_log

Stores command audit.

Fields:

id
correlation_id
tenant_id
user_id
aad_object_id
conversation_id
raw_text
normalized_text
command_name
arguments_json
risk_level
authorization_result
gensui_command_id
response_type
success
error_code
created_at
katana_teams_approval_requests

Stores approval metadata.

Fields:

id
approval_request_id
teams_message_id
conversation_id
requested_by_user_id
required_role
risk_level
status
expires_at
approved_by_user_id
rejected_by_user_id
action_payload_json
created_at
updated_at
katana_teams_notification_routes

Stores routing rules.

Fields:

id
route_name
severity
event_type
target_type
target_conversation_id
enabled
created_at
updated_at
12. Backend API Requirements

Add FastAPI endpoints under the existing API structure.

Suggested path:

/backend/app/api/v1/katana/teams.py
Configuration endpoints
GET /api/v1/katana/teams/config
PUT /api/v1/katana/teams/config
POST /api/v1/katana/teams/enable
POST /api/v1/katana/teams/disable
Setup and diagnostics
GET /api/v1/katana/teams/health
POST /api/v1/katana/teams/test/backend
POST /api/v1/katana/teams/test/graph
POST /api/v1/katana/teams/test/proactive-message
POST /api/v1/katana/teams/test/adaptive-card
POST /api/v1/katana/teams/diagnostics/export
Manifest
POST /api/v1/katana/teams/manifest/generate
GET /api/v1/katana/teams/manifest/download
POST /api/v1/katana/teams/manifest/validate

Microsoft 365 / Teams apps are defined through an app manifest that describes how the app integrates with Microsoft 365 and Teams. The generated manifest must include bot capabilities, valid domains, scopes, command lists, and SSO configuration where enabled.

Command logs
GET /api/v1/katana/teams/commands
GET /api/v1/katana/teams/commands/{correlation_id}
Users and roles
GET /api/v1/katana/teams/users
PUT /api/v1/katana/teams/users/{id}/role
POST /api/v1/katana/teams/users/sync
Notification routes
GET /api/v1/katana/teams/notification-routes
POST /api/v1/katana/teams/notification-routes
PUT /api/v1/katana/teams/notification-routes/{id}
DELETE /api/v1/katana/teams/notification-routes/{id}
Approval policies
GET /api/v1/katana/teams/approval-policies
PUT /api/v1/katana/teams/approval-policies
13. Teams Bridge Service

Create a separate service:

/bridge/teams/

Recommended implementation:

TypeScript
Microsoft 365 Agents Toolkit generated project
Teams SDK / Microsoft 365 Agents SDK path
Internal API client to Shogun FastAPI backend

The Teams Bridge must expose the public Teams bot messaging endpoint.

Suggested endpoints:

POST /api/teams/messages
GET /api/teams/health
GET /api/teams/version

The bridge must:

Receive Teams bot activities
Validate Microsoft/Bot authentication
Normalize activity into CommandEnvelope
Send command envelope to Shogun backend
Receive ResponseEnvelope
Render the response into Teams text or Adaptive Card
Store/update conversation references
Support proactive messages
Support Adaptive Card action submit events
Support channel mentions and personal chat

The bridge must not contain agent logic. It is only a channel adapter.

14. Internal Shogun Command API

Create or reuse an internal Gensui/Katana command endpoint:

POST /api/v1/katana/command/dispatch

Request:

{
  "command_envelope": {}
}

Response:

{
  "response_envelope": {}
}

This endpoint must:

Validate adapter source
Validate tenant
Resolve user
Apply RBAC
Classify risk
Dispatch to Gensui
Return a safe response
Write audit log

No Teams-specific logic should exist inside Gensui beyond generic command-channel metadata.

15. Teams App Manifest Requirements

Generate a Teams app package from Katana.

The package must include:

manifest.json
color.png
outline.png

Manifest must support:

Personal scope
Team scope
Group chat scope
Bot command lists
Valid domains
SSO configuration when enabled
App name: Shogun AFM
Short name: Shogun
Description: Agent Fleet Management command channel for Shogun AFM
Developer: Alpha Horizon or configurable customer value

Bot scopes:

[
  "personal",
  "team",
  "groupchat"
]

Command list examples:

[
  {
    "title": "status",
    "description": "Show Shogun fleet status"
  },
  {
    "title": "agents",
    "description": "Show active agents"
  },
  {
    "title": "approvals",
    "description": "Show pending approvals"
  },
  {
    "title": "help",
    "description": "Show available commands"
  }
]
16. Adaptive Cards

Use Adaptive Cards for structured operational actions. Adaptive Cards are JSON-based UI snippets that render natively in host applications such as Microsoft Teams.

Required card types:

16.1 Fleet status card

Shows:

Fleet health
Active agents
Paused agents
Errors
Pending approvals
Last incident
Open Katana button, where configured
16.2 Agent status card

Shows:

Agent name
Agent ID
State
Current workflow
Memory status
Security posture
Last action
Available actions based on role
16.3 Approval card

Shows:

Request ID
Agent
Workflow
Requested action
Risk level
Requesting user
Expiry
Approve button
Reject button
Details button
16.4 Harakiri confirmation card

Shows:

Scope
Impact
Requested by
Required confirmation text
Expiry
Confirm button
Cancel button
16.5 Error card

Shows:

Error type
Human-readable explanation
Correlation ID
Suggested next step
Diagnostics link in Katana
17. Proactive Notification Design

Gensui events must be routed into Teams through notification routes.

Supported event types:

agent.started
agent.completed
agent.failed
agent.paused
agent.requires_approval
workflow.started
workflow.completed
workflow.failed
komainu.paused_system
gensui.instance_discovered
gensui.security_event
harakiri.requested
harakiri.executed
system.health_warning
system.health_critical

Notification routing must support:

Send to personal chat
Send to Teams channel
Send to admin/security channel
Send to multiple targets
Severity filtering
Quiet hours, optional
Deduplication
Retry logic
Failure logging
18. Frontend Build Requirements

Add a new React tab under Katana.

Suggested path:

/frontend/src/modules/katana/adapters/MicrosoftTeamsAdapterTab.tsx

Shared components should be extracted if Telegram has reusable UI patterns.

Suggested shared components:

AdapterStatusBadge
AdapterEnableToggle
AdapterHealthPanel
AdapterSetupWizard
AdapterAuditLogTable
AdapterCommandList
AdapterSecurityPolicyPanel
AdapterNotificationRoutesPanel
AdapterDiagnosticsPanel
UI quality requirements

The UI must feel like a serious enterprise configuration console, not a developer-only settings page.

Use clear states:

Not configured
Configured but disabled
Enabled but unhealthy
Enabled and healthy
Partial warning
Security warning
Test failed
Production ready
19. Setup Wizard Flow

The setup wizard must guide the user through the full installation.

Step 1: Choose deployment mode

Options:

Local development
Customer-hosted Teams Bridge
Direct Shogun endpoint
Step 2: Configure Microsoft tenant

Fields:

Tenant ID
Tenant mode
Allowed tenants
Admin consent status
Step 3: Configure bot

Fields:

Bot/App ID
Client secret reference
Public messaging endpoint
Bot display name
Step 4: Configure SSO

Fields:

Enable/disable SSO
Application ID URI
OAuth scope
Web application info
Token validation test
Step 5: Generate manifest

Actions:

Generate manifest
Validate manifest
Download Teams app package
Step 6: Install in Teams

Checklist:

Upload custom app
Install for personal chat
Install in target team/channel
Confirm bot can receive message
Step 7: Test commands

Tests:

help
status
agents
show pending approvals
Step 8: Test proactive notification

Send a test notification from Shogun to Teams.

Step 9: Security review

Show:

Enabled commands
Risk policy
Approval policy
Allowed tenants
Allowed channels
Audit enabled
20. Environment Variables

Add environment variable support.

TEAMS_ADAPTER_ENABLED=false
TEAMS_DEPLOYMENT_MODE=dev|bridge|direct
TEAMS_TENANT_MODE=single|multi
TEAMS_ALLOWED_TENANT_IDS=
TEAMS_BOT_APP_ID=
TEAMS_BOT_CLIENT_SECRET_REF=
TEAMS_PUBLIC_MESSAGING_ENDPOINT=
TEAMS_SSO_ENABLED=false
TEAMS_GRAPH_ENABLED=false
TEAMS_PROACTIVE_ENABLED=false
TEAMS_MANIFEST_VALID_DOMAINS=
TEAMS_RATE_LIMIT_PER_USER_PER_MINUTE=20
TEAMS_RATE_LIMIT_PER_CHANNEL_PER_MINUTE=60
TEAMS_HIGH_RISK_CONFIRMATION_TTL_SECONDS=300
SHOGUN_INTERNAL_API_URL=
SHOGUN_INTERNAL_API_KEY_REF=

Do not store raw secrets in normal .env files for production documentation. Use secret references.

21. Logging and Observability

The Teams adapter must log:

Startup state
Config validation result
Incoming activity received
Tenant validation result
User mapping result
Command parsing result
Authorization result
Gensui dispatch result
Teams response result
Proactive send result
Adaptive Card action result
Errors with correlation ID

Logs must redact secrets and sensitive payloads.

Every request must include a correlation_id.

22. Error Handling

The user-facing Teams response must be clean.

Examples:

Unauthorized
You are not authorized to run this command.

Command: pause agent
Required role: Operator
Your role: Viewer
Correlation ID: 8f4...
Unknown command
I did not recognize that command.

Try:
status
agents
help
show pending approvals
High-risk confirmation required
This command requires confirmation.

Command: harakiri agent samurai-02
Risk level: L4
Confirmation code: HARA-8291
Expires in: 5 minutes
Backend unavailable
Shogun is currently unreachable.

The Teams adapter is online, but the Shogun backend did not respond.
Correlation ID: 8f4...
23. Testing Requirements

This build must include automated and manual tests.

Unit tests

Test:

Mention stripping
Command parsing
Risk classification
Role mapping
Tenant validation
Approval token validation
Notification route matching
Adaptive Card payload creation
Error response generation
Integration tests

Test:

Teams Bridge to Shogun backend
Command dispatch
Gensui authorization
Proactive notification
Approval card submit
Conversation reference storage
Manifest generation
Health checks
Security tests

Test:

Unknown tenant rejected
Unknown user rejected or mapped to lowest role
Viewer cannot run operator command
Operator cannot run Harakiri fleet
Expired approval rejected
Reused approval rejected
Invalid Adaptive Card payload rejected
Malformed command rejected safely
Rate limit enforced
Manual Teams tests

Test in Microsoft Teams:

Personal chat: help
Personal chat: status
Channel: @Shogun status
Group chat: @Shogun help
Proactive test notification
Approval card approve
Approval card reject
Harakiri confirmation denied for non-admin
Harakiri confirmation works for admin with confirmation code
24. Acceptance Criteria

The build is complete only when all of the following are true:

Microsoft Teams Adapter appears as a separate tab under Katana.
Telegram Adapter remains functional.
Teams Adapter can be enabled and disabled from Katana.
Teams app manifest can be generated and downloaded.
Teams bot can receive personal chat messages.
Teams bot can receive channel/group messages when mentioned.
Teams bot can send proactive notifications.
Teams bot can render Adaptive Cards.
Approval cards work end-to-end.
User identity is mapped from Teams/Entra to Shogun role.
Commands are classified by risk level.
Unauthorized commands are blocked.
High-risk commands require confirmation.
Harakiri commands cannot bypass Gensui.
All commands are audited.
Diagnostics page shows useful health checks.
Secrets are not exposed in UI, logs, or exports.
The adapter supports production deployment through a Teams Bridge service.
Documentation is included.
The code is structured so future adapters can reuse the same Katana command-channel interface.
25. Documentation Deliverables

Create documentation:

/docs/integrations/microsoft-teams-adapter.md
/docs/integrations/microsoft-teams-setup-guide.md
/docs/integrations/microsoft-teams-security-model.md
/docs/integrations/microsoft-teams-troubleshooting.md
/docs/integrations/microsoft-teams-manifest.md

Documentation must include:

Architecture diagram
Setup steps
Required Microsoft tenant setup
Required Teams app installation steps
SSO setup
Proactive messaging setup
Security model
Command reference
Troubleshooting guide
Deployment modes
Known limitations
26. Coding Agent Instructions

Before building, inspect the existing Telegram Adapter implementation under Katana.

Reuse its structure where appropriate, but do not copy Telegram-specific assumptions into the Teams adapter.

The coding agent must:

Identify the existing Katana tab structure.
Add Microsoft Teams as a sibling adapter tab.
Extract shared adapter UI components where useful.
Create a generic command-channel abstraction.
Keep Teams-specific code isolated.
Build a Teams Bridge service.
Add backend APIs.
Add database migrations.
Add frontend configuration UI.
Add audit logging.
Add tests.
Add documentation.
Preserve existing Telegram behavior.
27. Strategic Design Principle

Do not make Shogun dependent on Microsoft Teams.

The correct design is:

Shogun can use Teams.
Shogun can be controlled through Teams.
Shogun can notify through Teams.
But Shogun must remain operational without Teams.

That is the architecture-consistent way to build this.

The Teams Adapter is a command channel, not the control plane.

Gensui remains the control plane.