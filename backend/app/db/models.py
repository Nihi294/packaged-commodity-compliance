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
    reports: Mapped[list["Report"]] = relationship(back_populates="user")
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
    reports: Mapped[list["Report"]] = relationship(back_populates="scan")
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


class Report(TimestampMixin, Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id"), nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    file_path: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)

    scan: Mapped[Scan] = relationship(back_populates="reports")
    user: Mapped[User | None] = relationship(back_populates="reports")


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

    scan: Mapped[Scan] = relationship(back_populates="evidence")
    rule_result: Mapped[RuleResult | None] = relationship(back_populates="evidence")
