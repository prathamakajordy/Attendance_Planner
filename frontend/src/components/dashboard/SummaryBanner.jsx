import React from 'react';

export default function SummaryBanner({ metadata }) {
  if (!metadata) return null;

  const {
    overall_feasible,
    total_recommended_days,
    total_recommended_blocks,
    overall_attendance_threshold,
    subject_attendance_threshold,
    generated_at,
    engine_version
  } = metadata;

  // Format the generation time
  const dateObj = new Date(generated_at + 'Z'); // appending Z to parse as UTC
  const formattedTime = dateObj.toLocaleString();

  return (
    <div className={`p-4 md:p-6 rounded-xl border mb-6 shadow-sm ${
      overall_feasible 
        ? 'bg-slate-800/50 border-slate-700' 
        : 'bg-red-900/20 border-red-800'
    }`}>
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h2 className="text-xl font-bold text-slate-100">
              Plan Summary
            </h2>
            {overall_feasible ? (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-900/50 text-green-400 border border-green-800">
                Feasible
              </span>
            ) : (
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-900/50 text-red-400 border border-red-800">
                Infeasible
              </span>
            )}
          </div>
          
          <div className="flex gap-6 mt-4">
            <div>
              <p className="text-slate-400 text-sm">Recommended Days</p>
              <p className="text-2xl font-semibold text-slate-200">{total_recommended_days}</p>
            </div>
            <div>
              <p className="text-slate-400 text-sm">Total Lectures</p>
              <p className="text-2xl font-semibold text-slate-200">{total_recommended_blocks}</p>
            </div>
          </div>
        </div>

        <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-700/50 text-sm min-w-[200px]">
          <h3 className="text-slate-400 font-medium mb-2 text-xs uppercase tracking-wider">Configuration Snapshot</h3>
          <div className="space-y-1">
            <div className="flex justify-between">
              <span className="text-slate-400">Overall Target:</span>
              <span className="text-slate-200 font-mono">{overall_attendance_threshold}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Subject Target:</span>
              <span className="text-slate-200 font-mono">{subject_attendance_threshold}%</span>
            </div>
          </div>
          <div className="mt-3 pt-3 border-t border-slate-700/50 text-xs text-slate-500 space-y-1">
            <p>Last Generated: {formattedTime}</p>
            <p>Engine: {engine_version}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
