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

def extract_timetable_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    candidate_grids = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if not table:
                    continue
                
                # Convert raw string table to grid of dicts
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
        
    if not candidate_grids:
        return []
        
    return _parse_grid(candidate_grids[0], fixed_confidence=0.9)


def extract_timetable_from_image(image_path: str) -> List[Dict[str, Any]]:
    if not TESSERACT_AVAILABLE:
        raise NotImplementedError("OCR_UNAVAILABLE")
        
    # Preprocess the image
    binary_img = preprocess_image_for_ocr(image_path)
    
    # Run Tesseract OCR with detailed output
    try:
        # dict with keys: 'level', 'page_num', 'block_num', 'par_num', 'line_num', 'word_num', 'left', 'top', 'width', 'height', 'conf', 'text'
        data = pytesseract.image_to_data(binary_img, output_type=pytesseract.Output.DICT)
    except pytesseract.TesseractNotFoundError:
        raise NotImplementedError("OCR_UNAVAILABLE")
        
    # Reconstruct a grid via spatial clustering
    # 1. Extract valid words
    words = []
    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        if int(data['conf'][i]) > -1 and text:
            words.append({
                "text": text,
                "left": data['left'][i],
                "top": data['top'][i],
                "width": data['width'][i],
                "height": data['height'][i],
                "conf": float(data['conf'][i])
            })
            
    if not words:
        return []
        
    # 2. Cluster into lines based on Y-axis (top)
    # Sort by Y first
    words.sort(key=lambda w: w['top'])
    lines = []
    current_line = []
    y_threshold = 15 # pixels tolerance for same line
    
    for word in words:
        if not current_line:
            current_line.append(word)
        else:
            avg_y = sum(w['top'] for w in current_line) / len(current_line)
            if abs(word['top'] - avg_y) < y_threshold:
                current_line.append(word)
            else:
                lines.append(current_line)
                current_line = [word]
    if current_line:
        lines.append(current_line)
        
    # 3. Cluster lines into columns based on X-axis (left)
    # We will build a unified set of column boundaries across the document
    all_lefts = [w['left'] for w in words]
    all_lefts.sort()
    cols = []
    x_threshold = 30 # pixels tolerance for column alignment
    
    current_col = []
    for x in all_lefts:
        if not current_col:
            current_col.append(x)
        else:
            avg_x = sum(current_col) / len(current_col)
            if abs(x - avg_x) < x_threshold:
                current_col.append(x)
            else:
                cols.append(sum(current_col) / len(current_col))
                current_col = [x]
    if current_col:
        cols.append(sum(current_col) / len(current_col))
        
    cols.sort()
    
    # Now build the grid
    grid = []
    for line in lines:
        row = [{"text": "", "confidence": 0.0, "count": 0} for _ in cols]
        for word in line:
            # Find the closest column
            col_idx = min(range(len(cols)), key=lambda i: abs(cols[i] - word['left']))
            if row[col_idx]["text"]:
                row[col_idx]["text"] += " " + word["text"]
                row[col_idx]["confidence"] += word["conf"]
                row[col_idx]["count"] += 1
            else:
                row[col_idx]["text"] = word["text"]
                row[col_idx]["confidence"] = word["conf"]
                row[col_idx]["count"] = 1
                
        # Average the confidence
        final_row = []
        for cell in row:
            avg_conf = (cell["confidence"] / cell["count"]) if cell["count"] > 0 else 0.0
            final_row.append({"text": cell["text"], "confidence": avg_conf})
        grid.append(final_row)
        
    # Validate multiple timetables
    # Since we grouped everything into one grid, if there are multiple timetables they will appear 
    # as multiple header rows or repeated weekday clusters. 
    # Let's count weekday occurrences in the first non-empty column of each row
    weekday_rows = 0
    for row in grid:
        for cell in row:
            if cell["text"].strip().lower() in WEEKDAYS_MAP:
                weekday_rows += 1
                break # count once per row
                
    if weekday_rows > 7:
        # A single timetable should have at most 7 days
        raise ValueError("MULTIPLE_TIMETABLES_DETECTED")
        
    # In OCR, sometimes grids get split weirdly, but we'll consider it one candidate
    # Let's parse the grid. Pass fixed_confidence=None so it uses dynamic cell confidence
    return _parse_grid(grid, fixed_confidence=None)
