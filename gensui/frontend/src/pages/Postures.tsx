import { useEffect, useState } from 'react';
import api from '../lib/api';

export default function Postures() {
  const [postures, setPostures] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/postures').then(r => { setPostures(r.data || []); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const permKeys = [
    'allow_external_models', 'allow_local_models', 'allow_tool_execution', 'allow_mado',
    'allow_memory_write', 'allow_memory_read', 'allow_agent_flow', 'allow_nexus',
    'allow_samurai_delegation', 'allow_scheduled_triggers', 'allow_autonomous_loops',
    'allow_external_web', 'allow_file_write', 'allow_external_api',
  ];

  const shortLabel = (k: string) => k.replace('allow_', '').replace(/_/g, ' ');

  return (
    <div className="space-y-6 max-w-7xl">
      <div>
        <h1 className="text-2xl font-bold text-gensui-50">Security Postures</h1>
        <p className="text-sm text-gensui-400 mt-1">Define what Shogun instances are allowed to do</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-16">
          <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {postures.map(p => (
            <div key={p.id} className="glass-card p-5">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h3 className="font-bold text-gensui-100">{p.name}</h3>
                  <p className="text-xs text-gensui-500 mt-0.5">Level {p.level}</p>
                </div>
                {p.is_builtin && (
                  <span className="text-[10px] uppercase tracking-wider text-gensui-500 bg-gensui-700/50 px-2 py-0.5 rounded-full">Built-in</span>
                )}
              </div>
              <p className="text-xs text-gensui-400 mb-4 line-clamp-2">{p.description}</p>
              <div className="flex flex-wrap gap-1.5">
                {permKeys.map(k => (
                  <span key={k} className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                    p[k] ? 'bg-emerald-500/10 text-emerald-400' : 'bg-crimson-500/10 text-crimson-400'
                  }`}>
                    {p[k] ? '✓' : '✕'} {shortLabel(k)}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
