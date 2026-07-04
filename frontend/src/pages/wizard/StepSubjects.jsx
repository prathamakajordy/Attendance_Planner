/**
 * StepSubjects — Step 3 of the Setup Wizard.
 *
 * Collects: list of subjects with name, code, held_count, present_count, min_percentage_override.
 *
 * Per SRD Section 19 validation:
 *   - held_count >= 0, present_count >= 0
 *   - present_count <= held_count
 *   - min_percentage_override, if set, must be in (0, 100]
 *
 * Note: held/present counts are manually maintained by the user (MVP).
 * The system does NOT automatically update them.
 *
 * Props:
 *   subjects: SubjectData[]
 *   onChange: (subjects: SubjectData[]) => void
 *   errors: { [index]: { field: string } }
 */

const EMPTY_SUBJECT = {
  name: '',
  code: '',
  held_count: 0,
  present_count: 0,
  min_percentage_override: '',
};

function StepSubjects({ subjects, onChange, errors }) {
  const addSubject = () => {
    onChange([...subjects, { ...EMPTY_SUBJECT }]);
  };

  const removeSubject = (index) => {
    onChange(subjects.filter((_, i) => i !== index));
  };

  const updateSubject = (index, field, value) => {
    const updated = subjects.map((sub, i) =>
      i === index ? { ...sub, [field]: value } : sub
    );
    onChange(updated);
  };

  return (
    <div className="space-y-5">
      <div>
        <h2 className="text-xl font-semibold text-slate-100">Subjects & Attendance</h2>
        <p className="text-sm text-slate-400 mt-1">
          Add all subjects you're enrolled in this semester. Enter your current held and attended lecture counts — you can update these any time.
        </p>
      </div>

      {/* Manual update notice */}
      <div className="flex gap-2 items-start bg-blue-950/30 border border-blue-800/50 rounded-lg px-4 py-3">
        <svg className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p className="text-xs text-blue-300">
          <strong>MVP Note:</strong> Held and present counts are entered manually. The system does not automatically track real-time attendance. Update these counts when your actual attendance changes, then click "Recalculate Plan" on the Dashboard.
        </p>
      </div>

      {/* Global error (no subjects) */}
      {errors._list && (
        <p className="text-sm text-red-400 bg-red-950/30 border border-red-800 rounded-lg px-4 py-2.5">{errors._list}</p>
      )}

      {/* Subject rows */}
      <div className="space-y-3">
        {subjects.map((sub, index) => {
          const rowErrors = errors[index] || {};
          return (
            <div
              key={index}
              className="bg-slate-800/60 border border-slate-700 rounded-xl p-4"
            >
              {/* Row header */}
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                  Subject {index + 1}
                </span>
                <button
                  type="button"
                  onClick={() => removeSubject(index)}
                  className="text-slate-600 hover:text-red-400 transition-colors"
                  aria-label={`Remove subject ${index + 1}`}
                  id={`subject-remove-${index}`}
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {/* Name */}
                <div className="col-span-2 md:col-span-1">
                  <label className="block text-xs text-slate-400 mb-1">Name <span className="text-red-400">*</span></label>
                  <input
                    type="text"
                    value={sub.name}
                    onChange={(e) => updateSubject(index, 'name', e.target.value)}
                    placeholder="e.g. DBMS"
                    className={[
                      'w-full bg-slate-900 border rounded-lg px-3 py-2 text-sm text-slate-200',
                      'focus:outline-none focus:border-blue-500 transition-colors',
                      rowErrors.name ? 'border-red-500' : 'border-slate-600',
                    ].join(' ')}
                    id={`subject-name-${index}`}
                  />
                  {rowErrors.name && <p className="text-xs text-red-400 mt-1">{rowErrors.name}</p>}
                </div>

                {/* Code */}
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Code <span className="text-slate-600">(opt.)</span></label>
                  <input
                    type="text"
                    value={sub.code}
                    onChange={(e) => updateSubject(index, 'code', e.target.value)}
                    placeholder="CS301"
                    className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-blue-500 transition-colors"
                    id={`subject-code-${index}`}
                  />
                </div>

                {/* Min % override */}
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Min % Override <span className="text-slate-600">(opt.)</span></label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={sub.min_percentage_override}
                    onChange={(e) => updateSubject(index, 'min_percentage_override', e.target.value)}
                    placeholder="75"
                    className={[
                      'w-full bg-slate-900 border rounded-lg px-3 py-2 text-sm text-slate-200',
                      'focus:outline-none focus:border-blue-500 transition-colors',
                      rowErrors.min_percentage_override ? 'border-red-500' : 'border-slate-600',
                    ].join(' ')}
                    id={`subject-min-${index}`}
                  />
                  {rowErrors.min_percentage_override && (
                    <p className="text-xs text-red-400 mt-1">{rowErrors.min_percentage_override}</p>
                  )}
                </div>

                {/* Held count */}
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Classes Held</label>
                  <input
                    type="number"
                    min="0"
                    value={sub.held_count}
                    onChange={(e) => updateSubject(index, 'held_count', parseInt(e.target.value, 10) || 0)}
                    className={[
                      'w-full bg-slate-900 border rounded-lg px-3 py-2 text-sm text-slate-200',
                      'focus:outline-none focus:border-blue-500 transition-colors',
                      rowErrors.held_count ? 'border-red-500' : 'border-slate-600',
                    ].join(' ')}
                    id={`subject-held-${index}`}
                  />
                  {rowErrors.held_count && <p className="text-xs text-red-400 mt-1">{rowErrors.held_count}</p>}
                </div>

                {/* Present count */}
                <div>
                  <label className="block text-xs text-slate-400 mb-1">Classes Attended</label>
                  <input
                    type="number"
                    min="0"
                    value={sub.present_count}
                    onChange={(e) => updateSubject(index, 'present_count', parseInt(e.target.value, 10) || 0)}
                    className={[
                      'w-full bg-slate-900 border rounded-lg px-3 py-2 text-sm text-slate-200',
                      'focus:outline-none focus:border-blue-500 transition-colors',
                      rowErrors.present_count ? 'border-red-500' : 'border-slate-600',
                    ].join(' ')}
                    id={`subject-present-${index}`}
                  />
                  {rowErrors.present_count && <p className="text-xs text-red-400 mt-1">{rowErrors.present_count}</p>}
                </div>
              </div>

              {/* Running percentage indicator */}
              {sub.held_count > 0 && (
                <div className="mt-3 flex items-center gap-2">
                  <div className="flex-1 bg-slate-700 rounded-full h-1.5">
                    <div
                      className="bg-blue-500 h-1.5 rounded-full transition-all"
                      style={{ width: `${Math.min(100, (sub.present_count / sub.held_count) * 100)}%` }}
                    />
                  </div>
                  <span className="text-xs text-slate-400 w-12 text-right">
                    {((sub.present_count / sub.held_count) * 100).toFixed(1)}%
                  </span>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Add subject button */}
      <button
        type="button"
        onClick={addSubject}
        className="w-full flex items-center justify-center gap-2 py-3 border border-dashed border-slate-600 rounded-xl text-sm text-slate-400 hover:text-slate-200 hover:border-slate-500 transition-colors"
        id="add-subject-btn"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        Add Subject
      </button>
    </div>
  );
}

/**
 * Validates the Subjects step per SRD Section 19.
 */
export function validateSubjects(subjects) {
  const errors = {};

  if (subjects.length === 0) {
    errors._list = 'At least one subject is required before generating a plan.';
    return { isValid: false, errors };
  }

  const seenNames = new Set();
  subjects.forEach((sub, index) => {
    const rowErrors = {};
    const normalizedName = sub.name.trim().toLowerCase();

    if (!sub.name.trim()) {
      rowErrors.name = 'Subject name is required.';
    } else if (seenNames.has(normalizedName)) {
      rowErrors.name = 'Duplicate subject name.';
    } else {
      seenNames.add(normalizedName);
    }

    if (sub.held_count < 0) rowErrors.held_count = 'Cannot be negative.';
    if (sub.present_count < 0) rowErrors.present_count = 'Cannot be negative.';
    if (sub.present_count > sub.held_count) {
      rowErrors.present_count = 'Cannot exceed classes held.';
    }
    if (sub.min_percentage_override !== '' && sub.min_percentage_override !== null) {
      const val = Number(sub.min_percentage_override);
      if (val <= 0 || val > 100) {
        rowErrors.min_percentage_override = 'Must be between 1 and 100.';
      }
    }

    if (Object.keys(rowErrors).length > 0) errors[index] = rowErrors;
  });

  return { isValid: Object.keys(errors).length === 0, errors };
}

export default StepSubjects;
