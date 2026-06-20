import { useEffect, useState } from 'react';
import api from '../lib/api';
import { useTranslation } from '../i18n';

export default function ActivityMonitor() {
  const { t } = useTranslation();
  const [events, setEvents] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState('');

  const fetch = async () => {
    try {
      const params: any = { limit: 100 };
      if (categoryFilter) params.event_category = categoryFilter;
      const { data } = await api.get('/monitoring/activity', { params });
      setEvents(data.events || []);
      setTotal(data.total || 0);
    } catch {} finally { setLoading(false); }
  };

  useEffect(() => { fetch(); const i = setInterval(fetch, 5000); return () => clearInterval(i); }, [categoryFilter]);

  const sevColor = (s: string) => {
    if (s === 'critical') return 'text-crimson-400 bg-crimson-900/30';
    if (s === 'error') return 'text-crimson-300 bg-crimson-900/20';
    if (s === 'warn') return 'text-amber-400 bg-amber-900/20';
    return 'text-gensui-400 bg-gensui-700/30';
  };

  return (
    <div className="space-y-6 max-w-7xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gensui-50">{t('nav.activity', 'Activity Monitor')}</h1>
          <p className="text-sm text-gensui-400 mt-1">{total} {t('fleet_audit.total_events', 'telemetry events')}</p>
        </div>
        <select className="gensui-input w-auto" value={categoryFilter} onChange={e => setCategoryFilter(e.target.value)}>
          <option value="">All Categories</option>
          <option value="system">System</option>
          <option value="security">Security</option>
          <option value="agent">Agent</option>
          <option value="tool">Tool</option>
          <option value="model">Model</option>
        </select>
      </div>
      <div className="glass-card overflow-hidden">
        <table className="gensui-table">
          <thead><tr><th>Time</th><th>Severity</th><th>Type</th><th>Category</th><th>Shogun</th></tr></thead>
          <tbody>
            {events.map(e => (
              <tr key={e.id}>
                <td className="text-xs text-gensui-500">{e.timestamp ? new Date(e.timestamp).toLocaleString() : '—'}</td>
                <td><span className={`text-xs px-2 py-0.5 rounded-full font-medium ${sevColor(e.severity)}`}>{e.severity}</span></td>
                <td className="text-gensui-200 font-mono text-xs">{e.event_type}</td>
                <td className="text-gensui-400">{e.event_category}</td>
                <td className="text-xs text-gensui-500">{e.shogun_id?.slice(0, 8)}...</td>
              </tr>
            ))}
            {events.length === 0 && <tr><td colSpan={5} className="text-center py-8 text-gensui-500">No events</td></tr>}
          </tbody>
        </table>
      </div>
    </div>
  );
}
