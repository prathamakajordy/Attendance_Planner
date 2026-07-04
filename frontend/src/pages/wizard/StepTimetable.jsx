import TimetableSlotRow, { WEEKDAYS } from '../../components/wizard/TimetableSlotRow';

/**
 * StepTimetable — Step 4 of the Setup Wizard.
 *
 * Collects: list of weekly timetable slots.
 * Each slot: { subject_index, weekday, start_time, end_time, order_index }
 *
 * Validation per SRD Section 19:
 *   - start_time < end_time
 *   - No two slots on same weekday may overlap
 *   - At least one slot required
 *
 * Props:
 *   timetable: SlotData[]
 *   subjects: SubjectData[] — from Step 3
 *   onChange: (timetable) => void
 *   errors: { _list?, [index]: string }
 */
function StepTimetable({ timetable, subjects, onChange, errors }) {
  const addSlot = () => {
    const nextOrder = timetable.length;
    onChange([
      ...timetable,
      { subject_index: subjects.length > 0 ? 0 : -1, weekday: 0, start_time: '09:00', end_time: '10:00', order_index: nextOrder },
    ]);
  };

  const updateSlot = (index, field, value) => {
    const updated = timetable.map((slot, i) =>
      i === index ? { ...slot, [field]: value } : slot
    );
    onChange(updated);
  };

  const removeSlot = (index) => {
    onChange(timetable.filter((_, i) => i !== index));
  };

  // Group slots by weekday for display
  const slotsByDay = WEEKDAYS.map((day) => ({
    ...day,
    slots: timetable
      .map((slot, index) => ({ slot, index }))
      .filter(({ slot }) => slot.weekday === day.value),
  })).filter(({ slots }) => slots.length > 0);

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-xl font-semibold text-slate-100">Weekly Timetable</h2>
        <p className="text-sm text-slate-400 mt-1">
          Define your recurring weekly lecture schedule. Each slot maps a subject to a specific day and time. This timetable repeats every week of the semester.
        </p>
      </div>

      {/* Global list error */}
      {errors._list && (
        <p className="text-sm text-red-400 bg-red-950/30 border border-red-800 rounded-lg px-4 py-2.5">{errors._list}</p>
      )}

      {/* Slots grouped by day */}
      {slotsByDay.length > 0 && (
        <div className="space-y-4">
          {slotsByDay.map(({ label, slots }) => (
            <div key={label}>
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">{label}</h3>
              <div className="space-y-2">
                {slots.map(({ slot, index }) => (
                  <TimetableSlotRow
                    key={index}
                    slot={slot}
                    index={index}
                    subjects={subjects}
                    onUpdate={updateSlot}
                    onRemove={removeSlot}
                    error={errors[index] || null}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Ungrouped new slots — shown when no slots exist yet */}
      {timetable.length === 0 && (
        <div className="text-center py-10 text-slate-500 border border-dashed border-slate-700 rounded-xl">
          <svg className="w-8 h-8 mx-auto mb-2 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p className="text-sm">No slots added yet. Click "Add Slot" to begin.</p>
        </div>
      )}

      {/* Add slot button */}
      <button
        type="button"
        onClick={addSlot}
        disabled={subjects.length === 0}
        className={[
          'w-full flex items-center justify-center gap-2 py-3',
          'border border-dashed rounded-xl text-sm transition-colors',
          subjects.length === 0
            ? 'border-slate-700 text-slate-600 cursor-not-allowed'
            : 'border-slate-600 text-slate-400 hover:text-slate-200 hover:border-slate-500',
        ].join(' ')}
        id="add-slot-btn"
        title={subjects.length === 0 ? 'Add subjects first (Step 3)' : 'Add a timetable slot'}
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        Add Slot
      </button>

      <p className="text-xs text-slate-500">
        Time slots are stored as HH:MM. The system uses 24-hour format. Overlapping slots on the same day are not permitted.
      </p>
    </div>
  );
}

/**
 * Checks if two time ranges overlap.
 * Times are "HH:MM" strings.
 */
function timesOverlap(startA, endA, startB, endB) {
  return startA < endB && endA > startB;
}

/**
 * Validates the Timetable step per SRD Section 19.
 */
export function validateTimetable(timetable) {
  const errors = {};

  if (timetable.length === 0) {
    errors._list = 'At least one timetable slot is required before generating a plan.';
    return { isValid: false, errors };
  }

  // Per-row validation
  timetable.forEach((slot, index) => {
    if (slot.subject_index < 0) {
      errors[index] = 'Please select a subject for this slot.';
      return;
    }
    if (!slot.start_time || !slot.end_time) {
      errors[index] = 'Start and end times are required.';
      return;
    }
    if (slot.start_time >= slot.end_time) {
      errors[index] = 'Start time must be before end time.';
      return;
    }
  });

  // Overlap detection: for each pair of slots on the same weekday
  for (let i = 0; i < timetable.length; i++) {
    for (let j = i + 1; j < timetable.length; j++) {
      const a = timetable[i];
      const b = timetable[j];
      if (a.weekday !== b.weekday) continue;
      if (!a.start_time || !a.end_time || !b.start_time || !b.end_time) continue;
      if (timesOverlap(a.start_time, a.end_time, b.start_time, b.end_time)) {
        errors[i] = errors[i] || `Overlaps with another slot on ${WEEKDAYS[a.weekday]?.label}.`;
        errors[j] = errors[j] || `Overlaps with another slot on ${WEEKDAYS[b.weekday]?.label}.`;
      }
    }
  }

  return { isValid: Object.keys(errors).length === 0, errors };
}

export default StepTimetable;
