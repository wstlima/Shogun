import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  ArrowLeft, Server, Shield, Users, Activity, Clock, Zap,
  Monitor, Globe, Tag, Hash, AlertTriangle, CircleDot
} from 'lucide-react';
import api from '../lib/api';

interface MemberDetail {
  id: string;
  instance_name: string;
  hostname: string | null;
  environment: string;
  organization: string | null;
  owner: string | null;
  version: string | null;
  build_hash: string | null;
  status: string;
  enrollment_status: string;
  harakiri_state: string;
  local_os: string | null;
  deployment_type: string | null;
  samurai_count: number;
  active_workflow_count: number;
  active_mado_sessions: number;
  disconnect_behavior: string;
  last_seen_at: string | null;
  created_at: string | null;
  metadata: Record<string, any> | null;
  effective_posture: any;
  groups: { id: string; name: string }[];
}

interface TelemetryEvent {
  id: string;
  event_type: string;
  event_category: string | null;
  severity: string | null;
  payload: any;
  timestamp: string | null;
}

export default function ShogunDetail() {
  const { id } = useParams<{ id: string }>();
  const [member, setMember] = useState<MemberDetail | null>(null);
  const [events, setEvents] = useState<TelemetryEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState('');

  useEffect(() => {
    if (!id) return;
    const fetchData = async () => {
      try {
        const [memberRes, activityRes] = await Promise.all([
          api.get(`/members/${id}`),
          api.get('/monitoring/activity', { params: { shogun_id: id, limit: 50 } }),
        ]);
        setMember(memberRes.data);
        setEvents(activityRes.data.events || []);
      } catch (err) {
        console.error('Failed to fetch member detail:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    const interval = setInterval(fetchData, 15000);
    return () => clearInterval(interval);
  }, [id]);

  const handleDisable = async () => {
    if (!id || !confirm('Disable this Shogun instance?')) return;
    setActionLoading('disable');
    try {
      await api.post(`/members/${id}/disable`);
      setMember(prev => prev ? { ...prev, enrollment_status: 'disabled', status: 'offline' } : null);
    } catch {} finally { setActionLoading(''); }
  };

  const handleHarakiri = async (level: string) => {
    if (!id || !confirm(`Execute ${level.toUpperCase()} Harakiri on this instance?`)) return;
    setActionLoading('harakiri');
    try {
      await api.post('/harakiri/individual', { shogun_id: id, level });
      setMember(prev => prev ? { ...prev, harakiri_state: level } : null);
    } catch {} finally { setActionLoading(''); }
  };

  const getSeverityColor = (s: string | null) => {
    if (s === 'critical') return 'text-red-400';
    if (s === 'warn' || s === 'warning') return 'text-amber-400';
    if (s === 'info') return 'text-cyan-400';
    return 'text-gensui-400';
  };

  const getStatusStyle = (s: string) => {
    if (s === 'online') return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
    if (s === 'offline') return 'bg-gensui-600/15 text-gensui-400 border-gensui-500/30';
    return 'bg-amber-500/15 text-amber-400 border-amber-500/30';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="w-10 h-10 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!member) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4 text-gensui-400">
        <Server size={48} />
        <p>Shogun instance not found</p>
        <Link to="/fleet" className="btn-primary text-sm">Back to Fleet</Link>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl">
      {/* Back + Header */}
      <div className="flex items-center gap-4">
        <Link to="/fleet" className="p-2 rounded-lg hover:bg-gensui-700/50 transition-colors text-gensui-400 hover:text-gensui-100">
          <ArrowLeft size={20} />
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-gensui-50">{member.instance_name}</h1>
            <span className={`text-xs font-bold uppercase px-2.5 py-1 rounded-full border ${getStatusStyle(member.status)}`}>
              {member.status}
            </span>
            {member.harakiri_state !== 'none' && (
              <span className="text-xs font-bold uppercase px-2.5 py-1 rounded-full border bg-red-500/15 text-red-400 border-red-500/30 animate-pulse">
                ⚠ {member.harakiri_state}
              </span>
            )}
          </div>
          <p className="text-sm text-gensui-400 mt-0.5">
            {member.hostname || 'Unknown host'} · {member.environment} · Enrolled {member.created_at ? new Date(member.created_at).toLocaleDateString() : 'Unknown'}
          </p>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {[
          { label: 'Samurai', value: member.samurai_count, icon: Users, color: 'text-cyan-400' },
          { label: 'Workflows', value: member.active_workflow_count, icon: Activity, color: 'text-emerald-400' },
          { label: 'Mado Sessions', value: member.active_mado_sessions, icon: Monitor, color: 'text-purple-400' },
          { label: 'Last Seen', value: member.last_seen_at ? new Date(member.last_seen_at).toLocaleTimeString() : 'Never', icon: Clock, color: 'text-amber-400' },
          { label: 'Enrollment', value: member.enrollment_status, icon: Shield, color: member.enrollment_status === 'active' ? 'text-emerald-400' : 'text-amber-400' },
        ].map(stat => (
          <div key={stat.label} className="metric-card">
            <div className="flex items-center gap-2">
              <stat.icon size={14} className={stat.color} />
              <span className="metric-label text-xs">{stat.label}</span>
            </div>
            <span className={`text-xl font-bold ${stat.color}`}>{stat.value}</span>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column — Identity + Security */}
        <div className="lg:col-span-1 space-y-6">
          {/* Identity */}
          <div className="glass-card p-5 space-y-4">
            <h3 className="text-sm font-bold text-gensui-300 uppercase tracking-widest flex items-center gap-2">
              <Server size={14} className="text-cyan-400" /> Identity
            </h3>
            <div className="space-y-3 text-sm">
              {[
                { label: 'Version', value: member.version, icon: Tag },
                { label: 'Build', value: member.build_hash?.slice(0, 12), icon: Hash },
                { label: 'OS', value: member.local_os, icon: Monitor },
                { label: 'Deploy Type', value: member.deployment_type, icon: Globe },
                { label: 'Organization', value: member.organization, icon: Users },
                { label: 'Owner', value: member.owner, icon: CircleDot },
                { label: 'Disconnect', value: member.disconnect_behavior, icon: Zap },
              ].map(item => (
                <div key={item.label} className="flex items-center justify-between">
                  <span className="text-gensui-500 flex items-center gap-2">
                    <item.icon size={12} /> {item.label}
                  </span>
                  <span className="text-gensui-200 font-mono text-xs">{item.value || '—'}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Security Posture */}
          <div className="glass-card p-5 space-y-4">
            <h3 className="text-sm font-bold text-gensui-300 uppercase tracking-widest flex items-center gap-2">
              <Shield size={14} className="text-amber-400" /> Security Posture
            </h3>
            {member.effective_posture ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-gensui-400 text-xs">Active Posture</span>
                  <span className="text-sm font-bold text-amber-400">{member.effective_posture.posture_name || member.effective_posture.name || '—'}</span>
                </div>
                {member.effective_posture.source && (
                  <div className="flex items-center justify-between">
                    <span className="text-gensui-400 text-xs">Source</span>
                    <span className="text-xs text-gensui-300">{member.effective_posture.source}</span>
                  </div>
                )}
                {member.effective_posture.level != null && (
                  <div className="flex items-center justify-between">
                    <span className="text-gensui-400 text-xs">Level</span>
                    <span className="text-xs text-gensui-300">{member.effective_posture.level}</span>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-xs text-gensui-500">No posture assigned</p>
            )}
          </div>

          {/* Groups */}
          <div className="glass-card p-5 space-y-4">
            <h3 className="text-sm font-bold text-gensui-300 uppercase tracking-widest flex items-center gap-2">
              <Users size={14} className="text-purple-400" /> Groups
            </h3>
            {member.groups.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {member.groups.map(g => (
                  <span key={g.id} className="text-xs px-3 py-1.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20">
                    {g.name}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-xs text-gensui-500">Not in any groups</p>
            )}
          </div>

          {/* Actions */}
          <div className="glass-card p-5 space-y-4">
            <h3 className="text-sm font-bold text-gensui-300 uppercase tracking-widest flex items-center gap-2">
              <AlertTriangle size={14} className="text-red-400" /> Actions
            </h3>
            <div className="space-y-2">
              <button
                onClick={() => handleHarakiri('soft_freeze')}
                disabled={!!actionLoading || member.harakiri_state !== 'none'}
                className="w-full btn-danger text-xs py-2 disabled:opacity-40"
              >
                {actionLoading === 'harakiri' ? 'Executing...' : '⚡ Soft Freeze'}
              </button>
              <button
                onClick={() => handleHarakiri('hard_stop')}
                disabled={!!actionLoading || member.harakiri_state !== 'none'}
                className="w-full btn-danger text-xs py-2 disabled:opacity-40"
              >
                {actionLoading === 'harakiri' ? 'Executing...' : '🔥 Hard Stop'}
              </button>
              <button
                onClick={handleDisable}
                disabled={!!actionLoading || member.enrollment_status === 'disabled'}
                className="w-full btn-ghost text-xs py-2 text-red-400 border-red-500/30 hover:bg-red-500/10 disabled:opacity-40"
              >
                {actionLoading === 'disable' ? 'Disabling...' : 'Disable Instance'}
              </button>
            </div>
          </div>
        </div>

        {/* Right Column — Activity Timeline */}
        <div className="lg:col-span-2">
          <div className="glass-card p-5 space-y-4">
            <h3 className="text-sm font-bold text-gensui-300 uppercase tracking-widest flex items-center gap-2">
              <Activity size={14} className="text-cyan-400" /> Activity Timeline
            </h3>
            {events.length > 0 ? (
              <div className="space-y-1 max-h-[700px] overflow-y-auto pr-2">
                {events.map(evt => (
                  <div key={evt.id} className="flex items-start gap-3 py-2.5 border-b border-gensui-800/50 last:border-0 group hover:bg-gensui-800/30 rounded-lg px-2 -mx-2 transition-colors">
                    <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${
                      evt.severity === 'critical' ? 'bg-red-400' :
                      evt.severity === 'warn' || evt.severity === 'warning' ? 'bg-amber-400' :
                      evt.severity === 'info' ? 'bg-cyan-400' : 'bg-gensui-500'
                    }`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 text-xs">
                        <span className={`font-bold ${getSeverityColor(evt.severity)}`}>
                          {evt.event_type}
                        </span>
                        {evt.event_category && (
                          <span className="text-gensui-600 font-mono">{evt.event_category}</span>
                        )}
                      </div>
                      {evt.payload?.message && (
                        <p className="text-xs text-gensui-400 mt-0.5 truncate">{evt.payload.message}</p>
                      )}
                    </div>
                    <span className="text-[10px] text-gensui-600 shrink-0 font-mono">
                      {evt.timestamp ? new Date(evt.timestamp).toLocaleTimeString() : ''}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-16 text-gensui-500">
                <Activity size={32} className="mb-3 opacity-30" />
                <p className="text-sm">No telemetry events recorded</p>
                <p className="text-xs mt-1">Events will appear here once the Shogun starts sending telemetry</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
