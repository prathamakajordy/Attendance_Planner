import React from 'react';
import { Tent, AlertTriangle, CalendarRange } from 'lucide-react';

export default function CalendarDayCell({ 
  cellData, 
  planDay, 
  dayEvents,
  isActiveSemester, 
  activeFilters,
  onClick 
}) {
  const { dateObj, isPadding, isCurrentMonth } = cellData;

  // If outside semester entirely (disabled)
  if (!isActiveSemester || isPadding) {
    return (
      <div className={`min-h-[80px] md:min-h-[100px] border border-slate-800/50 p-2 ${
        isPadding ? 'bg-slate-900/20' : 'bg-slate-900/40'
      }`}>
        <span className="text-slate-600 text-sm">{dateObj.getDate()}</span>
      </div>
    );
  }

  // Derive visual state based purely on backend plan_day
  let state = 'none'; // attend, skip, mixed, holiday
  if (planDay) {
    if (!planDay.is_lecture_day) {
      state = 'holiday';
    } else if (planDay.blocks.length > 0) {
      const hasAttend = planDay.blocks.some(b => b.recommendation === 'Attend');
      const hasSkip = planDay.blocks.some(b => b.recommendation === 'Skip');
      
      if (hasAttend && !hasSkip) state = 'attend';
      else if (!hasAttend && hasSkip) state = 'skip';
      else if (hasAttend && hasSkip) state = 'mixed';
      else state = 'optional'; // everything is optional
    }
  }

  const hasEvents = dayEvents && dayEvents.length > 0;
  
  // Filtering Logic
  const isFilteredOut = () => {
    // If no filters are active, nothing is filtered out
    if (!activeFilters.attend && !activeFilters.skip && !activeFilters.holiday && !activeFilters.event) return false;
    
    // If at least one filter is active, check if THIS cell matches ANY active filter
    if (activeFilters.attend && state === 'attend') return false;
    if (activeFilters.attend && state === 'mixed') return false;
    if (activeFilters.skip && state === 'skip') return false;
    if (activeFilters.skip && state === 'mixed') return false;
    if (activeFilters.holiday && state === 'holiday') return false;
    if (activeFilters.event && hasEvents) return false;

    return true; // Filtered out
  };

  const dimmed = isFilteredOut();

  // Visual Styles
  let bgStyle = 'bg-slate-800 hover:bg-slate-700/80 cursor-pointer border-slate-700';
  let indicator = null;

  if (state === 'attend') {
    bgStyle = 'bg-green-900/20 border-green-800/50 hover:bg-green-900/40 cursor-pointer';
    indicator = <div className="absolute bottom-2 left-2 right-2 h-1.5 rounded-full bg-green-500/50"></div>;
  } else if (state === 'skip') {
    bgStyle = 'bg-slate-800 border-slate-700 hover:bg-slate-700 cursor-pointer';
    indicator = <div className="absolute bottom-2 left-2 right-2 h-1.5 rounded-full bg-slate-600/50"></div>;
  } else if (state === 'mixed') {
    bgStyle = 'bg-slate-800 border-slate-700 hover:bg-slate-700 cursor-pointer';
    indicator = (
      <div className="absolute bottom-2 left-2 right-2 h-1.5 flex rounded-full overflow-hidden">
        <div className="w-1/2 bg-green-500/50"></div>
        <div className="w-1/2 bg-slate-600/50"></div>
      </div>
    );
  } else if (state === 'holiday') {
    bgStyle = 'bg-orange-900/10 border-orange-900/30 hover:bg-orange-900/20 cursor-pointer';
  }

  // Today marker
  const today = new Date();
  const isToday = dateObj.getDate() === today.getDate() && 
                  dateObj.getMonth() === today.getMonth() && 
                  dateObj.getFullYear() === today.getFullYear();

  return (
    <div 
      onClick={() => onClick(dateObj, planDay, dayEvents)}
      className={`relative min-h-[80px] md:min-h-[100px] border p-2 transition-all group overflow-hidden ${bgStyle} ${dimmed ? 'opacity-25 grayscale' : 'opacity-100'}`}
    >
      {/* Date Number */}
      <div className="flex justify-between items-start">
        <span className={`text-sm font-medium w-6 h-6 flex items-center justify-center rounded-full ${
          isToday ? 'bg-blue-500 text-white' : 'text-slate-300 group-hover:text-white'
        }`}>
          {dateObj.getDate()}
        </span>

        {/* Small Icons Top Right */}
        <div className="flex gap-1">
          {state === 'holiday' && <Tent className="w-3.5 h-3.5 text-orange-400/70" />}
          {hasEvents && <CalendarRange className="w-3.5 h-3.5 text-blue-400/80" />}
        </div>
      </div>

      {indicator}
    </div>
  );
}
