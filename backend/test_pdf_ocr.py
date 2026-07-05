import pypdfium2 as pdfium
import pdfplumber
import cv2
import numpy as np
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# 1. Create a dummy text PDF
c = canvas.Canvas("dummy_text.pdf", pagesize=letter)
c.drawString(100, 700, "Monday 09:00 10:00 Math")
c.save()

# 2. Create a dummy image PDF
img = np.ones((800, 800, 3), dtype=np.uint8) * 255
cv2.putText(img, "Monday 09:00 10:00 Physics", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
cv2.imwrite("dummy.jpg", img)

c = canvas.Canvas("dummy_image.pdf", pagesize=letter)
c.drawImage("dummy.jpg", 0, 0, 600, 600)
c.save()

from app.import_service.timetable_parser import extract_timetable_from_pdf

print("Extracting Text PDF:")
try:
    print(extract_timetable_from_pdf("dummy_text.pdf"))
except Exception as e:
    print(e)

print("Extracting Image PDF:")
try:
    print(extract_timetable_from_pdf("dummy_image.pdf"))
except Exception as e:
    print(e)
