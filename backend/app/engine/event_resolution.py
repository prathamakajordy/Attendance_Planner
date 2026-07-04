from app.models.semester_event import SemesterEvent
from app.models.event_type_definition import EventTypeDefinition
from app.engine.types import ResolvedEvent

def resolve_events(
    events: list[SemesterEvent], type_defs: dict[int, EventTypeDefinition]
) -> list[ResolvedEvent]:
    resolved = []
    for e in events:
        t = type_defs[e.event_type_id]
        resolved.append(ResolvedEvent(
            id=e.id,
            start_date=e.start_date,
            end_date=e.end_date,
            cancels_lectures=_coalesce(e.cancels_lectures_override, t.default_cancels_lectures),
            counts_towards_attendance=_coalesce(e.counts_towards_attendance_override, t.default_counts_towards_attendance),
            is_working_day=_coalesce(e.is_working_day_override, t.default_is_working_day),
            exclude_from_recommendation=_coalesce(e.exclude_from_recommendation_override, t.default_exclude_from_recommendation),
        ))
    return resolved

def _coalesce(override: bool | None, default: bool) -> bool:
    return default if override is None else override
