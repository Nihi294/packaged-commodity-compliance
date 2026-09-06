from pathlib import Path

from PIL import Image

from app.services.ocr_service import OCRService, extract_declarations
from app.main import app
from app.rule_engine.assessment import generate_initial_assessment


def make_image(path: Path) -> None:
    Image.new("RGB", (20, 20), "white").save(path)


def test_extract_declarations_is_candidate_data_only():
    fields = extract_declarations("Manufactured by: XYZ Foods\nNet Quantity: 500 g\nMRP: Rs 120\nMFD: 01/2026")
    assert fields["manufacturer_name"]["value"] == "XYZ Foods"
    assert fields["net_quantity"]["value"] == "500 g"
    assert fields["mrp"]["value"] == "120"
    assert fields["manufacturing_date"]["value"] == "01/2026"


def test_processes_multiple_images_and_merges_source_attributed_text(tmp_path):
    first = tmp_path / "front.png"
    second = tmp_path / "back.png"
    make_image(first)
    make_image(second)
    service = OCRService(ocr_reader=lambda image: "Net Quantity: 500 g" if image is not None else "")
    result = service.process_images([first, second])
    assert len(result["images"]) == 2
    assert result["images"][0]["ocr_success"] is True
    assert "front.png" in result["merged_text"]
    assert "back.png" in result["merged_text"]
    assert result["extracted_fields"]["net_quantity"]["value"] == "500 g"


def test_unsupported_image_is_reported_without_stopping_other_images(tmp_path):
    unsupported = tmp_path / "notes.txt"
    supported = tmp_path / "front.png"
    unsupported.write_text("not an image", encoding="utf-8")
    make_image(supported)
    service = OCRService(ocr_reader=lambda image: "MRP: Rs 120")
    result = service.process_images([unsupported, supported])
    assert result["images"][0]["processing_success"] is False
    assert result["images"][0]["error"] == "Unsupported image format"
    assert result["images"][1]["ocr_success"] is True


def test_ocr_failure_is_structured(tmp_path):
    image_path = tmp_path / "broken.png"
    image_path.write_bytes(b"not a valid image")
    result = OCRService().process_images([image_path])
    assert result["images"][0]["processing_success"] is False
    assert result["images"][0]["ocr_success"] is False
    assert result["images"][0]["error"]


def test_missing_tesseract_is_structured(tmp_path):
    image_path = tmp_path / "front.png"
    make_image(image_path)
    service = OCRService(tesseract_cmd=str(tmp_path / "missing-tesseract.exe"))
    result = service.process_images([image_path])
    assert result["images"][0]["processing_success"] is True
    assert result["images"][0]["ocr_success"] is False
    assert result["images"][0]["error"]


def test_ocr_candidates_reach_existing_rule_engine_and_scan_route_exists():
    fields = extract_declarations("Net Quantity: 500 g\nMRP: Rs 120")
    assessment = generate_initial_assessment({"category": "food", **fields})
    assert assessment["rule_results"]
    paths = app.openapi()["paths"]
    assert "/scan" in paths
    assert "/api/inspections/{inspection_id}/final-report" in paths
