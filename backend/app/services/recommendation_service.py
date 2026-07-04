"""Recommendation Service: Orchestrates DB queries, academic eligibility filtering,
engine execution, and plan persistence.

This module is the ONLY bridge between the database layer and the frozen Recommendation Engine.
It must NOT duplicate any recommendation logic. All decisions live inside the engine.
"""
import json
from datetime import datetime
from sqlalchemy.orm import Session, joinedload

from app.models.semester import SemesterProfile
from app.models.subject import Subject
from app.models.timetable import TimetableSlot
from app.models.semester_event import SemesterEvent
from app.models.event_type_definition import EventTypeDefinition
from app.models.plan import PlanMetadata, PlanDay, PlanBlock

from app.engine.types import TimetableSlotRef
from app.engine.pipeline import generate_plan, PlanGenerationResult

# Engine version constant. Only updated when the frozen engine modules are patched.
ENGINE_VERSION = "v1.0"


class PlanNotGeneratedError(Exception):
    """Raised when GET /plan is called but no plan exists for the semester."""
    pass


class MissingPlanInputsError(Exception):
    """Raised when required data (subjects, timetable) is missing for plan generation."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def _filter_slots_for_eligibility(
    slots: list[TimetableSlot],
    student_groups: list[str],
) -> list[TimetableSlot]:
    """Filters timetable slots based on student academic eligibility.
    
    A slot is included if:
    - It has no required_groups (theory lecture, open to everyone), OR
    - At least one of its required_groups matches the student's student_groups.
    """
    eligible = []
    for slot in slots:
        if not slot.required_groups:
            eligible.append(slot)
        elif any(g in student_groups for g in slot.required_groups):
            eligible.append(slot)
    return eligible


def _db_slot_to_engine_ref(slot: TimetableSlot) -> TimetableSlotRef:
    """Converts a SQLAlchemy TimetableSlot model to a pure engine TimetableSlotRef dataclass."""
    return TimetableSlotRef(
        slot_id=slot.id,
        subject_id=slot.subject_id,
        weekday=int(slot.weekday),
        start_time=slot.start_time,
        end_time=slot.end_time,
        order_index=slot.order_index,
    )


def _persist_plan(
    db: Session,
    semester: SemesterProfile,
    result: PlanGenerationResult,
) -> None:
    """Purges existing plan data and persists the new engine output to the database.
    
    This implements the V1 single-plan-per-semester contract:
    delete old plan_days (cascade deletes plan_blocks) and old plan_metadata,
    then insert the new plan.
    """
    # Purge existing plan data for this semester
    db.query(PlanDay).filter(PlanDay.semester_id == semester.id).delete()
    db.query(PlanMetadata).filter(PlanMetadata.semester_id == semester.id).delete()

    # Persist metadata
    metadata = PlanMetadata(
        semester_id=semester.id,
        generated_at=datetime.utcnow(),
        engine_version=ENGINE_VERSION,
        overall_feasible=result.overall_feasible,
        overall_attendance_threshold=semester.min_overall_percentage,
        subject_attendance_threshold=semester.min_subject_percentage,
    )
    db.add(metadata)

    # Persist plan days and blocks
    for day_result in result.plan_days:
        plan_day = PlanDay(
            semester_id=semester.id,
            date=day_result.date,
            is_lecture_day=day_result.is_lecture_day,
            day_explanation=day_result.day_explanation,
        )
        db.add(plan_day)
        db.flush()  # Assigns plan_day.id for FK reference

        for block_result in day_result.blocks:
            plan_block = PlanBlock(
                plan_day_id=plan_day.id,
                start_time=block_result.start_time,
                end_time=block_result.end_time,
                subject_ids=json.dumps(block_result.subject_ids),
                recommendation=block_result.recommendation,
                block_explanation=block_result.block_explanation,
            )
            db.add(plan_block)

    db.commit()


def generate_and_persist_plan(db: Session, semester_id: int) -> PlanGenerationResult:
    """Full orchestration: query DB -> filter eligibility -> run engine -> persist.
    
    Returns the PlanGenerationResult from the engine for immediate API response.
    """
    # 1. Load semester with eager-loaded relationships
    semester = (
        db.query(SemesterProfile)
        .options(
            joinedload(SemesterProfile.subjects),
            joinedload(SemesterProfile.timetable_slots),
            joinedload(SemesterProfile.events).joinedload(SemesterEvent.event_type),
        )
        .filter(SemesterProfile.id == semester_id)
        .first()
    )

    if semester is None:
        from app.core.exceptions import SemesterNotFoundError
        raise SemesterNotFoundError()

    subjects: list[Subject] = semester.subjects
    all_slots: list[TimetableSlot] = semester.timetable_slots
    events: list[SemesterEvent] = semester.events

    # 2. Validate minimum inputs
    if not subjects:
        raise MissingPlanInputsError("No subjects found for this semester. Add subjects before generating a plan.")
    if not all_slots:
        raise MissingPlanInputsError("No timetable slots found for this semester. Add a timetable before generating a plan.")

    # 3. Academic Eligibility Filtering
    eligible_slots = _filter_slots_for_eligibility(all_slots, semester.student_groups)

    # 4. Convert DB models to engine input types
    timetable_refs = [_db_slot_to_engine_ref(s) for s in eligible_slots]
    event_types = {et.id: et for et in db.query(EventTypeDefinition).all()}

    # 5. Run the frozen Recommendation Engine
    result = generate_plan(semester, subjects, timetable_refs, events, event_types)

    # 6. Persist the result (replaces any existing plan)
    _persist_plan(db, semester, result)

    return result


def get_active_plan(db: Session, semester_id: int):
    """Retrieves the currently active plan for a semester from the database.
    
    Returns a tuple of (PlanMetadata, list[PlanDay]) or raises PlanNotGeneratedError.
    """
    # Verify semester exists
    semester = db.query(SemesterProfile).filter(SemesterProfile.id == semester_id).first()
    if semester is None:
        from app.core.exceptions import SemesterNotFoundError
        raise SemesterNotFoundError()

    metadata = db.query(PlanMetadata).filter(PlanMetadata.semester_id == semester_id).first()
    if metadata is None:
        raise PlanNotGeneratedError()

    plan_days = (
        db.query(PlanDay)
        .options(joinedload(PlanDay.blocks))
        .filter(PlanDay.semester_id == semester_id)
        .order_by(PlanDay.date)
        .all()
    )

    return metadata, plan_days
