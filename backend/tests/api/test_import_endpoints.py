import pytest
import os
import io
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.models.semester import SemesterProfile
from app.models.import_session import ImportSession, ImportTypeEnum, ImportStatusEnum
import pytesseract

@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_semester(test_client):
    res = test_client.post(
        "/api/v1/semesters",
        json={
            "name": "Test Sem",
            "start_date": "2026-08-01",
            "end_date": "2026-12-01",
            "min_overall_percentage": 75.0,
            "min_subject_percentage": 75.0
        }
    )
    # Return an object-like wrapper so mock_semester.id works
    class MockSemester:
        pass
    ms = MockSemester()
    ms.id = res.json()["id"]
    return ms

def test_upload_invalid_file_type(test_client, mock_semester):
    res = test_client.post(
        f"/api/v1/semesters/{mock_semester.id}/import/timetable",
        files={"file": ("test.txt", io.BytesIO(b"dummy content"), "text/plain")}
    )
    assert res.status_code == 400
    assert "Unsupported file format" in res.json()["detail"]

@patch('app.import_service.timetable_parser.TESSERACT_AVAILABLE', False)
def test_ocr_unavailable(test_client, mock_semester):
    # If we upload an image when Tesseract is not available, should return 501
    res = test_client.post(
        f"/api/v1/semesters/{mock_semester.id}/import/timetable",
        files={"file": ("test.png", io.BytesIO(b"dummy image bytes"), "image/png")}
    )
    assert res.status_code == 501
    assert "OCR_UNAVAILABLE" in res.json()["detail"]

@patch('app.import_service.timetable_parser.TESSERACT_AVAILABLE', True)
@patch('app.import_service.timetable_parser.preprocess_image_for_ocr')
@patch('pytesseract.image_to_data')
def test_ocr_failure(mock_image_to_data, mock_preprocess, test_client, mock_semester):
    mock_preprocess.return_value = "dummy_binary_img"
    mock_image_to_data.side_effect = pytesseract.TesseractNotFoundError()
    
    res = test_client.post(
        f"/api/v1/semesters/{mock_semester.id}/import/timetable",
        files={"file": ("test.png", io.BytesIO(b"dummy image bytes"), "image/png")}
    )
    assert res.status_code == 501
    assert "OCR_UNAVAILABLE" in res.json()["detail"]

@patch('app.import_service.timetable_parser.TESSERACT_AVAILABLE', True)
@patch('app.import_service.timetable_parser.preprocess_image_for_ocr')
@patch('pytesseract.image_to_data')
def test_empty_ocr_output(mock_image_to_data, mock_preprocess, test_client, mock_semester):
    mock_preprocess.return_value = "dummy_binary_img"
    # Mock empty tesseract output
    mock_image_to_data.return_value = {
        'text': [''], 'conf': ['-1'], 'left': [0], 'top': [0], 'width': [0], 'height': [0]
    }
    
    res = test_client.post(
        f"/api/v1/semesters/{mock_semester.id}/import/timetable",
        files={"file": ("test.png", io.BytesIO(b"dummy image bytes"), "image/png")}
    )
    # The endpoint should return 422 if no timetable data is found
    assert res.status_code == 422
    assert "No timetable data found" in res.json()["detail"]

@patch('app.import_service.timetable_parser.TESSERACT_AVAILABLE', True)
@patch('app.import_service.timetable_parser.preprocess_image_for_ocr')
@patch('pytesseract.image_to_data')
def test_valid_image_upload(mock_image_to_data, mock_preprocess, test_client, mock_semester):
    mock_preprocess.return_value = "dummy_binary_img"
    
    mock_image_to_data.return_value = {
        'text': ['Day', '09:00', 'Monday', 'Math'], 
        'conf': ['90', '90', '90', '80'], 
        'left': [10, 100, 10, 100], 
        'top': [0, 0, 20, 20], 
        'width': [50, 50, 50, 50], 
        'height': [20, 20, 20, 20]
    }
    
    res = test_client.post(
        f"/api/v1/semesters/{mock_semester.id}/import/timetable",
        files={"file": ("test.png", io.BytesIO(b"dummy image bytes"), "image/png")}
    )
    
    assert res.status_code == 201
    data = res.json()
    assert "session_id" in data or "id" in data
    assert data["import_type"] == "timetable"
    assert len(data["extracted_payload"]) == 1
    
    slot = data["extracted_payload"][0]
    assert slot["weekday"] == 0 # Monday
    assert slot["subject_name"] == "Math"
    assert slot["confidence"] == 0.8 # Math's conf is 80 -> 0.8

@patch('app.import_service.timetable_parser.extract_timetable_from_pdf')
def test_multiple_tables_validation(mock_pdf_extract, test_client, mock_semester):
    # Mock extract to raise multiple timetables detected
    mock_pdf_extract.side_effect = ValueError("MULTIPLE_TIMETABLES_DETECTED")
    
    res = test_client.post(
        f"/api/v1/semesters/{mock_semester.id}/import/timetable",
        files={"file": ("test.pdf", io.BytesIO(b"dummy pdf bytes"), "application/pdf")}
    )
    assert res.status_code == 400
    assert "Multiple timetables detected" in res.json()["detail"]

@patch('app.import_service.timetable_parser.extract_timetable_from_pdf')
def test_temporary_file_cleanup_on_success(mock_pdf_extract, test_client, mock_semester):
    mock_pdf_extract.return_value = [
        {"weekday": 1, "start_time": "09:00", "end_time": "10:00", "subject_name": "Physics", "confidence": 0.9}
    ]
    
    res = test_client.post(
        f"/api/v1/semesters/{mock_semester.id}/import/timetable",
        files={"file": ("cleanup.pdf", io.BytesIO(b"dummy"), "application/pdf")}
    )
    assert res.status_code == 201
    session_id = res.json()["id"]
    
    # We can use API to verify it was created
    res_get = test_client.get(f"/api/v1/import-sessions/{session_id}")
    assert res_get.status_code == 200
    file_path = res_get.json().get("file_path", f"uploads/{session_id}_cleanup.pdf") # Assuming file_path is returned or we guess it
    
    # Actually wait, ImportSessionResponse doesn't return file_path to the frontend!
    # So we'll just check if the file is generated using glob
    import glob
    files_before = glob.glob(f"uploads/{session_id}_*")
    assert len(files_before) > 0
    actual_file = files_before[0]
    
    # Confirm
    res_confirm = test_client.post(
        f"/api/v1/import-sessions/{session_id}/confirm",
        json={"final_payload": res.json()["extracted_payload"]}
    )
    assert res_confirm.status_code == 200
    
    # Verify file is deleted
    assert not os.path.exists(actual_file)

@patch('app.import_service.timetable_parser.extract_timetable_from_pdf')
def test_temporary_file_cleanup_on_delete(mock_pdf_extract, test_client, mock_semester):
    mock_pdf_extract.return_value = [
        {"weekday": 1, "start_time": "09:00", "end_time": "10:00", "subject_name": "Physics", "confidence": 0.9}
    ]
    
    res = test_client.post(
        f"/api/v1/semesters/{mock_semester.id}/import/timetable",
        files={"file": ("cleanup2.pdf", io.BytesIO(b"dummy"), "application/pdf")}
    )
    assert res.status_code == 201
    session_id = res.json()["id"]
    
    import glob
    files_before = glob.glob(f"uploads/{session_id}_*")
    assert len(files_before) > 0
    actual_file = files_before[0]
    
    # Delete
    res_del = test_client.delete(f"/api/v1/import-sessions/{session_id}")
    assert res_del.status_code == 204
    
    # Verify file is deleted
    assert not os.path.exists(actual_file)
