from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import semester, subject, timetable, event_types, semester_events, plan, import_endpoints
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

app = FastAPI(
    title="Attendance Planner AI API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(semester.router, prefix="/api/v1", tags=["Semesters"])
app.include_router(subject.router, prefix="/api/v1", tags=["Subjects"])
app.include_router(timetable.router, prefix="/api/v1", tags=["Timetable"])
app.include_router(event_types.router, prefix="/api/v1", tags=["Event Types"])
app.include_router(semester_events.router, prefix="/api/v1", tags=["Semester Events"])
app.include_router(plan.router, prefix="/api/v1", tags=["Recommendation Engine"])
app.include_router(import_endpoints.router, prefix="/api/v1/semesters", tags=["Document Import"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Attendance Planner AI API"}
