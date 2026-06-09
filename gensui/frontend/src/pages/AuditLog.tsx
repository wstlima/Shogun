import { useEffect, useState } from 'react';
import api from '../lib/api';

export default function AuditLog() {
  const [entries, setEntries] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState('');

  useEffect(() => {
    const params: any = { limit: 100 };
    if (actionFilter) params.action = actionFilter;
    api.get('/audit', { params }).then(r => {
      setEntries(r.data.entries || []);
      setTotal(r.data.total || 0);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [actionFilter]);

  return (
    <div className="space-y-6 max-w-7xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gensui-50">Audit Log</h1>
          <p className="text-sm text-gensui-400 mt-1">{total} entries — HMAC-chained</p>
        </div>
        <input className="gensui-input w-64" placeholder="Filter by action..." value={actionFilter} onChange={e => setActionFilter(e.target.value)} />
      </div>
      <div className="glass-card overflow-hidden">
        <table className="gensui-table">
          <thead><tr><th>Time</th><th>Actor</th><th>Action</th><th>Target</th><th>Reason</th></tr></thead>
          <tbody>
            {entries.map(e => (
              <tr key={e.id}>
                <td className="text-xs text-gensui-500">{e.timestamp ? new Date(e.timestamp).toLocaleString() : '—'}</td>
                <td><span className="text-xs text-gensui-300">{e.actor_type}</span></td>
                <td className="text-gensui-200 font-mono text-xs">{e.action}</td>
                <td className="text-xs text-gensui-400">{e.target_type} {e.target_id?.slice(0, 8)}</td>
                <td className="text-xs text-gensui-500 max-w-xs truncate">{e.reason || '—'}</td>
              </tr>
            ))}
            {entries.length === 0 && <tr><td colSpan={5} className="text-center py-8 text-gensui-500">No audit entries</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
