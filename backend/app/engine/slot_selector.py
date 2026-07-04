from app.engine.types import CalendarDay, RequirementResult, DaySelection, SlotMark

def select(days: list[CalendarDay], requirements: dict[int, RequirementResult]) -> list[DaySelection]:
    remaining_need = {r.subject_id: r.need_attend for r in requirements.values()}
    remaining_occurrences = {r.subject_id: r.total_future_lectures for r in requirements.values()}
    selections = []

    for d in days:
        if not d.is_lecture_day:
            selections.append(DaySelection(date=d.date, is_lecture_day=False, slot_marks=[]))
            continue
        marks = []
        for slot in d.slots:
            sid = slot.subject_id
            
            # If remaining occurrences <= remaining need, we must attend this to hit the target.
            # E.g., need 2 more, have 2 occurrences left -> attend both.
            # If need 2 more, have 3 occurrences left -> skip the first, attend the last 2.
            # This is a greedy "delay attendance as much as possible" approach, which concentrates 
            # attendance toward the end of the semester, but block consolidation might shift this.
            must_attend = remaining_occurrences[sid] <= remaining_need[sid] and remaining_need[sid] > 0
            
            # If remaining_need is 0, we can safely skip. If must_attend, we attend.
            mark = "Attend" if must_attend else "Skip"
            marks.append(SlotMark(slot=slot, mark=mark))

            remaining_occurrences[sid] -= 1
            if must_attend:
                remaining_need[sid] -= 1
        selections.append(DaySelection(date=d.date, is_lecture_day=True, slot_marks=marks))
    return selections
