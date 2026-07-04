import React from 'react';

// Formats time from "HH:MM:SS" to "HH:MM"
const formatTime = (timeStr) => {
  if (!timeStr) return '';
  return timeStr.slice(0, 5);
};

export default function LectureBlock({ block, subjectMap }) {
  const { start_time, end_time, recommendation, block_explanation, subject_ids } = block;

  const getRecommendationStyles = (rec) => {
    switch (rec) {
      case 'Attend':
        return 'bg-green-500/10 border-green-500/30 text-green-400';
      case 'Skip':
        return 'bg-slate-500/10 border-slate-500/30 text-slate-400 opacity-75';
      case 'Optional':
        return 'bg-blue-500/10 border-blue-500/30 text-blue-400 border-dashed';
      default:
        return 'bg-slate-800 border-slate-700 text-slate-300';
    }
  };

  const getRecommendationBadge = (rec) => {
    switch (rec) {
      case 'Attend':
        return 'bg-green-500/20 text-green-300 border-green-500/50';
      case 'Skip':
        return 'bg-slate-700 text-slate-300 border-slate-600';
      case 'Optional':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/50 border-dashed';
      default:
        return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  const subjectNames = subject_ids
    .map((id) => subjectMap[id]?.name || `Subject #${id}`)
    .join(', ');

  return (
    <div className={`p-4 rounded-lg border ${getRecommendationStyles(recommendation)} transition-colors`}>
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        
        <div className="flex flex-col sm:flex-row sm:items-center gap-3 md:gap-6 min-w-0">
          <div className="font-mono text-sm opacity-80 whitespace-nowrap shrink-0">
            {formatTime(start_time)} - {formatTime(end_time)}
          </div>
          <div className="font-medium text-lg leading-tight truncate" title={subjectNames}>
            {subjectNames}
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 shrink-0">
          {block_explanation && (
            <div className="text-xs opacity-75 max-w-[200px] leading-tight line-clamp-2" title={block_explanation}>
              {block_explanation}
            </div>
          )}
          <span className={`px-3 py-1 rounded-full text-xs font-semibold border uppercase tracking-wider whitespace-nowrap ${getRecommendationBadge(recommendation)}`}>
            {recommendation}
          </span>
        </div>
        
      </div>
    </div>
  );
}
