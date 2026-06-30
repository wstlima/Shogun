# Build Paper

# Shogun Office App Mode

## Day-1 controlled automation for Excel, Word, PowerPoint, and Outlook

---

## 1. Executive Summary

Shogun must support Microsoft Office application automation from the first company sandbox release.

This is not an optional future feature. It is a core requirement for making Shogun useful in real company environments, because many business sandbox experiments are based on existing Office workflows:

* Excel workbooks
* Word templates
* PowerPoint reports
* Outlook drafts
* PDF exports
* Folder-based input and output
* Existing company templates
* Reports generated from operational data

The purpose of **Office App Mode** is to allow Shogun to operate installed Microsoft Office applications in a controlled, permission-bound, auditable way.

This feature must be active from **Guarded Posture and upward**.

The principle is:

> Shogun may operate Office applications, but only through approved adapters, approved files, approved folders, approved actions, and logged execution.

Office App Mode is not the same as unrestricted desktop control.

It is a governed business-application automation layer.

---

## 2. Core Requirement

Office App Mode must support the following applications from Day 1:

1. Microsoft Excel
2. Microsoft Word
3. Microsoft PowerPoint
4. Microsoft Outlook

Day-1 support does not mean every possible Office feature is supported. It means each Office application must have a usable, tested, sandbox-ready capability set.

The minimum requirement is:

> Shogun must be able to open approved Office files, perform approved actions, save or export approved outputs, and log the full operation.

For Outlook, the Day-1 rule is stricter:

> Shogun may create drafts and prepare emails, but sending must require explicit approval unless the customer enables a higher permission level.

---

## 3. Why This Feature Matters

Without Office App Mode, Shogun risks appearing disconnected from how companies actually work.

Most companies do not begin AI sandbox experiments with advanced APIs. They begin with:

* “Can it update this Excel?”
* “Can it create this report?”
* “Can it fill out this Word template?”
* “Can it prepare the PowerPoint?”
* “Can it draft the email?”
* “Can it export the final PDF?”

Therefore, Shogun must meet companies where their workflows already exist.

The commercial argument is simple:

> If Shogun can operate the tools companies already use, it becomes immediately understandable and easier to pilot.

---

## 4. Feature Name

Recommended external name:

# Office App Mode

Recommended technical component name:

# Office Adapter Layer

Optional internal Shogun-style module name:

# Katana Office Adapter

Documentation should use the plain term **Office Adapter Layer** because it is clearer for enterprise stakeholders.

---

## 5. Position in Shogun Architecture

The Office Adapter Layer sits between Shogun agents and the installed Office applications.

The agent must not receive unrestricted desktop access.

Instead, the agent receives structured tool calls.

Example:

```text
office.excel.open_workbook
office.excel.read_range
office.excel.write_range
office.word.replace_placeholders
office.powerpoint.replace_text
office.outlook.create_draft
```

Not:

```text
control_desktop
click_button
move_mouse
type_anywhere
```

The purpose is to make Office automation controlled, testable, and auditable.

---

## 6. Revised Shogun Posture Model

Office App Mode must be mapped into the Shogun security posture model.

| Posture    | Office App Mode                   | Description                                                                    |
| ---------- | --------------------------------- | ------------------------------------------------------------------------------ |
| Locked     | Disabled                          | File-level read/write only. No Office application automation.                  |
| Guarded    | Enabled                           | Office apps may be operated only on approved files, folders, and actions.      |
| Supervised | Enabled                           | Broader Office operations allowed, but sensitive actions require confirmation. |
| Ronin      | Enabled + broader desktop control | Full desktop control available only when explicitly enabled.                   |

Core rule:

> Office App Mode is active from Guarded Posture and upward.

This is important because company sandbox experiments often need Office automation, but they still need a controlled posture.

---

## 7. Guarded Posture Rules

In Guarded Posture, Shogun may operate Office applications only within defined boundaries.

### 7.1 Folder Boundaries

Shogun may only access:

* Approved read folder
* Approved write folder
* Approved template folder
* Approved temporary working folder

Shogun must not access:

* Desktop
* Downloads
* Documents
* OneDrive
* SharePoint synced folders
* Network drives
* User profile folders
* Arbitrary paths

Unless those locations are explicitly approved in the posture configuration.

---

### 7.2 File Boundaries

Shogun may only open approved file types.

Initial allowed extensions:

```text
.xlsx
.xlsm only if macros are explicitly allowed
.docx
.pptx
.msg optional
.eml optional
.pdf output only
.csv
.txt
```

Initial blocked or restricted extensions:

```text
.exe
.bat
.cmd
.ps1
.vbs
.js
.com
.scr
.dll
.reg
.msi
```

Macro-enabled Office files should be blocked by default.

`.xlsm` can be allowed only if the company explicitly enables macro handling.

---

### 7.3 Action Boundaries

In Guarded Posture, Shogun may:

* Open approved files
* Read approved content
* Insert or replace content
* Update formulas
* Apply basic formatting
* Save as a new output file
* Export to PDF
* Create Outlook drafts
* Attach approved output files to drafts
* Log actions

Shogun may not:

* Run macros by default
* Open external data connections
* Send emails automatically
* Access files outside approved folders
* Overwrite original files by default
* Change Office security settings
* Install add-ins
* Access credentials
* Open browser links from Office documents
* Use arbitrary mouse/keyboard control unless Ronin mode is enabled

---

## 8. Technical Approach

The first implementation should target Windows company PCs.

Recommended approach:

```text
Python backend + pywin32 COM automation + FastAPI tool endpoints
```

Reason:

* The rest of Shogun already uses Python/FastAPI.
* Office on Windows exposes automation interfaces.
* COM automation allows structured control of installed Office applications.
* It is more reliable than visual desktop automation for Office tasks.
* It allows Shogun to operate Excel, Word, PowerPoint, and Outlook without giving the agent full desktop control.

The Office Adapter Layer should be implemented as a Python service/module inside the Shogun backend.

---

## 9. High-Level Architecture

```text
Shogun Agent
   ↓
Tool Permission Engine
   ↓
Office Adapter Layer
   ↓
Office Application Adapter
   ↓
Microsoft Excel / Word / PowerPoint / Outlook
   ↓
Approved Output Folder
```

Supporting components:

```text
Posture Config
Audit Logger
File Boundary Validator
Action Validator
Office Process Manager
Error Handler
Output Validator
Human Approval Handler
```

The agent never talks directly to COM automation.

The agent requests an approved Shogun tool.

The adapter validates the action.

Only then is Office automation executed.

---

## 10. Main Components

### 10.1 Office Adapter Layer

Responsible for:

* Receiving structured tool requests
* Checking posture permissions
* Validating file paths
* Validating allowed actions
* Opening Office applications
* Executing commands
* Saving outputs
* Exporting PDFs
* Closing Office processes
* Returning structured results
* Logging all operations

---

### 10.2 File Boundary Validator

Responsible for ensuring that every file path is inside an approved folder.

It must check:

* Absolute paths
* Relative paths
* Symlinks
* Shortcut files
* UNC paths
* Path traversal attempts
* File extension
* File size
* File lock status

Example rule:

```text
A file may only be opened if its resolved absolute path starts with an approved root folder.
```

This is critical.

The agent must never be able to escape approved directories by using `..\..\` or shortcut tricks.

---

### 10.3 Permission Engine

Responsible for checking whether the current Shogun posture allows the requested action.

Example:

```json
{
  "posture": "guarded",
  "application": "excel",
  "action": "write_range",
  "file": "input/report.xlsx",
  "allowed": true
}
```

Sensitive actions should require approval.

Examples:

| Action                        | Guarded | Supervised        | Ronin               |
| ----------------------------- | ------- | ----------------- | ------------------- |
| Open approved Excel file      | Allow   | Allow             | Allow               |
| Save as new file              | Allow   | Allow             | Allow               |
| Overwrite original            | Block   | Approval          | Allow if configured |
| Run macro                     | Block   | Approval          | Approval            |
| Send Outlook email            | Block   | Approval          | Approval            |
| Open external link            | Block   | Approval          | Approval            |
| Use arbitrary desktop control | Block   | Block or approval | Allow if configured |

---

### 10.4 Office Process Manager

Responsible for managing Office application lifecycle.

It must:

* Open Office apps when needed
* Run in visible or hidden mode depending on setting
* Track opened files
* Close files after operation
* Quit Office app instances when done
* Avoid leaving zombie Excel/Word/PowerPoint processes
* Detect hanging Office dialogs
* Timeout stalled operations
* Return meaningful errors

Important design rule:

> Every Office automation session must have a defined start, timeout, cleanup, and log entry.

---

### 10.5 Audit Logger

Every action must be logged.

Minimum audit fields:

| Field             | Description                      |
| ----------------- | -------------------------------- |
| timestamp         | When action occurred             |
| run_id            | Unique Shogun execution ID       |
| agent_id          | Which agent requested the action |
| user/session      | Which user/session initiated it  |
| posture           | Current posture                  |
| application       | Excel, Word, PowerPoint, Outlook |
| action            | Tool/action name                 |
| input_file        | Source file path                 |
| output_file       | Output file path                 |
| status            | Success/failure                  |
| duration          | Execution time                   |
| approval_required | Yes/no                           |
| approval_result   | Approved/rejected/not required   |
| error_message     | If failed                        |

Logs should be available in:

* JSONL audit log
* Shogun UI
* Optional exported audit report

---

## 11. Application-Specific Requirements

---

# 11.1 Excel Adapter

## Purpose

The Excel Adapter allows Shogun to operate Microsoft Excel workbooks in a controlled and auditable way.

## Day-1 Capabilities

Shogun must be able to:

* Open approved Excel workbooks
* Read workbook metadata
* List sheets
* Read used ranges
* Read named ranges
* Read specific cell/range values
* Read formulas
* Write values to approved ranges
* Create new sheets
* Copy sheets to new output workbook
* Apply basic formatting
* Refresh calculations
* Save as new workbook
* Export workbook or sheet to PDF
* Close workbook safely

## Day-1 Tool Functions

```text
office.excel.open_workbook
office.excel.close_workbook
office.excel.list_sheets
office.excel.read_used_range
office.excel.read_range
office.excel.read_named_range
office.excel.write_range
office.excel.create_sheet
office.excel.copy_sheet
office.excel.apply_basic_formatting
office.excel.calculate
office.excel.save_as
office.excel.export_pdf
office.excel.get_workbook_metadata
```

## Excel Safety Rules

* Do not overwrite source files by default.
* Save all outputs with timestamped filenames.
* Block external workbook links by default.
* Block macros by default.
* Disable alerts where safe.
* Detect password-protected files and return a controlled error.
* Detect corrupted files and return a controlled error.
* Log all read/write ranges.
* Never open files outside approved folders.

## Example Tool Request

```json
{
  "tool": "office.excel.write_range",
  "file_id": "sales_report_input",
  "sheet": "Summary",
  "range": "B4:D12",
  "values": [
    ["Product", "Revenue", "Margin"],
    ["A", 100000, 0.24],
    ["B", 75000, 0.19]
  ],
  "save_as": "output/sales_report_updated.xlsx"
}
```

## Example Result

```json
{
  "status": "success",
  "application": "excel",
  "action": "write_range",
  "output_file": "C:/Shogun/output/sales_report_updated_2026-07-01_1045.xlsx",
  "audit_id": "audit_93820",
  "duration_ms": 1832
}
```

---

# 11.2 Word Adapter

## Purpose

The Word Adapter allows Shogun to operate Word documents and templates.

## Day-1 Capabilities

Shogun must be able to:

* Open approved `.docx` files
* Open approved templates
* Read document text
* Read headings
* Replace placeholders
* Insert paragraphs
* Insert tables
* Insert content from Excel/data
* Apply basic styles
* Save as new document
* Export to PDF
* Close document safely

## Day-1 Tool Functions

```text
office.word.open_document
office.word.close_document
office.word.read_text
office.word.read_headings
office.word.replace_placeholders
office.word.insert_paragraph
office.word.insert_table
office.word.apply_style
office.word.save_as
office.word.export_pdf
office.word.get_document_metadata
```

## Placeholder Standard

Word templates should support placeholders such as:

```text
{{company_name}}
{{report_date}}
{{executive_summary}}
{{risk_table}}
{{recommendation}}
```

This makes Word automation deterministic and safer.

## Word Safety Rules

* Never overwrite original templates by default.
* Save generated documents as new files.
* Block macros by default.
* Block external links by default.
* Do not accept tracked changes automatically unless explicitly allowed.
* Preserve original template formatting where possible.
* Log all placeholder replacements.
* Log exported PDFs.

## Example Tool Request

```json
{
  "tool": "office.word.replace_placeholders",
  "template_file": "templates/monthly_report.docx",
  "placeholders": {
    "{{company_name}}": "Example GmbH",
    "{{report_date}}": "2026-07-01",
    "{{executive_summary}}": "The analysis indicates stable performance with increased risk in supplier lead times."
  },
  "save_as": "output/monthly_report_generated.docx"
}
```

---

# 11.3 PowerPoint Adapter

## Purpose

The PowerPoint Adapter allows Shogun to create and update presentation decks based on approved templates.

## Day-1 Capabilities

Shogun must be able to:

* Open approved `.pptx` templates
* Read slide titles
* Replace text placeholders
* Insert text boxes
* Insert tables
* Insert images from approved output folders
* Insert simple charts as images
* Duplicate slides
* Delete slides only if explicitly allowed
* Save as new presentation
* Export to PDF
* Close presentation safely

## Day-1 Tool Functions

```text
office.powerpoint.open_presentation
office.powerpoint.close_presentation
office.powerpoint.list_slides
office.powerpoint.read_slide_text
office.powerpoint.replace_text
office.powerpoint.replace_placeholders
office.powerpoint.insert_textbox
office.powerpoint.insert_table
office.powerpoint.insert_image
office.powerpoint.duplicate_slide
office.powerpoint.save_as
office.powerpoint.export_pdf
office.powerpoint.get_presentation_metadata
```

## PowerPoint Template Standard

Templates should include placeholders such as:

```text
{{title}}
{{subtitle}}
{{executive_summary}}
{{key_findings}}
{{recommendation}}
{{chart_1}}
{{table_1}}
```

PowerPoint automation should favor replacing placeholders over arbitrary layout generation.

This reduces risk and improves output quality.

## PowerPoint Safety Rules

* Never overwrite original template.
* Save new presentation to approved output folder.
* Only insert images from approved folders.
* Do not activate external media or links.
* Do not run embedded scripts or macros.
* Export to PDF for review.
* Log each slide modified.

---

# 11.4 Outlook Adapter

## Purpose

The Outlook Adapter allows Shogun to prepare communication outputs in a controlled way.

Outlook is the highest-risk Office application because it can send information outside the company.

Therefore, Outlook must be more restricted than Excel, Word, and PowerPoint.

## Day-1 Capabilities

Shogun must be able to:

* Create email drafts
* Set recipient fields only from approved input or user confirmation
* Set subject
* Set body
* Attach approved output files
* Save draft
* Open draft for human review
* Send only with explicit approval

## Day-1 Tool Functions

```text
office.outlook.create_draft
office.outlook.set_recipients
office.outlook.set_subject
office.outlook.set_body
office.outlook.attach_file
office.outlook.save_draft
office.outlook.open_draft_for_review
office.outlook.send_with_confirmation
office.outlook.get_draft_metadata
```

## Outlook Safety Rules

* Sending is blocked by default in Guarded Posture.
* Draft creation is allowed.
* Attachments must come only from approved output folders.
* Recipients must be visible in the approval screen.
* External recipients should trigger a warning.
* Bulk sending is blocked.
* Auto-forwarding is blocked.
* Reading mailbox content is disabled unless explicitly enabled.
* No credential extraction.
* No hidden sending.
* Every draft and send request is logged.

## Outlook Permission Levels

| Permission level        | Capability                          |
| ----------------------- | ----------------------------------- |
| Draft-only              | Create drafts, no sending           |
| Confirmed send          | Send only after human approval      |
| Approved recipient send | Send only to allowlisted recipients |
| Full send               | Not recommended for initial sandbox |

Initial company sandbox mode should use:

```text
Draft-only
```

or:

```text
Confirmed send
```

---

## 12. User Interface Requirements

The Shogun GUI must include an Office App Mode configuration screen.

### 12.1 Office App Mode Settings

The screen should allow the user/admin to configure:

* Enable/disable Office App Mode
* Select posture level
* Enable Excel
* Enable Word
* Enable PowerPoint
* Enable Outlook
* Configure read folders
* Configure write folders
* Configure template folders
* Configure temp folder
* Configure macro policy
* Configure overwrite policy
* Configure Outlook send policy
* Configure visible/hidden Office mode
* Configure timeout values
* Configure logging level

---

### 12.2 Approved Folders Screen

The admin should define folders like:

```text
C:\ShogunSandbox\Input
C:\ShogunSandbox\Output
C:\ShogunSandbox\Templates
C:\ShogunSandbox\Temp
```

Each folder should have a purpose:

| Folder    | Permission                                  |
| --------- | ------------------------------------------- |
| Input     | Read-only                                   |
| Output    | Write-only / read-write for generated files |
| Templates | Read-only                                   |
| Temp      | Read-write, auto-cleanup                    |

---

### 12.3 Office Application Status Screen

The UI should show:

| Application | Status                | Enabled    | Last action         |
| ----------- | --------------------- | ---------- | ------------------- |
| Excel       | Installed / available | Yes        | Updated workbook    |
| Word        | Installed / available | Yes        | Generated report    |
| PowerPoint  | Installed / available | Yes        | Created deck        |
| Outlook     | Installed / available | Draft-only | Created email draft |

---

### 12.4 Audit Log Screen

The UI should show:

* Timestamp
* Application
* Action
* Input file
* Output file
* Agent
* Status
* Approval
* Duration
* Error message

This is important for company trust.

---

## 13. Backend API Design

The Office Adapter Layer should expose internal FastAPI endpoints.

Example endpoints:

```text
GET  /api/v1/office/status
GET  /api/v1/office/config
POST /api/v1/office/config
POST /api/v1/office/validate-path
POST /api/v1/office/excel/open
POST /api/v1/office/excel/read-range
POST /api/v1/office/excel/write-range
POST /api/v1/office/excel/save-as
POST /api/v1/office/excel/export-pdf
POST /api/v1/office/word/replace-placeholders
POST /api/v1/office/word/export-pdf
POST /api/v1/office/powerpoint/replace-placeholders
POST /api/v1/office/powerpoint/export-pdf
POST /api/v1/office/outlook/create-draft
POST /api/v1/office/outlook/send-with-confirmation
GET  /api/v1/office/audit
```

These endpoints should not be exposed externally by default.

They should be local/internal to Shogun unless the admin explicitly enables Nexus-level access.

---

## 14. Internal Tool Schema

Shogun agents should receive tools using strict schemas.

Example Excel write schema:

```json
{
  "name": "office.excel.write_range",
  "description": "Write values to an approved range in an approved Excel workbook and save as a new output file.",
  "parameters": {
    "file_id": "string",
    "sheet": "string",
    "range": "string",
    "values": "array",
    "save_as": "string"
  },
  "permissions": {
    "minimum_posture": "guarded",
    "allowed_apps": ["excel"],
    "requires_approval": false,
    "blocks_original_overwrite": true
  }
}
```

Example Outlook draft schema:

```json
{
  "name": "office.outlook.create_draft",
  "description": "Create an Outlook email draft using approved content and approved attachments.",
  "parameters": {
    "to": "array",
    "cc": "array",
    "subject": "string",
    "body": "string",
    "attachments": "array"
  },
  "permissions": {
    "minimum_posture": "guarded",
    "allowed_apps": ["outlook"],
    "requires_approval": true,
    "send_allowed": false
  }
}
```

---

## 15. Configuration File

Office App Mode should have a dedicated configuration section.

Example:

```yaml
office_app_mode:
  enabled: true
  minimum_posture: guarded

  folders:
    input: "C:/ShogunSandbox/Input"
    output: "C:/ShogunSandbox/Output"
    templates: "C:/ShogunSandbox/Templates"
    temp: "C:/ShogunSandbox/Temp"

  applications:
    excel:
      enabled: true
      visible: false
      allow_macros: false
      allow_external_links: false
      overwrite_originals: false
      timeout_seconds: 60

    word:
      enabled: true
      visible: false
      allow_macros: false
      overwrite_originals: false
      timeout_seconds: 60

    powerpoint:
      enabled: true
      visible: false
      allow_macros: false
      overwrite_originals: false
      timeout_seconds: 90

    outlook:
      enabled: true
      mode: draft_only
      allow_send: false
      require_confirmation: true
      allow_external_recipients: false
      timeout_seconds: 60

  logging:
    enabled: true
    level: detailed
    jsonl_path: "C:/ShogunSandbox/Logs/office_audit.jsonl"

  safety:
    block_path_traversal: true
    block_shortcuts: true
    block_unc_paths: true
    version_outputs: true
    require_output_validation: true
```

---

## 16. Output Versioning

Shogun must not overwrite original files by default.

All outputs should be versioned.

Recommended format:

```text
{original_name}_shogun_{YYYYMMDD_HHMMSS}.{extension}
```

Example:

```text
sales_report_shogun_20260701_104500.xlsx
monthly_report_shogun_20260701_104520.docx
board_update_shogun_20260701_104550.pptx
```

This protects the company from accidental data loss.

---

## 17. Human Approval Layer

Certain actions must trigger approval.

Approval should be built into the Shogun UI.

Actions requiring approval in Guarded Posture:

* Sending Outlook email
* Overwriting original files
* Running macros
* Opening external links
* Refreshing external data connections
* Accessing files outside standard folders
* Attaching files to email
* Deleting slides/pages/sheets
* Large batch operations

Approval prompt example:

```text
Shogun wants to create an Outlook email draft.

Recipients:
- purchasing@example.com

Attachments:
- C:\ShogunSandbox\Output\supplier_analysis.pdf

Action:
Create draft only.

Approve?
[Approve] [Reject]
```

For the first sandbox release, Outlook sending should remain disabled unless explicitly enabled by the admin.

---

## 18. Error Handling

Office automation can fail because of:

* Missing Office installation
* License issues
* Password-protected files
* Corrupted files
* Locked files
* Open dialogs
* Protected View
* Trust Center restrictions
* File permission issues
* Hung Office process
* Invalid sheet/range names
* Missing placeholders
* External links
* Macro restrictions

The system must return clear errors.

Bad error:

```text
COM error 0x800A03EC
```

Good error:

```text
Excel could not write to the workbook because the target sheet "Summary" does not exist. No output file was created.
```

Every failure must include:

* Action attempted
* File involved
* Reason
* Whether anything was changed
* Suggested next step

---

## 19. Testing Requirements

Testing must be strict because this feature will be used in company environments.

### 19.1 Unit Tests

Test:

* Path validation
* Extension validation
* Permission validation
* Posture mapping
* Tool schemas
* Output naming
* Log generation
* Approval requirements

---

### 19.2 Integration Tests

Test with actual Office applications installed.

Excel tests:

* Open workbook
* Read range
* Write range
* Create new sheet
* Save as
* Export PDF
* Handle missing sheet
* Handle locked file

Word tests:

* Open template
* Replace placeholders
* Insert table
* Save as
* Export PDF
* Handle missing placeholder

PowerPoint tests:

* Open template
* Replace placeholders
* Insert image
* Insert table
* Save as
* Export PDF
* Handle missing slide

Outlook tests:

* Create draft
* Add recipient
* Add subject
* Add body
* Attach file
* Save draft
* Block send without approval
* Block external recipient if not allowed

---

### 19.3 Security Tests

Test:

* Path traversal attack
* Shortcut path attack
* UNC path attempt
* Macro-enabled file blocked
* External link blocked
* Unauthorized folder blocked
* Attempt to overwrite original blocked
* Attempt to send email blocked
* Attempt to attach unauthorized file blocked

---

### 19.4 Pilot Acceptance Tests

Before company deployment, run this test suite:

| Test                                | Expected result        |
| ----------------------------------- | ---------------------- |
| Excel file opened from input folder | Success                |
| Excel file outside input folder     | Blocked                |
| Excel output saved to output folder | Success                |
| Excel original overwrite attempt    | Blocked                |
| Word template filled                | Success                |
| Word exported to PDF                | Success                |
| PowerPoint generated from template  | Success                |
| PowerPoint exported to PDF          | Success                |
| Outlook draft created               | Success                |
| Outlook send without approval       | Blocked                |
| Macro-enabled workbook              | Blocked unless enabled |
| Full audit log generated            | Success                |

---

## 20. MVP Feature Definition

The Office App Mode MVP must include:

### Excel

* Open workbook
* Read sheet/range
* Write range
* Recalculate
* Save as
* Export PDF

### Word

* Open template/document
* Replace placeholders
* Insert table
* Save as
* Export PDF

### PowerPoint

* Open template/presentation
* Replace placeholders
* Insert image/table
* Save as
* Export PDF

### Outlook

* Create draft
* Add recipients
* Add subject/body
* Attach approved files
* Save draft
* Block sending unless confirmed

### Cross-cutting

* Folder boundary enforcement
* Posture enforcement
* Audit logging
* Output versioning
* Error handling
* Approval handling
* UI configuration
* Test suite

---

## 21. Implementation Phases

Although all Office applications must work from the start, implementation should still be structured internally.

This is not a staged product release. It is a staged development plan toward one Day-1 release.

### Phase 1: Foundation

Build:

* Office Adapter Layer structure
* Posture permission engine
* File boundary validator
* Audit logger
* Output versioning
* Office process manager
* Configuration model
* UI settings screen

Deliverable:

> Shogun can validate and govern Office tool calls before execution.

---

### Phase 2: Excel Adapter

Build:

* Excel COM wrapper
* Workbook open/close
* Sheet listing
* Range reading
* Range writing
* Calculation refresh
* Save as
* PDF export
* Excel error handling

Deliverable:

> Shogun can safely update and export approved Excel workbooks.

---

### Phase 3: Word Adapter

Build:

* Word COM wrapper
* Document open/close
* Text extraction
* Placeholder replacement
* Table insertion
* Save as
* PDF export
* Word error handling

Deliverable:

> Shogun can generate Word reports from approved templates.

---

### Phase 4: PowerPoint Adapter

Build:

* PowerPoint COM wrapper
* Presentation open/close
* Slide listing
* Text replacement
* Placeholder replacement
* Image insertion
* Table insertion
* Save as
* PDF export
* PowerPoint error handling

Deliverable:

> Shogun can generate PowerPoint presentations from approved templates.

---

### Phase 5: Outlook Adapter

Build:

* Outlook COM wrapper
* Draft creation
* Recipient handling
* Subject/body insertion
* Attachment handling
* Draft saving
* Send approval block
* Outlook error handling

Deliverable:

> Shogun can prepare Outlook drafts safely without uncontrolled sending.

---

### Phase 6: End-to-End Sandbox Workflow

Build a demo workflow:

1. Read Excel export from input folder.
2. Analyze data.
3. Update Excel output.
4. Generate Word summary.
5. Generate PowerPoint summary.
6. Export PDF versions.
7. Create Outlook draft with outputs attached.
8. Log every step.
9. Require human review before anything leaves the machine.

Deliverable:

> Complete company sandbox demonstration using all Office applications.

---

## 22. Recommended First Company Sandbox Workflow

For the German company pilot, use a simple but impressive workflow.

Example:

### Input

* One Excel workbook in the input folder
* One Word template in the template folder
* One PowerPoint template in the template folder

### Shogun Task

> Analyze the Excel workbook, identify key findings, generate an updated Excel output, create a Word summary report, create a PowerPoint summary deck, export both to PDF, and prepare an Outlook draft for review.

### Output

* Updated Excel workbook
* Word report
* PowerPoint deck
* PDF report
* PDF deck
* Outlook draft
* Audit log

This proves:

* Local execution
* Office automation
* Controlled folder access
* Business usefulness
* Human-in-the-loop safety
* Auditability

This is a strong first enterprise sandbox story.

---

## 23. Key Risk Controls

| Risk                              | Control                           |
| --------------------------------- | --------------------------------- |
| Shogun opens wrong file           | Folder/path validation            |
| Shogun overwrites source file     | Output versioning                 |
| Shogun sends email accidentally   | Outlook send blocked by default   |
| Shogun runs macro                 | Macros blocked by default         |
| Shogun accesses sensitive folders | Approved folder enforcement       |
| Office hangs                      | Timeout and cleanup               |
| Output is wrong                   | Human review                      |
| Company worries about black box   | Open code and audit logs          |
| IT worries about control          | Posture settings                  |
| User worries about trust          | Visible logs and approval prompts |

---

## 24. Documentation Requirements

Create documentation for:

1. Office App Mode overview
2. Guarded Posture rules
3. Approved folder setup
4. Excel adapter usage
5. Word adapter usage
6. PowerPoint adapter usage
7. Outlook adapter usage
8. Security and limitations
9. Audit log explanation
10. Pilot setup guide
11. Troubleshooting guide
12. Admin configuration guide

The documentation should be written for both:

* Business users
* IT/security reviewers

---

## 25. Final Acceptance Criteria

Office App Mode is ready when:

1. Excel, Word, PowerPoint, and Outlook all work in Guarded Posture.
2. Shogun can operate approved Office files without full desktop control.
3. Shogun cannot access files outside approved folders.
4. Shogun cannot overwrite originals by default.
5. Shogun cannot send Outlook emails without approval.
6. Macros are blocked by default.
7. Every action is logged.
8. Errors are understandable.
9. Outputs are versioned.
10. The full demo workflow runs end-to-end.
11. The feature can be explained clearly to company IT.
12. The system remains safe enough for a one-PC, no-internet sandbox.

---

## 26. Final Principle

Office App Mode must make Shogun more useful without making it reckless.

The correct enterprise message is:

> Shogun can operate the Office applications companies already use, but it does so through controlled, audited, permission-bound adapters.

This is what makes it suitable for real sandbox experiments.

The goal is not to give Shogun unlimited access to the desktop.

The goal is to give Shogun reliable access to the business tools companies already trust.

---
