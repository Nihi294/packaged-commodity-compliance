"""Callable OCR/image-processing adapter based on Member 1's prototype."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Callable

try:
    import cv2
except ImportError:  # pragma: no cover - reported as a structured processing failure
    cv2 = None

try:
    import pytesseract
    from PIL import Image
except ImportError:  # pragma: no cover - reported as a structured OCR failure
    pytesseract = None
    Image = None

SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif", ".jfif"}


class OCRService:
    def __init__(self, tesseract_cmd: str | None = None, ocr_reader: Callable[[Any], str] | None = None) -> None:
        self.ocr_reader = ocr_reader
        if pytesseract is not None and tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    @staticmethod
    def clean_image(image_path: str | Path) -> Any:
        if cv2 is None:
            raise RuntimeError("OpenCV is not installed")
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError("Image could not be opened")
        image = cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
        return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    def extract_text(self, image_path: str | Path) -> str:
        cleaned = self.clean_image(image_path)
        return self._read_cleaned(cleaned)

    def _read_cleaned(self, cleaned: Any) -> str:
        if self.ocr_reader is not None:
            return str(self.ocr_reader(cleaned) or "")
        if pytesseract is None or Image is None:
            raise RuntimeError("Tesseract OCR dependencies are not installed")
        return str(pytesseract.image_to_string(Image.fromarray(cleaned)) or "")

    def process_images(self, image_paths: list[str | Path]) -> dict[str, Any]:
        sources: list[dict[str, Any]] = []
        for image_path in image_paths:
            path = Path(image_path)
            item: dict[str, Any] = {"source_image": str(path), "filename": path.name, "processing_success": False, "ocr_success": False, "text": "", "error": None}
            if path.suffix.lower() not in SUPPORTED_SUFFIXES:
                item["error"] = "Unsupported image format"
                sources.append(item)
                continue
            try:
                cleaned = self.clean_image(path)
                item["processing_success"] = True
                item["text"] = self._read_cleaned(cleaned)
                item["ocr_success"] = True
            except Exception as exc:
                item["error"] = str(exc)
            sources.append(item)
        merged = "\n".join(f"--- From {item['filename']} ---\n{item['text']}" for item in sources if item["text"])
        return {"images": sources, "merged_text": merged, "extracted_fields": extract_declarations(merged)}


def extract_declarations(text: str) -> dict[str, Any]:
    """Extract candidate fields only; the existing rule engine remains authoritative."""
    fields: dict[str, Any] = {}
    patterns = {
        "net_quantity": r"(?:net\s*(?:quantity|wt|weight)|quantity)\s*[:\-]?\s*([0-9]+(?:\.[0-9]+)?\s*(?:kg|g|mg|l|litre|liter|ml))",
        "mrp": r"(?:m\.?r\.?p\.?|maximum\s*retail\s*price)\s*[:\-]?\s*(?:rs\.?|inr|₹)?\s*([0-9]+(?:\.[0-9]+)?)",
        "manufacturing_date": r"(?:mfd|manufactured|date\s*of\s*(?:mfg|manufacture|packing))\s*[:\-]?\s*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4}|[0-9]{1,2}[/-][0-9]{4})",
        "expiry": r"(?:exp|expiry|best\s*before)\s*[:\-]?\s*([^\n]+)",
        "consumer_contact": r"(?:consumer\s*care|customer\s*care|helpline)\s*[:\-]?\s*([^\n]+)",
    }
    for field, pattern in patterns.items():
        match = re.search(pattern, text or "", re.IGNORECASE)
        if match:
            fields[field] = {"value": match.group(1).strip(), "source": "ocr", "confidence": 0.6}
    manufacturer = re.search(r"(?:manufactured|packed|marketed)\s*by\s*[:\-]?\s*([^\n]+)", text or "", re.IGNORECASE)
    if manufacturer:
        fields["manufacturer_name"] = {"value": manufacturer.group(1).strip(), "source": "ocr", "confidence": 0.55}
    return fields