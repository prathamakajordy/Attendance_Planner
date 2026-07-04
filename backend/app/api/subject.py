from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.subject import Subject
from app.models.semester import SemesterProfile
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectRead

router = APIRouter()

@router.post("/semesters/{semester_id}/subjects", response_model=SubjectRead, status_code=201)
def create_subject(semester_id: int, subject_in: SubjectCreate, db: Session = Depends(get_db)):
    semester = db.query(SemesterProfile).filter(SemesterProfile.id == semester_id).first()
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    
    db_subject = Subject(**subject_in.model_dump(), semester_id=semester_id)
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject

@router.get("/semesters/{semester_id}/subjects", response_model=List[SubjectRead])
def get_subjects(semester_id: int, db: Session = Depends(get_db)):
    semester = db.query(SemesterProfile).filter(SemesterProfile.id == semester_id).first()
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    
    subjects = db.query(Subject).filter(Subject.semester_id == semester_id).all()
    return subjects

@router.put("/subjects/{subject_id}", response_model=SubjectRead)
def update_subject(subject_id: int, subject_in: SubjectUpdate, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    update_data = subject_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(subject, key, value)
    
    db.commit()
    db.refresh(subject)
    return subject

@router.delete("/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    db.delete(subject)
    db.commit()
    return None
