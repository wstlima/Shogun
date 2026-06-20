import { useEffect, useState, useCallback } from 'react';
import { Plus, Trash2, Users, Shield, X, UserPlus, RefreshCw } from 'lucide-react';
import api from '../lib/api';

interface Group {
  id: string; name: string; description: string | null;
  posture_id: string | null; member_count: number;
}
interface Member {
  id: string; instance_name: string; status: string; harakiri_state: string;
}
interface Posture {
  id: string; name: string; level: number;
}
interface FleetMember {
  id: string; instance_name: string; status: string; enrollment_status: string;
}

export default function Groups() {
  const [groups, setGroups] = useState<Group[]>([]);
  const [postures, setPostures] = useState<Posture[]>([]);
  const [fleetMembers, setFleetMembers] = useState<FleetMember[]>([]);
  const [newName, setNewName] = useState('');
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [groupMembers, setGroupMembers] = useState<Member[]>([]);
  const [loadingMembers, setLoadingMembers] = useState(false);

  const load = useCallback(async () => {
    try {
      const [gRes, pRes, mRes] = await Promise.all([
        api.get('/monitoring/groups'),
        api.get('/postures'),
        api.get('/members', { params: { limit: 200 } }),
      ]);
      setGroups(gRes.data || []);
      setPostures(pRes.data || []);
      setFleetMembers((mRes.data.members || []).filter((m: FleetMember) => m.enrollment_status === 'active'));
    } catch {} finally { setLoading(false); }
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleCreate = async () => {
    if (!newName) return;
    await api.post('/monitoring/groups', { name: newName });
    setNewName('');
    load();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this group?')) return;
    await api.delete(`/monitoring/groups/${id}`);
    if (expanded === id) setExpanded(null);
    load();
  };

  const toggleExpand = async (id: string) => {
    if (expanded === id) { setExpanded(null); return; }
    setExpanded(id);
    setLoadingMembers(true);
    try {
      const r = await api.get(`/monitoring/groups/${id}/members`);
      setGroupMembers(r.data || []);
    } catch {} finally { setLoadingMembers(false); }
  };

  const addMember = async (groupId: string, shogunId: string) => {
    try {
      await api.post(`/monitoring/groups/${groupId}/members`, { shogun_id: shogunId });
      toggleExpand(groupId);
      load();
    } catch (e: any) { alert(e.response?.data?.detail || 'Failed to add member'); }
  };

  const removeMember = async (groupId: string, shogunId: string) => {
    try {
      await api.delete(`/monitoring/groups/${groupId}/members/${shogunId}`);
      toggleExpand(groupId);
      load();
    } catch {}
  };

  const assignPosture = async (groupId: string, postureId: string | null) => {
    try {
      await api.post(`/monitoring/groups/${groupId}/posture`, { posture_id: postureId });
      load();
    } catch (e: any) { alert(e.response?.data?.detail || 'Failed to assign posture'); }
  };

  const getPostureName = (id: string | null) => {
    if (!id) return 'None';
    return postures.find(p => p.id === id)?.name || 'Unknown';
  };

  // Members not already in the expanded group
  const availableMembers = expanded
    ? fleetMembers.filter(fm => !groupMembers.some(gm => gm.id === fm.id))
    : [];

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold text-gensui-50">Groups</h1>
        <p className="text-sm text-gensui-400 mt-1">Organize Shogun instances for collective policy management</p>
      </div>

      <div className="flex gap-2">
        <input className="gensui-input flex-1 max-w-sm" placeholder="New group name..." value={newName} onChange={e => setNewName(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') handleCreate(); }}
        />
        <button onClick={handleCreate} disabled={!newName} className="gensui-btn-primary flex items-center gap-2 text-sm"><Plus size={16} /> Create Group</button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><RefreshCw className="animate-spin text-gensui-500" size={24} /></div>
      ) : (
        <div className="space-y-4">
          {groups.map(g => (
            <div key={g.id} className="glass-card overflow-hidden">
              {/* Group Header */}
              <div className="p-5 flex items-center justify-between cursor-pointer hover:bg-gensui-800/30 transition-colors" onClick={() => toggleExpand(g.id)}>
                <div className="flex items-center gap-3">
                  <Users size={18} className="text-purple-400" />
                  <div>
                    <h3 className="font-semibold text-gensui-100">{g.name}</h3>
                    <p className="text-xs text-gensui-500 mt-0.5">
                      {g.member_count} member{g.member_count !== 1 ? 's' : ''}
                      {g.description ? ` — ${g.description}` : ''}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {/* Posture Select */}
                  <div className="flex items-center gap-2" onClick={e => e.stopPropagation()}>
                    <Shield size={14} className="text-amber-400" />
                    <select
                      value={g.posture_id || ''}
                      onChange={e => assignPosture(g.id, e.target.value || null)}
                      className="gensui-input text-xs py-1 px-2 w-40"
                    >
                      <option value="">No Posture</option>
                      {postures.map(p => <option key={p.id} value={p.id}>{p.name} (L{p.level})</option>)}
                    </select>
                  </div>
                  <button onClick={e => { e.stopPropagation(); handleDelete(g.id); }} className="p-2 text-gensui-500 hover:text-red-400 transition-colors">
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>

              {/* Expanded: Members */}
              {expanded === g.id && (
                <div className="border-t border-gensui-700/30 p-5 space-y-4">
                  {loadingMembers ? (
                    <div className="flex justify-center py-4"><RefreshCw className="animate-spin text-gensui-500" size={16} /></div>
                  ) : (
                    <>
                      {/* Current Members */}
                      <div>
                        <h4 className="text-xs font-bold text-gensui-300 uppercase tracking-wider mb-2">Members</h4>
                        {groupMembers.length > 0 ? (
                          <div className="flex flex-wrap gap-2">
                            {groupMembers.map(m => (
                              <div key={m.id} className="flex items-center gap-2 bg-gensui-800/50 border border-gensui-700/30 rounded-lg px-3 py-1.5">
                                <span className={`w-2 h-2 rounded-full ${m.status === 'online' ? 'bg-emerald-400' : 'bg-gensui-500'}`} />
                                <span className="text-xs text-gensui-200">{m.instance_name}</span>
                                <button onClick={() => removeMember(g.id, m.id)} className="text-gensui-500 hover:text-red-400 transition-colors">
                                  <X size={12} />
                                </button>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-xs text-gensui-500">No members in this group</p>
                        )}
                      </div>

                      {/* Add Member */}
                      {availableMembers.length > 0 && (
                        <div>
                          <h4 className="text-xs font-bold text-gensui-300 uppercase tracking-wider mb-2">Add Member</h4>
                          <div className="flex flex-wrap gap-2">
                            {availableMembers.map(fm => (
                              <button
                                key={fm.id}
                                onClick={() => addMember(g.id, fm.id)}
                                className="flex items-center gap-1.5 bg-gensui-800/30 border border-gensui-700/20 rounded-lg px-3 py-1.5 text-xs text-gensui-400 hover:text-gensui-200 hover:border-cyan-500/30 transition-colors"
                              >
                                <UserPlus size={12} /> {fm.instance_name}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </div>
              )}
            </div>
          ))}
          {groups.length === 0 && (
            <div className="text-center py-12 text-gensui-500">No groups created yet</div>
          )}
        </div>
      )}
    </div>
  );
}
