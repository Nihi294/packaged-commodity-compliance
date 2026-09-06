from zipfile import ZipFile
from io import BytesIO

from app.reports.service import build_officer_verified_report, render_docx, render_pdf
from app.rule_engine.mock_data import MOCK_PRODUCT, mock_findings


def test_verified_report_preserves_ai_and_officer_sections():
    findings = mock_findings()
    report = build_officer_verified_report(
        {
            "id": 1,
            "status": "VERIFIED",
            "final_outcome": "NON_COMPLIANT",
            "verified_by": 7,
            "assessment": {"product": MOCK_PRODUCT, "rule_results": [], "declarations": [], "screening_score": 50},
            "findings": findings,
            "observations": [{"observation_id": 1, "description": "Observed", "evidence": []}],
            "evidence": [],
            "comments": [{"comment": "Reviewed", "officer": 7}],
        }
    )
    assert report["title"] == "OFFICER-VERIFIED COMPLIANCE REPORT"
    assert report["officer_verification_record"][0]["original_ai_status"] == "POTENTIAL_VIOLATION"
    assert report["officer_added_findings"][0]["source"] == "OFFICER"
    assert report["officer_observations"]
    assert report["overall_inspection_comments"]
    assert report["ai_assessment_preserved"]


def test_verified_report_exports_are_non_empty():
    report = build_officer_verified_report({"id": 1, "status": "VERIFIED", "assessment": {}, "findings": []})
    pdf = render_pdf(report)
    docx = render_docx(report)
    assert pdf.startswith(b"%PDF")
    assert docx.startswith(b"PK")


def test_renderers_use_readable_sections_instead_of_raw_python_containers():
    report = build_officer_verified_report(
        {
            "id": 1,
            "status": "VERIFIED",
            "final_outcome": "NON_COMPLIANT",
            "assessment": {"product": {"product_name": "Test Rice", "category": "Food", "net_quantity": {"value": "1 kg"}}, "declarations": [], "rule_results": [], "screening_score": 50},
            "findings": [],
            "observations": [],
            "comments": [],
            "evidence": [],
        }
    )
    pdf = render_pdf(report)
    with ZipFile(BytesIO(render_docx(report))) as archive:
        docx_text = archive.read("word/document.xml").decode("utf-8")
    assert pdf.count(b"stream") > 1
    assert "PRODUCT &amp; DECLARATION ANALYSIS" in docx_text
    assert "Test Rice" in docx_text
    assert "{'product':" not in docx_text
    assert "AI findings are screening results and require officer verification. This report records the officer-verified inspection decision." not in docx_text
