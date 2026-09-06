from app.rule_engine.assessment import (
    COMPLIANT,
    NEEDS_VERIFICATION,
    POTENTIAL_VIOLATION,
    generate_initial_assessment,
    screening_score,
)


def test_retail_applicability_runs_before_rules():
    result = generate_initial_assessment({"category": "food", "quantity_value": 30, "quantity_unit": "kg"})
    assert result["applicability"]["applicable"] is False
    assert result["rule_results"] == []


def test_uncertain_data_is_needs_verification_and_score_is_deterministic():
    results = [{"status": COMPLIANT}, {"status": POTENTIAL_VIOLATION}, {"status": NEEDS_VERIFICATION}]
    assert screening_score(results) == 50.0

