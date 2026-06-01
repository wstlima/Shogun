import { useState } from 'react';
import { 
  BookOpen, 
  Terminal, 
  ShieldCheck, 
  Zap, 
  Layout, 
  Cpu, 
  Database, 
  MessageSquare, 
  FileText, 
  Search, 
  Key, 
  Download, 
  RefreshCw, 
  AlertCircle,
  Network,
  Users,
  Compass,
  Lock,
  Flame,
  Binary,
  GitBranch,
  CheckCircle2,
  Package,
  Activity,
  HardDrive,
  Globe,
  Star,
  Layers,
  Sparkles,
  Filter,
  Link2,
  FileKey,
  Shield,
  Trash2,
  AppWindow,
  Mail,
  CalendarDays,
  Play,
  ExternalLink,
  Workflow,
  Camera,
} from "lucide-react";
import { cn } from '../lib/utils';
import { useTranslation } from '../i18n';

type DocTab = 'onboarding' | 'architecture' | 'reference' | 'safety';

export function Guide() {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<DocTab>('onboarding');

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500 pb-20">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h2 className="text-4xl font-bold shogun-title flex items-center gap-4">
            {t('guide.title', 'Framework Guide')}
            <span className="text-[10px] font-normal text-shogun-subdued bg-shogun-card px-2 py-1 rounded border border-shogun-border tracking-[0.3em] uppercase">{t('guide.badge', 'Knowledge Base')}</span>
          </h2>
          <p className="text-shogun-subdued text-sm mt-1">{t('guide.subtitle', 'Master the Shogun architecture, operations, and system maintenance.')}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap items-center gap-2 p-1 bg-shogun-card border border-shogun-border rounded-xl w-fit">
        {[
          { id: 'onboarding', label: t('guide.tab_onboarding', 'Onboarding'), icon: Compass },
          { id: 'reference', label: t('guide.tab_reference', 'Reference Manual'), icon: BookOpen },
          { id: 'architecture', label: t('guide.tab_architecture', 'Architecture'), icon: Cpu },
          { id: 'safety', label: t('guide.tab_safety', 'Safety Protocols'), icon: ShieldCheck },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as DocTab)}
            className={cn(
              "flex items-center gap-2 px-6 py-2.5 rounded-lg text-xs font-bold uppercase tracking-widest transition-all",
              activeTab === tab.id 
                ? "bg-shogun-blue text-white shadow-lg" 
                : "text-shogun-subdued hover:text-shogun-text hover:bg-shogun-bg"
            )}
          >
            <tab.icon className="w-4 h-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content Rendering */}
      <div className="grid grid-cols-1 gap-8">
        
        {/* Onboarding */}
        {activeTab === 'onboarding' && (
          <div className="space-y-8 animate-in slide-in-from-bottom-4">

             {/* Welcome Hero */}
             <section className="shogun-card border-l-4 border-shogun-blue">
                <h3 className="text-xl font-bold text-shogun-text mb-4 flex items-center gap-3">
                  <Zap className="w-6 h-6 text-shogun-blue" />
                  Your Journey Begins
                </h3>
                <p className="text-shogun-subdued leading-relaxed mb-6">
                  Welcome to Shogun. You are not just running a tool; you are commanding a distributed cognitive lattice. 
                  This system is designed for high-stakes automation, deep research, and secure agent-to-agent collaboration.
                  This guide will walk you through everything you need to go from zero to fully operational.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                   <div className="p-4 bg-shogun-bg border border-shogun-border rounded-xl">
                      <div className="text-shogun-blue font-bold text-lg mb-1">1. Connect Brains</div>
                      <p className="text-xs text-shogun-subdued">Head to <strong>Katana</strong> to add your API keys or local models. This is where your AI's "intelligence" comes from.</p>
                   </div>
                   <div className="p-4 bg-shogun-bg border border-shogun-border rounded-xl">
                      <div className="text-shogun-gold font-bold text-lg mb-1">2. Train Skills</div>
                      <p className="text-xs text-shogun-subdued">Visit the <strong>Dojo</strong> to browse 4,000+ specialized skills. Certify your agents for specific task categories.</p>
                   </div>
                   <div className="p-4 bg-shogun-bg border border-shogun-border rounded-xl">
                      <div className="text-green-500 font-bold text-lg mb-1">3. Start Chatting</div>
                      <p className="text-xs text-shogun-subdued">Open <strong>Tenshu</strong> or the global chat. Your Shogun is now ready to assist, research, and execute.</p>
                   </div>
                </div>
             </section>

             {/* YouTube Video Guides */}
             <section className="shogun-card bg-red-500/[0.04] border-red-500/20 border-l-4 border-l-red-500">
                <div className="flex flex-col md:flex-row md:items-center gap-4">
                   <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 shrink-0 w-fit">
                      <Play className="w-8 h-8 text-red-500" />
                   </div>
                   <div className="space-y-2 flex-1">
                      <h3 className="text-lg font-bold text-shogun-text flex items-center gap-2">
                         Complete Video Guide
                         <span className="text-[9px] font-bold text-red-400 bg-red-500/10 px-2 py-0.5 rounded-full uppercase tracking-widest">YouTube</span>
                      </h3>
                      <p className="text-xs text-shogun-subdued leading-relaxed">
                         Prefer video? Watch the full Shogun walkthrough series — from installation to advanced workflows, agent configuration, and security setup.
                      </p>
                      <a 
                         href="https://www.youtube.com/@ShogunAIAgents" 
                         target="_blank" 
                         rel="noopener noreferrer"
                         className="inline-flex items-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white text-xs font-bold rounded-lg transition-all duration-200 shadow-lg hover:shadow-red-500/25 mt-1"
                      >
                         <Play className="w-3.5 h-3.5" />
                         Watch on YouTube
                         <ExternalLink className="w-3 h-3 opacity-60" />
                      </a>
                   </div>
                </div>
             </section>

             {/* Prerequisites */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-blue/40 pb-3">
                   <CheckCircle2 className="w-6 h-6 text-shogun-blue" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Prerequisites</h4>
                      <p className="text-xs text-shogun-subdued">What you need before you begin.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Key className="w-4 h-4 text-shogun-blue" /> At Least One API Key</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">You need an API key from at least one AI provider — OpenAI, Anthropic, Google Gemini, or Perplexity. These are obtained from the provider's developer portal. Without a key, the Shogun cannot think.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><HardDrive className="w-4 h-4 text-shogun-blue" /> Or a Local Model (Optional)</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">If you prefer to run AI entirely on your own machine (no internet required), install <strong>Ollama</strong> and pull a model like <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">llama3</code>. Shogun will auto-detect it on the Katana → Local Models tab.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Globe className="w-4 h-4 text-shogun-blue" /> A Modern Browser</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Shogun's UI is designed for modern browsers — Chrome, Edge, Firefox, or Safari. Ensure JavaScript is enabled. The interface is fully responsive and works on tablets and phones as well.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Terminal className="w-4 h-4 text-shogun-blue" /> Shogun Backend Running</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The backend server must be running on <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">localhost:8000</code>. If you installed via Docker, it starts automatically. Otherwise, run <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">python main.py</code> from the project root.</p>
                   </div>
                </div>
             </section>

             {/* Step-by-Step First Launch */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-gold/40 pb-3">
                   <Compass className="w-6 h-6 text-shogun-gold" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">First Launch — Step by Step</h4>
                      <p className="text-xs text-shogun-subdued">Follow these steps in order for the smoothest setup experience.</p>
                   </div>
                </div>
                <div className="space-y-4">
                   {[
                     { step: 1, title: 'Add Your First AI Provider', color: 'text-shogun-blue', icon: Key, desc: 'Navigate to Katana → Cloud Providers. Click "Add Provider." Choose the provider type (e.g., OpenAI), paste your API key, and save. Within seconds, all available models from that provider will appear as options throughout Shogun.' },
                     { step: 2, title: 'Select a Primary Model', color: 'text-shogun-blue', icon: Cpu, desc: 'Go to Shogun Profile → Models tab. In the "Primary Model" dropdown, select which AI brain the Shogun will use by default. This is the model that answers every question and powers every decision unless a routing rule overrides it.' },
                     { step: 3, title: 'Review Your Security Posture', color: 'text-red-400', icon: Lock, desc: 'Visit Torii (Security). The default posture is TACTICAL — a balanced setting that gives the AI enough freedom for productive work while keeping dangerous operations locked down. Read the tier descriptions and choose the level that matches your risk comfort.' },
                     { step: 4, title: 'Write Your Constitution (Optional)', color: 'text-shogun-gold', icon: FileText, desc: 'Open Kaizen → Constitution tab. This is the AI\'s "rule book." The default constitution covers essential safety rules. You can add your own rules here — for example, "Never send emails without my approval" or "Always respond in formal English." Click "Publish Edicts" when done.' },
                     { step: 5, title: 'Deploy Your First Samurai (Optional)', color: 'text-shogun-gold', icon: Users, desc: 'Head to Samurai Network. Click "Deploy Samurai," choose a role (e.g., Researcher, Analyst), give it a name, and deploy. Your first sub-agent is now ready to receive delegated tasks from the main Shogun.' },
                     { step: 6, title: 'Start a Conversation', color: 'text-green-500', icon: MessageSquare, desc: 'Click "Enter Command" on the dashboard (or navigate to Comms). Type your first message. The Shogun will respond using the primary model you selected. Congratulations — you are operational!' },
                   ].map((item) => (
                     <div key={item.step} className="shogun-card flex gap-5 items-start">
                        <div className="flex flex-col items-center gap-2 shrink-0">
                           <div className={`w-10 h-10 rounded-xl bg-shogun-bg border border-shogun-border flex items-center justify-center font-bold text-lg ${item.color}`}>
                              {item.step}
                           </div>
                        </div>
                        <div className="space-y-1 min-w-0">
                           <div className={`font-bold text-shogun-text flex items-center gap-2`}>
                              <item.icon className={`w-4 h-4 ${item.color}`} />
                              {item.title}
                           </div>
                           <p className="text-xs text-shogun-subdued leading-relaxed">{item.desc}</p>
                        </div>
                     </div>
                   ))}
                </div>
             </section>

             {/* Core Concepts Glossary */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-blue/40 pb-3">
                   <BookOpen className="w-6 h-6 text-shogun-blue" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Core Concepts</h4>
                      <p className="text-xs text-shogun-subdued">Key terms you'll encounter throughout the platform.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                   {[
                     { term: 'Shogun', def: 'The main AI agent — your primary assistant. It coordinates everything, delegates to Samurai, and answers your questions directly.', icon: Cpu, color: 'text-shogun-gold' },
                     { term: 'Samurai', def: 'Specialized sub-agents that handle specific tasks. Think of them as employees — each one has a role, a name, and a current assignment.', icon: Users, color: 'text-shogun-gold' },
                     { term: 'Lattice', def: 'The network of all connected agents (Shogun + Samurai). The lattice distributes work intelligently and ensures no single agent is overwhelmed.', icon: Network, color: 'text-shogun-blue' },
                     { term: 'Constitution', def: 'A set of inviolable rules written in YAML that govern what all agents are allowed to do. Managed in the Kaizen page.', icon: FileText, color: 'text-shogun-gold' },
                     { term: 'Security Posture', def: 'A tiered system (SHRINE → RONIN) controlling how much autonomy and access agents have. Managed in Torii.', icon: Lock, color: 'text-red-400' },
                     { term: 'Harakiri', def: 'The emergency kill switch. Instantly freezes all agent activity and locks the system to maximum security (SHRINE).', icon: ShieldCheck, color: 'text-red-400' },
                     { term: 'Routing Profile', def: 'A set of rules that decides which AI model handles which type of task. For example: code → GPT-4, research → Perplexity.', icon: GitBranch, color: 'text-shogun-blue' },
                     { term: 'Salience', def: 'A memory importance score (0.0–1.0). High-salience memories are retrieved first. The system auto-adjusts salience over time.', icon: Star, color: 'text-shogun-gold' },
                     { term: 'Reflection Cycle', def: 'An automated self-improvement loop where the AI analyzes its own performance and generates optimization insights. Run from Bushido.', icon: RefreshCw, color: 'text-shogun-blue' },
                   ].map((item) => (
                     <div key={item.term} className="shogun-card space-y-2">
                        <div className={`font-bold text-shogun-text flex items-center gap-2`}>
                           <item.icon className={`w-4 h-4 ${item.color}`} />
                           {item.term}
                        </div>
                        <p className="text-xs text-shogun-subdued leading-relaxed">{item.def}</p>
                     </div>
                   ))}
                </div>
             </section>

             {/* Navigation Map */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-gold/40 pb-3">
                   <Layout className="w-6 h-6 text-shogun-gold" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Navigation Map</h4>
                      <p className="text-xs text-shogun-subdued">Every page in Shogun at a glance — what it does and when to use it.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   {[
                     { name: 'Tenshu (Dashboard)', purpose: 'Your home screen. See stat cards, active agents, recent events, quick actions, and the Harakiri button. The first thing you see when you open Shogun.', icon: Layout, color: 'text-shogun-blue' },
                     { name: 'Comms (Chat)', purpose: 'Talk directly to your Shogun. Send questions or commands. Responses stream in real time. View chat history and restore old sessions. Also includes an integrated email client and calendar.', icon: MessageSquare, color: 'text-shogun-blue' },
                     { name: 'Shogun Profile', purpose: 'Configure your AI\'s identity — name, personality, primary model, fallback models, behavioral directives, permissions, and scheduled jobs.', icon: Cpu, color: 'text-shogun-gold' },
                     { name: 'Samurai Network', purpose: 'Deploy and manage specialized sub-agents. Each Samurai has a role, routing profile, and spawn policy. Monitor their tasks and status.', icon: Users, color: 'text-shogun-gold' },
                     { name: 'Katana (System Forge)', purpose: 'Plug in AI providers (cloud or local), create routing profiles, manage tools, and configure Telegram integration.', icon: Cpu, color: 'text-shogun-blue' },
                     { name: 'Archives (Memory)', purpose: 'Search, browse, create, and manage the AI\'s memories. Supports semantic search, salience pinning, and memory type filtering.', icon: Database, color: 'text-shogun-gold' },
                     { name: 'Dojo (Training Hall)', purpose: 'Browse 4,000+ skills from the OpenClaw College. Study training material, take certification exams, and track achievements.', icon: Flame, color: 'text-shogun-gold' },
                     { name: 'Kaizen (Governance)', purpose: 'Write the Constitution (YAML rules) and the Mandate (Markdown mission statement). Manage revision history and audit trails.', icon: ShieldCheck, color: 'text-shogun-gold' },
                     { name: 'Bushido (Reflection)', purpose: 'Calibrate self-improvement behavior. Tune reflection intensity, consolidation rate, and exploration variance. View AI-generated insights.', icon: RefreshCw, color: 'text-shogun-blue' },
                     { name: 'Torii (Security)', purpose: 'Set the system\'s security posture (5 tiers from SHRINE to RONIN). Create and manage security policies. Access the Harakiri kill switch.', icon: Lock, color: 'text-red-400' },
                     { name: 'Mado (Browser)', purpose: 'Browser automation layer powered by Playwright. Your AI can navigate to URLs, extract page content, take screenshots, and interact with web pages — all controlled through the secure Torii permission system.', icon: AppWindow, color: 'text-cyan-400' },
                     { name: 'Agent Flow (Workflows)', purpose: 'Visual drag-and-drop workflow builder. Design multi-step AI pipelines by chaining Input, Samurai, Shogun Approval, Logic Gate, Browser, and Output nodes. Execute complex orchestration flows.', icon: Workflow, color: 'text-violet-400' },
                     { name: 'Mail (Email Client)', purpose: 'Full IMAP/SMTP email integration. Browse your inbox, read and compose emails, reply with CC/BCC, navigate folders. Your Shogun can also read, send, and manage emails via native skills.', icon: Mail, color: 'text-sky-400' },
                     { name: 'Calendar', purpose: 'CalDAV calendar integration. View upcoming events, create new ones (with time, location, and description), and manage your schedule. Your Shogun can query and create events via native skills.', icon: CalendarDays, color: 'text-emerald-400' },
                     { name: 'Nexus (Collaboration)', purpose: 'Create Joint Workspaces. Invite other Shogun instances over the network. Exchange typed messages and co-edit a shared whiteboard.', icon: Globe, color: 'text-indigo-400' },
                     { name: 'Backups & Data', purpose: 'Scheduled and manual backups with configurable retention. Export/import your entire database. Manage backup settings and restore from any point.', icon: HardDrive, color: 'text-shogun-gold' },
                     { name: 'Updates', purpose: 'Auto-checks for new Shogun versions every 6 hours. One-click install to download and apply updates. Preserves your data, configs, and environment.', icon: Download, color: 'text-emerald-400' },
                     { name: 'Logs (Compliance Dashboard)', purpose: 'NIS2, SOC2, and EU AI Act-compliant event stream. Filter by 11 categories (Decision, Oversight, Risk, Model, Policy, Memory, Tools, Auth, Incident, System). Click trace IDs for full workflow reconstruction. Audit chain verifies tamper-proof integrity.', icon: Terminal, color: 'text-shogun-subdued' },
                   ].map((item) => (
                     <div key={item.name} className="shogun-card flex gap-4 items-start">
                        <div className={`p-2 rounded-lg bg-shogun-bg border border-shogun-border shrink-0`}>
                           <item.icon className={`w-5 h-5 ${item.color}`} />
                        </div>
                        <div className="space-y-1 min-w-0">
                           <div className="font-bold text-shogun-text text-sm">{item.name}</div>
                           <p className="text-xs text-shogun-subdued leading-relaxed">{item.purpose}</p>
                        </div>
                     </div>
                   ))}
                </div>
             </section>

             {/* Tips & Best Practices */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-green-500/40 pb-3">
                   <Sparkles className="w-6 h-6 text-green-500" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Tips & Best Practices</h4>
                      <p className="text-xs text-shogun-subdued">Recommendations from experienced operators.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2 border-l-2 border-green-500/40">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-green-500" /> Start with TACTICAL Posture</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The default "TACTICAL" security tier is recommended for most users. It gives the AI enough autonomy to be useful while keeping dangerous operations (like shell access and auto-spawning) locked down. Only move to CAMPAIGN or RONIN when you fully understand the risks.</p>
                   </div>
                   <div className="shogun-card space-y-2 border-l-2 border-green-500/40">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Database className="w-4 h-4 text-green-500" /> Add Fallback Models</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Don't rely on a single AI provider. In Shogun Profile → Models, add at least one fallback model from a different provider. If your primary (e.g., OpenAI) goes down, the system automatically switches to the next available brain.</p>
                   </div>
                   <div className="shogun-card space-y-2 border-l-2 border-green-500/40">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Star className="w-4 h-4 text-green-500" /> Pin Important Memories</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">If there's a fact the AI must never forget — a company policy, a key contact, a critical instruction — create it as a memory in Archives and pin it. Pinned memories always have maximum salience and are always loaded into context.</p>
                   </div>
                   <div className="shogun-card space-y-2 border-l-2 border-green-500/40">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Download className="w-4 h-4 text-green-500" /> Enable Automatic Backups</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Your Shogun accumulates valuable knowledge over time. Go to <strong>Backups</strong> in the sidebar → enable automatic backups on a schedule. You can also manually export a "Safe JSON Bundle" from the Data Management tab. This protects you from data loss due to hardware failure.</p>
                   </div>
                   <div className="shogun-card space-y-2 border-l-2 border-green-500/40">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><FileText className="w-4 h-4 text-green-500" /> Write a Clear Mandate</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The Mandate (Kaizen → Mandate tab) is injected into every conversation. Use it to set the AI's overall purpose, tone, and special instructions. For example: "You are a senior financial analyst. Always cite sources. Respond in English."</p>
                   </div>
                   <div className="shogun-card space-y-2 border-l-2 border-green-500/40">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Activity className="w-4 h-4 text-green-500" /> Monitor the Compliance Dashboard</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Check the Logs page regularly — it records every action with full NIS2/SOC2/EU AI Act provenance. Use the <strong>Decision</strong> tab to track AI reasoning influences. Click trace IDs to reconstruct full workflows. Verify the <strong>"Chain Intact"</strong> badge stays green — a broken chain indicates tampering. Export the audit log periodically for off-site compliance archival.</p>
                   </div>
                </div>
             </section>

          </div>
        )}

        {/* Reference Manual (Comprehensive Function List) */}
        {activeTab === 'reference' && (
          <div className="space-y-16 animate-in slide-in-from-bottom-4">
             {/* Introduction */}
             <div className="text-center max-w-3xl mx-auto space-y-4">
                <h3 className="text-3xl font-bold shogun-title">The Grand Reference</h3>
                <p className="text-shogun-subdued leading-relaxed">A deep-dive, page-by-page, tab-by-tab, button-by-button manual of every single capability within the Shogun platform. Written in plain language so anyone can understand it — no technical jargon required.</p>
             </div>

             {/* ═══════════════════════════════════════════════════════════════ */}
             {/* 1. TENSHU (DASHBOARD) */}
             {/* ═══════════════════════════════════════════════════════════════ */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-blue/40 pb-3">
                   <Layout className="w-6 h-6 text-shogun-blue" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Tenshu — The Command Center</h4>
                      <p className="text-xs text-shogun-subdued">Your home screen. The first thing you see when you open Shogun.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Activity className="w-4 h-4 text-shogun-blue" /> Stat Cards (Top Row)</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Four large cards at the top of the page. Each one is a "quick look" at a different part of the system. They are clickable — clicking one takes you to the related page.</p>
                      <ul className="text-xs text-shogun-subdued space-y-1 ml-4 list-disc">
                         <li><strong>Neural Engine:</strong> Shows the name of your primary AI and whether it is currently running. Click to go to the Shogun Profile page.</li>
                         <li><strong>Active Lattice:</strong> How many sub-agents (Samurai) are currently deployed. Click to go to the Samurai Network page.</li>
                         <li><strong>Knowledge Volume:</strong> The total number of memories stored in the Archives. Also indicates whether the search index is healthy or has errors.</li>
                         <li><strong>Security Tier:</strong> Shows your current protection level (e.g., "GUARDED" or "TACTICAL"). Click to go to Torii.</li>
                      </ul>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Users className="w-4 h-4 text-shogun-blue" /> Active Deployment Registry</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">A table below the stat cards that lists every Samurai (sub-agent) currently running. For each one you can see:</p>
                      <ul className="text-xs text-shogun-subdued space-y-1 ml-4 list-disc">
                         <li><strong>Designation:</strong> The agent's name and its first-letter icon.</li>
                         <li><strong>Current Task:</strong> What the agent is working on right now.</li>
                         <li><strong>Engagement Bar:</strong> A progress bar showing how busy it is.</li>
                         <li><strong>Status:</strong> A green "active" or blue "suspended" badge.</li>
                      </ul>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Zap className="w-4 h-4 text-shogun-blue" /> Quick Actions Panel</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Two large shortcut buttons below the deployment registry:</p>
                      <ul className="text-xs text-shogun-subdued space-y-1 ml-4 list-disc">
                         <li><strong>New Samurai:</strong> Opens the Samurai Network page to deploy a new sub-agent.</li>
                         <li><strong>Model Setup:</strong> Opens the Katana page to configure AI models.</li>
                      </ul>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-red-400" /> Emergency Stop (Harakiri)</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">A red button on the dashboard. Pressing it opens a two-step confirmation modal. Once confirmed, <strong>all active agent operations are immediately stopped</strong>. The security posture locks to "SHRINE" (maximum protection). A pulsing red banner appears at the top of Every page until you press "Reset Harakiri".</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Activity className="w-4 h-4 text-shogun-gold" /> Telemetry Feed (Right Sidebar)</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">A timeline of recent system events displayed on the right side. Each event has a colored icon (red for security, gold for agent, blue for system) and a timestamp. At the bottom, a "System Load" bar shows current CPU usage.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><MessageSquare className="w-4 h-4 text-shogun-blue" /> "Enter Command" Button</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The blue button in the top right. Clicking it takes you straight to the Comms (Chat) page where you can start talking to your Shogun.</p>
                   </div>
                </div>
             </section>

             {/* ═══════════════════════════════════════════════════════════════ */}
             {/* 2. COMMS (CHAT) */}
             {/* ═══════════════════════════════════════════════════════════════ */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-blue/40 pb-3">
                   <MessageSquare className="w-6 h-6 text-shogun-blue" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Comms — The Conversation</h4>
                      <p className="text-xs text-shogun-subdued">Your direct line to the Shogun AI. Type a question or command and get a response.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><MessageSquare className="w-4 h-4 text-shogun-blue" /> Chat Window</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The main area showing your conversation. Your messages appear on the right (blue icon), and the Shogun's replies appear on the left (gold icon). While the AI is thinking, three bouncing dots are shown. Responses stream in token by token so you can watch the answer being written in real time.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Globe className="w-4 h-4 text-shogun-blue" /> Model & Search Tags</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Below each Shogun reply you will see a small tag. If the reply used a <strong>Web Search</strong> (via Perplexity), a blue "Web Search" badge appears. Otherwise, the name of the AI model used is shown (e.g., "gpt-4o").</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Search className="w-4 h-4 text-shogun-gold" /> Input Bar & Sending</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Type your message at the bottom and press <strong>Enter</strong> (or click the blue send arrow) to send. While the AI is responding, the input field is locked and shows "Transmitting directive..." to prevent double-sending.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Compass className="w-4 h-4 text-shogun-gold" /> Session History</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Below the input bar, click <strong>"View History"</strong> to open a right-hand drawer showing all your previous chat sessions. Each session shows a preview of the first message and the number of messages. Click <strong>"Restore"</strong> to reload an old conversation. Click <strong>"Clear All History"</strong> at the bottom to permanently erase all archived sessions.</p>
                   </div>
                   <div className="shogun-card space-y-2 md:col-span-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Activity className="w-4 h-4 text-red-400" /> Clear Button (Trash Icon)</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The trash icon in the top right <strong>archives</strong> the current session to history and starts a fresh conversation. Your old messages are not lost — they are kept in the History drawer and can be restored at any time.</p>
                   </div>
                </div>

                {/* Comms Sub-sections: Agent Flow, Mail, Calendar */}
                <div className="mt-8 space-y-4">
                   <div className="text-xs font-bold text-shogun-subdued uppercase tracking-widest pl-1 border-l-2 border-shogun-blue/40 ml-1">Also available from Comms</div>
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="shogun-card space-y-2 border-l-2 border-violet-400/40">
                         <div className="font-bold text-shogun-text flex items-center gap-2"><Workflow className="w-4 h-4 text-violet-400" /> Agent Flow — Workflow Builder</div>
                         <p className="text-xs text-shogun-subdued leading-relaxed">A visual drag-and-drop canvas for designing multi-step AI pipelines. Build workflows by chaining six node types: <strong>Input</strong> (entry point), <strong>Samurai</strong> (sub-agent delegation), <strong>Shogun Approval</strong> (human confirmation gate), <strong>Logic</strong> (conditional routing), <strong>Mado Browser</strong> (web automation), and <strong>Output</strong> (final result). Connect nodes with directed edges to define execution order. Workflows are saved to the database and can be loaded, edited, or executed at any time. You can also ask the Shogun to build workflows for you via the <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">create_agent_flow</code> native skill.</p>
                      </div>
                      <div className="shogun-card space-y-2 border-l-2 border-sky-400/40">
                         <div className="font-bold text-shogun-text flex items-center gap-2"><Mail className="w-4 h-4 text-sky-400" /> Mail — Email Client</div>
                         <p className="text-xs text-shogun-subdued leading-relaxed">A full IMAP/SMTP email client built into Comms. Browse your inbox with sender, subject, date, and preview. Click any message to read the full content. <strong>Compose</strong> new emails with To, CC, BCC, subject, and body. Reply to existing messages with quoted context. Navigate between folders (Inbox, Sent, Drafts). Configure your email account in the system settings. The Shogun can also manage email via native skills: <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">fetch_inbox</code>, <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">read_email</code>, <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">send_email</code>.</p>
                      </div>
                      <div className="shogun-card space-y-2 border-l-2 border-emerald-400/40 md:col-span-2">
                         <div className="font-bold text-shogun-text flex items-center gap-2"><CalendarDays className="w-4 h-4 text-emerald-400" /> Calendar — Event Management</div>
                         <p className="text-xs text-shogun-subdued leading-relaxed">CalDAV calendar integration. View your upcoming events on a timeline with titles, times, locations, and descriptions. Create new events by specifying a title, start/end time, location, and optional description. Supports all-day events. Connect a CalDAV server in the system settings. The Shogun can query and create events via native skills: <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">list_calendar_events</code>, <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">create_calendar_event</code>.</p>
                      </div>
                   </div>
                </div>
             </section>

             {/* ═══════════════════════════════════════════════════════════════ */}
             {/* 3. SHOGUN PROFILE */}
             {/* ═══════════════════════════════════════════════════════════════ */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-gold/40 pb-3">
                   <Cpu className="w-6 h-6 text-shogun-gold" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Shogun Profile — Your AI's Identity</h4>
                      <p className="text-xs text-shogun-subdued">Configure the personality, intelligence, and behavior of your main Shogun agent. Has 5 tabs.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Cpu className="w-4 h-4 text-shogun-gold" /> General Tab</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Set the Shogun's name, choose an active "Persona" (a pre-built personality template), and write a description. On the right side, adjust the <strong>Autonomy Level</strong> slider (how much freedom the AI gets), <strong>Tone</strong> (e.g., Analytical, Direct), <strong>Risk Tolerance</strong>, <strong>Verbosity</strong> (how detailed responses are), <strong>Planning Depth</strong>, <strong>Tool Usage</strong>, <strong>Security Bias</strong>, and <strong>Memory Style</strong>. Click the avatar image to upload a custom picture.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Database className="w-4 h-4 text-shogun-gold" /> Models Tab</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Choose exactly which AI brain the Shogun uses. Has two cards: <strong>Primary Model</strong> (the main brain used for every request) — select from a dropdown grouped by provider. <strong>Fallback Models</strong> — add backup brains in priority order. If the primary is unavailable, these are tried in order. Drag to reorder priorities. Also has a <strong>Routing Strategy</strong> dropdown to choose a routing profile.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><FileText className="w-4 h-4 text-shogun-gold" /> Behavior Tab</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">A full-screen YAML text editor showing the Shogun's core behavioral directives — its priorities, operational constraints, and delegation rules. Think of this as the AI's "rule book." You can edit it directly, and the badge in the top-right confirms it is in "YAML Mode."</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Lock className="w-4 h-4 text-shogun-gold" /> Permissions Tab</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Displays the security rules inherited from the current Security Policy. Shows a <strong>Risk Score</strong> meter (0–100, where higher = more dangerous). Every permission category (Filesystem, Network, Shell, Skills, Subagents, Memory) is listed with plain-English tooltips explaining what each setting does. You can toggle individual settings to customize rules beyond the base policy.</p>
                   </div>
                   <div className="shogun-card space-y-2 md:col-span-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><RefreshCw className="w-4 h-4 text-shogun-gold" /> Operations Tab</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">View and manage scheduled background jobs. Preset jobs include <strong>Memory Consolidation</strong> (summarizes and compresses old memories), <strong>Knowledge Refresh</strong> (updates outdated knowledge), and <strong>Security Audit</strong>. Each can be enabled/disabled with a toggle. Below the presets, you can <strong>create custom jobs</strong> with a name, schedule (nightly, weekly, monthly, or one-time), priority, and instructions.</p>
                   </div>
                </div>
             </section>

             {/* ═══════════════════════════════════════════════════════════════ */}
             {/* 4. SAMURAI NETWORK */}
             {/* ═══════════════════════════════════════════════════════════════ */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-gold/40 pb-3">
                   <Users className="w-6 h-6 text-shogun-gold" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Samurai Network — The Fleet</h4>
                      <p className="text-xs text-shogun-subdued">Deploy, manage, and monitor specialized sub-agents.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Users className="w-4 h-4 text-shogun-gold" /> Fleet Stats (Top)</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Four stat cards: <strong>Total Fleet</strong> (all agents), <strong>Active</strong> (currently working), <strong>Suspended</strong> (paused), and <strong>Signal Range</strong> (network reach).</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Search className="w-4 h-4 text-shogun-gold" /> Agent Table & Search</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">A large table listing every Samurai. Use the search bar to filter by name. Each row shows: the agent's <strong>name and role badge</strong>, <strong>status</strong> (green dot = active), <strong>current task</strong> (with a live progress bar if running), <strong>role/slug</strong>, <strong>routing profile</strong>, and <strong>deployment date</strong>. Hover over a row to reveal action buttons.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Zap className="w-4 h-4 text-shogun-gold" /> Row Action Buttons</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Three buttons appear when you hover over a Samurai row:</p>
                      <ul className="text-xs text-shogun-subdued space-y-1 ml-4 list-disc">
                         <li><strong>Pause/Play:</strong> Suspend a running agent or resume a suspended one.</li>
                         <li><strong>Trash:</strong> Permanently delete the agent (asks for confirmation first).</li>
                         <li><strong>Configure (⋮):</strong> Opens a modal where you can change the agent's name, role, routing profile, spawn policy, and description.</li>
                      </ul>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Package className="w-4 h-4 text-shogun-blue" /> "Deploy Samurai" Button</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The blue button in the top right. Opens a form where you choose a <strong>Role</strong> from the pre-defined Samurai roles list, give it a <strong>custom name</strong>, choose a <strong>Spawn Policy</strong> (Manual, Auto, or Scheduled), optionally assign a <strong>Routing Profile</strong>, and write a description. Click "Deploy Samurai" to create it.</p>
                   </div>
                </div>
             </section>

             {/* ═══════════════════════════════════════════════════════════════ */}
             {/* 5. KATANA (THE FORGE) */}
             {/* ═══════════════════════════════════════════════════════════════ */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-blue/40 pb-3">
                   <Cpu className="w-6 h-6 text-shogun-blue" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Katana — The System Forge</h4>
                      <p className="text-xs text-shogun-subdued">Where you plug in AI "brains", connect tools, and set up routing rules. Has 4 tabs.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Key className="w-4 h-4 text-shogun-blue" /> Cloud Providers Tab</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Lists every cloud AI service you have connected (OpenAI, Anthropic, Google Gemini, Perplexity, etc.). Each provider card shows its <strong>name</strong>, <strong>type</strong>, <strong>status</strong> (active/disabled), and which <strong>models</strong> it provides. You can <strong>add a new provider</strong> by clicking the button, entering a name, selecting the type, pasting your API key, and optionally listing specific model names. Each card has <strong>Edit</strong> and <strong>Delete</strong> buttons.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><HardDrive className="w-4 h-4 text-shogun-blue" /> Local Models Tab</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">For AI models running on your own computer (via Ollama). Shows a list of <strong>discovered models</strong> on your machine, each with its size and format. You can <strong>pull new models</strong> from the Ollama library with a real-time download progress bar showing speed and percentage.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Binary className="w-4 h-4 text-shogun-blue" /> Routing Profiles Tab</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Create "routing profiles" — sets of rules that decide which AI model handles which type of task. For example, you can create a "Balanced" profile where: code tasks go to GPT-4, research tasks go to Perplexity Sonar, and simple chat goes to a cheap model. Each profile has a <strong>name</strong>, optional <strong>default model</strong>, and a list of <strong>rules</strong> (task type → model pair). Profiles can be set as the system default.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Network className="w-4 h-4 text-shogun-blue" /> Toolbox Tab</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Lists all the external tools the Shogun can use — web search, file access, database connections, code execution, etc. Each tool shows its <strong>name</strong>, <strong>type</strong>, and <strong>status</strong> (enabled/disabled). You can <strong>register new tools</strong> and toggle existing ones on or off.</p>
                   </div>
                   <div className="shogun-card space-y-2 md:col-span-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Globe className="w-4 h-4 text-shogun-blue" /> Telegram Integration</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">At the bottom of the Katana page. Paste a Telegram Bot Token (obtained from @BotFather) and click "Connect" to let your Shogun send and receive messages via Telegram. This allows you to talk to your AI from your phone while away from your computer. The status indicator shows whether the bot is currently running.</p>
                   </div>
                </div>
             </section>

             {/* ═══════════════════════════════════════════════════════════════ */}
             {/* 6. ARCHIVES (MEMORY) */}
             {/* ═══════════════════════════════════════════════════════════════ */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-gold/40 pb-3">
                   <Database className="w-6 h-6 text-shogun-gold" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Archives — The Memory Vault</h4>
                      <p className="text-xs text-shogun-subdued">Everything the Shogun has ever learned, remembered, or been told.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Search className="w-4 h-4 text-shogun-gold" /> Semantic Search Bar</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Type a question or topic and the system finds matching memories using AI-powered "meaning" search — not just keyword matching. For example, searching "customer complaints" can also return memories about "user feedback" or "product issues." Results are ranked by relevance.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Layers className="w-4 h-4 text-shogun-gold" /> Memory Types</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Memories are categorized into types:</p>
                      <ul className="text-xs text-shogun-subdued space-y-1 ml-4 list-disc">
                         <li><strong>Semantic:</strong> Facts and knowledge (e.g., "The capital of France is Paris").</li>
                         <li><strong>Episodic:</strong> Experiences and events (e.g., "User asked about pricing on April 15").</li>
                         <li><strong>Procedural:</strong> How-to instructions and workflows.</li>
                      </ul>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Star className="w-4 h-4 text-shogun-gold" /> Salience Score</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Each memory has a "salience" score (0.0 to 1.0) that represents how important it is. High-salience memories are prioritized when the AI retrieves context. The system automatically adjusts salience over time — frequently used memories rise, rarely used ones fade. You can manually <strong>pin</strong> a memory to lock its salience at maximum.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Sparkles className="w-4 h-4 text-shogun-gold" /> Inscribe Memory (+ Button)</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Click the "+" button to manually add a new memory. You choose the <strong>type</strong> (semantic, episodic, etc.), write the <strong>content</strong>, and optionally set the <strong>salience</strong>. This is useful for injecting facts, rules, or context that the AI should always know about.</p>
                   </div>
                   <div className="shogun-card space-y-2 md:col-span-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Activity className="w-4 h-4 text-shogun-gold" /> Memory Cards</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Each memory is shown as a card with: the content text, memory type badge, salience bar, creation date, and action buttons. You can <strong>delete</strong> individual memories via the trash icon. The total count and an "Export" option are available in the header.</p>
                   </div>
                </div>
             </section>

             {/* ═══════════════════════════════════════════════════════════════ */}
             {/* 7. DOJO (TRAINING HALL) */}
             {/* ═══════════════════════════════════════════════════════════════ */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-gold/40 pb-3">
                   <Flame className="w-6 h-6 text-shogun-gold" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Dojo — The Training Hall</h4>
                      <p className="text-xs text-shogun-subdued">Browse, study, and certify your agents on 4,000+ skills. Has 4 tabs.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Search className="w-4 h-4 text-shogun-gold" /> Catalog Tab</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The default tab. Shows every available skill from the OpenClaw College database. Each skill shows its <strong>name</strong>, <strong>risk tier</strong> (Low, Medium, High, Critical), and faculty category. A sidebar shows faculty categories in a collapsible tree — click a category to filter skills. Use the search bar to find specific skills by name. Click any skill to see its full training literature.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Package className="w-4 h-4 text-shogun-gold" /> Bundles Tab</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Skills grouped into themed bundles (e.g., "Web Security Fundamentals," "Data Analysis Pack"). Each bundle card shows the bundle name, number of skills included, average difficulty, and a description. Click a bundle to expand it and see all the skills it contains.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Layers className="w-4 h-4 text-shogun-gold" /> Specializations Tab</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Higher-level groupings that combine multiple bundles into a career-path style progression. Think of these as "majors" — completing a specialization means your agent is deeply trained in an entire domain.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-shogun-gold" /> Achieved Tab</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Shows all the certifications your agents have already passed. Each entry shows the skill name, exam score, pass/fail status, and date achieved. This is your "trophy room" — proof that your AI has been tested and verified on specific capabilities.</p>
                   </div>
                   <div className="shogun-card space-y-2 md:col-span-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><FileText className="w-4 h-4 text-shogun-gold" /> Skill Detail & Exams</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">When you click on any individual skill, you see its full detail pane: the training literature (textbooks and reference material), the risk tier, and a <strong>"Take Exam"</strong> button. Exams are 30–50 multiple-choice questions. The AI agent answers them automatically. A passing score certifies the agent on that skill and appears in the "Achieved" tab.</p>
                   </div>
                </div>
             </section>

             {/* ═══════════════════════════════════════════════════════════════ */}
             {/* 8. KAIZEN (GOVERNANCE) */}
             {/* ═══════════════════════════════════════════════════════════════ */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-blue/40 pb-3">
                   <ShieldCheck className="w-6 h-6 text-shogun-gold" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Kaizen — The Constitutional Layer</h4>
                      <p className="text-xs text-shogun-subdued">Define the fundamental laws and ethical boundaries for all agents. Has 2 tabs.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><FileText className="w-4 h-4 text-shogun-gold" /> Constitution Tab</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">A full-screen YAML code editor where you write the "Constitution" — the AI's core laws. The system validates the YAML in real time (green dot = correct syntax, red = error with details). On the right sidebar, <strong>Active Principles</strong> are extracted from the YAML and shown as colored cards: red (Critical), orange (High), gold (Balanced), blue (Medium), green (Low). Click <strong>"Publish Edicts"</strong> to save your changes — a new revision is created automatically.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><FileText className="w-4 h-4 text-shogun-gold" /> The Mandate Tab</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">A Markdown editor for writing the Shogun's "Mission Statement." This is a free-form document defining objectives and operating principles. Use the <strong>Edit/Preview</strong> toggle to switch between writing mode and rendered mode. Key sections of this document are automatically injected into the AI's system prompt on every interaction, so if you write "Always respond in Danish" here, the AI will obey.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><RefreshCw className="w-4 h-4 text-shogun-gold" /> Revision History</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">On the right sidebar (both tabs). Shows a timeline of every saved version of the Constitution or Mandate. Each entry shows the version number, change summary, and date. The most recent version is highlighted.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Download className="w-4 h-4 text-shogun-gold" /> Download Audit Log</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">At the bottom of the sidebar. Downloads a JSON file containing the full audit history of all governance changes. Useful for compliance or reviewing what rules were changed and when.</p>
                   </div>
                </div>
             </section>

             {/* ═══════════════════════════════════════════════════════════════ */}
             {/* 9. BUSHIDO (REFLECTION ENGINE) */}
             {/* ═══════════════════════════════════════════════════════════════ */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-blue/40 pb-3">
                   <RefreshCw className="w-6 h-6 text-shogun-blue" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Bushido — The Reflection Engine</h4>
                      <p className="text-xs text-shogun-subdued">Automated self-improvement cycles where the AI analyzes its own performance.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Activity className="w-4 h-4 text-shogun-blue" /> Calibration Controls</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Three dials that control the Shogun's self-improvement behavior: <strong>Reflection Frequency</strong> (how often the system thinks about its own performance), <strong>Consolidation Threshold</strong> (when to compress old memories), and <strong>Exploration Budget</strong> (how willing the system is to try new approaches). Each has a slider and a plain-English description.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Sparkles className="w-4 h-4 text-shogun-blue" /> Insight Stream</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">A live feed of AI-generated suggestions. The system autonomously analyzes its own behavior and posts insights like "Model X is 2x faster for code tasks" or "Memory #412 hasn't been used in 30 days — consider archiving." Each insight has a severity badge and a timestamp.</p>
                   </div>
                   <div className="shogun-card space-y-2 md:col-span-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><RefreshCw className="w-4 h-4 text-shogun-blue" /> Reflection Trigger</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">A button to manually trigger a reflection cycle. The system will analyze recent interactions, evaluate model performance, check memory health, and produce a set of actionable insights. Results appear in the Insight Stream.</p>
                   </div>
                </div>
             </section>

             {/* ═══════════════════════════════════════════════════════════════ */}
             {/* 10. TORII (SECURITY) */}
             {/* ═══════════════════════════════════════════════════════════════ */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-red-400/40 pb-3">
                   <Lock className="w-6 h-6 text-red-400" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Torii — Security Portal</h4>
                      <p className="text-xs text-shogun-subdued">Control exactly what your agents are allowed to do, access, and reach.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-red-400" /> Security Posture (Left Column)</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Five clickable tiers, from safest to most dangerous:</p>
                      <ul className="text-xs text-shogun-subdued space-y-1 ml-4 list-disc">
                         <li><strong>SHRINE (MAX):</strong> Zero-trust. Local only. No external tools. Maximum safety.</li>
                         <li><strong>GUARDED:</strong> Restricted network. Only approved tools. Everything needs human approval.</li>
                         <li><strong>TACTICAL (DEFAULT):</strong> Balanced autonomy. The AI has scoped file access and can use approved tools on its own.</li>
                         <li><strong>CAMPAIGN:</strong> High autonomy. Broad internet access. Agents can auto-spawn without asking.</li>
                         <li><strong>RONIN (UNSAFE):</strong> Unrestricted. Only use in completely isolated test environments.</li>
                      </ul>
                      <p className="text-xs text-shogun-subdued leading-relaxed mt-2">Click a tier to switch. Below the tiers, a <strong>Current Constraints</strong> card shows exactly what the active tier allows (Filesystem mode, Network mode, Shell access, etc.).</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Lock className="w-4 h-4 text-red-400" /> Policy Registry (Right Column)</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">A list of all security policies defined in the system. Each policy card shows the name, tier badge, permission block count, and whether the kill-switch is enabled. Hover over a policy to reveal buttons:</p>
                      <ul className="text-xs text-shogun-subdued space-y-1 ml-4 list-disc">
                         <li><strong>Eye icon:</strong> Opens a full-screen modal showing every detail of the policy — all permission blocks as JSON.</li>
                         <li><strong>Copy icon:</strong> Exports the policy as JSON to your clipboard.</li>
                         <li><strong>Trash icon:</strong> Deletes the policy (only for user-created policies; built-in ones cannot be deleted).</li>
                      </ul>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-red-400" /> Create Tactical Policy</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Click "Create Tactical Policy" at the bottom of the registry. A form appears where you enter a <strong>name</strong>, choose a <strong>security tier</strong>, write a <strong>description</strong>, and toggle whether the <strong>kill-switch</strong> and <strong>dry-run</strong> are supported. Click "Save Policy" to create it.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-red-500" /> Harakiri Button</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The red button in the top right of the Torii page. Same as the one on the Dashboard — activates the global kill switch. Requires two-step confirmation. Once active, all agents are frozen and the posture locks to SHRINE. Press "Reset Harakiri" to restore normal operation.</p>
                   </div>
                </div>
             </section>

             {/* ═══════════════════════════════════════════════════════════════ */}
             {/* 11. NEXUS (COLLABORATION) */}
             {/* ═══════════════════════════════════════════════════════════════ */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-indigo-400/40 pb-3">
                   <Users className="w-6 h-6 text-indigo-400" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Nexus — The Alliance</h4>
                      <p className="text-xs text-shogun-subdued">Inter-agent collaboration. Work with other Shogun instances across the network.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Key className="w-4 h-4 text-indigo-400" /> Identity Card (Top)</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Displays your Shogun's unique ID and public key. Other Shogun instances need this to verify your messages are authentic. Click the copy icon to put your agent ID on the clipboard for sharing.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><GitBranch className="w-4 h-4 text-indigo-400" /> Workspace List (Left Column)</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">A list of all Joint Workspaces you have created or joined. Each card shows the workspace name, topic, and number of peer agents connected. Click a workspace to open it. Hover over a card to see the <strong>delete button</strong> (red X in the corner). Deleting a workspace permanently removes it and all its messages.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Package className="w-4 h-4 text-indigo-400" /> "Create Workspace" Button</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Opens a form where you enter a <strong>name</strong>, <strong>description</strong>, and <strong>topic</strong> for the new workspace. After creation, you can invite other Shogun agents by providing their network URL.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Users className="w-4 h-4 text-indigo-400" /> Invite Peers</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Inside a workspace detail view, click <strong>"Invite Peer"</strong>. Enter the <strong>endpoint URL</strong> of the other Shogun (e.g., http://192.168.1.50:8000) and optionally a display name. The system will contact the remote agent, exchange identity information, and add it to the workspace.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><MessageSquare className="w-4 h-4 text-indigo-400" /> A2A Message Thread</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Inside a workspace, the right panel shows all messages exchanged between agents. Messages can be typed in the compose box at the bottom. Choose a <strong>message type</strong> from the dropdown: "update" for status reports, "proposal" for suggestions, "approval" for sign-offs, or "task" for actionable assignments. Messages are automatically signed with your agent's identity.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><FileText className="w-4 h-4 text-indigo-400" /> Shared Whiteboard</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Below the message thread, a full-width text editor where all agents in the workspace can collaboratively write plans, code, or reports. Click <strong>"Edit"</strong> to enter editing mode, make your changes, then click <strong>"Save"</strong> to publish them to all connected peers.</p>
                   </div>
                </div>
             </section>

             {/* ═══════════════════════════════════════════════════════════════ */}
             {/* 12. LOGS (AUDIT TRAIL) */}
             {/* ═══════════════════════════════════════════════════════════════ */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-subdued/40 pb-3">
                   <Terminal className="w-6 h-6 text-shogun-subdued" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Logs — The Compliance Dashboard</h4>
                      <p className="text-xs text-shogun-subdued">NIS2, SOC2, and EU AI Act-compliant event logging with full trace reconstruction and tamper-proof audit chain.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2 md:col-span-2 border-l-2 border-shogun-blue/40">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Layers className="w-4 h-4 text-shogun-blue" /> Dual-Layer Architecture</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Every event is written to <strong>two independent stores</strong>: (1) an <strong>operational SQLite log</strong> (fast, searchable, 90-day retention) for day-to-day monitoring, and (2) a <strong>tamper-resistant HMAC-chained audit database</strong> (append-only, 7-year retention) for regulatory evidence. If anyone modifies or deletes an entry in the audit chain, the cryptographic hash chain breaks — and the dashboard flags it immediately.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Activity className="w-4 h-4 text-shogun-subdued" /> Event Stream</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The main panel shows every event in chronological order. Each row displays: <strong>timestamp</strong>, <strong>category icon</strong>, <strong>severity badge</strong> (info/warn/error/critical), <strong>result status</strong> (green check for success, red X for denied), the <strong>action description</strong>, <strong>event type tag</strong> (e.g., DECISION.CONTEXT), the <strong>model used</strong>, <strong>tool invoked</strong>, and <strong>trace ID link</strong>. Click any event to expand its detail panel. Toggle between <strong>Live</strong> (auto-refresh every 5 seconds) and <strong>Paused</strong> modes.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Filter className="w-4 h-4 text-shogun-subdued" /> Category Tabs</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Eleven filterable categories across the top, each with a real-time event count badge:</p>
                      <ul className="text-xs text-shogun-subdued space-y-1 ml-4 list-disc">
                         <li><strong>Decision:</strong> AI decision provenance — context assembled, influences tracked (EU AI Act). Events: <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">decision.context</code>, <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">decision.influences</code>.</li>
                         <li><strong>Oversight:</strong> Human review — AI responses delivered for implicit oversight, emergency shutdowns. Events: <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">oversight.response_delivered</code>, <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">oversight.emergency_shutdown</code>.</li>
                         <li><strong>Risk:</strong> Security tier warnings, denied tools, high-autonomy alerts. Events: <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">risk.tools_denied</code>, <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">risk.high_autonomy_mode</code>.</li>
                         <li><strong>Model:</strong> Model selection, LLM responses, API errors, fallback activations. Events: <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">model.selected</code>, <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">model.response</code>, <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">model.error</code>.</li>
                         <li><strong>Policy:</strong> Torii policy evaluations — tools granted or denied with reasons. Events: <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">policy.evaluated</code>.</li>
                         <li><strong>Memory:</strong> Memory recall, search queries, write operations with retrieval provenance. Events: <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">memory.search</code>, <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">memory.write</code>.</li>
                         <li><strong>Tools:</strong> Tool/skill executions, arguments, and results. Events: <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">tool.executed</code>.</li>
                         <li><strong>Auth:</strong> Session tracking, security posture changes, API credential lifecycle, kill switch activations. Events: <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">auth.session</code>, <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">auth.posture_changed</code>, <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">auth.credential_added</code>, <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">auth.kill_switch_activated</code>.</li>
                         <li><strong>Incident:</strong> Critical security events — model API failures, kill switch emergency actions, audit chain integrity violations. Events: <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">incident.model_api_error</code>, <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">incident.kill_switch</code>, <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">incident.chain_broken</code>.</li>
                         <li><strong>System:</strong> Server lifecycle (startup/shutdown), governance configuration changes (Constitution/Mandate), backup and restore provenance. Events: <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">system.startup</code>, <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">system.shutdown</code>, <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">system.config_changed</code>, <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">system.backup_created</code>, <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">system.backup_restored</code>.</li>
                      </ul>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Link2 className="w-4 h-4 text-shogun-blue" /> Trace Reconstruction</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Every chat turn generates a <strong>trace_id</strong> (e.g., <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">trc_d5ae40fb</code>) that links all events in that workflow — from policy evaluation through memory recall, model selection, tool execution, and decision provenance. Click any trace ID link to open the <strong>Trace Reconstruction modal</strong>, which displays every event in the chain as a numbered timeline. This allows full <strong>workflow reconstruction</strong> for incident investigation.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><FileKey className="w-4 h-4 text-shogun-gold" /> Event Detail Panel</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Click any event to expand a detail panel showing the full NIS2/SOC2 + EU AI Act record:</p>
                      <ul className="text-xs text-shogun-subdued space-y-1 ml-4 list-disc">
                         <li><strong>WHO/WHAT/WHEN:</strong> User ID, agent, event type, timestamp.</li>
                         <li><strong>MODEL/PROVIDER:</strong> Which AI model and cloud provider handled the request.</li>
                         <li><strong>POLICY:</strong> Security policy reference, decision (allowed/denied), and reason.</li>
                         <li><strong>RISK/TRACE:</strong> Risk score and correlated trace ID.</li>
                         <li><strong>AI Confidence bar:</strong> Color-coded indicator (green ≥ 70%, yellow 40–70%, red &lt; 40%).</li>
                         <li><strong>Framework badges:</strong> Shows which compliance frameworks apply (SOC2, NIS2, EU_AI_ACT).</li>
                         <li><strong>Governance flags:</strong> Human oversight required, evidence completeness, risk level.</li>
                         <li><strong>Detail payload:</strong> Full structured JSON of all event metadata.</li>
                      </ul>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Shield className="w-4 h-4 text-green-500" /> Audit Chain Integrity</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The top-right corner shows a real-time <strong>Chain Intact</strong> indicator (green) or <strong>Chain Broken</strong> alert (red, pulsing). This verifies the HMAC-SHA256 hash chain across all immutable audit records. If the chain is intact, no records have been tampered with. The status bar at the bottom also shows "AUDIT: INTACT" or "BROKEN."</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Download className="w-4 h-4 text-shogun-gold" /> Compliance Export</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Click the download icon to export the <strong>immutable audit log</strong> as a JSON file. This export pulls from the tamper-proof chain (not the operational log), making it suitable for regulatory auditors, compliance reviews, and incident investigations. The export includes all event metadata, governance flags, and chain hashes.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Trash2 className="w-4 h-4 text-red-400" /> Clear Operational Logs</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Click the trash icon to clear the <strong>operational log only</strong>. The immutable audit chain is <strong>never affected</strong> by this action — it is append-only and cannot be cleared. A confirmation dialog warns you before deletion. The clearing event itself is recorded in the immutable audit chain as evidence.</p>
                   </div>
                </div>
             </section>

             {/* 13. MAINTENANCE — BACKUPS, DATA & UPDATES */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-subdued/40 pb-3">
                   <HardDrive className="w-6 h-6 text-shogun-subdued" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Maintenance — Backups, Data & Updates</h4>
                      <p className="text-xs text-shogun-subdued">Found under the <strong>Maintenance</strong> section at the bottom of the sidebar.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2 border-l-2 border-shogun-gold/40">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Activity className="w-4 h-4 text-shogun-gold" /> Scheduled Backups</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Navigate to <strong>Backups</strong> in the sidebar. Enable automatic backups with a configurable schedule (hourly to weekly). Set how many old backups to keep — older ones are automatically deleted. Backups include your database, configs, governance documents, and environment settings.</p>
                   </div>
                   <div className="shogun-card space-y-2 border-l-2 border-shogun-blue/40">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Database className="w-4 h-4 text-shogun-blue" /> Data Management Tab</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">On the <strong>Backups</strong> page, switch to the <strong>Data Management</strong> tab. Here you'll find a live System Snapshot (row counts per table, DB size), one-click export as a <strong>Safe JSON Bundle</strong> or <strong>Raw Database Swap</strong>, and an Import area to restore from a previous export.</p>
                   </div>
                   <div className="shogun-card space-y-2 border-l-2 border-emerald-500/40">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Download className="w-4 h-4 text-emerald-400" /> System Updates</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Navigate to <strong>Updates</strong> in the sidebar. The system automatically checks for new versions every 6 hours. When an update is available, a green <strong>NEW</strong> badge appears on the sidebar. Click <strong>Install Update</strong> to download, extract, and rebuild — your data, configs, and environment are always preserved.</p>
                   </div>
                   <div className="shogun-card space-y-2 border-l-2 border-amber-500/40">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><FileText className="w-4 h-4 text-amber-400" /> Restore & Recovery</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Every backup in the list has a <strong>Restore</strong> button. Clicking it overwrites your current database and config files with the backup's contents. A restart is required afterwards. Use this to roll back after a bad config change, recover from corruption, or migrate to a new machine.</p>
                   </div>
                </div>
             </section>

             {/* ═══════════════════════════════════════════════════════════════ */}
             {/* 14. MADO (BROWSER AUTOMATION) */}
             {/* ═══════════════════════════════════════════════════════════════ */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-cyan-400/40 pb-3">
                   <AppWindow className="w-6 h-6 text-cyan-400" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Mado — The Browser Layer</h4>
                      <p className="text-xs text-shogun-subdued">Secure browser automation. Your AI can browse the web, extract content, and take screenshots.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Globe className="w-4 h-4 text-cyan-400" /> Browse Web</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The Shogun can navigate to any URL using the <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">browse_web</code> native skill. It loads the full page via Playwright (a real browser engine), then extracts the content as readable text or raw HTML. You can optionally pass a CSS selector to target a specific element on the page.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Camera className="w-4 h-4 text-cyan-400" /> Screenshots</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">After navigating to a page, the Shogun can take a screenshot using <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">take_screenshot</code>. Choose between viewport-only or full-page capture. Screenshots are saved locally and can be used in mission reports or sent via Telegram.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Lock className="w-4 h-4 text-cyan-400" /> Security Integration</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Mado respects the Torii security posture. Browser automation must be explicitly enabled in the agent's permission set. In <strong>SHRINE</strong> and <strong>GUARDED</strong> tiers, Mado is disabled entirely. In <strong>TACTICAL</strong> and above, it can be toggled on per-policy. This prevents the AI from browsing the web without explicit operator authorization.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Activity className="w-4 h-4 text-cyan-400" /> Session Management</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Browser sessions are managed automatically. When Shogun shuts down, all active Playwright browser instances are cleanly closed. The Mado page in the sidebar shows the current session status and lets you manually manage active browser contexts.</p>
                   </div>
                </div>
             </section>

             {/* ═══════════════════════════════════════════════════════════════ */}
             {/* 15. AGENT FLOW (WORKFLOW BUILDER) */}
             {/* ═══════════════════════════════════════════════════════════════ */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-violet-400/40 pb-3">
                   <Workflow className="w-6 h-6 text-violet-400" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Agent Flow — The Workflow Builder</h4>
                      <p className="text-xs text-shogun-subdued">Design and execute multi-step AI pipelines with a visual drag-and-drop canvas.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Layers className="w-4 h-4 text-violet-400" /> Node Types</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Build workflows using six node types:</p>
                      <ul className="text-xs text-shogun-subdued space-y-1 ml-4 list-disc">
                         <li><strong>Input:</strong> The entry point — accepts user text, data, or triggers.</li>
                         <li><strong>Samurai:</strong> Delegates a task to a specific sub-agent with a configurable task description.</li>
                         <li><strong>Shogun Approval:</strong> Pauses the flow and requires human confirmation before proceeding.</li>
                         <li><strong>Logic:</strong> A conditional gate — routes the flow based on a condition expression.</li>
                         <li><strong>Mado Browser:</strong> Automates a web browsing action (navigate, extract, screenshot).</li>
                         <li><strong>Output:</strong> The final result node — collects and presents the workflow's output.</li>
                      </ul>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><GitBranch className="w-4 h-4 text-violet-400" /> Canvas & Connections</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The visual canvas lets you position nodes freely and draw directed edges between them. Edges define the execution order — data flows from source to target. You can label edges for clarity. The canvas supports pan, zoom, and node reordering. Workflows are saved to the database and can be loaded, edited, or deleted at any time.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Zap className="w-4 h-4 text-violet-400" /> AI-Assisted Creation</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">You can also ask the Shogun to <strong>build workflows for you</strong> via the chat. The native skill <code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">create_agent_flow</code> lets the AI generate complete workflows with nodes and edges programmatically. Just describe what you want and the Shogun will create it.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><RefreshCw className="w-4 h-4 text-violet-400" /> Execution</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Once a workflow is designed, click <strong>Execute</strong> to run it. The system processes nodes in topological order, passing outputs from one node as inputs to the next. Shogun Approval nodes pause execution until you confirm. Failed nodes show error details inline.</p>
                   </div>
                </div>
             </section>

             {/* ═══════════════════════════════════════════════════════════════ */}
             {/* 16. COMMS EXTENDED — MAIL & CALENDAR */}
             {/* ═══════════════════════════════════════════════════════════════ */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-sky-400/40 pb-3">
                   <Mail className="w-6 h-6 text-sky-400" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Comms Extended — Mail & Calendar</h4>
                      <p className="text-xs text-shogun-subdued">Integrated email client and calendar. Manage your inbox and schedule directly from Shogun.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Mail className="w-4 h-4 text-sky-400" /> Email Inbox</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Connect your IMAP/SMTP email account in the system settings. Once connected, the <strong>Mail View</strong> page shows your inbox with sender, subject, date, and a body preview for each message. Click any message to read the full content. Navigate between folders (Inbox, Sent, Drafts, etc.) using the sidebar.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><FileText className="w-4 h-4 text-sky-400" /> Compose & Reply</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Click <strong>Compose</strong> to write a new email. Fill in the recipient (To), subject, and body. Optionally add CC and BCC recipients. The email is sent via your configured SMTP account. You can also reply to existing messages — the original message is quoted in the body for context.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><CalendarDays className="w-4 h-4 text-emerald-400" /> Calendar View</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Connect a CalDAV calendar server to view your events. The <strong>Calendar</strong> page shows events on a timeline with titles, times, locations, and descriptions. Create new events by specifying a title, start/end time, location, and optional description. Supports all-day events.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Sparkles className="w-4 h-4 text-sky-400" /> AI-Powered Email & Calendar</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Your Shogun has full access to your email and calendar via native skills. It can:</p>
                      <ul className="text-xs text-shogun-subdued space-y-1 ml-4 list-disc">
                         <li><strong>fetch_inbox:</strong> Check your inbox and list messages with previews.</li>
                         <li><strong>read_email:</strong> Read the full content of a specific message by UID.</li>
                         <li><strong>send_email:</strong> Compose and send an email on your behalf.</li>
                         <li><strong>list_calendar_events:</strong> Query upcoming events within a date range.</li>
                         <li><strong>create_calendar_event:</strong> Create new calendar events with full details.</li>
                      </ul>
                      <p className="text-xs text-shogun-subdued leading-relaxed mt-2">This means you can say "Check my inbox" or "Schedule a meeting for tomorrow at 2pm" in the chat, and the Shogun will handle it.</p>
                   </div>
                </div>
             </section>

          </div>
        )}

        {/* Architecture */}
        {activeTab === 'architecture' && (
          <div className="space-y-16 animate-in slide-in-from-bottom-4">

             {/* Introduction */}
             <div className="text-center max-w-3xl mx-auto space-y-4">
                <h3 className="text-3xl font-bold shogun-title">System Architecture</h3>
                <p className="text-shogun-subdued leading-relaxed">A deep-dive into how Shogun is built — the layers, protocols, and subsystems that make it work. Understanding the architecture helps you make better decisions about configuration, security, and scaling.</p>
             </div>

             {/* 1. High-Level Overview */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-blue/40 pb-3">
                   <Layers className="w-6 h-6 text-shogun-blue" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">System Topology</h4>
                      <p className="text-xs text-shogun-subdued">The big picture — how all the pieces fit together.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Layout className="w-4 h-4 text-shogun-blue" /> Three-Tier Design</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Shogun is built in three tiers: <strong>Presentation</strong> (the React-based UI you're looking at), <strong>Application</strong> (a FastAPI backend handling all business logic, routing, and orchestration), and <strong>Persistence</strong> (SQLite for structured data, Qdrant for vector memory). Each tier is independent and communicates via REST APIs.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Network className="w-4 h-4 text-shogun-blue" /> Lattice Architecture</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Instead of one monolithic AI, Shogun uses a "Lattice" — a network of specialized sub-agents (Samurai) coordinated by a central Shogun agent. Work is distributed across the lattice based on agent roles and routing profiles. This makes the system resilient, parallelizable, and scalable.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Globe className="w-4 h-4 text-shogun-blue" /> External Integrations</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The system connects outward to cloud AI providers (OpenAI, Anthropic, Gemini, Perplexity, OpenRouter) and local model servers (Ollama). It integrates with Telegram for mobile messaging, supports the A2A (Agent-to-Agent) protocol for cross-network collaboration via Nexus, automates web browsing via Mado (Playwright), connects to email servers (IMAP/SMTP), and syncs with calendar servers (CalDAV).</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Cpu className="w-4 h-4 text-shogun-blue" /> Single-Server Deployment</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The entire Shogun stack runs on a single machine. The backend serves on port 8000, the frontend is a Vite-powered React SPA proxied or served separately, and SQLite/Qdrant run locally. No cloud infrastructure is required — everything stays on your hardware.</p>
                   </div>
                </div>
             </section>

             {/* 2. Agent Hierarchy */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-gold/40 pb-3">
                   <Users className="w-6 h-6 text-shogun-gold" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Agent Hierarchy</h4>
                      <p className="text-xs text-shogun-subdued">How intelligence is distributed across the network.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                   <div className="shogun-card space-y-3 border-t-2 border-shogun-gold">
                      <div className="font-bold text-shogun-gold text-lg flex items-center gap-2"><Cpu className="w-5 h-5" /> The Shogun</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The central coordinator. Receives user queries, decides how to respond, and can delegate sub-tasks to Samurai agents. Has its own personality, behavioral directives, and primary model. Think of the Shogun as the CEO — it makes strategic decisions and assigns work.</p>
                      <div className="text-[9px] text-shogun-subdued uppercase font-bold tracking-widest bg-shogun-bg p-2 rounded border border-shogun-border">Configured in: Shogun Profile</div>
                   </div>
                   <div className="shogun-card space-y-3 border-t-2 border-shogun-blue">
                      <div className="font-bold text-shogun-blue text-lg flex items-center gap-2"><Users className="w-5 h-5" /> Samurai Agents</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Specialized sub-agents, each with a defined role (Researcher, Analyst, Developer, etc.). Samurai can run independently or be orchestrated by the Shogun. Each has its own routing profile, spawn policy, and task queue. Think of them as department heads — experts in their domain.</p>
                      <div className="text-[9px] text-shogun-subdued uppercase font-bold tracking-widest bg-shogun-bg p-2 rounded border border-shogun-border">Managed in: Samurai Network</div>
                   </div>
                   <div className="shogun-card space-y-3 border-t-2 border-indigo-400">
                      <div className="font-bold text-indigo-400 text-lg flex items-center gap-2"><Globe className="w-5 h-5" /> Peer Shoguns</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Other Shogun instances running on different machines. Connected via the Nexus collaboration module using the A2A Protocol. Peers exchange messages, share whiteboard content, and can coordinate on complex multi-agent tasks across network boundaries.</p>
                      <div className="text-[9px] text-shogun-subdued uppercase font-bold tracking-widest bg-shogun-bg p-2 rounded border border-shogun-border">Connected via: Nexus</div>
                   </div>
                </div>
             </section>

             {/* 3. Memory Tier */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-gold/40 pb-3">
                   <Database className="w-6 h-6 text-shogun-gold" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">The Memory Tier</h4>
                      <p className="text-xs text-shogun-subdued">How the system stores, retrieves, and manages knowledge.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Search className="w-4 h-4 text-shogun-gold" /> Vector Memory (Qdrant)</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Memories are converted into numerical vectors (embeddings) and stored in a Qdrant vector database. This enables <strong>semantic search</strong> — you can search by meaning, not just keywords. When the AI responds to a query, it automatically retrieves the most relevant memories from this layer and includes them in context.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Database className="w-4 h-4 text-shogun-gold" /> Structured Storage (SQLite)</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">All configuration data — agents, providers, routing profiles, governance documents, chat history, certifications, security policies — is stored in a local SQLite database (<code className="bg-shogun-bg px-1 py-0.5 rounded text-shogun-text">shogun.db</code>). This is the "source of truth" for everything except vector embeddings.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Layers className="w-4 h-4 text-shogun-gold" /> Memory Types</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Memories are categorized into three types: <strong>Semantic</strong> (facts and knowledge), <strong>Episodic</strong> (events and experiences), and <strong>Procedural</strong> (instructions and workflows). Each type has different retrieval priorities and consolidation rules. The type influences how aggressively the memory fades over time.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Star className="w-4 h-4 text-shogun-gold" /> Salience & Decay</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Every memory has a salience score (0.0–1.0). Frequently accessed memories rise in salience; unused ones decay naturally. The Bushido reflection engine periodically reviews memories and consolidates low-salience ones. You can <strong>pin</strong> critical memories to prevent decay entirely.</p>
                   </div>
                </div>
             </section>

             {/* 4. Communication Protocol */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-blue/40 pb-3">
                   <MessageSquare className="w-6 h-6 text-shogun-blue" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Communication Protocol</h4>
                      <p className="text-xs text-shogun-subdued">How agents talk to each other and to you.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><MessageSquare className="w-4 h-4 text-shogun-blue" /> User → Shogun (REST + SSE)</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">When you type a message in Comms, it is sent as an HTTP POST to the backend. The response is streamed back via <strong>Server-Sent Events (SSE)</strong> — the tokens appear one at a time in real-time. This is what creates the "typing" effect you see as the AI responds.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Users className="w-4 h-4 text-shogun-blue" /> Shogun → Samurai (Internal Dispatch)</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The Shogun delegates tasks to Samurai agents via an internal dispatch queue. Each delegation includes the task description, priority level, and context from the conversation. The Samurai processes the task independently and reports results back.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Globe className="w-4 h-4 text-indigo-400" /> Shogun → Peers (A2A Protocol)</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Inter-Shogun communication uses the <strong>Agent-to-Agent (A2A)</strong> protocol over HTTP. Messages are typed (update, proposal, approval, task) and cryptographically signed with the sender's identity keys. Each peer validates signatures before accepting messages.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Zap className="w-4 h-4 text-shogun-blue" /> Shogun → AI Providers (LLM Calls)</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The routing engine selects a model based on the active routing profile (or uses the default primary model). The request is sent to the chosen provider's API (OpenAI, Anthropic, etc.) with the assembled prompt (user message + system prompt + memory context + constitution). Streaming responses are relayed back to the frontend.</p>
                   </div>
                </div>
             </section>

             {/* 5. Security Layer */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-red-400/40 pb-3">
                   <Lock className="w-6 h-6 text-red-400" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Security Layer</h4>
                      <p className="text-xs text-shogun-subdued">Defense-in-depth architecture that protects every agent action.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-red-400" /> Tiered Posture System</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Five security tiers (SHRINE → GUARDED → TACTICAL → CAMPAIGN → RONIN) control what agents can access. Each tier defines permissions for filesystem, network, shell, tools, and sub-agent spawning. The active tier applies globally to all agents. Managed in Torii.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><FileText className="w-4 h-4 text-red-400" /> Kaizen Constitution Validator</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Every proposed agent action is validated against the Constitution (written in Kaizen). If an action violates any constitutional rule, it is blocked before execution. The validation happens server-side, so agents cannot bypass it. Rules are evaluated by priority (critical rules are checked first).</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><AlertCircle className="w-4 h-4 text-red-400" /> Harakiri Kill Switch</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">A global emergency mechanism. When activated, <strong>all</strong> agent activity is instantly frozen, the posture locks to SHRINE (maximum protection), and a prominent red banner appears system-wide. Requires a two-step confirmation to activate and a deliberate reset to restore normal operations.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Key className="w-4 h-4 text-red-400" /> Identity & Signing</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Each Shogun instance has a unique ID and cryptographic key pair. All A2A messages are signed, ensuring peers can verify authenticity. API keys for external providers are stored encrypted in the database and never exposed in the frontend.</p>
                   </div>
                </div>
             </section>

             {/* 6. Intelligence Pipeline */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-blue/40 pb-3">
                   <Cpu className="w-6 h-6 text-shogun-blue" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Intelligence Pipeline</h4>
                      <p className="text-xs text-shogun-subdued">The journey of a message from input to output.</p>
                   </div>
                </div>
                <div className="space-y-4">
                   {[
                     { step: 1, title: 'User Input', desc: 'You type a message in the Comms chat interface. The message is sent to the backend via HTTP POST.', color: 'text-shogun-blue', icon: MessageSquare },
                     { step: 2, title: 'Routing Decision', desc: 'The routing engine checks the active routing profile for matching task rules. If a rule matches (e.g., "research" → Perplexity), that model is used. Otherwise, the primary model is selected.', color: 'text-shogun-blue', icon: GitBranch },
                     { step: 3, title: 'Context Assembly', desc: 'The system assembles the full prompt: system instructions + Mandate (from Kaizen) + relevant memories (from Archives, via semantic search) + current conversation history + constitutional rules.', color: 'text-shogun-gold', icon: Layers },
                     { step: 4, title: 'Security Validation', desc: 'The assembled request is checked against the active security posture and constitutional rules. If any violations are found, the request is blocked or modified.', color: 'text-red-400', icon: ShieldCheck },
                     { step: 5, title: 'LLM Invocation', desc: 'The validated prompt is sent to the selected AI model\'s API. The response streams back token-by-token via SSE.', color: 'text-shogun-blue', icon: Cpu },
                     { step: 6, title: 'Memory Inscription', desc: 'After the response completes, key information from the exchange may be automatically stored as new memories in the Archives, increasing the AI\'s knowledge for future queries.', color: 'text-shogun-gold', icon: Database },
                   ].map((item) => (
                     <div key={item.step} className="shogun-card flex gap-5 items-start">
                        <div className="flex flex-col items-center gap-2 shrink-0">
                           <div className={`w-10 h-10 rounded-xl bg-shogun-bg border border-shogun-border flex items-center justify-center font-bold text-lg ${item.color}`}>
                              {item.step}
                           </div>
                        </div>
                        <div className="space-y-1 min-w-0">
                           <div className="font-bold text-shogun-text flex items-center gap-2">
                              <item.icon className={`w-4 h-4 ${item.color}`} />
                              {item.title}
                           </div>
                           <p className="text-xs text-shogun-subdued leading-relaxed">{item.desc}</p>
                        </div>
                     </div>
                   ))}
                </div>
             </section>

             {/* 7. Self-Improvement Loop */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-gold/40 pb-3">
                   <RefreshCw className="w-6 h-6 text-shogun-gold" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Self-Improvement Loop (Bushido)</h4>
                      <p className="text-xs text-shogun-subdued">How the system continuously optimizes itself.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Activity className="w-4 h-4 text-shogun-gold" /> Reflection Cycles</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The Bushido engine periodically analyzes recent interactions to evaluate model performance, memory utilization, and agent effectiveness. It looks for patterns — which models are faster, which memories are frequently retrieved, which agents are underperforming — and generates actionable insights.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Binary className="w-4 h-4 text-shogun-gold" /> Memory Consolidation</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Low-salience episodic memories are periodically transformed into compact semantic summaries. This prevents the memory store from growing indefinitely while preserving the knowledge within. The consolidation rate is configurable via the Bushido calibration controls.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Compass className="w-4 h-4 text-shogun-gold" /> Exploration vs. Exploitation</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The "Exploration Variance" parameter controls how much the system deviates from proven strategies. Low variance means the AI sticks to what works; high variance means it experiments with new approaches. This is the classic explore-exploit tradeoff, tunable in Bushido.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-shogun-gold" /> Formal Verification</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">All behavioral optimizations proposed by the Bushido engine are verified against the Kaizen constitution before being applied. This ensures that self-improvement never violates the fundamental laws defined by the operator. The system cannot "optimize its way" past your rules.</p>
                   </div>
                </div>
             </section>

          </div>
        )}

        {/* Safety Protocols */}
        {activeTab === 'safety' && (
          <div className="space-y-16 animate-in slide-in-from-bottom-4">

             {/* Introduction */}
             <div className="text-center max-w-3xl mx-auto space-y-4">
                <h3 className="text-3xl font-bold shogun-title">Safety & Security Protocols</h3>
                <p className="text-shogun-subdued leading-relaxed">Shogun is built with a defense-in-depth security model. Multiple independent layers work together to ensure that no single failure can compromise the system. This page explains every safety mechanism in detail.</p>
             </div>

             {/* 1. Security Philosophy */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-red-400/40 pb-3">
                   <ShieldCheck className="w-6 h-6 text-red-400" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Security Philosophy</h4>
                      <p className="text-xs text-shogun-subdued">The principles that govern every safety decision in Shogun.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                   <div className="shogun-card space-y-2 border-t-2 border-red-400">
                      <div className="font-bold text-shogun-text text-lg">Defense in Depth</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">No single layer is trusted alone. Security is enforced at the posture level (Torii), the constitutional level (Kaizen), the permission level (Shogun Profile), and the runtime level (action validation). An attacker would need to bypass all four layers simultaneously.</p>
                   </div>
                   <div className="shogun-card space-y-2 border-t-2 border-orange-400">
                      <div className="font-bold text-shogun-text text-lg">Least Privilege</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Agents are given only the minimum permissions they need to complete their tasks. By default, agents cannot access the filesystem, execute shell commands, or spawn sub-agents unless explicitly granted by the active security posture and individual permission overrides.</p>
                   </div>
                   <div className="shogun-card space-y-2 border-t-2 border-shogun-gold">
                      <div className="font-bold text-shogun-text text-lg">Fail Closed</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">When in doubt, the system blocks rather than allows. If a constitutional rule is ambiguous, the action is denied. If the security posture cannot be verified, the system defaults to SHRINE (maximum protection). The Harakiri kill switch ensures instant lockdown in emergencies.</p>
                   </div>
                </div>
             </section>

             {/* 2. Security Tiers */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-red-400/40 pb-3">
                   <Lock className="w-6 h-6 text-red-400" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">The Five Security Tiers</h4>
                      <p className="text-xs text-shogun-subdued">Each tier represents a different balance between safety and autonomy. Choose based on your environment and risk tolerance.</p>
                   </div>
                </div>
                <div className="space-y-4">
                   {[
                     { tier: 'SHRINE', subtitle: 'Maximum Protection', color: 'border-green-500 bg-green-500/5', badge: 'text-green-500 bg-green-500/10 border-green-500/30', desc: 'Zero-trust mode. All external connections are blocked. Agents can only process information locally with no filesystem, network, or shell access. No sub-agent spawning. Every action requires explicit human approval. Use this when you suspect a breach, while auditing, or when running highly sensitive operations.', perms: ['Filesystem: None', 'Network: None (local only)', 'Shell: Blocked', 'Sub-agents: Blocked', 'Tools: Disabled', 'Human approval: Required for everything'] },
                     { tier: 'GUARDED', subtitle: 'Restricted Operations', color: 'border-blue-500 bg-blue-500/5', badge: 'text-blue-500 bg-blue-500/10 border-blue-500/30', desc: 'Highly restricted. Limited read-only filesystem access. Network restricted to approved endpoints only. All tool usage requires human confirmation. Sub-agents can exist but cannot auto-spawn. Suitable for production environments where safety takes priority over speed.', perms: ['Filesystem: Read-only (scoped)', 'Network: Approved endpoints only', 'Shell: Blocked', 'Sub-agents: Manual spawn only', 'Tools: With approval', 'Human approval: Most actions'] },
                     { tier: 'TACTICAL', subtitle: 'Balanced (Default)', color: 'border-shogun-gold bg-shogun-gold/5', badge: 'text-shogun-gold bg-shogun-gold/10 border-shogun-gold/30', desc: 'The recommended default. Agents have scoped file access (read and write within designated directories), can use approved tools autonomously, and have filtered network access. Shell commands are still blocked. Sub-agents can be spawned manually. A good balance between productivity and safety.', perms: ['Filesystem: Scoped read/write', 'Network: Filtered (no raw sockets)', 'Shell: Blocked', 'Sub-agents: Manual spawn', 'Tools: Approved tools auto-allowed', 'Human approval: Dangerous actions only'] },
                     { tier: 'CAMPAIGN', subtitle: 'High Autonomy', color: 'border-orange-500 bg-orange-500/5', badge: 'text-orange-500 bg-orange-500/10 border-orange-500/30', desc: 'Extended autonomy for advanced users. Broad filesystem access. Full internet access. Shell commands allowed with logging. Sub-agents can auto-spawn based on policies. Only use this in controlled environments where you have monitoring in place and trust the AI models you are running.', perms: ['Filesystem: Broad access', 'Network: Full internet', 'Shell: Allowed (logged)', 'Sub-agents: Auto-spawn enabled', 'Tools: All enabled', 'Human approval: Critical actions only'] },
                     { tier: 'RONIN', subtitle: '⚠ Unrestricted', color: 'border-red-500 bg-red-500/5', badge: 'text-red-500 bg-red-500/10 border-red-500/30', desc: 'No restrictions whatsoever. Full filesystem, network, shell, and tool access with zero oversight. ONLY use this in completely isolated sandbox/test environments with no access to production data, external services, or sensitive information. This tier exists for testing and development purposes only.', perms: ['Filesystem: Unrestricted', 'Network: Unrestricted', 'Shell: Unrestricted', 'Sub-agents: Unrestricted', 'Tools: All enabled', 'Human approval: None'] },
                   ].map((item) => (
                     <div key={item.tier} className={`shogun-card border-l-4 ${item.color}`}>
                        <div className="flex flex-col md:flex-row md:items-start gap-4">
                           <div className="md:w-1/3 space-y-2">
                              <div className="flex items-center gap-3">
                                 <span className={`text-xs font-bold uppercase px-2 py-1 rounded border ${item.badge}`}>{item.tier}</span>
                                 <span className="text-sm font-bold text-shogun-text">{item.subtitle}</span>
                              </div>
                              <p className="text-xs text-shogun-subdued leading-relaxed">{item.desc}</p>
                           </div>
                           <div className="md:w-2/3 grid grid-cols-2 md:grid-cols-3 gap-2">
                              {item.perms.map((perm, i) => {
                                const [label, value] = perm.split(': ');
                                return (
                                  <div key={i} className="bg-shogun-bg border border-shogun-border rounded-lg p-2">
                                     <div className="text-[9px] text-shogun-subdued uppercase font-bold tracking-widest">{label}</div>
                                     <div className="text-[10px] text-shogun-text font-bold mt-0.5">{value}</div>
                                  </div>
                                );
                              })}
                           </div>
                        </div>
                     </div>
                   ))}
                </div>
             </section>

             {/* 3. Constitutional Guardrails */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-gold/40 pb-3">
                   <FileText className="w-6 h-6 text-shogun-gold" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Constitutional Guardrails</h4>
                      <p className="text-xs text-shogun-subdued">The AI's inviolable laws — written by you, enforced by the system.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><FileText className="w-4 h-4 text-shogun-gold" /> How It Works</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The Constitution is a YAML document written in the Kaizen page. Each rule has a <strong>name</strong>, <strong>description</strong>, <strong>priority level</strong> (critical, high, balanced, medium, low), and <strong>enforcement mode</strong>. Before any agent action is executed, the system checks it against every constitutional rule in priority order. Critical rules are checked first.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-shogun-gold" /> Enforcement Modes</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Rules can be set to different enforcement modes: <strong>Block</strong> (action is stopped entirely), <strong>Warn</strong> (action proceeds but a warning is logged), or <strong>Audit</strong> (action proceeds silently, logged for later review). Critical safety rules should always use "Block" mode.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><RefreshCw className="w-4 h-4 text-shogun-gold" /> Revision History</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Every time you publish the Constitution, a new revision is saved. You can review all past versions in the Kaizen sidebar. This creates an immutable audit trail — you can always see who changed what and when. Useful for compliance and debugging unexpected behavior.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Zap className="w-4 h-4 text-shogun-gold" /> The Mandate</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">In addition to the Constitution (hard rules), the Mandate (Kaizen → Mandate tab) injects soft directives into every AI conversation. While the Constitution blocks actions, the Mandate shapes behavior — tone, language, priorities, and focus areas. Both work together to align the AI with your intentions.</p>
                   </div>
                </div>
             </section>

             {/* 4. Harakiri Emergency Protocol */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-red-500/40 pb-3">
                   <AlertCircle className="w-6 h-6 text-red-500" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Harakiri — Emergency Protocol</h4>
                      <p className="text-xs text-shogun-subdued">The nuclear option. When everything else fails, this stops the world.</p>
                   </div>
                </div>
                <div className="shogun-card border-l-4 border-red-500 bg-red-500/[0.02] space-y-6">
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="space-y-3">
                         <div className="font-bold text-red-400 flex items-center gap-2"><Zap className="w-4 h-4" /> What Happens When Activated</div>
                         <ul className="text-xs text-shogun-subdued space-y-2 ml-4 list-disc leading-relaxed">
                            <li><strong>All agent activity is immediately frozen.</strong> Running tasks are interrupted mid-execution. No new tasks can be started.</li>
                            <li><strong>Security posture locks to SHRINE</strong> (maximum protection). Filesystem, network, shell, and tool access are all revoked.</li>
                            <li><strong>A pulsing red banner appears</strong> at the top of every page in the system, alerting all users that the kill switch is active.</li>
                            <li><strong>A critical log entry is created</strong> with the timestamp and reason for activation.</li>
                            <li><strong>External connections are severed.</strong> Telegram bot, Nexus peers, and outgoing API calls are all paused.</li>
                         </ul>
                      </div>
                      <div className="space-y-3">
                         <div className="font-bold text-shogun-text flex items-center gap-2"><Lock className="w-4 h-4 text-red-400" /> Activation & Recovery</div>
                         <ul className="text-xs text-shogun-subdued space-y-2 ml-4 list-disc leading-relaxed">
                            <li><strong>Two-step confirmation:</strong> You must click the Harakiri button, then confirm in a modal dialog. This prevents accidental activation.</li>
                            <li><strong>Available from two locations:</strong> The Dashboard (Tenshu) and the Security Portal (Torii). Both trigger the same global mechanism.</li>
                            <li><strong>To recover:</strong> Click "Reset Harakiri" on the banner or from the Torii page. The posture returns to TACTICAL (the safe default). You must then manually re-enable any higher postures if desired.</li>
                            <li><strong>No data is lost.</strong> Harakiri only freezes operations — it does not delete or modify any data, memories, agents, or settings.</li>
                         </ul>
                      </div>
                   </div>
                   <div className="bg-[#0a0505] border border-red-500/20 p-4 rounded-xl">
                      <p className="text-[10px] text-red-500 font-bold uppercase tracking-widest mb-2">When to Use Harakiri</p>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Use the kill switch when: you observe unexpected or harmful agent behavior, you suspect your API keys have been compromised, an agent is consuming excessive resources, or you need to perform a security audit. When in doubt, press the button — it's always better to freeze and investigate than to let a problem escalate.</p>
                   </div>
                </div>
             </section>

             {/* 5. Operational Security Best Practices */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-shogun-blue/40 pb-3">
                   <Lock className="w-6 h-6 text-shogun-blue" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Operational Security Best Practices</h4>
                      <p className="text-xs text-shogun-subdued">Recommended practices for maintaining a secure Shogun deployment.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2 border-l-2 border-shogun-blue/40">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Key className="w-4 h-4 text-shogun-blue" /> Rotate API Keys Regularly</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">API keys for AI providers should be rotated periodically. If you suspect a key has been exposed, revoke it immediately from the provider's dashboard and update it in Katana → Cloud Providers.</p>
                   </div>
                   <div className="shogun-card space-y-2 border-l-2 border-shogun-blue/40">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Terminal className="w-4 h-4 text-shogun-blue" /> Use the Compliance Dashboard</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">The Logs page is your compliance nerve center. Make it a habit to check the <strong>Decision</strong> tab to review AI reasoning provenance, the <strong>Risk</strong> tab for security tier warnings and denied tools, the <strong>Oversight</strong> tab for human review actions, the <strong>Incident</strong> tab for critical alerts (model API failures, kill switch activations, chain integrity violations), and the <strong>System</strong> tab for server lifecycle and governance config changes. Verify the audit chain stays intact. Export the immutable audit log regularly for off-site archival — this is your evidence for NIS2, SOC2, and EU AI Act compliance.</p>
                   </div>
                   <div className="shogun-card space-y-2 border-l-2 border-shogun-blue/40">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><ShieldCheck className="w-4 h-4 text-shogun-blue" /> Test Posture Changes in SHRINE</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Before upgrading to a higher security posture (e.g., TACTICAL → CAMPAIGN), test your constitutional rules in SHRINE mode first. This ensures your guardrails are properly configured before giving agents more freedom.</p>
                   </div>
                   <div className="shogun-card space-y-2 border-l-2 border-shogun-blue/40">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Network className="w-4 h-4 text-shogun-blue" /> Isolate RONIN Environments</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">If you need RONIN (unrestricted) mode for testing, run it on an isolated machine or VM with no access to production data, credential stores, or external services. Never run RONIN on a machine connected to your main network.</p>
                   </div>
                   <div className="shogun-card space-y-2 border-l-2 border-shogun-blue/40">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Download className="w-4 h-4 text-shogun-blue" /> Backup Before Major Changes</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Before changing the security posture, modifying the Constitution, or deploying new agents, export a backup via the Data Management tab. This gives you a restore point if something goes wrong.</p>
                   </div>
                   <div className="shogun-card space-y-2 border-l-2 border-shogun-blue/40">
                      <div className="font-bold text-shogun-text flex items-center gap-2"><Users className="w-4 h-4 text-shogun-blue" /> Limit Nexus Peer Access</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed">Only invite trusted Shogun instances as peers in Nexus. Every peer can send messages and propose tasks. Verify the identity of remote agents before accepting workspace invitations. Remove inactive or unknown peers promptly.</p>
                   </div>
                </div>
             </section>

             {/* 6. Threat Model */}
             <section className="space-y-6">
                <div className="flex items-center gap-3 border-b-2 border-red-400/40 pb-3">
                   <AlertCircle className="w-6 h-6 text-red-400" />
                   <div>
                      <h4 className="text-xl font-bold uppercase tracking-widest">Threat Model</h4>
                      <p className="text-xs text-shogun-subdued">Known risk categories and how Shogun mitigates them.</p>
                   </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-red-400 flex items-center gap-2"><AlertCircle className="w-4 h-4" /> Prompt Injection</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed"><strong>Risk:</strong> Malicious input that tricks the AI into ignoring its rules. <strong>Mitigation:</strong> Constitutional rules are enforced server-side and cannot be overridden by prompt content. The security posture applies independently of the AI's decision-making.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-red-400 flex items-center gap-2"><AlertCircle className="w-4 h-4" /> Credential Exposure</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed"><strong>Risk:</strong> API keys or secrets leaking through agent responses or logs. <strong>Mitigation:</strong> Keys are stored encrypted in the database and never included in prompts or agent context. The frontend never receives raw key values — only masked previews.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-red-400 flex items-center gap-2"><AlertCircle className="w-4 h-4" /> Runaway Agent</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed"><strong>Risk:</strong> An agent entering a loop, spawning unlimited sub-agents, or consuming excessive API credits. <strong>Mitigation:</strong> Spawn policies limit auto-spawning. The Harakiri kill switch provides instant global shutdown. Resource monitoring in Bushido flags anomalies.</p>
                   </div>
                   <div className="shogun-card space-y-2">
                      <div className="font-bold text-red-400 flex items-center gap-2"><AlertCircle className="w-4 h-4" /> Unauthorized Peer Access</div>
                      <p className="text-xs text-shogun-subdued leading-relaxed"><strong>Risk:</strong> A malicious Shogun instance connecting as a peer and injecting harmful tasks. <strong>Mitigation:</strong> All A2A messages are cryptographically signed. Peers must be explicitly invited by URL. Workspace deletion removes all peer access immediately.</p>
                   </div>
                </div>
             </section>

          </div>
        )}

      {/* Legal Disclaimer */}
      <div className="mt-16 pt-8 border-t border-shogun-border/40">
        <div className="shogun-card bg-orange-500/5 border-orange-500/20">
          <div className="flex items-start gap-4">
            <AlertCircle className="w-6 h-6 text-orange-400 shrink-0 mt-1" />
            <div className="space-y-4">
              <h4 className="text-sm font-bold text-shogun-text uppercase tracking-widest flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-orange-400" />
                {t('guide.disclaimer_title', 'Legal Disclaimer')}
              </h4>
              <p className="text-xs text-shogun-subdued leading-relaxed">
                {t('guide.disclaimer_body', 'Shogun is provided for general informational, experimental, and operational use only. It is provided “as is” and “as available,” without warranties of any kind, express or implied, including but not limited to accuracy, fitness for a particular purpose, merchantability, availability, or non-infringement. Users are solely responsible for evaluating, validating, monitoring, and approving any outputs, actions, configurations, or decisions made with or through Shogun. Alpha Horizon disclaims liability for any direct, indirect, incidental, consequential, or special damages arising from the use of, or inability to use, Shogun, except where such limitation is not permitted by applicable law.')}
              </p>
              <div className="p-3 bg-shogun-bg border border-shogun-border rounded-lg border-l-4 border-l-orange-400">
                <p className="text-xs font-bold text-shogun-text">
                  {t('guide.disclaimer_oversight', 'Human oversight required: Shogun may generate inaccurate, incomplete, or inappropriate outputs. It must not be relied upon without appropriate human review, especially in legal, financial, compliance, security, or other high-impact contexts.')}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  );
}
