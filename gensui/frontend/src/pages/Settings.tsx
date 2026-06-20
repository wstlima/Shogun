import { useEffect, useState } from 'react';
import { Settings as SettingsIcon, User, Lock, Server, Info, Check, AlertTriangle, Users, Plus, Trash2 } from 'lucide-react';
import api from '../lib/api';

interface Profile {
  id: string;
  email: string;
  role: string;
  display_name: string;
}

const ROLES = ['owner', 'admin', 'auditor', 'operator', 'viewer'];

function AdminManagement() {
  const [admins, setAdmins] = useState<any[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [role, setRole] = useState('admin');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const load = async () => {
    try {
      const { data } = await api.get('/auth/admins');
      setAdmins(data.admins || []);
    } catch {}
  };

  useEffect(() => { load(); }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(''); setSuccess('');
    try {
      await api.post('/auth/admins', { email, password, display_name: displayName || 'Admin', role });
      setSuccess('Admin created successfully');
      setShowCreate(false);
      setEmail(''); setPassword(''); setDisplayName(''); setRole('admin');
      load();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create admin');
    }
  };

  const handleDeactivate = async (id: string) => {
    if (!confirm('Deactivate this admin? They will no longer be able to login.')) return;
    try {
      await api.delete(`/auth/admins/${id}`);
      load();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to deactivate admin');
    }
  };

  return (
    <div className="glass-card p-6 space-y-5">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-bold text-gensui-300 uppercase tracking-widest flex items-center gap-2">
          <Users size={14} className="text-purple-400" /> Admin Users
        </h2>
        <button onClick={() => setShowCreate(!showCreate)} className="gensui-btn-primary flex items-center gap-1.5 text-xs">
          <Plus size={14} /> Add Admin
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-xs text-red-400">
          <AlertTriangle size={12} /> {error}
        </div>
      )}
      {success && (
        <div className="flex items-center gap-2 text-xs text-emerald-400">
          <Check size={12} /> {success}
        </div>
      )}

      {showCreate && (
        <form onSubmit={handleCreate} className="p-4 bg-gensui-800/50 border border-gensui-700/30 rounded-lg space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs text-gensui-400 mb-1">Email</label>
              <input className="gensui-input w-full" type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="admin@company.com" />
            </div>
            <div>
              <label className="block text-xs text-gensui-400 mb-1">Password</label>
              <input className="gensui-input w-full" type="password" value={password} onChange={e => setPassword(e.target.value)} required minLength={6} placeholder="Min 6 characters" />
            </div>
            <div>
              <label className="block text-xs text-gensui-400 mb-1">Display Name</label>
              <input className="gensui-input w-full" value={displayName} onChange={e => setDisplayName(e.target.value)} placeholder="Display name" />
            </div>
            <div>
              <label className="block text-xs text-gensui-400 mb-1">Role</label>
              <select className="gensui-input w-full" value={role} onChange={e => setRole(e.target.value)}>
                {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
          </div>
          <div className="flex gap-2">
            <button type="submit" className="gensui-btn-primary text-xs">Create Admin</button>
            <button type="button" onClick={() => setShowCreate(false)} className="gensui-btn-secondary text-xs">Cancel</button>
          </div>
        </form>
      )}

      <div className="space-y-2">
        {admins.map(a => (
          <div key={a.id} className="flex items-center justify-between py-2 border-b border-gensui-800/50 last:border-0">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-gensui-700 flex items-center justify-center text-xs font-bold text-gensui-300">
                {(a.display_name || a.email)?.[0]?.toUpperCase()}
              </div>
              <div>
                <p className="text-sm text-gensui-200">{a.display_name || a.email}</p>
                <p className="text-[10px] text-gensui-500">{a.email}</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs px-2 py-0.5 rounded-full border border-cyan-500/30 bg-cyan-500/10 text-cyan-400">{a.role}</span>
              <button onClick={() => handleDeactivate(a.id)} className="p-1.5 text-gensui-500 hover:text-red-400 transition-colors" title="Deactivate">
                <Trash2 size={14} />
              </button>
            </div>
          </div>
        ))}
        {admins.length === 0 && <p className="text-xs text-gensui-500 text-center py-4">No admins found</p>}
      </div>
    </div>
  );
}

export default function Settings() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);

  // Profile form
  const [displayName, setDisplayName] = useState('');
  const [profileSaved, setProfileSaved] = useState(false);
  const [profileError, setProfileError] = useState('');

  // Password form
  const [currentPw, setCurrentPw] = useState('');
  const [newPw, setNewPw] = useState('');
  const [confirmPw, setConfirmPw] = useState('');
  const [pwSaved, setPwSaved] = useState(false);
  const [pwError, setPwError] = useState('');
  const [pwLoading, setPwLoading] = useState(false);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const { data } = await api.get('/auth/me');
        setProfile(data);
        setDisplayName(data.display_name || '');
      } catch {} finally { setLoading(false); }
    };
    fetchProfile();
  }, []);

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileError('');
    setProfileSaved(false);
    try {
      const { data } = await api.patch('/auth/profile', { display_name: displayName });
      setProfile(data);
      setProfileSaved(true);
      setTimeout(() => setProfileSaved(false), 3000);
    } catch (err: any) {
      setProfileError(err.response?.data?.detail || 'Failed to update profile');
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPwError('');
    setPwSaved(false);
    if (newPw !== confirmPw) {
      setPwError('Passwords do not match');
      return;
    }
    if (newPw.length < 6) {
      setPwError('Password must be at least 6 characters');
      return;
    }
    setPwLoading(true);
    try {
      await api.post('/auth/change-password', {
        current_password: currentPw,
        new_password: newPw,
      });
      setPwSaved(true);
      setCurrentPw('');
      setNewPw('');
      setConfirmPw('');
      setTimeout(() => setPwSaved(false), 3000);
    } catch (err: any) {
      setPwError(err.response?.data?.detail || 'Failed to change password');
    } finally {
      setPwLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="w-10 h-10 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h1 className="text-2xl font-bold text-gensui-50 flex items-center gap-3">
          <SettingsIcon size={24} className="text-cyan-400" />
          Settings
        </h1>
        <p className="text-sm text-gensui-400 mt-1">Manage your profile, password, and server configuration</p>
      </div>

      {/* Profile Section */}
      <div className="glass-card p-6 space-y-5">
        <h2 className="text-sm font-bold text-gensui-300 uppercase tracking-widest flex items-center gap-2">
          <User size={14} className="text-cyan-400" /> Profile
        </h2>
        <form onSubmit={handleUpdateProfile} className="space-y-4">
          <div>
            <label className="block text-xs text-gensui-400 mb-1.5">Email</label>
            <input
              type="email"
              className="gensui-input opacity-60 cursor-not-allowed"
              value={profile?.email || ''}
              disabled
            />
          </div>
          <div>
            <label className="block text-xs text-gensui-400 mb-1.5">Role</label>
            <input
              type="text"
              className="gensui-input opacity-60 cursor-not-allowed"
              value={profile?.role || ''}
              disabled
            />
          </div>
          <div>
            <label className="block text-xs text-gensui-400 mb-1.5">Display Name</label>
            <input
              type="text"
              className="gensui-input"
              value={displayName}
              onChange={e => setDisplayName(e.target.value)}
              placeholder="Your display name"
            />
          </div>
          {profileError && (
            <div className="flex items-center gap-2 text-xs text-red-400">
              <AlertTriangle size={12} /> {profileError}
            </div>
          )}
          {profileSaved && (
            <div className="flex items-center gap-2 text-xs text-emerald-400">
              <Check size={12} /> Profile updated successfully
            </div>
          )}
          <button type="submit" className="btn-primary text-sm">
            Save Profile
          </button>
        </form>
      </div>

      {/* Password Section */}
      <div className="glass-card p-6 space-y-5">
        <h2 className="text-sm font-bold text-gensui-300 uppercase tracking-widest flex items-center gap-2">
          <Lock size={14} className="text-amber-400" /> Change Password
        </h2>
        <form onSubmit={handleChangePassword} className="space-y-4">
          <div>
            <label className="block text-xs text-gensui-400 mb-1.5">Current Password</label>
            <input
              type="password"
              className="gensui-input"
              value={currentPw}
              onChange={e => setCurrentPw(e.target.value)}
              placeholder="Enter current password"
              required
            />
          </div>
          <div>
            <label className="block text-xs text-gensui-400 mb-1.5">New Password</label>
            <input
              type="password"
              className="gensui-input"
              value={newPw}
              onChange={e => setNewPw(e.target.value)}
              placeholder="Enter new password (min 6 characters)"
              required
              minLength={6}
            />
          </div>
          <div>
            <label className="block text-xs text-gensui-400 mb-1.5">Confirm New Password</label>
            <input
              type="password"
              className="gensui-input"
              value={confirmPw}
              onChange={e => setConfirmPw(e.target.value)}
              placeholder="Confirm new password"
              required
            />
          </div>
          {pwError && (
            <div className="flex items-center gap-2 text-xs text-red-400">
              <AlertTriangle size={12} /> {pwError}
            </div>
          )}
          {pwSaved && (
            <div className="flex items-center gap-2 text-xs text-emerald-400">
              <Check size={12} /> Password changed successfully
            </div>
          )}
          <button
            type="submit"
            className="btn-primary text-sm"
            disabled={pwLoading}
          >
            {pwLoading ? 'Changing...' : 'Change Password'}
          </button>
        </form>
      </div>

      {/* Admin Management Section */}
      <AdminManagement />

      {/* Server Info Section */}
      <div className="glass-card p-6 space-y-5">
        <h2 className="text-sm font-bold text-gensui-300 uppercase tracking-widest flex items-center gap-2">
          <Server size={14} className="text-purple-400" /> Server Configuration
        </h2>
        <div className="space-y-3 text-sm">
          {[
            { label: 'JWT Token Expiry', value: '24 hours', desc: 'How long admin sessions stay valid' },
            { label: 'Heartbeat Timeout', value: '60 seconds', desc: 'Max time before a Shogun is marked offline' },
            { label: 'Enrollment Approval', value: 'Required', desc: 'New Shoguns must be manually approved' },
            { label: 'Default Posture', value: 'STANDARD', desc: 'Security posture assigned to new members' },
          ].map(item => (
            <div key={item.label} className="flex items-start justify-between py-2 border-b border-gensui-800/50 last:border-0">
              <div>
                <span className="text-gensui-200">{item.label}</span>
                <p className="text-[10px] text-gensui-500 mt-0.5">{item.desc}</p>
              </div>
              <span className="text-xs font-mono text-cyan-400 bg-cyan-500/10 px-2 py-1 rounded">{item.value}</span>
            </div>
          ))}
        </div>
        <p className="text-[10px] text-gensui-600 flex items-center gap-1">
          <Info size={10} /> Server settings are configured via the <code className="text-gensui-400">.env</code> file and require a restart to change.
        </p>
      </div>

      {/* About Section */}
      <div className="glass-card p-6 space-y-3">
        <h2 className="text-sm font-bold text-gensui-300 uppercase tracking-widest flex items-center gap-2">
          <Info size={14} className="text-gensui-400" /> About
        </h2>
        <div className="text-sm space-y-2">
          <div className="flex justify-between">
            <span className="text-gensui-500">Gensui Version</span>
            <span className="text-gensui-200 font-mono text-xs">0.1.0</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gensui-500">Part of</span>
            <span className="text-gensui-200 text-xs">Shogun AFM (Agent Fleet Management)</span>
          </div>
        </div>
      </div>
    </div>
  );
}
