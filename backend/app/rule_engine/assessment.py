"""Assessment and report data contracts for packaged commodity inspections."""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.rule_engine.engine import RuleEngine

COMPLIANT = "COMPLIANT"
POTENTIAL_VIOLATION = "POTENTIAL_VIOLATION"
NEEDS_VERIFICATION = "NEEDS_VERIFICATION"
NOT_APPLICABLE = "NOT_APPLICABLE"
AI_STATUSES = {COMPLIANT, POTENTIAL_VIOLATION, NEEDS_VERIFICATION, NOT_APPLICABLE}
SCORE_METHODOLOGY = (
    "Applicable rule results score COMPLIANT=1, NEEDS_VERIFICATION=0.5, "
    "POTENTIAL_VIOLATION=0; NOT_APPLICABLE is excluded. This is an AI screening "
    "metric and is not a legal, government, or official compliance score."
)


def _status(legacy_status: str | None) -> str:
    if legacy_status == "Compliant":
        return COMPLIANT
    if legacy_status in {"Potential Non-Compliance", "Missing Declaration"}:
        return POTENTIAL_VIOLATION
    return NEEDS_VERIFICATION


def _applicability(package: dict[str, Any]) -> tuple[bool, str]:
    quantity = package.get("quantity_value")
    unit = str(package.get("quantity_unit") or "").lower()
    if package.get("industrial_consumer"):
        return False, "Package is identified for an industrial consumer; retail checks are not run."
    if package.get("institutional_consumer"):
        return False, "Package is identified for an institutional consumer; retail checks are not run."
    if unit in {"kg", "kilogram", "l", "litre", "liter"} and quantity is not None and float(quantity) > 25 and not package.get("cement_or_fertilizer_exception"):
        return False, "Package exceeds 25 kg or 25 litre and no stated cement/fertilizer exception applies."
    return True, "Retail packaged commodity checks are applicable."


def _declarations(product: dict[str, Any], results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    values = {
        "manufacturer": product.get("manufacturer_name") or product.get("manufacturer"),
        "packer": product.get("packer_name") or product.get("packer"),
        "importer": product.get("importer_name") or product.get("importer"),
        "common_name": product.get("common_name") or product.get("product_name"),
        "net_quantity": product.get("net_quantity"),
        "manufacture_date": product.get("month_year_of_manufacture") or product.get("manufacture_date"),
        "mrp": product.get("mrp"),
        "consumer_contact": product.get("consumer_care_name") or product.get("consumer_care_phone"),
    }
    declarations = []
    for name, value in values.items():
        result = next((item for item in results if name in str(item.get("field_checked"))), None)
        declarations.append({"declaration": name, "detected_value": value, "status": _status(result.get("status")) if result else NEEDS_VERIFICATION, "rule": "Rule 6", "confidence": result.get("confidence", 0.0) if result else 0.0, "evidence": result.get("evidence") if result else {}})
    return declarations


def screening_score(results: list[dict[str, Any]]) -> float:
    scored = [item for item in results if item.get("status") != NOT_APPLICABLE]
    if not scored:
        return 100.0
    values = {COMPLIANT: 1.0, POTENTIAL_VIOLATION: 0.0, NEEDS_VERIFICATION: 0.5}
    return round(sum(values.get(item.get("status"), 0.5) for item in scored) / len(scored) * 100, 2)


def chart_data(results: list[dict[str, Any]], findings: list[dict[str, Any]], score: float) -> dict[str, Any]:
    distribution = Counter(item.get("status", NEEDS_VERIFICATION) for item in results)
    categories = Counter(item.get("category", "Other") for item in findings)
    resolutions = ("CONFIRM_VIOLATION", "DISMISS_CONCERN", "NEEDS_FURTHER_INSPECTION", "OFFICER_ADDED")
    return {
        "compliance_distribution": {status: distribution.get(status, 0) for status in AI_STATUSES},
        "findings_by_category": dict(categories),
        "screening_score_breakdown": {"Applicable checks": score},
        "finding_resolution": {status: sum(1 for item in findings if item.get("officer_decision") == status or item.get("source") == "OFFICER" and status == "OFFICER_ADDED") for status in resolutions},
    }


def generate_initial_assessment(product: dict[str, Any], *, findings: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    package = product or {}
    applicable, reason = _applicability(package)
    legacy = RuleEngine().evaluate(package) if applicable else {"results": []}
    results = [{
        "rule_number": item.get("rule_reference", item.get("rule_id")),
        "rule_title": item.get("rule_name"),
        "applicable": True,
        "applicability_reason": reason,
        "status": _status(item.get("status")),
        "explanation": item.get("explanation"),
        "evidence": item.get("evidence") or {"source_image": item.get("source_image")},
        "confidence": item.get("confidence", 0.0),
        "category": "Other",
        "legacy_rule_id": item.get("rule_id"),
    } for item in legacy.get("results", [])]
    result_findings = list(findings or [])
    score = screening_score(results)
    return {
        "title": "INITIAL COMPLIANCE ASSESSMENT",
        "preliminary_notice": "PRELIMINARY AI ASSESSMENT - OFFICER REVIEW REQUIRED",
        "product": package,
        "applicability": {"applicable": applicable, "reason": reason},
        "rule_results": results,
        "declarations": _declarations(package, legacy.get("results", [])),
        "screening_score": score,
        "screening_score_label": "SahiPack Screening Score",
        "screening_score_methodology": SCORE_METHODOLOGY,
        "physical_quantity": {"status": "NOT VERIFIED", "message": "Physical quantity not verified from image evidence."},
        "findings": result_findings,
        "charts": chart_data(results, result_findings, score),
    }


