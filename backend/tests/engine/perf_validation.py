import time
import tracemalloc
from datetime import date, time as dtime
from app.models.semester import SemesterProfile
from app.models.subject import Subject
from app.engine.types import TimetableSlotRef
from app.engine.pipeline import generate_plan

def _get_perf_data(num_slots):
    # 16 weeks semester
    semester = SemesterProfile(
        id=1, name="Sem Perf", start_date=date(2026, 1, 1), end_date=date(2026, 4, 22),
        min_overall_percentage=75.0, min_subject_percentage=75.0
    )
    
    subjects = [
        Subject(id=1, semester_id=1, name="S1", held_count=10, present_count=5, min_percentage_override=None),
        Subject(id=2, semester_id=1, name="S2", held_count=10, present_count=9, min_percentage_override=None),
    ]
    
    timetable = []
    # Distribute slots across 5 weekdays
    for i in range(num_slots):
        weekday = i % 5
        # hour between 8 and 18
        hour = 8 + (i % 10)
        subj = (i % 2) + 1
        timetable.append(TimetableSlotRef(
            slot_id=i, subject_id=subj, weekday=weekday, 
            start_time=dtime(hour, 0), end_time=dtime(hour+1, 0), order_index=i
        ))
        
    return semester, subjects, timetable

def measure_performance(num_slots):
    semester, subjects, timetable = _get_perf_data(num_slots)
    
    tracemalloc.start()
    start_time = time.perf_counter()
    
    result = generate_plan(semester, subjects, timetable, [], {})
    
    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    elapsed_ms = (end_time - start_time) * 1000
    peak_kb = peak / 1024
    
    print(f"[{num_slots} slots] Time: {elapsed_ms:.2f} ms | Peak Memory: {peak_kb:.2f} KB | Plan Days: {len(result.plan_days)}")

if __name__ == "__main__":
    for count in [50, 100, 500, 1000]:
        measure_performance(count)
