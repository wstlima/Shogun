import { useEffect, useState } from 'react';
import { AlertTriangle, Shield } from 'lucide-react';
import api from '../../lib/api';

export default function Header() {
  const [globalPosture, setGlobalPosture] = useState<any>(null);

  useEffect(() => {
    const fetchGlobal = async () => {
      try {
        const { data } = await api.get('/policy/global');
        setGlobalPosture(data);
      } catch {}
    };
    fetchGlobal();
    const interval = setInterval(fetchGlobal, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      {/* Global Posture Banner */}
      {globalPosture?.is_active && (
        <div className={`global-posture-banner ${
          globalPosture.posture_name === 'LOCKDOWN' ? 'lockdown' :
          globalPosture.posture_name === 'RESTRICTED' ? 'restricted' : 'lockdown'
        }`}>
          <div className="flex items-center justify-center gap-2">
            <AlertTriangle size={16} />
            <span>GLOBAL POSTURE ACTIVE: {globalPosture.posture_name}</span>
            {globalPosture.reason && <span className="opacity-70">— {globalPosture.reason}</span>}
          </div>
        </div>
      )}

      {/* Top Header Bar */}
      <header className="flex items-center justify-between px-6 py-3 border-b border-gensui-700/30 bg-gensui-800/20">
        <div className="flex items-center gap-3">
          <Shield size={16} className="text-gensui-500" />
          <span className="text-xs text-gensui-500 uppercase tracking-wider">Central Command</span>
        </div>
        <div className="flex items-center gap-4">
          {globalPosture?.is_active ? (
            <span className="status-badge harakiri">
              <span className="w-2 h-2 rounded-full bg-crimson-400 animate-pulse"></span>
              Global Override
            </span>
          ) : (
            <span className="status-badge online">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              Normal Operations
            </span>
          )}
        </div>
      </header>
    </>
  );
}
