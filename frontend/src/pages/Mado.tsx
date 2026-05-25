import { useState, useEffect, useCallback } from 'react';
import {
  AppWindow,
  Globe,
  Plus,
  Trash2,
  Play,
  Square,
  Camera,
  Download,
  RefreshCw,
  Loader2,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ExternalLink,
  Monitor,
  MonitorOff,
  Image,
  ChevronRight,
  Send,
  FileText,
  Settings2,
} from 'lucide-react';
import axios from 'axios';
import { cn } from '../lib/utils';

// ═══════════════════════════════════════════════════════════════
// TYPES
// ═══════════════════════════════════════════════════════════════

interface MadoSession {
  id: string;
  name: string;
  profile_name: string;
  agent_id: string | null;
  status: string;
  browser_mode: string;
  last_url: string | null;
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

  // Quick action state
  const [quickUrl, setQuickUrl] = useState('');
  const [quickSessionId, setQuickSessionId] = useState('');
  const [quickResult, setQuickResult] = useState<string | null>(null);
  const [quickLoading, setQuickLoading] = useState(false);

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
      await axios.post('/api/v1/mado/sessions', {
        name: newName,
        profile_name: newProfile.replace(/\s+/g, '_').toLowerCase(),
        browser_mode: newMode,
      });
      await loadSessions();
      setShowCreate(false);
      setNewName('');
      setNewProfile('');
    } catch { /* ignore */ }
    setCreating(false);
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
      const r = await axios.post(`/api/v1/mado/sessions/${quickSessionId}/extract`, {
        extract_type: 'text',
      });
      const content = r.data?.data?.content || '';
      setQuickResult(content.slice(0, 3000) + (content.length > 3000 ? '\n\n... [truncated]' : ''));
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
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
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
              <div className="grid grid-cols-3 gap-3">
                {screenshots.map((ss) => (
                  <div
                    key={ss.filename}
                    className="bg-[#0e1225] border border-[#1a2040] rounded-xl overflow-hidden group hover:border-[#2a3060] transition-all"
                  >
                    <div className="aspect-video bg-[#080b15] flex items-center justify-center">
                      <Image className="w-8 h-8" style={{ color: `${ACCENT}30` }} />
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
                  </div>
                ))}
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
