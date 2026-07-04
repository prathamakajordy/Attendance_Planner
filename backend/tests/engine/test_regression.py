import pytest
from datetime import date, time
from app.models.semester import SemesterProfile
from app.models.subject import Subject
from app.models.semester_event import SemesterEvent
from app.models.event_type_definition import EventTypeDefinition
from app.engine.types import TimetableSlotRef
from app.engine.pipeline import generate_plan

# Helper to generate basic test data
from datetime import timedelta
def _get_base_data(weeks=4):
    semester = SemesterProfile(
        id=1, name="Sem Test", start_date=date(2026, 1, 1), end_date=date(2026, 1, 1) + timedelta(days=weeks * 7 - 1),
        min_overall_percentage=75.0, min_subject_percentage=75.0
    )
    # 2026-01-01 is Thursday
    
    subjects = [
        Subject(id=10, semester_id=1, name="Subj1", held_count=4, present_count=4, min_percentage_override=None), 
        Subject(id=11, semester_id=1, name="Subj2", held_count=4, present_count=4, min_percentage_override=None), 
        Subject(id=12, semester_id=1, name="Subj3", held_count=4, present_count=4, min_percentage_override=None), 
    ]
    
    timetable = [
        TimetableSlotRef(slot_id=1, subject_id=10, weekday=3, start_time=time(9,0), end_time=time(10,0), order_index=0),
        TimetableSlotRef(slot_id=2, subject_id=11, weekday=3, start_time=time(10,0), end_time=time(11,0), order_index=1),
        TimetableSlotRef(slot_id=3, subject_id=12, weekday=3, start_time=time(11,0), end_time=time(12,0), order_index=2),
    ]
    
    return semester, subjects, timetable

def _get_events(events_list, type_def_dict=None):
    if type_def_dict is None:
        type_def_dict = {
            1: EventTypeDefinition(id=1, key="holiday", label="Holiday", default_cancels_lectures=True, default_exclude_from_recommendation=True, default_counts_towards_attendance=False, default_is_working_day=False),
            2: EventTypeDefinition(id=2, key="midsem", label="Mid Sem", default_cancels_lectures=True, default_exclude_from_recommendation=True, default_counts_towards_attendance=False, default_is_working_day=True)
        }
    return events_list, type_def_dict

# 1. Student already above all attendance thresholds
def test_above_all_thresholds():
    semester, subjects, timetable = _get_base_data()
    for s in subjects: s.present_count = 10
    result = generate_plan(semester, subjects, timetable, [], {})
    for day in result.plan_days:
        if day.is_lecture_day:
            for block in day.blocks:
                assert block.recommendation == "Skip"

# 2. One subject below threshold
def test_one_subject_below_threshold():
    semester, subjects, timetable = _get_base_data()
    subjects[0].present_count = 2 # Subj1 is below threshold (50%)
    result = generate_plan(semester, subjects, timetable, [], {})
    day = next(d for d in result.plan_days if d.is_lecture_day)
    assert len(day.blocks) == 2
    assert day.blocks[0].subject_ids == [10]
    assert day.blocks[0].recommendation == "Attend"
    assert day.blocks[1].subject_ids == [11, 12]
    assert day.blocks[1].recommendation == "Skip"

# 3. Multiple subjects below threshold
def test_multiple_subjects_below_threshold():
    semester, subjects, timetable = _get_base_data()
    subjects[0].present_count = 2 
    subjects[2].present_count = 2 
    result = generate_plan(semester, subjects, timetable, [], {})
    day = next(d for d in result.plan_days if d.is_lecture_day)
    assert len(day.blocks) == 3
    assert day.blocks[0].recommendation == "Attend"
    assert day.blocks[1].recommendation == "Optional" # Sandwiched
    assert day.blocks[2].recommendation == "Attend"

# 4. Practical batch filtering (Handled at API level, but simulate by missing slot)
def test_practical_batch_filtering():
    semester, subjects, timetable = _get_base_data()
    # Simulate API dropping slot 2 (Subj2) due to batch mismatch
    timetable = [t for t in timetable if t.subject_id != 11]
    
    # Subj1 and Subj3 are at 4/4 (Safe).
    # Since they are safe, they should both be marked Skip.
    result = generate_plan(semester, subjects, timetable, [], {})
    day = next(d for d in result.plan_days if d.is_lecture_day)
    assert len(day.blocks) == 1
    assert day.blocks[0].subject_ids == [10, 12]
    assert day.blocks[0].recommendation == "Skip"

# 5. Honors / Optional subject filtering
def test_honors_filtering():
    semester, subjects, timetable = _get_base_data()
    # Add an honors subject slot, but drop it as if student not enrolled
    timetable.append(TimetableSlotRef(slot_id=4, subject_id=13, weekday=3, start_time=time(12,0), end_time=time(13,0), order_index=3))
    # API drops it
    timetable = [t for t in timetable if t.subject_id != 13]
    result = generate_plan(semester, subjects, timetable, [], {})
    for day in result.plan_days:
        if day.is_lecture_day:
            assert 13 not in day.blocks[0].subject_ids

# 6. Holiday removing lectures
def test_holiday_removing_lectures():
    semester, subjects, timetable = _get_base_data()
    events, type_defs = _get_events([
        SemesterEvent(id=1, event_type_id=1, name="Holiday", start_date=date(2026, 1, 8), end_date=date(2026, 1, 8), cancels_lectures_override=None, counts_towards_attendance_override=None, is_working_day_override=None, exclude_from_recommendation_override=None)
    ])
    result = generate_plan(semester, subjects, timetable, events, type_defs)
    holiday_day = next(d for d in result.plan_days if d.date == date(2026, 1, 8))
    assert not holiday_day.is_lecture_day
    assert len(holiday_day.blocks) == 0

# 7. Mid-sem exam blocking lectures
def test_midsem_exam_blocking_lectures():
    semester, subjects, timetable = _get_base_data()
    events, type_defs = _get_events([
        SemesterEvent(id=1, event_type_id=2, name="Mid Sem", start_date=date(2026, 1, 8), end_date=date(2026, 1, 15), cancels_lectures_override=None, counts_towards_attendance_override=None, is_working_day_override=None, exclude_from_recommendation_override=None)
    ])
    result = generate_plan(semester, subjects, timetable, events, type_defs)
    midsem_day1 = next(d for d in result.plan_days if d.date == date(2026, 1, 8))
    midsem_day2 = next(d for d in result.plan_days if d.date == date(2026, 1, 15))
    assert not midsem_day1.is_lecture_day
    assert not midsem_day2.is_lecture_day

# 8. Impossible attendance
def test_impossible_attendance():
    semester, subjects, timetable = _get_base_data()
    subjects[0].held_count = 10
    subjects[0].present_count = 0
    result = generate_plan(semester, subjects, timetable, [], {})
    assert not result.overall_feasible
    feasibility = {f.subject_id: f for f in result.feasibility}
    assert not feasibility[10].is_feasible

# 9. Continuous block generation
def test_continuous_block_generation():
    semester, subjects, timetable = _get_base_data()
    subjects[0].present_count = 2
    subjects[1].present_count = 2
    subjects[2].present_count = 2
    result = generate_plan(semester, subjects, timetable, [], {})
    day = next(d for d in result.plan_days if d.is_lecture_day)
    # All are Attend, should merge into 1 block
    assert len(day.blocks) == 1
    assert day.blocks[0].subject_ids == [10, 11, 12]
    assert day.blocks[0].recommendation == "Attend"

# 10. Sandwich block generation
def test_sandwich_block_generation():
    semester, subjects, timetable = _get_base_data()
    subjects[0].present_count = 2 # Attend
    subjects[1].present_count = 4 # Skip
    subjects[2].present_count = 2 # Attend
    result = generate_plan(semester, subjects, timetable, [], {})
    day = next(d for d in result.plan_days if d.is_lecture_day)
    assert len(day.blocks) == 3
    assert day.blocks[1].recommendation == "Optional"

# 11. Entire day skipped
def test_entire_day_skipped():
    semester, subjects, timetable = _get_base_data()
    result = generate_plan(semester, subjects, timetable, [], {})
    day = next(d for d in result.plan_days if d.is_lecture_day)
    assert len(day.blocks) == 1
    assert day.blocks[0].recommendation == "Skip"

# 12. Entire day attended
def test_entire_day_attended():
    semester, subjects, timetable = _get_base_data()
    for s in subjects: s.present_count = 0
    result = generate_plan(semester, subjects, timetable, [], {})
    day = next(d for d in result.plan_days if d.is_lecture_day)
    assert len(day.blocks) == 1
    assert day.blocks[0].recommendation == "Attend"

# 13. Mixed attendance percentages
def test_mixed_attendance_percentages():
    semester, subjects, timetable = _get_base_data()
    subjects[0].present_count = 1 # Very low
    subjects[1].present_count = 3 # Below
    subjects[2].present_count = 10 # Safe
    
    # For subject 1: present=1, held=4, future=4. Total=8. Need 75% of 8 = 6. Need 5 more.
    # Future=4. Since 4 <= 5, week 1 must attend.
    # For subject 2: present=3. Total=8. Need 6. Need 3 more. Future=4. 
    # Week 1: 4 <= 3 is False. So it skips.
    # So Subj1=Attend, Subj2=Skip, Subj3=Skip.
    # Wait, my test asserted that Subj 1 & 2 Attend -> merge.
    # If I want Subj2 to Attend, I need present_count to be 2.
    subjects[1].present_count = 2 # Below, need 4 more. 4 <= 4 is True. Attend.
    
    result = generate_plan(semester, subjects, timetable, [], {})
    day = next(d for d in result.plan_days if d.is_lecture_day)
    # Subj 1 & 2 Attend -> merge. Subj 3 Skip.
    assert len(day.blocks) == 2
    assert day.blocks[0].subject_ids == [10, 11]
    assert day.blocks[0].recommendation == "Attend"
    assert day.blocks[1].subject_ids == [12]
    assert day.blocks[1].recommendation == "Skip"

# 14. Semester almost finished
def test_semester_almost_finished():
    semester, subjects, timetable = _get_base_data(weeks=1)
    # 1 week left, 1 lecture left
    subjects[0].present_count = 3 # 75% of 4. Need 75% of 5 = 4. Needs to attend the 1 lecture.
    result = generate_plan(semester, subjects, timetable, [], {})
    day = next(d for d in result.plan_days if d.is_lecture_day)
    assert day.blocks[0].subject_ids == [10]
    assert day.blocks[0].recommendation == "Attend"

# 15. Semester just started
def test_semester_just_started():
    semester, subjects, timetable = _get_base_data(weeks=16)
    # 0 held, 0 present. Target 75% of 16 = 12. Needs to attend 12/16.
    for s in subjects:
        s.held_count = 0
        s.present_count = 0
    result = generate_plan(semester, subjects, timetable, [], {})
    # First 4 weeks (4 occurrences) can be skipped (16 - 12 = 4 skips available)
    # The slot_selector checks remaining <= need. 16 <= 12 is False -> Skip.
    # So week 1 should be Skip.
    day1 = next(d for d in result.plan_days if d.is_lecture_day)
    assert day1.blocks[0].recommendation == "Skip"

# 16. Only one lecture remaining
def test_only_one_lecture_remaining():
    semester, subjects, timetable = _get_base_data(weeks=1)
    subjects[0].held_count = 20
    subjects[0].present_count = 15 # 75% of 20. Target 75% of 21 = 15.75 -> 16.
    result = generate_plan(semester, subjects, timetable, [], {})
    day = next(d for d in result.plan_days if d.is_lecture_day)
    assert day.blocks[0].subject_ids == [10]
    assert day.blocks[0].recommendation == "Attend"

# 17. Multiple labs on the same day
def test_multiple_labs():
    semester, subjects, timetable = _get_base_data()
    # Add two consecutive slots of the SAME subject (e.g. Lab)
    timetable.append(TimetableSlotRef(slot_id=4, subject_id=10, weekday=3, start_time=time(13,0), end_time=time(14,0), order_index=3))
    timetable.append(TimetableSlotRef(slot_id=5, subject_id=10, weekday=3, start_time=time(14,0), end_time=time(15,0), order_index=4))
    subjects[0].present_count = 0 # Force Attend
    result = generate_plan(semester, subjects, timetable, [], {})
    day = next(d for d in result.plan_days if d.is_lecture_day)
    assert day.blocks[-1].subject_ids == [10, 10]
    assert day.blocks[-1].recommendation == "Attend"

# 18. Consecutive holidays
def test_consecutive_holidays():
    semester, subjects, timetable = _get_base_data()
    events, type_defs = _get_events([
        SemesterEvent(id=1, event_type_id=1, name="H1", start_date=date(2026, 1, 8), end_date=date(2026, 1, 8), cancels_lectures_override=None, counts_towards_attendance_override=None, is_working_day_override=None, exclude_from_recommendation_override=None),
        SemesterEvent(id=2, event_type_id=1, name="H2", start_date=date(2026, 1, 15), end_date=date(2026, 1, 15), cancels_lectures_override=None, counts_towards_attendance_override=None, is_working_day_override=None, exclude_from_recommendation_override=None)
    ])
    result = generate_plan(semester, subjects, timetable, events, type_defs)
    assert not next(d for d in result.plan_days if d.date == date(2026, 1, 8)).is_lecture_day
    assert not next(d for d in result.plan_days if d.date == date(2026, 1, 15)).is_lecture_day

# 19. Large timetable (stress test)
def test_large_timetable():
    # Will be tested heavily in performance script, but just ensure it handles many slots
    semester, subjects, timetable = _get_base_data(weeks=16)
    # Add slots for every weekday
    large_timetable = []
    for w in range(7):
        for i in range(10):
            large_timetable.append(TimetableSlotRef(slot_id=w*10+i, subject_id=10, weekday=w, start_time=time(8+i,0), end_time=time(9+i,0), order_index=i))
    result = generate_plan(semester, subjects, large_timetable, [], {})
    assert len(result.plan_days) == 16 * 7
