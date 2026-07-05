# Software Requirements Document (SRD)
## Attendance Planner AI
**Document Version:** 1.1

---

## 1. Project Overview
Attendance Planner AI is an intelligent scheduling assistant for college students. It helps students maintain their required attendance percentages by generating optimal, personalized, day-by-day plans telling them exactly which lectures to attend and which they can safely skip, without forcing them to spend unnecessary idle hours on campus.

**Version 1.1 Scope** extends the stable 1.0 baseline by introducing Smart Academic Document Import (PDF/OCR), Attendance Distribution, and Generalized Attendance Policies (per-slot types).

---

## 2. Core Value Proposition
- **Peace of mind:** Students never have to manually calculate their attendance trajectory.
- **Time optimization:** Consolidate mandatory attendance into continuous blocks; eliminate "sandwiched" skips that require waiting around campus.
- **Dynamic adjustment:** Re-optimizes the plan instantly if a user takes an unplanned absence, changes their timetable, or adds a new Semester Event.
- **Rapid Onboarding:** (New in V1.1) Import timetables and academic calendars directly from PDFs or images, drastically reducing manual data entry friction.
- **Realistic Planning:** (New in V1.1) Skips are distributed evenly across the semester instead of aggressively front-loaded.
- **Flexible Policies:** (New in V1.1) Distinct policies for Lectures, Labs, and Tutorials.

---

## 3. Key Personas (Unchanged from V1.0)
1. **Borderline Rahul (The Optimizer):** Target: exactly 75%. Wants to skip the absolute maximum number of classes possible without getting debarred.
2. **Diligent Priya (The Overachiever):** Target: 90%. Never wants to be at risk but wants permission to occasionally skip a low-value class to study for an exam.
3. **Commuter Kabir (The Batcher):** Lives 2 hours away. Cares deeply about Rule 4 (Block Consolidation) and Rule 5 (Minimize Visits). Would rather attend an extra class than commute just for one hour.
4. **New Student Zara (The Blank Slate):** Has no history yet (0 held / 0 present). Relies entirely on the engine's projection for the upcoming semester.

---

## 4. Product Principles
- **Correctness over aggression:** The engine must *never* recommend a skip that drops a user below their threshold if a feasible plan exists.
- **Explainability:** Every recommendation (Attend or Skip) must be accompanied by a human-readable reason. The user must trust the system. No black-box AI models for the core math.
- **Determinism:** The same inputs must yield the exact same plan every time.
- **User Agency:** (New in V1.1) Document extraction is always treated as a suggestion. A mandatory Review & Correction screen guarantees the user has the final say.

---

## 5. Non-Goals
- This is **not** a general-purpose attendance tracking / register app for teachers or institutions.
- This is **not** an AI chatbot. There is no conversational interface.
- The system will **not** depend on paid/metered LLM APIs (OpenAI, Gemini) at any point. Document extraction uses free, local libraries (e.g., pdfplumber, Tesseract).
- The MVP and V1.1 will **not** include login/auth, multi-user accounts, or cloud sync.
- The system will **not** attempt to model real-time GPS/location.

---

## 6. Version 1.1 Feature Breakdown

| Feature | Status |
|---|---|
| Policy config, Timetable builder, Event manager, Dashboard, Engine | V1.0 Stable |
| **Smart Timetable Import (PDF & Image)** | **New in V1.1** |
| **Smart Academic Calendar Import (PDF & Image)** | **New in V1.1** |
| **Extraction Confidence Scoring & Review Screen** | **New in V1.1** |
| **Attendance Distribution Algorithm** | **New in V1.1** |
| **Generalized Attendance Policies (Slot Types)** | **New in V1.1** |
| User authentication, cloud sync, notifications | Future |

---

## 7. Data Models (Additions & Modifications in V1.1)

V1.1 preserves all V1.0 models (`SemesterProfile`, `Subject`, `EventTypeDefinition`, `SemesterEvent`, `PlanDay`, `PlanBlock`) and introduces the following extensions:

### SlotType (New in V1.1)
Defines a generic category of lecture slot (shared globally across all semesters).
- `id`
- `name` (e.g., "Normal Lecture", "Lab", "Project Review")
- `policy_mode` (Enum: `percentage`, `max_absence`, `mandatory`)
- `is_default` (bool)

### SemesterSlotPolicy (New in V1.1)
Associates a global `SlotType` with a specific policy value for a given semester or subject.
- `id`
- `semester_id` (FK)
- `slot_type_id` (FK)
- `policy_value` (nullable float — e.g., 75 for percentage, 2 for max_absence, null for mandatory)

### TimetableSlot (Modified in V1.1)
- `id`, `semester_id`, `subject_id`, `weekday`, `start_time`, `end_time`, `order_index`
- **`slot_type_id`** (FK -> SlotType) — default maps to "Normal Lecture".

### ImportSession (New in V1.1)
Stores temporary extraction candidates before user confirmation, surviving browser refreshes.
- `id`
- `semester_id`
- `import_type` (Enum: `timetable`, `calendar`)
- `status` (Enum: `pending_review`, `confirmed`, `discarded`)
- `extracted_payload` (JSON - list of rows with confidence scores)
- `created_at`

---

## 8. Smart Academic Document Import (FR-11, FR-12)

### 8.1 Timetable Import (PDF & Image)
Users can upload a PDF or Image of their class schedule. 
- The system extracts structured tabular data: `(weekday, start_time, end_time, subject_name, confidence)`.
- Extraction from PDFs uses `pdfplumber`. Extraction from Images uses `pytesseract`.
- Image extraction is an **optional capability** that degrades gracefully if the Tesseract system binary is not installed.

### 8.2 Academic Calendar Import (PDF & Image)
Users can upload an academic calendar document.
- The system extracts: `(event_name, start_date, end_date, inferred_event_type, confidence)`.

### 8.3 Review & Correction Screen
Extraction is never auto-saved. The user is redirected to a mandatory review UI:
- Each extracted row displays a visual indicator of its **Confidence Score**.
  - `≥ 0.8`: High confidence (Ready).
  - `0.5–0.8`: Medium confidence (Amber warning).
  - `< 0.5`: Low confidence (Red warning).
- The user can edit any field, delete rows, or add missing rows before committing the data to the database.

---

## 9. Recommendation Engine Refinements (V1.1)

### 9.1 Attendance Distribution Algorithm
The V1.0 engine used a greedy deferral algorithm that concentrated all skips at the beginning of the semester. V1.1 replaces this with a **Distribution Algorithm**.
- For each subject, the engine computes `slack = total_future_lectures - need_attend`.
- The engine distributes the `slack` evenly across the remaining semester.
- This produces a realistic, balanced plan while guaranteeing mathematical feasibility by keeping total skips strictly bounded by the available slack.

### 9.2 Generalized Attendance Policies (Slot Types)
The Requirement Calculation stage is upgraded to compute needs per `(subject, slot_type)` combination using a `PolicyEvaluator`:
- **Percentage Mode:** `(present + future_attend) / held >= threshold %`.
- **Maximum Absence Mode:** `need_attend = total_future - max_allowed_absences`.
- **Mandatory Mode:** `need_attend = total_future` (0 absences allowed).
Block Consolidation and Explanation Generation stages are updated to respect and explain these stricter per-slot policies.

---

## 10. Development Milestones (V1.1)

| Milestone | Scope | Engine Impact | DB Migration |
|---|---|---|---|
| **M1 — PDF Timetable Import** | PDF upload, `pdfplumber` extraction, confidence scoring, Review & Correction screen. | ❌ No | ✅ Yes (`import_session`) |
| **M2 — Image Timetable Import** | Image upload, Tesseract OCR extraction, hooks into M1 review screen. Gracefully degrades if Tesseract absent. | ❌ No | ❌ No |
| **M3 — PDF Calendar Import** | PDF upload, date-regex + event extraction, hooks into M1 review screen mapping to Semester Events. | ❌ No | ❌ No |
| **M4 — Image Calendar Import** | Image upload, Tesseract OCR calendar extraction. Gracefully degrades if Tesseract absent. | ❌ No | ❌ No |
| **M5 — Attendance Distribution** | Modify `slot_selector.py` to distribute skips evenly. Update ADD docs. Full regression testing. | ✅ Yes | ❌ No |
| **M6 — Attendance Policies** | New `slot_type` table, `timetable_slot.slot_type_id`, three generic policy modes, `PolicyEvaluator`, updated wizard UI. | ✅ Yes | ✅ Yes |

*(UX Polish such as tooltips and mobile responsiveness are incorporated iteratively within these milestones.)*

---

*End of V1.1 Software Requirements Document.*
