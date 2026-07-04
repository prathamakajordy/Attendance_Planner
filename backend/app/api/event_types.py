from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.event_type_definition import EventTypeDefinition
from app.schemas.event_type import EventTypeDefinitionRead

router = APIRouter()

@router.get("/event-types", response_model=List[EventTypeDefinitionRead])
def get_event_types(db: Session = Depends(get_db)):
    return db.query(EventTypeDefinition).all()
