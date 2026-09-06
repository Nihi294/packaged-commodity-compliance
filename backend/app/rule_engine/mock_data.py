from typing import Any


MOCK_PRODUCT: dict[str, Any] = {
    "product_name": "ABC Biscuits",
    "common_name": "Biscuits",
    "category": "food",
    "manufacturer_name": "XYZ Foods Pvt. Ltd.",
    "manufacturer_address": "Food Park, New Delhi",
    "net_quantity": {"value": "500 g", "confidence": 0.95, "source_image": "front"},
    "mrp": {"value": "MRP Rs 120", "confidence": 0.95, "source_image": "front"},
    "month_year_of_manufacture": "01/2026",
    "sale_basis": "mass",
    "font_height_mm": 1.0,
    "font_measurement_confidence": 0.91,
    "calibrated": True,
}


def mock_findings() -> list[dict[str, Any]]:
    return [
        {"finding_id": "F01", "source": "AI", "category": "Font & Readability", "title": "Font requirement concern", "description": "Declared font measurement may require review.", "applicable_rule": "Rule 7", "original_ai_status": "POTENTIAL_VIOLATION", "status": "POTENTIAL_VIOLATION", "ai_confidence": 0.91, "evidence": [{"evidence_id": "E01", "source": "AI"}]},
        {"finding_id": "F02", "source": "AI", "category": "Mandatory Declarations", "title": "Mandatory declaration missing", "description": "A Rule 6 declaration requires review.", "applicable_rule": "Rule 6", "original_ai_status": "POTENTIAL_VIOLATION", "status": "POTENTIAL_VIOLATION", "ai_confidence": 0.94, "evidence": [{"evidence_id": "E02", "source": "AI"}]},
        {"finding_id": "F03", "source": "AI", "category": "Misleading / Deceptive Packaging", "title": "Potential deceptive-package concern", "description": "Potential deceptive-package concern - officer verification required.", "applicable_rule": "Rule 23", "original_ai_status": "NEEDS_VERIFICATION", "status": "NEEDS_VERIFICATION", "ai_confidence": 0.72, "officer_decision": "DISMISS_CONCERN", "evidence": [{"evidence_id": "E03", "source": "AI"}]},
        {"finding_id": "F04", "source": "AI", "category": "Mandatory Declarations", "title": "MRP declaration", "description": "MRP declaration detected.", "applicable_rule": "Rule 6", "original_ai_status": "COMPLIANT", "status": "COMPLIANT", "ai_confidence": 0.98, "evidence": [{"evidence_id": "E04", "source": "AI"}]},
        {"finding_id": "F05", "source": "AI", "category": "Quantity & Unit", "title": "Net quantity declaration", "description": "Net quantity declaration detected.", "applicable_rule": "Rule 6", "original_ai_status": "COMPLIANT", "status": "COMPLIANT", "ai_confidence": 0.97, "evidence": [{"evidence_id": "E05", "source": "AI"}]},
        {"finding_id": "F06", "source": "OFFICER", "category": "Mandatory Declarations", "title": "Consumer complaint information missing", "description": "Consumer complaint information was not found.", "applicable_rule": "Rule 6", "status": "CONFIRMED_VIOLATION", "officer_decision": "CONFIRM_VIOLATION", "evidence": [{"evidence_id": "E06", "source": "OFFICER"}]},
    ]


MOCK_OBSERVATION = {"description": "Front panel reviewed by officer.", "evidence": [{"evidence_id": "E07", "source": "OFFICER"}], "officer": "officer-1"}