import { useState, useEffect, useCallback } from 'react';
import {
  AppWindow,
  Globe,
  Plus,
  Trash2,
  Camera,
  Download,
  RefreshCw,
  Loader2,
  CheckCircle2,
  XCircle,
  Monitor,
  MonitorOff,
  Image,
  Send,
  FileText,
  Settings2,
  Shield,
  X,
  ChevronLeft,
  ChevronRight,
  Maximize2,
} from 'lucide-react';
import axios from 'axios';
import { cn } from '../lib/utils';

// ═══════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════

interface SecurityPolicy {
  https_only: boolean;
  downloads: 'allowed' | 'blocked' | 'approval_required';
  uploads: 'allowed' | 'blocked' | 'approval_required';
  form_submit: 'allowed' | 'blocked' | 'approval_required';
  external_navigation: 'allowed' | 'blocked';
  js_execution: 'allowed' | 'blocked';
  max_page_loads: number;
}

const DEFAULT_POLICY: SecurityPolicy = {
  https_only: false,
  downloads: 'allowed',
  uploads: 'allowed',
  form_submit: 'allowed',
  external_navigation: 'allowed',
  js_execution: 'allowed',
  max_page_loads: 0,
};

interface MadoSession {
  id: string;
  name: string;
  profile_name: string;
  agent_id: string | null;
  status: string;
  browser_mode: string;
  last_url: string | null;
  domain_allowlist: string[];
  security_policy: SecurityPolicy;
  last_active_at: string | null;
  created_at: string;
}

interface MadoStatus {
  installed: boolean;
  version: string | null;
  active_sessions: number;
  mado_path: string;
  profiles_path: string;
  screenshots_path: string;
  downloads_path: string;
}

interface Screenshot {
  filename: string;
  path: string;
  size_bytes: number;
  created_at: string;
}

// ═══════════════════════════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════════════════════════

const ACCENT = '#06b6d4';  // Mado cyan
const TABS = ['Sessions', 'Quick Actions', 'Screenshots', 'Settings'] as const;
type Tab = typeof TABS[number];

const statusColors: Record<string, { bg: string; text: string; dot: string }> = {
  idle:   { bg: 'rgba(6,182,212,0.08)', text: '#06b6d4', dot: '#06b6d4' },
  active: { bg: 'rgba(34,197,94,0.08)', text: '#22c55e', dot: '#22c55e' },
  error:  { bg: 'rgba(239,68,68,0.08)', text: '#ef4444', dot: '#ef4444' },
  closed: { bg: 'rgba(122,136,153,0.08)', text: '#7a8899', dot: '#7a8899' },
};


// ═══════════════════════════════════════════════════════════════
// MADO PAGE
// ═══════════════════════════════════════════════════════════════

export function Mado() {
  const [tab, setTab] = useState<Tab>('Sessions');
  const [status, setStatus] = useState<MadoStatus | null>(null);
  const [sessions, setSessions] = useState<MadoSession[]>([]);
  const [screenshots, setScreenshots] = useState<Screenshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [installing, setInstalling] = useState(false);
  const [installMessage, setInstallMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Create session modal
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState('');
  const [newProfile, setNewProfile] = useState('');
  const [newMode, setNewMode] = useState<'headless' | 'visible'>('headless');
  const [creating, setCreating] = useState(false);
  const [showPolicySection, setShowPolicySection] = useState(false);
  const [newPolicy, setNewPolicy] = useState<SecurityPolicy>({ ...DEFAULT_POLICY });
  const [newDomainAllowlist, setNewDomainAllowlist] = useState('');

  // Edit policy modal
  const [editPolicySession, setEditPolicySession] = useState<MadoSession | null>(null);
  const [editPolicy, setEditPolicy] = useState<SecurityPolicy>({ ...DEFAULT_POLICY });
  const [savingPolicy, setSavingPolicy] = useState(false);

  // Screenshot lightbox
  const [lightboxIndex, setLightboxIndex] = useState<number | null>(null);

  // Quick action state
  const [quickUrl, setQuickUrl] = useState('');
  const [quickSessionId, setQuickSessionId] = useState('');
  const [quickResult, setQuickResult] = useState<string | null>(null);
  const [quickLoading, setQuickLoading] = useState(false);

  // Extract presets (mirrors Agent Flow Mado node)
  const EXTRACT_PRESETS = [
    { value: 'headlines',    label: '📰 All Headlines',       selector: 'h1, h2, h3, h4, article h2, article h3',         desc: 'Grabs all headline text from the page' },
    { value: 'links',        label: '🔗 All Links',           selector: 'a[href]',                                        desc: 'Extracts every link on the page with its URL' },
    { value: 'article',      label: '📄 Article Content',     selector: 'article, [role="article"], .post-content, .entry-content, .article-body, main', desc: 'Main article text and body content' },
    { value: 'news_cards',   label: '🗞️ News Cards',          selector: 'article a, [data-n-tid] a, c-wiz article, [jslog] h3, [jslog] h4', desc: 'News feed cards (Google News, news aggregators)' },
    { value: 'tables',       label: '📊 Tables & Data',       selector: 'table, [role="table"], .data-table',             desc: 'Structured tables and data grids' },
    { value: 'images',       label: '🖼️ Images',              selector: 'img[src], picture source',                       desc: 'All images with their source URLs' },
    { value: 'lists',        label: '📋 Lists',               selector: 'ul, ol, dl, [role="list"]',                      desc: 'Bullet points, numbered lists, and definition lists' },
    { value: 'prices',       label: '💰 Prices & Products',   selector: '[class*="price"], [data-price], .product-card, .product-title', desc: 'Product names, prices, and e-commerce data' },
    { value: 'full_page',    label: '📜 Full Page Text',      selector: 'body',                                           desc: 'Everything visible on the page' },
    { value: 'custom',       label: '⚙️ Custom Selector',     selector: '',                                               desc: 'Write your own CSS selector' },
  ];
  const [extractPreset, setExtractPreset] = useState('');
  const [extractSelector, setExtractSelector] = useState('');
  const [extractHint, setExtractHint] = useState('');
  const [showAdvancedSelector, setShowAdvancedSelector] = useState(false);

  // ── Data loading ──────────────────────────────────────────

  const loadStatus = useCallback(async () => {
    try {
      const r = await axios.get('/api/v1/mado/status');
      setStatus(r.data?.data);
    } catch { /* ignore */ }
  }, []);

  const loadSessions = useCallback(async () => {
    try {
      const r = await axios.get('/api/v1/mado/sessions');
      setSessions(r.data?.data || []);
    } catch { /* ignore */ }
  }, []);

  const loadScreenshots = useCallback(async () => {
    try {
      const r = await axios.get('/api/v1/mado/screenshots');
      setScreenshots(r.data?.data || []);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => {
    Promise.all([loadStatus(), loadSessions(), loadScreenshots()])
      .finally(() => setLoading(false));
  }, [loadStatus, loadSessions, loadScreenshots]);

  // ── Actions ───────────────────────────────────────────────

  const installChromium = async () => {
    setInstalling(true);
    setInstallMessage(null);
    try {
      const r = await axios.post('/api/v1/mado/install');
      const data = r.data?.data;
      if (data?.success) {
        setInstallMessage({ type: 'success', text: 'Chromium installed successfully! Browser engine is ready.' });
      } else {
        const errDetail = data?.error || data?.stderr || 'Unknown error';
        setInstallMessage({ type: 'error', text: `Install failed: ${errDetail.slice(0, 200)}` });
      }
      await loadStatus();
    } catch (err: any) {
      setInstallMessage({ type: 'error', text: `Install request failed: ${err.message || 'Network error'}` });
    }
    setInstalling(false);
    // Auto-clear success message
    setTimeout(() => setInstallMessage(null), 8000);
  };

  const createSession = async () => {
    if (!newName.trim() || !newProfile.trim()) return;
    setCreating(true);
    try {
      const domains = newDomainAllowlist.split(',').map(d => d.trim()).filter(Boolean);
      await axios.post('/api/v1/mado/sessions', {
        name: newName,
        profile_name: newProfile.replace(/\s+/g, '_').toLowerCase(),
        browser_mode: newMode,
        domain_allowlist: domains,
        security_policy: newPolicy,
      });
      await loadSessions();
      setShowCreate(false);
      setNewName('');
      setNewProfile('');
      setNewDomainAllowlist('');
      setNewPolicy({ ...DEFAULT_POLICY });
      setShowPolicySection(false);
    } catch { /* ignore */ }
    setCreating(false);
  };

  const openEditPolicy = (s: MadoSession) => {
    setEditPolicySession(s);
    setEditPolicy(s.security_policy ? { ...DEFAULT_POLICY, ...s.security_policy } : { ...DEFAULT_POLICY });
  };

  const savePolicy = async () => {
    if (!editPolicySession) return;
    setSavingPolicy(true);
    try {
      await axios.patch(`/api/v1/mado/sessions/${editPolicySession.id}/policy`, editPolicy);
      await loadSessions();
      setEditPolicySession(null);
    } catch { /* ignore */ }
    setSavingPolicy(false);
  };

  const deleteSession = async (id: string) => {
    try {
      await axios.delete(`/api/v1/mado/sessions/${id}`);
      await loadSessions();
    } catch { /* ignore */ }
  };

  const quickNavigate = async () => {
    if (!quickUrl.trim() || !quickSessionId) return;
    setQuickLoading(true);
    setQuickResult(null);
    try {
      const r = await axios.post(`/api/v1/mado/sessions/${quickSessionId}/navigate`, {
        url: quickUrl,
      });
      setQuickResult(`✅ ${r.data?.data?.title || 'Navigated'} — ${r.data?.data?.url || quickUrl}`);
      await loadSessions();
    } catch (err: any) {
      setQuickResult(`❌ ${err.response?.data?.detail || 'Navigation failed'}`);
    }
    setQuickLoading(false);
  };

  const quickScreenshot = async () => {
    if (!quickSessionId) return;
    setQuickLoading(true);
    try {
      const r = await axios.post(`/api/v1/mado/sessions/${quickSessionId}/screenshot`);
      setQuickResult(`📸 Screenshot saved: ${r.data?.data?.filename || 'unknown'}`);
      await loadScreenshots();
    } catch (err: any) {
      setQuickResult(`❌ ${err.response?.data?.detail || 'Screenshot failed'}`);
    }
    setQuickLoading(false);
  };

  const quickExtract = async () => {
    if (!quickSessionId) return;
    setQuickLoading(true);
    try {
      const selectorToUse = extractSelector || undefined;
      const r = await axios.post(`/api/v1/mado/sessions/${quickSessionId}/extract`, {
        extract_type: 'text',
        selector: selectorToUse,
      });
      let content = r.data?.data?.content || '';
      if (extractHint) {
        content = `[Extract hint: ${extractHint}]\n\n${content}`;
      }
      setQuickResult(content.slice(0, 5000) + (content.length > 5000 ? '\n\n... [truncated]' : ''));
    } catch (err: any) {
      setQuickResult(`❌ ${err.response?.data?.detail || 'Extraction failed'}`);
    }
    setQuickLoading(false);
  };

  // ── Render ────────────────────────────────────────────────

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center bg-[#0a0e1a]">
        <Loader2 className="w-8 h-8 animate-spin" style={{ color: ACCENT }} />
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-[#0a0e1a] overflow-hidden">
      {/* ── Header ──────────────────────────────────────────── */}
      <div className="px-6 py-5 border-b border-[#1a2040] flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-xl flex items-center justify-center"
            style={{ background: `${ACCENT}12`, border: `1px solid ${ACCENT}30` }}
          >
            <AppWindow className="w-5 h-5" style={{ color: ACCENT }} />
          </div>
          <div>
            <h1 className="text-lg font-bold text-[#c8d0d8] tracking-tight">Mado</h1>
            <p className="text-[10px] text-[#7a8899] uppercase tracking-widest font-bold">窓 — Browser Automation Layer</p>
          </div>
        </div>

        {/* Status badge */}
        <div className="flex items-center gap-3">
          {status?.installed ? (
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#22c55e]/8 border border-[#22c55e]/20">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#22c55e]" />
              <span className="text-[10px] font-bold text-[#22c55e] uppercase tracking-wider">Chromium Ready</span>
              {status.version && (
                <span className="text-[8px] text-[#22c55e]/60 font-mono">{status.version}</span>
              )}
            </div>
          ) : (
            <button
              onClick={installChromium}
              disabled={installing}
              className="flex items-center gap-2 px-4 py-2 rounded-lg border transition-all duration-200 cursor-pointer disabled:opacity-50"
              style={{
                background: installing ? '#0e1225' : `${ACCENT}10`,
                borderColor: installing ? '#1a2040' : `${ACCENT}40`,
                color: installing ? '#7a8899' : ACCENT,
              }}
            >
              {installing ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Download className="w-3.5 h-3.5" />
              )}
              <span className="text-[10px] font-bold uppercase tracking-wider">
                {installing ? 'Installing...' : 'Install Chromium'}
              </span>
            </button>
          )}

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0e1225] border border-[#1a2040]">
            <div className="w-2 h-2 rounded-full" style={{ background: status?.active_sessions ? '#22c55e' : '#7a8899' }} />
            <span className="text-[10px] font-bold text-[#7a8899] uppercase tracking-wider">
              {status?.active_sessions || 0} Active
            </span>
          </div>
        </div>
      </div>

      {/* ── Install progress overlay ────────────────────────── */}
      {installing && (
        <div className="px-6 py-4 bg-[#0e1225] border-b border-[#1a2040] flex items-center gap-4">
          <div className="relative w-8 h-8 shrink-0">
            <div className="absolute inset-0 rounded-full border-2 border-[#1a2040]" />
            <div className="absolute inset-0 rounded-full border-2 border-t-[#06b6d4] animate-spin" />
          </div>
          <div className="flex-1">
            <p className="text-xs font-bold text-[#c8d0d8]">Installing Mado Browser Engine</p>
            <p className="text-[10px] text-[#7a8899] mt-0.5">
              Downloading Playwright + Chromium browser. This may take 1–2 minutes...
            </p>
          </div>
          <div className="text-[9px] font-mono text-[#555] uppercase tracking-wider">
            Please wait
          </div>
        </div>
      )}

      {/* ── Install result banner ───────────────────────────── */}
      {installMessage && !installing && (
        <div className={cn(
          "px-6 py-3 flex items-center gap-2 text-xs font-bold",
          installMessage.type === 'success'
            ? "bg-[#22c55e]/10 text-[#22c55e] border-b border-[#22c55e]/20"
            : "bg-[#ef4444]/10 text-[#ef4444] border-b border-[#ef4444]/20"
        )}>
          {installMessage.type === 'success'
            ? <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
            : <XCircle className="w-3.5 h-3.5 shrink-0" />
          }
          <span>{installMessage.text}</span>
        </div>
      )}

      {/* ── Tabs ────────────────────────────────────────────── */}
      <div className="px-6 pt-3 flex items-center gap-1 border-b border-[#1a2040]">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={cn(
              "px-4 py-2.5 text-[11px] font-bold uppercase tracking-wider transition-all duration-200 border-b-2 -mb-px",
              tab === t
                ? "border-[#06b6d4] text-[#06b6d4]"
                : "border-transparent text-[#7a8899] hover:text-[#c8d0d8]"
            )}
          >
            {t}
          </button>
        ))}
      </div>

      {/* ── Content ─────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto p-6">
        {tab === 'Sessions' && (
          <div className="space-y-4">
            {/* Create button */}
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-bold text-[#7a8899] uppercase tracking-widest">Browser Sessions</h2>
              <button
                onClick={() => setShowCreate(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all duration-200 cursor-pointer"
                style={{
                  background: `${ACCENT}12`,
                  border: `1px solid ${ACCENT}30`,
                  color: ACCENT,
                }}
              >
                <Plus className="w-3 h-3" />
                New Session
              </button>
            </div>

            {/* Session list */}
            {sessions.length === 0 ? (
              <div className="text-center py-16 space-y-3">
                <AppWindow className="w-12 h-12 mx-auto" style={{ color: `${ACCENT}40` }} />
                <p className="text-sm text-[#7a8899]">No browser sessions yet</p>
                <p className="text-xs text-[#555]">Create a session to start browsing</p>
              </div>
            ) : (
              <div className="grid gap-3">
                {sessions.map((s) => {
                  const sc = statusColors[s.status] || statusColors.idle;
                  return (
                    <div
                      key={s.id}
                      className="group bg-[#0e1225] border border-[#1a2040] rounded-xl p-4 flex items-center gap-4 hover:border-[#2a3060] transition-all duration-200"
                    >
                      {/* Status dot */}
                      <div
                        className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
                        style={{ background: sc.bg }}
                      >
                        {s.browser_mode === 'headless' ? (
                          <MonitorOff className="w-4.5 h-4.5" style={{ color: sc.text }} />
                        ) : (
                          <Monitor className="w-4.5 h-4.5" style={{ color: sc.text }} />
                        )}
                      </div>

                      {/* Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <h3 className="text-sm font-bold text-[#c8d0d8] truncate">{s.name}</h3>
                          <span
                            className="text-[8px] font-bold uppercase tracking-widest px-1.5 py-0.5 rounded"
                            style={{ background: sc.bg, color: sc.text }}
                          >
                            {s.status}
                          </span>
                        </div>
                        <div className="flex items-center gap-3 mt-1">
                          <span className="text-[9px] text-[#555] font-mono">{s.profile_name}</span>
                          <span className="text-[9px] text-[#555]">•</span>
                          <span className="text-[9px] text-[#555]">{s.browser_mode}</span>
                        </div>
                        {s.last_url && (
                          <div className="flex items-center gap-1 mt-1">
                            <Globe className="w-2.5 h-2.5 text-[#555]" />
                            <span className="text-[9px] text-[#06b6d4]/70 truncate max-w-[400px]">{s.last_url}</span>
                          </div>
                        )}
                        {/* Policy badge */}
                        {s.security_policy && (() => {
                          const p = { ...DEFAULT_POLICY, ...s.security_policy };
                          const badges: string[] = [];
                          if (p.https_only) badges.push('HTTPS');
                          if ((s.domain_allowlist?.length || 0) > 0) badges.push(`${s.domain_allowlist.length} domain${s.domain_allowlist.length > 1 ? 's' : ''}`);
                          if (p.downloads === 'blocked') badges.push('No DL');
                          if (p.uploads === 'blocked') badges.push('No UL');
                          if (p.form_submit === 'blocked') badges.push('No forms');
                          if (p.external_navigation === 'blocked') badges.push('Locked nav');
                          if (p.js_execution === 'blocked') badges.push('No JS');
                          if (p.max_page_loads > 0) badges.push(`${p.max_page_loads} loads`);
                          if (badges.length === 0) return null;
                          return (
                            <div className="flex items-center gap-1 mt-1">
                              <Shield className="w-2.5 h-2.5 text-[#06b6d4]/50" />
                              <span className="text-[8px] text-[#06b6d4]/50 font-mono">{badges.join(' · ')}</span>
                            </div>
                          );
                        })()}
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => openEditPolicy(s)}
                          className="p-1.5 hover:bg-[#06b6d4]/10 text-[#7a8899] hover:text-[#06b6d4] rounded-lg transition-colors cursor-pointer"
                          title="Edit security policy"
                        >
                          <Shield className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => deleteSession(s.id)}
                          className="p-1.5 hover:bg-[#ef4444]/10 text-[#7a8899] hover:text-[#ef4444] rounded-lg transition-colors cursor-pointer"
                          title="Delete session"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {/* Create session modal */}
            {showCreate && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
                <div className="bg-[#0e1225] border border-[#1a2040] rounded-2xl w-[440px] shadow-2xl overflow-hidden">
                  <div className="p-5 border-b border-[#1a2040] flex items-center gap-3">
                    <div
                      className="w-8 h-8 rounded-lg flex items-center justify-center"
                      style={{ background: `${ACCENT}15`, border: `1px solid ${ACCENT}30` }}
                    >
                      <Plus className="w-4 h-4" style={{ color: ACCENT }} />
                    </div>
                    <h3 className="text-sm font-bold text-[#c8d0d8]">New Browser Session</h3>
                  </div>
                  <div className="p-5 space-y-4">
                    <div className="space-y-1.5">
                      <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Session Name</label>
                      <input
                        value={newName}
                        onChange={(e) => setNewName(e.target.value)}
                        className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2.5 text-xs text-[#c8d0d8] focus:border-[#06b6d4] transition-colors outline-none"
                        placeholder="e.g., Research Browser"
                      />
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Profile Name</label>
                      <input
                        value={newProfile}
                        onChange={(e) => setNewProfile(e.target.value)}
                        className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2.5 text-xs text-[#c8d0d8] focus:border-[#06b6d4] transition-colors outline-none"
                        placeholder="e.g., research_agent"
                      />
                      <p className="text-[8px] text-[#555]">Unique filesystem name for persistent profile storage</p>
                    </div>
                    <div className="space-y-1.5">
                      <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Browser Mode</label>
                      <div className="flex gap-2">
                        {(['headless', 'visible'] as const).map((mode) => (
                          <button
                            key={mode}
                            onClick={() => setNewMode(mode)}
                            className={cn(
                              "flex-1 flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg border text-[10px] font-bold uppercase tracking-wider transition-all cursor-pointer",
                              newMode === mode
                                ? "border-[#06b6d4] bg-[#06b6d4]/10 text-[#06b6d4]"
                                : "border-[#1a2040] text-[#7a8899] hover:border-[#2a3060]"
                            )}
                          >
                            {mode === 'headless' ? <MonitorOff className="w-3.5 h-3.5" /> : <Monitor className="w-3.5 h-3.5" />}
                            {mode}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* ▶ Security Policy (collapsible) */}
                    <button
                      type="button"
                      onClick={() => setShowPolicySection(!showPolicySection)}
                      className="flex items-center gap-1.5 text-[9px] font-bold text-[#7a8899] hover:text-[#c8d0d8] uppercase tracking-widest transition-colors cursor-pointer mt-1"
                    >
                      <Shield className="w-3 h-3" />
                      <span className="transition-transform" style={{ transform: showPolicySection ? 'rotate(90deg)' : 'rotate(0deg)' }}>▶</span>
                      Security Policy
                    </button>

                    {showPolicySection && (
                      <div className="space-y-3 pl-1 border-l-2 border-[#1a2040] ml-1">
                        {/* Allowed Domains */}
                        <div className="space-y-1 pl-3">
                          <label className="text-[8px] font-bold text-[#7a8899] uppercase tracking-widest">Allowed Domains</label>
                          <input
                            value={newDomainAllowlist}
                            onChange={(e) => setNewDomainAllowlist(e.target.value)}
                            className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2 text-[10px] text-[#c8d0d8] focus:border-[#06b6d4] transition-colors outline-none font-mono"
                            placeholder="e.g., github.com, google.com"
                          />
                          <p className="text-[7px] text-[#555]">Comma-separated list. Leave empty to allow all domains.</p>
                        </div>

                        {/* HTTPS Only */}
                        <div className="flex items-center justify-between pl-3">
                          <label className="text-[8px] font-bold text-[#7a8899] uppercase tracking-widest">HTTPS Only</label>
                          <button
                            type="button"
                            onClick={() => setNewPolicy(p => ({ ...p, https_only: !p.https_only }))}
                            className={cn(
                              "w-8 h-4 rounded-full transition-colors cursor-pointer relative",
                              newPolicy.https_only ? "bg-[#06b6d4]" : "bg-[#1a2040]"
                            )}
                          >
                            <span className={cn(
                              "absolute top-0.5 w-3 h-3 rounded-full bg-white transition-transform",
                              newPolicy.https_only ? "translate-x-4" : "translate-x-0.5"
                            )} />
                          </button>
                        </div>

                        {/* Tri-state dropdowns */}
                        {([
                          ['downloads', 'Downloads'] as const,
                          ['uploads', 'Uploads'] as const,
                          ['form_submit', 'Form Submission'] as const,
                        ] as const).map(([key, label]) => (
                          <div key={key} className="flex items-center justify-between pl-3">
                            <label className="text-[8px] font-bold text-[#7a8899] uppercase tracking-widest">{label}</label>
                            <select
                              value={newPolicy[key]}
                              onChange={(e) => setNewPolicy(p => ({ ...p, [key]: e.target.value }))}
                              className="bg-[#0a0e1a] border border-[#1a2040] rounded-md px-2 py-1 text-[9px] text-[#c8d0d8] focus:border-[#06b6d4] transition-colors outline-none cursor-pointer"
                            >
                              <option value="allowed">✅ Allowed</option>
                              <option value="blocked">🚫 Blocked</option>
                              <option value="approval_required">⏳ Approval Required</option>
                            </select>
                          </div>
                        ))}

                        {/* Binary toggles */}
                        {([
                          ['external_navigation', 'External Navigation'] as const,
                          ['js_execution', 'JS Execution'] as const,
                        ] as const).map(([key, label]) => (
                          <div key={key} className="flex items-center justify-between pl-3">
                            <label className="text-[8px] font-bold text-[#7a8899] uppercase tracking-widest">{label}</label>
                            <select
                              value={newPolicy[key]}
                              onChange={(e) => setNewPolicy(p => ({ ...p, [key]: e.target.value }))}
                              className="bg-[#0a0e1a] border border-[#1a2040] rounded-md px-2 py-1 text-[9px] text-[#c8d0d8] focus:border-[#06b6d4] transition-colors outline-none cursor-pointer"
                            >
                              <option value="allowed">✅ Allowed</option>
                              <option value="blocked">🚫 Blocked</option>
                            </select>
                          </div>
                        ))}

                        {/* Max Page Loads */}
                        <div className="flex items-center justify-between pl-3">
                          <label className="text-[8px] font-bold text-[#7a8899] uppercase tracking-widest">Max Page Loads</label>
                          <input
                            type="number"
                            min={0}
                            value={newPolicy.max_page_loads}
                            onChange={(e) => setNewPolicy(p => ({ ...p, max_page_loads: Math.max(0, parseInt(e.target.value) || 0) }))}
                            className="w-16 bg-[#0a0e1a] border border-[#1a2040] rounded-md px-2 py-1 text-[9px] text-[#c8d0d8] text-center focus:border-[#06b6d4] transition-colors outline-none"
                            placeholder="0"
                          />
                        </div>
                        <p className="text-[7px] text-[#555] pl-3">0 = unlimited navigations</p>
                      </div>
                    )}
                  </div>
                  <div className="px-5 py-3 border-t border-[#1a2040] flex items-center justify-end gap-2">
                    <button
                      onClick={() => setShowCreate(false)}
                      className="px-4 py-2 text-[10px] font-bold uppercase tracking-wider text-[#7a8899] hover:text-[#c8d0d8] transition-colors cursor-pointer"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={createSession}
                      disabled={creating || !newName.trim() || !newProfile.trim()}
                      className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all cursor-pointer disabled:opacity-40"
                      style={{ background: ACCENT, color: '#0a0e1a' }}
                    >
                      {creating ? <Loader2 className="w-3 h-3 animate-spin" /> : <Plus className="w-3 h-3" />}
                      Create
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Edit Policy Modal */}
            {editPolicySession && (
              <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
                <div className="bg-[#0e1225] border border-[#1a2040] rounded-2xl w-[440px] shadow-2xl overflow-hidden max-h-[80vh] flex flex-col">
                  <div className="p-5 border-b border-[#1a2040] flex items-center gap-3">
                    <div
                      className="w-8 h-8 rounded-lg flex items-center justify-center"
                      style={{ background: `${ACCENT}15`, border: `1px solid ${ACCENT}30` }}
                    >
                      <Shield className="w-4 h-4" style={{ color: ACCENT }} />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-[#c8d0d8]">Security Policy</h3>
                      <p className="text-[9px] text-[#555]">{editPolicySession.name}</p>
                    </div>
                  </div>
                  <div className="p-5 space-y-3 overflow-y-auto">
                    {/* HTTPS Only */}
                    <div className="flex items-center justify-between">
                      <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">HTTPS Only</label>
                      <button
                        type="button"
                        onClick={() => setEditPolicy(p => ({ ...p, https_only: !p.https_only }))}
                        className={cn(
                          "w-8 h-4 rounded-full transition-colors cursor-pointer relative",
                          editPolicy.https_only ? "bg-[#06b6d4]" : "bg-[#1a2040]"
                        )}
                      >
                        <span className={cn(
                          "absolute top-0.5 w-3 h-3 rounded-full bg-white transition-transform",
                          editPolicy.https_only ? "translate-x-4" : "translate-x-0.5"
                        )} />
                      </button>
                    </div>

                    {/* Tri-state dropdowns */}
                    {([
                      ['downloads', 'Downloads'] as const,
                      ['uploads', 'Uploads'] as const,
                      ['form_submit', 'Form Submission'] as const,
                    ] as const).map(([key, label]) => (
                      <div key={key} className="flex items-center justify-between">
                        <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">{label}</label>
                        <select
                          value={editPolicy[key]}
                          onChange={(e) => setEditPolicy(p => ({ ...p, [key]: e.target.value }))}
                          className="bg-[#0a0e1a] border border-[#1a2040] rounded-md px-2 py-1 text-[9px] text-[#c8d0d8] focus:border-[#06b6d4] transition-colors outline-none cursor-pointer"
                        >
                          <option value="allowed">✅ Allowed</option>
                          <option value="blocked">🚫 Blocked</option>
                          <option value="approval_required">⏳ Approval Required</option>
                        </select>
                      </div>
                    ))}

                    {/* Binary toggles */}
                    {([
                      ['external_navigation', 'External Navigation'] as const,
                      ['js_execution', 'JS Execution'] as const,
                    ] as const).map(([key, label]) => (
                      <div key={key} className="flex items-center justify-between">
                        <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">{label}</label>
                        <select
                          value={editPolicy[key]}
                          onChange={(e) => setEditPolicy(p => ({ ...p, [key]: e.target.value }))}
                          className="bg-[#0a0e1a] border border-[#1a2040] rounded-md px-2 py-1 text-[9px] text-[#c8d0d8] focus:border-[#06b6d4] transition-colors outline-none cursor-pointer"
                        >
                          <option value="allowed">✅ Allowed</option>
                          <option value="blocked">🚫 Blocked</option>
                        </select>
                      </div>
                    ))}

                    {/* Max Page Loads */}
                    <div className="flex items-center justify-between">
                      <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Max Page Loads</label>
                      <input
                        type="number"
                        min={0}
                        value={editPolicy.max_page_loads}
                        onChange={(e) => setEditPolicy(p => ({ ...p, max_page_loads: Math.max(0, parseInt(e.target.value) || 0) }))}
                        className="w-16 bg-[#0a0e1a] border border-[#1a2040] rounded-md px-2 py-1 text-[9px] text-[#c8d0d8] text-center focus:border-[#06b6d4] transition-colors outline-none"
                        placeholder="0"
                      />
                    </div>
                    <p className="text-[7px] text-[#555]">0 = unlimited navigations</p>
                  </div>
                  <div className="px-5 py-3 border-t border-[#1a2040] flex items-center justify-end gap-2">
                    <button
                      onClick={() => setEditPolicySession(null)}
                      className="px-4 py-2 text-[10px] font-bold uppercase tracking-wider text-[#7a8899] hover:text-[#c8d0d8] transition-colors cursor-pointer"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={savePolicy}
                      disabled={savingPolicy}
                      className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all cursor-pointer disabled:opacity-40"
                      style={{ background: ACCENT, color: '#0a0e1a' }}
                    >
                      {savingPolicy ? <Loader2 className="w-3 h-3 animate-spin" /> : <Shield className="w-3 h-3" />}
                      Save Policy
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {tab === 'Quick Actions' && (
          <div className="max-w-2xl mx-auto space-y-6">
            <div className="space-y-1">
              <h2 className="text-xs font-bold text-[#7a8899] uppercase tracking-widest">Quick Browser Commands</h2>
              <p className="text-[10px] text-[#555]">Execute browser actions directly without Agent Flow</p>
            </div>

            {/* Session selector */}
            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Active Session</label>
              <select
                value={quickSessionId}
                onChange={(e) => setQuickSessionId(e.target.value)}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2.5 text-xs text-[#c8d0d8] focus:border-[#06b6d4] transition-colors outline-none cursor-pointer"
              >
                <option value="">Select a session...</option>
                {sessions.map((s) => (
                  <option key={s.id} value={s.id}>{s.name} ({s.status})</option>
                ))}
              </select>
            </div>

            {/* URL + Navigate */}
            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Navigate to URL</label>
              <div className="flex gap-2">
                <input
                  value={quickUrl}
                  onChange={(e) => setQuickUrl(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && quickNavigate()}
                  className="flex-1 bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2.5 text-xs text-[#c8d0d8] focus:border-[#06b6d4] transition-colors outline-none"
                  placeholder="https://example.com"
                />
                <button
                  onClick={quickNavigate}
                  disabled={quickLoading || !quickSessionId || !quickUrl.trim()}
                  className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all cursor-pointer disabled:opacity-40"
                  style={{ background: ACCENT, color: '#0a0e1a' }}
                >
                  {quickLoading ? <Loader2 className="w-3 h-3 animate-spin" /> : <Send className="w-3 h-3" />}
                  Go
                </button>
              </div>
            </div>

            {/* What to Extract — preset dropdown */}
            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">What to Extract</label>
              <select
                value={extractPreset}
                onChange={(e) => {
                  const preset = EXTRACT_PRESETS.find(p => p.value === e.target.value);
                  setExtractPreset(e.target.value);
                  if (preset && preset.value !== 'custom') {
                    setExtractSelector(preset.selector);
                    setShowAdvancedSelector(false);
                  } else if (preset?.value === 'custom') {
                    setShowAdvancedSelector(true);
                  } else {
                    setExtractSelector('');
                  }
                }}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2.5 text-xs text-[#c8d0d8] focus:border-[#06b6d4] transition-colors outline-none cursor-pointer"
              >
                <option value="">— Choose what to extract —</option>
                {EXTRACT_PRESETS.map(p => (
                  <option key={p.value} value={p.value}>{p.label}</option>
                ))}
              </select>
              {extractPreset && extractPreset !== 'custom' && (() => {
                const cur = EXTRACT_PRESETS.find(p => p.value === extractPreset);
                return cur ? <p className="text-[8px] text-[#06b6d4]/70">{cur.desc}</p> : null;
              })()}
            </div>

            {/* Describe What You Need */}
            <div className="space-y-1.5">
              <label className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest">Describe What You Need</label>
              <textarea
                value={extractHint}
                onChange={(e) => setExtractHint(e.target.value)}
                rows={2}
                className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2.5 text-xs text-[#c8d0d8] focus:border-[#06b6d4] transition-colors outline-none resize-y min-h-[40px]"
                placeholder='e.g. "Get all article titles and their links" or "Find product prices"'
              />
              <p className="text-[8px] text-[#555]">Optional — helps the AI understand what to look for in the extracted content</p>
            </div>

            {/* Advanced: CSS Selector toggle */}
            <button
              type="button"
              onClick={() => setShowAdvancedSelector(!showAdvancedSelector)}
              className="flex items-center gap-1.5 text-[8px] font-bold text-[#555] hover:text-[#7a8899] uppercase tracking-widest transition-colors cursor-pointer"
            >
              <span className="transition-transform" style={{ transform: showAdvancedSelector ? 'rotate(90deg)' : 'rotate(0deg)' }}>▶</span>
              Advanced: CSS Selector
            </button>

            {showAdvancedSelector && (
              <div className="space-y-1.5">
                <input
                  type="text"
                  value={extractSelector}
                  onChange={(e) => {
                    setExtractSelector(e.target.value);
                    setExtractPreset('custom');
                  }}
                  className="w-full bg-[#0a0e1a] border border-[#1a2040] rounded-lg p-2.5 text-[10px] text-[#06b6d4] font-mono focus:border-[#06b6d4] transition-colors outline-none"
                  placeholder="e.g., .main-content, #article, table"
                />
                <p className="text-[8px] text-[#555]">Raw CSS selector — for power users who know the page structure</p>
              </div>
            )}

            {/* Action buttons */}
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={quickScreenshot}
                disabled={quickLoading || !quickSessionId}
                className="flex items-center justify-center gap-2 p-3 bg-[#0e1225] border border-[#1a2040] rounded-xl text-[10px] font-bold text-[#c8d0d8] uppercase tracking-wider hover:border-[#06b6d4]/40 transition-all cursor-pointer disabled:opacity-40"
              >
                <Camera className="w-4 h-4" style={{ color: ACCENT }} />
                Screenshot
              </button>
              <button
                onClick={quickExtract}
                disabled={quickLoading || !quickSessionId}
                className="flex items-center justify-center gap-2 p-3 bg-[#0e1225] border border-[#1a2040] rounded-xl text-[10px] font-bold text-[#c8d0d8] uppercase tracking-wider hover:border-[#06b6d4]/40 transition-all cursor-pointer disabled:opacity-40"
              >
                <FileText className="w-4 h-4" style={{ color: ACCENT }} />
                Extract Text
              </button>
            </div>

            {/* Result */}
            {quickResult && (
              <div className="bg-[#0e1225] border border-[#1a2040] rounded-xl p-4">
                <div className="text-[9px] font-bold text-[#7a8899] uppercase tracking-widest mb-2">Result</div>
                <pre className="text-xs text-[#c8d0d8] whitespace-pre-wrap font-mono max-h-[400px] overflow-y-auto leading-relaxed">
                  {quickResult}
                </pre>
              </div>
            )}
          </div>
        )}

        {tab === 'Screenshots' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-bold text-[#7a8899] uppercase tracking-widest">Captured Screenshots</h2>
              <button
                onClick={loadScreenshots}
                className="p-1.5 hover:bg-[#1a2040] text-[#7a8899] hover:text-[#c8d0d8] rounded-lg transition-colors cursor-pointer"
              >
                <RefreshCw className="w-3.5 h-3.5" />
              </button>
            </div>

            {screenshots.length === 0 ? (
              <div className="text-center py-16 space-y-3">
                <Image className="w-12 h-12 mx-auto" style={{ color: `${ACCENT}40` }} />
                <p className="text-sm text-[#7a8899]">No screenshots yet</p>
                <p className="text-xs text-[#555]">Take a screenshot from Quick Actions or Agent Flow</p>
              </div>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                {screenshots.map((ss, idx) => (
                  <button
                    key={ss.filename}
                    onClick={() => setLightboxIndex(idx)}
                    className="bg-[#0e1225] border border-[#1a2040] rounded-xl overflow-hidden group hover:border-[#06b6d4]/40 transition-all duration-200 text-left cursor-pointer hover:shadow-lg hover:shadow-[#06b6d4]/5"
                  >
                    <div className="aspect-video bg-[#080b15] relative overflow-hidden">
                      <img
                        src={`/mado/screenshots/${ss.filename}`}
                        alt={ss.filename}
                        className="w-full h-full object-cover opacity-80 group-hover:opacity-100 group-hover:scale-105 transition-all duration-300"
                        onError={(e) => {
                          (e.currentTarget as HTMLImageElement).style.display = 'none';
                        }}
                      />
                      {/* Hover overlay */}
                      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-all duration-200 flex items-center justify-center">
                        <Maximize2 className="w-5 h-5 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200 drop-shadow-lg" />
                      </div>
                    </div>
                    <div className="p-3 space-y-1">
                      <p className="text-[10px] font-bold text-[#c8d0d8] truncate">{ss.filename}</p>
                      <div className="flex items-center justify-between">
                        <span className="text-[8px] text-[#555]">
                          {(ss.size_bytes / 1024).toFixed(1)} KB
                        </span>
                        <span className="text-[8px] text-[#555]">
                          {new Date(ss.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            )}

            {/* ── Lightbox Modal ────────────────────────────────── */}
            {lightboxIndex !== null && screenshots[lightboxIndex] && (
              <div
                className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm"
                onClick={() => setLightboxIndex(null)}
              >
                {/* Close button */}
                <button
                  onClick={() => setLightboxIndex(null)}
                  className="absolute top-4 right-4 z-10 p-2 rounded-full bg-black/50 hover:bg-black/70 text-white/80 hover:text-white transition-all cursor-pointer"
                >
                  <X className="w-5 h-5" />
                </button>

                {/* Previous button */}
                {lightboxIndex > 0 && (
                  <button
                    onClick={(e) => { e.stopPropagation(); setLightboxIndex(lightboxIndex - 1); }}
                    className="absolute left-4 z-10 p-2 rounded-full bg-black/50 hover:bg-black/70 text-white/80 hover:text-white transition-all cursor-pointer"
                  >
                    <ChevronLeft className="w-6 h-6" />
                  </button>
                )}

                {/* Next button */}
                {lightboxIndex < screenshots.length - 1 && (
                  <button
                    onClick={(e) => { e.stopPropagation(); setLightboxIndex(lightboxIndex + 1); }}
                    className="absolute right-4 z-10 p-2 rounded-full bg-black/50 hover:bg-black/70 text-white/80 hover:text-white transition-all cursor-pointer"
                  >
                    <ChevronRight className="w-6 h-6" />
                  </button>
                )}

                {/* Image */}
                <div
                  className="max-w-[90vw] max-h-[85vh] relative"
                  onClick={(e) => e.stopPropagation()}
                >
                  <img
                    src={`/mado/screenshots/${screenshots[lightboxIndex].filename}`}
                    alt={screenshots[lightboxIndex].filename}
                    className="max-w-full max-h-[85vh] object-contain rounded-lg shadow-2xl"
                  />
                  {/* Caption bar */}
                  <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent rounded-b-lg px-4 py-3">
                    <p className="text-xs font-bold text-white truncate">{screenshots[lightboxIndex].filename}</p>
                    <div className="flex items-center gap-3 mt-0.5">
                      <span className="text-[9px] text-white/60">
                        {(screenshots[lightboxIndex].size_bytes / 1024).toFixed(1)} KB
                      </span>
                      <span className="text-[9px] text-white/60">
                        {new Date(screenshots[lightboxIndex].created_at).toLocaleString()}
                      </span>
                      <span className="text-[9px] text-white/40">
                        {lightboxIndex + 1} / {screenshots.length}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {tab === 'Settings' && (
          <div className="max-w-2xl mx-auto space-y-6">
            <div className="space-y-1">
              <h2 className="text-xs font-bold text-[#7a8899] uppercase tracking-widest">Mado Configuration</h2>
              <p className="text-[10px] text-[#555]">Browser automation settings and paths</p>
            </div>

            {/* Paths info */}
            <div className="bg-[#0e1225] border border-[#1a2040] rounded-xl p-4 space-y-3">
              <div className="flex items-center gap-2 mb-3">
                <Settings2 className="w-4 h-4" style={{ color: ACCENT }} />
                <span className="text-xs font-bold text-[#c8d0d8]">Storage Paths</span>
              </div>
              {status && (
                <div className="space-y-2">
                  {[
                    ['Mado Root', status.mado_path],
                    ['Profiles', status.profiles_path],
                    ['Screenshots', status.screenshots_path],
                    ['Downloads', status.downloads_path],
                  ].map(([label, path]) => (
                    <div key={label} className="flex items-center justify-between py-1.5">
                      <span className="text-[10px] font-bold text-[#7a8899] uppercase tracking-wider">{label}</span>
                      <span className="text-[10px] text-[#555] font-mono">{path}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Status */}
            <div className="bg-[#0e1225] border border-[#1a2040] rounded-xl p-4 space-y-3">
              <div className="flex items-center gap-2 mb-3">
                <Globe className="w-4 h-4" style={{ color: ACCENT }} />
                <span className="text-xs font-bold text-[#c8d0d8]">Browser Engine</span>
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between py-1.5">
                  <span className="text-[10px] font-bold text-[#7a8899] uppercase tracking-wider">Chromium</span>
                  <span className={cn(
                    "text-[9px] font-bold uppercase tracking-wider px-2 py-0.5 rounded",
                    status?.installed
                      ? "bg-[#22c55e]/10 text-[#22c55e]"
                      : "bg-[#ef4444]/10 text-[#ef4444]"
                  )}>
                    {status?.installed ? 'Installed' : 'Not installed'}
                  </span>
                </div>
                <div className="flex items-center justify-between py-1.5">
                  <span className="text-[10px] font-bold text-[#7a8899] uppercase tracking-wider">Active Sessions</span>
                  <span className="text-[10px] text-[#c8d0d8] font-mono">{status?.active_sessions || 0}</span>
                </div>
              </div>
            </div>

            {/* Security note */}
            <div className="bg-[#06b6d4]/5 border border-[#06b6d4]/20 rounded-xl p-4">
              <p className="text-[10px] text-[#06b6d4]/80 leading-relaxed">
                <strong>Security:</strong> Browser automation permissions are governed by the Torii security posture.
                Visit the <strong>Torii</strong> page to configure domain allowlists, session limits, headless enforcement,
                and autonomous browsing permissions per security tier.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
