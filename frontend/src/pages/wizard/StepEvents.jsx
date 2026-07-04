import { useState } from 'react';
import EventFormModal from '../../components/wizard/EventFormModal';

/**
 * StepEvents — Step 5 of the Setup Wizard (optional/skippable).
 *
 * Collects: list of semester events.
 * This step is optional per SRD Section 10.1.e —
 * events "can be skipped/added later."
 *
 * The "Skip for now" button is handled by WizardNavButtons (isSkippable=true).
 *
 * Props:
 *   events: SemesterEventData[]
 *   semesterStartDate: string
 *   semesterEndDate: string
 *   onChange: (events) => void
 *   errors: {} — events step has no blocking errors (it's optional)
 */
function StepEvents({ events, semesterStartDate, semesterEndDate, onChange }) {
  const [showModal, setShowModal] = useState(false);
  const [editingIndex, setEditingIndex] = useState(null);

  const openAddModal = () => {
    setEditingIndex(null);
    setShowModal(true);
  };

  const openEditModal = (index) => {
    setEditingIndex(index);
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingIndex(null);
  };

  const handleSave = (eventData) => {
    if (editingIndex !== null) {
      const updated = events.map((e, i) => (i === editingIndex ? eventData : e));
      onChange(updated);
    } else {
      onChange([...events, eventData]);
    }
    closeModal();
  };

  const removeEvent = (index) => {
    onChange(events.filter((_, i) => i !== index));
  };

  // Format date as "DD Mon YYYY" for display
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-xl font-semibold text-slate-100">Semester Events</h2>
        <p className="text-sm text-slate-400 mt-1">
          Add holidays, examination periods, college events, industrial visits, and any other dates that affect your schedule. You can skip this step and add events later from the Semester Events Manager.
        </p>
      </div>

      {/* Skip notice */}
      <div className="flex gap-2 items-start bg-slate-800/40 border border-slate-700 rounded-lg px-4 py-3">
        <svg className="w-4 h-4 text-slate-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="text-xs text-slate-400">
          This step is <strong>optional</strong>. Events can be added or edited at any time from the Dashboard. Each event type has pre-set attendance impact flags that you can override per event.
        </p>
      </div>

      {/* Events list */}
      {events.length === 0 ? (
        <div className="text-center py-10 border border-dashed border-slate-700 rounded-xl text-slate-500">
          <svg className="w-8 h-8 mx-auto mb-2 opacity-40" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          <p className="text-sm">No events added. Click "Add Event" or skip this step.</p>
        </div>
      ) : (
        <div className="space-y-2">
          {events.map((event, index) => (
            <div
              key={index}
              className="flex items-center gap-3 bg-slate-800/60 border border-slate-700 rounded-lg px-4 py-3"
            >
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-200 truncate">{event.name}</p>
                <p className="text-xs text-slate-500 mt-0.5">
                  {formatDate(event.start_date)}
                  {event.end_date !== event.start_date && ` → ${formatDate(event.end_date)}`}
                </p>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <button
                  type="button"
                  onClick={() => openEditModal(index)}
                  className="text-slate-500 hover:text-slate-300 transition-colors p-1"
                  aria-label={`Edit ${event.name}`}
                  id={`event-edit-${index}`}
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button
                  type="button"
                  onClick={() => removeEvent(index)}
                  className="text-slate-600 hover:text-red-400 transition-colors p-1"
                  aria-label={`Remove ${event.name}`}
                  id={`event-remove-${index}`}
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add event button */}
      <button
        type="button"
        onClick={openAddModal}
        className="w-full flex items-center justify-center gap-2 py-3 border border-dashed border-slate-600 rounded-xl text-sm text-slate-400 hover:text-slate-200 hover:border-slate-500 transition-colors"
        id="add-event-btn"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        Add Semester Event
      </button>

      {/* Modal */}
      {showModal && (
        <EventFormModal
          initialData={editingIndex !== null ? events[editingIndex] : null}
          semesterStartDate={semesterStartDate}
          semesterEndDate={semesterEndDate}
          onSave={handleSave}
          onClose={closeModal}
        />
      )}
    </div>
  );
}

export default StepEvents;
