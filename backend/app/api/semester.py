from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.semester import SemesterProfile
from app.schemas.semester import SemesterCreate, SemesterUpdate, SemesterRead

router = APIRouter()

@router.post("/semesters", response_model=SemesterRead, status_code=201)
def create_semester(semester_in: SemesterCreate, db: Session = Depends(get_db)):
    db_semester = SemesterProfile(**semester_in.model_dump())
    db.add(db_semester)
    db.commit()
    db.refresh(db_semester)
    return db_semester

@router.get("/semesters/{semester_id}", response_model=SemesterRead)
def get_semester(semester_id: int, db: Session = Depends(get_db)):
    semester = db.query(SemesterProfile).filter(SemesterProfile.id == semester_id).first()
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    return semester

@router.put("/semesters/{semester_id}", response_model=SemesterRead)
def update_semester(semester_id: int, semester_in: SemesterUpdate, db: Session = Depends(get_db)):
    semester = db.query(SemesterProfile).filter(SemesterProfile.id == semester_id).first()
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
    
    update_data = semester_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(semester, key, value)
    
    db.commit()
    db.refresh(semester)
    return semester
