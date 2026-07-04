# Build Paper

# Shogun Productivity App Mode — Phase 2

## Provider-based support for open-source, European, and non-Microsoft productivity suites

---

## 1. Executive Summary

The Microsoft Office part of Shogun Office App Mode has already been built.

Phase 2 extends the capability into a broader **Productivity App Mode** that is not tied to Microsoft Office.

The goal is to allow Shogun to work with the productivity stack a company has chosen, including:

* Microsoft Office
* LibreOffice
* OnlyOffice
* Collabora Online
* Future approved office/productivity suites
* Generic document engines
* Provider-neutral mail adapters

This is important because many European companies, public-sector organizations, and sovereignty-conscious enterprises may want to reduce dependency on American software vendors or support open-source/self-hosted productivity environments.

The principle for Phase 2 is:

> Shogun should not be hardcoded to Microsoft Office. Shogun should operate through a provider-based productivity layer where Microsoft Office is one provider, not the product assumption.

The result should be a more strategic Shogun capability:

> Shogun can operate approved productivity tools inside controlled business boundaries, regardless of whether the company uses Microsoft Office, LibreOffice, OnlyOffice, Collabora, or another approved stack.

---

## 2. Phase 2 Goal

The goal of Phase 2 is to build everything around and beyond the existing Microsoft Office automation:

1. Introduce a provider-based Productivity Adapter Layer.
2. Generalize tool names away from Microsoft-specific naming.
3. Add LibreOffice support.
4. Add OnlyOffice support.
5. Add Collabora support where relevant.
6. Add a cross-platform document engine.
7. Add provider-neutral mail/draft support.
8. Add provider capability probing.
9. Add provider selection in Shogun configuration and GUI.
10. Ensure all productivity events flow through Shogun’s existing audit system.
11. Preserve the existing Microsoft Office implementation as the first production-grade provider.

This phase should make Shogun more credible in European and mixed-environment company pilots.

---

## 3. Strategic Rationale

The original Office App Mode solves a major problem:

> Companies work in Office files and productivity applications.

However, the next strategic problem is:

> Not all companies want Microsoft to be the assumed productivity layer.

European companies may increasingly evaluate:

* Open-source office suites
* Self-hosted document platforms
* Non-US productivity environments
* Sovereignty-oriented infrastructure
* Local-first and auditable software stacks
* Mixed environments across Windows, Linux, macOS, browser, and private cloud

Therefore, Shogun should support a broader architecture.

This creates a strong market position:

> Shogun can support Microsoft-heavy companies without becoming Microsoft-dependent, and it can support sovereignty-conscious companies without requiring a Microsoft productivity stack.

That is a significant commercial advantage.

---

## 4. Naming Change

The user-facing name should change from:

# Office App Mode

to:

# Productivity App Mode

Recommended external description:

> Controlled automation for approved office and productivity suites.

Recommended internal component name:

# Productivity Adapter Layer

The existing Microsoft Office implementation becomes:

# Microsoft Office Provider

The new provider model should support:

```text
providers/
  microsoft_office/
  libreoffice/
  onlyoffice/
  collabora/
  document_engine/
  mail/
```

This avoids hardcoding Shogun around Excel, Word, PowerPoint, and Outlook.

---

## 5. Core Architecture Principle

Phase 2 must introduce a provider-neutral abstraction.

The agent should not call:

```text
office.excel.write_range
office.word.replace_placeholders
office.powerpoint.export_pdf
office.outlook.create_draft
```

The agent should call:

```text
productivity.spreadsheet.write_range
productivity.document.replace_placeholders
productivity.presentation.export_pdf
productivity.mail.create_draft
```

The selected provider then decides how the task is executed.

Example:

| Generic Tool                               | Microsoft Provider | LibreOffice Provider | OnlyOffice Provider  | Collabora Provider |
| ------------------------------------------ | ------------------ | -------------------- | -------------------- | ------------------ |
| productivity.spreadsheet.read_range        | Excel COM          | Calc UNO             | Document Builder/API | WOPI/API           |
| productivity.document.replace_placeholders | Word COM           | Writer UNO           | Document Builder/API | WOPI/API           |
| productivity.presentation.export_pdf       | PowerPoint COM     | Impress UNO/headless | Document Builder/API | Server/export API  |
| productivity.mail.create_draft             | Outlook COM        | Generic SMTP/EML     | Generic SMTP/EML     | Generic SMTP/EML   |

This makes Shogun provider-independent at the agent level.

---

## 6. Target Providers

Phase 2 should support five provider categories.

---

### 6.1 Microsoft Office Provider

Status:

> Already built.

Purpose:

* Maintain full support for Excel, Word, PowerPoint, and Outlook.
* Wrap the existing implementation behind the new provider-neutral interface.
* Do not remove or weaken the current Microsoft Office functionality.

Role in Phase 2:

> The existing Office App Mode becomes the first production-grade provider in Productivity App Mode.

Required work:

* Rename internal tool exposure.
* Map generic tool calls to existing Microsoft Office functions.
* Add provider registration.
* Add capability reporting.
* Add backward compatibility aliases.

Example mapping:

```text
productivity.spreadsheet.write_range
  -> microsoft_office.excel.write_range

productivity.document.replace_placeholders
  -> microsoft_office.word.replace_placeholders

productivity.presentation.export_pdf
  -> microsoft_office.powerpoint.export_pdf

productivity.mail.create_draft
  -> microsoft_office.outlook.create_draft
```

---

### 6.2 LibreOffice Provider

Purpose:

Support LibreOffice Calc, Writer, and Impress through a local open-source productivity suite.

Target applications:

| Microsoft equivalent | LibreOffice equivalent                         |
| -------------------- | ---------------------------------------------- |
| Excel                | Calc                                           |
| Word                 | Writer                                         |
| PowerPoint           | Impress                                        |
| Outlook              | No direct equivalent; use generic mail adapter |

Execution modes:

1. LibreOffice UNO automation
2. Headless LibreOffice conversion
3. File-based manipulation where sufficient

Recommended first capabilities:

| Capability                 | Target support      |
| -------------------------- | ------------------- |
| Open spreadsheet           | Yes                 |
| Read spreadsheet values    | Yes                 |
| Write spreadsheet values   | Yes                 |
| Recalculate spreadsheet    | Yes, where reliable |
| Export spreadsheet to PDF  | Yes                 |
| Open document template     | Yes                 |
| Replace placeholders       | Yes                 |
| Insert table               | Yes                 |
| Export document to PDF     | Yes                 |
| Open presentation template | Yes                 |
| Replace placeholders       | Yes                 |
| Export presentation to PDF | Yes                 |

Important limitation:

LibreOffice should not be treated as identical to Microsoft Office. It may have different rendering, formatting, macro behavior, compatibility handling, and automation stability.

Therefore, the provider must expose capabilities honestly.

Example:

```json
{
  "provider": "libreoffice",
  "spreadsheet": {
    "read_range": true,
    "write_range": true,
    "calculate": true,
    "export_pdf": true,
    "macro_execution": false
  },
  "document": {
    "replace_placeholders": true,
    "insert_table": true,
    "export_pdf": true
  },
  "presentation": {
    "replace_placeholders": true,
    "export_pdf": true
  },
  "mail": {
    "create_draft": false
  }
}
```

---

### 6.3 OnlyOffice Provider

Purpose:

Support OnlyOffice as a document generation and editing backend, especially for companies that use self-hosted or non-Microsoft office environments.

Target modes:

1. OnlyOffice Document Builder CLI
2. OnlyOffice Document Builder API
3. OnlyOffice Docs / Document Server integration where available

Best use cases:

* Generate `.docx`
* Generate `.xlsx`
* Generate `.pptx`
* Convert/export documents
* Template-based document creation
* Server-side document workflows

OnlyOffice should be treated primarily as a **document generation provider**, not necessarily as a desktop app automation provider.

Recommended first capabilities:

| Capability                               | Target support               |
| ---------------------------------------- | ---------------------------- |
| Generate document from template/data     | Yes                          |
| Generate spreadsheet from data           | Yes                          |
| Generate presentation from template/data | Yes                          |
| Export to PDF                            | Yes, where configured        |
| Edit existing complex files              | Limited                      |
| Interactive app control                  | No                           |
| Mail                                     | No; use generic mail adapter |

OnlyOffice provider should be useful in server or local-builder setups where Microsoft Office is not installed.

---

### 6.4 Collabora Provider

Purpose:

Support companies using Collabora Online / Collabora Office in self-hosted or sovereignty-oriented setups.

Target modes:

1. Collabora Online integration
2. WOPI-style document integration
3. Server-side conversion/export where configured
4. Browser-based collaboration environments

Collabora should not be treated as a local desktop automation tool in the same way as Microsoft Office COM.

It is better understood as a **self-hosted document platform provider**.

Recommended first capabilities:

| Capability                              | Target support                           |
| --------------------------------------- | ---------------------------------------- |
| Register document with provider         | Yes                                      |
| Request document conversion/export      | Yes                                      |
| Open document in controlled web context | Later / optional                         |
| Template-based generation               | Via document engine or integration layer |
| PDF export                              | Yes, where server supports it            |
| Interactive editing                     | Not required for Phase 2 MVP             |
| Mail                                    | No; use generic mail adapter             |

Collabora support is strategically important because it allows Shogun to fit into self-hosted European document environments.

---

### 6.5 Generic Document Engine

Purpose:

Provide cross-platform file manipulation without relying on installed office applications.

This engine should use file libraries where possible.

Target libraries:

* `openpyxl` for `.xlsx`
* `python-docx` for `.docx`
* `python-pptx` for `.pptx`
* CSV handling through Python standard libraries or pandas
* PDF generation/conversion libraries as needed

The Generic Document Engine should be the safest fallback.

It should support:

* Reading spreadsheets
* Writing spreadsheets
* Filling Word templates
* Creating simple documents
* Creating simple presentations
* Writing structured output files
* Basic formatting
* No app automation
* No external dependencies on Microsoft Office

This engine is not meant to replace native providers in all situations. It is meant to provide reliable, cross-platform functionality for controlled document operations.

---

## 7. Provider Capability Model

Every provider must expose its capabilities.

Shogun must never assume all providers support all actions.

A provider capability manifest should define:

```json
{
  "provider_id": "libreoffice",
  "provider_name": "LibreOffice Provider",
  "platforms": ["windows", "linux", "macos"],
  "status": "available",
  "capabilities": {
    "spreadsheet": {
      "read_range": true,
      "write_range": true,
      "calculate": true,
      "export_pdf": true
    },
    "document": {
      "replace_placeholders": true,
      "insert_table": true,
      "export_pdf": true
    },
    "presentation": {
      "replace_placeholders": true,
      "insert_image": true,
      "export_pdf": true
    },
    "mail": {
      "create_draft": false,
      "send_with_confirmation": false
    }
  },
  "limitations": [
    "No Outlook equivalent",
    "Formatting may differ from Microsoft Office",
    "Macro execution disabled by default"
  ]
}
```

This allows Shogun to show realistic provider support in the UI.

---

## 8. Provider Selection Logic

Shogun must support provider selection at three levels:

1. Global default provider
2. Capability-specific provider
3. Task-specific override

Example:

```json
{
  "productivity_app_mode": {
    "enabled": true,
    "minimum_posture": "guarded",
    "default_provider": "microsoft_office",
    "providers": {
      "microsoft_office": {
        "enabled": true
      },
      "libreoffice": {
        "enabled": true
      },
      "onlyoffice": {
        "enabled": false
      },
      "collabora": {
        "enabled": false
      },
      "document_engine": {
        "enabled": true
      }
    },
    "routing": {
      "spreadsheet": "microsoft_office",
      "document": "document_engine",
      "presentation": "microsoft_office",
      "mail": "microsoft_office"
    }
  }
}
```

A sovereignty-conscious company could configure:

```json
{
  "routing": {
    "spreadsheet": "libreoffice",
    "document": "libreoffice",
    "presentation": "libreoffice",
    "mail": "generic_mail"
  }
}
```

A server-oriented company could configure:

```json
{
  "routing": {
    "spreadsheet": "onlyoffice",
    "document": "onlyoffice",
    "presentation": "onlyoffice",
    "mail": "generic_mail"
  }
}
```

---

## 9. Provider Routing Engine

The Provider Routing Engine decides which provider executes a task.

Routing must consider:

* Configured default provider
* File type
* Operating system
* Installed applications
* Provider health status
* Required action
* Required fidelity
* Company policy
* Posture level
* Security restrictions
* Whether PDF export is required
* Whether mail/draft support is required

Example:

```text
Task:
productivity.document.replace_placeholders

Input:
.docx template

Required:
PDF export

Policy:
Prefer open-source provider

Routing result:
LibreOffice Provider
```

Example:

```text
Task:
productivity.spreadsheet.calculate

Input:
.xlsx with complex formulas

Required:
High Excel fidelity

Policy:
Microsoft Office allowed

Routing result:
Microsoft Office Provider
```

The routing engine should be explicit and auditable.

The report should say:

> This task was executed by the LibreOffice Provider because the project policy preferred open-source providers and the provider passed all required capability checks.

---

## 10. File Registry and Provider Compatibility

The existing File Registry should be extended with provider compatibility metadata.

Example:

```json
{
  "file_id": "monthly_report_template",
  "resolved_path": "C:/ShogunSandbox/Templates/monthly_report.docx",
  "file_type": "document",
  "extension": ".docx",
  "sha256": "abc123",
  "allowed_actions": ["read", "copy", "replace_placeholders", "export_pdf"],
  "compatible_providers": ["microsoft_office", "libreoffice", "onlyoffice", "document_engine"],
  "preferred_provider": "libreoffice",
  "origin": "template_folder",
  "status": "registered"
}
```

This prevents the agent from guessing.

The agent should use `file_id`, not raw paths.

The provider layer resolves the file, validates it, checks compatibility, and then executes.

---

## 11. Generalized Tool Schema

The Phase 2 tool schema should be provider-neutral.

### Spreadsheet tools

```text
productivity.spreadsheet.open
productivity.spreadsheet.read_range
productivity.spreadsheet.write_range
productivity.spreadsheet.list_sheets
productivity.spreadsheet.calculate
productivity.spreadsheet.save_as
productivity.spreadsheet.export_pdf
```

### Document tools

```text
productivity.document.open
productivity.document.read_text
productivity.document.replace_placeholders
productivity.document.insert_table
productivity.document.save_as
productivity.document.export_pdf
```

### Presentation tools

```text
productivity.presentation.open
productivity.presentation.list_slides
productivity.presentation.replace_placeholders
productivity.presentation.insert_image
productivity.presentation.insert_table
productivity.presentation.save_as
productivity.presentation.export_pdf
```

### Mail tools

```text
productivity.mail.create_draft
productivity.mail.attach_file
productivity.mail.save_draft
productivity.mail.send_with_confirmation
```

Provider-specific tools may still exist internally, but agents should use generic productivity tools by default.

---

## 12. Backward Compatibility

Existing Microsoft Office tools should continue to work during transition.

Backward-compatible aliases:

```text
office.excel.write_range
  -> productivity.spreadsheet.write_range using microsoft_office provider

office.word.replace_placeholders
  -> productivity.document.replace_placeholders using microsoft_office provider

office.powerpoint.export_pdf
  -> productivity.presentation.export_pdf using microsoft_office provider

office.outlook.create_draft
  -> productivity.mail.create_draft using microsoft_office provider
```

Deprecation strategy:

| Version        | Behavior                                       |
| -------------- | ---------------------------------------------- |
| Phase 2 MVP    | Old and new tool names both work               |
| Later version  | Old tool names show deprecation warning        |
| Future version | Old tool names remain as compatibility aliases |

Do not break the existing Office implementation.

---

## 13. Platform Support Matrix

Phase 2 must clearly define platform support.

| Platform | Microsoft Office Provider |      LibreOffice Provider | OnlyOffice Provider |             Collabora Provider | Document Engine |
| -------- | ------------------------: | ------------------------: | ------------------: | -----------------------------: | --------------: |
| Windows  |                      Full |                 Supported |           Supported | Supported if server configured |       Supported |
| macOS    |     Limited / not primary | Supported where installed |           Supported | Supported if server configured |       Supported |
| Linux    |             Not supported |                 Supported |           Supported |                      Supported |       Supported |

Important wording:

> Full Microsoft Office automation remains Windows-first. Cross-platform productivity automation is provided through the Document Engine, LibreOffice, OnlyOffice, and Collabora providers where configured.

This prevents false expectations.

---

## 14. Health Check and Capability Probing

Phase 2 must extend the Office health check into a general Productivity Provider Health Check.

For each provider, Shogun should detect:

* Installed or configured status
* Version
* Launch capability
* API/CLI availability
* Required binaries
* License/configuration status where detectable
* Ability to open test file
* Ability to save output
* Ability to export PDF
* Ability to operate inside approved folders
* Known warnings
* Provider-specific limitations

Example UI:

| Provider         | Status         | Spreadsheet | Document | Presentation |       Mail | Notes                    |
| ---------------- | -------------- | ----------: | -------: | -----------: | ---------: | ------------------------ |
| Microsoft Office | Available      |        Pass |     Pass |         Pass | Draft-only | Windows COM ready        |
| LibreOffice      | Available      |        Pass |     Pass |         Pass |        N/A | UNO/headless ready       |
| OnlyOffice       | Not configured |         N/A |      N/A |          N/A |        N/A | Document Builder missing |
| Collabora        | Not configured |         N/A |      N/A |          N/A |        N/A | Server endpoint not set  |
| Document Engine  | Available      |        Pass |     Pass |         Pass |        N/A | Cross-platform fallback  |

The health check must be runnable before a company pilot.

---

## 15. Security and Posture Model

The existing posture model remains.

| Posture    | Productivity App Mode                                            |
| ---------- | ---------------------------------------------------------------- |
| Locked     | Disabled or file-only Document Engine                            |
| Guarded    | Enabled for approved providers, approved files, approved actions |
| Supervised | Broader actions with human confirmation                          |
| Ronin      | Full desktop control where explicitly enabled                    |

Guarded Posture rules:

* Approved folders only
* File Registry required
* No raw path execution by agents
* No overwrite of originals by default
* Output versioning required
* Macros blocked by default
* External links blocked by default where possible
* Email sending blocked unless explicitly approved
* All provider actions audited
* Provider routing must be logged
* Health check warnings must be visible

---

## 16. Mail Provider Strategy

Outlook is already handled by the Microsoft Office Provider.

Phase 2 should introduce a generic mail abstraction.

Potential mail modes:

1. Outlook draft provider
2. EML file generation
3. SMTP draft/send provider
4. IMAP/SMTP enterprise provider
5. Future provider for self-hosted mail systems

For sovereignty-conscious companies, Shogun should not assume Outlook.

The minimum generic mail capability should be:

```text
productivity.mail.create_draft_file
```

This creates an `.eml` draft in the approved output folder.

That file can be reviewed and sent manually.

This is safer and vendor-neutral.

Recommended Day-1 generic mail capabilities:

| Capability            | Requirement                    |
| --------------------- | ------------------------------ |
| Create `.eml` draft   | Yes                            |
| Attach approved files | Yes                            |
| Save to output folder | Yes                            |
| Human review          | Yes                            |
| SMTP send             | Optional / disabled by default |
| Bulk send             | Blocked                        |
| External recipients   | Warning / approval             |

This gives non-Outlook companies a usable mail workflow without immediate mail-server integration risk.

---

## 17. Provider Job Queue

The existing COM worker queue should be generalized into a Productivity Job Queue.

Different providers may have different concurrency models.

Default strategy:

| Provider                        | Concurrency policy                                     |
| ------------------------------- | ------------------------------------------------------ |
| Microsoft Office                | Serialized per app and per file                        |
| LibreOffice UNO                 | Serialized per LibreOffice profile/session             |
| LibreOffice headless conversion | Limited parallel workers if isolated profiles are used |
| OnlyOffice CLI                  | Queue with configurable parallelism                    |
| Collabora                       | API rate/tenant limits                                 |
| Document Engine                 | Parallel-safe with per-file locks                      |
| Generic Mail                    | Serialized per draft/send operation                    |

Core rule:

> Every file must have a lock while being written.

No two agents should write to the same output file at the same time.

The job queue should support:

* Job ID
* Provider ID
* Action
* File locks
* Timeout
* Retry policy
* Cleanup policy
* Audit events
* Result payload

---

## 18. Audit Integration

Phase 2 must not create a separate audit system.

All productivity events must flow through Shogun’s existing audit pipeline.

Event types:

```text
productivity.provider.selected
productivity.provider.health_check_started
productivity.provider.health_check_completed
productivity.file.registered
productivity.file.opened
productivity.file.read
productivity.file.written
productivity.file.exported_pdf
productivity.spreadsheet.range_read
productivity.spreadsheet.range_written
productivity.document.placeholder_replaced
productivity.presentation.slide_modified
productivity.mail.draft_created
productivity.mail.send_blocked
productivity.action.blocked
productivity.approval.required
productivity.approval.granted
productivity.approval.rejected
```

Each event should include:

* Provider used
* Tool requested
* File ID
* Resolved path hash
* Posture level
* Agent ID
* Run ID
* Timestamp
* Action status
* Error message if failed

This gives Shogun a strong enterprise audit story.

---

## 19. GUI Requirements

The Shogun GUI should be updated from Office-specific configuration to Productivity App Mode configuration.

### 19.1 Productivity App Mode Dashboard

Show:

* Enabled/disabled status
* Current posture
* Default provider
* Available providers
* Provider health status
* Active routing rules
* Last productivity action
* Audit status

---

### 19.2 Provider Management Screen

The admin should be able to:

* Enable/disable providers
* Set provider priority
* Run health checks
* View provider capabilities
* View provider limitations
* Configure provider-specific settings
* Select default provider per capability

Example:

| Capability   | Selected provider  |
| ------------ | ------------------ |
| Spreadsheet  | Microsoft Office   |
| Document     | LibreOffice        |
| Presentation | LibreOffice        |
| Mail         | EML Draft Provider |

---

### 19.3 Provider Health Screen

Show:

| Provider         | Installed | Version  | Health         | Warnings               |
| ---------------- | --------- | -------- | -------------- | ---------------------- |
| Microsoft Office | Yes       | Detected | Pass           | None                   |
| LibreOffice      | Yes       | Detected | Warning        | PDF export test failed |
| OnlyOffice       | No        | N/A      | Not configured | Missing builder path   |
| Collabora        | No        | N/A      | Not configured | Endpoint missing       |
| Document Engine  | Yes       | Internal | Pass           | None                   |

---

### 19.4 File Registry Screen

Show registered files:

| File ID         | Type         | Folder    | Provider compatibility                  | Status |
| --------------- | ------------ | --------- | --------------------------------------- | ------ |
| sales_input     | Spreadsheet  | Input     | Microsoft, LibreOffice, Document Engine | Ready  |
| report_template | Document     | Templates | Microsoft, LibreOffice, OnlyOffice      | Ready  |
| board_template  | Presentation | Templates | Microsoft, LibreOffice                  | Ready  |

---

## 20. Configuration Model

Extend `setup.json`, not YAML.

Example:

```json
{
  "productivity_app_mode": {
    "enabled": true,
    "minimum_posture": "guarded",
    "default_provider": "microsoft_office",
    "folders": {
      "input": "C:/ShogunSandbox/Input",
      "output": "C:/ShogunSandbox/Output",
      "templates": "C:/ShogunSandbox/Templates",
      "temp": "C:/ShogunSandbox/Temp"
    },
    "providers": {
      "microsoft_office": {
        "enabled": true,
        "visible": false,
        "legacy_office_tools_enabled": true
      },
      "libreoffice": {
        "enabled": true,
        "soffice_path": "auto",
        "mode": "headless_or_uno",
        "profile_isolation": true
      },
      "onlyoffice": {
        "enabled": false,
        "document_builder_path": "",
        "document_server_url": ""
      },
      "collabora": {
        "enabled": false,
        "server_url": "",
        "wopi_enabled": false
      },
      "document_engine": {
        "enabled": true
      },
      "generic_mail": {
        "enabled": true,
        "mode": "eml_draft_only"
      }
    },
    "routing": {
      "spreadsheet": "microsoft_office",
      "document": "document_engine",
      "presentation": "microsoft_office",
      "mail": "microsoft_office"
    },
    "safety": {
      "require_file_registry": true,
      "block_raw_paths_from_agents": true,
      "version_outputs": true,
      "block_macros_by_default": true,
      "block_external_links_by_default": true,
      "require_approval_for_send": true
    }
  }
}
```

---

## 21. Implementation Phases

Phase 2 is a development phase, not a staged product promise. The release should only be considered complete when the provider-based layer works end-to-end.

---

### Phase 2.1 — Abstraction Layer

Build:

* Productivity Adapter Layer
* Provider interface
* Provider registry
* Provider routing engine
* Generic tool schemas
* Backward compatibility aliases
* Setup.json configuration extension

Deliverable:

> Existing Microsoft Office tools can be called through provider-neutral productivity tools.

---

### Phase 2.2 — File Registry Extension

Build:

* File ID mapping
* Provider compatibility metadata
* File type detection
* SHA256 hashing
* Approved folder validation
* Raw path blocking
* Provider-specific file rules

Deliverable:

> Agents use file IDs, and Shogun resolves files safely through the registry.

---

### Phase 2.3 — Productivity Health Check

Build:

* Provider detection
* Provider capability probing
* Provider warnings
* Provider status UI
* Exportable health report

Deliverable:

> Before a pilot, Shogun can show which productivity providers are available and safe to use.

---

### Phase 2.4 — Document Engine Provider

Build:

* Spreadsheet read/write using file libraries
* Word document template filling
* Presentation template filling
* Basic document creation
* Output versioning
* PDF export only where supported or routed through another provider

Deliverable:

> Shogun can manipulate Office-format files without requiring installed Office applications.

---

### Phase 2.5 — LibreOffice Provider

Build:

* LibreOffice detection
* Headless conversion
* UNO or command execution layer
* Calc read/write
* Writer template processing
* Impress template processing
* PDF export
* Provider-specific error handling
* Profile isolation where needed

Deliverable:

> Shogun can operate LibreOffice Calc, Writer, and Impress in controlled workflows.

---

### Phase 2.6 — OnlyOffice Provider

Build:

* Document Builder CLI configuration
* Document Builder API configuration
* Template/data input support
* DOCX/XLSX/PPTX generation
* PDF export where configured
* Provider-specific health check

Deliverable:

> Shogun can generate documents, spreadsheets, and presentations through OnlyOffice where configured.

---

### Phase 2.7 — Collabora Provider

Build:

* Collabora endpoint configuration
* WOPI/server integration preparation
* Document registration
* Export/conversion support where configured
* Provider health check
* Provider limitations reporting

Deliverable:

> Shogun can integrate with Collabora-based document environments where the company provides the required server setup.

---

### Phase 2.8 — Generic Mail Provider

Build:

* EML draft generation
* Attachment handling
* Recipient validation
* Approval rules
* Optional SMTP configuration for later use
* Audit events

Deliverable:

> Shogun can prepare email drafts without requiring Outlook.

---

### Phase 2.9 — GUI Update

Build:

* Productivity App Mode dashboard
* Provider management
* Routing configuration
* Health check view
* File registry view
* Provider capability matrix
* Audit filtering by productivity events

Deliverable:

> Admins can configure and monitor provider-based Productivity App Mode from the GUI.

---

### Phase 2.10 — End-to-End Test Pack

Build test workflows for:

1. Microsoft Office provider
2. Document Engine provider
3. LibreOffice provider
4. OnlyOffice provider where configured
5. Collabora provider where configured
6. Generic mail provider

Deliverable:

> Shogun can run a controlled productivity workflow across multiple provider configurations.

---

## 22. MVP Acceptance Criteria

Phase 2 MVP is complete when:

1. Existing Microsoft Office functionality works through generic productivity tools.
2. Microsoft-specific tool names remain backward compatible.
3. File Registry is mandatory for productivity tool calls.
4. Provider routing works.
5. Provider health checks work.
6. Document Engine provider works cross-platform.
7. LibreOffice provider can generate and export basic spreadsheet, document, and presentation outputs.
8. Generic mail provider can create `.eml` drafts with approved attachments.
9. All actions are posture-controlled.
10. All actions are audited through Shogun’s existing audit pipeline.
11. The GUI shows available providers and routing.
12. Output versioning is enforced.
13. Raw paths from agents are blocked by default.
14. The system can be explained as provider-neutral to European companies.

OnlyOffice and Collabora may be marked as “configured provider support” if they require external server or builder setup.

---

## 23. Recommended Demonstration Workflow

Use a provider-neutral demo.

### Input

* One spreadsheet file
* One document template
* One presentation template
* One approved output folder
* One mail draft output

### Task

> Analyze the spreadsheet, generate a report document, generate a presentation summary, export outputs to PDF, and prepare an email draft with attachments.

### Demonstrate with two configurations

#### Configuration A: Microsoft-heavy company

| Capability   | Provider         |
| ------------ | ---------------- |
| Spreadsheet  | Microsoft Office |
| Document     | Microsoft Office |
| Presentation | Microsoft Office |
| Mail         | Outlook          |

#### Configuration B: European/open-source preference

| Capability   | Provider                       |
| ------------ | ------------------------------ |
| Spreadsheet  | LibreOffice                    |
| Document     | LibreOffice or Document Engine |
| Presentation | LibreOffice or Document Engine |
| Mail         | EML Draft Provider             |

This proves the strategic point:

> Shogun does not depend on one productivity vendor.

---

## 24. Key Risks

| Risk                                         | Mitigation                                                    |
| -------------------------------------------- | ------------------------------------------------------------- |
| Provider behavior differs                    | Capability manifest and provider warnings                     |
| Formatting differences                       | Template validation and PDF comparison                        |
| LibreOffice automation instability           | Health checks, profile isolation, fallback to Document Engine |
| OnlyOffice requires setup                    | Mark as configured provider, not default                      |
| Collabora requires server integration        | Treat as enterprise integration provider                      |
| Agents pass raw paths                        | Block raw paths; require File Registry                        |
| Multiple providers produce different outputs | Add provider-specific test baselines                          |
| User expects identical Microsoft rendering   | Show provider limitations clearly                             |
| Too much complexity in UI                    | Default to simple provider selection, advanced routing hidden |

---

## 25. Updated Product Message

The message to companies should be:

> Shogun can work with the productivity tools your company has chosen. It supports Microsoft Office, but it is not architecturally dependent on Microsoft Office.

For European companies:

> Shogun is designed with a provider-based productivity layer, allowing companies to use Microsoft Office, open-source office suites, or self-hosted document platforms depending on policy, sovereignty requirements, and technical fit.

For IT/security:

> Productivity actions are controlled through approved providers, approved files, approved folders, posture rules, file registry validation, and immutable audit logging.

---

## 26. Final Principle

Phase 2 should make Shogun strategically stronger.

The goal is not just to add LibreOffice or OnlyOffice.

The goal is to make Shogun provider-neutral.

The final principle is:

> Shogun should automate business productivity workflows without forcing the company into a specific productivity vendor.

That makes Shogun more relevant for Microsoft-heavy enterprises, sovereignty-conscious European companies, and open-source-first organizations.

---
