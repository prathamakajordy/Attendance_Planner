import React from 'react';
import LectureBlock from './LectureBlock';

// Helper to format YYYY-MM-DD to "Monday, Aug 12"
const formatDate = (dateStr) => {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return new Intl.DateTimeFormat('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric'
  }).format(date);
};

export default function DayCard({ dayData, subjectMap }) {
  const { date, is_lecture_day, day_explanation, blocks } = dayData;
  const isWeekend = !is_lecture_day && !day_explanation;

  return (
    <div className="mb-6">
      <div className="sticky top-0 z-10 bg-slate-900/95 backdrop-blur py-2 mb-3 border-b border-slate-800">
        <h3 className="text-lg font-semibold text-slate-200">
          {formatDate(date)}
        </h3>
      </div>
      
      {!is_lecture_day ? (
        <div className="bg-slate-800/30 border border-slate-700/50 rounded-lg p-4 text-slate-400 text-sm italic">
          {day_explanation || "No lectures scheduled."}
        </div>
      ) : (
        <div className="space-y-3">
          {blocks.length === 0 ? (
            <div className="bg-slate-800/30 border border-slate-700/50 rounded-lg p-4 text-slate-400 text-sm italic">
              No blocks generated for this day.
            </div>
          ) : (
            blocks.map((block) => (
              <LectureBlock key={block.id} block={block} subjectMap={subjectMap} />
            ))
          )}
        </div>
      )}
    </div>
  );
}
