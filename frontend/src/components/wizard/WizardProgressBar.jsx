/**
 * WizardProgressBar — shows the 5 data-entry steps with current state.
 *
 * Props:
 *   currentStep: number (1-5)
 *   steps: string[] — step labels
 */
function WizardProgressBar({ currentStep, steps }) {
  return (
    <div className="flex items-center justify-between w-full mb-8">
      {steps.map((label, index) => {
        const stepNumber = index + 1;
        const isComplete = stepNumber < currentStep;
        const isActive = stepNumber === currentStep;

        return (
          <div key={stepNumber} className="flex items-center flex-1">
            {/* Step indicator circle */}
            <div className="flex flex-col items-center flex-shrink-0">
              <div
                className={[
                  'w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold',
                  'transition-all duration-300',
                  isComplete
                    ? 'bg-blue-500 text-white'
                    : isActive
                    ? 'bg-blue-600 text-white ring-4 ring-blue-600/30'
                    : 'bg-slate-700 text-slate-400',
                ].join(' ')}
                aria-current={isActive ? 'step' : undefined}
              >
                {isComplete ? (
                  /* Checkmark for completed steps */
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  stepNumber
                )}
              </div>
              <span
                className={[
                  'mt-2 text-xs font-medium text-center max-w-[72px] leading-tight',
                  isActive ? 'text-blue-400' : isComplete ? 'text-slate-400' : 'text-slate-600',
                ].join(' ')}
              >
                {label}
              </span>
            </div>

            {/* Connector line (not after last step) */}
            {index < steps.length - 1 && (
              <div
                className={[
                  'flex-1 h-0.5 mx-2 mt-[-18px] transition-all duration-300',
                  isComplete ? 'bg-blue-500' : 'bg-slate-700',
                ].join(' ')}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}

export default WizardProgressBar;
