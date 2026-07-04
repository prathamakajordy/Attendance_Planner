# Software Requirements Document (SRD)
## Attendance Planner AI

**Tagline:** Plan your semester intelligently. Attend only when necessary. Never fall below the required attendance.

**Document Version:** 1.0
**Prepared For:** Solo student developer, zero-budget build
**Prepared As:** Implementation-ready specification for AI coding assistants (Claude, Cursor, Antigravity, Gemini, etc.)

---

## Table of Contents

1. Executive Summary
2. Vision
3. Problem Statement
4. Goals
5. Non-Goals
6. User Personas
7. Functional Requirements
8. Non-Functional Requirements
9. User Stories
10. Complete User Flow
11. System Workflow
12. Feature Breakdown
13. Data Models
14. Database Schema
15. Recommendation Engine Design
16. Optimization Rules
17. Edge Cases
18. Constraints
19. Validation Rules
20. UI Screens
21. Navigation Flow
22. Technology Stack
23. Folder Structure
24. API Endpoints
25. Future Roadmap
26. Risks
27. Assumptions
28. Development Milestones
29. Testing Strategy
30. MVP Scope vs Future Scope

---

## 1. Executive Summary

Attendance Planner AI is a web-based attendance optimization system for college students. Unlike conventional attendance trackers that only report a percentage, this system computes an actionable, day-by-day and lecture-block-by-lecture-block schedule telling the student **exactly which days to attend, which continuous blocks of lectures to sit through, and which lectures are safe to skip** — while guaranteeing that both subject-wise and overall attendance policies are never violated.

The system is built and deployable at **zero cost**, using only free, open-source software. It is designed and coded by a single student developer, and is architected so that an AI coding assistant can implement it module-by-module directly from this document.

The core innovation is **block-based optimization**: the system never recommends attending or skipping individual isolated lectures in a way that would require a student to physically leave and re-enter a classroom mid-session. It reasons over continuous time blocks on a given day and produces schedules that are realistic for a human to execute.

The MVP is a rules-and-algorithms-driven planner (no LLMs, no external AI APIs) that takes manually entered timetable, attendance, and calendar data and produces a recommended plan visualized through a calendar, daily schedule, subject-wise view, dashboard, and semester timeline — each recommendation accompanied by a plain-language explanation.

---

## 2. Vision

To become the de-facto lightweight, free, open-source tool that any engineering (or general) college student can self-host or run locally to stop guessing about attendance and instead follow a concrete, algorithmically optimal, practically executable plan for the rest of the semester.

Long-term, the system should generalize beyond a single manual-entry MVP into a tool that can ingest a college's academic calendar and timetable automatically (via document upload and OCR), predict future attendance trajectories, and simulate "what-if" scenarios — without ever requiring the user to pay for anything or depend on a proprietary AI API.

---

## 3. Problem Statement

Existing attendance apps (and most college ERPs) stop at reporting: current percentage, classes held, classes attended, and a generic "you can miss N more classes" counter. They do not answer the question a student actually has:

> "Given my current attendance in every subject, my remaining timetable, and my remaining semester dates (including holidays and exams), exactly which days should I physically go to college, and which specific block of lectures should I sit through, in order to guarantee I meet every attendance rule while minimizing wasted time and unnecessary trips to campus?"

This is a **scheduling and optimization problem**, not a reporting problem. Attendance Planner AI treats it as such: it models the remaining semester as a sequence of days, each composed of lecture slots grouped into contiguous blocks, and computes a plan that satisfies hard constraints (attendance floors) while optimizing soft objectives (fewer visits, fewer campus-hours, no isolated skips inside a block).

---

## 4. Goals

- Let a student configure arbitrary attendance policies (overall % and per-subject %) rather than hardcoding 75%/70%.
- Accept a full weekly timetable and per-subject held/present counts as manual input.
- Accept semester start/end dates and a list of non-lecture days (holidays, exams, fests, visits, personal leave).
- Compute, for every remaining lecture day in the semester, a recommendation of **Attend** / **Skip** / **Optional**, grouped into continuous blocks, never isolated single lectures inside an attendable block.
- Guarantee (subject to feasibility) that the recommended plan keeps every subject and the overall percentage at or above the configured minimums by the end of the semester.
- Present the same underlying plan through five different views: Calendar, Daily Schedule, Subject View, Dashboard, Semester Timeline.
- Generate a human-readable explanation for every recommendation.
- Ship an MVP that runs entirely on free/open-source infrastructure with no paid APIs, no LLM dependency, and no subscription services.
- Structure the codebase so each feature/module can be implemented independently by an AI coding assistant using this document as its spec.

---

## 5. Non-Goals

- This is **not** a general-purpose attendance tracking / register app for teachers or institutions.
- This is **not** an AI chatbot. There is no conversational interface in the MVP.
- This is **not** a simple percentage calculator — recommendation and scheduling logic is the core value, not a side feature.
- The MVP will **not** perform OCR, PDF parsing, or automatic timetable/calendar extraction.
- The MVP will **not** include login/auth, multi-user accounts, or cloud sync.
- The MVP will **not** send notifications or push reminders.
- The system will **not** depend on OpenAI, Gemini, or any other paid/metered LLM API at any point in the MVP or near-term roadmap.
- The system will **not** attempt to model real-time GPS/location or biometric attendance capture.

---

## 6. User Personas

**Persona 1 — "Borderline Rahul" (Primary)**
Third-year engineering student. Attendance hovers around 70–75% in two subjects. Anxious about detention/debarment from exams. Wants a concrete plan, not a percentage. Checks the app weekly.

**Persona 2 — "Efficient Priya" (Secondary)**
Attendance is comfortably above every threshold. Wants to minimize time on campus (long commute) while staying safe. Wants the dashboard/subject view to confirm she can skip more.

**Persona 3 — "Planner Aman" (Secondary)**
Likes to plan the whole semester in advance around internships, hackathons, and travel. Uses the Semester Timeline view heavily and marks personal vacation days in advance to see if the remaining plan is still feasible.

**Persona 4 — "New Student Zara" (Edge case persona)**
Just joined; has almost no attendance history yet (0 or very few classes held). Needs the system to behave sensibly with near-empty data and not produce absurd or infeasible recommendations.

---

## 7. Functional Requirements

### FR-1 Attendance Policy Configuration (MVP)
The user can set a minimum overall attendance percentage and a minimum per-subject attendance percentage. These are stored per semester profile and used as hard constraints in the recommendation engine.

### FR-2 Semester Setup (MVP)
The user can enter a semester start date and end date. The system derives the full calendar range and, combined with the timetable and Semester Events (Section 13.1), generates the list of actual lecture-bearing days remaining.

### FR-3 Weekly Timetable Entry (MVP)
The user can define, per weekday (Mon–Sat/Sun as applicable), an ordered list of lecture slots, each with subject name, start time, and end time. The timetable is treated as recurring every week within the semester unless overridden by a Semester Event whose resolved flags cancel or exclude lectures on a given date (Section 13.1).

### FR-4 Attendance Data Entry (MVP)
For each subject, the user enters either (a) classes held and classes present, or (b) a current percentage directly. Held/Present is preferred internally; if only a percentage is given, the system asks for at least an assumed "held" count or defaults to a configurable assumed value so future math is consistent (see Edge Cases).

### FR-5 Semester Events Module (MVP) — *supersedes fixed Holiday/Mid-Sem/End-Sem/Fest fields*
Instead of a fixed set of predefined date fields, the user manages an **unlimited, user-defined list of Semester Events** via a single "Semester Events" page and an "Add Semester Event" action. Each event has a name, an event type (chosen from an extensible preset list or a fully custom label), a start date, an end date, an optional description, and a set of **attendance-impact flags** (Section 13.1) that determine how it affects lecture scheduling and attendance calculations. There is no cap on the number of events a user can create, and no college-specific structure (one mid-sem vs. three, presence or absence of a fest, etc.) is hardcoded — the calendar model is entirely event-driven.

### FR-5a Event Type Presets (MVP)
The system ships with a preset list of common event types (Holiday, Examination, Practical Examination, College Event, Technical Fest, Cultural Fest, Sports Event, Industrial Visit, Placement Activity, Vacation, Reading Week, Other/Custom), each carrying sensible **default** attendance-impact flags that the user can accept or override per event instance. Presets are stored as data, not hardcoded logic (Section 13.1), so new types can be added later without a schema change.

### FR-5b Custom Event Types (MVP)
When "Other/Custom" is selected, the user supplies a free-text custom type label. The event still requires the same attendance-impact flags to be set (defaulted conservatively, see Section 13.1) so the recommendation engine can treat it consistently with preset types.

### FR-5c Attendance-Impact-Driven Engine Behavior (MVP)
The recommendation engine never branches on an event's name or type string. It only reads four boolean properties resolved per event (Section 13.1: `cancels_lectures`, `counts_towards_attendance`, `is_working_day`, `exclude_from_recommendation`). This keeps the engine future-proof: any current or future event type — "Mid Sem," "Hackathon," "Department Farewell" — is handled identically as long as its impact flags are set.

### FR-6 Recommendation Engine (MVP)
Given policy, timetable, current attendance, and remaining calendar, the system computes a full remaining-semester plan: for every remaining lecture day, which continuous block(s) to attend and which to skip, such that projected end-of-semester attendance meets all configured minimums, subject to feasibility.

### FR-7 Block-Based Scheduling Rule (MVP)
The recommendation engine must never recommend a non-contiguous attendance pattern within a single day if doing so would require leaving and re-entering a classroom (i.e., skipping a lecture sandwiched between two "attend" lectures is disallowed; the sandwiched lecture is auto-upgraded to "attend" as part of block formation).

### FR-8 Explanation Engine (MVP)
Every day-level and block-level recommendation is accompanied by a short, human-readable reason string generated from a deterministic template engine (not an LLM) referencing the actual numeric drivers (e.g., "DBMS attendance is below threshold at 62%").

### FR-9 Multi-View Output (MVP)
The same computed plan is renderable as: Calendar View (color-coded), Daily Schedule View, Subject View, Dashboard View, and Semester Timeline View.

### FR-10 Recompute on Data Change (MVP)
Any change to attendance data, policy, timetable, or Semester Events triggers a recompute of the plan (manually triggered via a "Recalculate" action in MVP; automatic recompute is a fast-follow, not blocking MVP).

### FR-11 Academic Calendar Upload (Future, Post-MVP)
Upload a PDF; extract semester dates, holidays, exam windows, and events automatically.

### FR-12 Timetable Upload via OCR (Future, Post-MVP)
Upload an image/PDF of a timetable; extract subjects and time slots automatically.

### FR-13 Authentication & Multi-Semester Support (Future)
Login, saved user accounts, multiple semester profiles, history across semesters.

### FR-14 Cloud Sync & Notifications (Future)
Sync data across devices; send reminders ("Attend today 9–12").

### FR-15 Scenario Simulation (Future)
"What if I skip tomorrow?" — ad hoc single-change projections without committing to the plan.

---

## 8. Non-Functional Requirements

| Category | Requirement |
|---|---|
| Cost | Entire stack must run on free tiers / local machine. Zero recurring cost. |
| Performance | Full-semester recomputation (≈120 days × ~6 slots/day) must complete in well under 2 seconds on commodity hardware. |
| Portability | Backend and frontend must run locally with a single `pip install` / `npm install` and minimal setup steps. |
| Data Ownership | All data stored locally (SQLite file) in MVP; no third-party data sharing. |
| Usability | A student should be able to complete first-time setup (policy + timetable + attendance) in under 10 minutes. |
| Maintainability | Codebase organized into clearly separated modules (input, storage, engine, API, UI) so an AI coding assistant can regenerate or extend any one module without touching others. |
| Extensibility | Recommendation engine must be swappable/upgradable (e.g., adding OR-Tools-based solving) without changing the API contract. |
| Reliability | Engine must never silently produce a plan that violates a hard constraint; if infeasible, it must explicitly report infeasibility rather than returning a false "safe" plan. |
| Accessibility | Color-coded calendar view must not rely on color alone — include text/icon labels for Attend/Skip/Optional. |

---

## 9. User Stories

1. As a student, I want to enter my attendance policy once so that the app uses my college's actual rules instead of generic defaults.
2. As a student, I want to enter my weekly timetable once so that the app understands my recurring schedule.
3. As a student, I want to enter held/present counts per subject so that the app knows my real standing.
4. As a student, I want to mark holidays and exam dates so that the plan doesn't assume lectures happen then.
5. As a student, I want the app to tell me exactly which continuous block of hours to attend on a given day, not a scattered list of individual lectures.
6. As a student, I want to see why a recommendation was made, so I trust and understand it.
7. As a student, I want a calendar view so I can see my whole semester at a glance.
8. As a student, I want a dashboard showing current vs. required attendance and how many safe skips I have left.
9. As a student, I want a subject-wise view so I know exactly how many more lectures of a specific subject I must attend.
10. As a student, I want to recalculate the plan whenever my actual attendance changes (e.g., I skipped something unplanned).
11. As a student, I want the system to warn me clearly if my attendance goal has become mathematically infeasible for a subject.
12. As a new student with little data, I want the app to still produce a sensible plan rather than crashing or giving nonsense output.

---

## 10. Complete User Flow

1. **First-time setup**
   a. Enter semester start date and end date.
   b. Enter attendance policy (overall %, subject %).
   c. Build weekly timetable (per weekday, add lecture slots with subject/start/end).
   d. Enter current attendance per subject (held/present, or percentage fallback).
   e. Add Semester Events as needed (click "Add Semester Event" repeatedly) — choose a preset type or a custom type, set dates, and confirm/override the attendance-impact flags. Events can be added incrementally at any point in the semester, not just during setup.
2. **Generate Plan**
   a. User clicks "Generate Plan."
   b. Backend runs the recommendation engine over the remaining semester.
   c. Plan + explanations returned and cached.
3. **Explore Plan**
   a. User lands on Dashboard (overview).
   b. User can switch to Calendar, Daily Schedule, Subject View, or Semester Timeline — all reflecting the same underlying plan.
4. **Ongoing Use**
   a. Each day/week, user updates actual held/present counts (what they actually did) if it diverged from the plan.
   b. User adds any new Semester Events as they arise (a sudden holiday, a newly announced placement drive, etc.).
   c. User clicks "Recalculate" to refresh the plan.
5. **Edge Handling**
   a. If a subject/overall target becomes infeasible, the Dashboard and Subject View surface a clear warning with the best-achievable percentage instead of a false guarantee.

---

## 11. System Workflow

```
[User Input Layer]
   Semester Dates, Policy, Timetable, Attendance, Semester Events
            |
            v
[Validation Layer]
   Schema + business rule validation (see Section 19)
            |
            v
[Event Resolution Module]
   Resolves each Semester Event's effective attendance-impact flags
   (event-level override, falling back to its Event Type's defaults)
            |
            v
[Calendar Expansion Module]
   Expands semester date range x weekly timetable
   -> list of (date, weekday, [lecture slots]) adjusted per resolved
      event flags: cancels_lectures removes slots, exclude_from_recommendation
      removes the date from the planning search space, is_working_day and
      counts_towards_attendance annotate the day for engine and UI use
            |
            v
[Recommendation Engine]
   1. Compute remaining lecture counts per subject
   2. Compute minimum lectures-to-attend per subject to hit target
   3. For each remaining day: propose attend/skip per slot
   4. Apply Block Consolidation (merge sandwiched skips into attends)
   5. Apply optimization priorities (see Section 16)
   6. Validate resulting projected percentages against policy
            |
            v
[Explanation Generator]
   Template-based reason strings per day/block
            |
            v
[Plan Store / Cache]
   Persisted computed plan (SQLite) tied to semester profile
            |
            v
[View Adapters]
   Calendar / Daily / Subject / Dashboard / Timeline transformers
            |
            v
[Frontend Rendering]
```

---

## 12. Feature Breakdown

| Feature | MVP or Future |
|---|---|
| Policy configuration (overall + subject %) | MVP |
| Semester date range setup | MVP |
| Weekly timetable builder | MVP |
| Manual attendance entry (held/present or %) | MVP |
| Semester Events module (unlimited, type-driven, custom types) | MVP |
| Event Type presets with editable default attendance-impact flags | MVP |
| Block-based recommendation engine | MVP |
| Explanation engine (template-based) | MVP |
| Calendar view | MVP |
| Daily schedule view | MVP |
| Subject view | MVP |
| Dashboard view | MVP |
| Semester timeline view | MVP |
| Manual recalculation trigger | MVP |
| Infeasibility detection & warning | MVP |
| Data export (JSON/CSV backup of inputs) | MVP (lightweight) |
| Academic calendar PDF upload/extraction | Future |
| Timetable OCR upload | Future |
| User authentication | Future |
| Multiple semesters / history | Future |
| Cloud sync | Future |
| Notifications/reminders | Future |
| Mobile PWA packaging | Future |
| Daily push-style recommendations | Future |
| Attendance prediction (trend modeling) | Future |
| "What if I skip tomorrow?" simulator | Future |
| OR-Tools-based constrained solver upgrade | Future (engine v2) |

---

## 13. Data Models

### SemesterProfile
- `id`
- `name` (e.g., "Sem IV 2026")
- `start_date`
- `end_date`
- `min_overall_percentage`
- `min_subject_percentage` (default; can be overridden per subject)
- `created_at`, `updated_at`

### Subject
- `id`
- `semester_id` (FK)
- `name`
- `code` (optional)
- `min_percentage_override` (nullable — overrides semester default)
- `held_count`
- `present_count`

### TimetableSlot
- `id`
- `semester_id` (FK)
- `subject_id` (FK)
- `weekday` (0–6)
- `start_time`
- `end_time`
- `order_index` (position within the day, for block adjacency logic)

### 13.1 Design Note: Why Events Replace Fixed Fields

Earlier revisions of this SRD modeled the calendar using a fixed `ExceptionDate` entity with a closed `type` enum (Holiday, MidSem, EndSem, Festival, IndustrialVisit, Event, PersonalVacation). This does not generalize: colleges differ in how many internal exams they run, whether they hold practical exam weeks, reading weeks, placement drives, hackathons, department-specific events, etc.

This is replaced by a **Semester Events module** built on two entities:

- **EventTypeDefinition** — a reference table of event *types* (presets + custom), each carrying **default** attendance-impact flags. New types are added by inserting a row, never by changing code or the schema.
- **SemesterEvent** — a user-created event instance (unlimited per semester), referencing an `EventTypeDefinition` and optionally overriding its default flags.

The recommendation engine and calendar expansion logic (Section 15) only ever read four **resolved boolean flags** per event — never the event's name or type label — which is what makes the design future-proof: any event, existing or not-yet-invented, is handled identically as long as its flags are set.

**The four attendance-impact flags:**

| Flag | Question it answers | Effect on planning |
|---|---|---|
| `cancels_lectures` | Does this event cancel regular timetable lectures? | If true, no `TimetableSlot` occurrences are generated for dates within the event's range. |
| `counts_towards_attendance` | Does attendance count during this event (e.g., an official industrial visit marked present by default)? | If true and lectures are not cancelled, the day's slots are still included in percentage math; if lectures are cancelled, this flag can still mark the day as an automatic "present" credit for affected subjects (configurable, MVP defaults to no auto-credit unless explicitly set). |
| `is_working_day` | Is the day considered an official working/college day at all? | Metadata used for calendar display and future institutional-calendar sync; does not by itself cancel lectures. |
| `exclude_from_recommendation` | Should the recommendation engine skip generating a plan for these dates? | If true, the date is removed from the engine's planning search space entirely (no PlanDay/PlanBlock generated), regardless of the other three flags. |

A flag's **effective value** for a given event = the event's own override if set, otherwise its `EventTypeDefinition`'s default.

### EventTypeDefinition
- `id`
- `key` (unique slug, e.g. `holiday`, `examination`, `custom`)
- `label` (display name)
- `is_system_preset` (bool — distinguishes shipped presets from ones added later)
- `default_cancels_lectures` (bool)
- `default_counts_towards_attendance` (bool)
- `default_is_working_day` (bool)
- `default_exclude_from_recommendation` (bool)

### SemesterEvent
- `id`
- `semester_id` (FK)
- `event_type_id` (FK → EventTypeDefinition)
- `custom_type_label` (nullable — required when `event_type` = "Other/Custom")
- `name` (e.g., "Mid Semester 1", "Technical Fest", "Department Hackathon")
- `start_date`
- `end_date`
- `description` (optional)
- `cancels_lectures_override` (nullable bool)
- `counts_towards_attendance_override` (nullable bool)
- `is_working_day_override` (nullable bool)
- `exclude_from_recommendation_override` (nullable bool)
- `created_at`, `updated_at`

### PlanDay
- `id`
- `semester_id` (FK)
- `date`
- `weekday`
- `is_lecture_day` (bool)
- `blocks` (list of PlanBlock, serialized or child table)
- `day_explanation`

### PlanBlock
- `id`
- `plan_day_id` (FK)
- `start_time`
- `end_time`
- `subject_ids` (list, in order)
- `recommendation` (Attend | Skip | Optional)
- `block_explanation`

### PlanSlotOutcome (for post-hoc reconciliation of actual vs. planned)
- `id`
- `plan_block_id` (FK, nullable if unplanned event)
- `subject_id` (FK)
- `date`
- `actual_status` (Attended | Skipped | Cancelled | Unknown)

---

## 14. Database Schema (SQLite, MVP)

```sql
CREATE TABLE semester_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    min_overall_percentage REAL NOT NULL,
    min_subject_percentage REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE subject (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    semester_id INTEGER NOT NULL REFERENCES semester_profile(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    code TEXT,
    min_percentage_override REAL,
    held_count INTEGER NOT NULL DEFAULT 0,
    present_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE timetable_slot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    semester_id INTEGER NOT NULL REFERENCES semester_profile(id) ON DELETE CASCADE,
    subject_id INTEGER NOT NULL REFERENCES subject(id) ON DELETE CASCADE,
    weekday INTEGER NOT NULL CHECK (weekday BETWEEN 0 AND 6),
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    order_index INTEGER NOT NULL
);

-- Reference table of event types (presets + custom). New types are added
-- as rows, never as schema/code changes, which is what keeps the calendar
-- model future-proof.
CREATE TABLE event_type_definition (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    label TEXT NOT NULL,
    is_system_preset BOOLEAN NOT NULL DEFAULT 0,
    default_cancels_lectures BOOLEAN NOT NULL DEFAULT 1,
    default_counts_towards_attendance BOOLEAN NOT NULL DEFAULT 0,
    default_is_working_day BOOLEAN NOT NULL DEFAULT 1,
    default_exclude_from_recommendation BOOLEAN NOT NULL DEFAULT 1
);

-- Seeded presets (illustrative; exact defaults are editable by the user
-- per-event via the *_override columns below):
-- ('holiday', 'Holiday', 1, cancels=1, counts=0, working=0, exclude=1)
-- ('examination', 'Examination', 1, cancels=1, counts=0, working=1, exclude=1)
-- ('practical_examination', 'Practical Examination', 1, cancels=1, counts=0, working=1, exclude=1)
-- ('college_event', 'College Event', 1, cancels=1, counts=0, working=1, exclude=1)
-- ('technical_fest', 'Technical Fest', 1, cancels=1, counts=0, working=1, exclude=1)
-- ('cultural_fest', 'Cultural Fest', 1, cancels=1, counts=0, working=1, exclude=1)
-- ('sports_event', 'Sports Event', 1, cancels=1, counts=0, working=1, exclude=1)
-- ('industrial_visit', 'Industrial Visit', 1, cancels=1, counts=1, working=1, exclude=1)
-- ('placement_activity', 'Placement Activity', 1, cancels=1, counts=1, working=1, exclude=1)
-- ('vacation', 'Vacation', 1, cancels=1, counts=0, working=0, exclude=1)
-- ('reading_week', 'Reading Week', 1, cancels=1, counts=0, working=1, exclude=1)
-- ('custom', 'Other / Custom', 1, cancels=1, counts=0, working=1, exclude=1)

CREATE TABLE semester_event (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    semester_id INTEGER NOT NULL REFERENCES semester_profile(id) ON DELETE CASCADE,
    event_type_id INTEGER NOT NULL REFERENCES event_type_definition(id),
    custom_type_label TEXT,          -- required when event_type_id = 'custom'
    name TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    description TEXT,
    cancels_lectures_override BOOLEAN,             -- NULL = inherit type default
    counts_towards_attendance_override BOOLEAN,    -- NULL = inherit type default
    is_working_day_override BOOLEAN,               -- NULL = inherit type default
    exclude_from_recommendation_override BOOLEAN,  -- NULL = inherit type default
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CHECK (end_date >= start_date)
);

CREATE TABLE plan_day (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    semester_id INTEGER NOT NULL REFERENCES semester_profile(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    weekday INTEGER NOT NULL,
    is_lecture_day BOOLEAN NOT NULL,
    day_explanation TEXT
);

CREATE TABLE plan_block (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_day_id INTEGER NOT NULL REFERENCES plan_day(id) ON DELETE CASCADE,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    subject_ids TEXT NOT NULL,          -- JSON array of subject ids, ordered
    recommendation TEXT NOT NULL CHECK (recommendation IN ('Attend','Skip','Optional')),
    block_explanation TEXT
);

CREATE TABLE plan_slot_outcome (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_block_id INTEGER REFERENCES plan_block(id) ON DELETE SET NULL,
    subject_id INTEGER NOT NULL REFERENCES subject(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    actual_status TEXT NOT NULL CHECK (actual_status IN
        ('Attended','Skipped','Cancelled','Unknown'))
);

CREATE INDEX idx_timetable_semester ON timetable_slot(semester_id, weekday);
CREATE INDEX idx_semester_event_semester_dates ON semester_event(semester_id, start_date, end_date);
CREATE INDEX idx_plan_day_semester_date ON plan_day(semester_id, date);
```

---

## 15. Recommendation Engine Design

### 15.1 Inputs
- SemesterProfile (dates, policy)
- Subjects with held/present counts
- TimetableSlots (recurring weekly)
- SemesterEvents, each resolved to its four effective attendance-impact flags (Section 13.1)

### 15.2 Step 1 — Event Resolution
For every `SemesterEvent`, compute its **effective flags** by taking each `*_override` column if non-null, else falling back to the linked `EventTypeDefinition`'s default. This produces, for each event, a resolved `(cancels_lectures, counts_towards_attendance, is_working_day, exclude_from_recommendation)` tuple used by every downstream step. The engine never inspects `name`, `event_type`, or `custom_type_label` for decision-making — only the resolved flags.

### 15.3 Step 2 — Calendar Expansion
Expand `start_date`→`end_date` into individual dates. For each date, look up weekday and attach the matching `TimetableSlot`s. Then, for each date that falls inside one or more `SemesterEvent` ranges:
- If any covering event has `exclude_from_recommendation = true`, mark the date `is_lecture_day = false` and produce no `PlanBlock`s (regardless of the other flags) — this is the primary mechanism that keeps the date out of the engine's search space, replacing the old fixed "exception date" behavior.
- Else if any covering event has `cancels_lectures = true`, remove that event's overlapping `TimetableSlot` occurrences for that date before block generation.
- The resolved `counts_towards_attendance` and `is_working_day` values are attached to the `PlanDay` record as metadata for UI display and for the Explanation Engine, and for future attendance-crediting logic (Section 17).
- If two or more events overlap the same date with conflicting resolved flags, the **more restrictive** value wins for each flag independently (e.g., `exclude_from_recommendation = true` from any one event overrides `false` from another; see Edge Cases, Section 17).

### 15.4 Step 3 — Remaining Requirement Calculation
For each subject `s`:
```
required_min = subject.min_percentage_override or semester.min_subject_percentage
total_future_lectures(s) = count of s's slots across all remaining lecture days
worst_case_final_held(s) = held_count(s) + total_future_lectures(s)
```
Determine the **minimum number of future lectures of `s` the student must attend** (`need_attend(s)`) such that:
```
(present_count(s) + attended_future) / (held_count(s) + total_future_lectures(s)) >= required_min / 100
```
Solve for the smallest integer `attended_future` satisfying this. If `attended_future > total_future_lectures(s)`, the subject target is **infeasible**; flag it and compute the best achievable percentage (attend all remaining).

The same calculation is done in aggregate for the overall percentage (all subjects combined), producing `need_attend_overall`.

### 15.5 Step 4 — Greedy Slot Selection with Deficit Priority
For each remaining day, for each slot in order:
- Compute each subject's **current deficit score** = `required_min - projected_running_percentage`.
- Mark a slot's subject as "must-attend-soon" if attending it is necessary to keep `need_attend(s)` achievable given remaining occurrences (i.e., the number of remaining occurrences of `s` equals or is close to `need_attend(s)` remaining).
- Slots for subjects that are comfortably above threshold (deficit ≤ 0 and remaining occurrences of that subject far exceed what's needed) are tentatively marked **Skip candidates**.
- Slots for subjects below threshold, or subjects whose remaining occurrences ≈ remaining required attendances, are marked **Attend**.

### 15.6 Step 5 — Block Consolidation (Core Rule)
Within a single day, scan the ordered slot list. If a slot is marked **Skip** but is directly between two slots marked **Attend** (i.e., contiguous in time with no free gap), **upgrade it to Attend**. Repeat until no sandwiched Skip slots remain. This produces contiguous **PlanBlocks**: consecutive same-recommendation slots are merged into a single block with a combined start/end time and subject list.

A block is only marked **Skip** in full if all its slots are Skip candidates with no Attend slot before or after it on that day requiring a walk-through.

### 15.7 Step 6 — Global Feasibility Re-check
After block consolidation (which may force extra Attends beyond the greedy minimum), recompute projected final percentages for every subject and overall. If all meet policy → plan is **Confirmed Feasible**. If consolidation forced so many extra attends that some other subject's Skip assumptions changed favorably (more Attends never hurts feasibility), the plan remains feasible or improves; the engine does not need to re-solve — block consolidation never removes an Attend, so overall feasibility can only be preserved or improved relative to Step 3's solution when Step 3 was itself feasible.

### 15.8 Step 7 — Optional Marking
Slots that are marked Attend purely because block consolidation forced them (not because they were individually required) are labeled **Optional-but-included**, shown as a distinct sub-status in the UI (used for the "yellow" calendar marking) so users understand why a comfortably-safe subject still appears as attend.

### 15.9 Step 8 — Explanation Generation
For each PlanBlock, generate an explanation string from a template:
- If block is Attend because of a below-threshold subject: `"{subject} attendance is below the required {min}%. Attend to recover."`
- If block is Attend because of block consolidation only: `"{subject} attendance is already sufficient but is included because it lies between required lectures."`
- If block is Skip: `"{subject} attendance is safely above threshold ({current}% vs {min}% required); skipping reduces unnecessary campus time."`
Day-level explanation aggregates block-level reasons into one paragraph.

---

## 16. Optimization Rules (Priority Order)

1. **Never violate attendance rules** — hard constraint; the engine will never emit a plan it can verify violates a configured minimum if a feasible plan exists.
2. **Maintain required attendance per subject.**
3. **Maintain required overall attendance.**
4. **Generate continuous lecture blocks** — no isolated skip sandwiched between attends.
5. **Minimize number of college visits** — prefer concentrating necessary attendance into fewer distinct days when the timetable allows flexibility (note: in MVP, timetable is fixed/recurring, so this mostly manifests as fully-skippable days being marked Skip entirely rather than partial visits).
6. **Minimize total hours spent on campus** — among equally feasible plans, prefer the one with fewer total Attend hours.
7. **Avoid unnecessary idle waiting between lectures** — enforced structurally by Block Consolidation (Section 15.6), which eliminates gaps within a day's Attend schedule.

These are implemented as a strict lexicographic priority: a lower-numbered rule is never sacrificed to improve a higher-numbered one.

---

## 17. Edge Cases

| Edge Case | Handling |
|---|---|
| Subject has 0 classes held so far | Treat current percentage as undefined; base all decisions on future-only projection; require attending enough future lectures to hit the target from a 0/0 start. |
| User supplies only a percentage, no held/present | Prompt for an assumed "held so far" value (default configurable, e.g., 0 or a user-entered estimate) so held/present math stays consistent; store as an explicit estimate, flagged in the UI as "approximate." |
| Target is mathematically infeasible for a subject (even attending 100% of remaining lectures can't reach the minimum) | Mark subject as "At Risk / Infeasible," show best achievable percentage, and still recommend attending 100% of remaining lectures for that subject (Priority 2 default fallback). |
| Semester end date has already passed | Reject / prompt user to correct dates; no plan generated. |
| No timetable entered yet | Block "Generate Plan" with a clear message indicating missing setup step. |
| A Semester Event overlaps a date that also has timetable slots defined | Event's resolved flags take precedence per Section 15.3: `exclude_from_recommendation` removes the date from planning entirely; `cancels_lectures` alone removes only the overlapping slots. |
| Two or more Semester Events overlap the same date with conflicting flags (e.g., one says `exclude_from_recommendation=false`, another says `true`) | Most restrictive resolved value wins per flag, independently (Section 15.3). |
| User selects "Other/Custom" event type but leaves attendance-impact flags unset | System applies the "custom" preset's conservative defaults (cancels lectures, excluded from recommendation) and visibly flags the event as "using default impact — review recommended" until the user confirms. |
| User creates a Semester Event with `start_date` after `end_date`, or spanning outside the semester's date range | Rejected at validation (Section 19). |
| A Semester Event's date range extends beyond `semester_profile.end_date` (e.g., end-sem exams announced before the semester end date is finalized) | Allowed, but the portion beyond `end_date` is ignored by calendar expansion; UI surfaces a non-blocking warning. |
| An institution adds an event type not in the current preset list (e.g., "Hackathon") | User creates it via "Other/Custom" with a free-text label; no code or schema change required. A future admin/preset-management flow (Section 25) can promote frequently-used custom labels to first-class presets without breaking existing data, since `SemesterEvent` already stores a normalized `event_type_id`. |
| A subject is removed from the timetable mid-semester (e.g., elective dropped) | Historical held/present retained for record; future slots for that subject simply stop appearing in remaining calendar expansion. |
| Two subjects share the exact same start time (parallel batches / labs) | Flagged as a data-entry conflict during validation; user must resolve (only one subject can occupy a given day/time in a single student's plan). |
| All remaining lectures of a subject are already sufficient to hit target even with all skipped | Mark all as Skip candidates; block consolidation may still force some to Attend if they're between two other Attend blocks. |
| User has more "present" than "held" for a subject (data entry error) | Reject via validation (present_count cannot exceed held_count). |
| Weekly timetable has a day with zero lectures (e.g., no classes on Saturday) | That weekday simply produces no PlanDay blocks; not an error. |
| Plan requested for a semester with 0 remaining lecture days (fully in the past) | Return the final actual percentages with no forward plan; show as "Semester Complete" state. |

---

## 18. Constraints

- Zero monetary budget for hosting, APIs, or tooling.
- No dependency on OpenAI, Google Gemini, Anthropic, or any paid/metered LLM API.
- Must be implementable by a single developer without a team.
- Must run on free-tier hosting (Vercel/Render) or fully locally with no hosting at all.
- Data storage limited to SQLite in MVP (no managed cloud database costs).
- All third-party libraries used must be free and open-source (MIT/Apache/BSD-class licenses preferred).
- The recommendation engine must be explainable — no opaque black-box ML model in MVP; all logic must be traceable to explicit rules for the Explanation Engine to work.

---

## 19. Validation Rules

**Semester Profile**
- `end_date` must be after `start_date`.
- `min_overall_percentage` and `min_subject_percentage` must be in range (0, 100].

**Subject**
- `held_count >= 0`, `present_count >= 0`.
- `present_count <= held_count`.
- `min_percentage_override`, if set, must be in range (0, 100].

**TimetableSlot**
- `start_time < end_time`.
- No two slots for the same `semester_id` + `weekday` may overlap in time.
- `weekday` must fall within the semester's actual operating days (configurable, default Mon–Sat).

**SemesterEvent**
- `start_date` must be on or before `end_date`.
- `start_date` should fall within `[semester.start_date, semester.end_date]`; if `end_date` extends beyond `semester.end_date`, allow it but surface a non-blocking warning (Section 17).
- `event_type_id` must reference an existing `EventTypeDefinition`.
- `custom_type_label` is required (non-empty) when the referenced `EventTypeDefinition.key = 'custom'`; otherwise it must be null.
- `name` is required (non-empty).
- Each of the four `*_override` flags, if provided, must be boolean; `null` is valid and means "inherit from event type default."
- No hard limit on the number of `SemesterEvent` rows per semester (unlimited, per requirement).
- Overlapping events on the same date range are explicitly **allowed** (e.g., "Industrial Visit" overlapping "College Event"); conflicts are resolved at read-time via the most-restrictive-flag-wins rule (Section 15.3), not rejected at write-time.

**EventTypeDefinition**
- `key` must be unique.
- Exactly one row may have `key = 'custom'` and act as the fallback preset for user-defined types.
- Deleting a system preset is not permitted while any `SemesterEvent` references it; deletion of non-system (future custom-promoted) types requires reassignment first.

**Plan Generation Pre-check**
- At least one TimetableSlot must exist.
- At least one Subject must exist.
- Reject generation if any validation rule above is violated, returning a structured list of errors (not a generic failure).

---

## 20. UI Screens

1. **Onboarding / Setup Wizard** — multi-step form: Semester Dates → Policy → Timetable Builder → Attendance Entry → Semester Events (add as many as needed via "Add Semester Event"; can be skipped/added later).
2. **Dashboard (Home)** — overall attendance current vs. required, per-subject mini progress bars, "safe skips remaining," predicted final attendance, "Generate/Recalculate Plan" button.
3. **Calendar View** — month grid, each day colored Green (Attend), Red (Skip), Yellow (Optional-included), Gray (no lecture day / excluded by a Semester Event); click a day to see its block breakdown, any covering Semester Event(s), and explanation.
4. **Daily Schedule View** — list view by date, showing time blocks, subjects in each block, Attend/Skip tag, and explanation text.
5. **Subject View** — one card per subject: current %, required %, lectures remaining, lectures still needed to attend, at-risk flag if applicable.
6. **Semester Timeline View** — horizontal/vertical scrollable timeline across the whole remaining semester with day-level color markers, useful for spotting exam-heavy or vacation-heavy stretches.
7. **Settings / Policy Editor** — edit overall/subject minimums, per-subject overrides.
8. **Timetable Editor** — add/edit/remove weekly slots per weekday.
9. **Semester Events Manager** — single page listing all Semester Events (sorted by date), with an "Add Semester Event" action opening a form (Name, Event Type preset dropdown incl. "Other/Custom", Start Date, End Date, Description, and the four attendance-impact flags pre-filled from the type's defaults and editable). Supports edit/remove on any event, with no limit on count. Replaces separate Holiday/Mid-Sem/End-Sem/Fest forms entirely.
10. **Data Import/Export** — export all current input data as JSON/CSV backup; import to restore.

---

## 21. Navigation Flow

```
Landing / Setup Wizard (first run only)
        |
        v
   Dashboard (Home) <---------------------------+
   |     |        |         |                   |
   v     v        v         v                   |
Calendar Daily  Subject  Timeline                |
 View   Schedule View    View                    |
   |     |        |         |                    |
   +-----+--------+---------+--------------------+
              (all link back to Dashboard,
               and to Settings / Timetable Editor /
               Semester Events Manager via a persistent nav bar)

Settings, Timetable Editor, Semester Events Manager
   -> accessible from persistent side/top nav at all times
   -> changes here (including any Add/Edit/Remove Semester Event) enable
      "Recalculate Plan" on Dashboard
```

---

## 22. Technology Stack

| Layer | Choice | Why (free/open-source rationale) |
|---|---|---|
| Frontend framework | React + Vite | Free, fast dev server, huge free ecosystem. |
| Styling | Tailwind CSS | Free, utility-first, fast to build clean UI solo. |
| Charts | Chart.js | Free, lightweight, sufficient for dashboard bars/progress. |
| Calendar UI | FullCalendar (open-source core) | Free calendar rendering with day-coloring support. |
| Backend framework | Python FastAPI | Free, fast to build REST APIs, good typing/validation via Pydantic. |
| Database (MVP) | SQLite | Zero-cost, file-based, no server needed. |
| Database (later scale) | PostgreSQL | Free tier available on Render/Supabase if/when multi-user is added. |
| Optimization/algorithms | Pure Python (custom greedy + constraint checks) | No cost, fully explainable. |
| Optimization (future upgrade) | Google OR-Tools | Free, open-source constraint solver for more complex scheduling once MVP rules-engine is validated. |
| Hosting (frontend) | Vercel free tier | Zero cost for solo/student projects. |
| Hosting (backend) | Render free tier | Zero cost, sleeps when idle (acceptable for MVP). |
| Version control | GitHub | Free for public/private repos. |
| CDN/DNS (optional) | Cloudflare free tier | Free if a custom domain is used later. |

---

## 23. Folder Structure

```
attendance-planner-ai/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entrypoint
│   │   ├── api/
│   │   │   ├── semester.py         # /semesters endpoints
│   │   │   ├── subject.py          # /subjects endpoints
│   │   │   ├── timetable.py        # /timetable endpoints
│   │   │   ├── event_types.py      # /event-types endpoints
│   │   │   ├── semester_events.py  # /semester-events endpoints
│   │   │   └── plan.py             # /plan generate/fetch endpoints
│   │   ├── models/
│   │   │   ├── semester.py
│   │   │   ├── subject.py
│   │   │   ├── timetable.py
│   │   │   ├── event_type_definition.py
│   │   │   ├── semester_event.py
│   │   │   └── plan.py
│   │   ├── schemas/                # Pydantic request/response schemas
│   │   ├── engine/
│   │   │   ├── event_resolution.py
│   │   │   ├── calendar_expansion.py
│   │   │   ├── requirement_calc.py
│   │   │   ├── slot_selector.py
│   │   │   ├── block_consolidation.py
│   │   │   └── explanation_generator.py
│   │   ├── db/
│   │   │   ├── session.py
│   │   │   └── init_db.py
│   │   └── core/
│   │       ├── config.py
│   │       └── validation.py
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── CalendarView.jsx
│   │   │   ├── DailyScheduleView.jsx
│   │   │   ├── SubjectView.jsx
│   │   │   ├── TimelineView.jsx
│   │   │   ├── SetupWizard.jsx
│   │   │   ├── SettingsPage.jsx
│   │   │   ├── TimetableEditor.jsx
│   │   │   └── SemesterEventsManager.jsx
│   │   ├── components/
│   │   ├── api/
│   │   │   └── client.js
│   │   ├── hooks/
│   │   ├── context/
│   │   └── App.jsx
│   ├── index.html
│   ├── tailwind.config.js
│   └── package.json
├── docs/
│   └── Attendance_Planner_AI_SRD.md
└── README.md
```

---

## 24. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/semesters` | Create a semester profile (dates + policy). |
| GET | `/semesters/{id}` | Fetch a semester profile. |
| PUT | `/semesters/{id}` | Update semester dates/policy. |
| POST | `/semesters/{id}/subjects` | Add a subject with held/present. |
| PUT | `/subjects/{id}` | Update a subject's held/present or override %. |
| DELETE | `/subjects/{id}` | Remove a subject. |
| POST | `/semesters/{id}/timetable` | Add a timetable slot. |
| PUT | `/timetable/{id}` | Update a timetable slot. |
| DELETE | `/timetable/{id}` | Remove a timetable slot. |
| GET | `/event-types` | List all Event Type presets (including any custom types promoted to first-class presets later), each with default attendance-impact flags. |
| POST | `/semesters/{id}/events` | Add a Semester Event (name, event_type_id or "custom" + custom_type_label, dates, description, optional flag overrides). Unlimited per semester. |
| GET | `/semesters/{id}/events` | List all Semester Events for a semester, sorted by date. |
| PUT | `/events/{id}` | Update a Semester Event (dates, description, flag overrides, etc.). |
| DELETE | `/events/{id}` | Remove a Semester Event. |
| POST | `/semesters/{id}/plan/generate` | Run the recommendation engine and persist the plan. |
| GET | `/semesters/{id}/plan` | Fetch the current stored plan (raw day/block data). |
| GET | `/semesters/{id}/plan/calendar` | Plan reshaped for Calendar View. |
| GET | `/semesters/{id}/plan/daily` | Plan reshaped for Daily Schedule View. |
| GET | `/semesters/{id}/plan/subjects` | Plan reshaped for Subject View. |
| GET | `/semesters/{id}/plan/dashboard` | Aggregated dashboard metrics. |
| GET | `/semesters/{id}/plan/timeline` | Plan reshaped for Semester Timeline View. |
| GET | `/semesters/{id}/export` | Export all input data as JSON. |
| POST | `/semesters/{id}/import` | Import previously exported JSON. |

All endpoints return structured error objects (`{ "errors": [...] }`) on validation failure per Section 19, with HTTP 422.

---

## 25. Future Roadmap

**Phase 2 (Post-MVP Automation)**
- Academic calendar PDF upload + parsing, mapped directly onto the Semester Events model (each extracted item becomes a `SemesterEvent` with a best-guess `event_type_id` and pre-filled flags for the user to confirm) rather than a separate holiday/mid-sem/end-sem extraction pipeline.
- Timetable OCR upload (image/PDF → structured timetable).
- Admin/preset-management flow allowing frequently-used custom event type labels (e.g., a college's recurring "Hackathon Week") to be promoted to first-class `EventTypeDefinition` presets across a user's semesters, with zero schema change since the table already supports arbitrary rows.

**Phase 3 (Accounts & Persistence)**
- User authentication (free/open-source solution, e.g., self-hosted JWT auth — no paid auth-as-a-service).
- Multiple semester profiles per user, semester history.
- Cloud sync across devices (still free-tier infrastructure, e.g., Supabase free tier).

**Phase 4 (Engagement)**
- Notifications/reminders (browser push or free email service with generous free tier).
- Mobile PWA packaging for installable home-screen app.
- Daily "today's plan" push-style summary.

**Phase 5 (Intelligence Upgrade)**
- Attendance trend prediction (simple statistical projection, still not requiring a paid LLM).
- "What if I skip tomorrow?" ad hoc scenario simulator, reusing the engine in a dry-run mode.
- Optional OR-Tools-based solver as a pluggable alternative to the greedy engine for more complex timetables (e.g., alternating-week schedules, elective batches).

---

## 26. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Manual data entry burden discourages adoption | Users abandon setup before first plan | Keep Setup Wizard minimal; sensible defaults; allow partial setup with warnings instead of hard blocks where possible. |
| Greedy algorithm produces a suboptimal (though still feasible) plan | Slightly more campus time than truly optimal | Document as known MVP limitation; OR-Tools upgrade path already planned (Section 25). |
| Free hosting tiers (Render) sleep/cold-start | Slow first load after inactivity | Communicate as an accepted MVP trade-off; consider frontend-only local-first mode as fallback. |
| Infeasible targets confuse or alarm users | Loss of trust in the tool | Explicit "At Risk" UI state with clear best-achievable numbers, not a silent failure. |
| User misconfigures a Semester Event's attendance-impact flags (e.g., forgets to mark a fest as `cancels_lectures`) | Plan generated against a calendar that doesn't match reality | Sensible, editable defaults per Event Type preset; "using default impact — review recommended" indicator for custom types (Section 17); Calendar View surfaces the covering event on each affected day so mistakes are easy to spot. |
| Unlimited custom events lead to a cluttered Semester Events list over a long semester | Harder to scan/manage | List view sorted by date with type-based icon/color coding; search/filter by type is a low-cost near-term addition if needed. |
| Timetable changes mid-semester (electives, reschedules) not reflected promptly | Plan drifts from reality | "Recalculate" is a prominent, low-friction action; future auto-recompute on any edit. |
| Solo-developer bandwidth | Feature slippage | Strict MVP scope (Section 30) with explicit non-goals to prevent scope creep. |

---

## 27. Assumptions

- The student attends the same weekly timetable every week for the remainder of the semester except where it is overridden by a Semester Event's resolved attendance-impact flags.
- Event Type presets ship with reasonable default attendance-impact flags, but the user is expected to review/override them for events with unusual or institution-specific handling (e.g., an Industrial Visit that does *not* auto-credit attendance).
- A "block" is defined purely by time-contiguity within a single day; no cross-day blocking.
- Attendance percentage is computed as `present / held * 100`, consistent with standard college policy.
- The user is honest and reasonably diligent about updating actual held/present data; the system does not attempt to auto-detect real-world attendance (no biometric/GPS integration).
- All lecture slots for a given subject count equally toward that subject's percentage (no weighting by lecture type, e.g., lab vs. theory, in MVP).
- The college week structure (which weekdays have classes) is implicitly defined by whichever weekdays have timetable slots entered.

---

## 28. Development Milestones

| Milestone | Scope |
|---|---|
| M0 — Project Scaffolding | Repo structure, FastAPI skeleton, React+Vite+Tailwind skeleton, SQLite schema created. |
| M1 — Data Entry Backend | Semester, Subject, TimetableSlot, EventTypeDefinition (seeded presets), SemesterEvent models + CRUD API + validation (Section 19). |
| M2 — Setup Wizard Frontend | Multi-step onboarding UI wired to M1 endpoints. |
| M3 — Event Resolution + Calendar Expansion + Requirement Calculation | Engine modules for Sections 15.2–15.4, including the event-flag resolution and multi-event-overlap logic. |
| M4 — Slot Selection + Block Consolidation | Engine modules for Sections 15.5–15.7 with unit tests against the DBMS/OS/Maths/EFM example. |
| M5 — Explanation Engine | Template-based reason generation (Section 15.9). |
| M6 — Plan API + View Adapters | `/plan/*` endpoints reshaping data per view. |
| M7 — Dashboard + Calendar View Frontend | First two visualization screens. |
| M8 — Daily Schedule + Subject View Frontend | Remaining two core visualization screens. |
| M9 — Semester Timeline View | Final visualization screen. |
| M10 — Recalculation Flow + Edge Case Hardening | Manual recalculate wiring; implement all Section 17 edge cases; infeasibility UI. |
| M11 — Export/Import | JSON backup/restore. |
| M12 — Deployment | Vercel (frontend) + Render (backend) free-tier deployment, or documented local-run instructions. |

---

## 29. Testing Strategy

- **Unit tests (engine)**: cover requirement calculation math, block consolidation (including the DBMS/OS/Maths/EFM worked example from this SRD as a canonical test case), and infeasibility detection, using pytest.
- **Unit tests (validation)**: cover every rule in Section 19 with both valid and invalid fixtures.
- **API integration tests**: FastAPI TestClient covering the full CRUD + plan-generation flow end-to-end against an in-memory/temp SQLite DB.
- **Edge case regression tests**: one test per row in Section 17.
- **Frontend component tests**: React Testing Library for Setup Wizard step validation and for correct color-coding logic in Calendar View given a mocked plan response.
- **Manual exploratory testing**: full walkthrough of the User Flow (Section 10) before each milestone sign-off, using at least two personas' data (Persona 1 "Borderline Rahul" and Persona 4 "New Student Zara") to exercise both the common and near-empty-data paths.
- **Regression baseline**: the worked example in Section "Extremely Important Practical Constraint" of the source brief (DBMS 62%, OS 90%, Maths 64%, EFM 95% → Attend 9–12, Skip EFM) is kept as a permanent fixture test to guard against future engine regressions.

---

## 30. MVP Scope vs Future Scope

### MVP (Ship First)
- Manual entry: semester dates, policy, timetable, attendance (held/present or %), and an unlimited, type-driven Semester Events list (presets + fully custom types) with per-event attendance-impact flags.
- Block-based recommendation engine (greedy + consolidation) with hard-constraint feasibility checking.
- Explanation engine (template-based).
- Five views: Calendar, Daily Schedule, Subject, Dashboard, Semester Timeline.
- Manual "Recalculate Plan" action.
- Infeasibility detection and clear warning UI.
- JSON export/import for backup.
- Fully free-tier deployable (or local-only).

### Explicitly Future (Not MVP)
- Academic calendar PDF upload/parsing.
- Timetable OCR upload.
- User authentication and multi-semester accounts.
- Cloud sync.
- Notifications/reminders.
- Mobile PWA packaging.
- Automated daily recommendations (push-style).
- Attendance trend prediction.
- "What if I skip tomorrow?" scenario simulator.
- OR-Tools-based solver upgrade.

---

*End of Software Requirements Document. This document is intended to be handed directly to an AI coding assistant, module by module (per Section 28 milestones), to implement Attendance Planner AI from scratch.*
