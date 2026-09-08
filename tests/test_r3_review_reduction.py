from pathlib import Path

from translation_quarantine.r3.r3_bulk_evidence import acquire_and_freeze


ROOT = Path(__file__).resolve().parents[1]


def test_review_reduction_uses_exact_reference_for_high_risk_and_transparent_wording(monkeypatch):
    selected = [
        {"canonical": "girl_on_top", "risk_class": "CRITICAL", "semantic_class": ""},
        {"canonical": "blue_sky", "risk_class": "MEDIUM", "semantic_class": ""},
        {"canonical": "holding_staff", "risk_class": "CRITICAL", "semantic_class": ""},
    ]
    queue_path = ROOT / "translation_quarantine" / "missing_candidates.csv"
    monkeypatch.setattr("translation_quarantine.r3.r3_bulk_evidence.write_jsonl", lambda _path, _rows: None)
    monkeypatch.setattr("translation_quarantine.r3.r3_bulk_evidence.write_json", lambda _path, _value: None)
    evidence = acquire_and_freeze(
        ROOT, selected, queue_path, ROOT / "unused-review.jsonl",
        campaign_id="issue36-review-reduction-test",
        review_reduction=True,
        report_path=ROOT / "unused-review-report.json",
    )
    by_role = {(row["canonical"], row["evidence_role"]): row for row in evidence}
    assert by_role[("girl_on_top", "SEMANTIC_SCOPE")]["scope_basis"] == "EXACT_CANONICAL_AUTHORITATIVE_REFERENCE"
    assert by_role[("girl_on_top", "WORDING_CANDIDATE")]["source_type"] == "local_exact_authoritative_reference_wording"
    assert by_role[("blue_sky", "SEMANTIC_SCOPE")]["scope_basis"] == "TRANSPARENT_CANONICAL_COMPOSITION"
    assert by_role[("blue_sky", "WORDING_CANDIDATE")]["source_type"] == "local_overlay_wording_candidate"
    assert ("holding_staff", "SEMANTIC_SCOPE") not in by_role
    assert all(
        row["source_type"] != "local_overlay_wording_candidate"
        or row["evidence_role"] == "WORDING_CANDIDATE"
        for row in evidence
    )
