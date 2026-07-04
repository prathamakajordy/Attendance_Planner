from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.timetable import TimetableSlot
from app.models.semester import SemesterProfile
from app.models.subject import Subject
from app.schemas.timetable import TimetableSlotCreate, TimetableSlotUpdate, TimetableSlotRead

router = APIRouter()

@router.post("/semesters/{semester_id}/timetable", response_model=TimetableSlotRead, status_code=201)
def create_timetable_slot(semester_id: int, slot_in: TimetableSlotCreate, db: Session = Depends(get_db)):
    semester = db.query(SemesterProfile).filter(SemesterProfile.id == semester_id).first()
    if not semester:
        raise HTTPException(status_code=404, detail="Semester not found")
        
    subject = db.query(Subject).filter(Subject.id == slot_in.subject_id, Subject.semester_id == semester_id).first()
    if not subject:
        raise HTTPException(status_code=400, detail="Subject does not belong to this semester")

    # Check for overlapping slots
    overlapping = db.query(TimetableSlot).filter(
        TimetableSlot.semester_id == semester_id,
        TimetableSlot.weekday == slot_in.weekday,
        TimetableSlot.start_time < slot_in.end_time,
        TimetableSlot.end_time > slot_in.start_time
    ).first()
    if overlapping:
        raise HTTPException(status_code=422, detail="Timetable slot overlaps with an existing slot")
    
    db_slot = TimetableSlot(**slot_in.model_dump(), semester_id=semester_id)
    db.add(db_slot)
    db.commit()
    db.refresh(db_slot)
    return db_slot

@router.put("/timetable/{slot_id}", response_model=TimetableSlotRead)
def update_timetable_slot(slot_id: int, slot_in: TimetableSlotUpdate, db: Session = Depends(get_db)):
    slot = db.query(TimetableSlot).filter(TimetableSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
        
    # Check for overlaps (excluding self)
    overlapping = db.query(TimetableSlot).filter(
        TimetableSlot.id != slot_id,
        TimetableSlot.semester_id == slot.semester_id,
        TimetableSlot.weekday == slot_in.weekday,
        TimetableSlot.start_time < slot_in.end_time,
        TimetableSlot.end_time > slot_in.start_time
    ).first()
    if overlapping:
        raise HTTPException(status_code=422, detail="Timetable slot overlaps with an existing slot")
    
    update_data = slot_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(slot, key, value)
    
    db.commit()
    db.refresh(slot)
    return slot

@router.delete("/timetable/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_timetable_slot(slot_id: int, db: Session = Depends(get_db)):
    slot = db.query(TimetableSlot).filter(TimetableSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found")
    
    db.delete(slot)
    db.commit()
    return None
