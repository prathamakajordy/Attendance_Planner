/**
 * StepSemesterDetails — Step 1 of the Setup Wizard.
 *
 * Collects: semester name, start date, end date.
 * Validation per SRD Section 19: end_date must be >= start_date.
 *
 * Props:
 *   data: { name, start_date, end_date }
 *   onChange: (field, value) => void
 *   errors: { name?, start_date?, end_date? }
 */
function StepSemesterDetails({ data, onChange, errors }) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-100">Semester Details</h2>
        <p className="text-sm text-slate-400 mt-1">
          Enter the name and date range for your semester. The system will use these dates to build your academic calendar.
        </p>
      </div>

      {/* Semester Name */}
      <div>
        <label htmlFor="semester-name" className="block text-sm font-medium text-slate-300 mb-1.5">
          Semester Name <span className="text-red-400">*</span>
        </label>
        <input
          id="semester-name"
          type="text"
          value={data.name}
          onChange={(e) => onChange('name', e.target.value)}
          placeholder="e.g. Sem IV 2026"
          className={[
            'w-full bg-slate-900 border rounded-lg px-4 py-2.5 text-sm text-slate-200',
            'placeholder-slate-600 focus:outline-none focus:border-blue-500 transition-colors',
            errors.name ? 'border-red-500' : 'border-slate-600',
          ].join(' ')}
        />
        {errors.name && <p className="text-xs text-red-400 mt-1.5">{errors.name}</p>}
      </div>

      {/* Date Range */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label htmlFor="semester-start" className="block text-sm font-medium text-slate-300 mb-1.5">
            Start Date <span className="text-red-400">*</span>
          </label>
          <input
            id="semester-start"
            type="date"
            value={data.start_date}
            onChange={(e) => onChange('start_date', e.target.value)}
            className={[
              'w-full bg-slate-900 border rounded-lg px-4 py-2.5 text-sm text-slate-200',
              'focus:outline-none focus:border-blue-500 transition-colors',
              errors.start_date ? 'border-red-500' : 'border-slate-600',
            ].join(' ')}
          />
          {errors.start_date && <p className="text-xs text-red-400 mt-1.5">{errors.start_date}</p>}
        </div>

        <div>
          <label htmlFor="semester-end" className="block text-sm font-medium text-slate-300 mb-1.5">
            End Date <span className="text-red-400">*</span>
          </label>
          <input
            id="semester-end"
            type="date"
            value={data.end_date}
            onChange={(e) => onChange('end_date', e.target.value)}
            className={[
              'w-full bg-slate-900 border rounded-lg px-4 py-2.5 text-sm text-slate-200',
              'focus:outline-none focus:border-blue-500 transition-colors',
              errors.end_date ? 'border-red-500' : 'border-slate-600',
            ].join(' ')}
          />
          {errors.end_date && <p className="text-xs text-red-400 mt-1.5">{errors.end_date}</p>}
        </div>
      </div>

      {/* Helper note */}
      <p className="text-xs text-slate-500">
        Include the full semester range — from the first day of classes to the last. Holidays and exam periods are defined separately in the Semester Events step.
      </p>
    </div>
  );
}

/**
 * Validates the Semester Details step.
 * Returns { isValid: bool, errors: object }
 */
export function validateSemesterDetails(data) {
  const errors = {};
  if (!data.name.trim()) errors.name = 'Semester name is required.';
  if (!data.start_date) errors.start_date = 'Start date is required.';
  if (!data.end_date) errors.end_date = 'End date is required.';
  if (data.start_date && data.end_date && data.end_date < data.start_date) {
    errors.end_date = 'End date must be on or after start date.';
  }
  return { isValid: Object.keys(errors).length === 0, errors };
}

export default StepSemesterDetails;
