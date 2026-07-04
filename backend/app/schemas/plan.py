from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional


class ErrorResponse(BaseModel):
    """Standardized error response format for all recommendation service endpoints."""
    error_code: str
    message: str


class PlanBlockRead(BaseModel):
    """Response schema for a single continuous time block."""
    id: int
    start_time: time
    end_time: time
    subject_ids: list[int]
    recommendation: str  # "Attend" | "Skip" | "Optional"
    block_explanation: Optional[str] = None

    class Config:
        from_attributes = True


class PlanDayRead(BaseModel):
    """Response schema for a single plan day."""
    id: int
    date: date
    is_lecture_day: bool
    day_explanation: Optional[str] = None
    blocks: list[PlanBlockRead] = []

    class Config:
        from_attributes = True


class FeasibilityIssueRead(BaseModel):
    """Response schema for a single subject's feasibility report."""
    subject_id: int
    subject_name: str
    required_percentage: float
    best_achievable_percentage: float
    is_feasible: bool


class PlanMetadataRead(BaseModel):
    """Response schema for plan generation metadata."""
    generated_at: datetime
    engine_version: str
    overall_feasible: bool
    total_recommended_days: int
    total_recommended_blocks: int
    overall_attendance_threshold: float
    subject_attendance_threshold: float


class PlanGenerationResponse(BaseModel):
    """Top-level response schema for both POST /plan/generate and GET /plan."""
    metadata: PlanMetadataRead
    days: list[PlanDayRead]
    feasibility: list[FeasibilityIssueRead]
