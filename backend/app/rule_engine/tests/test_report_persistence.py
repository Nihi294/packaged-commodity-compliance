import json
from datetime import date, datetime, timezone
from types import SimpleNamespace

from app.api.inspections import _persist_report


class FakeSession:
    def add(self, record):
        self.record = record

    def commit(self):
        json.dumps(self.record.report_data)

    def refresh(self, record):
        return record


def test_report_data_with_nested_datetimes_is_persistable(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    timestamp = datetime(2026, 9, 7, 12, 30, tzinfo=timezone.utc)
    report = {
        "inspection_summary": {"verified_at": timestamp},
        "comments": [{"timestamp": timestamp.date()}],
        "nested": [{"created_at": timestamp}],
    }
    db = FakeSession()
    record = _persist_report(
        db,
        SimpleNamespace(id=42),
        SimpleNamespace(id=7),
        report,
        "JSON",
        b"{}",
        "application/json",
        "json",
    )

    assert record.report_data["inspection_summary"]["verified_at"] == "2026-09-07T12:30:00+00:00"
    assert record.report_data["comments"][0]["timestamp"] == "2026-09-07"
    assert record.report_data["nested"][0]["created_at"] == "2026-09-07T12:30:00+00:00"
