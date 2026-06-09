# Gensui — Central Command, Security Posture, and Kill-Switch Control Layer for Shogun

## 1. Purpose

Gensui is a separate server-side control program for Shogun.

It must be built as an independent application, but it must live inside the same repository as Shogun.

Gensui is not a normal Shogun instance. It is not a Samurai. It is not an Agent Flow node. It is not a local assistant.

Gensui is the central command layer.

Its role is to supervise, monitor, control, and enforce security across multiple Shogun instances, their Samurai, their tools, their memory systems, their workflows, their Nexus activity, and their connected runtime environments.

The core idea is simple:

> Individual Shogun instances can “sign up” to a Gensui server and become members of a governed control network.

Once a Shogun instance becomes a member of Gensui, that Shogun is no longer fully isolated from a governance perspective. It becomes a managed agent system under central oversight.

Gensui must be able to:

* Register and manage multiple Shogun instances.
* Monitor all member Shoguns in real time.
* Monitor all Samurai belonging to each Shogun.
* Monitor Nexus activity.
* Monitor Agent Flow executions.
* Monitor Mado browser automation.
* Monitor model routing decisions.
* Monitor tool calls.
* Monitor memory activity.
* Enforce security postures.
* Enforce one global security posture across all member Shoguns.
* Apply individual security posture overrides.
* Apply group-level security postures.
* Trigger Harakiri at individual, group, or global level.
* Provide full auditability of all monitored activity.
* Act as a server-grade governance layer for enterprise, multi-instance, or distributed Shogun deployments.

Gensui is the control tower.

Shogun instances are the field agents.

Samurai are the specialized workers.

Nexus is the communication and coordination layer.

Gensui observes, governs, and if necessary, shuts them down.

---

## 2. Naming and Concept

The name **Gensui** means commander-in-chief or marshal.

Within the Shogun architecture, this fits naturally:

* **Shogun**: the primary AI command agent.
* **Samurai**: specialized subordinate agents.
* **Mado**: browser automation engine.
* **Agent Flow**: visual workflow execution layer.
* **Archives**: persistent memory system.
* **Nexus**: communication / coordination / routing layer.
* **Torii**: local security gate / posture enforcement concept.
* **Harakiri**: emergency shutdown / self-termination / containment action.
* **Gensui**: central command authority across multiple Shoguns.

Gensui should feel like the enterprise-grade command and control extension of Shogun.

It should not dilute Shogun’s local-first philosophy. Instead, it should add a managed server option for organizations that need centralized control across many Shogun deployments.

---

## 3. Core Design Principle

Gensui must be a **separate program**.

It must not be implemented as just another page inside the existing Shogun frontend.

It must not be implemented as a normal Shogun feature module.

It must not require a Shogun instance to be running locally in order for the Gensui server to operate.

It should be built as its own server application inside the same repository.

Recommended repository structure:

```md
/shogun
  /apps
    /shogun-desktop-or-local
    /gensui-server
    /gensui-admin-ui
  /packages
    /shared-types
    /shared-security
    /shared-protocol
    /shared-telemetry
    /shared-auth
    /shared-audit
  /docs
    /gensui
```

Alternative structure is acceptable if it fits the existing repo architecture, but the separation must remain clear.

Gensui must be deployable independently.

Example deployment options:

```md
Local LAN server
Company internal server
Docker container
Cloud VM
Private VPS
On-prem enterprise server
VPN-only deployment
```

The key requirement:

> Shogun can exist without Gensui.
> Gensui can exist as a central control server for many Shoguns.
> A Shogun becomes governed only after it signs up and becomes a Gensui member.

---

## 4. High-Level Architecture

Gensui consists of five major layers:

```md
1. Gensui Server
2. Gensui Admin UI
3. Shogun Membership Client
4. Telemetry and Event Pipeline
5. Policy Enforcement and Harakiri Control Layer
```

### 4.1 Gensui Server

The Gensui Server is the authoritative backend.

It manages:

* Shogun registration.
* Membership tokens.
* Instance identity.
* Security posture definitions.
* Global policies.
* Group policies.
* Individual instance policies.
* Harakiri commands.
* Telemetry intake.
* Audit logs.
* Activity monitoring.
* Health checks.
* Command dispatching.
* Policy enforcement state.

The server must expose secure APIs for:

```md
Shogun registration
Heartbeat
Telemetry submission
Policy retrieval
Command polling or push
Harakiri execution acknowledgement
Security posture synchronization
Admin UI operations
Audit log queries
```

The server must be built for reliability, observability, and strict authorization.

---

### 4.2 Gensui Admin UI

The Gensui Admin UI is the web-based command interface for human operators.

It should provide:

* Overview dashboard.
* Registered Shogun instances.
* Online/offline status.
* Security posture status.
* Global posture controls.
* Group posture controls.
* Individual posture controls.
* Harakiri controls.
* Audit log search.
* Activity timeline.
* Samurai monitoring.
* Agent Flow monitoring.
* Nexus monitoring.
* Mado monitoring.
* Model routing monitoring.
* Tool call monitoring.
* Memory activity monitoring.
* Alerting view.
* Policy editor.
* Enrollment approvals.
* Instance grouping.

The Admin UI must be separate from the normal Shogun UI.

It may reuse shared design components if appropriate, but it must clearly be a server administration console.

---

### 4.3 Shogun Membership Client

Each Shogun instance must include a Gensui membership client.

This client is responsible for:

* Signing up to Gensui.
* Holding the membership identity.
* Sending heartbeats.
* Sending telemetry.
* Receiving security posture updates.
* Enforcing assigned posture locally.
* Receiving Harakiri commands.
* Executing local containment.
* Reporting execution status back to Gensui.
* Detecting loss of Gensui connection.
* Applying fallback behavior if disconnected.

This should be built as a modular service inside Shogun.

Suggested internal name:

```md
GensuiMembershipService
```

or:

```md
GensuiClient
```

The client must not be hardcoded to one Gensui server.

It should be configurable through:

```md
GENSUI_ENABLED=true
GENSUI_SERVER_URL=https://...
GENSUI_INSTANCE_NAME=...
GENSUI_ENROLLMENT_TOKEN=...
GENSUI_HEARTBEAT_INTERVAL_SECONDS=...
GENSUI_TELEMETRY_MODE=...
```

---

### 4.4 Telemetry and Event Pipeline

Gensui must receive events from every member Shogun.

Events should be structured, normalized, and append-only.

Example monitored event categories:

```md
shogun.lifecycle
samurai.lifecycle
agentflow.execution
agentflow.node_execution
mado.session
mado.navigation
mado.extraction
mado.screenshot
model.request
model.response
model.routing_decision
tool.call
tool.result
memory.read
memory.write
archives.recall
archives.inscription
nexus.message
nexus.route
security.posture_change
security.policy_violation
harakiri.command
harakiri.execution
system.health
auth.event
```

The goal is not only to log activity, but to make Gensui capable of showing full operational visibility across the entire Shogun network.

---

### 4.5 Policy Enforcement and Harakiri Control Layer

Gensui must be able to enforce security posture at three levels:

```md
1. Individual Shogun
2. Group of Shoguns
3. Global network
```

It must also be able to trigger Harakiri at the same three levels:

```md
1. Individual Harakiri
2. Group Harakiri
3. Global Harakiri
```

This is one of the most important features.

Gensui must not only observe.

It must be able to command containment.

---

## 5. Membership Model

A Shogun instance must explicitly join Gensui.

This is called signing up or enrollment.

### 5.1 Enrollment Flow

The enrollment flow should work as follows:

```md
1. Gensui admin creates an enrollment token.
2. Operator configures Shogun with the Gensui server URL and enrollment token.
3. Shogun sends an enrollment request to Gensui.
4. Gensui validates the token.
5. Gensui creates a unique member identity for that Shogun.
6. Gensui returns membership credentials.
7. Shogun stores credentials securely.
8. Shogun begins sending heartbeat and telemetry.
9. Gensui marks the Shogun as active.
10. Gensui assigns a default security posture.
```

Optional approval mode:

```md
1. Shogun requests enrollment.
2. Gensui places the instance in Pending Approval.
3. Admin reviews instance details.
4. Admin approves or rejects.
5. Approved Shogun receives active membership status.
```

Approval mode should be supported because enterprise deployments may not want automatic enrollment.

---

### 5.2 Shogun Identity

Each member Shogun must have a stable identity.

Suggested identity fields:

```md
shogun_id
instance_name
hostname
environment
organization
owner
version
build_hash
public_key
enrollment_status
last_seen_at
created_at
updated_at
assigned_group_ids
assigned_posture_id
effective_posture_id
harakiri_state
```

Each Shogun should also report:

```md
local_os
deployment_type
available_model_providers
enabled_tools
mado_status
archives_status
nexus_status
agentflow_status
samurai_count
```

---

### 5.3 Groups

Gensui must support groups.

Groups are used to manage security policies across multiple Shogun instances.

Examples:

```md
Production Shoguns
Development Shoguns
Manufacturing Site A
Sports Organization Pilots
High-Risk Workflows
Read-Only Agents
External-Facing Agents
```

A Shogun can belong to one or more groups.

Group policy resolution must be deterministic.

---

## 6. Security Postures

A security posture is a named policy configuration that defines what a Shogun is allowed to do.

Gensui must be able to define, assign, override, and enforce security postures.

Security postures can apply to:

```md
Global network
Groups
Individual Shogun instances
Specific Samurai
Specific tool categories
Specific workflows
Specific model providers
Specific Mado capabilities
Specific Nexus routing modes
```

---

### 6.1 Security Posture Levels

Gensui should include default posture templates.

Suggested templates:

```md
OPEN
STANDARD
RESTRICTED
LOCKDOWN
OBSERVE_ONLY
LOCAL_ONLY
NO_EXTERNAL_WEB
NO_TOOL_EXECUTION
NO_MEMORY_WRITE
NO_MADO
NO_AUTONOMY
```

The coding agent may adjust names if needed, but the concept must remain.

---

### 6.2 Example Posture Definitions

#### OPEN

Used for development or trusted local experimentation.

Allowed:

```md
External model providers
Local model providers
Mado browser navigation
Tool calls
Memory read/write
Agent Flow execution
Nexus communication
Samurai delegation
Screenshots
File access if locally permitted
```

#### STANDARD

Default operational mode.

Allowed:

```md
Approved model providers
Approved tools
Memory read/write
Agent Flow execution
Mado browser navigation with domain logging
Nexus communication
Samurai delegation
```

Restricted:

```md
Unapproved tools
Unknown model providers
Unapproved browser domains
High-risk file operations
Unapproved external callbacks
```

#### RESTRICTED

Used for sensitive workflows.

Allowed:

```md
Local models or approved API providers only
Approved workflows only
Memory read
Limited memory write
Limited Nexus communication
Approved tools only
```

Restricted:

```md
Free-form browser automation
Unapproved domains
File writes
External API calls
Tool execution without allowlist
Autonomous workflow creation
```

#### LOCKDOWN

Emergency containment mode.

Allowed:

```md
Heartbeat to Gensui
Policy sync with Gensui
Harakiri acknowledgement
Read-only local status reporting
```

Blocked:

```md
Agent execution
Samurai execution
Agent Flow execution
Mado sessions
Tool calls
Model calls
Memory writes
Nexus outbound communication
External API calls
```

#### OBSERVE_ONLY

Used when Shogun is allowed to run but Gensui only monitors.

Allowed:

```md
Normal local behavior
Telemetry submission
Audit reporting
```

Gensui does not enforce restrictions unless violations are configured to escalate.

#### LOCAL_ONLY

Used when no external AI providers are allowed.

Allowed:

```md
Local Ollama / llama.cpp / local inference providers
Local tools
Local memory
Local workflows
```

Blocked:

```md
OpenAI
Anthropic
Google
External model APIs
External embeddings APIs
External tool APIs unless specifically approved
```

#### NO_EXTERNAL_WEB

Blocks external browsing and web extraction.

Blocked:

```md
Mado navigation to internet domains
Web search tools
HTTP fetch tools
External scraping
External screenshots
```

Allowed:

```md
Local tools
Local memory
Approved internal URLs if configured
```

#### NO_TOOL_EXECUTION

Blocks all tool use.

Allowed:

```md
Plain model responses
Memory read if allowed
Policy sync
Telemetry
```

Blocked:

```md
Mado
File tools
Shell tools
HTTP tools
Agent Flow action nodes
External tool integrations
```

#### NO_MEMORY_WRITE

Blocks memory inscription.

Allowed:

```md
Memory read
Memory recall
Existing Archives lookup
```

Blocked:

```md
store_memory
manual memory inscription from agent
automatic memory writes
memory reinforcement updates if configured
```

#### NO_MADO

Blocks browser automation.

Blocked:

```md
Mado session launch
Mado navigation
Mado clicking
Mado form filling
Mado screenshots
Mado extraction
```

#### NO_AUTONOMY

Allows only direct human-triggered actions.

Blocked:

```md
Scheduled Agent Flow runs
Autonomous loops
Self-triggered missions
Background agents
Automatic tool execution without confirmation
```

---

## 7. Global Security Posture

Gensui must be able to enforce one global security posture across all member Shoguns.

This is critical.

A global posture is an emergency or governance-level override.

If global posture is enabled, it must take precedence over group and individual postures unless explicitly configured otherwise.

Example:

```md
Global posture: LOCKDOWN
Effect: Every member Shogun enters LOCKDOWN regardless of local or group settings.
```

Use cases:

```md
Security incident
Data leak concern
Model provider compromise
External API outage
Regulatory event
Enterprise freeze period
Testing pause
Emergency containment
```

The Admin UI must make it very clear when a global posture is active.

Suggested UI indicator:

```md
GLOBAL POSTURE ACTIVE: LOCKDOWN
All managed Shoguns are currently operating under global enforcement.
```

---

## 8. Individual and Group Security Postures

Gensui must also support targeted posture enforcement.

### 8.1 Individual Posture

An admin can set a posture for one Shogun.

Example:

```md
Shogun: KS-Pistons-Factory-Agent
Assigned posture: RESTRICTED
```

### 8.2 Group Posture

An admin can set a posture for a group.

Example:

```md
Group: Sports Pilots
Assigned posture: STANDARD
```

### 8.3 Effective Posture Resolution

The system must calculate an effective posture.

Suggested precedence:

```md
1. Global posture override, if active
2. Active Harakiri state, if active
3. Individual posture override
4. Highest-risk group posture
5. Default organization posture
6. Local Shogun default posture
```

The coding agent should implement deterministic posture resolution and make it visible in the UI.

Example UI:

```md
Assigned posture: STANDARD
Group posture: RESTRICTED
Global posture: None
Effective posture: RESTRICTED
Reason: Group policy has higher restriction level.
```

---

## 9. Harakiri System

Harakiri is the emergency shutdown / containment mechanism.

It must be enforceable from Gensui.

Harakiri is stronger than a normal security posture.

A posture restricts behavior.

Harakiri terminates, disables, isolates, or freezes behavior.

---

### 9.1 Harakiri Levels

Gensui must support:

```md
Individual Harakiri
Group Harakiri
Global Harakiri
```

### 9.2 Individual Harakiri

Targets one Shogun instance.

Example:

```md
Trigger Harakiri on: Shogun-KS-01
```

Expected result:

```md
Active workflows stop.
Samurai execution stops.
Mado sessions close.
Tool execution stops.
Model requests stop.
Nexus outbound routes close.
Memory writes stop.
Heartbeat continues if possible.
Harakiri execution status is reported to Gensui.
```

### 9.3 Group Harakiri

Targets all Shoguns in a group.

Example:

```md
Trigger Harakiri on group: Production Shoguns
```

Expected result:

```md
All group members enter Harakiri state.
Each member reports acknowledgement.
Gensui displays execution status per member.
Failures are highlighted.
```

### 9.4 Global Harakiri

Targets every registered and reachable Shogun.

Example:

```md
Trigger Global Harakiri
```

Expected result:

```md
All member Shoguns enter Harakiri state.
All active Samurai stop.
All Agent Flows stop.
All Mado sessions close.
All Nexus routes close except emergency reporting.
All tool calls are blocked.
All model calls are blocked.
All memory writes are blocked.
Gensui enters emergency monitoring mode.
```

---

### 9.5 Harakiri Modes

The coding agent should support multiple Harakiri modes if technically feasible.

Suggested modes:

```md
SOFT_FREEZE
HARD_STOP
NETWORK_ISOLATE
FULL_TERMINATE
```

#### SOFT_FREEZE

Stops new activity but allows current safe cleanup.

```md
No new workflows
No new model calls
No new tool calls
Current operation can complete if safe
```

#### HARD_STOP

Immediately interrupts active operations.

```md
Cancel workflows
Terminate running tools
Close Mado sessions
Stop Samurai
Block model calls
```

#### NETWORK_ISOLATE

Blocks outbound communication except Gensui heartbeat.

```md
Close Nexus outbound routes
Block external APIs
Block model providers
Block browser sessions
Allow emergency heartbeat only
```

#### FULL_TERMINATE

Attempts to shut down the Shogun process or service.

```md
Flush audit logs
Send final status
Terminate process
Require manual restart
```

The exact technical implementation may vary by operating system and deployment mode.

---

### 9.6 Harakiri Confirmation

Harakiri is high-risk and must require deliberate confirmation.

Admin UI must require:

```md
Explicit confirmation dialog
Typed confirmation phrase
Optional reason field
Optional incident ID
Operator identity logging
Timestamp logging
Target summary before execution
```

Example confirmation phrase:

```md
CONFIRM HARAKIRI
```

For global Harakiri:

```md
CONFIRM GLOBAL HARAKIRI
```

---

### 9.7 Harakiri Audit Log

Every Harakiri action must be logged immutably or append-only.

Minimum fields:

```md
harakiri_id
scope
target_id
target_type
mode
requested_by
requested_at
reason
confirmation_text_used
affected_shogun_ids
acknowledged_shogun_ids
failed_shogun_ids
completed_at
status
error_details
```

---

## 10. Full Monitoring Requirements

Gensui must provide full monitoring of all activity across member Shoguns.

The goal is to make the operator able to answer:

```md
What is each Shogun doing?
Which Samurai are active?
Which workflows are running?
Which tools are being used?
Which models are being called?
Which browser sessions are active?
Which memories are being read or written?
Which Nexus messages are being routed?
Which policies are being enforced?
Which violations occurred?
Which systems are unhealthy?
```

---

### 10.1 Shogun Monitoring

Monitor:

```md
Online/offline status
Heartbeat
Version
Deployment mode
Current posture
Effective posture
Harakiri state
Active Samurai
Active workflows
Active Mado sessions
Active model calls
Recent policy violations
Recent errors
Resource usage if available
```

---

### 10.2 Samurai Monitoring

Monitor per Samurai:

```md
samurai_id
parent_shogun_id
name
role
persona
status
current_task
assigned_model_profile
active_tool_permissions
memory_access_level
last_activity_at
error_state
current_workflow_id
```

Statuses:

```md
idle
running
waiting
blocked_by_policy
error
stopped
harakiri_stopped
offline
```

---

### 10.3 Nexus Monitoring

Monitor:

```md
message_id
source_agent
target_agent
source_shogun
target_shogun
route_type
message_type
timestamp
status
payload_size
policy_check_result
blocked_reason
```

The actual payload may be redacted depending on posture and privacy settings, but metadata must remain auditable.

---

### 10.4 Agent Flow Monitoring

Monitor:

```md
flow_id
flow_name
shogun_id
trigger_type
started_at
completed_at
status
current_node
node_execution_count
failed_node_count
blocked_node_count
policy_interventions
```

Node-level events:

```md
node_id
node_type
node_name
started_at
completed_at
status
input_summary
output_summary
tool_calls
model_calls
policy_result
error
```

---

### 10.5 Mado Monitoring

Monitor:

```md
session_id
shogun_id
samurai_id
flow_id
mode
headless
current_url
allowed_domain_status
started_at
last_activity_at
status
screenshot_count
extraction_count
click_count
form_fill_count
blocked_actions
```

Mado actions:

```md
navigation
click
form_fill
screenshot
extract
download_attempt
upload_attempt
```

Each must be policy-checkable.

---

### 10.6 Model Routing Monitoring

Monitor:

```md
request_id
shogun_id
samurai_id
provider
model
routing_profile
reason_for_route
fallback_used
tokens_in
tokens_out
cost_estimate
latency_ms
status
blocked_by_policy
```

Gensui should be able to enforce:

```md
Allowed providers
Blocked providers
Local-only mode
Maximum cost threshold
Maximum token threshold
Fallback rules
Sensitive-task routing rules
```

---

### 10.7 Tool Call Monitoring

Monitor:

```md
tool_call_id
tool_name
tool_category
shogun_id
samurai_id
workflow_id
timestamp
input_summary
output_summary
status
policy_result
blocked_reason
risk_level
```

Tool categories:

```md
browser
file
network
shell
memory
database
email
calendar
api
custom
```

---

### 10.8 Archives and Memory Monitoring

Monitor:

```md
memory_read
memory_write
memory_update
memory_archive
memory_pin
memory_unpin
memory_recall
```

Minimum fields:

```md
memory_id
memory_type
shogun_id
samurai_id
operation
importance
decay_class
pinned
timestamp
policy_result
```

Gensui must be able to enforce memory restrictions:

```md
No memory writes
No persona changes
No skill memory changes
No cross-agent memory access
No external memory sync
Pinned-only recall mode
```

---

## 11. Policy Enforcement Points

The coding agent must identify and implement enforcement points throughout Shogun.

Gensui policy cannot only be checked at startup.

It must be checked whenever a controlled action happens.

Required enforcement points:

```md
Before model call
Before tool call
Before Mado session launch
Before Mado navigation
Before Mado click
Before Mado form fill
Before Mado download/upload
Before Agent Flow start
Before Agent Flow node execution
Before Samurai delegation
Before Nexus message route
Before memory write
Before memory recall if restricted
Before external API call
Before file write
Before scheduled trigger execution
```

Each enforcement point should ask:

```md
Is this Shogun under Gensui control?
What is the effective security posture?
Is this action allowed?
Should it be blocked, allowed, logged, or escalated?
```

---

## 12. Policy Decision Model

Every controlled action should produce a policy decision.

Suggested decision structure:

```json
{
  "decision_id": "uuid",
  "timestamp": "ISO-8601",
  "shogun_id": "string",
  "samurai_id": "string | null",
  "action_type": "string",
  "resource_type": "string",
  "resource_id": "string | null",
  "posture_id": "string",
  "decision": "ALLOW | BLOCK | REQUIRE_APPROVAL | REDACT | ESCALATE",
  "reason": "string",
  "matched_rules": ["string"],
  "risk_score": 0.0
}
```

Possible decisions:

```md
ALLOW
BLOCK
REQUIRE_APPROVAL
REDACT
ESCALATE
```

---

## 13. Data Storage

Gensui needs durable storage.

Recommended default:

```md
SQLite for local/server-light mode
PostgreSQL optional for enterprise/server mode
```

Because Shogun already uses SQLite in other areas, SQLite can be the default for simple server deployment.

However, Gensui is a server-side multi-instance control plane, so the architecture should not prevent PostgreSQL support later.

---

### 13.1 Core Tables

Suggested tables:

```md
gensui_instances
shogun_members
member_groups
group_memberships
security_postures
posture_rules
global_posture_state
harakiri_events
harakiri_targets
telemetry_events
policy_decisions
audit_log
enrollment_tokens
admin_users
admin_sessions
api_keys
alerts
```

---

### 13.2 Shogun Members Table

```md
id
instance_name
hostname
environment
organization
owner
version
build_hash
public_key
status
enrollment_status
last_seen_at
created_at
updated_at
default_posture_id
individual_posture_id
effective_posture_id
harakiri_state
metadata_json
```

---

### 13.3 Security Postures Table

```md
id
name
description
level
is_builtin
is_global
created_by
created_at
updated_at
rules_json
```

---

### 13.4 Telemetry Events Table

```md
id
event_type
event_category
shogun_id
samurai_id
workflow_id
nexus_message_id
severity
timestamp
payload_json
redacted_payload_json
policy_decision_id
created_at
```

---

### 13.5 Audit Log Table

```md
id
actor_type
actor_id
action
target_type
target_id
timestamp
ip_address
user_agent
reason
before_json
after_json
metadata_json
hash
previous_hash
```

The audit log should be append-only.

If possible, implement hash chaining:

```md
current_hash = hash(previous_hash + event_payload)
```

This makes tampering easier to detect.

---

## 14. Authentication and Authorization

Gensui must have strong authentication.

### 14.1 Admin Authentication

Admin UI must require login.

Initial implementation can support:

```md
Local admin user
Password hash
Session token
JWT or secure session cookie
```

Future-ready support:

```md
SSO
OIDC
SAML
Azure AD / Entra ID
Google Workspace
```

### 14.2 Role-Based Access Control

Required roles:

```md
Owner
Admin
Security Operator
Observer
Auditor
```

#### Owner

Full access.

Can:

```md
Manage users
Manage global posture
Trigger global Harakiri
Delete/disable members
Create policies
View all telemetry
```

#### Admin

Can:

```md
Manage members
Manage groups
Assign postures
View telemetry
Trigger individual/group Harakiri
```

#### Security Operator

Can:

```md
View dashboards
Respond to alerts
Trigger predefined lockdown actions
Trigger individual Harakiri if permitted
```

#### Observer

Can:

```md
View status
View dashboards
View non-sensitive logs
```

#### Auditor

Can:

```md
View audit logs
Export reports
Verify hash chain if implemented
```

---

## 15. Communication Between Shogun and Gensui

Communication must be secure.

Minimum requirements:

```md
HTTPS support
Membership token or signed API key
Instance identity
Heartbeat
Policy sync
Telemetry push
Command retrieval
```

Preferred:

```md
Mutual authentication
Instance key pair
Signed telemetry events
Rotating tokens
TLS-ready architecture
```

---

### 15.1 Heartbeat

Each Shogun sends heartbeat to Gensui at a configurable interval.

Heartbeat payload:

```json
{
  "shogun_id": "string",
  "timestamp": "ISO-8601",
  "status": "online",
  "version": "string",
  "effective_posture": "STANDARD",
  "harakiri_state": "none",
  "active_samurai_count": 2,
  "active_workflow_count": 1,
  "active_mado_sessions": 0,
  "health": {
    "archives": "healthy",
    "mado": "healthy",
    "nexus": "healthy",
    "agent_flow": "healthy"
  }
}
```

---

### 15.2 Policy Sync

Shogun must periodically fetch its effective posture from Gensui.

It should also fetch immediately when notified, if real-time push is implemented.

Policy sync response:

```json
{
  "shogun_id": "string",
  "effective_posture": {
    "id": "posture_restricted",
    "name": "RESTRICTED",
    "rules": {}
  },
  "global_posture_active": false,
  "harakiri_state": "none",
  "policy_version": 42
}
```

---

### 15.3 Command Channel

Gensui must have a way to send commands to Shogun.

Two possible models:

```md
Polling model
Push model
```

Polling model is easier:

```md
Shogun polls /commands every N seconds.
Gensui returns pending commands.
Shogun executes commands.
Shogun reports command result.
```

Push model is more real-time:

```md
WebSocket
Server-Sent Events
Message broker
```

Initial implementation can use polling, as long as it is reliable and secure.

---

## 16. Failure Behavior

Gensui must define what happens if a Shogun loses contact with the server.

This must be configurable by posture.

Possible disconnect modes:

```md
CONTINUE_LAST_POLICY
DEGRADE_TO_RESTRICTED
DEGRADE_TO_LOCAL_ONLY
ENTER_LOCKDOWN
ENTER_HARAKIRI_SOFT_FREEZE
```

Example:

```md
If a production Shogun cannot reach Gensui for more than 5 minutes, enter RESTRICTED.
If a high-risk Shogun cannot reach Gensui for more than 1 minute, enter LOCKDOWN.
If a development Shogun cannot reach Gensui, continue with last known policy.
```

Each disconnect event must be logged locally and reported when connection resumes.

---

## 17. Local Enforcement Cache

Each Shogun must maintain a local cache of its last known Gensui policy.

This is required because Gensui may not always be reachable.

The cache should include:

```md
effective_posture
policy_version
last_sync_at
global_posture_flag
group_posture_summary
harakiri_state
disconnect_behavior
```

The cache should be stored securely.

---

## 18. Admin Dashboard Requirements

The Gensui Admin UI must make the system understandable at a glance.

### 18.1 Main Dashboard

Show:

```md
Total registered Shoguns
Online Shoguns
Offline Shoguns
Active Samurai
Active workflows
Active Mado sessions
Current global posture
Harakiri state summary
Recent policy violations
Recent critical alerts
Telemetry volume
```

### 18.2 Shogun Fleet View

Table of all Shogun members:

```md
Name
Status
Environment
Version
Groups
Effective posture
Last seen
Active Samurai
Active workflows
Harakiri state
Actions
```

Actions:

```md
View details
Assign posture
Move to group
Trigger Harakiri
Disable member
Rotate credentials
```

### 18.3 Shogun Detail View

Show:

```md
Identity
Health
Effective posture
Policy resolution explanation
Active Samurai
Active Agent Flows
Active Mado sessions
Recent Nexus messages
Recent model calls
Recent tool calls
Recent memory operations
Recent violations
Audit timeline
```

### 18.4 Groups View

Show:

```md
Group name
Member count
Assigned posture
Active violations
Harakiri status
Last activity
```

### 18.5 Security Postures View

Show:

```md
Built-in postures
Custom postures
Global posture controls
Policy rules
Assignment history
Effective posture preview
```

### 18.6 Harakiri Control Center

Show:

```md
Individual Harakiri
Group Harakiri
Global Harakiri
Active Harakiri events
Acknowledgement status
Failed acknowledgements
Recovery options
```

### 18.7 Activity Monitor

Searchable stream of telemetry events.

Filters:

```md
Shogun
Samurai
Event type
Severity
Workflow
Tool
Model provider
Policy decision
Time range
```

### 18.8 Audit Log

Searchable append-only audit log.

Filters:

```md
Actor
Action
Target
Time range
Severity
Policy
Harakiri event
```

---

## 19. Alerts and Violations

Gensui must detect and display policy violations.

Examples:

```md
Blocked model provider attempt
Blocked external domain
Blocked Mado action
Blocked memory write
Unauthorized Nexus route
Tool call denied
Shogun offline
Heartbeat missing
Harakiri acknowledgement missing
Policy sync failed
Version mismatch
Unexpected local posture change
```

Each alert should include:

```md
alert_id
severity
event_type
shogun_id
samurai_id
description
timestamp
status
linked_policy_decision
linked_telemetry_event
recommended_action
```

Severity levels:

```md
INFO
LOW
MEDIUM
HIGH
CRITICAL
```

---

## 20. Recovery and Release From Harakiri

Harakiri must not be irreversible unless configured as full termination.

Gensui must support recovery controls.

Recovery actions:

```md
Release individual Shogun from Harakiri
Release group from Harakiri
Release global Harakiri
Move released instances into LOCKDOWN
Move released instances into RESTRICTED
Restore previous posture
Require manual restart
```

After release, the Shogun should not automatically return to OPEN unless explicitly configured.

Recommended default:

```md
After Harakiri release, enter LOCKDOWN or RESTRICTED.
Admin must manually restore normal posture.
```

---

## 21. Privacy and Redaction

Gensui monitors activity, but enterprise environments may contain sensitive data.

The telemetry pipeline must support redaction.

Telemetry should separate:

```md
Metadata
Payload summary
Full payload
Redacted payload
```

Default should be safe.

Recommended default:

```md
Log metadata and summaries.
Do not send full prompt/response payloads unless explicitly enabled.
Redact secrets, API keys, tokens, passwords, cookies, and personal data patterns where possible.
```

Gensui should support telemetry modes:

```md
MINIMAL
STANDARD
DETAILED
FULL
```

### MINIMAL

```md
Heartbeat
Status
Policy decisions
Critical alerts
Harakiri events
```

### STANDARD

```md
Metadata for tool/model/workflow/memory events
Summaries only
No full payloads
```

### DETAILED

```md
Input/output summaries
More context
Still redacted
```

### FULL

```md
Full payload logging where allowed
High-risk
Must require explicit admin enablement
```

---

## 22. Compliance-Oriented Design

Gensui should be designed with enterprise auditability in mind.

It does not need full compliance certification immediately, but the architecture should support:

```md
Audit trails
Access control
Policy enforcement
Event monitoring
Incident response
Data minimization
Retention policies
Tamper-evident logs
Operator accountability
Exportable reports
```

Potential future alignment areas:

```md
NIS2
EU AI Act governance
ISO 27001-style controls
SOC2-style logging
Internal audit requirements
Enterprise AI governance
```

Do not overbuild certification features at first, but avoid architectural choices that would make them difficult later.

---

## 23. Integration With Existing Shogun Components

Gensui must integrate with the existing Shogun architecture through clean boundaries.

### 23.1 Integration With Agent Flow

Gensui must receive events when:

```md
Flow starts
Flow completes
Flow fails
Node starts
Node completes
Node fails
Node blocked by policy
Scheduled trigger fires
Scheduled trigger blocked
```

Gensui must be able to block:

```md
Flow execution
Specific node types
Scheduled autonomous runs
External action nodes
Tool execution nodes
Mado nodes
Memory-write nodes
```

---

### 23.2 Integration With Mado

Gensui must receive events when:

```md
Mado session starts
Mado session closes
Navigation occurs
Click occurs
Form fill occurs
Screenshot captured
Content extraction occurs
Download attempted
Upload attempted
```

Gensui must be able to block:

```md
Mado entirely
Navigation to unapproved domains
Form submission
Downloads
Uploads
Screenshots
Credential entry
```

---

### 23.3 Integration With Archives

Gensui must receive events when:

```md
Memory recalled
Memory written
Memory pinned
Memory archived
Memory updated
Memory reindexed
```

Gensui must be able to enforce:

```md
Read-only memory
No persona memory modification
No cross-agent memory sharing
No memory writes during restricted posture
Pinned-memory-only mode
```

---

### 23.4 Integration With Samurai

Gensui must monitor:

```md
Samurai creation
Samurai activation
Samurai task assignment
Samurai delegation
Samurai model profile
Samurai tool permissions
Samurai memory access
Samurai errors
```

Gensui must be able to block or restrict:

```md
Creating new Samurai
Activating Samurai
Delegating tasks
Using high-risk tools
Using external models
Writing memories
Accessing certain Nexus routes
```

---

### 23.5 Integration With Nexus

Gensui must monitor:

```md
Inter-agent messages
Cross-Shogun routes
Message metadata
Route approvals
Blocked routes
Payload size
Message category
```

Gensui must be able to enforce:

```md
No cross-Shogun communication
Only same-group communication
No external Nexus routes
Restricted payload routing
Approval-required routing
Emergency shutdown of Nexus routes
```

---

### 23.6 Integration With Model Routing

Gensui must monitor:

```md
Provider used
Model used
Routing profile
Fallbacks
Errors
Latency
Cost estimates
Token usage
```

Gensui must be able to enforce:

```md
Allowed providers
Blocked providers
Local-only providers
Maximum token budget
Maximum cost budget
Sensitive workflow routing
Fallback restrictions
```

---

## 24. API Design

The exact API can be adjusted by the coding agent to fit the existing stack.

Suggested endpoints:

### Enrollment

```http
POST /api/gensui/enroll
POST /api/gensui/enroll/approve
POST /api/gensui/enroll/reject
```

### Heartbeat

```http
POST /api/gensui/heartbeat
```

### Telemetry

```http
POST /api/gensui/telemetry
POST /api/gensui/telemetry/batch
```

### Policy

```http
GET /api/gensui/policy/effective/:shogun_id
POST /api/gensui/policy/assign
POST /api/gensui/policy/global
POST /api/gensui/policy/global/clear
```

### Commands

```http
GET /api/gensui/commands/:shogun_id
POST /api/gensui/commands/:command_id/ack
POST /api/gensui/commands/:command_id/result
```

### Harakiri

```http
POST /api/gensui/harakiri/individual
POST /api/gensui/harakiri/group
POST /api/gensui/harakiri/global
POST /api/gensui/harakiri/release
```

### Admin

```http
GET /api/gensui/members
GET /api/gensui/members/:id
POST /api/gensui/members/:id/disable
POST /api/gensui/members/:id/rotate-credentials
GET /api/gensui/groups
POST /api/gensui/groups
POST /api/gensui/groups/:id/members
GET /api/gensui/audit
GET /api/gensui/alerts
```

---

## 25. Local Shogun Enforcement API

Inside Shogun, create an internal enforcement interface.

Example:

```ts
interface GensuiPolicyGuard {
  checkAction(action: PolicyAction): Promise<PolicyDecision>;
  enforce(decision: PolicyDecision): Promise<void>;
  getEffectivePosture(): Promise<SecurityPosture>;
  isHarakiriActive(): boolean;
}
```

Example controlled action:

```ts
{
  actionType: "MADO_NAVIGATION",
  shogunId: "...",
  samuraiId: "...",
  resourceType: "URL",
  resourceValue: "https://example.com",
  riskLevel: "MEDIUM",
  metadata: {}
}
```

Every high-risk component should call this guard before execution.

---

## 26. Developer Experience

Because Shogun is open-code and free to use, Gensui should be understandable for developers.

Add clear documentation:

```md
How to run Gensui locally
How to enroll a Shogun
How to create a posture
How to trigger Harakiri safely
How telemetry works
How to disable Gensui
How to deploy Gensui on a server
How to configure environment variables
How to inspect audit logs
```

Add example configurations:

```md
Development mode
Local LAN mode
Small company mode
Enterprise server mode
High-security mode
```

---

## 27. Configuration

### 27.1 Gensui Server Environment Variables

```env
GENSUI_SERVER_HOST=0.0.0.0
GENSUI_SERVER_PORT=8787
GENSUI_DATABASE_URL=sqlite:///./data/gensui.db
GENSUI_ADMIN_EMAIL=admin@example.com
GENSUI_ADMIN_PASSWORD_HASH=...
GENSUI_JWT_SECRET=...
GENSUI_REQUIRE_ENROLLMENT_APPROVAL=true
GENSUI_DEFAULT_POSTURE=STANDARD
GENSUI_TELEMETRY_DEFAULT_MODE=STANDARD
GENSUI_ENABLE_GLOBAL_HARAKIRI=true
GENSUI_ENABLE_GROUP_HARAKIRI=true
GENSUI_ENABLE_INDIVIDUAL_HARAKIRI=true
```

### 27.2 Shogun Client Environment Variables

```env
GENSUI_ENABLED=true
GENSUI_SERVER_URL=http://localhost:8787
GENSUI_ENROLLMENT_TOKEN=...
GENSUI_INSTANCE_NAME=Local Shogun
GENSUI_ENVIRONMENT=development
GENSUI_HEARTBEAT_INTERVAL_SECONDS=15
GENSUI_COMMAND_POLL_INTERVAL_SECONDS=5
GENSUI_POLICY_SYNC_INTERVAL_SECONDS=30
GENSUI_DISCONNECT_BEHAVIOR=CONTINUE_LAST_POLICY
GENSUI_TELEMETRY_MODE=STANDARD
```

---

## 28. Security Rules Model

A posture should be rule-based.

Example posture rule:

```json
{
  "id": "rule_no_external_models",
  "description": "Block external model providers",
  "action_types": ["MODEL_CALL"],
  "conditions": {
    "provider_type": "external"
  },
  "decision": "BLOCK",
  "severity": "HIGH"
}
```

Example Mado domain rule:

```json
{
  "id": "rule_allowed_domains_only",
  "description": "Allow Mado navigation only to approved domains",
  "action_types": ["MADO_NAVIGATION"],
  "conditions": {
    "domain_in_allowlist": true
  },
  "decision": "ALLOW",
  "default_decision": "BLOCK",
  "severity": "MEDIUM"
}
```

Example memory rule:

```json
{
  "id": "rule_no_persona_memory_write",
  "description": "Block changes to persona memories",
  "action_types": ["MEMORY_WRITE", "MEMORY_UPDATE"],
  "conditions": {
    "memory_type": "persona"
  },
  "decision": "BLOCK",
  "severity": "HIGH"
}
```

---

## 29. Minimum Viable Gensui

The coding agent can decide implementation order, but the first useful version of Gensui must include the following capabilities:

```md
Separate Gensui server application
Separate Gensui admin UI
Shogun enrollment/sign-up
Member identity
Heartbeat
Fleet overview
Security posture definitions
Assign posture to individual Shogun
Global posture override
Basic telemetry intake
Activity monitor
Policy guard inside Shogun
Block at least model calls, tool calls, Mado, memory writes, and Agent Flow execution
Individual Harakiri
Global Harakiri
Audit log
Basic admin authentication
```

Group posture and group Harakiri should also be implemented as soon as possible because they are part of the core Gensui concept.

---

## 30. Non-Negotiable Requirements

The following requirements are mandatory:

```md
Gensui must be a separate server-side program.
Gensui must live in the same repository as Shogun.
Shogun instances must be able to sign up to Gensui.
A signed-up Shogun becomes a member of Gensui.
Gensui must control security postures for individual Shoguns.
Gensui must support group-level control.
Gensui must support a global security posture.
Gensui must be able to enforce one global security posture across all member Shoguns.
Gensui must support individual Harakiri.
Gensui must support group Harakiri.
Gensui must support global Harakiri.
Gensui must monitor all member Shogun activity.
Gensui must monitor Samurai activity.
Gensui must monitor Nexus activity.
Gensui must monitor Agent Flow activity.
Gensui must monitor Mado activity.
Gensui must monitor model routing activity.
Gensui must monitor tool usage.
Gensui must monitor Archives/memory activity.
Gensui must maintain an audit log.
Policy enforcement must happen inside Shogun at action time.
Harakiri must be auditable and require confirmation.
Loss of Gensui connection must have configurable fallback behavior.
```

---

## 31. Acceptance Criteria

Gensui is considered functionally successful when the following can be demonstrated:

```md
A Gensui server can be started independently.
A Gensui Admin UI can be opened in a browser.
A Shogun instance can enroll into Gensui.
The enrolled Shogun appears in the fleet view.
The enrolled Shogun sends heartbeat.
Gensui can assign a security posture to that Shogun.
The Shogun enforces that posture locally.
Gensui can activate a global posture.
The Shogun obeys the global posture.
Gensui can block model calls through policy.
Gensui can block tool calls through policy.
Gensui can block Mado through policy.
Gensui can block memory writes through policy.
Gensui receives telemetry from Shogun.
Gensui displays monitored activity in the Admin UI.
Gensui logs policy decisions.
Gensui logs audit events.
Gensui can trigger individual Harakiri.
The Shogun executes individual Harakiri and acknowledges it.
Gensui can trigger global Harakiri.
All reachable Shogun members execute global Harakiri and acknowledge it.
Gensui can release Harakiri into LOCKDOWN or RESTRICTED mode.
```

---

## 32. Strategic Positioning

Gensui is not just an admin panel.

It is the enterprise command layer for Shogun.

With Gensui, Shogun becomes more than a local AI agent platform.

It becomes a governed, monitorable, controllable agent network.

This matters because real organizations will not deploy AI agents at scale unless they can answer:

```md
Who is running?
What are they doing?
Which tools are they using?
Which models are they calling?
What data are they touching?
Which memories are they writing?
Which workflows are active?
Can we stop them immediately?
Can we enforce policy globally?
Can we prove what happened afterwards?
```

Gensui is the answer to those questions.

It gives Shogun a server-grade governance layer for serious use.

---

## 33. Final Definition

Gensui is a separate server-side control program, located in the same repository as Shogun, that allows Shogun instances to sign up as governed members.

Once a Shogun is a member, Gensui can monitor its activity, control its security posture, enforce global policies, manage groups, observe Samurai and Nexus behavior, and trigger individual, group, or global Harakiri.

In short:

> Gensui is the central command and security control plane for a fleet of Shogun agents.
