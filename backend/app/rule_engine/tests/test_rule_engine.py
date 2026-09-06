import pytest

from app.rule_engine.engine import RuleEngine


def get_rule_result(results, rule_id):
    for item in results:
        if item["rule_id"] == rule_id:
            return item
    raise AssertionError(f"Rule {rule_id} not found")


def make_food_product(**overrides):
    product = {
        "category": "food",
        "source_type": "physical_package",
        "source_image": "front",
        "product_name": "Biscuits",
        "manufacturer_name": "Sahi Foods Pvt Ltd",
        "manufacturer_address": "Plot 12, Industrial Area, Bengaluru, Karnataka",
        "common_name": "Biscuits",
        "net_quantity": {"value": "200 g", "confidence": 0.95, "source_image": "front"},
        "mrp": {"value": "₹50", "confidence": 0.95, "source_image": "front"},
        "manufacture_date": "2025-01-15",
        "packing_date": "2025-01-16",
        "month_year_of_manufacture": "01/2025",
        "consumer_care_name": "Customer Care",
        "consumer_care_address": "Sahi Foods Pvt Ltd, Bengaluru",
        "consumer_care_phone": "+91 9876543210",
        "consumer_care_email": "care@sahifoods.example",
        "detected_languages": ["English", "Hindi"],
        "font_height_mm": 1.2,
        "font_measurement_confidence": 0.91,
        "calibrated": True,
        "mrp_contrast_score": 0.90,
        "net_quantity_contrast_score": 0.88,
        "clear_space_ok": True,
        "pdp_expected": "front",
        "declaration_found_on_expected_panel": True,
        "returnable_bottle": False,
        "has_outer_wrapper": False,
        "liquid_display_concern": False,
        "sale_basis": "mass",
        "declared_mrp": 50,
        "actual_sale_price": 50,
        "gross_weight": 250,
        "packaging_weight": 50,
        "net_weight": 200,
    }
    product.update(overrides)
    return product


def test_01_fully_compliant_food_package():
    engine = RuleEngine()
    results = engine.evaluate(make_food_product())
    assert results["overall_status"] == "Requires Human Verification"
    assert get_rule_result(results["results"], "PC-001")["status"] == "Compliant"
    assert get_rule_result(results["results"], "PC-003")["status"] == "Compliant"
    assert get_rule_result(results["results"], "PC-005")["status"] == "Compliant"


def test_02_missing_mrp():
    engine = RuleEngine()
    product = make_food_product(mrp=None)
    results = engine.evaluate(product)
    assert get_rule_result(results["results"], "PC-005")["status"] == "Missing Declaration"


def test_03_missing_manufacturer():
    engine = RuleEngine()
    product = make_food_product(manufacturer_name=None, manufacturer_address=None)
    results = engine.evaluate(product)
    assert get_rule_result(results["results"], "PC-001")["status"] == "Missing Declaration"


def test_04_missing_net_quantity():
    engine = RuleEngine()
    product = make_food_product(net_quantity=None)
    results = engine.evaluate(product)
    assert get_rule_result(results["results"], "PC-003")["status"] == "Missing Declaration"


def test_05_wrong_quantity_unit():
    engine = RuleEngine()
    product = make_food_product(net_quantity={"value": "200 pieces", "confidence": 0.95})
    results = engine.evaluate(product)
    status = get_rule_result(results["results"], "PC-003")["status"]
    assert status in {"Potential Non-Compliance", "Unable to Verify"}


def test_06_low_confidence_mrp():
    engine = RuleEngine()
    product = make_food_product(mrp={"value": "₹50", "confidence": 0.55, "source_image": "front"})
    results = engine.evaluate(product)
    assert get_rule_result(results["results"], "PC-005")["status"] == "Unable to Verify"


def test_07_font_size_check_without_calibration():
    engine = RuleEngine()
    product = make_food_product(font_height_mm=None, font_measurement_confidence=None, calibrated=False)
    results = engine.evaluate(product)
    assert get_rule_result(results["results"], "PC-008")["status"] == "Requires Human Verification"


def test_08_import_product_missing_country_of_origin():
    engine = RuleEngine()
    product = make_food_product(
        country_of_origin=None,
        importer_name="Imported by: Global Foods Importers",
        importer_address="New Delhi",
        category="other",
    )
    results = engine.evaluate(product)
    assert get_rule_result(results["results"], "PC-001")["status"] in {"Missing Declaration", "Unable to Verify"}


def test_09_mrp_unclear_or_incomplete():
    engine = RuleEngine()
    product = make_food_product(mrp={"value": "₹", "confidence": 0.76, "source_image": "front"})
    results = engine.evaluate(product)
    status = get_rule_result(results["results"], "PC-005")["status"]
    assert status in {"Potential Non-Compliance", "Unable to Verify"}


def test_10_beverage_with_liquid_display_concern():
    engine = RuleEngine()
    product = make_food_product(category="beverage", liquid_display_concern=True, product_name="Orange Drink")
    results = engine.evaluate(product)
    status = get_rule_result(results["results"], "PC-015")["status"]
    assert status in {"Potential Non-Compliance", "Requires Human Verification"}


def test_11_returnable_beverage_bottle_mrp_on_cap():
    engine = RuleEngine()
    product = make_food_product(
        category="beverage",
        returnable_bottle=True,
        source_image="cap",
        mrp={"value": "MRP ₹40", "confidence": 0.95, "source_image": "cap"},
        bottle_label_mrp=None,
    )
    results = engine.evaluate(product)
    assert get_rule_result(results["results"], "PC-011")["status"] == "Compliant"


def test_12_mandatory_particulars_not_in_hindi_or_english():
    engine = RuleEngine()
    product = make_food_product(detected_languages=["Tamil"])
    results = engine.evaluate(product)
    assert get_rule_result(results["results"], "PC-017")["status"] == "Potential Non-Compliance"


def test_13_transparent_wrapper_with_readable_inner_declarations():
    engine = RuleEngine()
    product = make_food_product(
        has_outer_wrapper=True,
        wrapper_transparent=True,
        inner_declarations_readable=True,
    )
    results = engine.evaluate(product)
    assert get_rule_result(results["results"], "PC-016")["status"] == "Compliant"


def test_14_opaque_wrapper_without_required_declarations():
    engine = RuleEngine()
    product = make_food_product(
        has_outer_wrapper=True,
        wrapper_transparent=False,
        required_declarations_on_wrapper=False,
    )
    results = engine.evaluate(product)
    status = get_rule_result(results["results"], "PC-016")["status"]
    assert status in {"Missing Declaration", "Potential Non-Compliance"}


def test_15_misleading_quantity_wording():
    engine = RuleEngine()
    product = make_food_product(net_quantity={"value": "200 g extra free", "confidence": 0.9, "source_image": "front"})
    results = engine.evaluate(product)
    status = get_rule_result(results["results"], "PC-021")["status"]
    assert status in {"Potential Non-Compliance", "Requires Human Verification"}


def test_16_actual_sale_price_greater_than_mrp():
    engine = RuleEngine()
    product = make_food_product(actual_sale_price=60, declared_mrp=50)
    results = engine.evaluate(product)
    assert get_rule_result(results["results"], "PC-028")["status"] == "Potential Non-Compliance"


def test_17_mrp_overwritten_or_obliterated():
    engine = RuleEngine()
    product = make_food_product(mrp_obscured=True, mrp_overwritten=True, mrp_sticker_detected=True)
    results = engine.evaluate(product)
    assert get_rule_result(results["results"], "PC-029")["status"] == "Potential Non-Compliance"


def test_18_physical_quantity_mpe_without_physical_data():
    engine = RuleEngine()
    product = make_food_product()
    results = engine.evaluate(product)
    assert get_rule_result(results["results"], "PC-030")["status"] == "Requires Human Verification"


def test_19_special_commodity_rules_not_applicable_to_food():
    engine = RuleEngine()
    product = make_food_product()
    results = engine.evaluate(product)
    for rule_id in ["PC-023", "PC-024", "PC-025", "PC-026"]:
        if any(item["rule_id"] == rule_id for item in results["results"]):
            rule = get_rule_result(results["results"], rule_id)
            assert rule["status"] in {"Compliant", "Requires Human Verification"}


def test_20_multi_violation_product():
    engine = RuleEngine()
    product = make_food_product(
        manufacturer_name=None,
        net_quantity=None,
        mrp=None,
        actual_sale_price=60,
        declared_mrp=50,
        detected_languages=["Tamil"],
        font_height_mm=None,
        calibrated=False,
    )
    results = engine.evaluate(product)
    assert results["overall_status"] in {"Requires Human Verification", "Missing Declaration"}
    assert any(item["rule_id"] == "PC-001" and item["status"] == "Missing Declaration" for item in results["results"])
    assert any(item["rule_id"] == "PC-005" and item["status"] == "Missing Declaration" for item in results["results"])
    assert any(item["rule_id"] == "PC-028" and item["status"] == "Potential Non-Compliance" for item in results["results"])


def test_21_smoke_demo_prints_rule_output():
    engine = RuleEngine()
    product = make_food_product()
    results = engine.evaluate(product)
    assert isinstance(results["results"], list)
    assert results["overall_status"] in {"Compliant", "Requires Human Verification", "Missing Declaration", "Potential Non-Compliance", "Unable to Verify"}


@pytest.mark.parametrize(
    "category, expected",
    [
        ("food", "Compliant"),
        ("beverage", "Compliant"),
        ("alcoholic_beverage", "Compliant"),
        ("other", "Compliant"),
    ],
)
def test_rule_engine_handles_categories(category, expected):
    engine = RuleEngine()
    product = make_food_product(category=category)
    results = engine.evaluate(product)
    assert results["overall_status"] in {expected, "Requires Human Verification"}
