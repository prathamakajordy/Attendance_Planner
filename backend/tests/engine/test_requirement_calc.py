import pytest
from datetime import date
from app.models.subject import Subject
from app.engine.types import CalendarDay, TimetableSlotRef
from app.engine.requirement_calc import compute_requirements, _smallest_attend_count, _pct

def test_pct():
    assert _pct(0, 0) == 0.0
    assert _pct(75, 100) == 75.0
    assert _pct(1, 3) == 33.33

def test_smallest_attend_count():
    # If 75% is required out of 100 total (50 held, 50 future). Need 75 total present. 
    # Currently 30 present. Need 45 more.
    assert _smallest_attend_count(present=30, held=50, future_total=50, required_pct=75.0) == 45
    
    # If currently 80 present out of 50 held (impossible, but math works). Total 100. Need 75. Need 0 more.
    assert _smallest_attend_count(present=80, held=50, future_total=50, required_pct=75.0) == 0

def test_compute_requirements():
    subjects = [
        Subject(id=1, name="Math", held_count=10, present_count=5, min_percentage_override=None), # 50%
        Subject(id=2, name="Physics", held_count=10, present_count=9, min_percentage_override=80.0), # 90%
    ]

    # Create 2 future lecture days
    days = [
        CalendarDay(
            date=date(2026, 1, 1), weekday=0, is_lecture_day=True,
            slots=[TimetableSlotRef(slot_id=1, subject_id=1, weekday=0, start_time=None, end_time=None, order_index=0)],
            covering_event_ids=[], counts_towards_attendance=None, is_working_day=None
        ),
        CalendarDay(
            date=date(2026, 1, 2), weekday=1, is_lecture_day=True,
            slots=[
                TimetableSlotRef(slot_id=2, subject_id=1, weekday=1, start_time=None, end_time=None, order_index=0),
                TimetableSlotRef(slot_id=3, subject_id=2, weekday=1, start_time=None, end_time=None, order_index=1),
            ],
            covering_event_ids=[], counts_towards_attendance=None, is_working_day=None
        ),
        CalendarDay(
            date=date(2026, 1, 3), weekday=2, is_lecture_day=False, # Not a lecture day, shouldn't count
            slots=[TimetableSlotRef(slot_id=4, subject_id=1, weekday=2, start_time=None, end_time=None, order_index=0)],
            covering_event_ids=[], counts_towards_attendance=None, is_working_day=None
        )
    ]

    results = compute_requirements(subjects, days, default_pct=75.0)
    assert len(results) == 2

    r1 = results[0] # Math
    assert r1.subject_id == 1
    assert r1.required_percentage == 75.0
    assert r1.total_future_lectures == 2
    # Total = 10 + 2 = 12. Need 75% of 12 = 9. Present = 5. Need 4 more.
    assert r1.need_attend == 4
    assert r1.is_feasible is False # Need 4 but only 2 future lectures
    # Best achievable = (5 + 2) / 12 = 7 / 12 = 58.33%
    assert r1.best_achievable_percentage == 58.33

    r2 = results[1] # Physics
    assert r2.subject_id == 2
    assert r2.required_percentage == 80.0
    assert r2.total_future_lectures == 1
    # Total = 10 + 1 = 11. Need 80% of 11 = 8.8 -> 9. Present = 9. Need 0 more.
    assert r2.need_attend == 0
    assert r2.is_feasible is True
    assert r2.best_achievable_percentage == 80.0 # Feasible, so it returns required_pct (as per TRD logic)
