from dataclasses import dataclass
from datetime import date, time

@dataclass(frozen=True)
class ResolvedEvent:
    id: int
    start_date: date
    end_date: date
    cancels_lectures: bool
    counts_towards_attendance: bool
    is_working_day: bool
    exclude_from_recommendation: bool

@dataclass
class TimetableSlotRef:
    slot_id: int
    subject_id: int
    weekday: int
    start_time: time
    end_time: time
    order_index: int

@dataclass
class CalendarDay:
    date: date
    weekday: int
    is_lecture_day: bool
    slots: list[TimetableSlotRef]
    covering_event_ids: list[int]
    counts_towards_attendance: bool | None
    is_working_day: bool | None

@dataclass
class RequirementResult:
    subject_id: int
    required_percentage: float
    total_future_lectures: int
    need_attend: int
    is_feasible: bool
    best_achievable_percentage: float

@dataclass
class SlotMark:
    slot: TimetableSlotRef
    mark: str
    forced: bool = False

@dataclass
class DaySelection:
    date: date
    is_lecture_day: bool
    slot_marks: list[SlotMark]

@dataclass
class PlanBlockResult:
    start_time: time
    end_time: time
    subject_ids: list[int]
    recommendation: str
    block_explanation: str | None = None

@dataclass
class PlanDayResult:
    date: date
    is_lecture_day: bool
    blocks: list[PlanBlockResult]
    day_explanation: str | None = None
