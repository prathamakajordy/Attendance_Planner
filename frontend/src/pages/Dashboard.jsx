import React, { useEffect, useState, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { getPlan, generatePlan, getSubjects, getSemester, getSemesterEvents } from '../api/client';
import SummaryBanner from '../components/dashboard/SummaryBanner';
import FeasibilityReport from '../components/dashboard/FeasibilityReport';
import CalendarView from '../components/dashboard/calendar/CalendarView';
import { Loader2, CalendarX, RefreshCw } from 'lucide-react';

export default function Dashboard() {
  const [searchParams] = useSearchParams();
  const semesterId = searchParams.get('semester');
  const navigate = useNavigate();

  const [planData, setPlanData] = useState(null);
  const [subjects, setSubjects] = useState([]);
  const [semester, setSemester] = useState(null);
  const [semesterEvents, setSemesterEvents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!semesterId) {
      navigate('/setup');
      return;
    }
    fetchData();
  }, [semesterId]);

  const fetchData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [planRes, subRes, semRes, evRes] = await Promise.all([
        getPlan(semesterId).catch(err => {
          if (err.response?.status === 404 && err.response?.data?.detail?.error_code === 'PLAN_NOT_GENERATED') {
            return { data: null };
          }
          throw err;
        }),
        getSubjects(semesterId),
        getSemester(semesterId),
        getSemesterEvents(semesterId)
      ]);
      setPlanData(planRes.data);
      setSubjects(subRes.data);
      setSemester(semRes.data);
      setSemesterEvents(evRes.data);
    } catch (err) {
      if (err.message === 'Network Error') {
        setError('Cannot connect to server. Please ensure the backend is running.');
      } else {
        setError(err.response?.data?.detail?.message || err.message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);
    try {
      const res = await generatePlan(semesterId);
      // Re-fetch everything to ensure consistency
      const [subRes, semRes, evRes] = await Promise.all([
        getSubjects(semesterId),
        getSemester(semesterId),
        getSemesterEvents(semesterId)
      ]);
      setSubjects(subRes.data);
      setSemester(semRes.data);
      setSemesterEvents(evRes.data);
      setPlanData(res.data);
    } catch (err) {
      if (err.message === 'Network Error') {
        setError('Cannot connect to server. Please ensure the backend is running.');
      } else {
        setError(err.response?.data?.detail?.message || err.message);
      }
    } finally {
      setIsGenerating(false);
    }
  };

  const subjectMap = useMemo(() => {
    const map = {};
    subjects.forEach((s) => (map[s.id] = s));
    return map;
  }, [subjects]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center p-8">
        <div className="flex flex-col items-center gap-4 text-slate-400">
          <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
          <p>Loading your plan...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 pb-20">
      {/* Header */}
      <header className="bg-slate-900/90 backdrop-blur-md border-b border-slate-800 sticky top-0 z-30">
        <div className="max-w-4xl mx-auto px-4 md:px-6 h-16 flex items-center justify-between">
          <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
            Attendance Planner
          </h1>
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 border border-slate-700"
          >
            {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
            <span className="hidden sm:inline">Regenerate</span>
          </button>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 md:px-6 pt-6">
        
        {error && (
          <div className="mb-6 bg-red-500/10 border border-red-500/50 text-red-400 p-4 rounded-xl text-sm">
            {error}
          </div>
        )}

        {isGenerating ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-400 space-y-4">
            <Loader2 className="w-10 h-10 animate-spin text-blue-500" />
            <h2 className="text-xl font-medium text-slate-300">Generating deterministic plan...</h2>
            <p className="text-sm max-w-md text-center opacity-80">
              The engine is analyzing your timetable, holidays, and student groups to find the optimal attendance strategy.
            </p>
          </div>
        ) : !planData ? (
          <div className="flex flex-col items-center justify-center py-20 text-center space-y-6">
            <div className="w-20 h-20 bg-slate-800 rounded-full flex items-center justify-center border border-slate-700">
              <CalendarX className="w-10 h-10 text-slate-500" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-200 mb-2">No Active Plan</h2>
              <p className="text-slate-400 max-w-md mx-auto">
                You haven't generated an attendance plan for this semester yet.
              </p>
            </div>
            <button
              onClick={handleGenerate}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors shadow-lg shadow-blue-900/20"
            >
              Generate Plan Now
            </button>
          </div>
        ) : (
          <div className="pb-10">
            <SummaryBanner metadata={planData.metadata} />
            <FeasibilityReport feasibility={planData.feasibility} />
            
            <CalendarView 
              planData={planData}
              semester={semester}
              semesterEvents={semesterEvents}
              subjectMap={subjectMap}
            />
          </div>
        )}
      </main>
    </div>
  );
}
