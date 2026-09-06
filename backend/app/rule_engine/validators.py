"""Validator functions for packaged commodity compliance rules.

These are intentionally generic and operate on structured product metadata so the
rule engine can be evaluated without OCR or database dependencies.
"""

from __future__ import annotations

import re
from typing import Any

VALID_STATUSES = {
    "Compliant",
    "Potential Non-Compliance",
    "Missing Declaration",
    "Unable to Verify",
    "Requires Human Verification",
}

SUPPORTED_LANGUAGES = {"english", "hindi", "devanagari"}
UNIT_ALIASES = {
    "g": "g",
    "kg": "kg",
    "mg": "mg",
    "ml": "ml",
    "mL": "ml",
    "l": "l",
    "litre": "l",
    "liter": "l",
    "cm": "cm",
    "m": "m",
    "number": "number",
    "count": "number",
    "pcs": "number",
    "pc": "number",
    "pieces": "number",
    "piece": "number",
    "nos": "number",
    "no": "number",
    "n": "number",
    "u": "number",
}
SUSPICIOUS_QUANTITY_WORDS = [
    "extra free",
    "free",
    "bonus",
    "more than",
    "not less than",
    "as good as",
    "double",
    "mega",
]


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        if "value" in value:
            return str(value["value"])
        return str(value)
    if isinstance(value, list):
        return ", ".join(_as_text(item) for item in value)
    return str(value)


def _confidence(value: Any) -> float:
    if isinstance(value, dict):
        conf = value.get("confidence")
        if conf is None:
            return 0.8
        return float(conf)
    if isinstance(value, (int, float)):
        return float(value)
    return 0.8


def _source_image(value: Any) -> Any:
    if isinstance(value, dict):
        return value.get("source_image")
    return None


def _missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, dict):
        return _missing(value.get("value"))
    if isinstance(value, list):
        return len(value) == 0
    return False


def _result(
    rule: dict[str, Any],
    status: str,
    explanation: str,
    *,
    confidence: float = 1.0,
    field_checked: Any = None,
    detected_value: Any = None,
    expected_value: Any = None,
    source_image: Any = None,
    evidence: Any = None,
    automation_level: str | None = None,
    severity: str | None = None,
) -> dict[str, Any]:
    if status not in VALID_STATUSES:
        raise ValueError(f"Unsupported status: {status}")
    result = {
        "rule_id": rule.get("id"),
        "rule_reference": rule.get("rule_reference"),
        "rule_name": rule.get("name"),
        "status": status,
        "explanation": explanation,
        "severity": severity or rule.get("severity", "medium"),
        "confidence": round(float(confidence), 2),
        "field_checked": field_checked,
        "detected_value": detected_value,
        "expected_value": expected_value,
        "source_image": source_image,
        "evidence": evidence,
        "automation_level": automation_level or rule.get("automation_level", "heuristic"),
        "legal_reference": rule.get("legal_reference"),
    }
    return result


def _value_from_product(product: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in product:
            return product.get(key)
    return None


def _lower(value: Any) -> str:
    return _as_text(value).lower().strip()


def _has_mrp_text(value: Any) -> bool:
    text = _lower(value)
    return any(p in text for p in ["mrp", "maximum retail price", "rs", "inr", "₹"])


def _is_supported_language_list(values: Any) -> bool:
    if values is None:
        return False
    if isinstance(values, str):
        values = [values]
    present = {str(v).strip().lower() for v in values}
    return bool(present & SUPPORTED_LANGUAGES)


def validate_manufacturer_details(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    manufacturer_name = product.get("manufacturer_name") or product.get("manufacturer")
    manufacturer_address = product.get("manufacturer_address")
    packer_name = product.get("packer_name") or product.get("packer")
    packer_address = product.get("packer_address")
    importer_name = product.get("importer_name") or product.get("importer")
    importer_address = product.get("importer_address")
    country_of_origin = product.get("country_of_origin")
    is_imported = bool(product.get("is_imported") or importer_name or importer_address or country_of_origin)

    if manufacturer_name is None and packer_name is None and importer_name is None:
        return _result(
            rule,
            "Missing Declaration",
            "No manufacturer, packer or importer details were identified on the package.",
            confidence=0.7,
            field_checked=["manufacturer_name", "manufacturer_address", "packer_name", "importer_name"],
            detected_value={
                "manufacturer_name": manufacturer_name,
                "manufacturer_address": manufacturer_address,
                "packer_name": packer_name,
                "importer_name": importer_name,
                "country_of_origin": country_of_origin,
            },
            expected_value="Manufacturer name and address, with packer/importer details where applicable.",
            source_image=product.get("source_image"),
            evidence={"is_imported": is_imported},
            automation_level="automated",
            severity="high",
        )

    missing_fields: list[str] = []
    if manufacturer_name is None and (product.get("manufacturer_required") is not False):
        missing_fields.append("manufacturer_name")
    if manufacturer_address is None and manufacturer_name is not None:
        missing_fields.append("manufacturer_address")
    if packer_name is not None and packer_address is None:
        missing_fields.append("packer_address")
    if importer_name is not None and importer_address is None:
        missing_fields.append("importer_address")
    if is_imported and country_of_origin is None:
        missing_fields.append("country_of_origin")

    if missing_fields:
        return _result(
            rule,
            "Missing Declaration",
            f"Required declaration fields are missing: {', '.join(missing_fields)}.",
            confidence=0.8,
            field_checked=missing_fields,
            detected_value={
                "manufacturer_name": manufacturer_name,
                "manufacturer_address": manufacturer_address,
                "packer_name": packer_name,
                "importer_name": importer_name,
                "importer_address": importer_address,
                "country_of_origin": country_of_origin,
            },
            expected_value="Complete manufacturer/packer/importer identification and address, including country of origin for imports when applicable.",
            source_image=product.get("source_image"),
            evidence={"missing_fields": missing_fields},
            automation_level="automated",
            severity="high",
        )

    return _result(
        rule,
        "Compliant",
        "Manufacturer and relevant packer/importer details were detected and appear complete.",
        confidence=0.92,
        field_checked=["manufacturer_name", "manufacturer_address", "packer_name", "importer_name"],
        detected_value={
            "manufacturer_name": manufacturer_name,
            "manufacturer_address": manufacturer_address,
            "packer_name": packer_name,
            "importer_name": importer_name,
            "country_of_origin": country_of_origin,
        },
        source_image=product.get("source_image"),
        automation_level="automated",
        severity="high",
    )


def validate_common_name(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    common_name = product.get("common_name") or product.get("commodity_name") or product.get("product_name")
    if _missing(common_name):
        return _result(
            rule,
            "Missing Declaration",
            "Common or generic name of the commodity was not detected.",
            confidence=0.75,
            field_checked="common_name",
            detected_value=common_name,
            expected_value="Common/generic name of the commodity.",
            source_image=product.get("source_image"),
            automation_level="automated",
            severity="high",
        )
    return _result(
        rule,
        "Compliant",
        "Common or generic commodity name was detected.",
        confidence=0.9,
        field_checked="common_name",
        detected_value=common_name,
        source_image=product.get("source_image"),
        automation_level="automated",
        severity="high",
    )


def validate_net_quantity(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    value = product.get("net_quantity")
    text = _as_text(value)
    base = (isinstance(value, dict) and value.get("value")) or value
    if _missing(value):
        return _result(
            rule,
            "Missing Declaration",
            "Net quantity declaration is missing.",
            confidence=0.9,
            field_checked="net_quantity",
            detected_value=value,
            expected_value="Net quantity with a valid unit and basis.",
            source_image=product.get("source_image"),
            automation_level="automated",
            severity="high",
        )

    if isinstance(value, dict) and _confidence(value) < 0.7:
        return _result(
            rule,
            "Unable to Verify",
            "Net quantity OCR confidence is too low to rely on the extracted value.",
            confidence=_confidence(value),
            field_checked="net_quantity",
            detected_value=text,
            source_image=value.get("source_image"),
            expected_value="A legible net quantity declaration.",
            automation_level="automated",
            severity="high",
        )

    match = re.search(r"([0-9]+(?:\.[0-9]+)?(?:\s*to\s*[0-9]+(?:\.[0-9]+)?)?)\s*([A-Za-z]+)", text)
    unit = None
    if match:
        unit = match.group(2).lower()
        unit = UNIT_ALIASES.get(unit, unit)
    if not match:
        return _result(
            rule,
            "Potential Non-Compliance",
            "Net quantity is malformed or uses an unrecognized unit basis.",
            confidence=0.8,
            field_checked="net_quantity",
            detected_value=text,
            expected_value="Numeric quantity with an accepted unit such as g, kg, ml, L, cm, m, or count.",
            source_image=_source_image(value),
            automation_level="automated",
            severity="high",
        )

    sale_basis = str(product.get("sale_basis") or "").lower()
    if sale_basis in {"mass", "solid", "semi-solid", "viscous", "solid-liquid mixture"} and unit not in {"g", "kg", "mg"}:
        return _result(
            rule,
            "Potential Non-Compliance",
            "The declared quantity basis does not match the product's mass-based sale category.",
            confidence=0.8,
            field_checked="net_quantity",
            detected_value=text,
            expected_value="Mass-based quantity declaration (g/kg/mg).",
            source_image=_source_image(value),
            automation_level="automated",
            severity="high",
        )
    if sale_basis in {"liquid", "volume"} and unit not in {"ml", "l"}:
        return _result(
            rule,
            "Potential Non-Compliance",
            "The declared quantity basis does not match the liquid volume basis.",
            confidence=0.8,
            field_checked="net_quantity",
            detected_value=text,
            expected_value="Volume-based quantity declaration (ml/L).",
            source_image=_source_image(value),
            automation_level="automated",
            severity="high",
        )

    return _result(
        rule,
        "Compliant",
        "Net quantity declaration is present and appears to use an acceptable unit basis.",
        confidence=0.9,
        field_checked="net_quantity",
        detected_value=text,
        expected_value="Numeric quantity with a valid unit.",
        source_image=_source_image(value),
        automation_level="automated",
        severity="high",
    )


def validate_date_requirement(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    category = str(product.get("category") or "other").lower()
    date_fields = [
        product.get("manufacture_date"),
        product.get("packing_date"),
        product.get("import_date"),
        product.get("date_of_manufacture"),
    ]
    if category == "food":
        if any(field not in (None, "") for field in date_fields):
            return _result(
                rule,
                "Compliant",
                "Food date information is present; food-specific legal rules are category-dependent and the declaration is available.",
                confidence=0.9,
                field_checked=["manufacture_date", "packing_date", "import_date"],
                detected_value=date_fields,
                expected_value="Food-specific date declaration when required by the category and applicable law.",
                source_image=product.get("source_image"),
                automation_level="heuristic",
                severity="medium",
            )
        return _result(
            rule,
            "Requires Human Verification",
            "Food products may be governed by food-specific date requirements; the applicable legal determination cannot be automated from the photograph alone.",
            confidence=0.7,
            field_checked="manufacture_date",
            detected_value=None,
            expected_value="Category-specific date requirement as applicable under the food law framework.",
            source_image=product.get("source_image"),
            automation_level="human_verification",
            severity="medium",
        )

    if any(field not in (None, "") for field in date_fields):
        return _result(
            rule,
            "Compliant",
            "Manufacture/pre-packing/import date information is present.",
            confidence=0.9,
            field_checked=["manufacture_date", "packing_date", "import_date"],
            detected_value=date_fields,
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="medium",
        )
    return _result(
        rule,
        "Missing Declaration",
        "The applicable manufacture/pre-packing/import date declaration is absent.",
        confidence=0.8,
        field_checked="manufacture_date",
        detected_value=None,
        expected_value="Applicable date declaration for the product category.",
        source_image=product.get("source_image"),
        automation_level="heuristic",
        severity="medium",
    )


def validate_mrp(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    category = str(product.get("category") or "other").lower()
    mrp = product.get("mrp")
    text = _as_text(mrp)
    if _missing(mrp):
        if category in {"alcoholic_beverage"}:
            return _result(
                rule,
                "Requires Human Verification",
                "Alcoholic beverage MRP may be governed by State Excise laws and cannot be treated as a universal generic requirement without category-specific legal review.",
                confidence=0.8,
                field_checked="mrp",
                detected_value=mrp,
                expected_value="MRP declaration if required under applicable State Excise law.",
                source_image=product.get("source_image"),
                automation_level="heuristic",
                severity="high",
            )
        return _result(
            rule,
            "Missing Declaration",
            "MRP declaration is missing.",
            confidence=0.9,
            field_checked="mrp",
            detected_value=mrp,
            expected_value="MRP or Maximum Retail Price declaration.",
            source_image=product.get("source_image"),
            automation_level="automated",
            severity="high",
        )

    conf = _confidence(mrp)
    if conf < 0.7:
        return _result(
            rule,
            "Unable to Verify",
            "MRP text is too low-confidence to be relied on for compliance verification.",
            confidence=conf,
            field_checked="mrp",
            detected_value=text,
            expected_value="Clearly legible MRP declaration.",
            source_image=_source_image(mrp),
            automation_level="automated",
            severity="high",
        )

    if text in {"₹", "Rs", "INR", "", "MRP"} or not _has_mrp_text(mrp):
        return _result(
            rule,
            "Potential Non-Compliance",
            "MRP text is incomplete or does not present a clear numeric retail price.",
            confidence=conf,
            field_checked="mrp",
            detected_value=text,
            expected_value="MRP in rupees with a readable numeric value.",
            source_image=_source_image(mrp),
            automation_level="automated",
            severity="high",
        )

    return _result(
        rule,
        "Compliant",
        "MRP declaration was detected in a recognizable format.",
        confidence=conf,
        field_checked="mrp",
        detected_value=text,
        expected_value="MRP or Maximum Retail Price declaration.",
        source_image=_source_image(mrp),
        automation_level="automated",
        severity="high",
    )


def validate_month_year_rule(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    value = product.get("month_year_of_manufacture") or product.get("manufacture_month_year") or product.get("date_of_packaging")
    if _missing(value):
        if str(product.get("category") or "other").lower() == "food":
            return _result(
                rule,
                "Requires Human Verification",
                "Food-date obligations may be governed by food-specific legal rules rather than a universal month/year declaration rule.",
                confidence=0.7,
                field_checked="month_year_of_manufacture",
                detected_value=value,
                expected_value="Month and year of manufacture/packing/import if required under the relevant category rules.",
                source_image=product.get("source_image"),
                automation_level="heuristic",
                severity="medium",
            )
        return _result(
            rule,
            "Missing Declaration",
            "Month and year of manufacture/packing/import is missing where applicable.",
            confidence=0.8,
            field_checked="month_year_of_manufacture",
            detected_value=value,
            expected_value="Month and year in MM/YYYY, MM-YYYY or month + year format.",
            source_image=product.get("source_image"),
            automation_level="automated",
            severity="medium",
        )

    if re.search(r"(0?[1-9]|1[0-2])\s*[-/]\s*(19|20)\d{2}|(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+[0-9]{4}", _as_text(value), flags=re.I):
        return _result(
            rule,
            "Compliant",
            "Month and year declaration was detected in an acceptable format.",
            confidence=0.9,
            field_checked="month_year_of_manufacture",
            detected_value=value,
            expected_value="MM/YYYY, MM-YYYY or month + year.",
            source_image=product.get("source_image"),
            automation_level="automated",
            severity="medium",
        )

    return _result(
        rule,
        "Potential Non-Compliance",
        "The month/year format is not clearly in a valid declaration format or the date is not plausible.",
        confidence=0.7,
        field_checked="month_year_of_manufacture",
        detected_value=value,
        expected_value="A valid month/year format for the manufacture/packing/import date.",
        source_image=product.get("source_image"),
        automation_level="heuristic",
        severity="medium",
    )


def validate_consumer_contact(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    name = product.get("consumer_care_name") or product.get("consumer_complaint_name")
    address = product.get("consumer_care_address") or product.get("consumer_complaint_address")
    phone = product.get("consumer_care_phone") or product.get("consumer_complaint_phone")
    email = product.get("consumer_care_email") or product.get("consumer_complaint_email")
    missing = []
    for field_name, value in [("name", name), ("address", address), ("telephone", phone), ("email", email)]:
        if value is None or value == "":
            missing.append(field_name)

    if missing:
        return _result(
            rule,
            "Missing Declaration",
            f"Consumer complaint contact information is incomplete; missing: {', '.join(missing)}.",
            confidence=0.8,
            field_checked=missing,
            detected_value={"name": name, "address": address, "telephone": phone, "email": email},
            expected_value="Consumer complaint name, address, telephone and email where available.",
            source_image=product.get("source_image"),
            automation_level="automated",
            severity="high",
        )

    return _result(
        rule,
        "Compliant",
        "Consumer complaint contact information was detected and appears complete.",
        confidence=0.9,
        field_checked=["consumer_care_name", "consumer_care_address", "consumer_care_phone", "consumer_care_email"],
        detected_value={"name": name, "address": address, "telephone": phone, "email": email},
        source_image=product.get("source_image"),
        automation_level="automated",
        severity="high",
    )


def validate_font_dimensions(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    font_height = product.get("font_height_mm")
    if font_height is None:
        return _result(
            rule,
            "Requires Human Verification",
            "Minimum numeral/letter dimensions cannot be verified without a calibrated physical or vision measurement reference.",
            confidence=0.8,
            field_checked="font_height_mm",
            detected_value=font_height,
            expected_value="Calibrated font height measurement in millimetres when required.",
            source_image=product.get("source_image"),
            automation_level="human_verification",
            severity="medium",
        )

    calibration_ok = bool(product.get("calibrated"))
    if not calibration_ok:
        return _result(
            rule,
            "Requires Human Verification",
            "The rule requires a calibrated measurement to determine whether the font dimensions satisfy minimum size requirements.",
            confidence=0.8,
            field_checked="font_height_mm",
            detected_value=font_height,
            expected_value="A calibrated measurement demonstrating minimum size compliance.",
            source_image=product.get("source_image"),
            automation_level="human_verification",
            severity="medium",
        )

    if float(font_height) < 0.8:
        return _result(
            rule,
            "Potential Non-Compliance",
            "The measured font height appears below the minimum required dimensions for the display panel.",
            confidence=0.76,
            field_checked="font_height_mm",
            detected_value=font_height,
            expected_value="Minimum acceptable numeral/letter height based on package quantity and panel conditions.",
            source_image=product.get("source_image"),
            automation_level="human_verification",
            severity="medium",
        )

    return _result(
        rule,
        "Compliant",
        "The font size appears to satisfy minimum dimensions for the package display panel.",
        confidence=0.9,
        field_checked="font_height_mm",
        detected_value=font_height,
        expected_value="Minimum acceptable font height under the package's display-panel conditions.",
        source_image=product.get("source_image"),
        automation_level="human_verification",
        severity="medium",
    )


def validate_principal_display_panel(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    if product.get("declaration_found_on_expected_panel") is True:
        return _result(
            rule,
            "Compliant",
            "The declaration was detected on the expected principal display panel.",
            confidence=0.85,
            field_checked="declaration_found_on_expected_panel",
            detected_value=True,
            expected_value="Required declarations on the principal display panel.",
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="medium",
        )
    if product.get("declaration_found_on_expected_panel") is False:
        return _result(
            rule,
            "Potential Non-Compliance",
            "The required declaration appears to be located on the wrong panel or outside the expected principal display panel.",
            confidence=0.8,
            field_checked="declaration_found_on_expected_panel",
            detected_value=False,
            expected_value="Declarations on the principal display panel.",
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="medium",
        )
    return _result(
        rule,
        "Requires Human Verification",
        "The package panel information is insufficient to confirm whether the declaration is on the principal display panel.",
        confidence=0.6,
        field_checked="pdp_expected",
        detected_value=product.get("pdp_expected"),
        expected_value="Required declarations appearing on the principal display panel.",
        source_image=product.get("source_image"),
        automation_level="heuristic",
        severity="medium",
    )


def validate_clear_space(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    clear_space_ok = product.get("clear_space_ok")
    if clear_space_ok is False:
        return _result(
            rule,
            "Potential Non-Compliance",
            "The quantity declaration does not appear to have the required clear space around it.",
            confidence=0.7,
            field_checked="clear_space_ok",
            detected_value=False,
            expected_value="Required clear space around the quantity declaration.",
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="medium",
        )
    if clear_space_ok is None:
        return _result(
            rule,
            "Requires Human Verification",
            "No reliable computer-vision or layout analysis is available to verify the quantity declaration clear-space requirement.",
            confidence=0.6,
            field_checked="clear_space_ok",
            detected_value=None,
            expected_value="Clear space around the designated quantity declaration.",
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="medium",
        )
    return _result(
        rule,
        "Compliant",
        "The quantity declaration clear-space requirement appears satisfied.",
        confidence=0.9,
        field_checked="clear_space_ok",
        detected_value=True,
        expected_value="Required clear space around the quantity declaration.",
        source_image=product.get("source_image"),
        automation_level="heuristic",
        severity="medium",
    )


def validate_returnable_bottle(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    if not product.get("returnable_bottle"):
        return _result(
            rule,
            "Compliant",
            "Returnable-bottle MRP placement rules are not applicable for this package.",
            confidence=1.0,
            field_checked="returnable_bottle",
            detected_value=False,
            expected_value="Applicable returnable-bottle MRP placement rules where relevant.",
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="medium",
        )

    mrp = product.get("mrp")
    if isinstance(mrp, dict) and mrp.get("source_image") == "cap":
        return _result(
            rule,
            "Compliant",
            "The returnable bottle MRP is appropriately declared on the cap and not incorrectly treated as absent from the main bottle label.",
            confidence=0.95,
            field_checked="mrp",
            detected_value=mrp,
            expected_value="MRP on the cap or bottle for applicable returnable beverage containers.",
            source_image="cap",
            automation_level="heuristic",
            severity="medium",
        )

    if product.get("bottle_label_mrp") is None and product.get("source_image") == "cap":
        return _result(
            rule,
            "Compliant",
            "The relevant returnable-bottle package image indicates the MRP is on the cap rather than the main bottle label.",
            confidence=0.9,
            field_checked="source_image",
            detected_value="cap",
            expected_value="MRP on the cap or bottle as applicable.",
            source_image="cap",
            automation_level="heuristic",
            severity="medium",
        )

    return _result(
        rule,
        "Requires Human Verification",
        "The returnable bottle location of the MRP cannot be conclusively verified from the supplied package metadata.",
        confidence=0.7,
        field_checked="mrp",
        detected_value=mrp,
        expected_value="MRP on the crown cap, bottle or both for returnable beverage packaging.",
        source_image=product.get("source_image"),
        automation_level="heuristic",
        severity="medium",
    )


def validate_legibility(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    ocr_conf = product.get("ocr_confidence")
    readability = product.get("readability_score")
    if ocr_conf is not None and ocr_conf < 0.7:
        return _result(
            rule,
            "Unable to Verify",
            "OCR readability confidence is too low to reliably verify declaration legibility.",
            confidence=float(ocr_conf),
            field_checked="ocr_confidence",
            detected_value=ocr_conf,
            expected_value="High-confidence OCR/readability for mandatory declarations.",
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="medium",
        )
    if readability is not None and readability < 0.7:
        return _result(
            rule,
            "Unable to Verify",
            "The declaration readability score is too low to verify legibility.",
            confidence=float(readability),
            field_checked="readability_score",
            detected_value=readability,
            expected_value="Readable declaration text with adequate contrast and visibility.",
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="medium",
        )
    if product.get("clear_visual_readability_failure"):
        return _result(
            rule,
            "Potential Non-Compliance",
            "The declaration text appears visually unreadable or obscured in a way that affects legibility.",
            confidence=0.8,
            field_checked="clear_visual_readability_failure",
            detected_value=True,
            expected_value="Legible, prominent, readily readable declarations.",
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="medium",
        )
    return _result(
        rule,
        "Compliant",
        "Declaration legibility and prominence appear acceptable.",
        confidence=0.9,
        field_checked="readability_score",
        detected_value=readability,
        expected_value="Legible and prominent declarations.",
        source_image=product.get("source_image"),
        automation_level="heuristic",
        severity="medium",
    )


def validate_mrp_contrast(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    score = product.get("mrp_contrast_score") or product.get("contrast_confidence")
    if score is None:
        return _result(
            rule,
            "Requires Human Verification",
            "No computer-vision measurement is available to confirm the MRP contrast requirement.",
            confidence=0.6,
            field_checked="mrp_contrast_score",
            detected_value=None,
            expected_value="MRP contrast conspicuous against the background.",
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="medium",
        )
    if float(score) < 0.7:
        return _result(
            rule,
            "Potential Non-Compliance",
            "The MRP contrast appears insufficient for conspicuous display.",
            confidence=float(score),
            field_checked="mrp_contrast_score",
            detected_value=score,
            expected_value="MRP contrast score above the threshold for conspicuous display.",
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="medium",
        )
    return _result(
        rule,
        "Compliant",
        "The MRP contrast score indicates the price is conspicuous against the background.",
        confidence=float(score),
        field_checked="mrp_contrast_score",
        detected_value=score,
        expected_value="Conspicuous MRP contrast.",
        source_image=product.get("source_image"),
        automation_level="heuristic",
        severity="medium",
    )


def validate_net_qty_contrast(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    score = product.get("net_quantity_contrast_score") or product.get("contrast_confidence")
    if score is None:
        return _result(
            rule,
            "Requires Human Verification",
            "No computer-vision contrast measure is available for the net quantity declaration.",
            confidence=0.6,
            field_checked="net_quantity_contrast_score",
            detected_value=None,
            expected_value="Net quantity contrast conspicuous against the background.",
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="medium",
        )
    if float(score) < 0.7:
        return _result(
            rule,
            "Potential Non-Compliance",
            "The net quantity contrast appears insufficient.",
            confidence=float(score),
            field_checked="net_quantity_contrast_score",
            detected_value=score,
            expected_value="Net quantity contrast above threshold for conspicuous display.",
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="medium",
        )
    return _result(
        rule,
        "Compliant",
        "The net quantity contrast appears adequate.",
        confidence=float(score),
        field_checked="net_quantity_contrast_score",
        detected_value=score,
        expected_value="Conspicuous net quantity contrast.",
        source_image=product.get("source_image"),
        automation_level="heuristic",
        severity="medium",
    )


def validate_liquid_display(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    if str(product.get("category") or "").lower() not in {"beverage", "alcoholic_beverage"}:
        return _result(
            rule,
            "Compliant",
            "The liquid-display declaration rule is not applicable to this product category.",
            confidence=1.0,
            field_checked="category",
            detected_value=product.get("category"),
            expected_value="Liquid-display check for beverages where the package is transparent or liquid is visible.",
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="medium",
        )
    if product.get("liquid_display_concern"):
        return _result(
            rule,
            "Potential Non-Compliance",
            "The declaration may need to be read through liquid or a transparent display area, raising a liquid-display concern.",
            confidence=0.75,
            field_checked="liquid_display_concern",
            detected_value=True,
            expected_value="Mandatory declarations readable without being viewed through the liquid contents.",
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="medium",
        )
    return _result(
        rule,
        "Requires Human Verification",
        "The available image metadata is insufficient to determine whether declarations must be read through liquid.",
        confidence=0.65,
        field_checked="liquid_display_concern",
        detected_value=product.get("liquid_display_concern"),
        expected_value="Declarations visible outside the liquid display area.",
        source_image=product.get("source_image"),
        automation_level="heuristic",
        severity="medium",
    )


def validate_outer_wrapper(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    if not product.get("has_outer_wrapper"):
        return _result(
            rule,
            "Compliant",
            "No outer wrapper or container exists, so the outer-wrapper rule is not applicable.",
            confidence=1.0,
            field_checked="has_outer_wrapper",
            detected_value=False,
            expected_value="Outer wrapper declarations where an outer wrapper/container exists.",
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="medium",
        )
    if product.get("wrapper_transparent") and product.get("inner_declarations_readable"):
        return _result(
            rule,
            "Compliant",
            "The wrapper is transparent and the inner declarations are clearly readable through it.",
            confidence=0.9,
            field_checked=["wrapper_transparent", "inner_declarations_readable"],
            detected_value={"wrapper_transparent": True, "inner_declarations_readable": True},
            expected_value="Outer wrapper not required to carry all declarations where inner declarations are clearly readable through a transparent wrapper.",
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="medium",
        )
    if product.get("required_declarations_on_wrapper") is False:
        return _result(
            rule,
            "Missing Declaration",
            "The wrapper does not carry the required declarations needed for an opaque outer package.",
            confidence=0.8,
            field_checked="required_declarations_on_wrapper",
            detected_value=False,
            expected_value="Mandatory particulars on the wrapper or outside container where required.",
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="medium",
        )
    return _result(
        rule,
        "Requires Human Verification",
        "The wrapper visibility and declaration-readability information are insufficient to determine whether outer declarations are required.",
        confidence=0.6,
        field_checked=["has_outer_wrapper", "wrapper_transparent", "inner_declarations_readable"],
        detected_value={
            "has_outer_wrapper": product.get("has_outer_wrapper"),
            "wrapper_transparent": product.get("wrapper_transparent"),
            "inner_declarations_readable": product.get("inner_declarations_readable"),
        },
        expected_value="Mandatory particulars on the outer wrapper or clear readable inner declarations for transparent wrappers.",
        source_image=product.get("source_image"),
        automation_level="heuristic",
        severity="medium",
    )


def validate_language_check(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    detected = product.get("detected_languages")
    if not detected:
        return _result(
            rule,
            "Unable to Verify",
            "The language detection does not identify the mandatory declaration language.",
            confidence=0.6,
            field_checked="detected_languages",
            detected_value=detected,
            expected_value="Mandatory particulars in English or Hindi (Devanagari), with additional languages permitted.",
            source_image=product.get("source_image"),
            automation_level="automated",
            severity="medium",
        )
    lang_values = [str(item).lower() for item in detected]
    supported = {item.lower() for item in ["English", "Hindi", "Devanagari"]}
    if not set(lang_values).intersection(supported):
        return _result(
            rule,
            "Potential Non-Compliance",
            "The mandatory particulars appear to be in an unsupported language and may not satisfy the English/Hindi requirement.",
            confidence=0.8,
            field_checked="detected_languages",
            detected_value=detected,
            expected_value="Mandatory particulars in English or Hindi (Devanagari) or a supported combination.",
            source_image=product.get("source_image"),
            automation_level="automated",
            severity="medium",
        )
    return _result(
        rule,
        "Compliant",
        "The detected declaration language includes English or Hindi (Devanagari), which is permitted.",
        confidence=0.9,
        field_checked="detected_languages",
        detected_value=detected,
        expected_value="English, Hindi (Devanagari) or an accepted supported combination.",
        source_image=product.get("source_image"),
        automation_level="automated",
        severity="medium",
    )


def validate_identification_address(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    fields = {
        "manufacturer_name": product.get("manufacturer_name"),
        "manufacturer_address": product.get("manufacturer_address"),
        "packer_name": product.get("packer_name"),
        "packer_address": product.get("packer_address"),
        "importer_name": product.get("importer_name"),
        "importer_address": product.get("importer_address"),
    }
    if not any(value not in (None, "") for value in fields.values()):
        return _result(
            rule,
            "Missing Declaration",
            "No manufacturer/packer/importer identification or address information is present.",
            confidence=0.9,
            field_checked=list(fields.keys()),
            detected_value=fields,
            expected_value="Full identification and complete address for the relevant manufacturer/packer/importer entity.",
            source_image=product.get("source_image"),
            automation_level="automated",
            severity="high",
        )

    missing = [name for name, value in fields.items() if name.endswith("_name") and value in (None, "")] or [
        name for name, value in fields.items() if name.endswith("_address") and value in (None, "")
    ] if any(name.endswith("_name") for name in fields) else []
    if missing:
        return _result(
            rule,
            "Missing Declaration",
            f"The relevant manufacturer/packer/importer entity appears identified but the address or identifying field is missing: {', '.join(missing)}.",
            confidence=0.8,
            field_checked=missing,
            detected_value=fields,
            expected_value="Complete address and entity identification for the applicable party.",
            source_image=product.get("source_image"),
            automation_level="automated",
            severity="high",
        )
    return _result(
        rule,
        "Compliant",
        "Manufacturer/packer/importer identification and address information appear complete.",
        confidence=0.9,
        field_checked=list(fields.keys()),
        detected_value=fields,
        source_image=product.get("source_image"),
        automation_level="automated",
        severity="high",
    )


def validate_quantity_excludes_wrapper(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    gross_weight = product.get("gross_weight")
    packaging_weight = product.get("packaging_weight")
    net_weight = product.get("net_weight")
    if gross_weight is None and packaging_weight is None and net_weight is None:
        return _result(
            rule,
            "Requires Human Verification",
            "Actual net quantity against packaging material cannot be established from a package photograph alone.",
            confidence=0.7,
            field_checked=["gross_weight", "packaging_weight", "net_weight"],
            detected_value={"gross_weight": gross_weight, "packaging_weight": packaging_weight, "net_weight": net_weight},
            expected_value="Physical confirmation that net quantity excludes wrappers and packaging material.",
            source_image=product.get("source_image"),
            automation_level="physical_verification",
            severity="high",
        )
    if gross_weight is not None and packaging_weight is not None and net_weight is not None:
        if abs(float(gross_weight) - float(packaging_weight) - float(net_weight)) > 1e-9:
            return _result(
                rule,
                "Potential Non-Compliance",
                "The supplied physical weights do not reconcile to a net quantity excluding wrapper and packaging material.",
                confidence=0.8,
                field_checked=["gross_weight", "packaging_weight", "net_weight"],
                detected_value={"gross_weight": gross_weight, "packaging_weight": packaging_weight, "net_weight": net_weight},
                expected_value="Gross weight - packaging weight = net quantity.",
                source_image=product.get("source_image"),
                automation_level="physical_verification",
                severity="high",
            )
        return _result(
            rule,
            "Compliant",
            "The supplied gross, packaging and net weights reconcile to exclude wrapper and packaging material.",
            confidence=0.9,
            field_checked=["gross_weight", "packaging_weight", "net_weight"],
            detected_value={"gross_weight": gross_weight, "packaging_weight": packaging_weight, "net_weight": net_weight},
            expected_value="Gross minus packaging equals net quantity.",
            source_image=product.get("source_image"),
            automation_level="physical_verification",
            severity="high",
        )
    return _result(
        rule,
        "Requires Human Verification",
        "Partial physical measurement data is available, but a reliable net-quantity check still requires human verification.",
        confidence=0.7,
        field_checked=["gross_weight", "packaging_weight", "net_weight"],
        detected_value={"gross_weight": gross_weight, "packaging_weight": packaging_weight, "net_weight": net_weight},
        expected_value="Complete measurements enabling reconciliation of gross, packaging and net quantities.",
        source_image=product.get("source_image"),
        automation_level="physical_verification",
        severity="high",
    )


def validate_quantity_basis_match(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    category = str(product.get("category") or "").lower()
    if not category:
        return _result(
            rule,
            "Unable to Verify",
            "The product category is unknown, so the applicable quantity basis cannot be assessed reliably.",
            confidence=0.6,
            field_checked="category",
            detected_value=category,
            expected_value="A known commodity category such as food, beverage, alcoholic_beverage or other.",
            source_image=product.get("source_image"),
            automation_level="automated",
            severity="high",
        )

    basis = str(product.get("sale_basis") or "").lower()
    qty = _as_text(product.get("net_quantity"))
    if basis in {"mass", "solid", "semi-solid", "viscous", "solid-liquid mixture"} and not re.search(r"\b(g|kg|mg)\b", qty.lower()):
        return _result(
            rule,
            "Potential Non-Compliance",
            "The quantity basis is mass-based but the declaration does not use a mass unit such as g or kg.",
            confidence=0.8,
            field_checked=["sale_basis", "net_quantity"],
            detected_value={"sale_basis": basis, "net_quantity": qty},
            expected_value="Mass basis using g/kg/mg units for solid or semi-solid goods.",
            source_image=product.get("source_image"),
            automation_level="automated",
            severity="high",
        )
    if basis in {"liquid", "volume"} and not re.search(r"\b(ml|l|litre|liter)\b", qty.lower()):
        return _result(
            rule,
            "Potential Non-Compliance",
            "The quantity basis is liquid/volume-based but the declaration does not use a volume unit.",
            confidence=0.8,
            field_checked=["sale_basis", "net_quantity"],
            detected_value={"sale_basis": basis, "net_quantity": qty},
            expected_value="Volume basis using ml/L units for liquid goods.",
            source_image=product.get("source_image"),
            automation_level="automated",
            severity="high",
        )
    if basis in {"length"} and not re.search(r"\b(cm|m)\b", qty.lower()):
        return _result(
            rule,
            "Potential Non-Compliance",
            "The quantity basis is linear but the declaration does not use length units.",
            confidence=0.8,
            field_checked=["sale_basis", "net_quantity"],
            detected_value={"sale_basis": basis, "net_quantity": qty},
            expected_value="Length basis using cm or m.",
            source_image=product.get("source_image"),
            automation_level="automated",
            severity="high",
        )
    return _result(
        rule,
        "Compliant",
        "The quantity declaration basis is consistent with the product's sale basis.",
        confidence=0.9,
        field_checked=["sale_basis", "net_quantity"],
        detected_value={"sale_basis": basis, "net_quantity": qty},
        expected_value="A quantity basis that matches the commodity type and sale format.",
        source_image=product.get("source_image"),
        automation_level="automated",
        severity="high",
    )


def validate_misleading_quantity(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    text = _as_text(product.get("net_quantity"))
    lowered = text.lower()
    suspicious = [phrase for phrase in SUSPICIOUS_QUANTITY_WORDS if phrase in lowered]
    if suspicious:
        return _result(
            rule,
            "Potential Non-Compliance",
            "The quantity wording appears potentially misleading or exaggerated, suggesting a misleading impression.",
            confidence=0.8,
            field_checked="net_quantity",
            detected_value=text,
            expected_value="A clear, non-misleading quantity declaration without exaggerated or promotional wording.",
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="medium",
        )
    return _result(
        rule,
        "Requires Human Verification",
        "The quantity wording does not obviously trigger a misleading impression, but a human review may still be appropriate if the language is ambiguous.",
        confidence=0.65,
        field_checked="net_quantity",
        detected_value=text,
        expected_value="A quantity declaration that does not create an exaggerated, misleading or inadequate impression.",
        source_image=product.get("source_image"),
        automation_level="heuristic",
        severity="medium",
    )


def validate_number_count(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    sale_basis = str(product.get("sale_basis") or "").lower()
    qty = _as_text(product.get("net_quantity"))
    if sale_basis in {"number", "count"}:
        if re.search(r"\b(n|u|number|count|pcs|piece|pieces|nos|no)\b", qty.lower()):
            return _result(
                rule,
                "Compliant",
                "The reported quantity basis is consistent with a number-based commodity.",
                confidence=0.9,
                field_checked=["sale_basis", "net_quantity"],
                detected_value={"sale_basis": sale_basis, "net_quantity": qty},
                expected_value="Number/count notation for products sold by number.",
                source_image=product.get("source_image"),
                automation_level="automated",
                severity="medium",
            )
        return _result(
            rule,
            "Potential Non-Compliance",
            "The product is sold by number, but the quantity declaration does not use a count-based unit or notation.",
            confidence=0.8,
            field_checked=["sale_basis", "net_quantity"],
            detected_value={"sale_basis": sale_basis, "net_quantity": qty},
            expected_value="Number/count notation such as N, U or equivalent count basis.",
            source_image=product.get("source_image"),
            automation_level="automated",
            severity="medium",
        )
    return _result(
        rule,
        "Compliant",
        "Number/count basis is not applicable for this commodity.",
        confidence=1.0,
        field_checked="sale_basis",
        detected_value=sale_basis,
        expected_value="Count-based declaration only where applicable.",
        source_image=product.get("source_image"),
        automation_level="automated",
        severity="medium",
    )


def validate_special_commodity_rule(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    commodity = (product.get("special_commodity_type") or product.get("commodity_type") or product.get("category") or "").lower()
    allowed = {str(item).lower() for item in rule.get("special_commodity_types", [])}
    if commodity not in allowed:
        return _result(
            rule,
            "Compliant",
            "The special commodity rule is not applicable to this package category.",
            confidence=1.0,
            field_checked="special_commodity_type",
            detected_value=commodity,
            expected_value="Special commodity declarations only when the relevant special commodity category is involved.",
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="low",
        )
    return _result(
        rule,
        "Requires Human Verification",
        "A special commodity declaration rule may apply, but the detailed measurement or category conditions require human review.",
        confidence=0.7,
        field_checked="special_commodity_type",
        detected_value=commodity,
        expected_value="Applicable category-specific special commodity declaration requirements.",
        source_image=product.get("source_image"),
        automation_level="human_verification",
        severity="low",
    )


def validate_dealer_workflow(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    overall_status = str(product.get("overall_compliance_status") or "Compliant")
    dealer_action = str(product.get("dealer_action") or "").lower()
    if dealer_action in {"sell", "display", "store", "distribute"} and overall_status not in {"Compliant", "Not Applicable"}:
        return _result(
            rule,
            "Potential Non-Compliance",
            "The dealer attempted to sell, display, distribute or store a product whose overall compliance status remains unresolved or non-compliant.",
            confidence=0.8,
            field_checked=["overall_compliance_status", "dealer_action"],
            detected_value={"overall_compliance_status": overall_status, "dealer_action": dealer_action},
            expected_value="No sale or distribution of unresolved non-compliant packaged commodities.",
            source_image=product.get("source_image"),
            automation_level="workflow",
            severity="medium",
        )
    return _result(
        rule,
        "Compliant",
        "The dealer action is consistent with the current compliance status and does not present a workflow violation.",
        confidence=0.9,
        field_checked=["overall_compliance_status", "dealer_action"],
        detected_value={"overall_compliance_status": overall_status, "dealer_action": dealer_action},
        expected_value="No sale or display of items with unresolved non-compliance.",
        source_image=product.get("source_image"),
        automation_level="workflow",
        severity="medium",
    )


def validate_sale_price_limit(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    declared_mrp = product.get("declared_mrp")
    actual_sale_price = product.get("actual_sale_price")
    if actual_sale_price is None:
        return _result(
            rule,
            "Unable to Verify",
            "The actual sale price is unavailable, so the retail-price compliance check cannot be completed.",
            confidence=0.6,
            field_checked=["declared_mrp", "actual_sale_price"],
            detected_value={"declared_mrp": declared_mrp, "actual_sale_price": actual_sale_price},
            expected_value="Actual retail sale price not exceeding the declared MRP.",
            source_image=product.get("source_image"),
            automation_level="workflow",
            severity="medium",
        )
    if float(actual_sale_price) > float(declared_mrp or 0):
        return _result(
            rule,
            "Potential Non-Compliance",
            "The actual sale price exceeds the declared MRP, which breaches the retail price limit.",
            confidence=0.9,
            field_checked=["declared_mrp", "actual_sale_price"],
            detected_value={"declared_mrp": declared_mrp, "actual_sale_price": actual_sale_price},
            expected_value="Actual sale price <= declared MRP.",
            source_image=product.get("source_image"),
            automation_level="workflow",
            severity="medium",
        )
    return _result(
        rule,
        "Compliant",
        "The actual sale price does not exceed the declared MRP.",
        confidence=0.9,
        field_checked=["declared_mrp", "actual_sale_price"],
        detected_value={"declared_mrp": declared_mrp, "actual_sale_price": actual_sale_price},
        expected_value="Actual sale price <= declared MRP.",
        source_image=product.get("source_image"),
        automation_level="workflow",
        severity="medium",
    )


def validate_mrp_obscured(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    if product.get("mrp_obscured") or product.get("mrp_overwritten") or product.get("mrp_sticker_detected"):
        return _result(
            rule,
            "Potential Non-Compliance",
            "The MRP appears to be obscured, overwritten or altered in a way that may violate the requirement.",
            confidence=0.85,
            field_checked=["mrp_obscured", "mrp_overwritten", "mrp_sticker_detected"],
            detected_value={
                "mrp_obscured": product.get("mrp_obscured"),
                "mrp_overwritten": product.get("mrp_overwritten"),
                "mrp_sticker_detected": product.get("mrp_sticker_detected"),
            },
            expected_value="An unobscured, unaltered MRP declaration.",
            source_image=product.get("source_image"),
            automation_level="heuristic",
            severity="high",
        )
    return _result(
        rule,
        "Requires Human Verification",
        "The image quality is insufficient to determine whether the MRP has been obscured, altered or smudged.",
        confidence=0.6,
        field_checked=["mrp_obscured", "mrp_overwritten", "mrp_sticker_detected"],
        detected_value={
            "mrp_obscured": product.get("mrp_obscured"),
            "mrp_overwritten": product.get("mrp_overwritten"),
            "mrp_sticker_detected": product.get("mrp_sticker_detected"),
        },
        expected_value="No obscuring or overwriting of the declared MRP.",
        source_image=product.get("source_image"),
        automation_level="heuristic",
        severity="high",
    )


def validate_physical_sampling(rule: dict[str, Any], product: dict[str, Any]) -> dict[str, Any]:
    if product.get("physical_test_verified"):
        return _result(
            rule,
            "Compliant",
            "Physical sampling and MPE review data has been supplied and verified.",
            confidence=1.0,
            field_checked=["physical_sample_count", "measured_quantities", "statistical_average", "maximum_permissible_error"],
            detected_value={
                "physical_sample_count": product.get("physical_sample_count"),
                "measured_quantities": product.get("measured_quantities"),
                "statistical_average": product.get("statistical_average"),
                "maximum_permissible_error": product.get("maximum_permissible_error"),
            },
            expected_value="Physical sample test with actual measured quantities, average and MPE data.",
            source_image=product.get("source_image"),
            automation_level="physical_verification",
            severity="high",
        )
    return _result(
        rule,
        "Requires Human Verification",
        "A package photograph cannot reliably establish actual net quantity, average quantity or maximum permissible error. Physical testing is required.",
        confidence=0.8,
        field_checked=["physical_sample_count", "statistical_average", "maximum_permissible_error"],
        detected_value={
            "physical_sample_count": product.get("physical_sample_count"),
            "measured_quantities": product.get("measured_quantities"),
            "statistical_average": product.get("statistical_average"),
            "maximum_permissible_error": product.get("maximum_permissible_error"),
        },
        expected_value="Physical sampling with measured quantities, average and MPE verification.",
        source_image=product.get("source_image"),
        automation_level="physical_verification",
        severity="high",
    )


VALIDATOR_MAP = {
    "manufacturer_details": validate_manufacturer_details,
    "common_name": validate_common_name,
    "net_quantity_check": validate_net_quantity,
    "date_requirement": validate_date_requirement,
    "mrp_check": validate_mrp,
    "month_year_check": validate_month_year_rule,
    "consumer_contact_check": validate_consumer_contact,
    "font_dimensions_check": validate_font_dimensions,
    "pdp_placement_check": validate_principal_display_panel,
    "clear_space_check": validate_clear_space,
    "returnable_bottle_check": validate_returnable_bottle,
    "legibility_check": validate_legibility,
    "mrp_contrast_check": validate_mrp_contrast,
    "net_qty_contrast_check": validate_net_qty_contrast,
    "liquid_display_check": validate_liquid_display,
    "outer_wrapper_check": validate_outer_wrapper,
    "language_check": validate_language_check,
    "manufacturer_address_check": validate_identification_address,
    "quantity_excludes_wrapper_check": validate_quantity_excludes_wrapper,
    "quantity_basis_check": validate_quantity_basis_match,
    "misleading_quantity_check": validate_misleading_quantity,
    "number_count_check": validate_number_count,
    "special_commodity_check": validate_special_commodity_rule,
    "dealer_workflow_check": validate_dealer_workflow,
    "sale_price_limit_check": validate_sale_price_limit,
    "mrp_obscured_check": validate_mrp_obscured,
    "physical_sampling_check": validate_physical_sampling,
}
