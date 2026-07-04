# Technical Requirements Document (TRD)
## Attendance Planner AI

**Companion to:** `Attendance_Planner_AI_SRD.md` (v1.0, including the Flexible Semester Events enhancement)
**Document Version:** 1.0
**Audience:** AI coding assistants and the solo developer implementing this system module by module.

**Relationship to the SRD:** The SRD defines *what* the system must do and *why* (personas, requirements, UX, optimization philosophy). This TRD defines *how* it is built — concrete architecture, module contracts, algorithm implementations, schema-to-ORM mapping, API contracts with request/response bodies, and engineering/operational detail. Every section here traces back to an SRD section; where the two could drift, the SRD's rules (Sections 15–19) are the source of truth for *behavior*, and this document is the source of truth for *implementation*.

---

## Table of Contents

1. Purpose & Scope
2. System Architecture
3. Technology Stack (Pinned)
4. Repository & Module Layout
5. Backend Component Design
6. ORM Models (SQLAlchemy)
7. Pydantic Schemas (Request/Response Contracts)
8. Recommendation Engine — Technical Design
9. API Specification (Detailed)
10. Frontend Architecture
11. State Management & Data Flow
12. Error Handling & Logging
13. Security Considerations
14. Performance Requirements & Complexity Analysis
15. Configuration & Environment Management
16. Local Development Setup
17. Deployment Architecture
18. CI/CD Pipeline
19. Testing Strategy (Technical)
20. Coding Standards & Conventions
21. Dependency Manifest
22. Technical Risks & Mitigations
23. Traceability Matrix (SRD → TRD)
24. Appendix: Sample Payloads

---

## 1. Purpose & Scope

This TRD translates the Attendance Planner AI SRD into an implementable technical specification. It covers:

- Concrete module boundaries and their responsibilities/interfaces.
- Exact ORM models mapped 1:1 to the SRD's Section 14 schema.
- Pydantic request/response contracts for every endpoint in SRD Section 24.
- A step-by-step, pseudocode-level specification of the Recommendation Engine (SRD Section 15), including the Event Resolution step introduced by the Flexible Semester Events enhancement.
- Frontend component/state design supporting SRD Sections 20–21.
- Non-functional engineering concerns (performance, security, logging, deployment) not detailed in the SRD.

Out of scope: product rationale, personas, UX copy, and roadmap prioritization — all of which remain owned by the SRD.

---

## 2. System Architecture

### 2.1 High-Level Architecture (MVP)

```
┌─────────────────────────┐        HTTPS/JSON        ┌──────────────────────────────┐
│   Frontend (React SPA)  │ ───────────────────────▶ │   Backend (FastAPI, Python)  │
│   Vite build, Tailwind  │ ◀─────────────────────── │   Uvicorn ASGI server        │
└─────────────────────────┘                           └───────────────┬───────────────┘
                                                                       │ SQLAlchemy ORM
                                                                       ▼
                                                        ┌──────────────────────────────┐
                                                        │   SQLite (file: app.db)      │
                                                        └──────────────────────────────┘
```

- **Deployment topology:** stateless backend process (single instance, MVP scale does not require horizontal scaling), file-based SQLite DB co-located with the backend (or a mounted persistent disk on Render).
- **No message queue, no background workers, no cache layer** in MVP — plan generation is synchronous and fast enough (Section 14) to run inline on request.
- **No server-side session state** — the frontend is a single-user, single-semester-at-a-time client in MVP (SRD explicitly excludes auth/multi-user, Section 5).

### 2.2 Layered Backend Architecture

```
api/            → FastAPI routers; HTTP concerns only (status codes, request parsing)
schemas/        → Pydantic request/response models; validation boundary
models/         → SQLAlchemy ORM models; persistence boundary
engine/         → Pure-Python domain logic (no FastAPI/SQLAlchemy imports); the
                  recommendation engine, event resolution, calendar expansion
core/           → Cross-cutting config, validation helpers, custom exceptions
db/             → Session management, engine bootstrap, seed data (event type presets)
```

The `engine/` package is deliberately **framework-agnostic** (plain Python, dataclasses/typed dicts in, typed dicts out) so it can be unit-tested without spinning up FastAPI or a real database, and so it remains portable if the OR-Tools upgrade (SRD Section 25) is introduced later as an alternate implementation behind the same interface.

### 2.3 Request Lifecycle (Plan Generation)

```
POST /semesters/{id}/plan/generate
  → api/plan.py: validate semester_id exists
  → db: load SemesterProfile, Subjects, TimetableSlots, SemesterEvents, EventTypeDefinitions
  → engine.event_resolution.resolve_events(events, type_defs) -> ResolvedEvent[]
  → engine.calendar_expansion.expand(semester, timetable, resolved_events) -> CalendarDay[]
  → engine.requirement_calc.compute_requirements(subjects, calendar_days) -> RequirementResult[]
  → engine.slot_selector.select(calendar_days, requirement_results) -> DaySelection[]
  → engine.block_consolidation.consolidate(day_selections) -> PlanDay[] (with PlanBlocks)
  → engine.requirement_calc.verify_feasibility(...) -> FeasibilityReport
  → engine.explanation_generator.annotate(plan_days) -> PlanDay[] (with explanation strings)
  → db: persist PlanDay + PlanBlock rows (replace prior plan for this semester)
  → api/plan.py: return PlanGenerateResponse (summary + feasibility report)
```

---

## 3. Technology Stack (Pinned)

| Layer | Technology | Target Version (MVP baseline) | Notes |
|---|---|---|---|
| Backend language/runtime | Python | 3.11+ | Matches FastAPI/Pydantic v2 support window. |
| Backend framework | FastAPI | 0.115.x | ASGI, native Pydantic v2 integration. |
| ASGI server | Uvicorn | 0.30.x | `uvicorn app.main:app --reload` for dev. |
| Validation | Pydantic | 2.x | Used for all request/response schemas. |
| ORM | SQLAlchemy | 2.x (declarative style) | Sync engine in MVP; async is a non-goal until scale demands it. |
| Migrations | Alembic | 1.13.x | Even for SQLite MVP, so schema changes (e.g., future event types tooling) are tracked. |
| DB (MVP) | SQLite | 3.4x (bundled with Python) | Single file, `app.db`. |
| DB (future) | PostgreSQL | 15+ | Swap-in via `DATABASE_URL`; SQLAlchemy abstracts dialect differences. |
| Frontend build tool | Vite | 5.x | Dev server + production bundling. |
| Frontend framework | React | 18.x | Function components + hooks only; no class components. |
| Styling | Tailwind CSS | 3.x | Utility-first; no CSS-in-JS. |
| Charts | Chart.js (+ react-chartjs-2) | 4.x / 5.x | Dashboard progress bars, subject charts. |
| Calendar UI | FullCalendar (core + daygrid) | 6.x | Calendar View day coloring. |
| HTTP client | fetch (native) or Axios | Axios 1.x | Centralized in `frontend/src/api/client.js`. |
| Testing (backend) | pytest, pytest-cov | latest stable | Unit + API integration tests. |
| Testing (frontend) | Vitest + React Testing Library | latest stable | Component and interaction tests. |
| Linting/formatting (Python) | ruff, black | latest stable | `ruff check`, `black --check` in CI. |
| Linting/formatting (JS) | ESLint, Prettier | latest stable | Airbnb-style or standard config, project's choice. |
| Hosting (frontend) | Vercel | — | Free tier. |
| Hosting (backend) | Render | — | Free tier web service. |
| CI | GitHub Actions | — | Free for public/private repos within free-tier minutes. |

All versions above are **floors, not ceilings** — pin exact versions in `requirements.txt` / `package.json` at implementation time and update this table to match.

---

## 4. Repository & Module Layout

This expands SRD Section 23 with responsibility notes per file:

```
attendance-planner-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                       # FastAPI() app, router registration, CORS, startup hooks
│   │   ├── api/
│   │   │   ├── semester.py               # CRUD: SemesterProfile
│   │   │   ├── subject.py                # CRUD: Subject
│   │   │   ├── timetable.py              # CRUD: TimetableSlot
│   │   │   ├── event_types.py            # READ: EventTypeDefinition (seeded, read-mostly in MVP)
│   │   │   ├── semester_events.py        # CRUD: SemesterEvent
│   │   │   └── plan.py                   # POST generate, GET plan + view adapters
│   │   ├── models/
│   │   │   ├── semester.py
│   │   │   ├── subject.py
│   │   │   ├── timetable.py
│   │   │   ├── event_type_definition.py
│   │   │   ├── semester_event.py
│   │   │   └── plan.py                   # PlanDay, PlanBlock, PlanSlotOutcome
│   │   ├── schemas/
│   │   │   ├── semester.py
│   │   │   ├── subject.py
│   │   │   ├── timetable.py
│   │   │   ├── event_type.py
│   │   │   ├── semester_event.py
│   │   │   └── plan.py
│   │   ├── engine/
│   │   │   ├── types.py                  # Shared dataclasses/TypedDicts across engine modules
│   │   │   ├── event_resolution.py       # SRD 15.2
│   │   │   ├── calendar_expansion.py     # SRD 15.3
│   │   │   ├── requirement_calc.py       # SRD 15.4 + 15.7 (feasibility re-check)
│   │   │   ├── slot_selector.py          # SRD 15.5
│   │   │   ├── block_consolidation.py    # SRD 15.6
│   │   │   ├── explanation_generator.py  # SRD 15.9
│   │   │   └── pipeline.py               # Orchestrates the above in order (Section 2.3)
│   │   ├── db/
│   │   │   ├── session.py                # SessionLocal, get_db() dependency
│   │   │   ├── base.py                   # Declarative Base
│   │   │   ├── init_db.py                # create_all() for local/dev; Alembic used for real migrations
│   │   │   └── seed_event_types.py       # Seeds the 12 SRD-defined presets idempotently
│   │   └── core/
│   │       ├── config.py                 # Pydantic Settings (env-driven)
│   │       ├── exceptions.py             # Domain exceptions (InfeasibleTargetError, ValidationError, etc.)
│   │       └── validation.py             # Shared validators (date ranges, overlap checks)
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── tests/
│   │   ├── engine/                       # Pure unit tests, no DB/HTTP
│   │   ├── api/                          # FastAPI TestClient integration tests
│   │   └── fixtures/
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/
│   ├── src/
│   │   ├── pages/                        # One file per SRD Section 20 screen
│   │   ├── components/
│   │   │   ├── calendar/
│   │   │   ├── dashboard/
│   │   │   ├── forms/                    # SemesterEventForm, TimetableSlotForm, etc.
│   │   │   └── shared/
│   │   ├── api/
│   │   │   └── client.js                 # Axios instance + typed request helpers
│   │   ├── hooks/
│   │   │   ├── useSemester.js
│   │   │   ├── usePlan.js
│   │   │   └── useSemesterEvents.js
│   │   ├── context/
│   │   │   └── SemesterContext.jsx       # Active semester_id + shared cache
│   │   └── App.jsx
│   ├── index.html
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── package.json
├── docs/
│   ├── Attendance_Planner_AI_SRD.md
│   └── Attendance_Planner_AI_TRD.md
└── README.md
```

---

## 5. Backend Component Design

### 5.1 `db/session.py`
```python
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
`get_db` is injected into every route via FastAPI `Depends`.

### 5.2 `core/config.py`
Environment-driven settings (Section 15):
```python
class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./app.db"
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    ENV: Literal["local", "staging", "production"] = "local"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
```

### 5.3 `core/exceptions.py`
Domain-specific exceptions, mapped to HTTP responses via FastAPI exception handlers (not raw 500s):
```python
class ValidationFailedError(Exception):
    def __init__(self, errors: list[dict]): self.errors = errors

class SemesterNotFoundError(Exception): ...
class InfeasibleTargetWarning(Exception):
    """Not fatal — carries a FeasibilityReport for the caller to surface as a warning."""
```

### 5.4 `db/seed_event_types.py`
Idempotent seeding run at app startup (`main.py` startup event) and available as a standalone script for fresh environments/tests:
```python
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
                key=key, label=label, is_system_preset=True,
                default_cancels_lectures=cancels,
                default_counts_towards_attendance=counts,
                default_is_working_day=working,
                default_exclude_from_recommendation=exclude,
            ))
    db.commit()
```

---

## 6. ORM Models (SQLAlchemy)

Direct mapping of SRD Section 14. Declarative style, SQLAlchemy 2.x typed mappings shown in abbreviated form:

```python
class SemesterProfile(Base):
    __tablename__ = "semester_profile"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    start_date: Mapped[date]
    end_date: Mapped[date]
    min_overall_percentage: Mapped[float]
    min_subject_percentage: Mapped[float]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    subjects: Mapped[list["Subject"]] = relationship(back_populates="semester", cascade="all, delete-orphan")
    timetable_slots: Mapped[list["TimetableSlot"]] = relationship(back_populates="semester", cascade="all, delete-orphan")
    events: Mapped[list["SemesterEvent"]] = relationship(back_populates="semester", cascade="all, delete-orphan")
    plan_days: Mapped[list["PlanDay"]] = relationship(back_populates="semester", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subject"
    id: Mapped[int] = mapped_column(primary_key=True)
    semester_id: Mapped[int] = mapped_column(ForeignKey("semester_profile.id", ondelete="CASCADE"))
    name: Mapped[str]
    code: Mapped[str | None]
    min_percentage_override: Mapped[float | None]
    held_count: Mapped[int] = mapped_column(default=0)
    present_count: Mapped[int] = mapped_column(default=0)

    semester: Mapped["SemesterProfile"] = relationship(back_populates="subjects")


class TimetableSlot(Base):
    __tablename__ = "timetable_slot"
    id: Mapped[int] = mapped_column(primary_key=True)
    semester_id: Mapped[int] = mapped_column(ForeignKey("semester_profile.id", ondelete="CASCADE"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subject.id", ondelete="CASCADE"))
    weekday: Mapped[int]                  # 0=Mon .. 6=Sun
    start_time: Mapped[time]
    end_time: Mapped[time]
    order_index: Mapped[int]


class EventTypeDefinition(Base):
    __tablename__ = "event_type_definition"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(unique=True)
    label: Mapped[str]
    is_system_preset: Mapped[bool] = mapped_column(default=False)
    default_cancels_lectures: Mapped[bool]
    default_counts_towards_attendance: Mapped[bool]
    default_is_working_day: Mapped[bool]
    default_exclude_from_recommendation: Mapped[bool]


class SemesterEvent(Base):
    __tablename__ = "semester_event"
    id: Mapped[int] = mapped_column(primary_key=True)
    semester_id: Mapped[int] = mapped_column(ForeignKey("semester_profile.id", ondelete="CASCADE"))
    event_type_id: Mapped[int] = mapped_column(ForeignKey("event_type_definition.id"))
    custom_type_label: Mapped[str | None]
    name: Mapped[str]
    start_date: Mapped[date]
    end_date: Mapped[date]
    description: Mapped[str | None]
    cancels_lectures_override: Mapped[bool | None]
    counts_towards_attendance_override: Mapped[bool | None]
    is_working_day_override: Mapped[bool | None]
    exclude_from_recommendation_override: Mapped[bool | None]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    event_type: Mapped["EventTypeDefinition"] = relationship()
    semester: Mapped["SemesterProfile"] = relationship(back_populates="events")


class PlanDay(Base):
    __tablename__ = "plan_day"
    id: Mapped[int] = mapped_column(primary_key=True)
    semester_id: Mapped[int] = mapped_column(ForeignKey("semester_profile.id", ondelete="CASCADE"))
    date: Mapped[date]
    weekday: Mapped[int]
    is_lecture_day: Mapped[bool]
    day_explanation: Mapped[str | None]

    blocks: Mapped[list["PlanBlock"]] = relationship(back_populates="plan_day", cascade="all, delete-orphan")
    semester: Mapped["SemesterProfile"] = relationship(back_populates="plan_days")


class PlanBlock(Base):
    __tablename__ = "plan_block"
    id: Mapped[int] = mapped_column(primary_key=True)
    plan_day_id: Mapped[int] = mapped_column(ForeignKey("plan_day.id", ondelete="CASCADE"))
    start_time: Mapped[time]
    end_time: Mapped[time]
    subject_ids: Mapped[str]              # JSON-encoded list[int]
    recommendation: Mapped[str]           # "Attend" | "Skip" | "Optional"
    block_explanation: Mapped[str | None]

    plan_day: Mapped["PlanDay"] = relationship(back_populates="blocks")
```

`subject_ids` is stored as a JSON string column (SQLite has no native array type); the ORM layer exposes a `subject_ids_list` property that (de)serializes via `json.loads`/`json.dumps` so callers never touch raw JSON.

---

## 7. Pydantic Schemas (Request/Response Contracts)

### 7.1 SemesterEvent schemas
```python
class SemesterEventBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    event_type_id: int
    custom_type_label: str | None = None
    start_date: date
    end_date: date
    description: str | None = None
    cancels_lectures_override: bool | None = None
    counts_towards_attendance_override: bool | None = None
    is_working_day_override: bool | None = None
    exclude_from_recommendation_override: bool | None = None

    @model_validator(mode="after")
    def check_dates_and_custom_label(self) -> "SemesterEventBase":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self

class SemesterEventCreate(SemesterEventBase): pass
class SemesterEventUpdate(SemesterEventBase): pass

class SemesterEventRead(SemesterEventBase):
    id: int
    semester_id: int
    resolved_cancels_lectures: bool
    resolved_counts_towards_attendance: bool
    resolved_is_working_day: bool
    resolved_exclude_from_recommendation: bool
    model_config = ConfigDict(from_attributes=True)
```
Note: `resolved_*` fields are computed server-side at read time (not stored) by applying Section 8.1's resolution rule, so the frontend never has to reimplement the override-vs-default fallback logic.

### 7.2 EventTypeDefinition (read-only in MVP)
```python
class EventTypeDefinitionRead(BaseModel):
    id: int
    key: str
    label: str
    is_system_preset: bool
    default_cancels_lectures: bool
    default_counts_towards_attendance: bool
    default_is_working_day: bool
    default_exclude_from_recommendation: bool
    model_config = ConfigDict(from_attributes=True)
```

### 7.3 Plan generation response
```python
class FeasibilityIssue(BaseModel):
    subject_id: int
    subject_name: str
    required_percentage: float
    best_achievable_percentage: float
    is_feasible: bool

class PlanGenerateResponse(BaseModel):
    semester_id: int
    generated_at: datetime
    total_plan_days: int
    total_attend_blocks: int
    total_skip_blocks: int
    overall_feasible: bool
    subject_feasibility: list[FeasibilityIssue]
```

Full schemas for `Semester`, `Subject`, `TimetableSlot`, and the five plan-view response shapes (`CalendarViewResponse`, `DailyScheduleResponse`, `SubjectViewResponse`, `DashboardResponse`, `TimelineResponse`) follow the same `*Base / *Create / *Update / *Read` pattern and are enumerated in Section 9.

---

## 8. Recommendation Engine — Technical Design

This section is the implementation-level counterpart to SRD Section 15. All engine functions are pure (no I/O), operate on plain dataclasses, and are independently unit-testable.

### 8.1 `engine/types.py`
```python
@dataclass(frozen=True)
class ResolvedEvent:
    id: int
    start_date: date
    end_date: date
    cancels_lectures: bool
    counts_towards_attendance: bool
    is_working_day: bool
    exclude_from_recommendation: bool

@dataclass
class CalendarDay:
    date: date
    weekday: int
    is_lecture_day: bool
    slots: list["TimetableSlotRef"]        # empty if is_lecture_day is False
    covering_event_ids: list[int]
    counts_towards_attendance: bool | None  # None if no covering event
    is_working_day: bool | None

@dataclass
class TimetableSlotRef:
    slot_id: int
    subject_id: int
    start_time: time
    end_time: time
    order_index: int

@dataclass
class RequirementResult:
    subject_id: int
    required_percentage: float
    total_future_lectures: int
    need_attend: int
    is_feasible: bool
    best_achievable_percentage: float
```

### 8.2 `engine/event_resolution.py` (SRD 15.2)
```python
def resolve_events(
    events: list[SemesterEvent], type_defs: dict[int, EventTypeDefinition]
) -> list[ResolvedEvent]:
    resolved = []
    for e in events:
        t = type_defs[e.event_type_id]
        resolved.append(ResolvedEvent(
            id=e.id,
            start_date=e.start_date,
            end_date=e.end_date,
            cancels_lectures=_coalesce(e.cancels_lectures_override, t.default_cancels_lectures),
            counts_towards_attendance=_coalesce(e.counts_towards_attendance_override, t.default_counts_towards_attendance),
            is_working_day=_coalesce(e.is_working_day_override, t.default_is_working_day),
            exclude_from_recommendation=_coalesce(e.exclude_from_recommendation_override, t.default_exclude_from_recommendation),
        ))
    return resolved

def _coalesce(override: bool | None, default: bool) -> bool:
    return default if override is None else override
```

### 8.3 `engine/calendar_expansion.py` (SRD 15.3)
```python
def expand(
    semester: SemesterProfile,
    timetable: list[TimetableSlotRef],
    resolved_events: list[ResolvedEvent],
) -> list[CalendarDay]:
    days: list[CalendarDay] = []
    for d in daterange(semester.start_date, semester.end_date):
        weekday = d.weekday()
        covering = [e for e in resolved_events if e.start_date <= d <= e.end_date]

        # Most-restrictive-wins per flag across all covering events (SRD 15.3, Edge Cases 17)
        exclude = any(e.exclude_from_recommendation for e in covering)
        cancels = any(e.cancels_lectures for e in covering)
        counts = _most_restrictive_or_none([e.counts_towards_attendance for e in covering])
        working = _most_restrictive_or_none([e.is_working_day for e in covering], invert=True)
        # "most restrictive" for is_working_day means False (not-a-working-day) wins if any event says so.

        base_slots = [s for s in timetable if s.weekday == weekday]
        slots = [] if (exclude or cancels) else base_slots
        is_lecture_day = (not exclude) and len(slots) > 0

        days.append(CalendarDay(
            date=d, weekday=weekday, is_lecture_day=is_lecture_day, slots=slots,
            covering_event_ids=[e.id for e in covering],
            counts_towards_attendance=counts, is_working_day=working,
        ))
    return days
```

`is_lecture_day = False` days never proceed to slot selection — they are terminal for planning purposes but still stored (with `blocks = []`) so the Calendar View can render them as gray/excluded with the covering event(s) shown on click (SRD Section 20, item 3).

### 8.4 `engine/requirement_calc.py` (SRD 15.4 + 15.7)
```python
def compute_requirements(subjects: list[Subject], days: list[CalendarDay]) -> list[RequirementResult]:
    results = []
    for s in subjects:
        required_pct = s.min_percentage_override or DEFAULT_SUBJECT_PCT
        future_count = sum(
            1 for d in days if d.is_lecture_day
            for slot in d.slots if slot.subject_id == s.id
        )
        need = _smallest_attend_count(
            present=s.present_count, held=s.held_count,
            future_total=future_count, required_pct=required_pct,
        )
        feasible = need <= future_count
        best_pct = _pct(s.present_count + future_count, s.held_count + future_count) if not feasible \
                   else required_pct
        results.append(RequirementResult(
            subject_id=s.id, required_percentage=required_pct,
            total_future_lectures=future_count, need_attend=max(need, 0),
            is_feasible=feasible, best_achievable_percentage=best_pct,
        ))
    return results

def _smallest_attend_count(present: int, held: int, future_total: int, required_pct: float) -> int:
    # Solve for smallest integer x in [0, future_total] such that
    # (present + x) / (held + future_total) >= required_pct / 100
    threshold = (required_pct / 100) * (held + future_total) - present
    return max(0, math.ceil(threshold))
```

### 8.5 `engine/slot_selector.py` (SRD 15.5)
```python
def select(days: list[CalendarDay], requirements: dict[int, RequirementResult]) -> list[DaySelection]:
    remaining_need = {r.subject_id: r.need_attend for r in requirements.values()}
    remaining_occurrences = {r.subject_id: r.total_future_lectures for r in requirements.values()}
    selections = []

    for d in days:
        if not d.is_lecture_day:
            selections.append(DaySelection(date=d.date, slot_marks=[]))
            continue
        marks = []
        for slot in d.slots:
            sid = slot.subject_id
            # Attend if this occurrence is required to hit remaining need,
            # i.e. remaining occurrences <= remaining need for this subject.
            must_attend = remaining_occurrences[sid] <= remaining_need[sid]
            mark = "Attend" if must_attend else "Skip"
            marks.append(SlotMark(slot=slot, mark=mark))

            remaining_occurrences[sid] -= 1
            if must_attend:
                remaining_need[sid] -= 1
        selections.append(DaySelection(date=d.date, slot_marks=marks))
    return selections
```

### 8.6 `engine/block_consolidation.py` (SRD 15.6)
```python
def consolidate(day_selections: list[DaySelection]) -> list[PlanDayResult]:
    results = []
    for ds in day_selections:
        marks = list(ds.slot_marks)
        changed = True
        while changed:
            changed = False
            for i in range(1, len(marks) - 1):
                if marks[i].mark == "Skip" and marks[i - 1].mark == "Attend" and marks[i + 1].mark == "Attend":
                    marks[i] = replace(marks[i], mark="Attend", forced=True)
                    changed = True
        blocks = _merge_contiguous(marks)   # groups consecutive same-mark slots into PlanBlock ranges
        results.append(PlanDayResult(date=ds.date, blocks=blocks))
    return results
```
`forced=True` on a mark is what drives the "Optional-but-included" sub-status (SRD 15.8 / TOC Section 15.8→15.8 renumbered as 15.8 "Optional Marking") surfaced in the UI as the yellow calendar color.

### 8.7 `engine/explanation_generator.py` (SRD 15.9)
Template lookup keyed by a small enum of reasons (`BELOW_THRESHOLD`, `BLOCK_FORCED`, `SAFELY_ABOVE`, `EVENT_EXCLUDED`), never free-form string concatenation of user data beyond simple `.format()` substitution — keeps output deterministic and testable.

```python
TEMPLATES = {
    "BELOW_THRESHOLD": "{subject} attendance is below the required {min}%. Attend to recover.",
    "BLOCK_FORCED": "{subject} attendance is already sufficient but is included because it lies between required lectures.",
    "SAFELY_ABOVE": "{subject} attendance is safely above threshold ({current}% vs {min}% required); skipping reduces unnecessary campus time.",
    "EVENT_EXCLUDED": "No lectures are planned on this date due to: {event_names}.",
}
```

### 8.8 Orchestration: `engine/pipeline.py`
```python
def generate_plan(semester, subjects, timetable, events, event_types) -> PlanGenerationResult:
    resolved_events = resolve_events(events, event_types)
    calendar_days = expand(semester, timetable, resolved_events)
    requirements = compute_requirements(subjects, calendar_days)
    day_selections = select(calendar_days, {r.subject_id: r for r in requirements})
    plan_days = consolidate(day_selections)
    plan_days = annotate_explanations(plan_days, requirements, calendar_days)
    feasibility = build_feasibility_report(requirements)
    return PlanGenerationResult(plan_days=plan_days, feasibility=feasibility)
```
This is the single function the `plan.py` API route calls; it has zero FastAPI/SQLAlchemy imports, making it directly reusable by a future batch job, CLI tool, or the Section 25 "what-if" simulator (which calls the same pipeline with a mutated single day, without persisting).

---

## 9. API Specification (Detailed)

Base path: `/api/v1`. All bodies are JSON. All list endpoints support no pagination in MVP (data volume per semester is small: ≤ ~40 subjects/slots, ≤ ~150 days).

| Method | Path | Request Body | Response | Status |
|---|---|---|---|---|
| POST | `/semesters` | `SemesterCreate` | `SemesterRead` | 201 |
| GET | `/semesters/{id}` | — | `SemesterRead` | 200 / 404 |
| PUT | `/semesters/{id}` | `SemesterUpdate` | `SemesterRead` | 200 / 404 / 422 |
| POST | `/semesters/{id}/subjects` | `SubjectCreate` | `SubjectRead` | 201 / 404 / 422 |
| PUT | `/subjects/{id}` | `SubjectUpdate` | `SubjectRead` | 200 / 404 / 422 |
| DELETE | `/subjects/{id}` | — | — | 204 / 404 |
| POST | `/semesters/{id}/timetable` | `TimetableSlotCreate` | `TimetableSlotRead` | 201 / 404 / 422 |
| PUT | `/timetable/{id}` | `TimetableSlotUpdate` | `TimetableSlotRead` | 200 / 404 / 422 |
| DELETE | `/timetable/{id}` | — | — | 204 / 404 |
| GET | `/event-types` | — | `list[EventTypeDefinitionRead]` | 200 |
| POST | `/semesters/{id}/events` | `SemesterEventCreate` | `SemesterEventRead` | 201 / 404 / 422 |
| GET | `/semesters/{id}/events` | — | `list[SemesterEventRead]` | 200 / 404 |
| PUT | `/events/{id}` | `SemesterEventUpdate` | `SemesterEventRead` | 200 / 404 / 422 |
| DELETE | `/events/{id}` | — | — | 204 / 404 |
| POST | `/semesters/{id}/plan/generate` | — | `PlanGenerateResponse` | 200 / 404 / 422 (validation pre-check, SRD 19) |
| GET | `/semesters/{id}/plan` | — | `PlanRaw` (days + blocks) | 200 / 404 |
| GET | `/semesters/{id}/plan/calendar` | — | `CalendarViewResponse` | 200 / 404 |
| GET | `/semesters/{id}/plan/daily` | — | `DailyScheduleResponse` | 200 / 404 |
| GET | `/semesters/{id}/plan/subjects` | — | `SubjectViewResponse` | 200 / 404 |
| GET | `/semesters/{id}/plan/dashboard` | — | `DashboardResponse` | 200 / 404 |
| GET | `/semesters/{id}/plan/timeline` | — | `TimelineResponse` | 200 / 404 |
| GET | `/semesters/{id}/export` | — | `SemesterExportBundle` (JSON) | 200 / 404 |
| POST | `/semesters/{id}/import` | `SemesterExportBundle` | `SemesterRead` | 200 / 422 |

### 9.1 Error Response Shape (uniform across all endpoints)
```json
{
  "errors": [
    { "field": "end_date", "message": "end_date must be on or after start_date" }
  ]
}
```
Produced by a FastAPI exception handler registered for `ValidationFailedError` and for Pydantic's native `RequestValidationError`, so both hand-written and schema-level validation failures return the same shape (HTTP 422).

### 9.2 Plan Generation Pre-check (SRD Section 19)
`POST /semesters/{id}/plan/generate` runs, in order, before invoking `engine.pipeline.generate_plan`:
1. Semester exists (404 if not).
2. At least one `Subject` exists (422 if not).
3. At least one `TimetableSlot` exists (422 if not).
4. No overlapping `TimetableSlot`s on the same weekday (422 if violated — should already be prevented at write time, but re-checked defensively).
5. All `SemesterEvent.start_date/end_date` within a sane range (defensive re-check; primary enforcement is at write time per Section 7.1).

If pre-check passes but the engine's feasibility report marks any subject infeasible, the response is still **200 OK** (a generated plan with a warning) — infeasibility is a domain state, not an HTTP error (SRD Edge Cases, Section 17).

---

## 10. Frontend Architecture

### 10.1 Component Tree (abbreviated)
```
App
├── SemesterContext.Provider (holds active semester_id, cached plan data)
├── NavBar (links to all pages, "Recalculate" button when dirty)
├── Routes
│   ├── /setup            → SetupWizard
│   ├── /dashboard         → Dashboard
│   ├── /calendar          → CalendarView (wraps FullCalendar)
│   ├── /daily              → DailyScheduleView
│   ├── /subjects           → SubjectView
│   ├── /timeline            → TimelineView
│   ├── /settings            → SettingsPage
│   ├── /timetable            → TimetableEditor
│   └── /events                 → SemesterEventsManager
```

### 10.2 `SemesterEventsManager.jsx` — key behaviors
- Fetches `GET /event-types` once (cached in context; rarely changes) to populate the type dropdown.
- "Add Semester Event" opens `SemesterEventForm` pre-filled with the selected type's defaults (`default_cancels_lectures`, etc.) shown as toggle switches the user can override — these map directly to the four `*_override` fields, sent as `null` if left untouched (so the backend correctly falls back to type defaults, per Section 8.2's `_coalesce`).
- List view groups/sorts by `start_date`, shows a colored chip per `event_type.label` (or `custom_type_label` when type is "custom"), and an inline "⚠ review defaults" badge for custom-type events whose overrides are still all `null` (SRD Edge Cases 17 / Risks 26).

### 10.3 Data Fetching Pattern
Each `use*` hook wraps Axios calls with a consistent `{ data, isLoading, error, refetch }` shape:
```javascript
function useSemesterEvents(semesterId) {
  const [state, setState] = useState({ data: null, isLoading: true, error: null });
  const refetch = useCallback(async () => {
    setState(s => ({ ...s, isLoading: true }));
    try {
      const { data } = await apiClient.get(`/semesters/${semesterId}/events`);
      setState({ data, isLoading: false, error: null });
    } catch (error) {
      setState({ data: null, isLoading: false, error });
    }
  }, [semesterId]);
  useEffect(() => { refetch(); }, [refetch]);
  return { ...state, refetch };
}
```
No global state library (Redux/Zustand) is needed at MVP scale — `SemesterContext` + per-resource hooks are sufficient given a single active semester and no real-time collaboration.

### 10.4 Calendar View Color Mapping
```javascript
const STATUS_COLOR = {
  Attend: "var(--color-attend-green)",
  Skip: "var(--color-skip-red)",
  OptionalIncluded: "var(--color-optional-yellow)",
  NoLecture: "var(--color-gray-200)",
};
```
Each FullCalendar day-cell renderer reads `plan_day.is_lecture_day` and, if true, the dominant block status for that day (Attend if any block is Attend, else Skip) plus a small dot/badge if any block is `OptionalIncluded`. Days with `is_lecture_day = false` additionally render the covering event name(s) on hover/click, sourced from `plan_day.covering_event_ids` resolved client-side against the already-fetched `SemesterEvent` list.

---

## 11. State Management & Data Flow

```
User edits Semester Events / Timetable / Attendance / Policy
        │
        ▼
 Local form state → API mutation (POST/PUT/DELETE)
        │
        ▼
 SemesterContext marks plan as "stale" (isPlanStale = true)
        │
        ▼
 NavBar shows "Recalculate Plan" as active/highlighted
        │
        ▼
 User clicks Recalculate → POST /plan/generate
        │
        ▼
 On success: refetch all /plan/* view endpoints, isPlanStale = false
```
Automatic recompute-on-every-edit is explicitly deferred (SRD FR-10) — the frontend only ever marks state "stale" and never auto-triggers `/plan/generate`, to avoid surprising API load and to keep the mental model (SRD Section 10, step 4c) matching "explicit recalculate."

---

## 12. Error Handling & Logging

### 12.1 Backend
- All domain exceptions (Section 5.3) are caught by FastAPI exception handlers registered in `main.py` and translated to the uniform error shape (Section 9.1).
- Unhandled exceptions are caught by a catch-all handler that logs the full traceback at `ERROR` level and returns a generic `{"errors": [{"field": null, "message": "Internal server error"}]}` with 500 — never leaking stack traces to the client.
- Structured logging via Python's `logging` module, JSON-formatted in non-local environments (`ENV != "local"`), human-readable in local dev.
- Key log events: plan generation start/end + duration, feasibility warnings, validation failures (at `WARNING`, not `ERROR`, since they're expected user-input issues).

### 12.2 Frontend
- Every `use*` hook surfaces `error` to its consuming page; pages render a dismissible inline error banner (not a full-page crash) using the `errors[]` array from Section 9.1 to show field-level messages next to the relevant form input where applicable.
- A top-level React Error Boundary wraps `<Routes>` to catch render-time exceptions and show a "Something went wrong — reload" fallback, distinct from API error banners.

---

## 13. Security Considerations

Even though MVP has no auth (SRD Non-Goals, Section 5), the following baseline hygiene applies:

- **CORS**: restricted to the known frontend origin(s) via `CORS_ORIGINS` setting; wildcard `*` never used even in local dev beyond `localhost`.
- **Input validation**: every write endpoint validates through Pydantic schemas before touching the DB; no raw SQL string interpolation anywhere (SQLAlchemy ORM/parameterized queries only).
- **SQL injection**: not applicable in practice given ORM-only access, but explicitly disallow any raw `execute()` calls with string-formatted SQL in code review.
- **Rate limiting**: not implemented in MVP (single-user, free-tier hosting); flagged as a pre-requisite before any future multi-user/auth phase (SRD Section 25, Phase 3).
- **Secrets**: `DATABASE_URL` and any future API keys loaded exclusively from environment variables / `.env` (git-ignored), never hardcoded.
- **Export/Import (Section 9)**: `POST /semesters/{id}/import` must validate the uploaded JSON against the same Pydantic schemas as normal writes — never `eval`/`pickle`-deserialize — to prevent malformed or malicious import payloads from corrupting the DB.

---

## 14. Performance Requirements & Complexity Analysis

Restates and grounds SRD Section 8's performance NFR in concrete complexity terms.

- **Calendar Expansion**: O(D × E) where D = days in remaining semester (≤ ~180), E = number of Semester Events (expected ≤ ~30). Well under 10,000 operations.
- **Requirement Calculation**: O(S × D_slots) where S = subjects (≤ ~10), D_slots = total remaining slot occurrences (≤ ~1,000). Trivial.
- **Slot Selection**: O(total remaining slot occurrences), single pass, ≤ ~1,000 operations.
- **Block Consolidation**: O(D × K²) worst case per day for the sandwiched-skip sweep (K = slots per day, typically ≤ 8), but converges in at most K passes; effectively O(D × K) in practice.
- **Overall**: full pipeline is O(D × E + D × K) — comfortably sub-second, satisfying the "<2 seconds" NFR (SRD Section 8) with wide margin even on modest free-tier hardware.
- **DB writes on plan generation**: replace-all strategy (delete existing `PlanDay`/`PlanBlock` rows for the semester, bulk-insert new ones) inside a single transaction, avoiding partial-plan states if generation fails midway.

---

## 15. Configuration & Environment Management

| Variable | Purpose | Local default |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./app.db` |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins | `http://localhost:5173` |
| `ENV` | `local` \| `staging` \| `production` | `local` |
| `LOG_LEVEL` | Python logging level | `INFO` |
| `VITE_API_BASE_URL` (frontend) | Backend base URL the SPA calls | `http://localhost:8000/api/v1` |

`.env.example` checked into the repo for both `backend/` and `frontend/`; actual `.env` files git-ignored.

---

## 16. Local Development Setup

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.db.seed_event_types    # idempotent
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev    # Vite dev server, default port 5173
```

`app.main` also registers an `@app.on_event("startup")` hook that runs `seed_event_types` automatically, so the manual step above is a convenience/CI-friendly fallback, not a hard requirement.

---

## 17. Deployment Architecture

```
GitHub repo (main branch)
   │
   ├── Vercel (auto-deploy on push, frontend/ as root)
   │     → builds via `npm run build`, serves static Vite output
   │     → VITE_API_BASE_URL set to the Render backend URL via Vercel env vars
   │
   └── Render (auto-deploy on push, backend/ as root, Web Service)
         → build: `pip install -r requirements.txt && alembic upgrade head`
         → start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
         → persistent disk mounted for `app.db` (Render free tier supports a small persistent disk;
           if unavailable, document the accepted MVP trade-off that data resets on redeploy — SRD Risk table, Section 26)
```

No containerization (Docker) is required for MVP given Render/Vercel native Python/Node build support, but a `Dockerfile` per service is a low-cost addition if local parity with prod becomes valuable — left as an optional, non-blocking task.

---

## 18. CI/CD Pipeline

`.github/workflows/ci.yml` (conceptual):
```yaml
on: [push, pull_request]
jobs:
  backend:
    steps:
      - checkout
      - setup-python (3.11)
      - pip install -r backend/requirements.txt
      - ruff check backend/
      - black --check backend/
      - pytest backend/tests --cov=backend/app
  frontend:
    steps:
      - checkout
      - setup-node (20)
      - npm ci --prefix frontend
      - npm run lint --prefix frontend
      - npm run test --prefix frontend
      - npm run build --prefix frontend
```
Deployment itself is handled by Vercel/Render's native GitHub integration (auto-deploy on merge to `main`), not by the GitHub Actions workflow — CI's job is strictly gatekeeping (lint + test + build must pass before merge is allowed via branch protection).

---

## 19. Testing Strategy (Technical)

Expands SRD Section 29 with concrete technical targets:

| Test Layer | Tooling | Target Coverage / Focus |
|---|---|---|
| Engine unit tests | pytest | 100% of `engine/*.py` branch coverage; canonical fixture = the DBMS(62%)/OS(90%)/Maths(64%)/EFM(95%) example from the SRD, asserted to produce exactly `Attend 9–12, Skip EFM`. |
| Event resolution unit tests | pytest | Every combination of override-present vs. override-null against every preset; multi-event overlap conflict resolution (most-restrictive-wins) per flag independently. |
| Validation unit tests | pytest | One test per rule in SRD Section 19 (both pass and fail cases). |
| API integration tests | pytest + FastAPI TestClient | Full CRUD + plan-generation round trip per resource, against a temp SQLite DB created/torn down per test module. |
| Edge case regression | pytest | One test per row in SRD Section 17, including the newly added Semester Event edge cases. |
| Frontend component tests | Vitest + RTL | `SemesterEventForm` default-prefill-from-type behavior; `CalendarView` color-coding given a mocked `/plan/calendar` response; `SemesterEventsManager` "review defaults" badge logic. |
| Frontend integration (light) | Vitest + RTL + msw (mock service worker) | Setup Wizard step validation gating "Next" correctly per SRD Section 19 rules. |
| Manual exploratory | — | Full walkthrough per SRD Section 10 using Persona 1 and Persona 4 data before each milestone sign-off (unchanged from SRD). |

CI enforces: engine + validation unit tests must pass with no skips before any merge to `main`; API/frontend integration tests run on every PR but a documented flaky-test quarantine process may apply post-MVP if free-tier CI minutes become constrained.

---

## 20. Coding Standards & Conventions

- **Python**: `black` formatting (line length 100), `ruff` for linting (imports, unused vars, complexity). Type hints required on all `engine/` and `models/` code; `schemas/` inherits typing from Pydantic. Docstrings required on all public `engine/*.py` functions, describing inputs/outputs in terms of the SRD section they implement (e.g., `"""Implements SRD Section 15.6 — Block Consolidation."""`).
- **JavaScript/React**: functional components only, hooks-based state, no default exports for shared utilities (named exports only) to keep refactors/AI-assisted edits unambiguous. Props destructured in the function signature, not inside the body.
- **Naming**: backend module/file names mirror SRD entity names (`semester_event.py`, not `events.py`) to keep the SRD-to-code mapping obvious for future AI-assisted work.
- **Commits**: Conventional Commits style (`feat:`, `fix:`, `test:`, `docs:`) to keep milestone-based history (SRD Section 28) legible.
- **No magic numbers**: attendance math constants (e.g., default subject percentage fallback) live in `core/config.py` or as named constants in `engine/types.py`, never inlined.

---

## 21. Dependency Manifest

### Backend (`requirements.txt`, indicative)
```
fastapi
uvicorn[standard]
sqlalchemy>=2.0
alembic
pydantic>=2.0
pydantic-settings
python-dateutil
pytest
pytest-cov
httpx            # required by FastAPI TestClient
ruff
black
```

### Frontend (`package.json`, indicative)
```
react
react-dom
react-router-dom
vite
tailwindcss
postcss
autoprefixer
axios
chart.js
react-chartjs-2
@fullcalendar/react
@fullcalendar/daygrid
vitest
@testing-library/react
msw
eslint
prettier
```

All packages MIT/Apache/BSD-licensed per SRD Constraint (Section 18) — license check is a CI-addable step (`pip-licenses`, `license-checker`) if desired, not blocking for MVP.

---

## 22. Technical Risks & Mitigations

| Risk | Technical Impact | Mitigation |
|---|---|---|
| SQLite file loss on Render redeploy (no persistent disk on lowest free tier) | Full data loss between deploys | Document clearly in README; provide `/export` and `/import` (Section 9) as a manual backup workflow; evaluate Render's paid persistent disk only if this becomes a real pain point — stays free-tier by default via user-driven export. |
| `subject_ids` stored as JSON string in SQLite | Slightly awkward querying (can't index into the array via SQL) | Acceptable at MVP scale (≤ ~10 subjects per block); documented as a known limitation; PostgreSQL migration (SRD Section 22) can move this to a native `JSONB` or a proper join table if needed later. |
| Event resolution "most-restrictive-wins" logic diverges subtly from user expectation for complex overlaps | Confusing plan output | Section 8.3's per-flag resolution is unit-tested exhaustively (Section 19) and the Calendar View always shows *which* events cover a given excluded day, making the resolution auditable rather than opaque. |
| Free-tier backend cold starts (Render sleep) | Slow first request after idle | Documented as an accepted MVP trade-off (matches SRD Risk table, Section 26); a simple frontend loading state covers the UX gap. |
| Engine correctness regressions during future refactors (e.g., OR-Tools swap-in) | Silent plan-quality degradation | The DBMS/OS/Maths/EFM fixture (Section 19) is a permanent, framework-agnostic regression test that any alternate engine implementation must also pass before being swapped in behind `engine/pipeline.py`'s interface. |

---

## 23. Traceability Matrix (SRD → TRD)

| SRD Section | TRD Section(s) |
|---|---|
| 7 Functional Requirements | 5, 6, 7, 8, 9 |
| 13 Data Models | 6 |
| 14 Database Schema | 6 |
| 15 Recommendation Engine Design | 8 |
| 16 Optimization Rules | 8.5, 8.6 |
| 17 Edge Cases | 8.3–8.6, 19 |
| 19 Validation Rules | 7.1, 9.2 |
| 20 UI Screens | 10 |
| 21 Navigation Flow | 10.1, 11 |
| 22 Technology Stack | 3 |
| 23 Folder Structure | 4 |
| 24 API Endpoints | 9 |
| 26 Risks | 22 |
| 29 Testing Strategy | 19 |

---

## 24. Appendix: Sample Payloads

### 24.1 Create a Semester Event (accepting type defaults)
```json
POST /semesters/12/events
{
  "name": "Mid Semester 1",
  "event_type_id": 2,
  "start_date": "2026-08-18",
  "end_date": "2026-08-23",
  "description": "First internal examination week"
}
```
Response:
```json
{
  "id": 41,
  "semester_id": 12,
  "name": "Mid Semester 1",
  "event_type_id": 2,
  "custom_type_label": null,
  "start_date": "2026-08-18",
  "end_date": "2026-08-23",
  "description": "First internal examination week",
  "cancels_lectures_override": null,
  "counts_towards_attendance_override": null,
  "is_working_day_override": null,
  "exclude_from_recommendation_override": null,
  "resolved_cancels_lectures": true,
  "resolved_counts_towards_attendance": false,
  "resolved_is_working_day": true,
  "resolved_exclude_from_recommendation": true
}
```

### 24.2 Create a Custom Semester Event (overriding defaults)
```json
POST /semesters/12/events
{
  "name": "Department Hackathon",
  "event_type_id": 12,
  "custom_type_label": "Hackathon",
  "start_date": "2026-09-10",
  "end_date": "2026-09-11",
  "cancels_lectures_override": true,
  "counts_towards_attendance_override": true,
  "exclude_from_recommendation_override": true
}
```

### 24.3 Plan Generation Response (feasibility warning example)
```json
{
  "semester_id": 12,
  "generated_at": "2026-07-04T10:15:00Z",
  "total_plan_days": 96,
  "total_attend_blocks": 132,
  "total_skip_blocks": 40,
  "overall_feasible": false,
  "subject_feasibility": [
    {
      "subject_id": 3,
      "subject_name": "DBMS",
      "required_percentage": 70.0,
      "best_achievable_percentage": 66.4,
      "is_feasible": false
    }
  ]
}
```

---

*End of Technical Requirements Document. Implement per the milestone order in SRD Section 28, using this document's module boundaries (Section 4–8) as the concrete file/function targets for each milestone.*
