import { useEffect, useState } from 'react';
import { UserPlus, Check, X, Copy, AlertCircle, Loader2, Plus, CheckCircle2, Ban } from 'lucide-react';
import api from '../lib/api';
import { useTranslation } from '../i18n';

export default function Enrollment() {
  const { t } = useTranslation();
  const [pending, setPending] = useState<any[]>([]);
  const [tokens, setTokens] = useState<any[]>([]);
  const [newLabel, setNewLabel] = useState('');
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      const [p, t] = await Promise.all([api.get('/enrollment/pending'), api.get('/enrollment/tokens')]);
      setPending(p.data.members || []);
      setTokens(t.data || []);
    } catch (err: any) {
      console.error('Failed to load enrollment data:', err);
      setError(err.response?.data?.detail || 'Failed to load enrollment data');
    } finally { setLoading(false); }
  };

  useEffect(() => { fetchData(); }, []);

  // Auto-clear messages after 5 seconds
  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => { setError(null); setSuccess(null); }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, success]);

  const handleApprove = async (id: string) => {
    try {
      await api.post(`/enrollment/approve/${id}`);
      setSuccess('Enrollment approved successfully');
      fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to approve enrollment');
    }
  };

  const handleReject = async (id: string) => {
    try {
      await api.post(`/enrollment/reject/${id}`);
      setSuccess('Enrollment rejected');
      fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reject enrollment');
    }
  };

  const handleCreateToken = async () => {
    setCreating(true);
    setError(null);
    const label = newLabel.trim() || `Token ${new Date().toLocaleDateString()}`;
    try {
      const res = await api.post('/enrollment/tokens', { label, max_uses: 1 });
      setNewLabel('');
      setSuccess(`Token created: ${res.data?.token?.slice(0, 30)}...`);
      fetchData();
    } catch (err: any) {
      const detail = err.response?.data?.detail || err.message || 'Failed to create token';
      setError(`Token creation failed: ${detail}`);
      console.error('Token creation error:', err.response || err);
    } finally {
      setCreating(false);
    }
  };

  const handleRevokeToken = async (tokenId: string) => {
    if (!confirm('Revoke this token? It will no longer be usable for enrollment.')) return;
    try {
      await api.post(`/enrollment/tokens/${tokenId}/revoke`);
      setSuccess('Token revoked successfully');
      fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to revoke token');
    }
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold text-gensui-50">{t('enrollment.title', 'Enrollment Management')}</h1>
        <p className="text-sm text-gensui-400 mt-1">{t('enrollment.subtitle', 'Approve new Shogun instances and manage tokens')}</p>
      </div>

      {/* Error/Success Banner */}
      {error && (
        <div className="flex items-center gap-2 px-4 py-3 bg-red-900/30 border border-red-700/40 rounded-xl text-sm text-red-300">
          <AlertCircle size={16} className="shrink-0" />
          <span>{error}</span>
        </div>
      )}
      {success && (
        <div className="flex items-center gap-2 px-4 py-3 bg-emerald-900/30 border border-emerald-700/40 rounded-xl text-sm text-emerald-300">
          <CheckCircle2 size={16} className="shrink-0" />
          <span>{success}</span>
        </div>
      )}

      {/* Pending Enrollments */}
      <div className="glass-card overflow-hidden">
        <div className="px-5 py-4 border-b border-gensui-700/30 flex items-center gap-2">
          <UserPlus size={16} className="text-amber-400" />
          <h3 className="text-sm font-semibold text-gensui-200">{t('enrollment.pending_enrollments', 'Pending Enrollments')} ({pending.length})</h3>
        </div>
        <table className="gensui-table">
          <thead><tr><th>Instance</th><th>Hostname</th><th>Environment</th><th>OS</th><th>Requested</th><th>Actions</th></tr></thead>
          <tbody>
            {pending.map(m => (
              <tr key={m.id}>
                <td className="text-gensui-100 font-medium">{m.instance_name}</td>
                <td className="text-gensui-400">{m.hostname || '—'}</td>
                <td className="text-gensui-400">{m.environment}</td>
                <td className="text-gensui-400">{m.local_os || '—'}</td>
                <td className="text-xs text-gensui-500">{m.created_at ? new Date(m.created_at).toLocaleString() : '—'}</td>
                <td className="flex gap-2">
                  <button onClick={() => handleApprove(m.id)} className="p-1.5 text-emerald-400 hover:bg-emerald-900/30 rounded-lg"><Check size={16} /></button>
                  <button onClick={() => handleReject(m.id)} className="p-1.5 text-crimson-400 hover:bg-crimson-900/30 rounded-lg"><X size={16} /></button>
                </td>
              </tr>
            ))}
            {pending.length === 0 && <tr><td colSpan={6} className="text-center py-6 text-gensui-500">No pending enrollments</td></tr>}
          </tbody>
        </table>
      </div>

      {/* Tokens */}
      <div className="glass-card p-5">
        <h3 className="text-sm font-semibold text-gensui-200 mb-4">Enrollment Tokens</h3>
        <div className="flex gap-2 mb-4">
          <input
            className="gensui-input flex-1"
            placeholder="Token label..."
            value={newLabel}
            onChange={e => setNewLabel(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleCreateToken()}
          />
          <button
            onClick={handleCreateToken}
            disabled={creating}
            className="btn-primary flex items-center gap-1.5 disabled:opacity-50 cursor-pointer"
          >
            {creating ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
            {t('enrollment.generate_token', 'Generate Token')}
          </button>
        </div>
        <div className="space-y-2">
          {tokens.map(t => (
            <div key={t.id} className="flex items-center justify-between p-3 bg-gensui-800/40 rounded-xl">
              <div>
                <p className="text-sm text-gensui-200">{t.label || 'Unlabeled'}</p>
                <p className="text-xs text-gensui-500 font-mono">{t.token.slice(0, 30)}...</p>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-gensui-400">{t.use_count}/{t.max_uses} uses</span>
                {t.is_revoked && <span className="text-[10px] text-red-400 font-bold uppercase">Revoked</span>}
                {!t.is_revoked && (
                  <button
                    onClick={() => handleRevokeToken(t.id)}
                    className="p-1.5 text-gensui-400 hover:text-red-400 transition-colors"
                    title="Revoke token"
                  >
                    <Ban size={14} />
                  </button>
                )}
                <button
                  onClick={() => { navigator.clipboard.writeText(t.token); setSuccess('Token copied to clipboard'); }}
                  className="p-1.5 text-gensui-400 hover:text-cyan-400 transition-colors"
                  title="Copy token"
                >
                  <Copy size={14} />
                </button>
              </div>
            </div>
          ))}
          {tokens.length === 0 && !loading && (
            <p className="text-center py-4 text-gensui-500 text-sm">No tokens created yet</p>
          )}
        </div>
      </div>
    </div>
  );
}
