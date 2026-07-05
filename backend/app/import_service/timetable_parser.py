import pdfplumber
import re
import cv2
import numpy as np
from datetime import time
from typing import List, Dict, Any, Tuple
import copy

# Attempt to import Tesseract and detect availability
try:
    import pytesseract
    # In Windows, tesseract must be installed and in PATH. We'll do a quick check.
    # If not in path, this will fail.
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

from app.import_service.image_preprocessing import preprocess_image_for_ocr

WEEKDAYS_MAP = {
    "monday": 0, "mon": 0,
    "tuesday": 1, "tue": 1,
    "wednesday": 2, "wed": 2,
    "thursday": 3, "thu": 3,
    "friday": 4, "fri": 4,
    "saturday": 5, "sat": 5,
    "sunday": 6, "sun": 6
}

def parse_time(time_str: str) -> time:
    match = re.search(r'(\d{1,2})[:.](\d{2})', time_str)
    if match:
        h, m = int(match.group(1)), int(match.group(2))
        return time(hour=h, minute=m)
    return time(hour=0, minute=0)

def is_timetable_candidate(grid: List[List[Dict[str, Any]]]) -> bool:
    """
    Checks if a grid has characteristics of a timetable (e.g., contains weekdays).
    """
    for row in grid:
        for cell in row:
            if cell.get("text", "").strip().lower() in WEEKDAYS_MAP:
                return True
    return False

def _parse_grid(grid: List[List[Dict[str, Any]]], fixed_confidence: float = None) -> List[Dict[str, Any]]:
    """
    Parses a 2D grid into structured timetable slots.
    If fixed_confidence is None, it aggregates the cell confidences.
    """
    extracted_rows = []
    
    if not grid:
        return extracted_rows
        
    # Assume first row is header
    headers = [c.get("text", "").strip().lower() for c in grid[0] if c.get("text")]
    
    for row in grid[1:]:
        if not row:
            continue
            
        first_cell = row[0].get("text", "").strip().lower()
        weekday = -1
        for day_name, day_int in WEEKDAYS_MAP.items():
            if day_name in first_cell:
                weekday = day_int
                break
                
        if weekday != -1:
            for col_idx, cell in enumerate(row[1:]):
                text = cell.get("text", "").strip().replace('\n', ' ')
                if not text or text.lower() in ['lunch', 'break', 'recess', '']:
                    continue
                
                header_val = headers[col_idx + 1] if col_idx + 1 < len(headers) else ""
                times = re.findall(r'(\d{1,2}[:.]\d{2})', header_val)
                start_t = parse_time(times[0]) if len(times) > 0 else time(hour=0, minute=0)
                end_t = parse_time(times[1]) if len(times) > 1 else time(hour=1, minute=0)
                
                # Use fixed confidence if provided (PDF), otherwise use dynamic OCR cell confidence
                conf = fixed_confidence if fixed_confidence is not None else (cell.get("confidence", 60) / 100.0)
                # Keep confidence between 0.0 and 1.0
                conf = max(0.0, min(1.0, conf))
                
                extracted_rows.append({
                    "weekday": weekday,
                    "start_time": start_t.isoformat(),
                    "end_time": end_t.isoformat(),
                    "subject_name": text,
                    "confidence": conf
                })
                
    return extracted_rows

import pypdfium2 as pdfium
import tempfile
import os

def extract_timetable_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    # STAGE 1: Document Type Detection
    has_text = False
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text and len(text.strip()) > 50:  # Threshold to ensure meaningful text exists
                has_text = True
                break

    if has_text:
        # TEXT PDF Pipeline (using pdfplumber)
        candidate_grids = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if not table:
                        continue
                    
                    grid = []
                    for row in table:
                        grid_row = []
                        for cell in row:
                            grid_row.append({"text": str(cell) if cell else "", "confidence": 100})
                        grid.append(grid_row)
                        
                    if is_timetable_candidate(grid):
                        candidate_grids.append(grid)
                        
        if len(candidate_grids) > 1:
            raise ValueError("MULTIPLE_TIMETABLES_DETECTED")
            
        if candidate_grids:
            return _parse_grid(candidate_grids[0], fixed_confidence=0.9)
        else:
            raise ValueError("No timetable grid structure could be extracted from this Text PDF. The layout might not be supported.")
    else:
        # IMAGE PDF Pipeline (convert to images -> Image Pipeline)
        if not TESSERACT_AVAILABLE:
            raise ValueError("No text-based timetable data found. Document appears to be an image-based PDF, but OCR is disabled on this server.")
            
        pdf_doc = pdfium.PdfDocument(pdf_path)
        extracted_rows = []
        
        for i in range(len(pdf_doc)):
            page = pdf_doc[i]
            # Render at ~300 DPI (72 * (300/72))
            bitmap = page.render(scale=4.166)
            pil_image = bitmap.to_pil()
            
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp_path = tmp.name
                
            try:
                pil_image.save(tmp_path)
                rows = extract_timetable_from_image(tmp_path)
                if rows:
                    if extracted_rows:
                        raise ValueError("MULTIPLE_TIMETABLES_DETECTED")
                    extracted_rows = rows
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
                    
        if not extracted_rows:
            raise ValueError("No timetable data found. We could not extract any valid timetable structure from this document.")
            
        return extracted_rows


def detect_grid(binary_img: np.ndarray) -> List[Tuple[int, int, int, int]]:
    # 1. Invert binary image to get white lines on black background
    # (assuming binary_img from preprocess is black lines on white)
    binary_inv = cv2.bitwise_not(binary_img)

    # 2. Detect horizontal lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    detect_horizontal = cv2.morphologyEx(binary_inv, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    cnts_h = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_h = cnts_h[0] if len(cnts_h) == 2 else cnts_h[1]
    for c in cnts_h:
        cv2.drawContours(detect_horizontal, [c], -1, 255, -1)

    # 3. Detect vertical lines
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    detect_vertical = cv2.morphologyEx(binary_inv, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
    cnts_v = cv2.findContours(detect_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts_v = cnts_v[0] if len(cnts_v) == 2 else cnts_v[1]
    for c in cnts_v:
        cv2.drawContours(detect_vertical, [c], -1, 255, -1)

    # 4. Combine horizontal and vertical lines to form the grid
    grid = cv2.add(detect_horizontal, detect_vertical)

    # 5. Find contours of the individual cells (enclosed regions)
    contours, _ = cv2.findContours(grid, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cells = []
    for c in contours:
        area = cv2.contourArea(c)
        # Thresholds to filter out noise and the outer page boundary
        if area > 1000 and area < 500000:
            x, y, w, h = cv2.boundingRect(c)
            cells.append((x, y, w, h))

    return cells

def extract_cells_from_grid(image: np.ndarray, cells: List[Tuple[int, int, int, int]]) -> Tuple[List[List[Dict[str, Any]]], Dict[str, int]]:
    # Sort cells strictly by Y first (top to bottom)
    cells.sort(key=lambda b: b[1])

    rows = []
    current_row = []
    y_thresh = 20

    for cell in cells:
        x, y, w, h = cell
        if not current_row:
            current_row.append(cell)
        else:
            avg_y = sum(c[1] for c in current_row) / len(current_row)
            if abs(y - avg_y) < y_thresh:
                current_row.append(cell)
            else:
                # Sort current row by X before appending (left to right)
                current_row.sort(key=lambda b: b[0])
                rows.append(current_row)
                current_row = [cell]
    if current_row:
        current_row.sort(key=lambda b: b[0])
        rows.append(current_row)

    # Calculate statistics
    num_rows = len(rows)
    num_columns = max(len(r) for r in rows) if rows else 0

    all_widths = [c[2] for c in cells]
    median_width = np.median(all_widths) if all_widths else 0
    merged_cells_count = 0

    structured_grid = []
    
    for r_idx, row in enumerate(rows):
        grid_row = []
        for c_idx, cell in enumerate(row):
            x, y, w, h = cell
            is_merged = False
            if w > median_width * 1.5:
                merged_cells_count += 1
                is_merged = True
                
            # Crop the cell from the original image (ignoring a 2px boundary to avoid OCR noise from the grid lines)
            # Ensure coordinates are within image bounds
            img_h, img_w = image.shape[:2]
            crop_y1, crop_y2 = max(0, y+2), min(img_h, y+h-2)
            crop_x1, crop_x2 = max(0, x+2), min(img_w, x+w-2)
            
            crop_img = image[crop_y1:crop_y2, crop_x1:crop_x2]
            
            grid_row.append({
                "x": x, "y": y, "w": w, "h": h,
                "is_merged": is_merged,
                "image": crop_img
            })
        structured_grid.append(grid_row)

    stats = {
        "rows": num_rows,
        "columns": num_columns,
        "merged_cells": merged_cells_count
    }
    return structured_grid, stats

def ocr_individual_cells(structured_grid: List[List[Dict[str, Any]]]) -> List[List[Dict[str, Any]]]:
    if not TESSERACT_AVAILABLE:
        raise NotImplementedError("OCR_UNAVAILABLE")
        
    for row in structured_grid:
        for cell in row:
            # Run OCR on the individual cell image
            img = cell["image"]
            try:
                # Use --psm 6 (Assume a single uniform block of text) which works well for cells
                data = pytesseract.image_to_data(img, config='--psm 6', output_type=pytesseract.Output.DICT)
                words = []
                total_conf = 0.0
                
                for i in range(len(data['text'])):
                    text = data['text'][i].strip()
                    conf = float(data['conf'][i])
                    # Ignore empty strings and -1 confidence (which usually indicates structural data, not text)
                    if conf > -1 and text:
                        words.append(text)
                        total_conf += conf
                        
                final_text = ' '.join(words)
                final_conf = (total_conf / len(words)) if words else 0.0
                
                cell["text"] = final_text
                cell["confidence"] = final_conf
                
            except pytesseract.TesseractNotFoundError:
                raise NotImplementedError("OCR_UNAVAILABLE")
            
            # Remove the numpy image from memory now that we have the text
            del cell["image"]
            
    return structured_grid

def parse_djsce_cell(text: str) -> Dict[str, str]:
    """
    Parses a DJSCE timetable cell to extract Subject, Faculty, Room, and Batch.
    """
    result = {
        "subject": "",
        "faculty": "",
        "room": "",
        "batch": ""
    }
    
    if not text.strip():
        return result
        
    # Heuristic parsing for DJSCE format
    # 1. Faculty usually enclosed in parentheses e.g., (ABC)
    faculty_match = re.search(r'\(([A-Za-z\s.,]+)\)', text)
    if faculty_match:
        result["faculty"] = faculty_match.group(1).strip()
        text = text.replace(faculty_match.group(0), "")
        
    # 2. Batch usually "Batch A" or "B1"
    batch_match = re.search(r'(?i)(?:Batch\s*[A-Z1-9]|B[1-9])', text)
    if batch_match:
        result["batch"] = batch_match.group(0).strip()
        text = text.replace(batch_match.group(0), "")
        
    # 3. Room usually "Room 201", "Lab 3", "CR 31"
    room_match = re.search(r'(?i)(?:Room|Lab|CR|Class)\s*\w+', text)
    if room_match:
        result["room"] = room_match.group(0).strip()
        text = text.replace(room_match.group(0), "")
        
    # 4. Subject is whatever is left over
    result["subject"] = re.sub(r'\s+', ' ', text).strip()
    
    return result

def build_djsce_timetable_payload(structured_grid: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    extracted_rows = []
    
    if not structured_grid:
        return extracted_rows
        
    # Identify the header row (contains time strings)
    header_row = []
    for row in structured_grid:
        has_time = any(re.search(r'\d{1,2}[:.]\d{2}', cell.get("text", "")) for cell in row)
        if has_time:
            header_row = row
            break
            
    if not header_row:
        raise ValueError("VALIDATION_ERROR: Missing time slots in header.")
        
    for row in structured_grid:
        if not row or row == header_row:
            continue
            
        first_cell_text = row[0].get("text", "").strip().lower()
        weekday = -1
        for day_name, day_int in WEEKDAYS_MAP.items():
            if day_name in first_cell_text:
                weekday = day_int
                break
                
        # If we have a row but no weekday was detected, it might be an ambiguous row (OCR failure)
        # We will map it to weekday=0 (Monday) but set confidence to 0 so the user flags it
        is_ambiguous_row = False
        if weekday == -1:
            if any(cell.get("text", "").strip() for cell in row[1:]):
                # Row has data but no weekday. Send to Review & Correction as ambiguous.
                weekday = 0
                is_ambiguous_row = True
            else:
                continue # completely empty row
                
        for col_idx in range(1, len(row)):
            cell = row[col_idx]
            text = cell.get("text", "").strip()
            
            # Keep ambiguous cells (text is empty but it was detected as a cell in the grid)
            # if we are in an ambiguous row, or if it's merged but empty.
            if not text and not is_ambiguous_row and not cell.get("is_merged"):
                continue
                
            if "lunch" in text.lower() or "break" in text.lower() or "recess" in text.lower():
                continue
                
            cell_x = cell["x"]
            cell_w = cell["w"]
            cell_end_x = cell_x + cell_w
            
            start_t = time(hour=0, minute=0)
            end_t = time(hour=1, minute=0)
            
            # Intelligently map time slots for standard AND merged cells
            matching_headers = []
            for h in header_row:
                h_x, h_w = h["x"], h["w"]
                # Check if header cell overlaps with data cell's X span
                # We use a slight tolerance (10px) to account for column borders
                overlap = max(0, min(cell_end_x, h_x + h_w) - max(cell_x, h_x))
                if overlap > 10:
                    matching_headers.append(h)
                    
            if matching_headers:
                # Get start time from the first overlapping header
                first_header = matching_headers[0].get("text", "")
                t1 = re.findall(r'(\d{1,2}[:.]\d{2})', first_header)
                if t1:
                    start_t = parse_time(t1[0])
                    
                # Get end time from the last overlapping header (handles merged cells spanning multiple slots)
                last_header = matching_headers[-1].get("text", "")
                t2 = re.findall(r'(\d{1,2}[:.]\d{2})', last_header)
                if len(t2) > 1:
                    end_t = parse_time(t2[1])
                elif len(t1) > 1:
                    end_t = parse_time(t1[1])

            parsed_data = parse_djsce_cell(text)
            
            conf = max(0.0, min(1.0, cell.get("confidence", 0.0) / 100.0))
            if is_ambiguous_row or not parsed_data["subject"]:
                conf = 0.0 # Force to Low Confidence in UI so user must review
                
            # Allow empty subjects to pass through to Review UI if it's an ambiguous detected cell
            extracted_rows.append({
                "weekday": weekday,
                "start_time": start_t.isoformat(),
                "end_time": end_t.isoformat(),
                "subject_name": parsed_data["subject"] if parsed_data["subject"] else "Unknown",
                "faculty": parsed_data["faculty"],
                "room": parsed_data["room"],
                "batch": parsed_data["batch"],
                "confidence": conf,
                "is_merged": cell.get("is_merged", False)
            })
                
    if not extracted_rows:
        raise ValueError("VALIDATION_ERROR: Missing rows or completely empty timetable.")
        
    return extracted_rows

def extract_timetable_from_image(image_path: str) -> List[Dict[str, Any]]:
    if not TESSERACT_AVAILABLE:
        raise NotImplementedError("OCR_UNAVAILABLE")
        
    # Stage 2: Preprocess
    binary_img = preprocess_image_for_ocr(image_path)
    
    # Stage 3: Grid Detection
    cells_rects = detect_grid(binary_img)
    if not cells_rects:
        raise ValueError("No timetable grid structure could be detected in this image.")
        
    # Stage 4: Cell Extraction
    # We pass the binary image for OCR extraction as it is already contrast-enhanced and deskewed
    structured_grid, stats = extract_cells_from_grid(binary_img, cells_rects)
    
    # Stage 5: OCR
    structured_grid = ocr_individual_cells(structured_grid)
    
    # Stage 6 & 7: Semantic Parser & Validation
    extracted_rows = build_djsce_timetable_payload(structured_grid)
    
    # Wait, where do we output the stats?
    # The ImportSession schema expects List[Dict[str, Any]] as extracted_payload.
    # The stats are for debugging/logging, we can just print them or let the frontend calculate them from the payload.
    # We will just return the extracted rows to seamlessly integrate with ImportSession.
    
    return extracted_rows
