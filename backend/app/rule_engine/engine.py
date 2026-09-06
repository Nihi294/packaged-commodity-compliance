"""JSON-driven packaged commodity compliance engine.

The engine loads rule definitions from a JSON file, maps each rule to a validator
function, and evaluates them against structured product metadata without relying
on OCR modules or the database layer.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.rule_engine.validators import VALIDATOR_MAP

VALID_STATUSES = [
    "Requires Human Verification",
    "Unable to Verify",
    "Missing Declaration",
    "Potential Non-Compliance",
    "Compliant",
]


class RuleEngine:
    """Evaluate packaged commodity declarations against the SahiPack rule set."""

    def __init__(self, rules_path: str | Path | None = None) -> None:
        if rules_path is None:
            rules_path = Path(__file__).resolve().parent / "rules" / "packaged_commodities.json"
        self.rules_path = Path(rules_path)
        self.rules = self._load_rules()
        self.rules_by_id = {rule["id"]: rule for rule in self.rules}

    def _load_rules(self) -> list[dict[str, Any]]:
        with self.rules_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, dict):
            return list(payload.get("rules", []))
        return list(payload)

    def _is_rule_applicable(self, rule: dict[str, Any], product: dict[str, Any]) -> bool:
        category = str(product.get("category") or "other").lower()
        if rule.get("category_specific") and not rule.get("default_enabled", True):
            special = product.get("special_commodity_type") or product.get("commodity_type")
            if not special:
                return False
            allowed = {str(item).lower() for item in rule.get("special_commodity_types", [])}
            if special.lower() not in allowed:
                return False

        categories = rule.get("category", ["food", "beverage", "alcoholic_beverage", "other"])
        if categories and category not in {str(item).lower() for item in categories}:
            return False
        return True

    def _normalize_result(self, rule: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
        normalized = {
            "rule_id": result.get("rule_id", rule.get("id")),
            "rule_reference": result.get("rule_reference", rule.get("rule_reference")),
            "rule_name": result.get("rule_name", rule.get("name")),
            "status": result.get("status"),
            "explanation": result.get("explanation"),
            "severity": result.get("severity", rule.get("severity", "medium")),
            "confidence": result.get("confidence", 0.8),
            "field_checked": result.get("field_checked"),
            "detected_value": result.get("detected_value"),
            "expected_value": result.get("expected_value") or rule.get("expected_value"),
            "source_image": result.get("source_image"),
            "evidence": result.get("evidence") or {},
            "automation_level": result.get("automation_level", rule.get("automation_level", "heuristic")),
            "legal_reference": result.get("legal_reference", rule.get("rule_reference")),
        }
        if normalized["status"] not in VALID_STATUSES:
            normalized["status"] = "Unable to Verify"
        return normalized

    def _overall_status(self, results: list[dict[str, Any]]) -> str:
        if not results:
            return "Compliant"
        order = {status: index for index, status in enumerate(VALID_STATUSES)}
        return min(results, key=lambda item: order.get(item.get("status"), 99)).get("status", "Compliant")

    def evaluate(self, product: dict[str, Any]) -> dict[str, Any]:
        product = product or {}
        rule_results: list[dict[str, Any]] = []

        for rule in self.rules:
            if not self._is_rule_applicable(rule, product):
                continue
            validator = VALIDATOR_MAP.get(rule.get("validator"))
            if validator is None:
                continue
            outcome = validator(rule, product)
            if outcome is None:
                continue
            rule_results.append(self._normalize_result(rule, outcome))

        overall_status = self._overall_status(rule_results)
        return {
            "overall_status": overall_status,
            "rule_count": len(rule_results),
            "results": rule_results,
            "category": product.get("category"),
            "source_type": product.get("source_type"),
        }


if __name__ == "__main__":
    engine = RuleEngine()
    mock_product = {
        "category": "food",
        "source_type": "physical_package",
        "source_image": "front",
        "product_name": "Biscuits",
        "common_name": "Biscuits",
        "manufacturer_name": "Sahi Foods Pvt Ltd",
        "manufacturer_address": "Plot 12, Industrial Area, Bengaluru",
        "net_quantity": {"value": "200 g", "confidence": 0.95, "source_image": "front"},
        "mrp": {"value": "₹50", "confidence": 0.95, "source_image": "front"},
        "manufacture_date": "2025-01-15",
        "month_year_of_manufacture": "01/2025",
        "consumer_care_name": "Customer Care",
        "consumer_care_address": "Sahi Foods Pvt Ltd, Bengaluru",
        "consumer_care_phone": "+91 9876543210",
        "consumer_care_email": "care@sahifoods.example",
        "detected_languages": ["English", "Hindi"],
        "sale_basis": "mass",
        "declared_mrp": 50,
        "actual_sale_price": 50,
    }
    results = engine.evaluate(mock_product)
    print(f"Overall status: {results['overall_status']}")
    for item in results["results"]:
        print(item["rule_id"], item["status"], item["rule_reference"], item["explanation"])
