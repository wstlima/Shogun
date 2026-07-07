import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { Shell } from './components/layout/Shell'
import { Dashboard } from './pages/Dashboard'
import { Chat } from './pages/Chat'
import { ShogunProfile } from './pages/ShogunProfile'
import { SamuraiNetwork } from './pages/SamuraiNetwork'
import { Katana } from './pages/Katana'
import { Torii } from './pages/Torii'
import { Kaizen } from './pages/Kaizen'
import { Bushido } from './pages/Bushido'
import { Archives } from './pages/Archives'
import { Dojo } from './pages/Dojo'
import { Logs } from './pages/Logs'
import { Guide } from './pages/Guide'
import { Nexus } from './pages/Nexus'
import { Updates } from './pages/Updates'
import { Backups } from './pages/Backups'
import { Gensui } from './pages/Gensui'
import { SetupWizard } from './pages/SetupWizard'
import { useState, useEffect, useRef } from 'react'
import { useTranslation, I18nProvider } from './i18n'
import { AlertTriangle, Loader2, X } from 'lucide-react'

interface SystemNotification {
  id: string
  title: string
  message: string
  severity: string
}

function SystemNotifications() {
  const [notification, setNotification] = useState<SystemNotification | null>(null)
  const lastSeen = useRef<string | null>(null)

  useEffect(() => {
    let active = true
    const poll = async () => {
      try {
        const suffix = lastSeen.current ? `?after=${encodeURIComponent(lastSeen.current)}` : ''
        const response = await fetch(`/api/v1/system/notifications${suffix}`)
        const payload = await response.json()
        const items: SystemNotification[] = payload.data || []
        if (active && items.length) {
          const latest = items[items.length - 1]
          lastSeen.current = latest.id
          setNotification(latest)
        }
      } catch {
        // Notifications are supplementary; transient polling failures are harmless.
      }
    }
    poll()
    const timer = window.setInterval(poll, 2000)
    return () => {
      active = false
      window.clearInterval(timer)
    }
  }, [])

  useEffect(() => {
    if (!notification) return
    const timer = window.setTimeout(() => setNotification(null), 12000)
    return () => window.clearTimeout(timer)
  }, [notification])

  if (!notification) return null
  return (
    <div className="fixed right-5 top-5 z-[9999] w-[min(440px,calc(100vw-2.5rem))] rounded-xl border border-amber-400/50 bg-[#15120a] p-4 shadow-2xl shadow-amber-500/20">
      <div className="flex items-start gap-3">
        <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-400" />
        <div className="min-w-0 flex-1">
          <p className="font-bold text-amber-200">{notification.title}</p>
          <p className="mt-1 text-sm leading-relaxed text-amber-50/80">{notification.message}</p>
        </div>
        <button onClick={() => setNotification(null)} className="text-amber-100/60 hover:text-amber-100" aria-label="Dismiss notification">
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}

function BuildRefreshGuard() {
  useEffect(() => {
    let active = true
    const storageKey = 'shogun_loaded_build'

    const checkBuild = async () => {
      try {
        const response = await fetch('/api/v1/health', { cache: 'no-store' })
        const payload = await response.json()
        const currentBuild = payload?.build != null ? String(payload.build) : null
        if (!active || !currentBuild) return

        const previousBuild = sessionStorage.getItem(storageKey)
        sessionStorage.setItem(storageKey, currentBuild)

        if (previousBuild && previousBuild !== currentBuild) {
          window.location.reload()
        }
      } catch {
        // The app can still run while the server is warming up.
      }
    }

    checkBuild()
    const timer = window.setInterval(checkBuild, 5000)
    return () => {
      active = false
      window.clearInterval(timer)
    }
  }, [])

  return null
}

/**
 * Wrapper that checks first-run status and redirects to /setup if needed.
 * Only affects the "/" route on initial load.
 */
function FirstRunGate({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = useState<'loading' | 'first_run' | 'ready'>('loading')
  const location = useLocation()
  const { setLanguage } = useTranslation()

  useEffect(() => {
    // Only check once, only on initial page load
    fetch('/api/v1/setup/status')
      .then(r => r.json())
      .then(d => {
        const complete = d.data?.setup_complete ?? true
        if (d.data?.language) {
          setLanguage(d.data.language)
        }
        if (d.data?.operator_name) {
          localStorage.setItem('shogun_operator_name', d.data.operator_name)
        }
        setStatus(complete ? 'ready' : 'first_run')
      })
      .catch(() => setStatus('ready'))
  }, [setLanguage])

  if (status === 'loading') {
    return (
      <div className="fixed inset-0 bg-[#0a0e1a] flex flex-col items-center justify-center gap-4">
        <Loader2 className="w-8 h-8 text-[#d4a017] animate-spin" />
        <p className="text-sm text-[#555] font-mono tracking-widest uppercase">Initializing Shogun...</p>
      </div>
    )
  }

  // First run: redirect to /setup (unless already on /setup)
  if (status === 'first_run' && location.pathname !== '/setup') {
    return <Navigate to="/setup" replace />
  }

  return <>{children}</>
}

/**
 * Setup page wrapper — handles completion and redirect.
 */
function SetupPage() {
  return (
    <SetupWizard onComplete={() => {
      window.location.href = '/guide'
    }} />
  )
}

function AppContent() {
  return (
    <Router>
      <FirstRunGate>
        <Routes>
          {/* Setup wizard — always accessible at /setup */}
          <Route path="/setup" element={<SetupPage />} />

          {/* Main Tenshu routes (wrapped in Shell) */}
          <Route path="/" element={<Shell><Dashboard /></Shell>} />
          <Route path="/chat" element={<Shell><Chat /></Shell>} />
          <Route path="/shogun" element={<Shell><ShogunProfile /></Shell>} />
          <Route path="/samurai" element={<Shell><SamuraiNetwork /></Shell>} />
          <Route path="/katana" element={<Shell><Katana /></Shell>} />
          <Route path="/torii" element={<Shell><Torii /></Shell>} />
          <Route path="/kaizen" element={<Shell><Kaizen /></Shell>} />
          <Route path="/bushido" element={<Shell><Bushido /></Shell>} />
          <Route path="/archives" element={<Shell><Archives /></Shell>} />
          <Route path="/dojo" element={<Shell><Dojo /></Shell>} />
          <Route path="/logs" element={<Shell><Logs /></Shell>} />
          <Route path="/guide" element={<Shell><Guide /></Shell>} />
          <Route path="/nexus" element={<Shell><Nexus /></Shell>} />
          <Route path="/updates" element={<Shell><Updates /></Shell>} />
          <Route path="/backups" element={<Shell><Backups /></Shell>} />
          <Route path="/gensui" element={<Shell><Gensui /></Shell>} />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </FirstRunGate>
    </Router>
  )
}

function App() {
  return (
    <I18nProvider>
      <BuildRefreshGuard />
      <AppContent />
      <SystemNotifications />
    </I18nProvider>
  )
}

export default App
