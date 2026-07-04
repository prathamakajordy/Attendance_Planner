from pydantic import BaseModel

class EventTypeDefinitionRead(BaseModel):
    id: int
    key: str
    label: str
    is_system_preset: bool
    default_cancels_lectures: bool
    default_counts_towards_attendance: bool
    default_is_working_day: bool
    default_exclude_from_recommendation: bool
    
    class Config:
        from_attributes = True
