const STORAGE_KEY = 'shogun.samuraiDiagnostics';
const MAX_EVENTS = 250;
const DIAGNOSTIC_BUILD = '1.6.10-build57';

type DiagnosticEvent = {
  ts: string;
  event: string;
  details?: Record<string, unknown>;
};

let globalHandlersInstalled = false;

function readEvents(): DiagnosticEvent[] {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function writeEvents(events: DiagnosticEvent[]) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(events.slice(-MAX_EVENTS)));
  } catch {
    // Ignore storage failures; diagnostics should never break the app.
  }
}

function cleanValue(value: unknown): unknown {
  if (value instanceof Error) {
    return { name: value.name, message: value.message, stack: value.stack };
  }
  if (value && typeof value === 'object') {
    try {
      return JSON.parse(JSON.stringify(value));
    } catch {
      return String(value);
    }
  }
  return value;
}

export function logSamuraiDiagnostic(event: string, details: Record<string, unknown> = {}) {
  if (typeof window === 'undefined') return;
  const entry: DiagnosticEvent = {
    ts: new Date().toISOString(),
    event,
    details: Object.fromEntries(
      Object.entries(details).map(([key, value]) => [key, cleanValue(value)])
    ),
  };
  writeEvents([...readEvents(), entry]);
  console.info('[SamuraiDiagnostics]', entry);
}

export function installSamuraiDiagnostics() {
  if (typeof window === 'undefined' || globalHandlersInstalled) return;
  globalHandlersInstalled = true;

  window.addEventListener('error', (event) => {
    logSamuraiDiagnostic('window.error', {
      message: event.message,
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      error: event.error,
    });
  });

  window.addEventListener('unhandledrejection', (event) => {
    logSamuraiDiagnostic('window.unhandledrejection', {
      reason: event.reason,
    });
  });
}

export function clearSamuraiDiagnostics() {
  writeEvents([]);
  logSamuraiDiagnostic('diagnostics.cleared');
}

export function getSamuraiDiagnosticsText(): string {
  const events = readEvents();
  const header = [
    'SHOGUN SAMURAI DIAGNOSTICS',
    `diagnostic_build=${DIAGNOSTIC_BUILD}`,
    `created_at=${new Date().toISOString()}`,
    `url=${window.location.href}`,
    `user_agent=${navigator.userAgent}`,
    `events=${events.length}`,
    '',
  ];
  return header.concat(events.map((entry) => JSON.stringify(entry))).join('\n');
}

export async function copySamuraiDiagnostics(): Promise<boolean> {
  const text = getSamuraiDiagnosticsText();
  try {
    await navigator.clipboard.writeText(text);
    logSamuraiDiagnostic('diagnostics.copied', { length: text.length });
    return true;
  } catch {
    logSamuraiDiagnostic('diagnostics.copy_failed', { length: text.length });
    return false;
  }
}

export function downloadSamuraiDiagnostics() {
  const text = getSamuraiDiagnosticsText();
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `shogun-samurai-diagnostics-${new Date().toISOString().replace(/[:.]/g, '-')}.txt`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
  logSamuraiDiagnostic('diagnostics.downloaded', { length: text.length });
}

export function getSamuraiDiagnosticBuild() {
  return DIAGNOSTIC_BUILD;
}
