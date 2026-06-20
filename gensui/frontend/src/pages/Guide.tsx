import { useState, useEffect, useRef, useCallback } from 'react';
import {
  LayoutDashboard, Shield, Users, Layers, Activity,
  FileSearch, Bell, UserPlus, Skull, Network, Settings,
  BookOpen, List, Server, AlertTriangle, Zap, Lock,
  Monitor, Globe, Tag, Copy, Search, Eye, Trash2,
  Check, X, Key, Info, ShieldAlert, Clock, BarChart3
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
  { id: 'ref-security', label: 'Security Protocols', icon: ShieldAlert, color: 'text-red-400' },
  { id: 'ref-fleet-audit', label: 'Fleet Audit', icon: BarChart3, color: 'text-cyan-400' },
  { id: 'ref-identity', label: 'Enterprise Identity', icon: Key, color: 'text-purple-400' },
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
                <p className="text-xs text-gensui-400">Define what Shogun instances are allowed to do. Each posture is a permission template. Create, edit, and delete postures to control your fleet.</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="glass-card p-4 space-y-2 md:col-span-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Shield size={14} className="text-amber-400" /> Posture Cards</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Each posture card shows the <strong>name</strong>, <strong>level number</strong> (0–100, higher = more restrictive), and <strong>description</strong>. A "Built-in" tag appears on system-defined postures. Below the description, every permission is shown as a colored badge:</p>
                <ul className="text-xs text-gensui-400 space-y-1 ml-4 list-disc">
                  <li><strong className="text-emerald-400">Green (✓):</strong> Permission is <em>allowed</em> in this posture.</li>
                  <li><strong className="text-red-400">Red (✕):</strong> Permission is <em>denied</em> in this posture.</li>
                </ul>
                <p className="text-xs text-gensui-400 leading-relaxed mt-2">A stats row at the bottom shows the count of allowed, blocked, and tool override rules.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Zap size={14} className="text-emerald-400" /> Create Posture</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Click <strong>"Create Posture"</strong> in the top right to open the creation modal. Fill in a name, description, level (0–100), and toggle each of the 14 permission flags. You can also add <strong>tool overrides</strong> — per-tool rules that override the posture's general tool execution flag for specific tools (e.g., block <code className="text-gensui-300 bg-gensui-800 px-1 py-0.5 rounded">send_email</code> while allowing other tools). Click <strong>"Create"</strong> to save.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Eye size={14} className="text-cyan-400" /> Edit Posture</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Hover over any posture card and click the <strong>pencil icon</strong> to open the edit modal. You can change the description, level, all 14 permission flags, and tool overrides. <strong>Built-in postures</strong> (like OPEN, STANDARD, LOCKDOWN) can be edited — flags and description are modifiable — but their names cannot be changed. Edits persist across server restarts.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Trash2 size={14} className="text-red-400" /> Delete Posture</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Custom postures can be deleted by clicking the <strong>trash icon</strong> on the card. A confirmation dialog appears. Deleting a posture automatically <strong>unassigns</strong> it from any members or groups that were using it. <strong>Built-in postures cannot be deleted</strong> — the trash icon is hidden for them.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Settings size={14} className="text-purple-400" /> Tool Overrides</div>
                <p className="text-xs text-gensui-400 leading-relaxed">In the create/edit modal, expand the <strong>"Tool Overrides"</strong> section to define per-tool rules. Select a tool from the dropdown, then set it to <strong>Allow</strong>, <strong>Confirm</strong> (requires human approval before execution), or <strong>Block</strong> (tool call is rejected). Add multiple overrides for fine-grained control. These overrides are pushed to fleet members as part of their effective posture.</p>
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
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><X size={14} className="text-red-400" /> Revoke Token</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Click the <strong>ban icon</strong> (✘) next to any active token to revoke it. A confirmation dialog appears. Once revoked, the token can <strong>never be used again</strong> for enrollment &mdash; any Shogun instance attempting to enroll with a revoked token will be rejected. The token remains visible in the list with a red <strong>"Revoked"</strong> badge for audit purposes. This action is logged in the HMAC-chained audit trail.</p>
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

          {/* Security Protocols */}
          <section id="ref-security" className="space-y-6">
            <div className="flex items-center gap-3 border-b border-gensui-700 pb-3">
              <ShieldAlert size={28} className="text-red-400" />
              <div>
                <h2 className="text-2xl font-bold text-gensui-50">Safety & Security Protocols</h2>
                <p className="text-xs text-gensui-400">Gensui's defense-in-depth security model for centrally governing Shogun instances.</p>
              </div>
            </div>

            {/* ToolGate Governance */}
            <div className="glass-card p-5 space-y-4">
              <div className="flex items-center gap-2">
                <ShieldAlert size={18} className="text-amber-400" />
                <h3 className="text-lg font-bold text-gensui-100">ToolGate — Centralized Tool Enforcement</h3>
              </div>
              <p className="text-xs text-gensui-400 leading-relaxed">ToolGate is the runtime safety gate that sits between the AI model and tool execution on every Shogun instance. From Gensui, you can centrally manage <strong>tool-level overrides</strong> that are pushed to all member instances via the policy sync mechanism.</p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-lg p-3 space-y-1">
                  <div className="text-xs font-bold text-emerald-400 uppercase tracking-wider">ALLOW</div>
                  <p className="text-[11px] text-gensui-400">Tool executes immediately with no interruption. Used for low-risk, read-only operations.</p>
                </div>
                <div className="bg-amber-500/5 border border-amber-500/20 rounded-lg p-3 space-y-1">
                  <div className="text-xs font-bold text-amber-400 uppercase tracking-wider">CONFIRM</div>
                  <p className="text-[11px] text-gensui-400">Tool pauses and shows a confirmation card to the local operator. They must approve or deny before execution. 60-second auto-deny timeout.</p>
                </div>
                <div className="bg-red-500/5 border border-red-500/20 rounded-lg p-3 space-y-1">
                  <div className="text-xs font-bold text-red-400 uppercase tracking-wider">BLOCK</div>
                  <p className="text-[11px] text-gensui-400">Tool is blocked outright. The AI receives a "blocked" response and must find an alternative.</p>
                </div>
              </div>
              <div className="bg-gensui-800 border border-gensui-700 p-3 rounded-lg">
                <p className="text-xs text-gensui-400 leading-relaxed"><strong className="text-gensui-200">Governance Override Priority:</strong> Campaign Preset → <strong className="text-amber-400">Gensui Governance Override</strong> → Parameter-Aware Checks → Mode×Risk Threshold. Gensui overrides take priority over local ToolGate defaults but are superseded by active Campaign Presets.</p>
              </div>
            </div>

            {/* Posture Push */}
            <div className="glass-card p-5 space-y-4">
              <div className="flex items-center gap-2">
                <Shield size={18} className="text-cyan-400" />
                <h3 className="text-lg font-bold text-gensui-100">Posture Push — Policy Sync</h3>
              </div>
              <p className="text-xs text-gensui-400 leading-relaxed">Every Shogun instance periodically (every 30 seconds by default) fetches its effective posture from Gensui. This includes:</p>
              <ul className="text-xs text-gensui-400 space-y-2 ml-4 list-disc leading-relaxed">
                <li><strong className="text-gensui-200">Posture Rules:</strong> allow/deny flags for external models, tool execution, Mado browser, memory access, Nexus, sub-agents, scheduled triggers, autonomous loops, file writes, and external APIs.</li>
                <li><strong className="text-gensui-200">Tool Overrides:</strong> Per-tool allow/confirm/block overrides configured in the posture's tool_overrides field. These are pushed to ToolGate on the local instance.</li>
                <li><strong className="text-gensui-200">Global Posture:</strong> If a global posture override is active, it takes precedence over individual or group assignments.</li>
                <li><strong className="text-gensui-200">Harakiri State:</strong> If Harakiri is triggered from Gensui, the posture is forced to the most restrictive level.</li>
              </ul>
            </div>

            {/* Quarantine */}
            <div className="glass-card p-5 space-y-4">
              <div className="flex items-center gap-2">
                <Trash2 size={18} className="text-purple-400" />
                <h3 className="text-lg font-bold text-gensui-100">Quarantine — Shogun Trash</h3>
              </div>
              <p className="text-xs text-gensui-400 leading-relaxed">Each Shogun instance includes a quarantine system (<code className="text-gensui-300 bg-gensui-800 px-1 py-0.5 rounded">.shogun_trash/</code>) that moves deleted files to a recoverable trash folder instead of permanently deleting them. Files can be recovered within 30 days. This protects against accidental or AI-initiated data loss.</p>
            </div>

            {/* Prompt Injection Containment */}
            <div className="glass-card p-5 space-y-4">
              <div className="flex items-center gap-2">
                <Lock size={18} className="text-red-400" />
                <h3 className="text-lg font-bold text-gensui-100">Prompt Injection Containment</h3>
              </div>
              <p className="text-xs text-gensui-400 leading-relaxed">When Shogun agents fetch external content (web pages, emails, calendar events), the content is wrapped with <strong className="text-amber-400">[UNTRUSTED EXTERNAL DATA]</strong> boundary markers. This prevents the LLM from following instructions embedded in external content (a common prompt injection attack vector). The wrapping is automatic and applies to all tools that return external data.</p>
            </div>

            {/* Audit & Compliance */}
            <div className="glass-card p-5 space-y-4">
              <div className="flex items-center gap-2">
                <FileSearch size={18} className="text-gensui-400" />
                <h3 className="text-lg font-bold text-gensui-100">Audit & Compliance</h3>
              </div>
              <p className="text-xs text-gensui-400 leading-relaxed">Every security decision — ToolGate allow/confirm/block/deny, posture changes, harakiri activations, token revocations — is logged to the HMAC-chained immutable audit trail. This provides cryptographically tamper-evident evidence for NIS2, SOC2, and EU AI Act compliance. The audit chain can be verified at any time to detect tampering.</p>
            </div>
          </section>

          {/* Fleet Audit Dashboard */}
          <section id="ref-fleet-audit" className="space-y-6">
            <div className="flex items-center gap-3 border-b border-gensui-700 pb-3">
              <BarChart3 size={28} className="text-cyan-400" />
              <div>
                <h2 className="text-2xl font-bold text-gensui-50">Fleet Audit Dashboard</h2>
                <p className="text-xs text-gensui-400">Multi-instance audit analytics, compliance reporting, and chain verification.</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><BarChart3 size={14} className="text-cyan-400" /> Overview Tab</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Fleet-wide statistics: total audit events, last 24h/7d counts, security-critical events (30d), HMAC chain integrity verification, action breakdown, and actor type distribution. A green or red banner shows chain integrity status.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Users size={14} className="text-emerald-400" /> Per Member Tab</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Audit and telemetry event counts per fleet member. Shows instance name, enrollment status, total audit/telemetry events, critical event count, and last event timestamp. Sorted by telemetry volume.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Activity size={14} className="text-amber-400" /> Telemetry Analytics Tab</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Aggregated telemetry breakdown by severity (info/warn/error/critical), category, event type (top 20), and per-member distribution. Filterable by date range and specific member.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Shield size={14} className="text-cyan-400" /> Compliance Tab</div>
                <p className="text-xs text-gensui-400 leading-relaxed">NIS2/SOC2/EU AI Act compliance report. Shows fleet size, harakiri activations, posture changes, enrollment events, token revocations, critical telemetry count, and HMAC chain integrity over the last 30 days.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><FileSearch size={14} className="text-gensui-400" /> Raw Log Tab</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Full audit log with action filtering. Shows timestamp, actor type, action, target, reason, and IP address. Supports up to 200 entries per query.</p>
              </div>
              <div className="glass-card p-4 space-y-2">
                <div className="font-semibold text-gensui-100 flex items-center gap-2 text-sm"><Copy size={14} className="text-purple-400" /> CSV Export</div>
                <p className="text-xs text-gensui-400 leading-relaxed">Export the full audit trail as a CSV file for offline analysis, compliance audits, or SIEM integration. Up to 50,000 entries per export.</p>
              </div>
            </div>
          </section>

          {/* Enterprise Identity */}
          <section id="ref-identity" className="space-y-6">
            <div className="flex items-center gap-3 border-b border-gensui-700 pb-3">
              <Key size={28} className="text-purple-400" />
              <div>
                <h2 className="text-2xl font-bold text-gensui-50">Enterprise Identity</h2>
                <p className="text-xs text-gensui-400">Service accounts, API keys, and SSO/OIDC configuration for enterprise environments.</p>
              </div>
            </div>

            {/* Service Accounts */}
            <div className="glass-card p-5 space-y-4">
              <div className="flex items-center gap-2">
                <Key size={18} className="text-amber-400" />
                <h3 className="text-lg font-bold text-gensui-100">Service Accounts &amp; API Keys</h3>
              </div>
              <p className="text-xs text-gensui-400 leading-relaxed">Service accounts provide machine-to-machine API authentication for CI/CD pipelines, SIEM integrations, monitoring systems, and custom automation. Each account has a unique API key (shown once on creation), a role, optional scopes, and rate limiting.</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="bg-gensui-800 border border-gensui-700 rounded-lg p-3 space-y-1">
                  <div className="text-xs font-bold text-gensui-200">API Key Format</div>
                  <p className="text-[11px] text-gensui-400"><code className="text-gensui-300 bg-gensui-900 px-1 rounded">gsk_</code> prefix + 48 random characters. HMAC-SHA256 hashed at rest. Key prefix stored for display identification.</p>
                </div>
                <div className="bg-gensui-800 border border-gensui-700 rounded-lg p-3 space-y-1">
                  <div className="text-xs font-bold text-gensui-200">Key Lifecycle</div>
                  <p className="text-[11px] text-gensui-400"><strong>Create</strong> &rarr; shown once. <strong>Rotate</strong> &rarr; invalidates old key, generates new. <strong>Revoke</strong> &rarr; permanently deactivates. All actions are audit-logged.</p>
                </div>
              </div>
              <div className="bg-gensui-800 border border-gensui-700 p-3 rounded-lg">
                <p className="text-xs text-gensui-400 leading-relaxed"><strong className="text-gensui-200">Roles:</strong> <span className="text-cyan-400">readonly</span> (read-only access), <span className="text-emerald-400">auditor</span> (audit + telemetry read), <span className="text-amber-400">operator</span> (fleet management), <span className="text-red-400">admin</span> (full access). Authenticate via <code className="text-gensui-300 bg-gensui-900 px-1 rounded">X-API-Key</code> header.</p>
              </div>
            </div>

            {/* SSO / OIDC */}
            <div className="glass-card p-5 space-y-4">
              <div className="flex items-center gap-2">
                <Globe size={18} className="text-purple-400" />
                <h3 className="text-lg font-bold text-gensui-100">SSO / OIDC Providers</h3>
              </div>
              <p className="text-xs text-gensui-400 leading-relaxed">Configure external identity providers for single sign-on. Gensui supports <strong>OpenID Connect</strong> (Keycloak, Auth0, Okta, Azure AD, Google), <strong>SAML 2.0</strong>, and <strong>SPIFFE/SPIRE</strong> trust domains. One provider can be marked as &ldquo;Primary&rdquo; to show an SSO button on the login page.</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div className="bg-gensui-800 border border-gensui-700 rounded-lg p-3 space-y-1">
                  <div className="text-xs font-bold text-gensui-200">OIDC Configuration</div>
                  <p className="text-[11px] text-gensui-400">Set issuer URL, client ID, client secret (encrypted at rest), scopes, and audience. Discovery URL is auto-derived from the issuer.</p>
                </div>
                <div className="bg-gensui-800 border border-gensui-700 rounded-lg p-3 space-y-1">
                  <div className="text-xs font-bold text-gensui-200">Role Mapping</div>
                  <p className="text-[11px] text-gensui-400">Map external IdP roles/groups to Gensui roles. Claim mapping extracts email, name, and role from OIDC tokens. Unmapped users receive the default role.</p>
                </div>
                <div className="bg-gensui-800 border border-gensui-700 rounded-lg p-3 space-y-1">
                  <div className="text-xs font-bold text-gensui-200">Auto-Provisioning</div>
                  <p className="text-[11px] text-gensui-400">Optionally auto-create Gensui admin accounts on first SSO login. Domain allowlisting restricts which email domains can register.</p>
                </div>
                <div className="bg-gensui-800 border border-gensui-700 rounded-lg p-3 space-y-1">
                  <div className="text-xs font-bold text-gensui-200">Security</div>
                  <p className="text-[11px] text-gensui-400">Client secrets are encrypted at rest. Token validation checks issuer, audience, and expiry. All SSO config changes are logged in the HMAC audit chain.</p>
                </div>
              </div>
            </div>
          </section>

        </div>
      </div>
    </div>
  );
}
