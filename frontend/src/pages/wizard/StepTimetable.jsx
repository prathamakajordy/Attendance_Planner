import React, { useState } from 'react';
import TimetableSlotRow, { WEEKDAYS } from '../../components/wizard/TimetableSlotRow';
import ImportWizard from './ImportWizard';
import { FiUploadCloud } from 'react-icons/fi';
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
function StepTimetable({ timetable, subjects, onChange, onSubjectsChange, errors, semesterId }) {
  const [importMode, setImportMode] = useState(false);

  const addSlot = (weekdayValue) => {
    const nextOrder = timetable.length;
    
    // Find the latest slot for this weekday to infer the start time
    let defaultStart = '09:00';
    let defaultEnd = '10:00';
    
    const daySlots = timetable.filter(s => s.weekday === weekdayValue);
    if (daySlots.length > 0) {
      // Find max end time for this day
      const latestEnd = daySlots.reduce((max, slot) => slot.end_time > max ? slot.end_time : max, '00:00');
      
      if (latestEnd !== '00:00') {
        defaultStart = latestEnd;
        // Add 1 hour for end time
        let [hr, min] = latestEnd.split(':').map(Number);
        hr = Math.min(23, hr + 1);
        defaultEnd = `${hr.toString().padStart(2, '0')}:${min.toString().padStart(2, '0')}`;
      }
    }

    onChange([
      ...timetable,
      { 
        subject_index: -1, 
        weekday: weekdayValue, 
        start_time: defaultStart, 
        end_time: defaultEnd, 
        order_index: nextOrder 
      },
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

  // Group slots by weekday for display (Always show all 7 days)
  const slotsByDay = WEEKDAYS.map((day) => ({
    ...day,
    slots: timetable
      .map((slot, index) => ({ slot, index }))
      .filter(({ slot }) => slot.weekday === day.value),
  }));

  const handleImportComplete = (payload) => {
    if (payload && payload.length > 0) {
      // payload has {weekday, start_time, end_time, subject_name}
      // Step 3 creates subjects, so we need to map subject names to existing subject_index or create new ones
      let nextSubjectOrder = subjects.length;
      let newSubjects = [...subjects];
      let newTimetable = [...timetable];
      let orderIndex = timetable.length;
      
      payload.forEach(row => {
        let subjIdx = newSubjects.findIndex(s => s.name.toLowerCase() === row.subject_name.toLowerCase());
        if (subjIdx === -1) {
          subjIdx = nextSubjectOrder++;
          newSubjects.push({ name: row.subject_name, code: '', held_count: 0, present_count: 0 });
        }
        
        newTimetable.push({
          subject_index: subjIdx,
          weekday: row.weekday,
          start_time: row.start_time.substring(0, 5), // '09:00:00' -> '09:00'
          end_time: row.end_time.substring(0, 5),
          order_index: orderIndex++
        });
      });
      
      if (newSubjects.length > subjects.length && onSubjectsChange) {
         onSubjectsChange(newSubjects);
      }
      onChange(newTimetable);
    }
    setImportMode(false);
  };

  if (importMode) {
    return (
      <ImportWizard 
        semesterId={semesterId || "wizard"} 
        onComplete={handleImportComplete} 
        onCancel={() => setImportMode(false)} 
      />
    );
  }

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-xl font-semibold text-slate-100">Weekly Timetable</h2>
        <div className="flex items-center justify-between mt-1">
          <p className="text-sm text-slate-400">
            Define your recurring weekly lecture schedule. Each slot maps a subject to a specific day and time. This timetable repeats every week of the semester.
          </p>
          <button
            onClick={() => setImportMode(true)}
            className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-brand-400 bg-brand-500/10 hover:bg-brand-500/20 rounded-lg transition-colors border border-brand-500/20"
          >
            <FiUploadCloud size={14} /> Smart Import
          </button>
        </div>
      </div>

      {/* Global list error */}
      {errors._list && (
        <p className="text-sm text-red-400 bg-red-950/30 border border-red-800 rounded-lg px-4 py-2.5">{errors._list}</p>
      )}

      {/* Slots grouped by day */}
      <div className="space-y-6">
        {slotsByDay.map(({ label, value, slots }) => (
          <div key={label} className="bg-slate-900/40 p-4 rounded-xl border border-slate-800">
            <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3 ml-1">{label}</h3>
            
            <div className="space-y-2 mb-3">
              {slots.length === 0 ? (
                <p className="text-sm text-slate-600 italic ml-1 mb-1">No slots added yet.</p>
              ) : (
                slots.map(({ slot, index }) => (
                  <TimetableSlotRow
                    key={index}
                    slot={slot}
                    index={index}
                    subjects={subjects}
                    onUpdate={updateSlot}
                    onRemove={removeSlot}
                    error={errors[index] || null}
                  />
                ))
              )}
            </div>

            {/* Add slot button for this specific day */}
            <button
              type="button"
              onClick={() => addSlot(value)}
              disabled={subjects.length === 0}
              className={[
                'w-full flex items-center justify-center gap-2 py-2.5 mt-2',
                'border border-dashed rounded-lg text-sm transition-colors',
                subjects.length === 0
                  ? 'border-slate-700 text-slate-600 cursor-not-allowed'
                  : 'border-slate-600 text-slate-400 hover:text-slate-200 hover:border-slate-500 hover:bg-slate-800/50',
              ].join(' ')}
              id={`add-slot-btn-${value}`}
              title={subjects.length === 0 ? 'Add subjects first (Step 3)' : `Add a timetable slot for ${label}`}
            >
              <svg className="w-4 h-4 opacity-70" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add Slot
            </button>
          </div>
        ))}
      </div>

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
