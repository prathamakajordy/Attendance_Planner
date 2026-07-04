from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.semester_event import SemesterEvent
from app.models.semester import SemesterProfile
from app.schemas.semester_event import SemesterEventCreate, SemesterEventUpdate, SemesterEventRead

router = APIRouter()

@router.post("/semesters/{semester_id}/events", response_model=SemesterEventRead, status_code=201)
def create_semester_event(semester_id: int, event_in: SemesterEventCreate, db: Session = Depends(get_db)):
    semester = db.query(SemesterProfile).filter(SemesterProfile.id == semester_id).first()
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
        
    db_event = SemesterEvent(**event_in.model_dump(), semester_id=semester_id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.get("/semesters/{semester_id}/events", response_model=List[SemesterEventRead])
def get_semester_events(semester_id: int, db: Session = Depends(get_db)):
    return db.query(SemesterEvent).filter(SemesterEvent.semester_id == semester_id).all()

@router.put("/events/{event_id}", response_model=SemesterEventRead)
def update_semester_event(event_id: int, event_in: SemesterEventUpdate, db: Session = Depends(get_db)):
    event = db.query(SemesterEvent).filter(SemesterEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    update_data = event_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(event, key, value)
    
    db.commit()
    db.refresh(event)
    return event

@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_semester_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(SemesterEvent).filter(SemesterEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    db.delete(event)
    db.commit()
    return None
