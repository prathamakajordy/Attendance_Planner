from dataclasses import replace
from app.engine.types import DaySelection, PlanDayResult, PlanBlockResult, SlotMark

def consolidate(day_selections: list[DaySelection]) -> list[PlanDayResult]:
    results = []
    for ds in day_selections:
        marks = list(ds.slot_marks)
        changed = True
        while changed:
            changed = False
            for i in range(1, len(marks) - 1):
                # If a Skip is sandwiched between two Attends, upgrade it to Attend
                if marks[i].mark == "Skip" and marks[i - 1].mark == "Attend" and marks[i + 1].mark == "Attend":
                    marks[i] = replace(marks[i], mark="Attend", forced=True)
                    changed = True
        
        blocks = _merge_contiguous(marks)
        results.append(PlanDayResult(date=ds.date, is_lecture_day=ds.is_lecture_day, blocks=blocks))
    return results

def _merge_contiguous(marks: list[SlotMark]) -> list[PlanBlockResult]:
    if not marks:
        return []

    blocks = []
    current_block_slots = [marks[0]]
    
    for mark in marks[1:]:
        last_mark = current_block_slots[-1]
        
        # Determine if we should merge.
        # We merge if they have the exact same mark and forced status.
        # "OptionalIncluded" vs "Attend" means they don't merge if one is forced and the other isn't?
        # Actually, TRD Section 15.8 says "Optional-but-included... shown as a distinct sub-status".
        # We can map `mark="Attend", forced=True` to "Optional" recommendation.
        # Let's define recommendation string:
        
        def _get_rec(m: SlotMark) -> str:
            if m.mark == "Attend":
                return "Optional" if m.forced else "Attend"
            return m.mark
            
        current_rec = _get_rec(last_mark)
        next_rec = _get_rec(mark)
        
        # Also, to merge, they must be contiguous in time?
        # Yes, normally slots are contiguous. But if there's a gap, should we merge?
        # The TRD block rule says "groups consecutive same-mark slots".
        # If there's a time gap between slots, should they merge?
        # A gap means the student is waiting. But Block Consolidation specifically forces skips to attends to eliminate gaps.
        # If there's a physical gap in the timetable (e.g. lunch break), it is still contiguous in the `marks` array.
        # Let's just merge them if they have the same recommendation.
        if current_rec == next_rec:
            current_block_slots.append(mark)
        else:
            blocks.append(_create_block(current_block_slots, current_rec))
            current_block_slots = [mark]

    if current_block_slots:
        blocks.append(_create_block(current_block_slots, _get_rec(current_block_slots[-1])))
        
    return blocks

def _create_block(slots: list[SlotMark], rec: str) -> PlanBlockResult:
    return PlanBlockResult(
        start_time=slots[0].slot.start_time,
        end_time=slots[-1].slot.end_time,
        subject_ids=[m.slot.subject_id for m in slots],
        recommendation=rec
    )
