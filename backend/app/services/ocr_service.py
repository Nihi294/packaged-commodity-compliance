import pytesseract
from PIL import Image
import os
import cv2
import re
from collections import defaultdict
from app.services.declaration_extractor import extract_declarations

# ─────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

folder_path = os.path.dirname(os.path.abspath(__file__))

SUPPORTED = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif', '.jfif')

# ─────────────────────────────────────────────
# STEP 1: IMAGE CLEANING
# ─────────────────────────────────────────────

def clean_image(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh

# ─────────────────────────────────────────────
# STEP 2: GROUP IMAGES BY PRODUCT NAME
# ─────────────────────────────────────────────

def group_images():
    products = defaultdict(list)

    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(SUPPORTED):
            continue
        if filename.startswith('cleaned_'):
            continue

        # Split by last underscore to get product name
        # dettol_front.jpg → product = "dettol", part = "front"
        name_without_ext = os.path.splitext(filename)[0]

        if '_' in name_without_ext:
            product_name = '_'.join(name_without_ext.split('_')[:-1])
        else:
            # No underscore — treat whole name as product
            product_name = name_without_ext

        products[product_name].append(filename)

    return products

# ─────────────────────────────────────────────
# STEP 3: EXTRACT TEXT FROM ALL IMAGES OF ONE PRODUCT
# ─────────────────────────────────────────────

def extract_merged_text(filenames):
    merged_text = ""

    for filename in filenames:
        image_path = os.path.join(folder_path, filename)

        # Clean image
        cleaned = clean_image(image_path)

        # Save cleaned version
        clean_path = os.path.join(folder_path, 'cleaned_' + filename)
        cv2.imwrite(clean_path, cleaned)

        # Extract text
        text = pytesseract.image_to_string(Image.open(clean_path))

        print(f"    → Extracted from {filename}: {len(text.strip())} characters")

        merged_text += f"\n--- From {filename} ---\n" + text

    return merged_text

# ─────────────────────────────────────────────
# FASTAPI ADAPTER
# Connects Member 1's OCR functions to /scan
# ─────────────────────────────────────────────

class OCRService:
    def __init__(self, tesseract_cmd=None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def process_images(self, paths):
        global folder_path

        if not paths:
            return {
                "images": [],
                "merged_text": "",
                "extracted_fields": extract_declarations(merged_text),
            }

        original_folder = folder_path
        folder_path = str(paths[0].parent)

        try:
            filenames = [path.name for path in paths]

            merged_text = extract_merged_text(filenames)

            image_results = []

            for path in paths:
                clean_path = path.parent / ("cleaned_" + path.name)

                text = pytesseract.image_to_string(
                    Image.open(clean_path)
                )

                image_results.append({
                    "file_path": str(path),
                    "text": text,
                    "ocr_success": bool(text.strip()),
                })

            return {
                "images": image_results,
                "merged_text": merged_text,
                "extracted_fields": {},
            }

        finally:
            folder_path = original_folder