# DJSCE Timetable Parser Architecture

We are shifting the objective from a generic OCR timetable parser to a specialized, high-accuracy parser designed specifically for DJSCE engineering timetables. 

This approach uses traditional Computer Vision (OpenCV) techniques to detect the physical grid lines of the timetable, allowing us to isolate and OCR individual cells with extremely high precision.

## User Review Required

> [!IMPORTANT]
> Please review this architecture carefully. Once approved, I will implement this pipeline to replace our current generic OCR clustering algorithm.

## Open Questions

> [!WARNING]
> 1. **Cell Merging Strategy**: For merged cells like "Saturday Project Work" that span multiple time slots, how should they be represented in the final structured payload? (e.g., as a single slot with a long `end_time`, or duplicated across the time slots?)
> 2. **Header Metadata**: Do you want the extracted metadata (Class, Semester, Effective Date) to be saved somewhere in the `ImportSession`, or just logged and discarded for now?
> 3. **Text-based PDFs vs Image pipeline**: For text-based PDFs, `pdfplumber` can extract tables but sometimes struggles with merged cells. If the DJSCE layout heavily relies on merged cells, do you want to force *all* PDFs through the highly-accurate OpenCV image pipeline, or stick to the `pdfplumber` text-extraction for pure-text PDFs?

---

## Proposed Architecture Pipeline

The pipeline will be fully encapsulated within `app/import_service/timetable_parser.py` and `app/import_service/image_preprocessing.py`, completely replacing the current spatial-clustering algorithm. The rest of the system (`ImportSession`, `Review & Correction` UI, Confidence Scoring) remains untouched.

### Stage 1: Document Routing
- **Input Detection**: The system checks if the uploaded file is a PDF or an Image.
- **PDF Handling**:
  - We will attempt a fast text-extraction using `pdfplumber`. 
  - If meaningful text grids are found, we proceed with the existing `pdfplumber` text-parser.
  - If no textual grids are found (Image-based PDF), we use `pypdfium2` to render the pages into high-resolution images and pass them to the Image Pipeline.
- **Image Handling**: Direct pass-through to the Image Pipeline.

### Stage 2: Computer Vision Preprocessing
- **Grayscale & Binarization**: Convert the image to grayscale and apply adaptive thresholding to maximize contrast for line detection.
- **Deskewing**: Detect and correct slight document rotations.

### Stage 3: OpenCV Grid Detection
- **Morphological Operations**: 
  - Use horizontal and vertical structural elements in OpenCV (`cv2.getStructuringElement`) to isolate horizontal and vertical lines.
  - Combine the horizontal and vertical masks to isolate the exact structure of the timetable grid.
- **Intersection Detection**: Find the intersection points of the grid lines to precisely map out the bounding boxes of every cell.
- **Region of Interest (ROI) Filtering**: Identify the largest contiguous grid on the page, successfully ignoring the header (Class/Semester details) and the footer (Faculty list).

### Stage 4: Cell Extraction & OCR
- **Cell Slicing**: Crop the original high-resolution image into smaller images, one for each detected cell.
- **Positional Mapping**: Based on the grid coordinates, map each cell to its corresponding column (Weekday) and row (Time Slot).
- **Targeted OCR**: Run Tesseract (`pytesseract.image_to_data` or `image_to_string`) strictly on the individual cell images. This guarantees that words belonging to the same subject are never accidentally clustered into adjacent columns.

### Stage 5: Structural Parsing & Post-Processing
- **Header Parsing**: (Optional) Use regex on the region above the grid to extract Class, Semester, and Effective Date.
- **Cell Mapping**: 
  - The top row of the grid will be parsed to verify weekdays (Monday - Saturday).
  - The leftmost column will be parsed to extract time ranges (e.g., `09:00 - 10:00`).
  - Empty cells (no text or just whitespace) will be explicitly ignored.
  - Multi-line text will be joined cleanly.
- **Confidence Scoring**: Tesseract's confidence score for each cell will be aggregated and passed directly to the `ImportSession` payload, ensuring the `Review & Correction` screen continues to show High/Medium/Low confidence indicators perfectly.

---

## Proposed Changes

### 1. Image Preprocessing

#### [MODIFY] `image_preprocessing.py`
- Enhance the preprocessing to return both the binarized image (for line detection) and a deskewed high-res image (for cropping and OCR).
- Add OpenCV functions for detecting horizontal/vertical lines and extracting cell bounding boxes.

### 2. Timetable Parser

#### [MODIFY] `timetable_parser.py`
- Completely remove the current spatial-clustering OCR logic (`extract_timetable_from_image`).
- Implement the new CV-based pipeline:
  - `detect_grid(image)`
  - `extract_cells_from_grid(image, grid_lines)`
  - `ocr_individual_cells(cells)`
  - `build_timetable_payload(ocr_results)`

## Verification Plan

### Automated Verification
- We will generate dummy DJSCE-formatted images and verify that the OpenCV morphological transformations successfully identify the grid boundaries.
- Ensure the bounding boxes properly map to row/column indexes.

### Manual Verification
- We will ask the user to upload a real DJSCE timetable image/PDF through the UI and verify that the `Review & Correction` screen successfully renders the exact time slots and subjects with high confidence.
