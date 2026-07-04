from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import semester, subject, timetable, event_types, semester_events
from app.db.session import SessionLocal
from app.db.seed_event_types import seed

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()
    yield

app = FastAPI(title="Attendance Planner AI API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(semester.router, prefix="/api/v1", tags=["semesters"])
app.include_router(subject.router, prefix="/api/v1", tags=["subjects"])
app.include_router(timetable.router, prefix="/api/v1", tags=["timetable"])
app.include_router(event_types.router, prefix="/api/v1", tags=["event_types"])
app.include_router(semester_events.router, prefix="/api/v1", tags=["semester_events"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Attendance Planner AI API"}
