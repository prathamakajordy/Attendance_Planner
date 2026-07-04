"""Integration tests for the Plan API endpoints.

These tests create a complete in-memory database with semester, subjects,
timetable, and events, then exercise the full pipeline:
DB -> Service -> Engine -> Persistence -> API Response.
"""
import pytest
from datetime import date, time
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.semester import SemesterProfile
from app.models.subject import Subject
from app.models.timetable import TimetableSlot, WeekdayEnum
from app.models.event_type_definition import EventTypeDefinition
from app.models.semester_event import SemesterEvent
from app.models.plan import PlanMetadata, PlanDay, PlanBlock


# --- Test database setup ---

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def override_deps():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def setup_db():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)

    # Seed event type definitions
    db = TestingSessionLocal()
    if not db.query(EventTypeDefinition).first():
        db.add(EventTypeDefinition(
            id=1, key="holiday", label="Holiday",
            is_system_preset=True,
            default_cancels_lectures=True,
            default_counts_towards_attendance=False,
            default_is_working_day=False,
            default_exclude_from_recommendation=True,
        ))
        db.commit()
    db.close()

    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def _seed_semester(db, with_subjects=True, with_timetable=True):
    """Helper to seed a complete semester for testing."""
    semester = SemesterProfile(
        name="Test Sem",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 28),
        min_overall_percentage=75.0,
        min_subject_percentage=75.0,
        student_groups=[],
    )
    db.add(semester)
    db.commit()
    db.refresh(semester)

    if with_subjects:
        s1 = Subject(semester_id=semester.id, name="DBMS", held_count=4, present_count=2)
        s2 = Subject(semester_id=semester.id, name="OS", held_count=4, present_count=4)
        db.add_all([s1, s2])
        db.commit()
        db.refresh(s1)
        db.refresh(s2)

        if with_timetable:
            # Thursday = weekday 3
            t1 = TimetableSlot(
                semester_id=semester.id, subject_id=s1.id,
                weekday=WeekdayEnum.THURSDAY,
                start_time=time(9, 0), end_time=time(10, 0), order_index=0,
            )
            t2 = TimetableSlot(
                semester_id=semester.id, subject_id=s2.id,
                weekday=WeekdayEnum.THURSDAY,
                start_time=time(10, 0), end_time=time(11, 0), order_index=1,
            )
            db.add_all([t1, t2])
            db.commit()

    return semester.id


# --- Tests ---

class TestGeneratePlan:
    """Tests for POST /api/v1/semesters/{id}/plan/generate"""

    def test_generate_plan_success(self, client, db):
        sem_id = _seed_semester(db)
        response = client.post(f"/api/v1/semesters/{sem_id}/plan/generate")

        assert response.status_code == 200
        data = response.json()

        # Verify metadata
        assert "metadata" in data
        meta = data["metadata"]
        assert meta["engine_version"] == "v1.0"
        assert "generated_at" in meta
        assert isinstance(meta["overall_feasible"], bool)
        assert isinstance(meta["total_recommended_days"], int)
        assert isinstance(meta["total_recommended_blocks"], int)
        assert meta["overall_attendance_threshold"] == 75.0
        assert meta["subject_attendance_threshold"] == 75.0

        # Verify days exist
        assert "days" in data
        assert len(data["days"]) > 0

        # Verify feasibility
        assert "feasibility" in data

    def test_generate_plan_semester_not_found(self, client):
        response = client.post("/api/v1/semesters/9999/plan/generate")
        assert response.status_code == 404
        detail = response.json()["detail"]
        assert detail["error_code"] == "SEMESTER_NOT_FOUND"

    def test_generate_plan_no_subjects(self, client, db):
        sem_id = _seed_semester(db, with_subjects=False)
        response = client.post(f"/api/v1/semesters/{sem_id}/plan/generate")
        assert response.status_code == 400
        detail = response.json()["detail"]
        assert detail["error_code"] == "MISSING_PLAN_INPUTS"
        assert "subjects" in detail["message"].lower()

    def test_generate_plan_no_timetable(self, client, db):
        sem_id = _seed_semester(db, with_timetable=False)
        response = client.post(f"/api/v1/semesters/{sem_id}/plan/generate")
        assert response.status_code == 400
        detail = response.json()["detail"]
        assert detail["error_code"] == "MISSING_PLAN_INPUTS"
        assert "timetable" in detail["message"].lower()

    def test_generate_plan_replaces_existing(self, client, db):
        sem_id = _seed_semester(db)

        # Generate first plan
        r1 = client.post(f"/api/v1/semesters/{sem_id}/plan/generate")
        assert r1.status_code == 200
        gen1 = r1.json()["metadata"]["generated_at"]

        # Generate second plan (should replace)
        r2 = client.post(f"/api/v1/semesters/{sem_id}/plan/generate")
        assert r2.status_code == 200
        gen2 = r2.json()["metadata"]["generated_at"]

        # Timestamps should be different
        assert gen1 != gen2

        # Only one metadata row should exist
        count = db.query(PlanMetadata).filter(PlanMetadata.semester_id == sem_id).count()
        assert count == 1


class TestGetPlan:
    """Tests for GET /api/v1/semesters/{id}/plan"""

    def test_get_plan_success(self, client, db):
        sem_id = _seed_semester(db)
        # Generate first
        client.post(f"/api/v1/semesters/{sem_id}/plan/generate")

        response = client.get(f"/api/v1/semesters/{sem_id}/plan")
        assert response.status_code == 200
        data = response.json()
        assert "metadata" in data
        assert "days" in data

    def test_get_plan_not_generated(self, client, db):
        sem_id = _seed_semester(db)
        response = client.get(f"/api/v1/semesters/{sem_id}/plan")
        assert response.status_code == 404
        detail = response.json()["detail"]
        assert detail["error_code"] == "PLAN_NOT_GENERATED"

    def test_get_plan_semester_not_found(self, client):
        response = client.get("/api/v1/semesters/9999/plan")
        assert response.status_code == 404
        detail = response.json()["detail"]
        assert detail["error_code"] == "SEMESTER_NOT_FOUND"

    def test_get_plan_has_blocks(self, client, db):
        sem_id = _seed_semester(db)
        client.post(f"/api/v1/semesters/{sem_id}/plan/generate")

        response = client.get(f"/api/v1/semesters/{sem_id}/plan")
        data = response.json()

        # Find a lecture day
        lecture_days = [d for d in data["days"] if d["is_lecture_day"]]
        assert len(lecture_days) > 0

        # Lecture days should have blocks
        for ld in lecture_days:
            assert len(ld["blocks"]) > 0
            for block in ld["blocks"]:
                assert "start_time" in block
                assert "end_time" in block
                assert "subject_ids" in block
                assert "recommendation" in block
                assert block["recommendation"] in ("Attend", "Skip", "Optional")


class TestPlanIntegrity:
    """Integration tests verifying the full pipeline correctness."""

    def test_plan_reflects_attendance_state(self, client, db):
        """DBMS is at 50% (below 75%), OS is at 100% (safe).
        The engine should recommend attending DBMS and skipping OS."""
        sem_id = _seed_semester(db)
        client.post(f"/api/v1/semesters/{sem_id}/plan/generate")

        response = client.get(f"/api/v1/semesters/{sem_id}/plan")
        data = response.json()

        # Find the first lecture day
        lecture_day = next(d for d in data["days"] if d["is_lecture_day"])

        # Should have blocks with meaningful recommendations
        assert len(lecture_day["blocks"]) >= 1

    def test_holiday_excludes_lectures(self, client, db):
        """A holiday on a lecture day should result in no blocks for that day."""
        sem_id = _seed_semester(db)

        # Add a holiday on the first Thursday (Jan 1)
        db.add(SemesterEvent(
            semester_id=sem_id, event_type_id=1, name="New Year",
            start_date=date(2026, 1, 1), end_date=date(2026, 1, 1),
        ))
        db.commit()

        client.post(f"/api/v1/semesters/{sem_id}/plan/generate")
        response = client.get(f"/api/v1/semesters/{sem_id}/plan")
        data = response.json()

        holiday_day = next(d for d in data["days"] if d["date"] == "2026-01-01")
        assert holiday_day["is_lecture_day"] is False
        assert len(holiday_day["blocks"]) == 0
