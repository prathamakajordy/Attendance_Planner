from pydantic import BaseModel, Field, model_validator
from datetime import time
from app.models.timetable import WeekdayEnum

class TimetableSlotBase(BaseModel):
    subject_id: int
    weekday: WeekdayEnum
    start_time: time
    end_time: time
    order_index: int
    required_groups: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def check_time(self) -> "TimetableSlotBase":
        if self.start_time >= self.end_time:
            raise ValueError("start_time must be strictly less than end_time")
        return self

class TimetableSlotCreate(TimetableSlotBase):
    pass

class TimetableSlotUpdate(TimetableSlotBase):
    pass

class TimetableSlotRead(TimetableSlotBase):
    id: int
    semester_id: int

    class Config:
        from_attributes = True
