import { WEEKDAYS } from '../../components/wizard/TimetableSlotRow';

/**
 * StepReview — Final review screen before submitting to the API.
 *
 * Displays a read-only summary of all entered data grouped by section.
 * No validation happens here — all validation was done in previous steps.
 *
 * Props:
 *   formData: { semester, policy, subjects, timetable, events }
 *   submitError: string | null — error from the API submission
 */
function StepReview({ formData, submitError }) {
  const { semester, policy, subjects, timetable, events } = formData;

  const formatDate = (dateStr) => {
    if (!dateStr) return '—';
    return new Date(dateStr + 'T00:00:00').toLocaleDateString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric',
    });
  };

  const weekdayLabel = (value) => WEEKDAYS.find((d) => d.value === value)?.label || '—';

  const Section = ({ title, children }) => (
    <div className="bg-slate-800/60 border border-slate-700 rounded-xl overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-700 bg-slate-800">
        <h3 className="text-sm font-semibold text-slate-300">{title}</h3>
      </div>
      <div className="px-4 py-3">{children}</div>
    </div>
  );

  const Row = ({ label, value }) => (
    <div className="flex justify-between items-start py-1.5 text-sm border-b border-slate-700/50 last:border-0">
      <span className="text-slate-500 flex-shrink-0 mr-4">{label}</span>
      <span className="text-slate-200 text-right">{value}</span>
    </div>
  );

  // Group timetable by weekday for display
  const timetableByDay = WEEKDAYS
    .map((day) => ({
      ...day,
      slots: timetable
        .filter((slot) => slot.weekday === day.value)
        .sort((a, b) => a.start_time.localeCompare(b.start_time)),
    }))
    .filter(({ slots }) => slots.length > 0);

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-xl font-semibold text-slate-100">Review & Submit</h2>
        <p className="text-sm text-slate-400 mt-1">
          Review your configuration below. Click "Finish Setup" to save everything and go to the Dashboard.
        </p>
      </div>

      {/* API error */}
      {submitError && (
        <div className="bg-red-950/40 border border-red-700 rounded-lg px-4 py-3 text-sm text-red-300">
          <strong>Submission failed:</strong> {submitError}
        </div>
      )}

      {/* Semester */}
      <Section title="Semester Details">
        <Row label="Name" value={semester.name || '—'} />
        <Row label="Start Date" value={formatDate(semester.start_date)} />
        <Row label="End Date" value={formatDate(semester.end_date)} />
      </Section>

      {/* Policy */}
      <Section title="Attendance Policy">
        <Row label="Min. Overall" value={`${policy.min_overall_percentage}%`} />
        <Row label="Min. Per-Subject" value={`${policy.min_subject_percentage}%`} />
      </Section>

      {/* Subjects */}
      <Section title={`Subjects (${subjects.length})`}>
        {subjects.length === 0 ? (
          <p className="text-sm text-slate-500 py-2">No subjects added.</p>
        ) : (
          <div className="space-y-2">
            {subjects.map((sub, i) => (
              <div key={i} className="flex justify-between items-start text-sm py-1.5 border-b border-slate-700/50 last:border-0">
                <div>
                  <span className="text-slate-200 font-medium">{sub.name}</span>
                  {sub.code && <span className="text-slate-500 ml-2 text-xs">({sub.code})</span>}
                </div>
                <div className="text-right">
                  <span className="text-slate-400 text-xs">
                    {sub.present_count}/{sub.held_count} held
                    {sub.held_count > 0 && ` · ${((sub.present_count / sub.held_count) * 100).toFixed(0)}%`}
                  </span>
                  {sub.min_percentage_override && (
                    <span className="block text-slate-500 text-xs">Min: {sub.min_percentage_override}%</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </Section>

      {/* Timetable */}
      <Section title={`Timetable (${timetable.length} slot${timetable.length !== 1 ? 's' : ''})`}>
        {timetableByDay.length === 0 ? (
          <p className="text-sm text-slate-500 py-2">No timetable slots added.</p>
        ) : (
          <div className="space-y-3">
            {timetableByDay.map(({ label, slots }) => (
              <div key={label}>
                <p className="text-xs text-slate-500 font-medium mb-1.5">{label}</p>
                {slots.map((slot, si) => {
                  const subjectName = subjects[slot.subject_index]?.name || '—';
                  return (
                    <div key={si} className="flex justify-between text-sm py-1 pl-3 border-l-2 border-slate-700">
                      <span className="text-slate-300">{subjectName}</span>
                      <span className="text-slate-500">{slot.start_time} – {slot.end_time}</span>
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        )}
      </Section>

      {/* Events */}
      <Section title={`Semester Events (${events.length})`}>
        {events.length === 0 ? (
          <p className="text-sm text-slate-500 py-2">No events added. You can add them later from the Dashboard.</p>
        ) : (
          <div className="space-y-1.5">
            {events.map((event, i) => (
              <div key={i} className="flex justify-between items-center text-sm py-1.5 border-b border-slate-700/50 last:border-0">
                <span className="text-slate-300">{event.name}</span>
                <span className="text-slate-500 text-xs">
                  {formatDate(event.start_date)}
                  {event.end_date !== event.start_date && ` → ${formatDate(event.end_date)}`}
                </span>
              </div>
            ))}
          </div>
        )}
      </Section>
    </div>
  );
}

export default StepReview;
