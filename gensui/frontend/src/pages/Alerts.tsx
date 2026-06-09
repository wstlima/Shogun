import { useEffect, useState } from 'react';
import api from '../lib/api';

export default function Alerts() {
  const [alerts, setAlerts] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/alerts').then(r => { setAlerts(r.data.alerts || []); setTotal(r.data.total || 0); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const handleResolve = async (id: string) => {
    await api.post(`/alerts/${id}/resolve`);
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, status: 'resolved' } : a));
  };

  const sevColor = (s: string) => {
    if (s === 'CRITICAL') return 'bg-crimson-500/15 text-crimson-400';
    if (s === 'HIGH') return 'bg-crimson-500/10 text-crimson-300';
    if (s === 'MEDIUM') return 'bg-amber-500/15 text-amber-400';
    return 'bg-gensui-500/15 text-gensui-400';
  };

  return (
    <div className="space-y-6 max-w-7xl">
      <div>
        <h1 className="text-2xl font-bold text-gensui-50">Alerts</h1>
        <p className="text-sm text-gensui-400 mt-1">{total} alerts</p>
      </div>
      <div className="glass-card overflow-hidden">
        <table className="gensui-table">
          <thead><tr><th>Time</th><th>Severity</th><th>Type</th><th>Description</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
            {alerts.map(a => (
              <tr key={a.id}>
                <td className="text-xs text-gensui-500">{a.timestamp ? new Date(a.timestamp).toLocaleString() : '—'}</td>
                <td><span className={`status-badge ${sevColor(a.severity)}`}>{a.severity}</span></td>
                <td className="text-xs text-gensui-300 font-mono">{a.event_type}</td>
                <td className="text-xs text-gensui-200 max-w-xs truncate">{a.description}</td>
                <td><span className={`status-badge ${a.status === 'active' ? 'harakiri' : 'online'}`}>{a.status}</span></td>
                <td>
                  {a.status === 'active' && (
                    <button onClick={() => handleResolve(a.id)} className="text-xs text-emerald-400 hover:text-emerald-300 font-medium">Resolve</button>
                  )}
                </td>
              </tr>
            ))}
            {alerts.length === 0 && <tr><td colSpan={6} className="text-center py-8 text-gensui-500">No alerts</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
