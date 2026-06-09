import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, Cpu, AlertTriangle, Activity, Skull, Shield, Workflow, Globe } from 'lucide-react';
import api from '../lib/api';

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const { data: d } = await api.get('/dashboard');
        setData(d);
      } catch (err) {
        console.error('Dashboard fetch failed:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
    const interval = setInterval(fetchDashboard, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const fleet = data?.fleet || {};
  const alerts = data?.alerts || {};
  const globalPosture = data?.global_posture || {};

  return (
    <div className="space-y-6 max-w-7xl">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gensui-50">Command Overview</h1>
        <p className="text-sm text-gensui-400 mt-1">Real-time fleet monitoring and security status</p>
      </div>

      {/* Fleet Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Members Online"
          value={fleet.online_members ?? 0}
          total={fleet.total_members ?? 0}
          icon={Users}
          color="emerald"
        />
        <MetricCard
          label="Active Samurai"
          value={fleet.total_samurai ?? 0}
          icon={Cpu}
          color="cyan"
        />
        <MetricCard
          label="Active Workflows"
          value={fleet.total_workflows ?? 0}
          icon={Workflow}
          color="amber"
        />
        <MetricCard
          label="Mado Sessions"
          value={fleet.total_mado_sessions ?? 0}
          icon={Globe}
          color="cyan"
        />
      </div>

      {/* Alert & Status Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Active Alerts */}
        <Link to="/alerts" className="glass-card p-5 hover:border-gensui-600/70 transition-all group">
          <div className="flex items-center gap-3 mb-3">
            <div className={`p-2 rounded-xl ${alerts.total > 0 ? 'bg-crimson-900/40' : 'bg-gensui-700/40'}`}>
              <AlertTriangle size={18} className={alerts.total > 0 ? 'text-crimson-400' : 'text-gensui-400'} />
            </div>
            <span className="text-sm text-gensui-400">Active Alerts</span>
          </div>
          <div className="flex items-baseline gap-2">
            <span className={`text-3xl font-bold ${alerts.total > 0 ? 'text-crimson-400' : 'text-gensui-300'}`}>
              {alerts.total ?? 0}
            </span>
            {alerts.critical > 0 && (
              <span className="text-xs text-crimson-400 font-semibold">{alerts.critical} CRITICAL</span>
            )}
          </div>
        </Link>

        {/* Harakiri Status */}
        <Link to="/harakiri" className="glass-card p-5 hover:border-gensui-600/70 transition-all group">
          <div className="flex items-center gap-3 mb-3">
            <div className={`p-2 rounded-xl ${data?.active_harakiri_count > 0 ? 'bg-crimson-900/40 danger-glow' : 'bg-gensui-700/40'}`}>
              <Skull size={18} className={data?.active_harakiri_count > 0 ? 'text-crimson-400' : 'text-gensui-400'} />
            </div>
            <span className="text-sm text-gensui-400">Harakiri Active</span>
          </div>
          <span className={`text-3xl font-bold ${data?.active_harakiri_count > 0 ? 'text-crimson-400' : 'text-emerald-400'}`}>
            {data?.active_harakiri_count > 0 ? data.active_harakiri_count : 'None'}
          </span>
        </Link>

        {/* Pending Enrollment */}
        <Link to="/enrollment" className="glass-card p-5 hover:border-gensui-600/70 transition-all group">
          <div className="flex items-center gap-3 mb-3">
            <div className={`p-2 rounded-xl ${fleet.pending_enrollment > 0 ? 'bg-amber-900/40' : 'bg-gensui-700/40'}`}>
              <Shield size={18} className={fleet.pending_enrollment > 0 ? 'text-amber-400' : 'text-gensui-400'} />
            </div>
            <span className="text-sm text-gensui-400">Pending Enrollment</span>
          </div>
          <span className={`text-3xl font-bold ${fleet.pending_enrollment > 0 ? 'text-amber-400' : 'text-gensui-300'}`}>
            {fleet.pending_enrollment ?? 0}
          </span>
        </Link>
      </div>

      {/* Global Posture */}
      {globalPosture.is_active && (
        <div className="glass-card p-5 border-crimson-700/30 danger-glow">
          <div className="flex items-center gap-3">
            <AlertTriangle size={20} className="text-crimson-400" />
            <div>
              <p className="font-bold text-crimson-300">Global Posture Override Active</p>
              <p className="text-sm text-gensui-400">
                {globalPosture.posture_name} — activated by {globalPosture.activated_by}
                {globalPosture.reason && ` — ${globalPosture.reason}`}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function MetricCard({ label, value, total, icon: Icon, color }: {
  label: string; value: number; total?: number;
  icon: any; color: string;
}) {
  const colorMap: Record<string, string> = {
    emerald: 'text-emerald-400 bg-emerald-900/30',
    cyan: 'text-cyan-400 bg-cyan-900/30',
    amber: 'text-amber-400 bg-amber-900/30',
    crimson: 'text-crimson-400 bg-crimson-900/30',
  };
  const [textColor, bgColor] = (colorMap[color] || colorMap.cyan).split(' ');

  return (
    <div className="metric-card">
      <div className="flex items-center gap-2 mb-1">
        <div className={`p-1.5 rounded-lg ${bgColor}`}>
          <Icon size={16} className={textColor} />
        </div>
      </div>
      <div className="flex items-baseline gap-1.5">
        <span className={`metric-value ${textColor}`}>{value}</span>
        {total !== undefined && (
          <span className="text-sm text-gensui-500">/ {total}</span>
        )}
      </div>
      <span className="metric-label">{label}</span>
    </div>
  );
}
