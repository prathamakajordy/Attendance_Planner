import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import WizardProgressBar from '../../components/wizard/WizardProgressBar';
import WizardNavButtons from '../../components/wizard/WizardNavButtons';
import StepSemesterDetails, { validateSemesterDetails } from './StepSemesterDetails';
import StepAttendancePolicy, { validateAttendancePolicy } from './StepAttendancePolicy';
import StepSubjects, { validateSubjects } from './StepSubjects';
import StepTimetable, { validateTimetable } from './StepTimetable';
import StepEvents from './StepEvents';
import StepReview from './StepReview';
import {
  createSemester,
  createSubject,
  createTimetableSlot,
  createSemesterEvent,
} from '../../api/client';

// The 5 data-entry step labels shown in the progress bar.
const STEP_LABELS = ['Semester', 'Policy', 'Subjects', 'Timetable', 'Events'];

// Total steps: 5 data entry + 1 review = 6 "screens", but progress bar shows 5.
const TOTAL_DATA_STEPS = 5;
const REVIEW_STEP = 6;

const INITIAL_FORM_DATA = {
  semester: { name: '', start_date: '', end_date: '', student_groups: '' },
  policy: { min_overall_percentage: 75, min_subject_percentage: 75 },
  subjects: [],
  timetable: [],
  events: [],
};

function SetupWizard() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState(INITIAL_FORM_DATA);
  const [stepErrors, setStepErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  // ── Field updaters per step ──────────────────────────────────────────────

  const updateSemester = (field, value) => {
    setFormData((prev) => ({ ...prev, semester: { ...prev.semester, [field]: value } }));
  };

  const updatePolicy = (field, value) => {
    setFormData((prev) => ({ ...prev, policy: { ...prev.policy, [field]: value } }));
  };

  const updateSubjects = (subjects) => {
    setFormData((prev) => ({ ...prev, subjects }));
  };

  const updateTimetable = (timetable) => {
    setFormData((prev) => ({ ...prev, timetable }));
  };

  const updateEvents = (events) => {
    setFormData((prev) => ({ ...prev, events }));
  };

  // ── Step validation ──────────────────────────────────────────────────────

  const validateCurrentStep = () => {
    let result = { isValid: true, errors: {} };
    switch (currentStep) {
      case 1: result = validateSemesterDetails(formData.semester); break;
      case 2: result = validateAttendancePolicy(formData.policy); break;
      case 3: result = validateSubjects(formData.subjects); break;
      case 4: result = validateTimetable(formData.timetable); break;
      case 5: result = { isValid: true, errors: {} }; break; // events step is optional
      default: break;
    }
    setStepErrors(result.errors);
    return result.isValid;
  };

  // ── Navigation ───────────────────────────────────────────────────────────

  const handleNext = () => {
    if (!validateCurrentStep()) return;
    setStepErrors({});
    setCurrentStep((prev) => (currentStep < TOTAL_DATA_STEPS ? prev + 1 : REVIEW_STEP));
  };

  const handleBack = () => {
    setStepErrors({});
    setCurrentStep((prev) => {
      if (prev === REVIEW_STEP) return TOTAL_DATA_STEPS;
      return Math.max(1, prev - 1);
    });
  };

  const handleSkip = () => {
    // Step 5 (Events) is the only skippable step per SRD Section 10.1.e
    setStepErrors({});
    setCurrentStep(REVIEW_STEP);
  };

  // ── API Submission ───────────────────────────────────────────────────────

  /**
   * Sequential API calls in the dependency order required:
   * 1. POST /semesters → get semester.id
   * 2. For each subject: POST /semesters/{id}/subjects → get subject.id
   * 3. For each timetable slot: POST /semesters/{id}/timetable (uses subject.id from step 2)
   * 4. For each event: POST /semesters/{id}/events
   */
  const handleFinish = async () => {
    setIsSubmitting(true);
    setSubmitError(null);

    try {
      // Step 1: Create semester
      const semesterPayload = {
        ...formData.semester,
        student_groups: formData.semester.student_groups
          ? formData.semester.student_groups.split(',').map((g) => g.trim()).filter(Boolean)
          : [],
        min_overall_percentage: formData.policy.min_overall_percentage,
        min_subject_percentage: formData.policy.min_subject_percentage,
      };
      const { data: createdSemester } = await createSemester(semesterPayload);
      const semesterId = createdSemester.id;

      // Step 2: Create subjects (sequential; we need each subject's ID for timetable)
      const subjectIds = [];
      for (const subject of formData.subjects) {
        const subjectPayload = {
          name: subject.name.trim(),
          code: subject.code.trim() || null,
          held_count: subject.held_count,
          present_count: subject.present_count,
          min_percentage_override:
            subject.min_percentage_override !== '' && subject.min_percentage_override !== null
              ? Number(subject.min_percentage_override)
              : null,
        };
        const { data: createdSubject } = await createSubject(semesterId, subjectPayload);
        subjectIds.push(createdSubject.id);
      }

      // Step 3: Create timetable slots (uses subject_ids resolved above)
      for (let i = 0; i < formData.timetable.length; i++) {
        const slot = formData.timetable[i];
        const slotPayload = {
          subject_id: subjectIds[slot.subject_index],
          weekday: slot.weekday,
          start_time: slot.start_time,
          end_time: slot.end_time,
          order_index: i,
          required_groups: slot.required_groups
            ? slot.required_groups.split(',').map((g) => g.trim()).filter(Boolean)
            : [],
        };
        await createTimetableSlot(semesterId, slotPayload);
      }

      // Step 4: Create semester events (if any)
      for (const event of formData.events) {
        const eventPayload = {
          name: event.name.trim(),
          event_type_id: Number(event.event_type_id),
          custom_type_label: event.custom_type_label?.trim() || null,
          start_date: event.start_date,
          end_date: event.end_date,
          description: event.description?.trim() || null,
          cancels_lectures_override: event.cancels_lectures_override,
          counts_towards_attendance_override: event.counts_towards_attendance_override,
          is_working_day_override: event.is_working_day_override,
          exclude_from_recommendation_override: event.exclude_from_recommendation_override,
        };
        await createSemesterEvent(semesterId, eventPayload);
      }

      // All done — redirect to dashboard with the new semester ID
      navigate(`/dashboard?semester=${semesterId}`);
    } catch (error) {
      // Surface the first structured API error message, or a generic fallback
      const apiErrors = error?.response?.data?.errors;
      if (apiErrors && apiErrors.length > 0) {
        const msg = apiErrors.map((e) => e.message || e.msg).join(' ');
        setSubmitError(msg);
      } else {
        setSubmitError('An unexpected error occurred. Please check that the backend is running and try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // ── Render ───────────────────────────────────────────────────────────────

  const isReview = currentStep === REVIEW_STEP;
  const progressStep = isReview ? TOTAL_DATA_STEPS : currentStep; // bar stays at 5 on review

  return (
    <div className="min-h-screen bg-slate-900 flex items-start justify-center py-12 px-4">
      <div className="w-full max-w-2xl">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-2xl font-bold text-slate-100">
            {isReview ? 'Review & Finish' : 'Set Up Your Semester'}
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            {isReview
              ? 'Confirm your configuration before saving.'
              : `Step ${currentStep} of ${TOTAL_DATA_STEPS}`}
          </p>
        </div>

        {/* Progress bar — only shown for data entry steps, not review */}
        {!isReview && (
          <WizardProgressBar currentStep={progressStep} steps={STEP_LABELS} />
        )}

        {/* Step card */}
        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-6 shadow-xl">
          {currentStep === 1 && (
            <StepSemesterDetails
              data={formData.semester}
              onChange={updateSemester}
              errors={stepErrors}
            />
          )}
          {currentStep === 2 && (
            <StepAttendancePolicy
              data={formData.policy}
              onChange={updatePolicy}
              errors={stepErrors}
            />
          )}
          {currentStep === 3 && (
            <StepSubjects
              subjects={formData.subjects}
              onChange={updateSubjects}
              errors={stepErrors}
            />
          )}
          {currentStep === 4 && (
            <StepTimetable
              timetable={formData.timetable}
              subjects={formData.subjects}
              onChange={updateTimetable}
              errors={stepErrors}
            />
          )}
          {currentStep === 5 && (
            <StepEvents
              events={formData.events}
              semesterStartDate={formData.semester.start_date}
              semesterEndDate={formData.semester.end_date}
              onChange={updateEvents}
            />
          )}
          {isReview && (
            <StepReview formData={formData} submitError={submitError} />
          )}

          {/* Navigation */}
          <WizardNavButtons
            currentStep={currentStep}
            onBack={handleBack}
            onNext={handleNext}
            onSkip={handleSkip}
            onFinish={handleFinish}
            isSkippable={currentStep === 5}
            isReview={isReview}
            isSubmitting={isSubmitting}
          />
        </div>
      </div>
    </div>
  );
}

export default SetupWizard;
