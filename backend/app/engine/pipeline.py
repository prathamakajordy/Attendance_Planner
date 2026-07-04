from dataclasses import dataclass
from app.models.semester import SemesterProfile
from app.models.subject import Subject
from app.models.semester_event import SemesterEvent
from app.models.event_type_definition import EventTypeDefinition
from app.engine.types import TimetableSlotRef, PlanDayResult, RequirementResult
from app.engine.event_resolution import resolve_events
from app.engine.calendar_expansion import expand
from app.engine.requirement_calc import compute_requirements
from app.engine.slot_selector import select
from app.engine.block_consolidation import consolidate
from app.engine.explanation_generator import annotate_explanations

@dataclass
class FeasibilityIssue:
    subject_id: int
    subject_name: str
    required_percentage: float
    best_achievable_percentage: float
    is_feasible: bool

@dataclass
class PlanGenerationResult:
    plan_days: list[PlanDayResult]
    feasibility: list[FeasibilityIssue]
    overall_feasible: bool

def generate_plan(
    semester: SemesterProfile,
    subjects: list[Subject],
    timetable: list[TimetableSlotRef],
    events: list[SemesterEvent],
    event_types: dict[int, EventTypeDefinition]
) -> PlanGenerationResult:
    
    # 1. Resolve Events
    resolved_events = resolve_events(events, event_types)
    
    # 2. Expand Calendar
    calendar_days = expand(semester, timetable, resolved_events)
    
    # 3. Compute Requirements
    requirements = compute_requirements(subjects, calendar_days)
    req_dict = {r.subject_id: r for r in requirements}
    
    # 4. Greedy Slot Selection
    day_selections = select(calendar_days, req_dict)
    
    # 5. Block Consolidation
    plan_days = consolidate(day_selections)
    
    # 6. Annotate Explanations
    subject_names = {s.id: s.name for s in subjects}
    event_names = {e.id: e.name for e in events}
    plan_days = annotate_explanations(plan_days, req_dict, calendar_days, subject_names, event_names)
    
    # 7. Build Feasibility Report
    feasibility = []
    overall_feasible = True
    for req in requirements:
        if not req.is_feasible:
            overall_feasible = False
        feasibility.append(FeasibilityIssue(
            subject_id=req.subject_id,
            subject_name=subject_names.get(req.subject_id, "Unknown"),
            required_percentage=req.required_percentage,
            best_achievable_percentage=req.best_achievable_percentage,
            is_feasible=req.is_feasible
        ))
        
    return PlanGenerationResult(plan_days=plan_days, feasibility=feasibility, overall_feasible=overall_feasible)
