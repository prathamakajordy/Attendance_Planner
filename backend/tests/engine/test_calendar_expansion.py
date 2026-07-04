import pytest
from datetime import date
from app.models.semester import SemesterProfile
from app.engine.types import ResolvedEvent, TimetableSlotRef, CalendarDay
from app.engine.calendar_expansion import expand, _daterange, _most_restrictive_or_none

def test_daterange():
    d_start = date(2026, 1, 1)
    d_end = date(2026, 1, 3)
    dates = list(_daterange(d_start, d_end))
    assert len(dates) == 3
    assert dates[0] == date(2026, 1, 1)
    assert dates[2] == date(2026, 1, 3)

def test_most_restrictive_or_none():
    assert _most_restrictive_or_none([]) is None
    assert _most_restrictive_or_none([True, True]) is True
    assert _most_restrictive_or_none([True, False]) is False
    assert _most_restrictive_or_none([False, False]) is False

def test_expand_no_events():
    semester = SemesterProfile(
        id=1,
        name="Test",
        start_date=date(2026, 1, 1), # Thursday
        end_date=date(2026, 1, 7)    # Wednesday
    )
    
    # 2026-01-01 is Thursday (weekday 3)
    # 2026-01-02 is Friday (weekday 4)
    # 2026-01-05 is Monday (weekday 0)
    
    timetable = [
        TimetableSlotRef(slot_id=1, subject_id=10, weekday=3, start_time=None, end_time=None, order_index=0),
        TimetableSlotRef(slot_id=2, subject_id=11, weekday=3, start_time=None, end_time=None, order_index=1),
        TimetableSlotRef(slot_id=3, subject_id=10, weekday=0, start_time=None, end_time=None, order_index=0),
    ]

    days = expand(semester, timetable, [])
    assert len(days) == 7

    # Check Thursday
    day_1 = days[0]
    assert day_1.date == date(2026, 1, 1)
    assert day_1.weekday == 3
    assert day_1.is_lecture_day is True
    assert len(day_1.slots) == 2
    assert day_1.covering_event_ids == []
    assert day_1.counts_towards_attendance is None
    assert day_1.is_working_day is None

    # Check Friday
    day_2 = days[1]
    assert day_2.date == date(2026, 1, 2)
    assert day_2.weekday == 4
    assert day_2.is_lecture_day is False
    assert len(day_2.slots) == 0

def test_expand_with_events():
    semester = SemesterProfile(
        id=1,
        name="Test",
        start_date=date(2026, 1, 1), # Thursday
        end_date=date(2026, 1, 3)    # Saturday
    )
    
    timetable = [
        TimetableSlotRef(slot_id=1, subject_id=10, weekday=3, start_time=None, end_time=None, order_index=0),
        TimetableSlotRef(slot_id=2, subject_id=10, weekday=4, start_time=None, end_time=None, order_index=0),
    ]

    events = [
        # Event cancels lectures on Thursday
        ResolvedEvent(
            id=101, start_date=date(2026, 1, 1), end_date=date(2026, 1, 1),
            cancels_lectures=True, counts_towards_attendance=False, is_working_day=False, exclude_from_recommendation=False
        ),
        # Event excludes Friday from recommendation
        ResolvedEvent(
            id=102, start_date=date(2026, 1, 2), end_date=date(2026, 1, 2),
            cancels_lectures=False, counts_towards_attendance=True, is_working_day=True, exclude_from_recommendation=True
        )
    ]

    days = expand(semester, timetable, events)
    assert len(days) == 3

    # Thursday: lectures cancelled
    assert days[0].date == date(2026, 1, 1)
    assert days[0].is_lecture_day is False
    assert len(days[0].slots) == 0
    assert days[0].covering_event_ids == [101]
    assert days[0].counts_towards_attendance is False
    assert days[0].is_working_day is False

    # Friday: excluded from recommendation
    assert days[1].date == date(2026, 1, 2)
    assert days[1].is_lecture_day is False
    assert len(days[1].slots) == 0
    assert days[1].covering_event_ids == [102]
    assert days[1].counts_towards_attendance is True
    assert days[1].is_working_day is True

def test_expand_multiple_overlapping_events():
    semester = SemesterProfile(
        id=1, name="Test", start_date=date(2026, 1, 1), end_date=date(2026, 1, 1)
    )
    timetable = [
        TimetableSlotRef(slot_id=1, subject_id=10, weekday=3, start_time=None, end_time=None, order_index=0)
    ]
    events = [
        # Event 1 says: working day, counts
        ResolvedEvent(
            id=1, start_date=date(2026, 1, 1), end_date=date(2026, 1, 1),
            cancels_lectures=False, counts_towards_attendance=True, is_working_day=True, exclude_from_recommendation=False
        ),
        # Event 2 says: NOT working day, does NOT count
        ResolvedEvent(
            id=2, start_date=date(2026, 1, 1), end_date=date(2026, 1, 1),
            cancels_lectures=False, counts_towards_attendance=False, is_working_day=False, exclude_from_recommendation=False
        )
    ]

    days = expand(semester, timetable, events)
    day = days[0]
    
    # Most restrictive wins: False for working, False for counts
    assert day.is_working_day is False
    assert day.counts_towards_attendance is False
    assert set(day.covering_event_ids) == {1, 2}
    assert day.is_lecture_day is True
    assert len(day.slots) == 1
