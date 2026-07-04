import { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Activity, AlertTriangle, CheckCircle2, Download, FileCheck2, Loader2,
  MessageSquare, RefreshCw, Save, ShieldCheck, Users, Wrench,
} from 'lucide-react';
import { cn } from '../../lib/utils';

const allCommands = ['help', 'status', 'agents', 'workflows', 'approvals', 'ask', 'run', 'pause', 'resume', 'summarize', 'logs', 'approve', 'reject', 'harakiri'];
const defaults = {
  enabled: false, deployment_mode: 'dev', tenant_mode: 'single',
  allowed_tenant_ids: [] as string[], bot_app_id: '', bot_name: 'Shogun',
  client_secret_ref: '', public_messaging_endpoint: '', valid_domains: [] as string[],
  graph_enabled: false, proactive_enabled: false, sso_enabled: false,
  allowed_commands: allCommands, allowed_channels: [] as string[],
  destructive_commands_enabled: false, dual_approval_fleet: true, approval_ttl_seconds: 900,
};
type Section = 'overview' | 'setup' | 'identity' | 'security' | 'audit' | 'diagnostics';

function Toggle({ value, onChange, label, hint }: { value: boolean; onChange: (v: boolean) => void; label: string; hint?: string }) {
  return <button type="button" onClick={() => onChange(!value)} className="w-full flex items-center justify-between gap-4 text-left">
    <span><span className="block text-sm font-bold text-shogun-text">{label}</span>{hint && <span className="block text-[10px] text-shogun-subdued mt-0.5">{hint}</span>}</span>
    <span className={cn('relative w-10 h-5 rounded-full border transition-all shrink-0', value ? 'bg-shogun-blue border-shogun-blue' : 'bg-[#050508] border-shogun-border')}>
      <span className={cn('absolute top-0.5 w-3.5 h-3.5 rounded-full bg-white transition-all', value ? 'left-5' : 'left-0.5')} />
    </span>
  </button>;
}

export function MicrosoftTeamsAdapterTab() {
  const [section, setSection] = useState<Section>('overview');
  const [config, setConfig] = useState<any>(defaults);
  const [health, setHealth] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState<{ ok: boolean; text: string } | null>(null);
  const [testResult, setTestResult] = useState<any>(null);

  const load = async () => {
    setLoading(true);
    try {
      const [cfg, status] = await Promise.all([
        axios.get('/api/v1/katana/teams/config'), axios.get('/api/v1/katana/teams/health'),
      ]);
      setConfig({ ...defaults, ...(cfg.data.data || {}) });
      setHealth(status.data.data);
    } catch { setNotice({ ok: false, text: 'Could not load the Teams adapter configuration.' }); }
    finally { setLoading(false); }
  };
  useEffect(() => { load(); }, []);
  useEffect(() => {
    if (section === 'identity') axios.get('/api/v1/katana/teams/users').then(r => setUsers(r.data.data || []));
    if (section === 'audit') axios.get('/api/v1/katana/teams/commands').then(r => setLogs(r.data.data || []));
  }, [section]);

  const save = async () => {
    setSaving(true);
    try {
      const payload = { ...defaults, ...config };
      ['id', 'created_at', 'updated_at', 'last_inbound_at', 'last_outbound_at', 'last_error'].forEach(k => delete payload[k]);
      const response = await axios.put('/api/v1/katana/teams/config', payload);
      setConfig(response.data.data); setNotice({ ok: true, text: 'Microsoft Teams configuration saved.' });
    } catch (error: any) {
      setNotice({ ok: false, text: error.response?.data?.detail?.[0]?.msg || 'Configuration could not be saved.' });
    } finally { setSaving(false); setTimeout(() => setNotice(null), 4000); }
  };
  const setEnabled = async (enabled: boolean) => {
    try {
      await axios.post(`/api/v1/katana/teams/${enabled ? 'enable' : 'disable'}`);
      setConfig((v: any) => ({ ...v, enabled })); await load();
    } catch { setNotice({ ok: false, text: 'Adapter state could not be changed.' }); }
  };
  const download = async (path: string, filename: string) => {
    try {
      const response = await axios({ url: `/api/v1/katana/teams/${path}`, method: path.includes('download') ? 'GET' : 'POST', responseType: 'blob' });
      const url = URL.createObjectURL(response.data); const a = document.createElement('a');
      a.href = url; a.download = filename; a.click(); URL.revokeObjectURL(url);
    } catch { setNotice({ ok: false, text: 'The requested package could not be generated.' }); }
  };
  const input = 'w-full bg-[#050508] border border-shogun-border rounded-lg px-3 py-2.5 text-sm text-shogun-text focus:border-shogun-blue outline-none';
  const label = 'text-[10px] font-bold uppercase tracking-widest text-shogun-subdued';
  const sections: { id: Section; name: string; icon: any }[] = [
    { id: 'overview', name: 'Overview', icon: Activity }, { id: 'setup', name: 'Setup Wizard', icon: Wrench },
    { id: 'identity', name: 'Entra & Roles', icon: Users }, { id: 'security', name: 'Security Policy', icon: ShieldCheck },
    { id: 'audit', name: 'Audit Log', icon: FileCheck2 }, { id: 'diagnostics', name: 'Diagnostics', icon: RefreshCw },
  ];
  if (loading) return <div className="py-24 flex justify-center"><Loader2 className="w-7 h-7 text-shogun-blue animate-spin" /></div>;

  return <div className="space-y-5 animate-in fade-in duration-300">
    <div className="flex flex-wrap items-center justify-between gap-4">
      <div><h3 className="text-lg font-bold flex items-center gap-2 text-shogun-text"><MessageSquare className="w-5 h-5 text-[#7B83EB]" /> Microsoft Teams Adapter</h3>
        <p className="text-xs text-shogun-subdued mt-1">Enterprise command channel governed by Katana and Gensui.</p></div>
      <div className="flex items-center gap-3">
        <span className={cn('px-3 py-1.5 rounded-lg border text-[10px] font-bold uppercase tracking-widest', health?.status === 'healthy' ? 'bg-green-400/10 border-green-400/30 text-green-400' : 'bg-amber-400/10 border-amber-400/30 text-amber-400')}>
          {health?.status === 'healthy' ? 'Production ready' : config.enabled ? 'Needs attention' : 'Disabled'}</span>
        <button onClick={() => setEnabled(!config.enabled)} className={cn('px-4 py-2 rounded-lg text-xs font-bold border', config.enabled ? 'border-red-400/30 text-red-400' : 'border-green-400/30 text-green-400')}>{config.enabled ? 'Disable adapter' : 'Enable adapter'}</button>
      </div>
    </div>
    {notice && <div className={cn('p-3 rounded-lg border text-sm flex items-center gap-2', notice.ok ? 'bg-green-400/10 border-green-400/20 text-green-400' : 'bg-red-400/10 border-red-400/20 text-red-400')}>
      {notice.ok ? <CheckCircle2 className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}{notice.text}</div>}

    <div className="grid grid-cols-1 xl:grid-cols-[220px_1fr] gap-5">
      <div className="shogun-card p-2 h-fit">{sections.map(({ id, name, icon: Icon }) => <button key={id} onClick={() => setSection(id)}
        className={cn('w-full flex items-center gap-2.5 px-3 py-2.5 rounded-lg text-xs font-bold', section === id ? 'bg-shogun-blue/15 text-shogun-blue' : 'text-shogun-subdued hover:text-shogun-text')}>
        <Icon className="w-4 h-4" />{name}</button>)}</div>

      <div className="space-y-5">
        {section === 'overview' && <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">{[
            ['Adapter', config.enabled ? 'Enabled' : 'Disabled'], ['Tenant', health?.tenant_status || 'Unknown'],
            ['SSO', health?.sso_status || 'Disabled'], ['Approvals', String(health?.active_approvals ?? 0)],
          ].map(([k, v]) => <div key={k} className="shogun-card"><p className={label}>{k}</p><p className="text-lg font-bold text-shogun-text mt-2 capitalize">{v}</p></div>)}</div>
          <div className="shogun-card space-y-4"><h4 className="font-bold text-sm text-shogun-text">Connection health</h4>
            {(health?.issues || []).length ? health.issues.map((issue: string) => <div key={issue} className="flex items-center gap-2 text-xs text-amber-400"><AlertTriangle className="w-3.5 h-3.5" />{issue}</div>)
              : <div className="flex items-center gap-2 text-xs text-green-400"><CheckCircle2 className="w-4 h-4" />Configuration checks passed.</div>}
          </div>
        </>}

        {section === 'setup' && <>
          <div className="shogun-card space-y-5"><div><h4 className="font-bold text-shogun-text">1. Deployment and tenant</h4><p className="text-[10px] text-shogun-subdued mt-1">A customer-hosted bridge is recommended for production.</p></div>
            <div className="grid md:grid-cols-2 gap-4">
              <div><label className={label}>Deployment mode</label><select value={config.deployment_mode} onChange={e => setConfig({ ...config, deployment_mode: e.target.value })} className={cn(input, 'mt-1.5')}><option value="dev">Local development + tunnel</option><option value="bridge">Customer-hosted Teams Bridge</option><option value="direct">Direct Shogun callback</option></select></div>
              <div><label className={label}>Tenant mode</label><select value={config.tenant_mode} onChange={e => setConfig({ ...config, tenant_mode: e.target.value })} className={cn(input, 'mt-1.5')}><option value="single">Single tenant</option><option value="multi">Multi tenant</option></select></div>
            </div>
            <div><label className={label}>Allowed tenant IDs (one per line)</label><textarea value={(config.allowed_tenant_ids || []).join('\n')} onChange={e => setConfig({ ...config, allowed_tenant_ids: e.target.value.split(/\s+/).filter(Boolean) })} rows={3} className={cn(input, 'mt-1.5 font-mono')} /></div>
          </div>
          <div className="shogun-card space-y-5"><h4 className="font-bold text-shogun-text">2. Bot and public endpoint</h4>
            <div className="grid md:grid-cols-2 gap-4"><div><label className={label}>Bot / App ID</label><input value={config.bot_app_id || ''} onChange={e => setConfig({ ...config, bot_app_id: e.target.value })} className={cn(input, 'mt-1.5 font-mono')} /></div>
              <div><label className={label}>Bot display name</label><input value={config.bot_name || ''} onChange={e => setConfig({ ...config, bot_name: e.target.value })} className={cn(input, 'mt-1.5')} /></div></div>
            <div><label className={label}>Client secret / certificate reference</label><input value={config.client_secret_ref || ''} onChange={e => setConfig({ ...config, client_secret_ref: e.target.value })} className={cn(input, 'mt-1.5 font-mono')} placeholder="vault://teams/bot-client-secret" /><p className="text-[9px] text-shogun-subdued mt-1">Only a secret reference is stored. Never paste the secret value here.</p></div>
            <div><label className={label}>Public messaging endpoint</label><input value={config.public_messaging_endpoint || ''} onChange={e => setConfig({ ...config, public_messaging_endpoint: e.target.value })} className={cn(input, 'mt-1.5 font-mono')} placeholder="https://teams-bridge.example.com/api/teams/messages" /></div>
            <div><label className={label}>Valid domains (comma separated)</label><input value={(config.valid_domains || []).join(', ')} onChange={e => setConfig({ ...config, valid_domains: e.target.value.split(',').map(x => x.trim()).filter(Boolean) })} className={cn(input, 'mt-1.5 font-mono')} /></div>
          </div>
          <div className="shogun-card flex flex-wrap gap-3"><button onClick={save} disabled={saving} className="px-4 py-2.5 bg-shogun-blue text-white rounded-lg text-xs font-bold flex items-center gap-2">{saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}Save configuration</button>
            <button onClick={() => download('manifest/download', 'shogun-teams-app.zip')} className="px-4 py-2.5 border border-shogun-border rounded-lg text-xs font-bold text-shogun-text flex items-center gap-2"><Download className="w-4 h-4" />Generate Teams app package</button></div>
        </>}

        {section === 'identity' && <div className="shogun-card space-y-5">
          <div className="grid md:grid-cols-3 gap-5 pb-4 border-b border-shogun-border"><Toggle label="Microsoft Entra SSO" hint="Required for production identity assurance." value={config.sso_enabled} onChange={v => setConfig({ ...config, sso_enabled: v })} />
            <Toggle label="Microsoft Graph" hint="Tenant app operations." value={config.graph_enabled} onChange={v => setConfig({ ...config, graph_enabled: v })} />
            <Toggle label="Proactive messaging" hint="Installed conversations only." value={config.proactive_enabled} onChange={v => setConfig({ ...config, proactive_enabled: v })} /></div>
          <div><h4 className="font-bold text-shogun-text">Teams user mappings</h4><p className="text-[10px] text-shogun-subdued">New identities enter as Viewer until deliberately promoted.</p></div>
          <div className="overflow-x-auto"><table className="w-full text-xs"><thead><tr className="text-left text-shogun-subdued border-b border-shogun-border"><th className="py-2">User</th><th>UPN</th><th>Tenant</th><th>Role</th></tr></thead>
            <tbody>{users.map(u => <tr key={u.id} className="border-b border-shogun-border/50"><td className="py-3 text-shogun-text font-bold">{u.display_name}</td><td>{u.user_principal_name || '—'}</td><td className="font-mono">{u.tenant_id}</td><td className="capitalize">{u.shogun_role.replace('_', ' ')}</td></tr>)}</tbody></table>
            {!users.length && <p className="text-center py-10 text-shogun-subdued italic">No Teams identities observed yet.</p>}</div>
          <button onClick={save} className="px-4 py-2.5 bg-shogun-blue text-white rounded-lg text-xs font-bold flex items-center gap-2"><Save className="w-4 h-4" />Save identity settings</button>
        </div>}

        {section === 'security' && <div className="space-y-5">
          <div className="shogun-card space-y-4"><h4 className="font-bold text-shogun-text">Command policy</h4><div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2">{allCommands.map(cmd => {
            const enabled = config.allowed_commands?.includes(cmd); return <button key={cmd} onClick={() => setConfig({ ...config, allowed_commands: enabled ? config.allowed_commands.filter((x: string) => x !== cmd) : [...config.allowed_commands, cmd] })}
              className={cn('px-3 py-2 rounded-lg border text-xs text-left capitalize', enabled ? 'border-shogun-blue/30 bg-shogun-blue/10 text-shogun-blue' : 'border-shogun-border text-shogun-subdued')}>{cmd}<span className="float-right">{['harakiri', 'pause', 'resume'].includes(cmd) ? 'L4' : ['approve', 'reject'].includes(cmd) ? 'L3' : 'L0–L2'}</span></button>;
          })}</div></div>
          <div className="shogun-card space-y-5"><Toggle label="Allow destructive commands to enter approval flow" hint="This never bypasses Gensui confirmation." value={config.destructive_commands_enabled} onChange={v => setConfig({ ...config, destructive_commands_enabled: v })} />
            <Toggle label="Dual approval for fleet shutdown" value={config.dual_approval_fleet} onChange={v => setConfig({ ...config, dual_approval_fleet: v })} />
            <div><label className={label}>Approval expiry (seconds)</label><input type="number" min={60} max={86400} value={config.approval_ttl_seconds} onChange={e => setConfig({ ...config, approval_ttl_seconds: Number(e.target.value) })} className={cn(input, 'mt-1.5 max-w-xs')} /></div>
            <div className="p-3 rounded-lg border border-amber-400/20 bg-amber-400/5 text-xs text-amber-300">Attachments are rejected by default. High-risk free-form input cannot invoke tools directly.</div>
            <button onClick={save} className="px-4 py-2.5 bg-shogun-blue text-white rounded-lg text-xs font-bold flex items-center gap-2"><Save className="w-4 h-4" />Save security policy</button></div>
        </div>}

        {section === 'audit' && <div className="shogun-card"><div className="flex justify-between mb-4"><div><h4 className="font-bold text-shogun-text">Command audit</h4><p className="text-[10px] text-shogun-subdued">Authorization decisions and outcomes.</p></div>
          <button onClick={() => download('diagnostics/export', 'shogun-teams-diagnostics.json')} className="text-xs text-shogun-blue flex items-center gap-1"><Download className="w-3.5 h-3.5" />Export safe bundle</button></div>
          <div className="overflow-x-auto"><table className="w-full text-xs"><thead><tr className="text-left text-shogun-subdued border-b border-shogun-border"><th className="py-2">Time</th><th>Command</th><th>Risk</th><th>Decision</th><th>Correlation</th></tr></thead><tbody>
            {logs.map(row => <tr key={row.id} className="border-b border-shogun-border/50"><td className="py-3">{new Date(row.created_at).toLocaleString()}</td><td>{row.command_name}</td><td>{row.risk_level}</td><td className={row.success ? 'text-green-400' : 'text-red-400'}>{row.authorization_result}</td><td className="font-mono">{row.correlation_id.slice(0, 8)}…</td></tr>)}</tbody></table>
            {!logs.length && <p className="text-center py-10 text-shogun-subdued italic">No Teams commands audited yet.</p>}</div></div>}

        {section === 'diagnostics' && <div className="grid md:grid-cols-2 gap-4">{[
          ['Shogun backend', 'test/backend'], ['Microsoft Graph credentials', 'test/graph'],
          ['Proactive messaging', 'test/proactive-message'], ['Teams manifest', 'manifest/validate'],
        ].map(([name, path]) => <div key={path} className="shogun-card"><h4 className="text-sm font-bold text-shogun-text">{name}</h4><p className="text-[10px] text-shogun-subdued mt-1 mb-4">Run a non-destructive configuration check.</p>
          <button onClick={async () => { try { const r = await axios.post(`/api/v1/katana/teams/${path}`); setTestResult({ name, ...r.data.data }); } catch (e: any) { setTestResult({ name, ok: false, error: e.message }); } }}
            className="px-3 py-2 border border-shogun-border rounded-lg text-xs font-bold text-shogun-text">Run test</button></div>)}
          {testResult && <div className="md:col-span-2 shogun-card"><h4 className="text-sm font-bold">{testResult.name}</h4><pre className="mt-3 p-3 bg-[#050508] rounded-lg text-[10px] text-shogun-subdued overflow-auto">{JSON.stringify(testResult, null, 2)}</pre></div>}</div>}
      </div>
    </div>
  </div>;
}
