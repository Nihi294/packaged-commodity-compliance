import re
from typing import Any


def _clean(value: str | None) -> str | None:
    if not value:
        return None

    value = re.sub(r"\s+", " ", value).strip(" :,-.\t")

    return value or None


def _search(pattern: str, text: str, flags=re.IGNORECASE) -> str | None:
    match = re.search(pattern, text, flags)
    if not match:
        return None

    return _clean(match.group(1))


def extract_declarations(text: str) -> dict[str, Any]:
    """
    Convert raw OCR text into structured packaged-commodity declarations.

    This is an extraction layer only.
    It does NOT decide legal compliance.
    """

    result: dict[str, Any] = {}

    # ---------------------------------------------------------
    # MANUFACTURER
    # ---------------------------------------------------------

    manufacturer = _search(
        r"(?:MANUFACTURED\s*BY|MANUFACTURER)\s*[:\-]?\s*(.+)",
        text,
    )

    if manufacturer:
        result["manufacturer_name"] = manufacturer

    # ---------------------------------------------------------
    # PACKER
    # ---------------------------------------------------------

    packer = _search(
        r"(?:PACKED\s*BY|PACKER)\s*[:\-]?\s*(.+)",
        text,
    )

    if packer:
        result["packer_name"] = packer

    # ---------------------------------------------------------
    # MARKETER
    # ---------------------------------------------------------

    marketer = _search(
        r"(?:MARKETED\s*BY|MARKETER)\s*[:\-]?\s*(.+)",
        text,
    )

    if marketer:
        result["marketer_name"] = marketer

    # ---------------------------------------------------------
    # IMPORTER
    # ---------------------------------------------------------

    importer = _search(
        r"(?:IMPORTED\s*BY|IMPORTER)\s*[:\-]?\s*(.+)",
        text,
    )

    if importer:
        result["importer_name"] = importer

    # ---------------------------------------------------------
    # NET QUANTITY
    # ---------------------------------------------------------

    quantity_match = re.search(
        r"(?:NET\s*(?:QUANTITY|WT|WEIGHT|CONTENT))"
        r"\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)\s*"
        r"(kg|g|gm|grams?|l|lt|litre?s?|ml)",
        text,
        re.IGNORECASE,
    )

    if quantity_match:
        value = float(quantity_match.group(1))
        unit = quantity_match.group(2).lower()

        if value.is_integer():
            value = int(value)

        result["net_quantity"] = {
            "value": value,
            "unit": unit,
        }

        result["quantity_value"] = value
        result["quantity_unit"] = unit

    # ---------------------------------------------------------
    # MRP
    # ---------------------------------------------------------

    mrp = _search(
        r"(?:MRP|MAXIMUM\s+RETAIL\s+PRICE)"
        r"\s*(?:₹|RS\.?|INR)?\s*[:\-]?\s*"
        r"(?:₹|RS\.?|INR)?\s*(\d+(?:\.\d+)?)",
        text,
    )

    if mrp:
        result["mrp"] = mrp

    # ---------------------------------------------------------
    # MANUFACTURE DATE
    # ---------------------------------------------------------

    manufacture_date = _search(
        r"(?:MANUFACTURE\s*DATE|DATE\s*OF\s*MANUFACTURE|MFG\.?\s*DATE)"
        r"\s*[:\-]?\s*([A-Za-z0-9\/\-. ]+)",
        text,
    )

    if manufacture_date:
        result["manufacture_date"] = manufacture_date
        result["month_year_of_manufacture"] = manufacture_date

    # ---------------------------------------------------------
    # EXPIRY
    # ---------------------------------------------------------

    expiry = _search(
        r"(?:EXPIRY|EXP\.?|USE\s*BY|BEST\s*BEFORE)"
        r"\s*(?:DATE)?\s*[:\-]?\s*([A-Za-z0-9\/\-. ]+)",
        text,
    )

    if expiry:
        result["expiry_date"] = expiry

    # ---------------------------------------------------------
    # BATCH / LOT
    # ---------------------------------------------------------

    batch = _search(
        r"(?:BATCH\s*(?:NO\.?|NUMBER)?|LOT\s*(?:NO\.?|NUMBER)?)"
        r"\s*[:\-]?\s*([A-Za-z0-9\/\-.]+)",
        text,
    )

    if batch:
        result["batch_number"] = batch

    # ---------------------------------------------------------
    # FSSAI LICENSE
    # ---------------------------------------------------------

    fssai = _search(
        r"(?:LIC\.?\s*NO\.?|LICENSE\s*NO\.?|FSSAI)"
        r"\s*[:\-]?\s*(\d{8,20})",
        text,
    )

    if fssai:
        result["fssai_license"] = fssai

    # ---------------------------------------------------------
    # CONSUMER CARE PHONE
    # ---------------------------------------------------------

    phone_matches = re.findall(
        r"\b(?:\+91[\s\-]?)?[6-9]\d{9}\b|\b1800\d{7,8}\b",
        text,
    )

    if phone_matches:
        result["consumer_care_phone"] = phone_matches[0]

    # ---------------------------------------------------------
    # EMAIL
    # ---------------------------------------------------------

    email = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text,
        re.IGNORECASE,
    )

    if email:
        result["consumer_care_email"] = email.group(0)

    # ---------------------------------------------------------
    # WEBSITE
    # ---------------------------------------------------------

    website = re.search(
        r"\b(?:https?://)?(?:www\.)?[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?:/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=-]*)?",
        text,
        re.IGNORECASE,
    )

    if website:
        result["website"] = website.group(0)

    return result