/**
 * WizardNavButtons — Back / Next / Skip / Finish navigation row.
 *
 * Props:
 *   currentStep: number (1-based)
 *   totalSteps: number
 *   onBack: () => void
 *   onNext: () => void
 *   onSkip: () => void — only shown when the step is optional
 *   onFinish: () => void — shown on review screen
 *   isSkippable: bool — shows Skip button when true
 *   isReview: bool — shows Finish instead of Next when true
 *   isSubmitting: bool — disables buttons during API submission
 */
function WizardNavButtons({
  currentStep,
  onBack,
  onNext,
  onSkip,
  onFinish,
  isSkippable = false,
  isReview = false,
  isSubmitting = false,
}) {
  const isFirstStep = currentStep === 1;

  return (
    <div className="flex items-center justify-between pt-6 mt-6 border-t border-slate-700">
      {/* Back button */}
      <button
        type="button"
        onClick={onBack}
        disabled={isFirstStep || isSubmitting}
        className={[
          'flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
          isFirstStep || isSubmitting
            ? 'text-slate-600 cursor-not-allowed'
            : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700',
        ].join(' ')}
        id="wizard-back-btn"
      >
        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
        </svg>
        Back
      </button>

      {/* Right side: Skip + Next/Finish */}
      <div className="flex items-center gap-3">
        {isSkippable && !isReview && (
          <button
            type="button"
            onClick={onSkip}
            disabled={isSubmitting}
            className="px-4 py-2 text-sm font-medium text-slate-400 hover:text-slate-200 transition-colors"
            id="wizard-skip-btn"
          >
            Skip for now
          </button>
        )}

        {isReview ? (
          <button
            type="button"
            onClick={onFinish}
            disabled={isSubmitting}
            className={[
              'flex items-center gap-2 px-6 py-2.5 rounded-lg text-sm font-semibold',
              'bg-blue-600 hover:bg-blue-500 text-white transition-colors',
              'disabled:opacity-60 disabled:cursor-not-allowed',
            ].join(' ')}
            id="wizard-finish-btn"
          >
            {isSubmitting ? (
              <>
                <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
                Saving…
              </>
            ) : (
              <>
                Finish Setup
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </>
            )}
          </button>
        ) : (
          <button
            type="button"
            onClick={onNext}
            disabled={isSubmitting}
            className={[
              'flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-semibold',
              'bg-blue-600 hover:bg-blue-500 text-white transition-colors',
              'disabled:opacity-60 disabled:cursor-not-allowed',
            ].join(' ')}
            id="wizard-next-btn"
          >
            Continue
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}

export default WizardNavButtons;
