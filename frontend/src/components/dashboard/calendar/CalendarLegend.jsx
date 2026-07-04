import React from 'react';
import { Tent, CalendarRange } from 'lucide-react';

export default function CalendarLegend() {
  return (
    <div className="flex flex-wrap items-center justify-center gap-4 sm:gap-6 pt-4 pb-2 text-xs sm:text-sm text-slate-400 border-x border-b border-slate-700/50 bg-slate-800/20 rounded-b-xl px-4">
      <div className="flex items-center gap-2">
        <div className="w-3 h-3 rounded-full bg-green-500/80 border border-green-500/50"></div>
        <span>Attend</span>
      </div>
      
      <div className="flex items-center gap-2">
        <div className="w-3 h-3 rounded-full bg-slate-600/80 border border-slate-500/50"></div>
        <span>Skip</span>
      </div>

      <div className="flex items-center gap-2">
        <div className="w-3 h-3 flex rounded-full overflow-hidden border border-slate-500/50">
          <div className="w-1/2 bg-green-500/80"></div>
          <div className="w-1/2 bg-slate-600/80"></div>
        </div>
        <span>Mixed</span>
      </div>

      <div className="flex items-center gap-1.5">
        <Tent className="w-4 h-4 text-orange-400/80" />
        <span>Holiday</span>
      </div>

      <div className="flex items-center gap-1.5">
        <CalendarRange className="w-4 h-4 text-blue-400/80" />
        <span>Event</span>
      </div>
    </div>
  );
}
