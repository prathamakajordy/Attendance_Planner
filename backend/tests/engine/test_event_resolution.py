import pytest
from datetime import date
from app.models.semester_event import SemesterEvent
from app.models.event_type_definition import EventTypeDefinition
from app.engine.event_resolution import resolve_events, _coalesce

def test_coalesce():
    assert _coalesce(None, True) is True
    assert _coalesce(None, False) is False
    assert _coalesce(True, False) is True
    assert _coalesce(False, True) is False

def test_resolve_events():
    type_defs = {
        1: EventTypeDefinition(
            id=1,
            key="test_type",
            label="Test Type",
            is_system_preset=True,
            default_cancels_lectures=True,
            default_counts_towards_attendance=False,
            default_is_working_day=False,
            default_exclude_from_recommendation=True
        )
    }

    events = [
        SemesterEvent(
            id=101,
            semester_id=1,
            name="Event 1",
            event_type_id=1,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 2),
            cancels_lectures_override=None,
            counts_towards_attendance_override=None,
            is_working_day_override=None,
            exclude_from_recommendation_override=None
        ),
        SemesterEvent(
            id=102,
            semester_id=1,
            name="Event 2",
            event_type_id=1,
            start_date=date(2026, 1, 3),
            end_date=date(2026, 1, 4),
            cancels_lectures_override=False,
            counts_towards_attendance_override=True,
            is_working_day_override=True,
            exclude_from_recommendation_override=False
        )
    ]

    resolved = resolve_events(events, type_defs)
    assert len(resolved) == 2

    # Event 1 should use defaults
    e1 = resolved[0]
    assert e1.id == 101
    assert e1.cancels_lectures is True
    assert e1.counts_towards_attendance is False
    assert e1.is_working_day is False
    assert e1.exclude_from_recommendation is True

    # Event 2 should use overrides
    e2 = resolved[1]
    assert e2.id == 102
    assert e2.cancels_lectures is False
    assert e2.counts_towards_attendance is True
    assert e2.is_working_day is True
    assert e2.exclude_from_recommendation is False
