import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { isAuthenticated } from './lib/auth';
import Layout from './components/layout/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Fleet from './pages/Fleet';
import ShogunDetail from './pages/ShogunDetail';
import NetworkTopology from './pages/NetworkTopology';
import Groups from './pages/Groups';
import Postures from './pages/Postures';
import HarakiriControl from './pages/HarakiriControl';
import ActivityMonitor from './pages/ActivityMonitor';
import AuditLog from './pages/AuditLog';
import Alerts from './pages/Alerts';
import Enrollment from './pages/Enrollment';
import Settings from './pages/Settings';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  return isAuthenticated() ? <>{children}</> : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="fleet" element={<Fleet />} />
          <Route path="fleet/:id" element={<ShogunDetail />} />
          <Route path="network" element={<NetworkTopology />} />
          <Route path="groups" element={<Groups />} />
          <Route path="postures" element={<Postures />} />
          <Route path="harakiri" element={<HarakiriControl />} />
          <Route path="activity" element={<ActivityMonitor />} />
          <Route path="audit" element={<AuditLog />} />
          <Route path="alerts" element={<Alerts />} />
          <Route path="enrollment" element={<Enrollment />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
