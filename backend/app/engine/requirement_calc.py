import math
from app.models.subject import Subject
from app.engine.types import CalendarDay, RequirementResult

DEFAULT_SUBJECT_PCT = 75.0

def compute_requirements(subjects: list[Subject], days: list[CalendarDay], default_pct: float = DEFAULT_SUBJECT_PCT) -> list[RequirementResult]:
    results = []
    for s in subjects:
        required_pct = s.min_percentage_override if s.min_percentage_override is not None else default_pct
        future_count = sum(
            1 for d in days if d.is_lecture_day
            for slot in d.slots if slot.subject_id == s.id
        )
        need = _smallest_attend_count(
            present=s.present_count, held=s.held_count,
            future_total=future_count, required_pct=required_pct,
        )
        feasible = need <= future_count
        best_pct = _pct(s.present_count + future_count, s.held_count + future_count) if not feasible \
                   else required_pct
        results.append(RequirementResult(
            subject_id=s.id, required_percentage=required_pct,
            total_future_lectures=future_count, need_attend=max(need, 0),
            is_feasible=feasible, best_achievable_percentage=best_pct,
        ))
    return results

def _smallest_attend_count(present: int, held: int, future_total: int, required_pct: float) -> int:
    threshold = (required_pct / 100.0) * (held + future_total) - present
    return max(0, math.ceil(threshold))

def _pct(present: int, held: int) -> float:
    if held == 0:
        return 0.0
    return round((present / held) * 100, 2)
