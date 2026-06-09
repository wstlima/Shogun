import { useState, useEffect } from 'react';
import { Skull, AlertTriangle, Shield, Users } from 'lucide-react';
import api from '../lib/api';

export default function HarakiriControl() {
  const [members, setMembers] = useState<any[]>([]);
  const [events, setEvents] = useState<any[]>([]);
  const [mode, setMode] = useState('soft_freeze');
  const [scope, setScope] = useState<'individual' | 'global'>('individual');
  const [targetId, setTargetId] = useState('');
  const [reason, setReason] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const [loading, setLoading] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  useEffect(() => {
    api.get('/members').then(r => setMembers(r.data.members || []));
    api.get('/harakiri/events').then(r => setEvents(r.data || []));
  }, []);

  const expectedText = scope === 'global' ? 'CONFIRM GLOBAL HARAKIRI' : 'CONFIRM HARAKIRI';

  const handleTrigger = async () => {
    if (confirmation !== expectedText) return;
    setLoading(true);
    try {
      const endpoint = scope === 'global' ? '/harakiri/global' : '/harakiri/individual';
      await api.post(endpoint, {
        target_id: scope === 'individual' ? targetId : undefined,
        mode,
        reason,
        confirmation_text: confirmation,
      });
      setShowConfirm(false);
      setConfirmation('');
      setReason('');
      const { data } = await api.get('/harakiri/events');
      setEvents(data || []);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Harakiri failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRelease = async (eventId: string) => {
    try {
      await api.post('/harakiri/release', { harakiri_event_id: eventId, release_to_posture: 'RESTRICTED' });
      const { data } = await api.get('/harakiri/events');
      setEvents(data || []);
    } catch {}
  };

  return (
    <div className="space-y-6 max-w-5xl">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-3 rounded-xl bg-crimson-900/40 danger-glow">
          <Skull size={24} className="text-crimson-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gensui-50">Harakiri Control Center</h1>
          <p className="text-sm text-crimson-400">Emergency shutdown and containment</p>
        </div>
      </div>

      {/* Trigger Panel */}
      <div className="glass-card p-6 border-crimson-900/30">
        <h2 className="text-lg font-semibold text-gensui-100 mb-4">Initiate Harakiri</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-xs text-gensui-400 uppercase tracking-wider mb-1.5">Scope</label>
            <select className="gensui-input" value={scope} onChange={e => setScope(e.target.value as any)}>
              <option value="individual">Individual Shogun</option>
              <option value="global">Global (ALL Shoguns)</option>
            </select>
          </div>
          <div>
            <label className="block text-xs text-gensui-400 uppercase tracking-wider mb-1.5">Mode</label>
            <select className="gensui-input" value={mode} onChange={e => setMode(e.target.value)}>
              <option value="soft_freeze">Soft Freeze</option>
              <option value="hard_stop">Hard Stop</option>
              <option value="network_isolate">Network Isolate</option>
              <option value="full_terminate">Full Terminate</option>
            </select>
          </div>
        </div>

        {scope === 'individual' && (
          <div className="mb-4">
            <label className="block text-xs text-gensui-400 uppercase tracking-wider mb-1.5">Target Shogun</label>
            <select className="gensui-input" value={targetId} onChange={e => setTargetId(e.target.value)}>
              <option value="">Select a Shogun instance...</option>
              {members.filter(m => m.enrollment_status === 'active').map(m => (
                <option key={m.id} value={m.id}>{m.instance_name} ({m.status})</option>
              ))}
            </select>
          </div>
        )}

        <div className="mb-4">
          <label className="block text-xs text-gensui-400 uppercase tracking-wider mb-1.5">Reason</label>
          <input className="gensui-input" value={reason} onChange={e => setReason(e.target.value)} placeholder="Reason for Harakiri..." />
        </div>

        {!showConfirm ? (
          <button
            onClick={() => setShowConfirm(true)}
            disabled={scope === 'individual' && !targetId}
            className="btn-danger w-full py-3 flex items-center justify-center gap-2"
          >
            <Skull size={16} />
            Initiate Harakiri
          </button>
        ) : (
          <div className="space-y-3 p-4 rounded-xl border border-crimson-700/50 bg-crimson-900/20">
            <div className="flex items-center gap-2 text-crimson-300">
              <AlertTriangle size={16} />
              <span className="text-sm font-semibold">Type "{expectedText}" to confirm</span>
            </div>
            <input
              className="gensui-input border-crimson-700/50 focus:border-crimson-500/50 focus:ring-crimson-500/20"
              value={confirmation}
              onChange={e => setConfirmation(e.target.value)}
              placeholder={expectedText}
              autoFocus
            />
            <div className="flex gap-2">
              <button
                onClick={handleTrigger}
                disabled={confirmation !== expectedText || loading}
                className="btn-danger flex-1 flex items-center justify-center gap-2"
              >
                {loading ? 'Executing...' : '⚡ Execute Harakiri'}
              </button>
              <button onClick={() => { setShowConfirm(false); setConfirmation(''); }} className="btn-ghost">
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Event History */}
      <div className="glass-card overflow-hidden">
        <div className="px-5 py-4 border-b border-gensui-700/30">
          <h3 className="text-sm font-semibold text-gensui-200">Harakiri Event History</h3>
        </div>
        <table className="gensui-table">
          <thead>
            <tr>
              <th>Scope</th>
              <th>Mode</th>
              <th>Status</th>
              <th>Affected</th>
              <th>Acknowledged</th>
              <th>Time</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {events.map(e => (
              <tr key={e.id}>
                <td><span className="status-badge harakiri">{e.scope}</span></td>
                <td className="text-gensui-300">{e.mode}</td>
                <td>
                  <span className={`status-badge ${e.status === 'released' ? 'online' : e.status === 'completed' ? 'pending' : 'harakiri'}`}>
                    {e.status}
                  </span>
                </td>
                <td className="text-gensui-300">{e.affected_count}</td>
                <td className="text-gensui-300">{e.acknowledged_count}/{e.affected_count}</td>
                <td className="text-xs text-gensui-500">
                  {e.requested_at ? new Date(e.requested_at).toLocaleString() : '—'}
                </td>
                <td>
                  {['pending', 'executing', 'completed'].includes(e.status) && (
                    <button
                      onClick={() => handleRelease(e.id)}
                      className="text-xs text-emerald-400 hover:text-emerald-300 font-medium"
                    >
                      Release
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {events.length === 0 && (
              <tr><td colSpan={7} className="text-center py-8 text-gensui-500">No Harakiri events</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
