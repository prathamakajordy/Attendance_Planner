/**
 * StepAttendancePolicy — Step 2 of the Setup Wizard.
 *
 * Collects: min_overall_percentage, min_subject_percentage.
 * Validation per SRD Section 19: both must be in range (0, 100].
 *
 * Props:
 *   data: { min_overall_percentage, min_subject_percentage }
 *   onChange: (field, value) => void
 *   errors: { min_overall_percentage?, min_subject_percentage? }
 */
function StepAttendancePolicy({ data, onChange, errors }) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-100">Attendance Policy</h2>
        <p className="text-sm text-slate-400 mt-1">
          Set the minimum attendance percentages required by your college. These are used as hard constraints — the recommendation engine will never generate a plan that violates them.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {/* Overall percentage */}
        <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-5">
          <label htmlFor="policy-overall" className="block text-sm font-semibold text-slate-200 mb-1">
            Minimum Overall Attendance
          </label>
          <p className="text-xs text-slate-500 mb-3">
            The aggregate attendance across all subjects combined.
          </p>
          <div className="flex items-center gap-2">
            <input
              id="policy-overall"
              type="number"
              min="1"
              max="100"
              step="0.5"
              value={data.min_overall_percentage}
              onChange={(e) => onChange('min_overall_percentage', parseFloat(e.target.value) || '')}
              className={[
                'w-24 bg-slate-900 border rounded-lg px-3 py-2 text-sm text-slate-200',
                'focus:outline-none focus:border-blue-500 transition-colors text-right',
                errors.min_overall_percentage ? 'border-red-500' : 'border-slate-600',
              ].join(' ')}
            />
            <span className="text-slate-400 text-sm">%</span>
          </div>
          {errors.min_overall_percentage && (
            <p className="text-xs text-red-400 mt-1.5">{errors.min_overall_percentage}</p>
          )}
        </div>

        {/* Per-subject percentage */}
        <div className="bg-slate-800/60 border border-slate-700 rounded-xl p-5">
          <label htmlFor="policy-subject" className="block text-sm font-semibold text-slate-200 mb-1">
            Minimum Per-Subject Attendance
          </label>
          <p className="text-xs text-slate-500 mb-3">
            The minimum required in each individual subject. Can be overridden per subject in the next step.
          </p>
          <div className="flex items-center gap-2">
            <input
              id="policy-subject"
              type="number"
              min="1"
              max="100"
              step="0.5"
              value={data.min_subject_percentage}
              onChange={(e) => onChange('min_subject_percentage', parseFloat(e.target.value) || '')}
              className={[
                'w-24 bg-slate-900 border rounded-lg px-3 py-2 text-sm text-slate-200',
                'focus:outline-none focus:border-blue-500 transition-colors text-right',
                errors.min_subject_percentage ? 'border-red-500' : 'border-slate-600',
              ].join(' ')}
            />
            <span className="text-slate-400 text-sm">%</span>
          </div>
          {errors.min_subject_percentage && (
            <p className="text-xs text-red-400 mt-1.5">{errors.min_subject_percentage}</p>
          )}
        </div>
      </div>

      <p className="text-xs text-slate-500">
        Most colleges require 75%. If your college has different rules per subject, you can set a per-subject override in the next step.
      </p>
    </div>
  );
}

/**
 * Validates the Attendance Policy step.
 */
export function validateAttendancePolicy(data) {
  const errors = {};
  const overall = Number(data.min_overall_percentage);
  const subject = Number(data.min_subject_percentage);

  if (!data.min_overall_percentage && data.min_overall_percentage !== 0) {
    errors.min_overall_percentage = 'Required.';
  } else if (overall <= 0 || overall > 100) {
    errors.min_overall_percentage = 'Must be between 1 and 100.';
  }

  if (!data.min_subject_percentage && data.min_subject_percentage !== 0) {
    errors.min_subject_percentage = 'Required.';
  } else if (subject <= 0 || subject > 100) {
    errors.min_subject_percentage = 'Must be between 1 and 100.';
  }

  return { isValid: Object.keys(errors).length === 0, errors };
}

export default StepAttendancePolicy;
