/**
 * Dashboard — placeholder for Milestone 7.
 *
 * This page is the landing target after the Setup Wizard completes.
 * Full implementation is in M7 (Dashboard + Calendar View Frontend).
 *
 * For M2, this page confirms the wizard completed successfully and
 * shows the semester_id from the URL query string.
 */
import { useSearchParams, Link } from 'react-router-dom';

function Dashboard() {
  const [searchParams] = useSearchParams();
  const semesterId = searchParams.get('semester');

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-8">
      <div className="max-w-md w-full text-center space-y-4">
        <div className="w-16 h-16 rounded-full bg-green-900/40 border border-green-700 flex items-center justify-center mx-auto">
          <svg className="w-8 h-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold text-slate-100">Semester Created!</h1>
        <p className="text-slate-400 text-sm">
          Semester ID <span className="text-blue-400 font-mono">#{semesterId}</span> has been saved. The full Dashboard will be available in Milestone 7.
        </p>
        <Link
          to="/setup"
          className="inline-block mt-4 text-sm text-slate-500 hover:text-slate-300 transition-colors underline underline-offset-2"
        >
          ← Go back to Setup Wizard
        </Link>
      </div>
    </div>
  );
}

export default Dashboard;
