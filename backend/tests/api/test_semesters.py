from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Attendance Planner AI API"}

def test_create_semester():
    with TestClient(app) as test_client: # Uses lifespan
        response = test_client.post(
            "/api/v1/semesters",
            json={
                "name": "Test Sem",
                "start_date": "2026-08-01",
                "end_date": "2026-12-01",
                "min_overall_percentage": 75.0,
                "min_subject_percentage": 75.0
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Sem"
        assert "id" in data

def test_get_event_types():
    with TestClient(app) as test_client:
        response = test_client.get("/api/v1/event-types")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 12
        assert any(e["key"] == "holiday" for e in data)
