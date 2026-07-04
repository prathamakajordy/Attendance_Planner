import pytest
from datetime import date, time
from app.models.semester import SemesterProfile
from app.models.subject import Subject
from app.models.semester_event import SemesterEvent
from app.models.event_type_definition import EventTypeDefinition
from app.engine.types import TimetableSlotRef
from app.engine.pipeline import generate_plan

def _get_base_data():
    semester = SemesterProfile(
        id=1, name="Sem IV", start_date=date(2026, 1, 1), end_date=date(2026, 1, 28), # 4 weeks
        min_overall_percentage=75.0, min_subject_percentage=75.0
    )
    # 2026-01-01 is Thursday
    
    subjects = [
        Subject(id=10, semester_id=1, name="DBMS", held_count=4, present_count=2, min_percentage_override=None), # 50% - Low
        Subject(id=11, semester_id=1, name="OS", held_count=4, present_count=4, min_percentage_override=None), # 100% - Safe
        Subject(id=12, semester_id=1, name="CN", held_count=4, present_count=2, min_percentage_override=None), # 50% - Low
    ]
    
    timetable = [
        # Thursday (weekday=3)
        TimetableSlotRef(slot_id=1, subject_id=10, weekday=3, start_time=time(9,0), end_time=time(10,0), order_index=0),
        TimetableSlotRef(slot_id=2, subject_id=11, weekday=3, start_time=time(10,0), end_time=time(11,0), order_index=1),
        TimetableSlotRef(slot_id=3, subject_id=12, weekday=3, start_time=time(11,0), end_time=time(12,0), order_index=2),
    ]
    
    return semester, subjects, timetable

def test_case_1_low_dbms_only():
    semester, subjects, timetable = _get_base_data()
    # Modify CN to be safe
    subjects[2].present_count = 4
    
    # Thursday timetable: DBMS (Low) -> OS (Safe) -> CN (Safe)
    result = generate_plan(semester, subjects, timetable, [], {})
    
    assert result.overall_feasible is True
    
    # Thursday is the only lecture day in the range (actually Thursday Jan 1st is)
    days = [d for d in result.plan_days if d.date == date(2026, 1, 1)]
    assert len(days) == 1
    blocks = days[0].blocks
    
    # Since OS and CN are safe, they should be marked Skip.
    # DBMS is low, so it should be Attend.
    # Block Consolidation shouldn't merge them because Attend -> Skip -> Skip. No sandwiched Skip.
    assert len(blocks) == 2
    assert blocks[0].subject_ids == [10]
    assert blocks[0].recommendation == "Attend"
    assert "below the required" in blocks[0].block_explanation
    
    assert blocks[1].subject_ids == [11, 12]
    assert blocks[1].recommendation == "Skip"
    assert "safely above threshold" in blocks[1].block_explanation

def test_case_2_sandwich_block_consolidation():
    semester, subjects, timetable = _get_base_data()
    
    # Thursday timetable: DBMS (Low) -> OS (Safe) -> CN (Low)
    result = generate_plan(semester, subjects, timetable, [], {})
    
    days = [d for d in result.plan_days if d.date == date(2026, 1, 1)]
    assert len(days) == 1
    blocks = days[0].blocks
    
    # OS is Skip but sandwiched between DBMS (Attend) and CN (Attend)
    # The consolidator marks OS as Attend (forced). Because it is "Optional" recommendation,
    # it stays as a separate block but is contiguous with the other two Attend blocks.
    assert len(blocks) == 3
    assert blocks[0].subject_ids == [10]
    assert blocks[0].recommendation == "Attend"
    
    assert blocks[1].subject_ids == [11]
    assert blocks[1].recommendation == "Optional"
    assert "included because it lies between required lectures" in blocks[1].block_explanation
    
    assert blocks[2].subject_ids == [12]
    assert blocks[2].recommendation == "Attend"

def test_case_3_all_safe():
    semester, subjects, timetable = _get_base_data()
    for s in subjects:
        s.present_count = 4 # 100% attendance
        
    result = generate_plan(semester, subjects, timetable, [], {})
    
    days = [d for d in result.plan_days if d.date == date(2026, 1, 1)]
    assert len(days) == 1
    blocks = days[0].blocks
    
    assert len(blocks) == 1
    assert blocks[0].subject_ids == [10, 11, 12]
    assert blocks[0].recommendation == "Skip"

def test_case_4_impossible_attendance():
    semester, subjects, timetable = _get_base_data()
    # DBMS has 0/4 attendance, 4 lectures left. Total = 8. Need 75% of 8 = 6. Impossible.
    subjects[0].held_count = 4
    subjects[0].present_count = 0
    
    result = generate_plan(semester, subjects, timetable, [], {})
    
    assert result.overall_feasible is False
    
    feasibility = {f.subject_id: f for f in result.feasibility}
    assert feasibility[10].is_feasible is False
    # best achievable: (0+4) / (4+4) = 4/8 = 50.0%
    assert feasibility[10].best_achievable_percentage == 50.0
    
    # Even though impossible, it should recommend Attending the remaining lectures
    days = [d for d in result.plan_days if d.date == date(2026, 1, 1)]
    assert len(days) == 1
    # DBMS (Attend) -> OS (Safe) -> CN (Low)
    assert days[0].blocks[0].recommendation == "Attend"
    assert days[0].blocks[0].subject_ids == [10]

def test_case_5_event_excluded():
    semester, subjects, timetable = _get_base_data()
    
    type_defs = {
        1: EventTypeDefinition(id=1, key="holiday", label="Holiday", default_exclude_from_recommendation=True)
    }
    events = [
        SemesterEvent(id=1, event_type_id=1, name="New Year", start_date=date(2026,1,1), end_date=date(2026,1,1))
    ]
    
    result = generate_plan(semester, subjects, timetable, events, type_defs)
    
    days = [d for d in result.plan_days if d.date == date(2026, 1, 1)]
    assert len(days) == 1
    assert len(days[0].blocks) == 0
    assert "No lectures are planned on this date due to: New Year" in days[0].day_explanation
