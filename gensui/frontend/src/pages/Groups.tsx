import { useEffect, useState } from 'react';
import { Plus, Trash2 } from 'lucide-react';
import api from '../lib/api';

export default function Groups() {
  const [groups, setGroups] = useState<any[]>([]);
  const [newName, setNewName] = useState('');
  const [loading, setLoading] = useState(true);

  const fetch = async () => {
    try {
      const { data } = await api.get('/monitoring/groups');
      setGroups(data || []);
    } catch {} finally { setLoading(false); }
  };

  useEffect(() => { fetch(); }, []);

  const handleCreate = async () => {
    if (!newName) return;
    await api.post('/monitoring/groups', { name: newName });
    setNewName('');
    fetch();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this group?')) return;
    await api.delete(`/monitoring/groups/${id}`);
    fetch();
  };

  return (
    <div className="space-y-6 max-w-5xl">
      <div>
        <h1 className="text-2xl font-bold text-gensui-50">Groups</h1>
        <p className="text-sm text-gensui-400 mt-1">Organize Shogun instances for collective policy management</p>
      </div>

      <div className="flex gap-2">
        <input className="gensui-input flex-1 max-w-sm" placeholder="New group name..." value={newName} onChange={e => setNewName(e.target.value)} />
        <button onClick={handleCreate} className="btn-primary flex items-center gap-2"><Plus size={16} /> Create Group</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {groups.map(g => (
          <div key={g.id} className="glass-card p-5 flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-gensui-100">{g.name}</h3>
              <p className="text-xs text-gensui-500 mt-1">{g.member_count} members{g.description ? ` — ${g.description}` : ''}</p>
            </div>
            <button onClick={() => handleDelete(g.id)} className="p-2 text-gensui-500 hover:text-crimson-400 transition-colors"><Trash2 size={16} /></button>
          </div>
        ))}
        {groups.length === 0 && (
          <div className="col-span-2 text-center py-8 text-gensui-500">No groups created yet</div>
        )}
      </div>
    </div>
  );
}
