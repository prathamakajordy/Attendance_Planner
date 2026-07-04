import React from 'react';
import CalendarDayCell from './CalendarDayCell';

export default function CalendarGrid({ 
  monthGrid, 
  planDaysMap, 
  semesterEvents,
  semesterStart,
  semesterEnd,
  activeFilters,
  onDayClick
}) {
  const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  // Helper to check if a day falls inside the semester
  const isDateInSemester = (dateObj) => {
    // Zero out times for fair comparison
    const d = new Date(dateObj.getFullYear(), dateObj.getMonth(), dateObj.getDate()).getTime();
    const start = new Date(semesterStart.getFullYear(), semesterStart.getMonth(), semesterStart.getDate()).getTime();
    const end = new Date(semesterEnd.getFullYear(), semesterEnd.getMonth(), semesterEnd.getDate()).getTime();
    return d >= start && d <= end;
  };

  // Helper to find events for a specific day
  const getEventsForDay = (dateObj) => {
    if (!semesterEvents) return [];
    const d = new Date(dateObj.getFullYear(), dateObj.getMonth(), dateObj.getDate()).getTime();
    
    return semesterEvents.filter(ev => {
      const start = new Date(ev.start_date);
      start.setHours(0,0,0,0);
      const end = new Date(ev.end_date);
      end.setHours(0,0,0,0);
      return d >= start.getTime() && d <= end.getTime();
    });
  };

  return (
    <div className="bg-slate-900 border-x border-b border-slate-700 overflow-hidden">
      {/* Weekday Headers */}
      <div className="grid grid-cols-7 border-b border-slate-700 bg-slate-800/50">
        {WEEKDAYS.map(day => (
          <div key={day} className="py-2 text-center text-xs font-semibold text-slate-400 uppercase tracking-wider">
            <span className="hidden sm:inline">{day}</span>
            <span className="sm:hidden">{day.charAt(0)}</span>
          </div>
        ))}
      </div>

      {/* Days Grid */}
      <div className="grid grid-cols-7">
        {monthGrid.map((cell, i) => {
          const isActiveSemester = isDateInSemester(cell.dateObj);
          const planDay = planDaysMap[cell.dateStr];
          const dayEvents = getEventsForDay(cell.dateObj);

          return (
            <CalendarDayCell 
              key={i}
              cellData={cell}
              planDay={planDay}
              dayEvents={dayEvents}
              isActiveSemester={isActiveSemester}
              activeFilters={activeFilters}
              onClick={onDayClick}
            />
          );
        })}
      </div>
    </div>
  );
}
