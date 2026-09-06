import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.auth import require_officer
from app.core.config import settings
from app.db.database import get_db
from app.db.models import Evidence, ExtractedDeclaration, Image, Inspection, InspectionFinding, OcrResult, Product, Scan, User
from app.rule_engine.assessment import generate_initial_assessment
from app.services.ocr_service import OCRService

router = APIRouter()


def _candidate_product(product_data: dict[str, Any], extracted: dict[str, Any], merged_text: str) -> dict[str, Any]:
    product = dict(product_data)
    product.update(extracted)
    product["source_type"] = "physical_package"
    product["ocr_text"] = merged_text
    return product


def _field_value(value: Any) -> Any:
    return value.get("value") if isinstance(value, dict) else value


@router.get("/")
def scan_status() -> dict[str, str]:
    return {"message": "Scan endpoint accepts multipart package images."}


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_scan(
    images: list[UploadFile] = File(...),
    product_data: str = Form(default="{}"),
    product_id: int | None = Form(default=None),
    db: Session = Depends(get_db),
    officer: User = Depends(require_officer),
) -> dict[str, Any]:
    if not images:
        raise HTTPException(status_code=422, detail="At least one package image is required")
    try:
        supplied_product = json.loads(product_data or "{}")
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail="product_data must be valid JSON") from exc
    if not isinstance(supplied_product, dict):
        raise HTTPException(status_code=422, detail="product_data must be a JSON object")

    scan = Scan(user_id=officer.id, product_id=product_id, status="ocr_processing")
    db.add(scan)
    db.flush()
    scan_dir = Path(settings.upload_dir) / "scans" / str(scan.id)
    scan_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    image_rows: list[Image] = []
    for upload in images:
        filename = Path(upload.filename or "image.bin").name
        path = scan_dir / filename
        path.write_bytes(await upload.read())
        image_row = Image(scan_id=scan.id, file_path=str(path), image_type=upload.content_type)
        db.add(image_row)
        image_rows.append(image_row)
        paths.append(path)
    db.flush()

    ocr_result = OCRService(tesseract_cmd=settings.tesseract_cmd).process_images(paths)
    for image_row, image_result in zip(image_rows, ocr_result["images"], strict=True):
        db.add(OcrResult(scan_id=scan.id, image_id=image_row.id, raw_text=image_result["text"], confidence=1.0 if image_result["ocr_success"] else 0.0))
        db.add(Evidence(scan_id=scan.id, file_path=image_row.file_path, description=f"OCR source image: {image_row.file_path}", source="AI"))
    extracted = ocr_result["extracted_fields"]
    for declaration_type, value in extracted.items():
        db.add(ExtractedDeclaration(scan_id=scan.id, declaration_type=declaration_type, value=str(_field_value(value)), source_data={"ocr": value, "merged_text": ocr_result["merged_text"]}))

    candidate = _candidate_product(supplied_product, extracted, ocr_result["merged_text"])
    if product_id is not None:
        product = db.get(Product, product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        candidate.setdefault("product_name", product.name)
        candidate.setdefault("brand", product.brand)
        candidate.setdefault("category", product.category)
    assessment = generate_initial_assessment(candidate)
    inspection = Inspection(scan_id=scan.id, user_id=officer.id, product_data=candidate, assessment_data=assessment, evidence_data=[{"source_image": str(path)} for path in paths])
    db.add(inspection)
    db.flush()
    for result in assessment["rule_results"]:
        db.add(InspectionFinding(inspection_id=inspection.id, source="AI", category=result.get("category", "Other"), title=result.get("rule_title") or "OCR-assisted rule assessment", description=result.get("explanation") or "OCR-assisted rule assessment.", applicable_rule=result.get("rule_number"), original_ai_status=result.get("status"), ai_confidence=result.get("confidence"), ai_evidence=result.get("evidence"), status=result.get("status"), evidence_data=[]))
    scan.status = "assessment_ready"
    db.commit()
    db.refresh(inspection)
    return {"scan_id": scan.id, "inspection_id": inspection.id, "status": scan.status, "ocr": ocr_result, "assessment": assessment}
