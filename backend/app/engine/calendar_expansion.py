from datetime import timedelta
from app.models.semester import SemesterProfile
from app.engine.types import ResolvedEvent, TimetableSlotRef, CalendarDay

def expand(
    semester: SemesterProfile,
    timetable: list[TimetableSlotRef],
    resolved_events: list[ResolvedEvent],
) -> list[CalendarDay]:
    days: list[CalendarDay] = []
    for d in _daterange(semester.start_date, semester.end_date):
        weekday = d.weekday()
        covering = [e for e in resolved_events if e.start_date <= d <= e.end_date]

        # Most-restrictive-wins per flag across all covering events
        exclude = any(e.exclude_from_recommendation for e in covering)
        cancels = any(e.cancels_lectures for e in covering)
        counts = _most_restrictive_or_none([e.counts_towards_attendance for e in covering])
        working = _most_restrictive_or_none([e.is_working_day for e in covering], invert=True)

        base_slots = [s for s in timetable if s.weekday == weekday]
        slots = [] if (exclude or cancels) else base_slots
        is_lecture_day = (not exclude) and len(slots) > 0

        days.append(CalendarDay(
            date=d, weekday=weekday, is_lecture_day=is_lecture_day, slots=slots,
            covering_event_ids=[e.id for e in covering],
            counts_towards_attendance=counts, is_working_day=working,
        ))
    return days

def _daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def _most_restrictive_or_none(values: list[bool], invert: bool = False) -> bool | None:
    if not values:
        return None
    # For counts_towards_attendance, False is most restrictive (invert=False -> if any False, return False)
    # For is_working_day, False is most restrictive (invert=True -> wait, TRD says invert=True. Let's see what that means.
    # Actually, TRD says: "working = _most_restrictive_or_none([e.is_working_day for e in covering], invert=True)
    # "most restrictive" for is_working_day means False (not-a-working-day) wins if any event says so."
    # So if invert is just an ignored argument, or if invert means we invert the logic?
    # If False wins in both, then we just need `if False in values: return False else return True`.
    # Let's just implement it simply: if False is in values, return False. Else return True.
    if False in values:
        return False
    return True
