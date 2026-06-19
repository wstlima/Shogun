<p align="center">
  <img src="Assets/shogun-afm-logo.png" alt="Shogun AFM Logo" width="200" />
</p>

<h1 align="center">🏯 Shogun AFM — Your AI Command Center</h1>

<p align="center">
  <strong>Shogun is an AI agent control plane with persistent memory, multi-agent orchestration, and full governance. Build, manage, and evolve agents via GUI—no terminal required. Powered by Qdrant, skill systems, and secure, inspectable autonomy.</strong>
</p>

<p align="center">
  <a href="https://github.com/AlphaHorizon-AI/Shogun/releases/latest"><img src="https://img.shields.io/github/v/release/AlphaHorizon-AI/Shogun?style=flat-square&label=Version&color=d4a017" alt="Version" /></a>
  <a href="#-14-supported-languages"><img src="https://img.shields.io/badge/Languages-14-blue?style=flat-square" alt="Languages" /></a>
  <a href="#-install-shogun-one-click"><img src="https://img.shields.io/badge/Install-One_Click-green?style=flat-square" alt="Install" /></a>
  <a href="https://www.youtube.com/@ShogunAIAgents"><img src="https://img.shields.io/badge/YouTube-Video_Guides-red?style=flat-square&logo=youtube" alt="YouTube" /></a>
</p>

---

## 📺 Complete Video Guide

New to Shogun? **Watch the full walkthrough series** on our YouTube channel — from installation to advanced workflows:

### **[▶️ youtube.com/@ShogunAIAgents](https://www.youtube.com/@ShogunAIAgents)**

---

## ⚡ Why Shogun?

Most AI tools give you a chat box. Shogun gives you an **entire operating system for AI agents**.

| | What You Get |
|---|---|
| 🧠 **Multi-Model Intelligence** | Connect OpenAI, Anthropic, Google, Perplexity, OpenRouter, or run local models via Ollama — all at once. Intelligent routing sends each task to the right brain. |
| 🥷 **Agent Fleet** | Deploy specialized sub-agents (Samurai) for research, coding, analysis, or any domain. The Shogun orchestrates them automatically. |
| 📚 **Persistent Memory** | Your AI remembers everything across sessions. Semantic search, salience scoring, and automatic memory consolidation — powered by embedded Qdrant. |
| 🌐 **Browser Automation (Mado)** | Your AI can browse the web, extract content, and take screenshots — all controlled through a secure Playwright layer. |
| 📧 **Email & Calendar** | Connect your IMAP/SMTP inbox and CalDAV calendar. Your Shogun can read, compose, and send emails — and manage your schedule. |
| 💬 **Telegram Integration** | Talk to your AI from your phone. Full streaming responses with live typing indicators. |
| 🔗 **Agent-to-Agent (Nexus)** | Connect multiple Shogun instances via peer-to-peer Nexus, **and** accept tasks from external enterprise agents (Microsoft 365, Salesforce, Google, ServiceNow) through the Nexus External Gateway with governed A2A interoperability. |
| 🔄 **Visual Workflow Builder** | Design multi-step AI pipelines with a drag-and-drop canvas. Chain agents, approvals, logic gates, and browser actions into executable flows. |
| 📜 **Constitutional Governance** | Write YAML rules your AI can never break. Version-controlled, auditable, with enforcement modes (Block / Warn / Audit). |
| 🛡️ **5-Tier Security** | From SHRINE (zero-trust) to RONIN (unrestricted). Fine-grained control over filesystem, network, shell, and tool access. Emergency kill switch (Harakiri) freezes everything instantly. |
| 📊 **Compliance Dashboard** | NIS2, SOC2, and EU AI Act-ready logging. Tamper-proof HMAC audit chain, trace reconstruction, and compliance exports. |
| 🎓 **4,000+ Skills (Dojo)** | Browse and certify your agents on specialized skills from [OpenClaw College](https://www.openclawcollege.com). Training literature, exams, and achievement tracking. |
| 🔄 **Self-Improvement (Bushido)** | Automated reflection cycles where the AI analyzes its own performance and generates optimization insights. |
| 💾 **Backup & Auto-Updates** | Scheduled backups with configurable retention. One-click updates that preserve all your data and settings. |
| 🌍 **14 Languages** | The entire interface is fully translated. Switch anytime from the dashboard. |
| 🏗️ **Setup Wizard** | 8-step guided onboarding gets you operational in minutes. |

**No cloud account needed. No Docker required. Everything runs locally.**

---

## 🎖️ Gensui — Agent Fleet Management

<p align="center">
  <img src="Assets/shogun-afm-logo.png" alt="Shogun AFM Logo" width="200" />
</p>

<p align="center">
  <strong>Shogun AFM (Agent Fleet Management)</strong><br/>
  A dedicated central command platform for managing, monitoring, and securing fleets of Shogun AI agents across your organization.
</p>

When you move beyond a single Shogun instance, **Gensui** becomes your command-and-control hub. It provides real-time visibility into every agent in your fleet — whether that's 3 machines in a startup or 500+ across a global enterprise.

### What Gensui Does

| Capability | Description |
|---|---|
| 📡 **Real-Time Fleet Dashboard** | Live status of every enrolled Shogun instance — online/offline state, samurai count, active workflows, and version info. |
| 🗺️ **Interactive Network Topology** | Visual SVG map of your entire agent fleet with pan/zoom, hub-and-spoke layout, and nexus peer connection lines. |
| 🔍 **LAN Network Scanner** | One-click scan of your local network to discover Shogun instances. Detects enrolled agents, unenrolled (rogue) agents, and unknown services on port 8000. |
| ⚠️ **Rogue Agent Detection** | Instantly spot unauthorized Shogun instances running on your network — critical for security compliance and preventing shadow AI. |
| 🎟️ **Enrollment Token System** | Generate secure enrollment tokens for new Shogun instances. Approve/reject enrollment requests with optional labels. |
| 🏷️ **Group Management** | Organize agents into logical groups (by team, environment, region). Apply policies and postures at the group level. |
| 🛡️ **Security Posture Control** | Define and enforce security postures across your fleet. Standard, Elevated, and Lockdown modes with granular permission control. |
| 💀 **Remote Harakiri** | Emergency kill switch — instantly freeze any agent (soft freeze, hard stop, network isolate, or full terminate) from the Gensui dashboard. |
| 📋 **Centralized Audit Log** | Tamper-proof HMAC-chained audit trail across all managed agents. NIS2/SOC2/EU AI Act compliant. |
| 🔒 **Admin Authentication** | JWT-based admin portal with role-based access control (Owner, Admin, Viewer). |

### Install Gensui (One Click)

Download **one file** for your platform, double-click it, and you're done:

| Platform | Download | Instructions |
|----------|----------|-------------|
| **🪟 Windows** | [⬇️ **Gensui-Install.bat**](https://github.com/AlphaHorizon-AI/Shogun/releases/latest/download/Gensui-Install.bat) | **Click to download** → Double-click the file |
| **🍎 macOS** | [⬇️ **Gensui-Install.command**](https://github.com/AlphaHorizon-AI/Shogun/releases/latest/download/Gensui-Install.command) | **Click to download** → Double-click the file |
| **🐳 Docker (Server)** | [⬇️ **Gensui-Docker-Install.sh**](https://github.com/AlphaHorizon-AI/Shogun/releases/latest/download/Gensui-Docker-Install.sh) | **Click to download** → `bash Gensui-Docker-Install.sh` |
| **🪟 Docker (Windows)** | [⬇️ **Gensui-Docker-Install.bat**](https://github.com/AlphaHorizon-AI/Shogun/releases/latest/download/Gensui-Docker-Install.bat) | **Click to download** → Double-click the file |

### Deployment Options (Advanced)

Gensui runs independently from Shogun instances and can also be deployed manually via Docker if you prefer not to use the one-click scripts:

| Deployment | Command | Best For |
|---|---|---|
| **🪟 Windows Desktop** | Double-click `gensui/install.bat` | Personal fleet on a Windows machine |
| **🍎 macOS / Linux Desktop** | `./gensui/install.sh` | Personal fleet on Mac or Linux |
| **🐳 Docker (Server)** | `docker compose up` | Production server, always-on |
| **🐳 Docker + TLS** | `docker compose --profile server up` | Production with Nginx reverse proxy, HTTPS, rate limiting |

<details>
<summary><strong>Quick Start — Local Install</strong></summary>

```bash
# Clone the repo
git clone https://github.com/AlphaHorizon-AI/Shogun.git
cd Shogun/gensui

# Windows
install.bat

# macOS / Linux
chmod +x install.sh && ./install.sh
```

Gensui starts at **http://localhost:8787**. Default credentials: `admin@gensui.local` / `changeme`.

</details>

<details>
<summary><strong>Quick Start — Manual Docker Server</strong></summary>

```bash
cd Shogun/gensui

# Setup config
cp .env.example .env
# Edit .env and change GENSUI_JWT_SECRET to a random 64-char string

# Basic (no TLS)
docker compose up -d

# Production with TLS (place certs in ./certs/gensui.crt and ./certs/gensui.key)
docker compose --profile server up -d
```

Includes Nginx reverse proxy with:
- TLS 1.2/1.3 termination
- Rate limiting (30 req/s API, 5 req/min auth)
- Security headers (HSTS, X-Frame-Options, CSP)
- Health checks

</details>

### How It Works

```
┌─────────────────────────────────────────────────┐
│                    GENSUI                       │
│              Agent Fleet Manager                │
│                                                 │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│   │ Dashboard │  │ Network  │  │ Enrollment│    │
│   │          │  │ Topology │  │ & Tokens  │    │
│   └──────────┘  └──────────┘  └──────────┘    │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│   │  Groups  │  │ Security │  │  Harakiri │    │
│   │          │  │ Postures │  │ Kill Switch│    │
│   └──────────┘  └──────────┘  └──────────┘    │
└────────────────────┬────────────────────────────┘
                     │ Heartbeat Protocol
         ┌───────────┼───────────┐
         │           │           │
    ┌────▼────┐ ┌────▼────┐ ┌────▼────┐
    │ Shogun  │ │ Shogun  │ │ Shogun  │
    │ Alpha   │ │ Bravo   │ │ Charlie │
    │ (prod)  │ │ (prod)  │ │ (stage) │
    └────┬────┘ └────┬────┘ └─────────┘
         │           │
         └─── Nexus ─┘
        (peer-to-peer)
```

Each Shogun instance sends periodic heartbeats to Gensui with status, metrics, and version info. Gensui cross-references these against its enrollment database to classify every agent as enrolled, unenrolled, or unknown — providing instant visibility into your fleet's security posture.

---

## 🔗 Nexus External Gateway — Enterprise Agent Interoperability

Shogun isn't limited to its own agent ecosystem. The **Nexus External Gateway** lets enterprise agents from other platforms — Microsoft 365 Copilot agents, Salesforce Einstein agents, Google Vertex agents, ServiceNow virtual agents — send tasks directly into Shogun for execution, all governed by the same security policies as internal operations.

This is **not** about replacing enterprise agents. It's about letting Shogun serve as an independent execution and orchestration layer that works *alongside* them.

### Three Operating Modes

| Mode | Description |
|------|-------------|
| 🏯 **Standalone** | Shogun runs independently with local agents, models, browser control, and memory. No external connectivity needed. |
| 🔗 **Enterprise-Connected** | External enterprise agents submit tasks via A2A, webhooks, or MCP. Shogun executes and returns results. |
| 🛡️ **Governed Hybrid** | Both modes combined, with Gensui enforcing security postures, platform allowlists, and real-time policy checks on every inbound task. |

### How It Works

```
                     ┌─────────────────────────────────────┐
                     │    External Enterprise Agents        │
                     │  (M365 · Salesforce · Google · SNow) │
                     └────────────────┬────────────────────┘
                                      │ A2A / Webhook / MCP
                                      ▼
                     ┌────────────────────────────────────┐
                     │     Nexus External Gateway          │
                     │  auth_handler → request_handler     │
                     └────────────────┬───────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
    ┌──────────────────┐  ┌───────────────────────┐  ┌──────────────┐
    │   Policy Hooks   │  │   Capability Router   │  │ Audit Logger │
    │ Gensui posture + │  │  Match capability     │  │ L1 + L2      │
    │ platform rules   │  │  → best agent         │  │ dual write   │
    └────────┬─────────┘  └──────────┬────────────┘  └──────────────┘
             │                       │
             │ allowed?              ▼
             │              ┌──────────────────┐
             │              │  Internal Shogun │
             │              │    Adapter        │
             │              │  (LLM execution) │
             │              └────────┬─────────┘
             │                       │
             ▼                       ▼
    ┌──────────────┐      ┌──────────────────┐
    │   BLOCKED    │      │    COMPLETED     │
    │  (response)  │      │   (result sent   │
    │              │      │    via callback)  │
    └──────────────┘      └──────────────────┘
```

### Task Lifecycle

Every external task follows a strict 7-step execution pipeline:

1. **Authenticate** — Bearer token verified against the registered agent database
2. **Normalize** — Protocol adapter (A2A/Webhook/MCP) maps the payload to a standard `NexusTask`
3. **Persist** — Task saved to database with status `pending`
4. **Policy Check** — Platform allowlists, Gensui posture, and hardcoded blocks evaluated
5. **Route** — Capability registry matches the task to the best internal Shogun/Samurai agent
6. **Execute** — Internal adapter runs the task against the matched agent's LLM
7. **Respond** — Result packaged and returned; optional callback URL notified

### Security Model

Security is non-negotiable for external connectivity. Every task passes through **four enforcement layers** before execution:

| Layer | What It Checks |
|-------|-----------------|
| 🔐 **Bearer Authentication** | Each registered agent receives a unique API token. Invalid tokens get a `401` immediately. |
| 🚫 **Hardcoded Blocks** | `desktop.execute`, `ronin.stop`, `ronin.harakiri`, and `unrestricted_browser_control` are **permanently blocked** for all external agents — no override possible. |
| 📋 **Platform Allowlists** | Per-platform rules define exactly which capabilities each platform can access. Microsoft 365 agents can summarize documents but cannot touch local files. Salesforce agents can prepare CRM updates but cannot browse freely. |
| 🎖️ **Gensui Posture** | If Gensui is active, its real-time security posture can disable all Nexus communication, block Mado browser sessions, block Ronin desktop automation, or restrict file writes — fleet-wide. |

### Default Capabilities

Shogun exposes 9 capabilities through the gateway. Custom capabilities can be registered at runtime.

| Capability | Category | Description |
|------------|----------|-------------|
| `document.summarize` | document | Summarize text or PDF files |
| `spreadsheet.analyze` | spreadsheet | Analyze Excel or CSV spreadsheets locally |
| `email.draft` | email | Draft client or internal emails |
| `file.analyze` | file | Inspect and extract data from local files |
| `browser.research` | browser | Browse the web to gather research on a topic |
| `crm.prepare_update` | crm | Draft customer relationship update instructions |
| `local_model.reasoning` | local_model | Run reasoning tasks against local models |
| `workflow.execute` | workflow | Execute sequential workflows / agent flows |
| `desktop.execute` | desktop | Execute local desktop tasks (**blocked by default**) |

### API Endpoints

All endpoints live under `/api/v1/nexus`:

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| `POST` | `/external/register-agent` | — | Register a trusted external agent, returns API token |
| `GET` | `/external/agents` | — | List all registered external agents |
| `GET` | `/capabilities` | — | Discover available Shogun capabilities |
| `POST` | `/external/a2a/task` | Bearer | Submit a task via A2A protocol |
| `GET` | `/external/task/{id}` | Bearer | Poll task status and result |
| `POST` | `/external/task/{id}/callback` | Bearer | Receive async callback updates |

### Example: A2A Task from Microsoft 365

```json
POST /api/v1/nexus/external/a2a/task
Authorization: Bearer <agent-token>

{
  "task_id": "m365-task-001",
  "action": "document.summarize",
  "input": {
    "content": "<document text or reference>"
  },
  "source_agent_id": "copilot-agent-42",
  "source_platform": "microsoft_365",
  "callback_url": "https://m365.example.com/callbacks/shogun"
}
```

Shogun processes the task, returns a result, and optionally `POST`s the result back to the `callback_url`.

### Supported Protocols

| Protocol | Status | Adapter |
|----------|--------|---------|
| **A2A** (Agent-to-Agent) | ✅ Implemented | `a2a_adapter.py` |
| **Internal Shogun** | ✅ Implemented | `internal_shogun_adapter.py` |
| **Webhook** | 🔧 Base structure | `webhook_adapter.py` |
| **MCP** (Model Context Protocol) | 🔧 Base structure | `mcp_adapter.py` |

### Audit Trail

Every gateway operation produces dual-logged audit events:

- **Layer 1 (Operational)** — Stored in the main SQLite database with 90-day retention for dashboards and debugging
- **Layer 2 (Immutable)** — Written to the HMAC-chained append-only audit database for NIS2/SOC2/EU AI Act compliance with 7-year retention

All events include: task ID, source agent, source platform, requested action, policy decision, execution result, latency, and timestamp.

---

## 🚀 Install Shogun (One Click)

**Prerequisites:** [Python 3.10+](https://www.python.org/downloads/) and [Node.js v18+](https://nodejs.org/en/download) must be installed.

Download **one file** for your platform, double-click it, and you're done:

| Platform | Download | Instructions |
|----------|----------|-------------|
| **🪟 Windows** | [⬇️ **Shogun-Install.bat**](https://github.com/AlphaHorizon-AI/Shogun/releases/latest/download/Shogun-Install.bat) | **Click to download** → Double-click the file |
| **🍎 macOS** | [⬇️ **Shogun-Install.command**](https://github.com/AlphaHorizon-AI/Shogun/releases/latest/download/Shogun-Install.command) | **Click to download** → Double-click the file |

**The installer automatically:**
- ✅ Downloads Shogun from GitHub (no git needed)
- ✅ Sets up the Python environment and installs all dependencies
- ✅ Builds the interface
- ✅ Creates a **desktop shortcut** (⚔️ Shogun — The Tenshu)
- ✅ Opens the **Setup Wizard** in your browser

### What Happens Next

1. **Your browser opens** to the Setup Wizard
2. Walk through **8 guided steps**: pick your language (14 available), name your AI agent, connect a model provider (OpenAI, Anthropic, Google, etc.), and configure governance rules
3. **Done** — you're taken to The Tenshu, your mission control dashboard
4. **Next time**, just click the ⚔️ **Shogun** shortcut on your Desktop

> 📺 **Need help?** Watch the [complete setup walkthrough on YouTube](https://www.youtube.com/@ShogunAIAgents).

---

## 🖥️ After Installation

### Launching Shogun

| Platform | How to launch |
|----------|--------------| 
| **Windows** | Double-click **"Shogun — The Tenshu"** on your Desktop |
| **macOS** | Double-click **Shogun.app** on your Desktop |
| **Linux** | Double-click **shogun.desktop** on your Desktop |

Shogun opens at **http://localhost:8000** in your default browser. *(If your OS blocks the popup, type that address manually.)*

### 🧹 Uninstalling Shogun

Open your `Shogun` installation folder and run the uninstaller:

| Platform | How to uninstall |
|----------|-----------------| 
| **Windows** | Double-click **`uninstall.bat`** |
| **macOS/Linux** | Run **`./uninstall.sh`** |

*Removes the virtual environment, databases, memories, desktop shortcut, and the folder itself.*

---

## 🏗️ The Shogun Architecture

Shogun is built around a clear hierarchy of interconnected systems:

| Module | What It Does |
|--------|-------------|
| ⚔️ **Shogun** | Your primary AI orchestrator — the central brain that coordinates everything |
| 🥷 **Samurai** | Specialized sub-agents for domain-specific tasks (research, coding, analysis) |
| 🏯 **The Tenshu** | Mission control dashboard — the React UI you interact with |
| 💬 **Comms** | Direct chat with streaming responses, chat history, email client, and calendar |
| ⚔️ **The Katana** | Model providers, API tools, routing profiles, and Telegram integration |
| 📚 **Archives** | Persistent memory with semantic search, salience scoring, and vector embeddings |
| 📜 **Kaizen** | Constitutional governance — versioned YAML rules the AI must follow |
| 🔄 **Bushido** | Self-improvement engine with scheduled reflection cycles and insight generation |
| ⛩️ **The Torii** | 5-tier security gateway with fine-grained permissions and kill switch |
| 🥋 **The Dojo** | Skills system — 4,000+ certifiable capabilities from [OpenClaw College](https://www.openclawcollege.com) |
| 🪟 **Mado** | Browser automation layer — web browsing, screenshots, content extraction via Playwright |
| 🔗 **Nexus** | Agent-to-Agent collaboration — peer-to-peer shared workspaces **and** external enterprise agent gateway (A2A, Webhook, MCP) |
| 🔄 **Agent Flow** | Visual workflow builder — drag-and-drop multi-agent pipelines |
| 🎖️ **Gensui** | Agent Fleet Management — central command for monitoring and securing fleets of Shogun agents |

---

## 🌍 14 Supported Languages

The entire interface — menus, labels, explainers, and system messages — is fully translated:

| | Language | Native Name | Code |
|---|----------|-------------|------|
| 🇬🇧 | English | English | `en` |
| 🇩🇪 | German | Deutsch | `de` |
| 🇮🇹 | Italian | Italiano | `it` |
| 🇫🇷 | French | Français | `fr` |
| 🇪🇸 | Spanish | Español | `es` |
| 🇵🇹 | Portuguese | Português | `pt` |
| 🇵🇱 | Polish | Polski | `pl` |
| 🇩🇰 | Danish | Dansk | `da` |
| 🇳🇴 | Norwegian | Norsk | `no` |
| 🇸🇪 | Swedish | Svenska | `sv` |
| 🇺🇦 | Ukrainian | Українська | `uk` |
| 🇨🇳 | Chinese | 中文 | `zh` |
| 🇯🇵 | Japanese | 日本語 | `ja` |
| 🇰🇷 | Korean | 한국어 | `ko` |

---

## 🧑‍💻 Developer Install (With Git)

<details>
<summary>Click to expand developer instructions</summary>

```bash
git clone https://github.com/AlphaHorizon-AI/Shogun.git
cd Shogun
```

| Platform | Command |
|----------|---------|
| **Windows** | Double-click `install.bat` |
| **macOS/Linux** | `chmod +x install.sh && ./install.sh` |

Or install manually:

```bash
python -m venv venv
source venv/bin/activate        # Linux / Mac
# venv\Scripts\activate         # Windows

pip install -e .
cd frontend && npm install && npm run build && cd ..
python -m shogun
```

**Endpoints:**
- **Tenshu UI**: http://localhost:8000/
- **Setup Wizard**: http://localhost:8000/setup
- **API Docs**: http://localhost:8000/docs
- **Reset Setup**: `POST /api/v1/setup/reset`

No Docker, no external services. SQLite + Qdrant embedded handles everything locally.

</details>

---

## 🔧 Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python, FastAPI, SQLAlchemy 2.0 |
| Frontend | React, TypeScript, Vite |
| Database | SQLite (default) / PostgreSQL (optional) |
| Vector Memory | Qdrant (embedded) |
| Browser Automation | Playwright |
| Email | IMAP / SMTP |
| Calendar | CalDAV |
| Validation | Pydantic v2 |
| Scheduling | APScheduler |
| Embeddings | sentence-transformers |
| Fleet Management | Gensui (independent SQLite + React UI) |
| External Gateway | Nexus A2A/Webhook/MCP protocol adapters |
| Containerization | Docker, Docker Compose, Nginx |

---

## 📺 Resources

- **[YouTube — Video Guides](https://www.youtube.com/@ShogunAIAgents)** — Full walkthrough series from install to advanced
- **[OpenClaw College](https://www.openclawcollege.com)** — AI skills marketplace
- **[GitHub Releases](https://github.com/AlphaHorizon-AI/Shogun/releases)** — Download the latest version

---

## License

[Proprietary](LICENSE.md) — [AlphaHorizon AI](https://github.com/AlphaHorizon-AI)
