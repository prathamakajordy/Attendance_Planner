import os
import shutil
import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.import_session import ImportSession, ImportTypeEnum, ImportStatusEnum
from app.models.semester import SemesterProfile
from app.schemas.import_schemas import ImportSessionResponse, TimetableConfirmRequest
from app.import_service.timetable_parser import extract_timetable_from_pdf, extract_timetable_from_image
from app.models.timetable import TimetableSlot
from app.schemas.timetable import TimetableSlotCreate
from datetime import time
from app.models.subject import Subject

router = APIRouter()

@router.post("/{semester_id}/import/timetable", response_model=ImportSessionResponse, status_code=201)
async def import_timetable(semester_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = file.filename.split('.')[-1].lower()
    valid_exts = ['pdf', 'png', 'jpg', 'jpeg', 'webp']
    if ext not in valid_exts:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use PDF, PNG, JPG, JPEG, or WEBP.")
    
    parsed_semester_id = None
    if semester_id != "wizard":
        parsed_semester_id = int(semester_id)
        semester = db.query(SemesterProfile).filter(SemesterProfile.id == parsed_semester_id).first()
        if not semester:
            raise HTTPException(status_code=404, detail="Semester not found")
        
    session_id_val = str(uuid.uuid4())
    temp_file_path = f"uploads/{session_id_val}_{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        if ext == 'pdf':
            extracted_rows = extract_timetable_from_pdf(temp_file_path)
        else:
            extracted_rows = extract_timetable_from_image(temp_file_path)
            
        if not extracted_rows:
            os.remove(temp_file_path)
            raise HTTPException(status_code=422, detail="No timetable data found in document.")
            
        session = ImportSession(
            id=session_id_val,
            semester_id=parsed_semester_id,
            import_type=ImportTypeEnum.timetable,
            status=ImportStatusEnum.pending_review,
            extracted_payload=extracted_rows,
            file_path=temp_file_path
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return session
        
    except NotImplementedError as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        if str(e) == "OCR_UNAVAILABLE":
            raise HTTPException(status_code=501, detail="OCR_UNAVAILABLE")
        raise e
    except ValueError as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        if str(e) == "MULTIPLE_TIMETABLES_DETECTED":
            raise HTTPException(status_code=400, detail="Multiple timetables detected. Please upload a single timetable.")
        raise HTTPException(status_code=422, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise e

@router.get("/sessions/{session_id}", response_model=ImportSessionResponse)
def get_import_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(ImportSession).filter(ImportSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.delete("/sessions/{session_id}", status_code=204)
def delete_import_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(ImportSession).filter(ImportSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.file_path and os.path.exists(session.file_path):
        try:
            os.remove(session.file_path)
        except Exception:
            pass
            
    db.delete(session)
    db.commit()

@router.post("/sessions/{session_id}/confirm")
def confirm_import_session(session_id: str, req: TimetableConfirmRequest, db: Session = Depends(get_db)):
    session = db.query(ImportSession).filter(ImportSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status != ImportStatusEnum.pending_review:
        raise HTTPException(status_code=400, detail="Session is not pending review")
    
    if session.import_type != ImportTypeEnum.timetable:
        raise HTTPException(status_code=400, detail="Invalid session type")

    semester_id = session.semester_id
    
    subject_map = {}
    existing_subjects = db.query(Subject).filter(Subject.semester_id == semester_id).all()
    for s in existing_subjects:
        subject_map[s.name.lower()] = s.id

    slots_to_add = []
    for row in req.final_payload:
        sname = row.subject_name.strip()
        if not sname: continue
        key = sname.lower()
        if key not in subject_map:
            new_subject = Subject(semester_id=semester_id, name=sname, held_count=0, present_count=0)
            db.add(new_subject)
            db.commit()
            db.refresh(new_subject)
            subject_map[key] = new_subject.id
        
        slot = TimetableSlot(
            semester_id=semester_id,
            subject_id=subject_map[key],
            weekday=row.weekday,
            start_time=row.start_time,
            end_time=row.end_time,
            order_index=0
        )
        slots_to_add.append(slot)
    
    for slot in slots_to_add:
        db.add(slot)
    
    session.status = ImportStatusEnum.confirmed
    db.commit()
    
    if session.file_path and os.path.exists(session.file_path):
        try:
            os.remove(session.file_path)
        except Exception:
            pass
    
    return {"message": "Confirmed successfully"}
