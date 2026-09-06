from typing import Any

from pydantic import BaseModel, Field


class InspectionCreate(BaseModel):
    product: dict[str, Any] = Field(default_factory=dict)
    evidence: list[dict[str, Any]] = Field(default_factory=list)


class FindingCreate(BaseModel):
    category: str
    title: str
    description: str
    applicable_rule: str | None = None
    status: str = "CONFIRMED_VIOLATION"
    officer_comment: str | None = None
    evidence: list[dict[str, Any]] = Field(default_factory=list)


class FindingVerification(BaseModel):
    officer_decision: str
    officer_comment: str | None = None


class ObservationCreate(BaseModel):
    description: str
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    rule: str | None = None
    status: str | None = None


class CommentCreate(BaseModel):
    comment: str
    finding_id: int | None = None


class VerificationCreate(BaseModel):
    final_outcome: str
    final_remarks: str | None = None