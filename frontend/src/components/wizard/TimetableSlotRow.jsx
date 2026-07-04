/**
 * TimetableSlotRow — a single editable row in the timetable builder.
 *
 * Props:
 *   slot: { subject_index, weekday, start_time, end_time }
 *   index: number — row index in the slot list
 *   subjects: Subject[] — from Step 3 (to populate the subject dropdown)
 *   onUpdate: (index, field, value) => void
 *   onRemove: (index) => void
 *   error: string | null — overlap or time-range error for this row
 */

const WEEKDAYS = [
  { value: 0, label: 'Monday' },
  { value: 1, label: 'Tuesday' },
  { value: 2, label: 'Wednesday' },
  { value: 3, label: 'Thursday' },
  { value: 4, label: 'Friday' },
  { value: 5, label: 'Saturday' },
  { value: 6, label: 'Sunday' },
];

function TimetableSlotRow({ slot, index, subjects, onUpdate, onRemove, error }) {
  return (
    <div className={[
      'p-3 rounded-lg border transition-colors',
      error ? 'border-red-500/60 bg-red-950/20' : 'border-slate-700 bg-slate-800/50',
    ].join(' ')}>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 items-end">
        {/* Subject selector */}
        <div>
          <label className="block text-xs text-slate-400 mb-1">Subject</label>
          <select
            value={slot.subject_index}
            onChange={(e) => onUpdate(index, 'subject_index', Number(e.target.value))}
            className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
            id={`slot-subject-${index}`}
          >
            <option value={-1} disabled>Select subject</option>
            {subjects.map((sub, si) => (
              <option key={si} value={si}>{sub.name || `Subject ${si + 1}`}</option>
            ))}
          </select>
        </div>

        {/* Weekday selector */}
        <div>
          <label className="block text-xs text-slate-400 mb-1">Day</label>
          <select
            value={slot.weekday}
            onChange={(e) => onUpdate(index, 'weekday', Number(e.target.value))}
            className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
            id={`slot-weekday-${index}`}
          >
            {WEEKDAYS.map((d) => (
              <option key={d.value} value={d.value}>{d.label}</option>
            ))}
          </select>
        </div>

        {/* Start time */}
        <div>
          <label className="block text-xs text-slate-400 mb-1">Start Time</label>
          <input
            type="time"
            value={slot.start_time}
            onChange={(e) => onUpdate(index, 'start_time', e.target.value)}
            className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
            id={`slot-start-${index}`}
          />
        </div>

        {/* End time + remove button */}
        <div className="flex gap-2 items-end">
          <div className="flex-1">
            <label className="block text-xs text-slate-400 mb-1">End Time</label>
            <input
              type="time"
              value={slot.end_time}
              onChange={(e) => onUpdate(index, 'end_time', e.target.value)}
              className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              id={`slot-end-${index}`}
            />
          </div>
          <button
            type="button"
            onClick={() => onRemove(index)}
            className="flex-shrink-0 p-2 text-slate-500 hover:text-red-400 hover:bg-red-950/30 rounded-lg transition-colors mb-0.5 md:hidden"
            aria-label="Remove slot"
            id={`slot-remove-${index}-mobile`}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        {/* Required Groups (Optional) */}
        <div className="md:col-span-3 flex gap-2 items-end mt-2 md:mt-0">
          <div className="flex-1">
            <label className="block text-xs text-slate-400 mb-1">Required Groups <span className="opacity-60">(Optional)</span></label>
            <input
              type="text"
              value={slot.required_groups || ''}
              onChange={(e) => onUpdate(index, 'required_groups', e.target.value)}
              placeholder="e.g. I2-1"
              className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-blue-500 placeholder-slate-600"
              id={`slot-groups-${index}`}
            />
          </div>
        </div>
        
        {/* Remove button (Desktop) */}
        <div className="hidden md:flex justify-end mt-2 md:mt-0">
          <button
            type="button"
            onClick={() => onRemove(index)}
            className="flex-shrink-0 p-2 text-slate-500 hover:text-red-400 hover:bg-red-950/30 rounded-lg transition-colors mb-0.5"
            aria-label="Remove slot"
            id={`slot-remove-${index}-desktop`}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      {/* Row-level error */}
      {error && (
        <p className="mt-2 text-xs text-red-400">{error}</p>
      )}
    </div>
  );
}

export { WEEKDAYS };
export default TimetableSlotRow;
