import React from 'react';
import { AlertTriangle } from 'lucide-react';

export default function FeasibilityReport({ feasibility }) {
  if (!feasibility || feasibility.length === 0) return null;

  const infeasibleSubjects = feasibility.filter(f => !f.is_feasible);
  
  if (infeasibleSubjects.length === 0) return null;

  return (
    <div className="bg-red-950/30 border border-red-900/50 rounded-xl p-4 md:p-6 mb-6">
      <div className="flex items-start gap-3">
        <div className="mt-0.5">
          <AlertTriangle className="w-5 h-5 text-red-500" />
        </div>
        <div className="flex-1">
          <h3 className="text-red-400 font-semibold mb-2">Impossible Attendance Scenario</h3>
          <p className="text-red-300/80 text-sm mb-4">
            Based on the current date, timetable, and remaining semester duration, it is mathematically impossible to meet the attendance requirements for the following subjects. The engine has generated the best possible plan, prioritizing the subjects closest to passing.
          </p>
          
          <div className="space-y-2">
            {infeasibleSubjects.map((sub) => (
              <div key={sub.subject_id} className="bg-red-900/20 border border-red-800/30 rounded-lg p-3 flex flex-col md:flex-row md:items-center justify-between gap-2">
                <span className="font-medium text-red-200">{sub.subject_name}</span>
                <div className="flex items-center gap-4 text-sm">
                  <div className="text-red-300/60">
                    Required: <span className="text-red-300 font-mono">{sub.required_percentage.toFixed(1)}%</span>
                  </div>
                  <div className="text-red-400 font-medium">
                    Best Achievable: <span className="font-mono">{sub.best_achievable_percentage.toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
