from pydantic import BaseModel, Field, model_validator
from typing import Optional

class SubjectBase(BaseModel):
    name: str = Field(min_length=1)
    code: Optional[str] = None
    min_percentage_override: Optional[float] = Field(default=None, gt=0, le=100)
    held_count: int = Field(default=0, ge=0)
    present_count: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def check_counts(self) -> "SubjectBase":
        if self.present_count > self.held_count:
            raise ValueError("present_count cannot exceed held_count")
        return self

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(SubjectBase):
    pass

class SubjectRead(SubjectBase):
    id: int
    semester_id: int

    class Config:
        from_attributes = True
