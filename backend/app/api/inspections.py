import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.auth import require_officer
from app.db.database import get_db
from app.db.models import Inspection, InspectionComment, InspectionFinding, InspectionObservation, InspectionReport, User
from app.reports.service import build_initial_assessment, build_officer_verified_report, render_docx, render_pdf
from app.schemas.inspection import CommentCreate, FindingCreate, FindingVerification, InspectionCreate, ObservationCreate, VerificationCreate

router = APIRouter()


def _get(db: Session, inspection_id: int) -> Inspection:
    inspection = db.get(Inspection, inspection_id)
    if inspection is None:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return inspection


def _finding_dict(finding: InspectionFinding) -> dict[str, Any]:
    return {
        "finding_id": finding.id,
        "source": finding.source,
        "category": finding.category,
        "title": finding.title,
        "description": finding.description,
        "applicable_rule": finding.applicable_rule,
        "original_ai_status": finding.original_ai_status,
        "ai_confidence": finding.ai_confidence,
        "ai_description": finding.description if finding.source == "AI" else None,
        "ai_rule": finding.applicable_rule if finding.source == "AI" else None,
        "ai_evidence": finding.ai_evidence,
        "status": finding.status,
        "officer_decision": finding.officer_decision,
        "officer_comment": finding.officer_comment,
        "verified_by": finding.verified_by,
        "verified_at": finding.verified_at,
        "evidence": finding.evidence_data,
    }


def _inspection_dict(inspection: Inspection) -> dict[str, Any]:
    return {
        "id": inspection.id,
        "status": inspection.status,
        "final_outcome": inspection.final_outcome,
        "verified_by": inspection.verified_by,
        "verified_at": inspection.verified_at,
        "product": inspection.product_data,
        "assessment": inspection.assessment_data,
        "findings": [_finding_dict(item) for item in inspection.findings],
        "observations": [{"observation_id": item.id, "description": item.description, "rule": item.rule, "status": item.status, "evidence": item.evidence_data, "officer": item.officer_id, "timestamp": item.created_at} for item in inspection.observations],
        "comments": [{"comment_id": item.id, "finding_id": item.finding_id, "comment": item.comment, "officer": item.officer_id, "timestamp": item.created_at} for item in inspection.comments],
        "evidence": inspection.evidence_data,
        "reports": [{"report_id": item.id, "report_type": item.report_type, "status": item.status, "generated_at": item.generated_at, "file_path": item.file_path, "version": item.version} for item in inspection.reports],
    }


def _require_verified(inspection: Inspection) -> None:
    if inspection.status != "VERIFIED":
        raise HTTPException(status_code=409, detail="Officer-verified reports are available only after human verification")


def _persist_report(db: Session, inspection: Inspection, officer: User, report: dict[str, Any], report_type: str, payload: bytes, mime_type: str, suffix: str) -> InspectionReport:
    report_data = jsonable_encoder(report)
    directory = Path("generated_reports")
    directory.mkdir(exist_ok=True)
    path = directory / f"inspection-{inspection.id}-{report_type.lower()}.{suffix}"
    path.write_bytes(payload)
    record = InspectionReport(inspection_id=inspection.id, report_type=report_type, status="GENERATED", generated_by=officer.id, file_path=str(path), mime_type=mime_type, report_data=report_data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/inspections", status_code=status.HTTP_201_CREATED)
def create_inspection(payload: InspectionCreate, db: Session = Depends(get_db), officer: User = Depends(require_officer)) -> dict[str, Any]:
    assessment = build_initial_assessment(payload.product)
    inspection = Inspection(user_id=officer.id, product_data=payload.product, assessment_data=assessment, evidence_data=payload.evidence)
    db.add(inspection)
    db.flush()
    for result in assessment["rule_results"]:
        db.add(InspectionFinding(inspection_id=inspection.id, source="AI", category=result.get("category", "Other"), title=result["rule_title"] or "AI assessment finding", description=result["explanation"] or "AI assessment result.", applicable_rule=result["rule_number"], original_ai_status=result["status"], ai_confidence=result["confidence"], ai_evidence=result["evidence"], status=result["status"], evidence_data=[]))
    db.commit()
    db.refresh(inspection)
    return _inspection_dict(inspection)


@router.get("/inspections/history")
def inspection_history(db: Session = Depends(get_db), officer: User = Depends(require_officer)) -> list[dict[str, Any]]:
    inspections = db.scalars(select(Inspection).order_by(Inspection.created_at.desc())).all()
    return [{"id": item.id, "status": item.status, "final_outcome": item.final_outcome, "created_at": item.created_at, "reports": [{"report_id": report.id, "report_type": report.report_type, "status": report.status, "generated_at": report.generated_at} for report in item.reports]} for item in inspections]


@router.get("/inspections/{inspection_id}")
def read_inspection(inspection_id: int, db: Session = Depends(get_db), officer: User = Depends(require_officer)) -> dict[str, Any]:
    return _inspection_dict(_get(db, inspection_id))


@router.get("/inspections/{inspection_id}/assessment")
def read_assessment(inspection_id: int, db: Session = Depends(get_db), officer: User = Depends(require_officer)) -> dict[str, Any]:
    return _get(db, inspection_id).assessment_data


@router.get("/inspections/{inspection_id}/findings")
def read_findings(inspection_id: int, db: Session = Depends(get_db), officer: User = Depends(require_officer)) -> list[dict[str, Any]]:
    return [_finding_dict(item) for item in _get(db, inspection_id).findings]


@router.post("/inspections/{inspection_id}/findings", status_code=status.HTTP_201_CREATED)
def add_finding(inspection_id: int, payload: FindingCreate, db: Session = Depends(get_db), officer: User = Depends(require_officer)) -> dict[str, Any]:
    _get(db, inspection_id)
    finding = InspectionFinding(inspection_id=inspection_id, source="OFFICER", category=payload.category, title=payload.title, description=payload.description, applicable_rule=payload.applicable_rule, status=payload.status, officer_comment=payload.officer_comment, verified_by=officer.id, verified_at=datetime.now(timezone.utc), evidence_data=payload.evidence)
    db.add(finding)
    db.commit()
    db.refresh(finding)
    if payload.officer_comment:
        db.add(InspectionComment(inspection_id=inspection_id, finding_id=finding.id, comment=payload.officer_comment, officer_id=officer.id))
        db.commit()
    return _finding_dict(finding)


@router.patch("/inspections/{inspection_id}/findings/{finding_id}/verify")
def verify_finding(inspection_id: int, finding_id: int, payload: FindingVerification, db: Session = Depends(get_db), officer: User = Depends(require_officer)) -> dict[str, Any]:
    _get(db, inspection_id)
    finding = db.scalar(select(InspectionFinding).where(InspectionFinding.id == finding_id, InspectionFinding.inspection_id == inspection_id))
    if finding is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    if finding.source != "AI":
        raise HTTPException(status_code=400, detail="Only AI findings use officer verification decisions")
    if payload.officer_decision not in {"CONFIRM_VIOLATION", "DISMISS_CONCERN", "NEEDS_FURTHER_INSPECTION", "KEEP_COMPLIANT"}:
        raise HTTPException(status_code=422, detail="Invalid officer decision")
    if not payload.officer_comment.strip():
        raise HTTPException(status_code=422, detail="An officer comment is required for every finding decision")
    finding.officer_decision = payload.officer_decision
    finding.officer_comment = payload.officer_comment
    finding.verified_by = officer.id
    finding.verified_at = datetime.now(timezone.utc)
    db.add(InspectionComment(inspection_id=inspection_id, finding_id=finding.id, comment=payload.officer_comment, officer_id=officer.id))
    db.commit()
    db.refresh(finding)
    return _finding_dict(finding)


@router.post("/inspections/{inspection_id}/observations", status_code=status.HTTP_201_CREATED)
def add_observation(inspection_id: int, payload: ObservationCreate, db: Session = Depends(get_db), officer: User = Depends(require_officer)) -> dict[str, Any]:
    _get(db, inspection_id)
    observation = InspectionObservation(inspection_id=inspection_id, description=payload.description, rule=payload.rule, status=payload.status, evidence_data=payload.evidence, officer_id=officer.id)
    db.add(observation)
    db.commit()
    db.refresh(observation)
    return {"observation_id": observation.id, "description": observation.description, "evidence": observation.evidence_data, "officer": officer.id, "timestamp": observation.created_at}


@router.post("/inspections/{inspection_id}/comments", status_code=status.HTTP_201_CREATED)
def add_comment(inspection_id: int, payload: CommentCreate, db: Session = Depends(get_db), officer: User = Depends(require_officer)) -> dict[str, Any]:
    inspection = _get(db, inspection_id)
    if payload.finding_id is not None and not any(item.id == payload.finding_id for item in inspection.findings):
        raise HTTPException(status_code=404, detail="Finding not found")
    comment = InspectionComment(inspection_id=inspection_id, finding_id=payload.finding_id, comment=payload.comment, officer_id=officer.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {"comment_id": comment.id, "finding_id": comment.finding_id, "comment": comment.comment, "officer": comment.officer_id, "timestamp": comment.created_at}


@router.post("/inspections/{inspection_id}/verify")
def complete_verification(inspection_id: int, payload: VerificationCreate, db: Session = Depends(get_db), officer: User = Depends(require_officer)) -> dict[str, Any]:
    inspection = _get(db, inspection_id)
    unresolved = [item.id for item in inspection.findings if item.source == "AI" and item.officer_decision is None]
    missing_comments = [item.id for item in inspection.findings if item.source == "AI" and not item.officer_comment]
    if unresolved or missing_comments:
        raise HTTPException(status_code=409, detail={"message": "Every AI finding requires an officer decision and comment", "unresolved_finding_ids": unresolved, "missing_comment_finding_ids": missing_comments})
    if payload.final_outcome not in {"COMPLIANT", "NON_COMPLIANT", "REQUIRES_FURTHER_INSPECTION"}:
        raise HTTPException(status_code=422, detail="Invalid final outcome")
    inspection.status = "VERIFIED"
    inspection.final_outcome = payload.final_outcome
    inspection.final_remarks = payload.final_remarks
    inspection.verified_by = officer.id
    inspection.verified_at = datetime.now(timezone.utc)
    if payload.final_remarks:
        db.add(InspectionComment(inspection_id=inspection_id, comment=payload.final_remarks, officer_id=officer.id))
    db.commit()
    db.refresh(inspection)
    return _inspection_dict(inspection)


@router.get("/inspections/{inspection_id}/final-report")
def final_report(inspection_id: int, db: Session = Depends(get_db), officer: User = Depends(require_officer)) -> dict[str, Any]:
    inspection = _get(db, inspection_id)
    _require_verified(inspection)
    report = build_officer_verified_report(_inspection_dict(inspection))
    _persist_report(db, inspection, officer, report, "JSON", json.dumps(report, default=str).encode("utf-8"), "application/json", "json")
    return report


@router.get("/inspections/{inspection_id}/final-report/pdf")
def final_report_pdf(inspection_id: int, db: Session = Depends(get_db), officer: User = Depends(require_officer)) -> Response:
    inspection = _get(db, inspection_id)
    _require_verified(inspection)
    report = build_officer_verified_report(_inspection_dict(inspection))
    record = _persist_report(db, inspection, officer, report, "PDF", render_pdf(report), "application/pdf", "pdf")
    return Response(content=Path(record.file_path).read_bytes(), media_type=record.mime_type, headers={"Content-Disposition": f'attachment; filename="inspection-{inspection.id}-report.pdf"'})


@router.get("/inspections/{inspection_id}/final-report/docx")
def final_report_docx(inspection_id: int, db: Session = Depends(get_db), officer: User = Depends(require_officer)) -> Response:
    inspection = _get(db, inspection_id)
    _require_verified(inspection)
    report = build_officer_verified_report(_inspection_dict(inspection))
    record = _persist_report(db, inspection, officer, report, "DOCX", render_docx(report), "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "docx")
    return Response(content=Path(record.file_path).read_bytes(), media_type=record.mime_type, headers={"Content-Disposition": f'attachment; filename="inspection-{inspection.id}-report.docx"'})
