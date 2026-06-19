import { useState, useEffect, useRef, useCallback } from 'react';
import {
  LayoutDashboard, Shield, Users, Layers, Activity,
  FileSearch, Bell, UserPlus, Skull, Network, Settings,
  BookOpen, List, Server, AlertTriangle, Zap, Lock,
  Monitor, Globe, Tag, Copy, Search, Eye, Trash2,
  Check, X, Key, Info
} from 'lucide-react';

const SECTIONS = [
  { id: 'ref-dashboard', label: 'Dashboard', icon: LayoutDashboard, color: 'text-cyan-400' },
  { id: 'ref-fleet', label: 'Fleet', icon: Users, color: 'text-emerald-400' },
  { id: 'ref-detail', label: 'Shogun Detail', icon: Server, color: 'text-cyan-400' },
  { id: 'ref-network', label: 'Network Topology', icon: Network, color: 'text-cyan-400' },
  { id: 'ref-groups', label: 'Groups', icon: Layers, color: 'text-purple-400' },
  { id: 'ref-postures', label: 'Postures', icon: Shield, color: 'text-amber-400' },
  { id: 'ref-harakiri', label: 'Harakiri Control', icon: Skull, color: 'text-red-400' },
  { id: 'ref-activity', label: 'Activity Monitor', icon: Activity, color: 'text-cyan-400' },
  { id: 'ref-audit', label: 'Audit Log', icon: FileSearch, color: 'text-gensui-400' },
  { id: 'ref-alerts', label: 'Alerts', icon: Bell, color: 'text-amber-400' },
  { id: 'ref-enrollment', label: 'Enrollment', icon: UserPlus, color: 'text-amber-400' },
  { id: 'ref-settings', label: 'Settings', icon: Settings, color: 'text-cyan-400' },
];

export default function Guide() {
  const [activeSection, setActiveSection] = useState('ref-dashboard');

  const scrollToSection = useCallback((id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setActiveSection(id);
    }
  }, []);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) setActiveSection(entry.target.id);
        }
      },
      { rootMargin: '-80px 0px -60% 0px', threshold: 0.1 }
    );
    const timer = setTimeout(() => {
      SECTIONS.forEach(({ id }) => {
        const el = document.getElementById(id);
        if (el) observer.observe(el);
      });
    }, 100);
    return () => { clearTimeout(timer); observer.disconnect(); };
  }, []);

  const cn = (...classes: (string | boolean | undefined)[]) => classes.filter(Boolean).join(' ');

  return (
    <div className="space-y-6 max-w-7xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gensui-50 flex items-center gap-3">
          <BookOpen size={24} className="text-cyan-400" />
          Reference Manual
          <span className="text-[10px] font-normal text-gensui-500 bg-gensui-800/60 px-2 py-0.5 rounded border border-gensui-700/30 tracking-[0.3em] uppercase">Guide</span>
        </h1>
        <p className="text-sm text-gensui-400 mt-1">A comprehensive, page-by-page, button-by-button manual of every capability within Gensui Command Center.</p>
      </div>

      {/* Two-column layout: sidebar + content */}
      <div className="flex gap-8">
        {/* Sticky Sidebar Navigation */}
        <nav className="hidden lg:block w-52 shrink-0">
          <div className="sticky top-6 space-y-1 p-3 bg-gensui-800/40 border border-gensui-700/30 rounded-xl max-h-[calc(100vh-120px)] overflow-y-auto">
            <div className="flex items-center gap-2 px-2 pb-2 mb-2 border-b border-gensui-700/30">
              <List size={14} className="text-cyan-400" />
              <span className="text-[10px] font-bold text-gensui-500 uppercase tracking-widest">Sections</span>
            </div>
            {SECTIONS.map((sec) => (
              <button
                key={sec.id}
                onClick={() => scrollToSection(sec.id)}
                className={cn(
                  "w-full flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-[11px] font-medium transition-all duration-200 text-left",
                  activeSection === sec.id
                    ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-sm"
                    : "text-gensui-400 hover:text-gensui-200 hover:bg-gensui-700/30 border border-transparent"
                )}
              >
                <sec.icon size={14} className={cn("shrink-0", activeSection === sec.id ? 'text-cyan-400' : sec.color)} />
                {sec.label}
              </button>
            ))}
          </div>
        </nav>

        {/* Main Content */}
        <div className="flex-1 min-w-0 space-y-14">

          {/* ═══════════════════════════════════════════════════════ */}
          {/* 1. DASHBOARD */}
          {/* ═══════════════════════════════════════════════════════ */}
          <section id="ref-dashboard" className="space-y-4 scroll-mt-6">
            <div className="flex items-center gap-3 border-b border-gensui-700/30 pb-3">
              <LayoutDashboard size={20} className="text-cyan-400" />
              <div>
                <h2 className="text-lg font-bold text-gensui-100 uppercase tracking-widest">Dashboard &mdash; Command Overview</h2>
                <p className="text-xs text-gensui-400">Real-time fleet monitoring and security status at a glance.</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Users size={14} className="text-emerald-400" /> Fleet Stats Grid (Top Row)</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Four metric cards at the top. Each shows a count and optional total:</p>
                <ul className="text-xs text-gensui-400 space-y-1 ml-4 list-disc">
                  <li><strong className="text-gensui-200">Members Online:</strong> Shows how many Shogun instances are currently connected vs. total enrolled.</li>
                  <li><strong className="text-gensui-200">Active Samurai:</strong> Total sub-agents running across all fleet members.</li>
                  <li><strong className="text-gensui-200">Active Workflows:</strong> Running Agent Flow pipelines fleet-wide.</li>
                  <li><strong className="text-gensui-200">Mado Sessions:</strong> Active browser automation sessions across all Shoguns.</li>
                </ul>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><AlertTriangle size={14} className="text-red-400" /> Alert &amp; Status Row</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Three clickable cards below the stats grid:</p>
                <ul className="text-xs text-gensui-400 space-y-1 ml-4 list-disc">
                  <li><strong className="text-gensui-200">Active Alerts:</strong> Number of unresolved alerts. Turns red when critical alerts exist. Click to navigate to the Alerts page.</li>
                  <li><strong className="text-gensui-200">Harakiri Active:</strong> Shows "None" (green) or the count of active Harakiri events (red pulsing). Click to go to Harakiri Control.</li>
                  <li><strong className="text-gensui-200">Pending Enrollment:</strong> Number of Shogun instances awaiting approval. Click to go to Enrollment Management.</li>
                </ul>
              </div>
              <div className="glass-card p-4 space-y-2 md:col-span-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Shield size={14} className="text-red-400" /> Global Posture Override Banner</div>
                <p className="text-xs text-gensui-400 leading-relaxed">When a Global Posture Override is active (see Postures), a red danger-glowing banner appears showing the posture name, who activated it, and the reason. This means <strong>all fleet members are currently locked to a specific security posture</strong> regardless of their individual settings.</p>
              </div>
              <div className="glass-card p-4 space-y-2 md:col-span-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Activity size={14} className="text-cyan-400" /> Auto-Refresh</div>
                <p className="text-xs text-gensui-400 leading-relaxed">All dashboard data auto-refreshes every <strong>10 seconds</strong>. No manual reload needed. The data is fetched from <code className="text-gensui-300 bg-gensui-800 px-1 py-0.5 rounded">GET /api/v1/dashboard</code>.</p>
              </div>
            </div>
          </section>

          {/* ═══════════════════════════════════════════════════════ */}
          {/* 2. FLEET */}
          {/* ═══════════════════════════════════════════════════════ */}
          <section id="ref-fleet" className="space-y-4 scroll-mt-6">
            <div className="flex items-center gap-3 border-b border-gensui-700/30 pb-3">
              <Users size={20} className="text-emerald-400" />
              <div>
                <h2 className="text-lg font-bold text-gensui-100 uppercase tracking-widest">Fleet Management</h2>
                <p className="text-xs text-gensui-400">View, search, and filter all enrolled Shogun instances.</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Search size={14} className="text-cyan-400" /> Search &amp; Filter Bar</div>
                <p className="text-xs text-gensui-400 leading-relaxed">A text search field and a status dropdown at the top. Search by <strong>instance name</strong> or <strong>hostname</strong>. Filter by status: All, Online, or Offline.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Eye size={14} className="text-cyan-400" /> Fleet Table</div>
                <p className="text-xs text-gensui-400 leading-relaxed">A sortable table with columns: <strong>Instance</strong> (name + hostname, clickable to detail), <strong>Status</strong> (online/offline badge with pulse), <strong>Environment</strong>, <strong>Harakiri</strong> (active state or "—"), <strong>Samurai</strong> count, <strong>Workflows</strong> count, <strong>Last Seen</strong> timestamp. Data auto-refreshes every 10 seconds.</p>
              </div>
              <div className="glass-card p-4 space-y-2 md:col-span-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Server size={14} className="text-cyan-400" /> Clicking an Instance</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Click any instance name in the table to navigate to its <strong>Shogun Detail</strong> page (see next section). This is the deep-dive view for a single fleet member.</p>
              </div>
            </div>
          </section>

          {/* ═══════════════════════════════════════════════════════ */}
          {/* 3. SHOGUN DETAIL */}
          {/* ═══════════════════════════════════════════════════════ */}
          <section id="ref-detail" className="space-y-4 scroll-mt-6">
            <div className="flex items-center gap-3 border-b border-gensui-700/30 pb-3">
              <Server size={20} className="text-cyan-400" />
              <div>
                <h2 className="text-lg font-bold text-gensui-100 uppercase tracking-widest">Shogun Detail &mdash; Instance Deep Dive</h2>
                <p className="text-xs text-gensui-400">Full operational profile for a single Shogun instance.</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Tag size={14} className="text-cyan-400" /> Header &amp; Status Badges</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Shows the instance name, online/offline badge, and a pulsing red Harakiri badge if active. Below: hostname, environment, and enrollment date. A back arrow returns to the Fleet page.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Activity size={14} className="text-cyan-400" /> Stats Row</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Five metric cards: <strong>Samurai</strong> count, <strong>Workflows</strong> running, <strong>Mado Sessions</strong>, <strong>Last Seen</strong> time, and <strong>Enrollment</strong> status. Each has a colored icon.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Info size={14} className="text-cyan-400" /> Identity Card (Left Column)</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Displays: Version, Build hash (first 12 chars), OS, Deploy Type, Organization, Owner, and Disconnect Behavior. All read from the Shogun's heartbeat telemetry.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Shield size={14} className="text-amber-400" /> Security Posture Card</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Shows the <strong>effective posture</strong> currently applied to this Shogun: posture name, source (individual, group, or global), and level number. If no posture is assigned, shows "No posture assigned."</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Layers size={14} className="text-purple-400" /> Groups Card</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Lists all groups this Shogun belongs to as purple tag badges. Groups are managed from the Groups page and allow collective posture/policy application.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><AlertTriangle size={14} className="text-red-400" /> Actions Card</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Three action buttons for this specific instance:</p>
                <ul className="text-xs text-gensui-400 space-y-1 ml-4 list-disc">
                  <li><strong className="text-amber-400">Soft Freeze:</strong> Triggers a soft Harakiri &mdash; suspends all active operations gracefully.</li>
                  <li><strong className="text-red-400">Hard Stop:</strong> Triggers a hard Harakiri &mdash; immediately kills all processes.</li>
                  <li><strong className="text-red-400">Disable Instance:</strong> Revokes enrollment. The Shogun is disconnected from the fleet permanently until re-enrolled.</li>
                </ul>
              </div>
              <div className="glass-card p-4 space-y-2 md:col-span-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Activity size={14} className="text-cyan-400" /> Activity Timeline (Right Column)</div>
                <p className="text-xs text-gensui-400 leading-relaxed">A scrollable timeline of telemetry events from this specific Shogun. Each event shows: severity dot (red/amber/cyan/gray), event type, category, payload message, and timestamp. Limited to the 50 most recent events. Auto-refreshes every 15 seconds.</p>
              </div>
            </div>
          </section>

          {/* ═══════════════════════════════════════════════════════ */}
          {/* 4. NETWORK TOPOLOGY */}
          {/* ═══════════════════════════════════════════════════════ */}
          <section id="ref-network" className="space-y-4 scroll-mt-6">
            <div className="flex items-center gap-3 border-b border-gensui-700/30 pb-3">
              <Network size={20} className="text-cyan-400" />
              <div>
                <h2 className="text-lg font-bold text-gensui-100 uppercase tracking-widest">Network Topology &mdash; Visual Map</h2>
                <p className="text-xs text-gensui-400">Interactive SVG graph showing all fleet members, their connections, and discovered hosts.</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Globe size={14} className="text-cyan-400" /> Topology Graph</div>
                <p className="text-xs text-gensui-400 leading-relaxed">A full-width interactive SVG canvas. At the center: the <strong>Gensui Hub</strong> (gold border, logo). Around it in a circle: all enrolled Shogun instances as colored nodes. Lines connect each node to the hub (cyan). Dashed amber lines show Nexus peer-to-peer connections between Shoguns.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Eye size={14} className="text-emerald-400" /> Node Colors &amp; Status</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Each node has a color indicating status:</p>
                <ul className="text-xs text-gensui-400 space-y-1 ml-4 list-disc">
                  <li><strong className="text-emerald-400">Green (Online):</strong> Connected and reporting heartbeats. Has a pulsing animation ring.</li>
                  <li><strong className="text-gensui-400">Gray (Offline):</strong> Not responding. No pulse.</li>
                  <li><strong className="text-red-400">Red (Harakiri):</strong> Emergency shutdown is active on this instance.</li>
                </ul>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Search size={14} className="text-cyan-400" /> Network Scan</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Click <strong>"Scan Network"</strong> to probe your local subnet for other Shogun instances. The scan probes all IPs on port 8000, identifies Shogun instances (by checking <code className="text-gensui-300 bg-gensui-800 px-1 py-0.5 rounded">/health</code>), and classifies them as <strong>enrolled</strong>, <strong>unenrolled (rogue)</strong>, or <strong>unknown</strong>. Results appear as dashed-border nodes in an outer ring.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Monitor size={14} className="text-cyan-400" /> Pan &amp; Zoom Controls</div>
                <p className="text-xs text-gensui-400 leading-relaxed"><strong>Scroll wheel</strong> to zoom in/out. <strong>Click and drag</strong> to pan. Use the zoom controls in the bottom-left: zoom in (+), zoom out (−), reset view. Hover over any node to see a detailed tooltip with hostname, status, samurai count, and enrollment info. Click an enrolled node to navigate to its detail page.</p>
              </div>
              <div className="glass-card p-4 space-y-2 md:col-span-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><AlertTriangle size={14} className="text-red-400" /> Rogue Detection</div>
                <p className="text-xs text-gensui-400 leading-relaxed">After a network scan, <strong>unenrolled Shogun instances</strong> appear as red dashed-border nodes with a warning icon. These are Shogun instances on your network that are <em>not</em> enrolled in Gensui &mdash; potential security risks. <strong>Unknown hosts</strong> (port 8000 open but not Shogun) appear as gray dotted nodes. A red trust boundary ring separates enrolled nodes from external ones.</p>
              </div>
              <div className="glass-card p-4 space-y-2 md:col-span-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Globe size={14} className="text-purple-400" /> External Enterprise Agents</div>
                <p className="text-xs text-gensui-400 leading-relaxed">When Shogun instances have external agents registered via the <strong>Nexus External Gateway</strong>, they appear on the topology as <strong>diamond-shaped nodes</strong> connected to their host Shogun with dashed purple lines. Each agent node shows:</p>
                <ul className="text-xs text-gensui-400 space-y-1 ml-4 list-disc">
                  <li><strong className="text-gensui-200">Platform-specific colors:</strong> Microsoft 365 (blue), Salesforce (cyan), Google (green), ServiceNow (lime), Custom (purple).</li>
                  <li><strong className="text-gensui-200">Direction arrows:</strong> &larr; = inbound (agent sends tasks to Shogun), &rarr; = outbound (Shogun sends tasks to agent), &#x21c4; = bidirectional (both directions).</li>
                  <li><strong className="text-gensui-200">Tooltip on hover:</strong> Shows agent name, platform, communication direction, whether an outbound endpoint is configured, and which Shogun hosts the connection.</li>
                </ul>
                <p className="text-xs text-gensui-400 leading-relaxed">The legend shows an "External Agents" section when agents are present, and a "Nexus Gateway" connection type in the Connections list.</p>
              </div>
            </div>
          </section>

          {/* ═══════════════════════════════════════════════════════ */}
          {/* 5. GROUPS */}
          {/* ═══════════════════════════════════════════════════════ */}
          <section id="ref-groups" className="space-y-4 scroll-mt-6">
            <div className="flex items-center gap-3 border-b border-gensui-700/30 pb-3">
              <Layers size={20} className="text-purple-400" />
              <div>
                <h2 className="text-lg font-bold text-gensui-100 uppercase tracking-widest">Groups &mdash; Collective Management</h2>
                <p className="text-xs text-gensui-400">Organize Shogun instances into groups for collective policy management.</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Zap size={14} className="text-purple-400" /> Create Group</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Enter a group name in the text field and click <strong>"Create Group"</strong>. Groups let you apply postures, trigger Harakiri, and manage policies for multiple Shoguns at once instead of one by one.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Trash2 size={14} className="text-red-400" /> Group Cards</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Each group appears as a card showing the <strong>group name</strong>, <strong>member count</strong>, and optional description. Click the <strong>trash icon</strong> on a card to delete the group (with confirmation). Deleting a group does not delete its member Shoguns &mdash; they simply become ungrouped.</p>
              </div>
            </div>
          </section>

          {/* ═══════════════════════════════════════════════════════ */}
          {/* 6. POSTURES */}
          {/* ═══════════════════════════════════════════════════════ */}
          <section id="ref-postures" className="space-y-4 scroll-mt-6">
            <div className="flex items-center gap-3 border-b border-gensui-700/30 pb-3">
              <Shield size={20} className="text-amber-400" />
              <div>
                <h2 className="text-lg font-bold text-gensui-100 uppercase tracking-widest">Security Postures</h2>
                <p className="text-xs text-gensui-400">Define what Shogun instances are allowed to do. Each posture is a permission template.</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="glass-card p-4 space-y-2 md:col-span-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Shield size={14} className="text-amber-400" /> Posture Cards</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Each posture card shows the <strong>name</strong>, <strong>level number</strong>, and <strong>description</strong>. A "Built-in" tag appears on system-defined postures. Below the description, every permission is shown as a colored badge:</p>
                <ul className="text-xs text-gensui-400 space-y-1 ml-4 list-disc">
                  <li><strong className="text-emerald-400">Green (✓):</strong> Permission is <em>allowed</em> in this posture.</li>
                  <li><strong className="text-red-400">Red (✕):</strong> Permission is <em>denied</em> in this posture.</li>
                </ul>
              </div>
              <div className="glass-card p-4 space-y-2 md:col-span-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Lock size={14} className="text-amber-400" /> Permission Categories (14 Total)</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Each posture controls these 14 permission flags:</p>
                <div className="flex flex-wrap gap-1.5 mt-2">
                  {[
                    'external models', 'local models', 'tool execution', 'mado (browser)',
                    'memory write', 'memory read', 'agent flow', 'nexus',
                    'samurai delegation', 'scheduled triggers', 'autonomous loops',
                    'external web', 'file write', 'external api',
                  ].map(p => (
                    <span key={p} className="text-[10px] px-2 py-0.5 rounded-full bg-gensui-700/40 text-gensui-300 border border-gensui-600/30">{p}</span>
                  ))}
                </div>
              </div>
            </div>
          </section>

          {/* ═══════════════════════════════════════════════════════ */}
          {/* 7. HARAKIRI CONTROL */}
          {/* ═══════════════════════════════════════════════════════ */}
          <section id="ref-harakiri" className="space-y-4 scroll-mt-6">
            <div className="flex items-center gap-3 border-b border-red-800/40 pb-3">
              <Skull size={20} className="text-red-400" />
              <div>
                <h2 className="text-lg font-bold text-gensui-100 uppercase tracking-widest">Harakiri Control Center</h2>
                <p className="text-xs text-red-400">Emergency shutdown and containment. Use with extreme caution.</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="glass-card p-4 space-y-2 md:col-span-2 border border-red-800/30">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Zap size={14} className="text-red-400" /> Initiate Harakiri Panel</div>
                <p className="text-xs text-gensui-400 leading-relaxed">The main trigger panel. Configure and execute emergency shutdowns:</p>
                <ul className="text-xs text-gensui-400 space-y-1.5 ml-4 list-disc">
                  <li><strong className="text-gensui-200">Scope:</strong> Choose <strong>Individual</strong> (one Shogun) or <strong>Global</strong> (ALL Shoguns in the fleet simultaneously).</li>
                  <li><strong className="text-gensui-200">Mode:</strong> Four escalation levels:
                    <ul className="mt-1 ml-4 space-y-0.5 list-disc">
                      <li><strong>Soft Freeze:</strong> Gracefully suspends all active operations.</li>
                      <li><strong>Hard Stop:</strong> Immediately kills all running processes.</li>
                      <li><strong>Network Isolate:</strong> Cuts all external network access while keeping the instance alive.</li>
                      <li><strong>Full Terminate:</strong> Complete shutdown of the Shogun instance.</li>
                    </ul>
                  </li>
                  <li><strong className="text-gensui-200">Target Shogun:</strong> (Individual mode only) Select which instance to target from a dropdown of active members.</li>
                  <li><strong className="text-gensui-200">Reason:</strong> A text field for documenting why the Harakiri is being triggered. Logged in the audit trail.</li>
                </ul>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Lock size={14} className="text-red-400" /> Two-Step Confirmation</div>
                <p className="text-xs text-gensui-400 leading-relaxed">After clicking "Initiate Harakiri," a red confirmation box appears. You must type <strong>"CONFIRM HARAKIRI"</strong> (or <strong>"CONFIRM GLOBAL HARAKIRI"</strong> for global scope) exactly to enable the Execute button. This prevents accidental activation.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Activity size={14} className="text-cyan-400" /> Event History Table</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Below the trigger panel, a table of all past Harakiri events: Scope (individual/global), Mode, Status (pending/executing/completed/released), Affected count, Acknowledged count, Timestamp, and a <strong>Release</strong> button to lift an active Harakiri and restore the instance to RESTRICTED posture.</p>
              </div>
            </div>
          </section>

          {/* ═══════════════════════════════════════════════════════ */}
          {/* 8. ACTIVITY MONITOR */}
          {/* ═══════════════════════════════════════════════════════ */}
          <section id="ref-activity" className="space-y-4 scroll-mt-6">
            <div className="flex items-center gap-3 border-b border-gensui-700/30 pb-3">
              <Activity size={20} className="text-cyan-400" />
              <div>
                <h2 className="text-lg font-bold text-gensui-100 uppercase tracking-widest">Activity Monitor</h2>
                <p className="text-xs text-gensui-400">Real-time telemetry event stream from all fleet members.</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Search size={14} className="text-cyan-400" /> Category Filter</div>
                <p className="text-xs text-gensui-400 leading-relaxed">A dropdown filter in the top-right lets you filter events by category: <strong>System</strong>, <strong>Security</strong>, <strong>Agent</strong>, <strong>Tool</strong>, <strong>Model</strong>, or <strong>All Categories</strong>.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Eye size={14} className="text-cyan-400" /> Event Table</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Columns: <strong>Time</strong>, <strong>Severity</strong> (colored badge: critical/error = red, warn = amber, info = default), <strong>Type</strong> (monospace event identifier), <strong>Category</strong>, <strong>Shogun</strong> (first 8 chars of ID). Shows the latest 100 events. Auto-refreshes every <strong>5 seconds</strong>.</p>
              </div>
            </div>
          </section>

          {/* ═══════════════════════════════════════════════════════ */}
          {/* 9. AUDIT LOG */}
          {/* ═══════════════════════════════════════════════════════ */}
          <section id="ref-audit" className="space-y-4 scroll-mt-6">
            <div className="flex items-center gap-3 border-b border-gensui-700/30 pb-3">
              <FileSearch size={20} className="text-gensui-400" />
              <div>
                <h2 className="text-lg font-bold text-gensui-100 uppercase tracking-widest">Audit Log &mdash; HMAC-Chained</h2>
                <p className="text-xs text-gensui-400">Tamper-resistant record of every administrative action.</p>
              </div>
            </div>
            <div className="grid grid-cols-1 gap-3">
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><FileSearch size={14} className="text-gensui-300" /> Audit Table</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Columns: <strong>Time</strong>, <strong>Actor</strong> (who performed the action &mdash; admin user or system), <strong>Action</strong> (monospace identifier like <code className="text-gensui-300 bg-gensui-800 px-1 py-0.5 rounded">harakiri.trigger</code>, <code className="text-gensui-300 bg-gensui-800 px-1 py-0.5 rounded">enrollment.approve</code>, etc.), <strong>Target</strong> (type + first 8 chars of target ID), <strong>Reason</strong>. Filter by action using the text input in the top-right. The subtitle shows "HMAC-chained" confirming these entries are cryptographically linked for tamper detection.</p>
              </div>
            </div>
          </section>

          {/* ═══════════════════════════════════════════════════════ */}
          {/* 10. ALERTS */}
          {/* ═══════════════════════════════════════════════════════ */}
          <section id="ref-alerts" className="space-y-4 scroll-mt-6">
            <div className="flex items-center gap-3 border-b border-gensui-700/30 pb-3">
              <Bell size={20} className="text-amber-400" />
              <div>
                <h2 className="text-lg font-bold text-gensui-100 uppercase tracking-widest">Alerts</h2>
                <p className="text-xs text-gensui-400">Security and system alerts from across the fleet.</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Bell size={14} className="text-amber-400" /> Alerts Table</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Columns: <strong>Time</strong>, <strong>Severity</strong> (CRITICAL = red, HIGH = lighter red, MEDIUM = amber, LOW = gray), <strong>Type</strong> (monospace event identifier), <strong>Description</strong>, <strong>Status</strong> (active = red badge, resolved = green badge), <strong>Actions</strong>.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Check size={14} className="text-emerald-400" /> Resolving Alerts</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Active alerts show a <strong>"Resolve"</strong> button in the Actions column. Clicking it marks the alert as resolved (green badge) and logs the resolution in the audit trail. Resolved alerts remain visible for historical reference.</p>
              </div>
            </div>
          </section>

          {/* ═══════════════════════════════════════════════════════ */}
          {/* 11. ENROLLMENT */}
          {/* ═══════════════════════════════════════════════════════ */}
          <section id="ref-enrollment" className="space-y-4 scroll-mt-6">
            <div className="flex items-center gap-3 border-b border-gensui-700/30 pb-3">
              <UserPlus size={20} className="text-amber-400" />
              <div>
                <h2 className="text-lg font-bold text-gensui-100 uppercase tracking-widest">Enrollment Management</h2>
                <p className="text-xs text-gensui-400">Approve new Shogun instances and manage enrollment tokens.</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="glass-card p-4 space-y-2 md:col-span-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><UserPlus size={14} className="text-amber-400" /> Pending Enrollments Table</div>
                <p className="text-xs text-gensui-400 leading-relaxed">When a Shogun instance connects to Gensui for the first time, it appears here as a pending enrollment. The table shows: <strong>Instance</strong> name, <strong>Hostname</strong>, <strong>Environment</strong>, <strong>OS</strong>, <strong>Requested</strong> timestamp, and <strong>Actions</strong>:</p>
                <ul className="text-xs text-gensui-400 space-y-1 ml-4 list-disc">
                  <li><strong className="text-emerald-400">✓ Approve:</strong> Accept the instance into the fleet. It becomes an active member and starts receiving posture policies.</li>
                  <li><strong className="text-red-400">✕ Reject:</strong> Deny the enrollment request. The instance will not be able to participate in the fleet.</li>
                </ul>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Key size={14} className="text-cyan-400" /> Enrollment Tokens</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Pre-generate tokens that Shogun instances can use to auto-enroll. Enter a <strong>label</strong> (optional) and click <strong>"Generate Token"</strong>. Each token shows: label, first 30 characters (monospace), use count vs. max uses, and a revoked indicator if applicable.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Copy size={14} className="text-cyan-400" /> Copy Token</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Click the <strong>copy icon</strong> next to any token to copy it to your clipboard. Send this token to the Shogun operator &mdash; they paste it into their Gensui connection form on the Shogun side (Gensui page &rarr; Connect). The token is single-use by default.</p>
              </div>
            </div>
          </section>

          {/* ═══════════════════════════════════════════════════════ */}
          {/* 12. SETTINGS */}
          {/* ═══════════════════════════════════════════════════════ */}
          <section id="ref-settings" className="space-y-4 scroll-mt-6">
            <div className="flex items-center gap-3 border-b border-gensui-700/30 pb-3">
              <Settings size={20} className="text-cyan-400" />
              <div>
                <h2 className="text-lg font-bold text-gensui-100 uppercase tracking-widest">Settings</h2>
                <p className="text-xs text-gensui-400">Manage your admin profile, password, and view server configuration.</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Users size={14} className="text-cyan-400" /> Profile Section</div>
                <p className="text-xs text-gensui-400 leading-relaxed">View your <strong>email</strong> (read-only), <strong>role</strong> (read-only), and edit your <strong>display name</strong>. Click <strong>"Save Profile"</strong> to persist changes. A green confirmation message appears on success.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Lock size={14} className="text-amber-400" /> Change Password</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Enter your <strong>current password</strong>, <strong>new password</strong> (minimum 6 characters), and <strong>confirm</strong> the new password. Passwords must match. Click <strong>"Change Password"</strong> to update. Error messages appear for mismatches or incorrect current passwords.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Server size={14} className="text-purple-400" /> Server Configuration</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Read-only display of server settings: <strong>JWT Token Expiry</strong> (24 hours), <strong>Heartbeat Timeout</strong> (60 seconds &mdash; how long before a Shogun is marked offline), <strong>Enrollment Approval</strong> (required/auto), <strong>Default Posture</strong> (STANDARD). These are configured via the <code className="text-gensui-300 bg-gensui-800 px-1 py-0.5 rounded">.env</code> file and require a server restart to change.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Info size={14} className="text-gensui-400" /> About</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Displays the Gensui version number and confirms it is part of the <strong>Shogun AFM (Agent Fleet Management)</strong> platform.</p>
              </div>
            </div>
          </section>

        </div>
      </div>
    </div>
  );
}
