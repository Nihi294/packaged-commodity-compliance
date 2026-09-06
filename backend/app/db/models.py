from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="officer", nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    scans: Mapped[list["Scan"]] = relationship(back_populates="user")
    inspection_history: Mapped[list["InspectionHistory"]] = relationship(back_populates="user")


class Product(TimestampMixin, Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text)

    scans: Mapped[list["Scan"]] = relationship(back_populates="product")
    inspection_history: Mapped[list["InspectionHistory"]] = relationship(back_populates="product")


class Scan(TimestampMixin, Base):
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    product_id: Mapped[int | None] = mapped_column(ForeignKey("products.id"))
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)

    user: Mapped[User | None] = relationship(back_populates="scans")
    product: Mapped[Product | None] = relationship(back_populates="scans")
    images: Mapped[list["Image"]] = relationship(back_populates="scan", cascade="all, delete-orphan")
    ocr_results: Mapped[list["OcrResult"]] = relationship(back_populates="scan", cascade="all, delete-orphan")
    declarations: Mapped[list["ExtractedDeclaration"]] = relationship(back_populates="scan", cascade="all, delete-orphan")
    rule_results: Mapped[list["RuleResult"]] = relationship(back_populates="scan", cascade="all, delete-orphan")
    violations: Mapped[list["Violation"]] = relationship(back_populates="scan", cascade="all, delete-orphan")
    inspection_history: Mapped[list["InspectionHistory"]] = relationship(back_populates="scan")
    evidence: Mapped[list["Evidence"]] = relationship(back_populates="scan", cascade="all, delete-orphan")

    __table_args__ = (Index("ix_scans_user_created_at", "user_id", "created_at"),)


class Image(TimestampMixin, Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    image_type: Mapped[str | None] = mapped_column(String(50))

    scan: Mapped[Scan] = relationship(back_populates="images")
    ocr_results: Mapped[list["OcrResult"]] = relationship(back_populates="image")


class OcrResult(TimestampMixin, Base):
    __tablename__ = "ocr_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id"), nullable=False)
    image_id: Mapped[int | None] = mapped_column(ForeignKey("images.id"))
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float | None]

    scan: Mapped[Scan] = relationship(back_populates="ocr_results")
    image: Mapped[Image | None] = relationship(back_populates="ocr_results")


class ExtractedDeclaration(TimestampMixin, Base):
    __tablename__ = "extracted_declarations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id"), nullable=False)
    declaration_type: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str | None] = mapped_column(Text)
    source_data: Mapped[dict | None] = mapped_column(JSONB)

    scan: Mapped[Scan] = relationship(back_populates="declarations")


class Rule(TimestampMixin, Base):
    __tablename__ = "rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    rule_definition: Mapped[dict | None] = mapped_column(JSONB)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    results: Mapped[list["RuleResult"]] = relationship(back_populates="rule")


class RuleResult(TimestampMixin, Base):
    __tablename__ = "rule_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id"), nullable=False)
    rule_id: Mapped[int] = mapped_column(ForeignKey("rules.id"), nullable=False)
    passed: Mapped[bool] = mapped_column(nullable=False)
    details: Mapped[dict | None] = mapped_column(JSONB)

    scan: Mapped[Scan] = relationship(back_populates="rule_results")
    rule: Mapped[Rule] = relationship(back_populates="results")
    violations: Mapped[list["Violation"]] = relationship(back_populates="rule_result")
    evidence: Mapped[list["Evidence"]] = relationship(back_populates="rule_result", cascade="all, delete-orphan")


class Violation(TimestampMixin, Base):
    __tablename__ = "violations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id"), nullable=False)
    rule_result_id: Mapped[int | None] = mapped_column(ForeignKey("rule_results.id"))
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(50), default="medium", nullable=False)

    scan: Mapped[Scan] = relationship(back_populates="violations")
    rule_result: Mapped[RuleResult | None] = relationship(back_populates="violations")


class InspectionHistory(TimestampMixin, Base):
    __tablename__ = "inspection_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    scan_id: Mapped[int | None] = mapped_column(ForeignKey("scans.id"))
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    scan: Mapped[Scan] = relationship(back_populates="inspection_history")
    user: Mapped[User | None] = relationship(back_populates="inspection_history")
    product: Mapped[Product] = relationship(back_populates="inspection_history")


class Evidence(TimestampMixin, Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id"), nullable=False)
    rule_result_id: Mapped[int | None] = mapped_column(ForeignKey("rule_results.id"))
    violation_id: Mapped[int | None] = mapped_column(ForeignKey("violations.id"))
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(20), default="AI", nullable=False)
    finding_id: Mapped[int | None] = mapped_column(ForeignKey("inspection_findings.id"))

    scan: Mapped[Scan] = relationship(back_populates="evidence")
    rule_result: Mapped[RuleResult | None] = relationship(back_populates="evidence")


class Inspection(TimestampMixin, Base):
    __tablename__ = "inspections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(40), default="ASSESSMENT_READY", nullable=False, index=True)
    final_outcome: Mapped[str | None] = mapped_column(String(50))
    verified_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    final_remarks: Mapped[str | None] = mapped_column(Text)
    product_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    assessment_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    evidence_data: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    findings: Mapped[list["InspectionFinding"]] = relationship(back_populates="inspection", cascade="all, delete-orphan")
    observations: Mapped[list["InspectionObservation"]] = relationship(back_populates="inspection", cascade="all, delete-orphan")
    comments: Mapped[list["InspectionComment"]] = relationship(back_populates="inspection", cascade="all, delete-orphan")
    reports: Mapped[list["InspectionReport"]] = relationship(back_populates="inspection", cascade="all, delete-orphan")


class InspectionFinding(TimestampMixin, Base):
    __tablename__ = "inspection_findings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inspection_id: Mapped[int] = mapped_column(ForeignKey("inspections.id"), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(20), default="AI", nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    applicable_rule: Mapped[str | None] = mapped_column(String(100))
    original_ai_status: Mapped[str | None] = mapped_column(String(50))
    ai_confidence: Mapped[float | None]
    ai_evidence: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    officer_decision: Mapped[str | None] = mapped_column(String(50))
    officer_comment: Mapped[str | None] = mapped_column(Text)
    verified_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    evidence_data: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)

    inspection: Mapped[Inspection] = relationship(back_populates="findings")


class InspectionObservation(TimestampMixin, Base):
    __tablename__ = "inspection_observations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inspection_id: Mapped[int] = mapped_column(ForeignKey("inspections.id"), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    rule: Mapped[str | None] = mapped_column(String(100))
    status: Mapped[str | None] = mapped_column(String(50))
    evidence_data: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    officer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    inspection: Mapped[Inspection] = relationship(back_populates="observations")


class InspectionComment(TimestampMixin, Base):
    __tablename__ = "inspection_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inspection_id: Mapped[int] = mapped_column(ForeignKey("inspections.id"), nullable=False, index=True)
    finding_id: Mapped[int | None] = mapped_column(ForeignKey("inspection_findings.id"))
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    officer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    inspection: Mapped[Inspection] = relationship(back_populates="comments")


class InspectionReport(TimestampMixin, Base):
    __tablename__ = "inspection_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inspection_id: Mapped[int] = mapped_column(ForeignKey("inspections.id"), nullable=False, index=True)
    report_type: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    generated_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(500))
    mime_type: Mapped[str | None] = mapped_column(String(120))
    report_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    inspection: Mapped[Inspection] = relationship(back_populates="reports")
