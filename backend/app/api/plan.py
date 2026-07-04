"""API endpoints for recommendation plan generation and retrieval."""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.plan import (
    PlanGenerationResponse,
    PlanMetadataRead,
    PlanDayRead,
    PlanBlockRead,
    FeasibilityIssueRead,
    ErrorResponse,
)
from app.services.recommendation_service import (
    generate_and_persist_plan,
    get_active_plan,
    PlanNotGeneratedError,
    MissingPlanInputsError,
    ENGINE_VERSION,
)
from app.core.exceptions import SemesterNotFoundError

router = APIRouter()


def _build_plan_response(
    metadata_row,
    plan_day_rows,
    feasibility_list: list[FeasibilityIssueRead] | None = None,
    overall_feasible: bool = True,
) -> PlanGenerationResponse:
    """Converts DB rows into the PlanGenerationResponse schema."""
    days = []
    total_blocks = 0
    for pd in plan_day_rows:
        blocks = []
        for b in pd.blocks:
            blocks.append(PlanBlockRead(
                id=b.id,
                start_time=b.start_time,
                end_time=b.end_time,
                subject_ids=json.loads(b.subject_ids),
                recommendation=b.recommendation,
                block_explanation=b.block_explanation,
            ))
        total_blocks += len(blocks)
        days.append(PlanDayRead(
            id=pd.id,
            date=pd.date,
            is_lecture_day=pd.is_lecture_day,
            day_explanation=pd.day_explanation,
            blocks=blocks,
        ))

    metadata = PlanMetadataRead(
        generated_at=metadata_row.generated_at,
        engine_version=metadata_row.engine_version,
        overall_feasible=overall_feasible,
        total_recommended_days=sum(1 for d in days if d.is_lecture_day),
        total_recommended_blocks=total_blocks,
        overall_attendance_threshold=metadata_row.overall_attendance_threshold,
        subject_attendance_threshold=metadata_row.subject_attendance_threshold,
    )

    return PlanGenerationResponse(
        metadata=metadata,
        days=days,
        feasibility=feasibility_list or [],
    )


@router.post(
    "/semesters/{semester_id}/plan/generate",
    response_model=PlanGenerationResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
def generate_plan_endpoint(semester_id: int, db: Session = Depends(get_db)):
    """Generates a new recommendation plan for the given semester.
    
    Replaces any existing plan. Returns the full plan with metadata and feasibility report.
    """
    try:
        result = generate_and_persist_plan(db, semester_id)
    except SemesterNotFoundError:
        raise HTTPException(
            status_code=404,
            detail={"error_code": "SEMESTER_NOT_FOUND", "message": "The requested semester does not exist."},
        )
    except MissingPlanInputsError as e:
        raise HTTPException(
            status_code=400,
            detail={"error_code": "MISSING_PLAN_INPUTS", "message": e.message},
        )

    # Build feasibility from engine result
    feasibility = [
        FeasibilityIssueRead(
            subject_id=f.subject_id,
            subject_name=f.subject_name,
            required_percentage=f.required_percentage,
            best_achievable_percentage=f.best_achievable_percentage,
            is_feasible=f.is_feasible,
        )
        for f in result.feasibility
    ]

    # Re-fetch from DB to get assigned IDs for the response
    metadata, plan_days = get_active_plan(db, semester_id)

    return _build_plan_response(metadata, plan_days, feasibility, result.overall_feasible)


@router.get(
    "/semesters/{semester_id}/plan",
    response_model=PlanGenerationResponse,
    responses={
        404: {"model": ErrorResponse},
    },
)
def get_plan_endpoint(semester_id: int, db: Session = Depends(get_db)):
    """Retrieves the currently active recommendation plan for the given semester."""
    try:
        metadata, plan_days = get_active_plan(db, semester_id)
    except SemesterNotFoundError:
        raise HTTPException(
            status_code=404,
            detail={"error_code": "SEMESTER_NOT_FOUND", "message": "The requested semester does not exist."},
        )
    except PlanNotGeneratedError:
        raise HTTPException(
            status_code=404,
            detail={"error_code": "PLAN_NOT_GENERATED", "message": "Generate an attendance plan before requesting it."},
        )

    return _build_plan_response(metadata, plan_days, [], metadata.overall_feasible)
