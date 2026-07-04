from pydantic import BaseModel, Field, model_validator
from datetime import date, datetime
from typing import Optional

class SemesterEventBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    event_type_id: int
    custom_type_label: Optional[str] = None
    start_date: date
    end_date: date
    description: Optional[str] = None
    cancels_lectures_override: Optional[bool] = None
    counts_towards_attendance_override: Optional[bool] = None
    is_working_day_override: Optional[bool] = None
    exclude_from_recommendation_override: Optional[bool] = None

    @model_validator(mode="after")
    def check_dates(self) -> "SemesterEventBase":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self

class SemesterEventCreate(SemesterEventBase):
    pass

class SemesterEventUpdate(SemesterEventBase):
    pass

class SemesterEventRead(SemesterEventBase):
    id: int
    semester_id: int
    created_at: datetime
    updated_at: datetime

    # The computed fields are handled by backend properties or resolved dynamically
    resolved_cancels_lectures: bool
    resolved_counts_towards_attendance: bool
    resolved_is_working_day: bool
    resolved_exclude_from_recommendation: bool

    class Config:
        from_attributes = True
