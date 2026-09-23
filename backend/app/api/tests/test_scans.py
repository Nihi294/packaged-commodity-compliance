import asyncio
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException, UploadFile

from app.api import scans
from app.db.models import Product
from app.services.ocr_service import OCRService


class FakeSession:
    def __init__(self, products=None):
        self.records = list(products or [])
        self.next_id = max((record.id for record in self.records), default=0) + 1

    def get(self, model, record_id):
        return next((record for record in self.records if isinstance(record, model) and record.id == record_id), None)

    def add(self, record):
        self.records.append(record)

    def flush(self):
        for record in self.records:
            if getattr(record, "id", None) is None:
                record.id = self.next_id
                self.next_id += 1

    def commit(self):
        return None

    def refresh(self, record):
        return record


def upload(filename: str, content: bytes = b"image") -> UploadFile:
    return UploadFile(filename=filename, file=BytesIO(content), headers={"content-type": "image/png"})


def fake_assessment(candidate):
    return {"rule_results": [{"category": "labeling", "status": "needs_verification"}], "candidate": candidate}


def test_scan_without_product_id_creates_product_and_processes_uploaded_images(tmp_path, monkeypatch):
    db = FakeSession()
    captured_paths = []
    assessment_candidates = []

    class FakeOCR:
        def __init__(self, **kwargs):
            pass

        def process_images(self, paths):
            captured_paths.extend(paths)
            return {
                "images": [
                    {"filename": Path(path).name, "text": "Net Quantity: 500 g", "ocr_success": True}
                    for path in paths
                ],
                "merged_text": "--- From front.png ---\nNet Quantity: 500 g",
                "extracted_fields": {"net_quantity": {"value": "500 g", "source": "ocr"}},
            }

    monkeypatch.setattr(scans, "OCRService", FakeOCR)
    monkeypatch.setattr(scans, "generate_initial_assessment", lambda candidate: assessment_candidates.append(candidate) or fake_assessment(candidate))
    monkeypatch.setattr(scans.settings, "upload_dir", str(tmp_path))

    response = asyncio.run(
        scans.create_scan(
            [upload("front.png", b"front-bytes"), upload("back.png", b"back-bytes")],
            '{"name": "New cereal", "brand": "Fresh"}',
            None,
            db,
            SimpleNamespace(id=11),
        )
    )

    product = next(record for record in db.records if isinstance(record, Product))
    scan = next(record for record in db.records if isinstance(record, scans.Scan))
    assert product.name == "New cereal"
    assert scan.product_id == product.id
    assert [Path(path).name for path in captured_paths] == ["front.png", "back.png"]
    assert Path(captured_paths[0]).read_bytes() == b"front-bytes"
    assert assessment_candidates[0]["net_quantity"]["value"] == "500 g"
    assert response["status"] == "assessment_ready"


def test_scan_with_existing_product_uses_that_product(tmp_path, monkeypatch):
    existing = Product(id=7, name="Existing product", brand="Brand", category="food")
    db = FakeSession([existing])
    monkeypatch.setattr(scans, "OCRService", lambda **kwargs: SimpleNamespace(process_images=lambda paths: {"images": [{"filename": "image.png", "text": "", "ocr_success": True}], "merged_text": "", "extracted_fields": {}}))
    monkeypatch.setattr(scans, "generate_initial_assessment", fake_assessment)
    monkeypatch.setattr(scans.settings, "upload_dir", str(tmp_path))

    asyncio.run(scans.create_scan([upload("image.png")], "{}", 7, db, SimpleNamespace(id=11)))

    scans_created = [record for record in db.records if isinstance(record, scans.Scan)]
    assert len(scans_created) == 1
    assert scans_created[0].product_id == 7
    assert len([record for record in db.records if isinstance(record, Product)]) == 1


def test_scan_with_invalid_product_returns_404():
    with pytest.raises(HTTPException) as error:
        asyncio.run(scans.create_scan([upload("image.png")], "{}", 999, FakeSession(), SimpleNamespace(id=11)))

    assert error.value.status_code == 404
    assert error.value.detail == "Product not found"


def test_ocr_reports_failure_and_empty_result(tmp_path):
    broken = tmp_path / "broken.png"
    broken.write_bytes(b"not an image")
    empty = tmp_path / "empty.png"
    empty.write_bytes(b"not an image")

    failure = OCRService(ocr_reader=lambda image: "").process_images([broken])
    empty_result = OCRService(ocr_reader=lambda image: "").process_images([empty])

    assert failure["images"][0]["ocr_success"] is False
    assert failure["images"][0]["error"]
    assert empty_result["merged_text"] == ""
    assert empty_result["extracted_fields"] == {}