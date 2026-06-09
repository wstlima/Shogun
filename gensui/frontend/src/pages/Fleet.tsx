import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, Filter } from 'lucide-react';
import api from '../lib/api';

export default function Fleet() {
  const [members, setMembers] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const fetchMembers = async () => {
    try {
      const params: any = {};
      if (statusFilter) params.status = statusFilter;
      const { data } = await api.get('/members', { params });
      setMembers(data.members || []);
      setTotal(data.total || 0);
    } catch {} finally { setLoading(false); }
  };

  useEffect(() => { fetchMembers(); const i = setInterval(fetchMembers, 10000); return () => clearInterval(i); }, [statusFilter]);

  const filtered = members.filter(m =>
    !search || m.instance_name?.toLowerCase().includes(search.toLowerCase()) ||
    m.hostname?.toLowerCase().includes(search.toLowerCase())
  );

  const getStatusColor = (s: string) => {
    if (s === 'online') return 'online';
    if (s === 'offline') return 'offline';
    return 'pending';
  };

  const getHarakiriColor = (s: string) => s !== 'none' ? 'harakiri' : '';

  return (
    <div className="space-y-6 max-w-7xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gensui-50">Fleet Management</h1>
          <p className="text-sm text-gensui-400 mt-1">{total} registered Shogun instances</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1 max-w-sm">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gensui-500" />
          <input
            className="gensui-input pl-9"
            placeholder="Search by name or hostname..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <select
          className="gensui-input w-auto"
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
        >
          <option value="">All Status</option>
          <option value="online">Online</option>
          <option value="offline">Offline</option>
        </select>
      </div>

      {/* Table */}
      <div className="glass-card overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : (
          <table className="gensui-table">
            <thead>
              <tr>
                <th>Instance</th>
                <th>Status</th>
                <th>Environment</th>
                <th>Harakiri</th>
                <th>Samurai</th>
                <th>Workflows</th>
                <th>Last Seen</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(m => (
                <tr key={m.id}>
                  <td>
                    <Link to={`/fleet/${m.id}`} className="hover:text-cyan-400 transition-colors">
                      <div className="font-medium text-gensui-100">{m.instance_name}</div>
                      <div className="text-xs text-gensui-500">{m.hostname || 'Unknown host'}</div>
                    </Link>
                  </td>
                  <td>
                    <span className={`status-badge ${getStatusColor(m.status)}`}>
                      <span className={`w-2 h-2 rounded-full ${m.status === 'online' ? 'bg-emerald-400 animate-pulse' : 'bg-gensui-500'}`}></span>
                      {m.status}
                    </span>
                  </td>
                  <td className="text-gensui-400">{m.environment}</td>
                  <td>
                    {m.harakiri_state !== 'none' ? (
                      <span className="status-badge harakiri">{m.harakiri_state}</span>
                    ) : (
                      <span className="text-gensui-600 text-xs">—</span>
                    )}
                  </td>
                  <td className="text-gensui-300">{m.samurai_count}</td>
                  <td className="text-gensui-300">{m.active_workflow_count}</td>
                  <td className="text-xs text-gensui-500">
                    {m.last_seen_at ? new Date(m.last_seen_at).toLocaleString() : 'Never'}
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr><td colSpan={7} className="text-center py-8 text-gensui-500">No members found</td></tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
