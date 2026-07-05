import cv2
import numpy as np
from PIL import Image, ExifTags

def apply_exif_rotation(img_path: str) -> np.ndarray:
    """
    Reads an image from disk using Pillow to apply EXIF orientation data.
    Returns a numpy array suitable for OpenCV (BGR).
    """
    try:
        with Image.open(img_path) as img:
            # We don't want to use ImageOps.exif_transpose because we want strict control
            if hasattr(img, '_getexif') and img._getexif() is not None:
                exif = img._getexif()
                orientation_key = None
                for k, v in ExifTags.TAGS.items():
                    if v == 'Orientation':
                        orientation_key = k
                        break
                        
                if orientation_key and orientation_key in exif:
                    orientation = exif[orientation_key]
                    if orientation == 3:
                        img = img.rotate(180, expand=True)
                    elif orientation == 6:
                        img = img.rotate(270, expand=True)
                    elif orientation == 8:
                        img = img.rotate(90, expand=True)
                        
            # Convert to OpenCV format
            # Pillow uses RGB, OpenCV uses BGR
            img_rgb = img.convert('RGB')
            cv_img = np.array(img_rgb)
            # Convert RGB to BGR
            cv_img = cv_img[:, :, ::-1].copy()
            return cv_img
    except Exception as e:
        # Fallback to standard cv2 imread if Pillow fails
        return cv2.imread(img_path)

def preprocess_image_for_ocr(img_path: str) -> np.ndarray:
    """
    Deterministically processes the image for optimal OCR extraction.
    1. EXIF Auto-rotation
    2. Grayscale conversion
    3. Contrast enhancement (CLAHE)
    4. Adaptive thresholding
    """
    # 1. Read and apply EXIF rotation
    img = apply_exif_rotation(img_path)
    if img is None:
        raise ValueError("Failed to load image.")

    # 2. Convert to Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. Contrast enhancement using CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 4. Adaptive Thresholding / Binarization
    # Using Gaussian adaptive thresholding to cleanly separate text from varying background shadows
    binary = cv2.adaptiveThreshold(
        enhanced, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 
        11, 
        2
    )
    
    return binary
