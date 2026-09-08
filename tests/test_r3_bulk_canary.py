import json
from pathlib import Path

import pytest

from translation_quarantine.r3.r3_bulk_run import check_masked_rows
from translation_quarantine.r3.r3_bulk_evidence import (
    _exact_reference_index,
    acquire_and_freeze,
    transparent_composition_scope,
)
from translation_quarantine.r3.r3_bulk_select import CANARY_SEED, portable_csv_text_hash, select_canary, select_records
from translation_quarantine.r3.r3_common import stable_key


ROOT = Path(__file__).resolve().parents[1]


def test_canary_selection_is_200_unseen_and_seeded():
    queue = [{"canonical": f"canary_{index:03d}", "priority": "P0", "lanes": "general"} for index in range(240)]
    selected = select_records(queue, {f"canary_{index:03d}" for index in range(20)})
    assert len(selected) == 200
    assert len({row["canonical"] for row in selected}) == 200
    assert all(row["selection_key"] == stable_key(CANARY_SEED, row["canonical"]) for row in selected)


def test_canary_preflight_uses_portable_identity_for_frozen_git_sources():
    selection = select_canary(ROOT)
    assert selection["canary_size"] == 200
    assert selection["source_identity"]["missing_candidates.csv"]["current_git_blob"] == selection["source_identity"]["missing_candidates.csv"]["validated_git_blob"]
    assert selection["source_queue_portable_content_identity"]


def test_portable_source_identity_ignores_newlines_but_detects_field_change():
    lf = "canonical,priority\nfoo,P0\nbar,P1\n"
    crlf = lf.replace("\n", "\r\n")
    changed = "canonical,priority\nfoo,P0\nbar,P0\n"
    assert portable_csv_text_hash(lf) == portable_csv_text_hash(crlf)
    assert portable_csv_text_hash(lf) != portable_csv_text_hash(changed)


def test_masked_audit_leakage_checker_is_fail_closed():
    masked_rows = [{"canonical": "sample", "candidate_display": ""}]
    key = {"selected": [{"canonical": "sample", "audit_key": "secret"}]}
    result = check_masked_rows(masked_rows, key)
    assert result["ok"] is True
    assert check_masked_rows([{"canonical": "sample", "row_state": "READY"}], key)["ok"] is False


def test_bulk_evidence_freeze_keeps_unresolved_rows_identity_only(monkeypatch):
    selection = select_canary(ROOT)
    queue_path = ROOT / "translation_quarantine" / "missing_candidates.csv"
    monkeypatch.setattr(
        "translation_quarantine.r3.r3_bulk_evidence.write_jsonl",
        lambda _path, _rows: None,
    )
    evidence = acquire_and_freeze(ROOT, selection["selected"], queue_path, ROOT / "unused.jsonl")
    identities = {
        row["canonical"] for row in evidence if row["evidence_role"] == "IDENTITY_ONLY"
    }
    semantic = [row for row in evidence if row["evidence_role"] == "SEMANTIC_SCOPE"]
    wording = [row for row in evidence if row["evidence_role"] == "WORDING_CANDIDATE"]
    assert identities == {row["canonical"] for row in selection["selected"]}
    assert len(semantic) == len(wording) > 0
    assert all(row["frozen"] is True for row in evidence)
    assert all(row["scope_basis"] == "TRANSPARENT_CANONICAL_COMPOSITION" for row in semantic)


def test_bulk_evidence_expands_only_transparent_low_medium_compositions():
    assert transparent_composition_scope("blue_flower", "MEDIUM") is not None
    assert transparent_composition_scope("socks", "LOW") is not None
    assert transparent_composition_scope("simple_background", "MEDIUM") is None
    assert transparent_composition_scope("anal_object_insertion", "CRITICAL") is None
    assert transparent_composition_scope("holding_sword", "HIGH_POSE_ACTION") is None


def test_transparent_wording_safety_keeps_narrowing_or_ambiguous_terms_review(monkeypatch):
    selected = [{"canonical": name, "semantic_class": ""} for name in ("green_jacket", "sword", "cloud")]
    queue_path = ROOT / "translation_quarantine" / "missing_candidates.csv"
    monkeypatch.setattr("translation_quarantine.r3.r3_bulk_evidence.write_jsonl", lambda _path, _rows: None)
    monkeypatch.setattr("translation_quarantine.r3.r3_bulk_evidence.write_json", lambda _path, _value: None)
    evidence = acquire_and_freeze(
        ROOT, selected, queue_path, ROOT / "unused.jsonl",
        campaign_id="issue36-r3-bulk-remaining-test",
    )
    assert not [row for row in evidence if row.get("evidence_role") == "WORDING_CANDIDATE"]


def test_exact_reference_index_does_not_promote_alias_rows():
    index, _content_hash, _stats = _exact_reference_index(ROOT)
    assert "girl_on_top" in index
    assert index["girl_on_top"]["Tag"].replace(" ", "_") == "girl_on_top"
    assert "titjob" not in index


def test_overlay_wording_never_becomes_semantic_authority(monkeypatch):
    selected = [{"canonical": "blue_flower", "semantic_class": ""}]
    queue_path = ROOT / "translation_quarantine" / "missing_candidates.csv"
    monkeypatch.setattr(
        "translation_quarantine.r3.r3_bulk_evidence.write_jsonl",
        lambda _path, _rows: None,
    )
    monkeypatch.setattr(
        "translation_quarantine.r3.r3_bulk_evidence.write_json",
        lambda _path, _value: None,
    )
    evidence = acquire_and_freeze(
        ROOT, selected, queue_path, ROOT / "unused.jsonl",
        campaign_id="issue36-r3-bulk-remaining-test",
        report_path=ROOT / "unused-report.json",
    )
    semantic = [row for row in evidence if row["evidence_role"] == "SEMANTIC_SCOPE"]
    wording = [row for row in evidence if row["evidence_role"] == "WORDING_CANDIDATE"]
    assert semantic and wording
    assert all("overlay" not in row["source_type"] for row in semantic)
    assert all("semantic authority" in row["scope_note"] or "semantic authority" in row.get("scope_note", "") for row in wording)


def test_masked_audit50_is_50_rows_and_preserves_existing_audit20():
    base = ROOT / "translation_quarantine" / "r3_bulk_canary"
    existing = {
        json.loads(line)["canonical"]
        for line in (base / "masked_audit20_input.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    masked = [
        json.loads(line)
        for line in (base / "masked_audit50_input.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    leakage = json.loads((base / "masked_audit50_leakage_check.json").read_text(encoding="utf-8"))
    assert len(masked) == 50
    assert existing <= {row["canonical"] for row in masked}
    assert all(
        not set(row) & {
            "state", "risk", "reason", "key", "prior_verdict", "selection_group",
            "source_membership", "effective_risk_class", "display_state", "search_state",
            "bridge32_state", "row_state", "reason_codes", "audit_key",
        }
        for row in masked
    )
    assert leakage["ok"] is True
