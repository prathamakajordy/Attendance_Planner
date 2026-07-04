import { useState, useEffect } from 'react';
import useEventTypes from '../../hooks/useEventTypes';

/**
 * EventFormModal — modal for adding or editing a single SemesterEvent.
 *
 * Props:
 *   initialData: object | null — if null, creates a new event; otherwise, edits
 *   semesterStartDate: string — for out-of-range warning
 *   semesterEndDate: string — for out-of-range warning
 *   onSave: (eventData) => void
 *   onClose: () => void
 */

const EMPTY_EVENT = {
  name: '',
  event_type_id: '',
  custom_type_label: '',
  start_date: '',
  end_date: '',
  description: '',
  // Four overrides — null means "inherit from event type default" (TRD 7.1)
  cancels_lectures_override: null,
  counts_towards_attendance_override: null,
  is_working_day_override: null,
  exclude_from_recommendation_override: null,
};

function EventFormModal({ initialData, semesterStartDate, semesterEndDate, onSave, onClose }) {
  const { eventTypes, isLoading, error: fetchError } = useEventTypes();
  const [formData, setFormData] = useState(initialData || EMPTY_EVENT);
  const [errors, setErrors] = useState({});

  // When event type changes, reset override flags so they re-derive from defaults.
  // The user can then deliberately change individual flags.
  const handleTypeChange = (eventTypeId) => {
    setFormData((prev) => ({
      ...prev,
      event_type_id: Number(eventTypeId),
      cancels_lectures_override: null,
      counts_towards_attendance_override: null,
      is_working_day_override: null,
      exclude_from_recommendation_override: null,
      custom_type_label: '',
    }));
  };

  const selectedType = eventTypes.find((t) => t.id === Number(formData.event_type_id));
  const isCustomType = selectedType?.key === 'custom';

  // For each flag, compute the "displayed" value: override if set, else type default.
  const resolvedFlag = (overrideKey, defaultKey) => {
    if (formData[overrideKey] !== null) return formData[overrideKey];
    if (selectedType) return selectedType[defaultKey];
    return false;
  };

  // Toggle a flag — first click sets override to !default, second click clears override (back to null).
  const toggleFlag = (overrideKey, defaultKey) => {
    const currentDefault = selectedType?.[defaultKey] ?? false;
    const currentOverride = formData[overrideKey];
    if (currentOverride === null) {
      // First interaction: override to opposite of default
      setFormData((prev) => ({ ...prev, [overrideKey]: !currentDefault }));
    } else {
      // Second interaction: clear override (back to inheriting from type)
      setFormData((prev) => ({ ...prev, [overrideKey]: null }));
    }
  };

  const validate = () => {
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = 'Event name is required.';
    if (!formData.event_type_id) newErrors.event_type_id = 'Please select an event type.';
    if (isCustomType && !formData.custom_type_label?.trim()) {
      newErrors.custom_type_label = 'A custom type label is required for "Other / Custom" events.';
    }
    if (!formData.start_date) newErrors.start_date = 'Start date is required.';
    if (!formData.end_date) newErrors.end_date = 'End date is required.';
    if (formData.start_date && formData.end_date && formData.end_date < formData.start_date) {
      newErrors.end_date = 'End date must be on or after start date.';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSave = () => {
    if (!validate()) return;
    onSave(formData);
  };

  // Out-of-range warning (non-blocking, per SRD Section 17)
  const isOutOfRange =
    formData.start_date &&
    semesterStartDate &&
    semesterEndDate &&
    (formData.start_date < semesterStartDate || formData.start_date > semesterEndDate);

  const FLAG_CONFIG = [
    { key: 'cancels_lectures_override', defaultKey: 'default_cancels_lectures', label: 'Cancels lectures' },
    { key: 'counts_towards_attendance_override', defaultKey: 'default_counts_towards_attendance', label: 'Counts towards attendance' },
    { key: 'is_working_day_override', defaultKey: 'default_is_working_day', label: 'Is a working day' },
    { key: 'exclude_from_recommendation_override', defaultKey: 'default_exclude_from_recommendation', label: 'Exclude from recommendation' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-lg bg-slate-800 border border-slate-700 rounded-2xl shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700">
          <h2 className="text-base font-semibold text-slate-100">
            {initialData ? 'Edit Event' : 'Add Semester Event'}
          </h2>
          <button onClick={onClose} className="text-slate-500 hover:text-slate-300 transition-colors" id="event-modal-close">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5 space-y-4 max-h-[70vh] overflow-y-auto">
          {fetchError && (
            <p className="text-sm text-red-400 bg-red-950/30 border border-red-800 rounded-lg px-3 py-2">{fetchError}</p>
          )}

          {/* Event name */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Event Name <span className="text-red-400">*</span></label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData((p) => ({ ...p, name: e.target.value }))}
              placeholder="e.g. Mid Semester Examination"
              className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              id="event-name"
            />
            {errors.name && <p className="text-xs text-red-400 mt-1">{errors.name}</p>}
          </div>

          {/* Event type */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Event Type <span className="text-red-400">*</span></label>
            <select
              value={formData.event_type_id}
              onChange={(e) => handleTypeChange(e.target.value)}
              disabled={isLoading}
              className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
              id="event-type"
            >
              <option value="">Select type…</option>
              {eventTypes.map((t) => (
                <option key={t.id} value={t.id}>{t.label}</option>
              ))}
            </select>
            {errors.event_type_id && <p className="text-xs text-red-400 mt-1">{errors.event_type_id}</p>}
          </div>

          {/* Custom type label — shown only when type key === 'custom' */}
          {isCustomType && (
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Custom Type Label <span className="text-red-400">*</span></label>
              <input
                type="text"
                value={formData.custom_type_label}
                onChange={(e) => setFormData((p) => ({ ...p, custom_type_label: e.target.value }))}
                placeholder="e.g. Department Hackathon"
                className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
                id="event-custom-label"
              />
              {errors.custom_type_label && <p className="text-xs text-red-400 mt-1">{errors.custom_type_label}</p>}
            </div>
          )}

          {/* Dates */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Start Date <span className="text-red-400">*</span></label>
              <input
                type="date"
                value={formData.start_date}
                onChange={(e) => setFormData((p) => ({ ...p, start_date: e.target.value }))}
                className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
                id="event-start-date"
              />
              {errors.start_date && <p className="text-xs text-red-400 mt-1">{errors.start_date}</p>}
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">End Date <span className="text-red-400">*</span></label>
              <input
                type="date"
                value={formData.end_date}
                onChange={(e) => setFormData((p) => ({ ...p, end_date: e.target.value }))}
                className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-blue-500"
                id="event-end-date"
              />
              {errors.end_date && <p className="text-xs text-red-400 mt-1">{errors.end_date}</p>}
            </div>
          </div>

          {/* Out-of-range warning */}
          {isOutOfRange && (
            <p className="text-xs text-yellow-400 bg-yellow-950/20 border border-yellow-800 rounded-lg px-3 py-2">
              ⚠ This event's start date is outside the semester date range. It will be ignored during plan generation for dates beyond the semester.
            </p>
          )}

          {/* Description */}
          <div>
            <label className="block text-xs font-medium text-slate-400 mb-1">Description <span className="text-slate-600">(optional)</span></label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData((p) => ({ ...p, description: e.target.value }))}
              placeholder="Any additional notes…"
              rows={2}
              className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-blue-500 resize-none"
              id="event-description"
            />
          </div>

          {/* Attendance impact flags */}
          {selectedType && (
            <div>
              <p className="text-xs font-medium text-slate-400 mb-2">
                Attendance Impact Flags
                <span className="text-slate-600 ml-1 font-normal">— pre-filled from type defaults. Click to override.</span>
              </p>
              <div className="space-y-2">
                {FLAG_CONFIG.map(({ key, defaultKey, label }) => {
                  const value = resolvedFlag(key, defaultKey);
                  const isOverridden = formData[key] !== null;
                  return (
                    <button
                      key={key}
                      type="button"
                      onClick={() => toggleFlag(key, defaultKey)}
                      className={[
                        'w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm',
                        'border transition-colors',
                        isOverridden
                          ? 'border-blue-600/50 bg-blue-950/20'
                          : 'border-slate-700 bg-slate-900/50 hover:border-slate-600',
                      ].join(' ')}
                      id={`event-flag-${key}`}
                    >
                      <span className="text-slate-300">{label}</span>
                      <div className="flex items-center gap-2">
                        {isOverridden && (
                          <span className="text-xs text-blue-400">overridden</span>
                        )}
                        <span
                          className={[
                            'px-2 py-0.5 rounded-full text-xs font-medium',
                            value
                              ? 'bg-green-900/50 text-green-400'
                              : 'bg-slate-700 text-slate-400',
                          ].join(' ')}
                        >
                          {value ? 'Yes' : 'No'}
                        </span>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-3 px-6 py-4 border-t border-slate-700">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-sm text-slate-400 hover:text-slate-200 transition-colors"
            id="event-modal-cancel"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors"
            id="event-modal-save"
          >
            {initialData ? 'Save Changes' : 'Add Event'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default EventFormModal;
