import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import SetupWizard from './pages/wizard/SetupWizard';
import Dashboard from './pages/Dashboard';
import './index.css';

/**
 * App — root router.
 *
 * Current routes (M2):
 *   /setup      → Setup Wizard (M2)
 *   /dashboard  → Dashboard (placeholder; full implementation in M7)
 *   /           → Redirects to /setup (first-run experience for MVP)
 *
 * Future routes (added in their respective milestones):
 *   /calendar, /daily, /subjects, /timeline, /settings, /timetable, /events
 */
function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/setup" element={<SetupWizard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        {/* Default: redirect to setup wizard for first-run MVP */}
        <Route path="*" element={<Navigate to="/setup" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
