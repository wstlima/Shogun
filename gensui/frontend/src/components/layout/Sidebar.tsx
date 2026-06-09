import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Shield, Users, Layers, Activity,
  FileSearch, Bell, UserPlus, Skull, LogOut, ChevronLeft, ChevronRight,
  Network, Settings
} from 'lucide-react';
import { clearAuth, getAdmin } from '../../lib/auth';

const NAV_ITEMS = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/fleet', label: 'Fleet', icon: Users },
  { path: '/network', label: 'Network', icon: Network },
  { path: '/groups', label: 'Groups', icon: Layers },
  { path: '/postures', label: 'Postures', icon: Shield },
  { path: '/harakiri', label: 'Harakiri', icon: Skull },
  { path: '/activity', label: 'Activity', icon: Activity },
  { path: '/audit', label: 'Audit Log', icon: FileSearch },
  { path: '/alerts', label: 'Alerts', icon: Bell },
  { path: '/enrollment', label: 'Enrollment', icon: UserPlus },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar() {
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const admin = getAdmin();

  return (
    <aside className={`flex flex-col h-screen bg-gensui-800/40 border-r border-gensui-700/30 transition-all duration-300 ${collapsed ? 'w-16' : 'w-64'}`}>
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-gensui-700/30">
        <img
          src="/gensui-logo.png"
          alt="Gensui"
          className="w-9 h-9 rounded-lg object-cover"
        />
        {!collapsed && (
          <div>
            <h1 className="text-sm font-bold text-gensui-50 tracking-wide">GENSUI</h1>
            <p className="text-[10px] text-gensui-500 uppercase tracking-widest">Command Center</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map(({ path, label, icon: Icon }) => {
          const active = location.pathname === path || (path !== '/' && location.pathname.startsWith(path));
          return (
            <Link
              key={path}
              to={path}
              className={`sidebar-item ${active ? 'active' : ''}`}
              title={collapsed ? label : undefined}
            >
              <Icon size={18} />
              {!collapsed && <span>{label}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Collapse Toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center justify-center p-2 mx-2 mb-2 rounded-lg text-gensui-500 hover:text-gensui-300 hover:bg-gensui-700/30 transition-colors"
      >
        {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>

      {/* Admin Profile */}
      <div className="border-t border-gensui-700/30 p-3">
        {!collapsed && admin && (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gensui-600 flex items-center justify-center text-xs font-bold text-gensui-200">
              {(admin.display_name || admin.email)?.[0]?.toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium text-gensui-200 truncate">{admin.display_name || admin.email}</p>
              <p className="text-[10px] text-gensui-500 uppercase">{admin.role}</p>
            </div>
            <button
              onClick={() => { clearAuth(); window.location.href = '/login'; }}
              className="p-1.5 text-gensui-500 hover:text-crimson-400 transition-colors"
              title="Logout"
            >
              <LogOut size={14} />
            </button>
          </div>
        )}
        {collapsed && (
          <button
            onClick={() => { clearAuth(); window.location.href = '/login'; }}
            className="w-full flex justify-center p-2 text-gensui-500 hover:text-crimson-400 transition-colors"
            title="Logout"
          >
            <LogOut size={16} />
          </button>
        )}
      </div>
    </aside>
  );
}
