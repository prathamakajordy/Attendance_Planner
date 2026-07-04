import React from 'react';
import { Filter, Calendar } from 'lucide-react';

export default function DashboardControls({ 
  filterMode, 
  setFilterMode, 
  subjectFilter, 
  setSubjectFilter, 
  subjects,
  months,
  onMonthJump 
}) {
  return (
    <div className="bg-slate-800/80 backdrop-blur border border-slate-700 p-3 md:p-4 rounded-xl mb-6 sticky top-0 z-20 shadow-lg shadow-slate-900/50 flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
      
      {/* Primary Filters */}
      <div className="flex flex-col sm:flex-row gap-4 w-full md:w-auto">
        
        {/* Recommendation Filter */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <div className="flex bg-slate-900 rounded-lg p-1 border border-slate-700/50">
            {['All', 'Attend', 'Skip'].map((mode) => (
              <button
                key={mode}
                onClick={() => setFilterMode(mode)}
                className={`px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                  filterMode === mode 
                    ? 'bg-blue-600 text-white' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                {mode}
              </button>
            ))}
          </div>
        </div>

        {/* Subject Filter */}
        <div className="flex items-center gap-2 flex-1 sm:flex-none">
          <select
            value={subjectFilter}
            onChange={(e) => setSubjectFilter(e.target.value)}
            className="w-full sm:w-auto bg-slate-900 border border-slate-700/50 text-slate-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2"
          >
            <option value="All">All Subjects</option>
            {subjects.map((sub) => (
              <option key={sub.id} value={sub.id.toString()}>
                {sub.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Navigation (Month Jump) */}
      <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto pb-1 md:pb-0 hide-scrollbar">
        <Calendar className="w-4 h-4 text-slate-400 shrink-0 hidden md:block" />
        <div className="flex gap-2">
          {months.map((month) => (
            <button
              key={month.id}
              onClick={() => onMonthJump(month.id)}
              className="px-3 py-1.5 text-xs font-medium bg-slate-900 border border-slate-700 text-slate-300 rounded-lg hover:bg-slate-700 hover:text-white transition-colors whitespace-nowrap"
            >
              {month.label}
            </button>
          ))}
        </div>
      </div>

    </div>
  );
}
