import React from 'react';
import { X, CalendarRange, Tent } from 'lucide-react';
import LectureBlock from '../LectureBlock';

// Helper to format YYYY-MM-DD to "Monday, August 12, 2026"
const formatFullDate = (dateObj) => {
  if (!dateObj) return '';
  return new Intl.DateTimeFormat('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(dateObj);
};

export default function DayDetailsPanel({ 
  dateObj, 
  planDay, 
  dayEvents, 
  subjectMap, 
  onClose 
}) {
  if (!dateObj) return null;

  return (
    <>
      {/* Mobile Backdrop */}
      <div 
        className="fixed inset-0 bg-black/60 z-40 md:hidden backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Panel */}
      <div className="fixed inset-x-0 bottom-0 top-20 md:top-[73px] md:right-0 md:left-auto md:w-[400px] lg:w-[450px] bg-slate-900 border-t md:border-t-0 md:border-l border-slate-700 z-50 flex flex-col shadow-2xl transition-transform duration-300 transform translate-y-0 md:translate-x-0 rounded-t-2xl md:rounded-none">
        
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-slate-900/95 sticky top-0">
          <div>
            <h3 className="text-lg font-bold text-slate-100">{formatFullDate(dateObj)}</h3>
            {!planDay && <p className="text-sm text-slate-400">Outside Semester Range</p>}
          </div>
          <button 
            onClick={onClose}
            aria-label="Close details"
            className="p-2 rounded-full hover:bg-slate-800 text-slate-400 hover:text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          
          {/* Semester Events */}
          {dayEvents && dayEvents.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <CalendarRange className="w-4 h-4" /> Events
              </h4>
              {dayEvents.map(ev => (
                <div key={ev.id} className="bg-blue-900/10 border border-blue-900/30 rounded-lg p-3">
                  <div className="font-medium text-blue-300">{ev.name}</div>
                  {ev.description && <div className="text-sm text-blue-400/80 mt-1">{ev.description}</div>}
                </div>
              ))}
            </div>
          )}

          {/* Plan Details */}
          {planDay ? (
            !planDay.is_lecture_day ? (
              <div className="space-y-2">
                <h4 className="text-sm font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Tent className="w-4 h-4" /> Holiday / No Lectures
                </h4>
                <div className="bg-orange-900/10 border border-orange-900/30 rounded-lg p-4 text-orange-200/80 text-sm italic">
                  {planDay.day_explanation || "No lectures scheduled on this day."}
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <h4 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
                  Lecture Blocks ({planDay.blocks.length})
                </h4>
                {planDay.blocks.length === 0 ? (
                  <div className="bg-slate-800/30 border border-slate-700/50 rounded-lg p-4 text-slate-400 text-sm italic">
                    No blocks generated for this day.
                  </div>
                ) : (
                  planDay.blocks.map((block) => (
                    <LectureBlock key={block.id} block={block} subjectMap={subjectMap} />
                  ))
                )}
              </div>
            )
          ) : (
            <div className="text-center py-10 text-slate-500 italic">
              This day is outside the active semester boundaries.
            </div>
          )}
        </div>

      </div>
    </>
  );
}
