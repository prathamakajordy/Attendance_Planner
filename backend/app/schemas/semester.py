from pydantic import BaseModel, Field, model_validator
from datetime import date, datetime
from typing import List, Optional

class SemesterBase(BaseModel):
    name: str = Field(min_length=1)
    start_date: date
    end_date: date
    min_overall_percentage: float = Field(gt=0, le=100)
    min_subject_percentage: float = Field(gt=0, le=100)

    @model_validator(mode="after")
    def check_dates(self) -> "SemesterBase":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self

class SemesterCreate(SemesterBase):
    pass

class SemesterUpdate(SemesterBase):
    pass

class SemesterRead(SemesterBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
