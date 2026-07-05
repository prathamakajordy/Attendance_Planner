from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import time, date
from uuid import UUID

from app.models.import_session import ImportTypeEnum, ImportStatusEnum

class ExtractedTimetableRow(BaseModel):
    weekday: int = Field(..., description="0=Monday, 6=Sunday")
    start_time: time
    end_time: time
    subject_name: str
    confidence: float

class ExtractedCalendarRow(BaseModel):
    event_name: str
    start_date: date
    end_date: date
    inferred_event_type: Optional[str] = None
    confidence: float

class ImportSessionResponse(BaseModel):
    id: str
    semester_id: Optional[int]
    import_type: ImportTypeEnum
    status: ImportStatusEnum
    extracted_payload: List[Dict[str, Any]]

    class Config:
        from_attributes = True

class TimetableConfirmRequest(BaseModel):
    final_payload: List[ExtractedTimetableRow]

class CalendarConfirmRequest(BaseModel):
    final_payload: List[ExtractedCalendarRow]
