# Technical Requirements Document (TRD)
## Attendance Planner AI
**Document Version:** 1.1
**Companion to:** `Attendance_Planner_AI_SRD_v1.1.md`

---

## 1. Architecture Changes

Version 1.1 integrates directly into the existing Version 1.0 architecture without altering the core deployment topology (FastAPI backend + React frontend + SQLite). The primary architectural additions are a new `import_service` package in the backend, a new generic policy abstraction in the engine, and an ephemeral staging pipeline for document imports.

### Data Flow for Plan Generation (Updated)
1. **Manual / Import Entry:** Data enters via existing CRUD endpoints or the new Import Session workflow.
2. **Persistence:** Data is committed to `timetable_slot`, `semester_event`, and `subject` (with new `slot_type_id` and global `slot_type` metadata).
3. **Plan Request:** `POST /semesters/{id}/plan/generate`.
4. **Pipeline:**
   - Event Resolution (Unchanged)
   - Calendar Expansion (Unchanged)
   - **Requirement Calculation (Updated):** Uses a `PolicyEvaluator` to resolve exact required attendances per `(subject, slot_type)` combination instead of per subject alone.
   - **Slot Selection (Updated):** Greedy deferral is replaced with a **Distribution Algorithm** allocating skips evenly.
   - Block Consolidation (Unchanged)
   - **Explanation Generation (Updated):** Templates are enriched to mention slot policies (e.g., Mandatory, Max Absences) when relevant.
5. **Response:** Identical V1.0 API contract for plan output.

---

## 2. Backend Changes

- **New Services:**
  - `import_service/timetable_parser.py` (PDF and OCR logic for timetables)
  - `import_service/calendar_parser.py` (PDF and OCR logic for academic calendars)
- **New Modules:**
  - `engine/policy_evaluator.py`: Encapsulates logic for Percentage, Maximum Absence, and Mandatory math.
- **New Database Models:**
  - `SlotType` (Reference table for policy modes)
  - `SemesterSlotPolicy` (Overrides policy values per semester)
  - `ImportSession` (Ephemeral storage for unconfirmed extractions)
- **New API Endpoints:**
  - `POST /semesters/{id}/import/timetable`
  - `POST /semesters/{id}/import/calendar`
  - `GET /import-sessions/{session_id}`
  - `POST /import-sessions/{session_id}/confirm`
  - `DELETE /import-sessions/{session_id}`
  - `GET /slot-types`
- **New Validation Rules:**
  - `ImportSession` payloads must strictly conform to expected row schemas depending on `import_type`.
  - `SemesterSlotPolicy` values must match their referenced `SlotType.policy_mode` requirements (e.g., `null` for mandatory, `float <= 100` for percentage).

---

## 3. OCR & Document Processing Pipeline

The backend exposes document uploads via `multipart/form-data`. Parsing relies on local, free libraries (`pdfplumber` and `pytesseract`) to avoid external API costs.

### PDF Timetable Import
- **Upload:** User uploads a `.pdf`.
- **Parsing:** `pdfplumber` extracts bounded tables from the PDF pages.
- **Extraction:** Heuristics map columns (time, Monday-Friday) and rows to `(weekday, start_time, end_time, subject_name)` tuples.
- **Confidence Scoring:** High (1.0) if table bounds are perfect and text is clean. Lowered if row-spanning cells or ambiguous time formats exist.
- **Session:** Results are serialized as JSON and saved to `ImportSession`.

### Image Timetable Import (OCR)
- **Upload:** User uploads a `.png`, `.jpg`, or `.jpeg`.
- **Parsing:** Image is grayscaled and thresholded using `Pillow`. `pytesseract` extracts text with bounding boxes.
- **Extraction:** Spatial coordinate matching infers a grid layout to recreate the table structure.
- **Confidence Scoring:** Inherently lower than PDF. Driven by Tesseract's word-level confidence scores.
- **Session:** Results saved to `ImportSession`.

### PDF Academic Calendar Import
- **Upload:** User uploads a `.pdf`.
- **Parsing:** `pdfplumber` extracts raw text and tables.
- **Extraction:** Date-regex (e.g., "DD-MM-YYYY", "DD MMM") identifies lines containing events. Heuristics extract `(event_name, start_date, end_date, inferred_event_type)`.
- **Confidence Scoring:** High if a clear "Start Date - End Date" matches an existing event type. Low if the date is ambiguous or single-date.
- **Session:** Results saved to `ImportSession`.

### Image Academic Calendar Import (OCR)
- **Upload:** User uploads an image.
- **Parsing/Extraction:** Similar to image timetable but applies the date-regex text processing logic instead of grid reconstruction.
- **Confidence Scoring:** Tesseract word-confidence combined with regex match strength.
- **Session:** Results saved to `ImportSession`.

---

## 4. Import Session Lifecycle

Because extraction is imperfect, parsed data is placed in a staging area (`ImportSession`) rather than written directly to production tables. 

1. **Created:** Client hits the upload endpoint. Backend validates file type and size.
2. **Processing:** Extraction runs synchronously (for MVP scale) or blocks until complete.
3. **Pending Review:** The `ImportSession` record is created in the DB with status `pending_review`. The API returns the `session_id` and the extracted JSON payload (with confidence scores) to the frontend. *Because it is in the database, the user can refresh the browser, fetch the session by ID, and resume review.*
4. **Confirmed:** User completes review on the frontend, modifying the JSON payload as needed. The frontend sends the final payload to `/confirm`.
5. **Committed:** The backend validates the final payload and inserts the records into `timetable_slot` or `semester_event`. The session status updates to `confirmed`.
6. **Deleted:** Sessions are meant to be ephemeral. A background script or lazy-delete cleans up `ImportSession` rows older than 24 hours.

---

## 5. Recommendation Engine Changes

### Attendance Distribution
The `slot_selector.py` module is updated. The V1.0 greedy logic (`must_attend = remaining_occurrences <= remaining_need`) is replaced.
- **New Logic:** The engine calculates `slack = total_future_lectures - need_attend` for each subject. It computes a `skip_interval = total_future_lectures / (slack + 1)`. As it iterates chronologically over the calendar days, it spaces Skips evenly using the interval, falling back to Attend when no slack remains.
- **Integration:** This changes only the internal logic of `slot_selector.py`. The input (`CalendarDay[]`, `RequirementResult[]`) and output (`DaySelection[]`) contracts remain completely identical. Feasibility is guaranteed because total allowable skips never exceed `slack`.

### Attendance Policies
The `requirement_calc.py` module is updated to evaluate requirements grouped by `(subject, slot_type)` instead of just `subject`.
- **New Logic:** A new `PolicyEvaluator` processes the list of slots for a day. Depending on the `slot_type`'s mode:
  - `percentage`: Solves `(present + x) / held >= threshold`.
  - `max_absence`: `need_attend = total_future - max_allowed`.
  - `mandatory`: `need_attend = total_future`.
- **Integration:** `types.py` is updated so `RequirementResult` carries a `slot_type_id`. `explanation_generator.py` is updated to read the `PolicyEvaluator`'s mode to output customized justification strings.

---

## 6. Database Changes

### New Tables
1. **`slot_type`**
   - **Columns:** `id` (PK), `name` (String), `policy_mode` (String/Enum), `is_default` (Boolean).
   - **Why:** Central dictionary of generic slot types (e.g., Normal Lecture, Lab).
2. **`semester_slot_policy`**
   - **Columns:** `id` (PK), `semester_id` (FK), `slot_type_id` (FK), `policy_value` (Float, nullable).
   - **Why:** Allows Semester 2 to require 80% for Lectures while Semester 1 requires 75%, without polluting the global `slot_type` table.
3. **`import_session`**
   - **Columns:** `id` (PK UUID), `semester_id` (FK), `import_type` (String), `status` (String), `extracted_payload` (JSON), `created_at` (Datetime).
   - **Why:** Supports the mandatory Review & Correction workflow and browser-refresh resilience.

### Modified Tables
1. **`timetable_slot`**
   - **New Column:** `slot_type_id` (FK -> `slot_type.id`, nullable).
   - **Why:** Links a specific class occurrence to an attendance policy.

### Migration Strategy
- Alembic migration will create the new tables.
- `slot_type` will be seeded with defaults (Normal Lecture, Tutorial, Lab) in `init_db.py`.
- Alembic migration will add `slot_type_id` to `timetable_slot`, defaulting to the ID of "Normal Lecture" to preserve backward compatibility for V1.0 data.

---

## 7. API Design

### POST `/api/v1/semesters/{id}/import/timetable`
- **Request:** `multipart/form-data` containing `file`.
- **Response (201):** `{"session_id": "uuid", "import_type": "timetable", "payload": [...]}`
- **Validation:** Must be valid PDF/Image. Max size 5MB.
- **Errors:** 400 Bad Request (invalid file), 415 Unsupported Media Type.

### POST `/api/v1/semesters/{id}/import/calendar`
- **Request:** `multipart/form-data` containing `file`.
- **Response (201):** `{"session_id": "uuid", "import_type": "calendar", "payload": [...]}`

### GET `/api/v1/import-sessions/{session_id}`
- **Response (200):** Full `ImportSession` object.
- **Errors:** 404 Not Found.

### POST `/api/v1/import-sessions/{session_id}/confirm`
- **Request:** `{"final_payload": [...]}`
- **Response (200):** Status success.
- **Validation:** `final_payload` must pass standard V1.0 validation rules for `TimetableSlotCreate` or `SemesterEventCreate`.
- **Errors:** 400 Bad Request (invalid data formatting), 404 Not Found.

### GET `/api/v1/slot-types`
- **Request:** None
- **Response (200):** List of global `SlotType` objects.

---

## 8. Frontend Architecture

### Upload Flow
- New `ImportWizard` component integrated into the Setup flow.
- Users select "Import from Document" or "Manual Entry".
- Drag-and-drop file upload using standard HTML5 APIs.
- Loading spinner indicating extraction in progress.

### Review & Correction UI
- Renders the `extracted_payload` in a dynamic, spreadsheet-like table.
- **Confidence Indicators:**
  - Rows with `confidence >= 0.8` have a green/neutral background.
  - Rows with `confidence < 0.8` have an amber background and a warning icon indicating "Review Required".
- Inline editing allows the user to correct typos from OCR or fix misaligned columns.
- Users can add missing rows manually or delete junk rows extracted by mistake.

### Graceful Degradation
- If the backend returns a 501 Not Implemented or similar for image uploads (due to missing Tesseract), the UI displays a clear fallback message: "Image OCR is currently disabled on this server. Please upload a PDF or use Manual Entry."

---

## 9. Security Considerations

- **Allowed File Types:** Enforced both on frontend (`accept` attribute) and backend (`mimetype` checking). Only `application/pdf`, `image/png`, `image/jpeg`.
- **Maximum Upload Size:** Strictly enforced at 5MB via FastAPI middleware to prevent DOS via memory exhaustion during parsing.
- **File Validation:** Files are processed entirely in memory; no execution of files.
- **Temporary Storage:** Files are not saved to disk permanently. The parsed JSON is stored in SQLite; the binary blob is discarded immediately after extraction.
- **Protection Against Malformed Uploads:** `pdfplumber` and `Pillow` are resilient to corrupted files and will throw catchable exceptions, resulting in a 400 error rather than a server crash.

---

## 10. Performance Considerations

- **Large Documents:** Timetables and Calendars are typically 1-3 pages. 5MB hard limit prevents abuse.
- **OCR Execution Time:** `pytesseract` can take 2-5 seconds per image. Handled synchronously for MVP, but frontend must display a non-blocking loading state.
- **Memory Usage:** `pdfplumber` can be memory-heavy. Running synchronously ensures one import is handled per request thread, acceptable for solo-developer/personal scale.
- **Import Scalability:** SQLite handles `ImportSession` inserts trivially. Stale session cleanup prevents DB bloat.

---

## 11. Testing Strategy

- **Unit Tests:**
  - `PolicyEvaluator`: Test Percentage, Max Absence, and Mandatory math explicitly.
  - Distribution Algorithm: Test skip spacing logic, proving total skips equals available slack.
- **Integration Tests:**
  - Full API flow: Upload dummy file -> get `session_id` -> confirm payload -> verify DB insertion.
- **OCR Tests:**
  - Use pre-committed fixture PDFs and Images (anonymized) to assert extraction logic outputs expected JSON schemas.
- **Frontend Tests:**
  - Component tests for the Review UI verifying that low-confidence scores trigger the correct visual CSS classes.
- **Regression Tests:**
  - Ensure V1.0 endpoints and the canonical DBMS/OS/Maths/EFM engine fixture still pass perfectly.

---

## 12. Non-Goals

Version 1.1 explicitly does **NOT** support:
- **Handwritten timetables:** OCR targets printed text only.
- **Multi-language OCR:** English only.
- **Password-protected PDFs:** Must be unlocked prior to upload.
- **Multiple timetables in a single document:** If a college PDF contains timetables for all departments, the extraction will likely fail or produce massive noise. Users should crop or split documents to their specific schedule.
- **Automatic acceptance:** The system will never bypass the user Review & Correction screen, regardless of 1.0 confidence scores.

---
*End of Version 1.1 Technical Requirements Document.*
