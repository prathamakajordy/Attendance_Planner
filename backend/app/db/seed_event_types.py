from sqlalchemy.orm import Session
from app.models.event_type_definition import EventTypeDefinition

PRESETS = [
    # key, label, cancels, counts, working, exclude
    ("holiday", "Holiday", True, False, False, True),
    ("examination", "Examination", True, False, True, True),
    ("practical_examination", "Practical Examination", True, False, True, True),
    ("college_event", "College Event", True, False, True, True),
    ("technical_fest", "Technical Fest", True, False, True, True),
    ("cultural_fest", "Cultural Fest", True, False, True, True),
    ("sports_event", "Sports Event", True, False, True, True),
    ("industrial_visit", "Industrial Visit", True, True, True, True),
    ("placement_activity", "Placement Activity", True, True, True, True),
    ("vacation", "Vacation", True, False, False, True),
    ("reading_week", "Reading Week", True, False, True, True),
    ("custom", "Other / Custom", True, False, True, True),
]

def seed(db: Session) -> None:
    for key, label, cancels, counts, working, exclude in PRESETS:
        existing = db.query(EventTypeDefinition).filter_by(key=key).one_or_none()
        if existing is None:
            db.add(EventTypeDefinition(
                key=key, 
                label=label, 
                is_system_preset=True,
                default_cancels_lectures=cancels,
                default_counts_towards_attendance=counts,
                default_is_working_day=working,
                default_exclude_from_recommendation=exclude,
            ))
    db.commit()
