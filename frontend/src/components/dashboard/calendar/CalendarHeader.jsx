import React from 'react';
import { ChevronLeft, ChevronRight, CalendarDays } from 'lucide-react';

export default function CalendarHeader({ 
  currentDate, 
  onPrevMonth, 
  onNextMonth, 
  onToday,
  canGoPrev,
  canGoNext 
}) {
  const monthYearLabel = currentDate.toLocaleString('default', { month: 'long', year: 'numeric' });

  return (
    <div className="flex items-center justify-between bg-slate-800/80 backdrop-blur border border-slate-700 p-4 rounded-t-xl">
      <div className="flex items-center gap-3">
        <h2 className="text-xl font-bold text-slate-100 min-w-[140px]">{monthYearLabel}</h2>
        <button
          onClick={onToday}
          className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-slate-700/50 hover:bg-slate-700 text-slate-300 rounded-md transition-colors border border-slate-600/50"
        >
          <CalendarDays className="w-3.5 h-3.5" />
          Today
        </button>
      </div>
      
      <div className="flex items-center gap-1">
        <button
          onClick={onPrevMonth}
          disabled={!canGoPrev}
          aria-label="Previous Month"
          className="p-2 rounded-md hover:bg-slate-700 text-slate-400 hover:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors disabled:opacity-30 disabled:hover:bg-transparent"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
        <button
          onClick={onNextMonth}
          disabled={!canGoNext}
          aria-label="Next Month"
          className="p-2 rounded-md hover:bg-slate-700 text-slate-400 hover:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors disabled:opacity-30 disabled:hover:bg-transparent"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
}
