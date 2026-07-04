import React from 'react';
import { Filter } from 'lucide-react';

export default function CalendarFilters({ activeFilters, toggleFilter }) {
  const FILTERS = [
    { id: 'attend', label: 'Attend', color: 'text-green-400 bg-green-500/10 border-green-500/30 hover:bg-green-500/20' },
    { id: 'skip', label: 'Skip', color: 'text-slate-300 bg-slate-700/50 border-slate-600 hover:bg-slate-700' },
    { id: 'holiday', label: 'Holidays', color: 'text-orange-400 bg-orange-500/10 border-orange-500/30 hover:bg-orange-500/20' },
    { id: 'event', label: 'Events', color: 'text-blue-400 bg-blue-500/10 border-blue-500/30 hover:bg-blue-500/20' }
  ];

  return (
    <div className="bg-slate-800/60 border-x border-b border-slate-700/80 p-3 flex flex-wrap items-center gap-3">
      <div className="flex items-center gap-1.5 text-slate-400 text-sm font-medium pr-2 border-r border-slate-700">
        <Filter className="w-4 h-4" />
        <span className="hidden sm:inline">Highlight</span>
      </div>
      
      <div className="flex flex-wrap gap-2">
        {FILTERS.map(f => {
          const isActive = activeFilters[f.id];
          return (
            <button
              key={f.id}
              onClick={() => toggleFilter(f.id)}
              className={`px-3 py-1 rounded-full text-xs font-semibold border transition-all ${
                isActive 
                  ? f.color 
                  : 'bg-slate-900/50 text-slate-500 border-slate-700 hover:text-slate-300 hover:bg-slate-800'
              }`}
            >
              {f.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
