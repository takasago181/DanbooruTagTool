from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path

import pytest

from translation_quarantine.r3.r3_build_blind_audit import build
from translation_quarantine.r3.r3_common import (
    derive_row_state,
    disallowed_search_reason,
    ensure_r3_output,
    issue32_fingerprint,
    issue32_propositions,
    classify_risk,
    term_class,
)
from translation_quarantine.r3.r3_run import _candidate_terms, run
from translation_quarantine.r3.r3_select_pilot import select_pilot
from translation_quarantine.r3.r3_verify import verify


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def r3_fixture_root():
    tmp_path = ROOT / "translation_quarantine" / "r3" / f".pytest-fixture-{uuid.uuid4().hex}"
    tmp_path.mkdir(parents=True)
    try:
        yield tmp_path
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def _quarantine_fixture(tmp_path: Path) -> Path:
    (tmp_path / "translation_quarantine").mkdir()
    for name in ("missing_candidates.csv", "phase1a_review.csv"):
        shutil.copyfile(ROOT / "translation_quarantine" / name, tmp_path / "translation_quarantine" / name)
    return tmp_path


def test_r3_known_failure_patterns_are_systemic_rules():
    assert classify_risk("1girl") == "MEDIUM"
    assert classify_risk("simple_background") == "MEDIUM"
    assert classify_risk("straddling") == "HIGH_POSE_ACTION"
    assert classify_risk("gaping") == "HIGH_ANATOMY_ADULT"
    assert classify_risk("cuffs") == "CRITICAL"
    assert disallowed_search_reason("ガールズイラスト", "1girl") == "CATEGORY_OR_NOISY_ALIAS"
    assert disallowed_search_reason("単色背景", "simple_background") == "NARROWER_THAN_CANONICAL"
    assert disallowed_search_reason("騎乗位", "straddling") == "SEXUAL_SUBTYPE_NARROWING"
    assert disallowed_search_reason("手錠", "cuffs") == "SUBTYPE_COLLISION_REQUIRES_SCOPE"


def _candidate(canonical: str, term: str, **extra):
    return _candidate_terms(
        [
            {
                "evidence_id": "scope",
                "canonical": canonical,
                "evidence_role": "SEMANTIC_SCOPE",
                "scope_note": "exact canonical scope",
                "frozen": True,
            },
            {
                "evidence_id": "term",
                "canonical": canonical,
                "evidence_role": "WORDING_CANDIDATE",
                "term": term,
                "term_class": "EXACT_SYNONYM",
                "search_equivalence_proof": "EXACT",
                "frozen": True,
                **extra,
            },
        ],
        canonical,
    )[0]


def test_search_safety_rejects_narrowing_but_not_direct_simple_background_form():
    narrow = _candidate("simple_background", "単色背景")
    direct = _candidate("simple_background", "シンプル背景")
    assert narrow["term_state"] == "REJECTED"
    assert narrow["rejection_reason"] == "NARROWER_THAN_CANONICAL"
    assert direct["rejection_reason"] != "NARROWER_THAN_CANONICAL"
    assert direct["term_state"] == "ACCEPTED"


def test_search_safety_rejects_count_attribute_and_relation_scope_changes():
    assert _candidate("1girl", "女の子")["term_state"] == "REJECTED"
    attribute = _candidate("1girl", "美少女")
    assert attribute["term_state"] == "REJECTED"
    assert attribute["rejection_reason"] == "ATTRIBUTE_ADDED"
    for relation in ("parent", "child", "adjacent", "actor_added", "target_added", "context_added"):
        result = _candidate("girl", "女性", candidate_relation=relation)
        assert result["term_state"] == "REJECTED", relation


def test_unproven_japanese_term_is_not_orthographic_or_ready():
    assert term_class("まつげ", "eyelashes") == "COMMON_EXACT_PARAPHRASE"
    result = _candidate_terms(
        [
            {"evidence_id": "scope", "canonical": "eyelashes", "evidence_role": "SEMANTIC_SCOPE", "frozen": True},
            {"evidence_id": "term", "canonical": "eyelashes", "evidence_role": "WORDING_CANDIDATE", "term": "まつげ", "frozen": True},
        ],
        "eyelashes",
    )[0]
    assert result["term_class"] != "ORTHOGRAPHIC_VARIANT"
    assert result["term_state"] == "REVIEW"


def test_high_or_critical_without_exact_scope_remains_review():
    result = _candidate_terms(
        [{
            "evidence_id": "term",
            "canonical": "gaping",
            "evidence_role": "WORDING_CANDIDATE",
            "term": "拡張",
            "term_class": "EXACT_SYNONYM",
            "search_equivalence_proof": "EXACT",
            "frozen": True,
        }],
        "gaping",
    )[0]
    assert result["term_state"] == "REVIEW"


def test_states_follow_contradiction_then_stale_then_review_priority():
    assert derive_row_state("READY", "READY", "UNCHANGED") == "READY"
    assert derive_row_state("REVIEW", "READY", "UNCHANGED") == "REVIEW"
    assert derive_row_state("READY", "READY", "STALE_REVIEW") == "STALE_REVIEW"
    assert derive_row_state("STALE_REVIEW", "READY", "CONTRADICTION") == "CONTRADICTION"


def test_issue32_fingerprint_ignores_generation_only_metadata():
    first = {"candidate_canonical": "feet", "support_class": "CORE_SUPPORT", "semantic_support_used": True, "generation_test_status": "NOT_TESTED"}
    second = {"candidate_canonical": "feet", "support_class": "CORE_SUPPORT", "semantic_support_used": True, "generation_test_status": "PASS"}
    assert issue32_fingerprint(first) == issue32_fingerprint(second)
    changed = {"candidate_canonical": "feet", "support_class": "DIFFERENT_RELATION", "semantic_support_used": True}
    assert issue32_fingerprint(first) != issue32_fingerprint(changed)


def test_translation_visible_proposition_allowlist_covers_meaning_width_and_support_usage():
    base = {
        "candidate_canonical": "example",
        "entity_scope": "body_part",
        "count": 1,
        "actor": "person",
        "ownership": "self",
        "target": "viewer",
        "body_site": "hand",
        "action_vs_state": "action",
        "intrinsic_relation": "holding",
        "pose": "standing",
        "spatial_requirement": "near",
        "required_qualifier": "left",
        "canonical_meaning_width": "exact",
        "support_class": "semantic_support",
        "semantic_support_used": True,
        "generation_weight": 1.5,
        "model_family": "ignored",
        "prompt_use_mode": "ignored",
    }
    propositions = issue32_propositions(base)
    assert propositions["count_cardinality"] == 1
    assert propositions["action_state"] == "action"
    assert propositions["intrinsic_relation"] == "holding"
    assert propositions["required_modifier"] == "left"
    assert propositions["canonical_meaning_width"] == "exact"
    assert propositions["semantic_support_relation"] == "semantic_support"
    without_support_use = dict(base, semantic_support_used=False)
    assert "semantic_support_relation" not in issue32_propositions(without_support_use)


def test_selection_is_deterministic_and_excludes_existing_phase1a_100(r3_fixture_root):
    root = _quarantine_fixture(r3_fixture_root)
    first = select_pilot(root)
    second = select_pilot(root)
    assert [row["canonical"] for row in first["selected"]] == [row["canonical"] for row in second["selected"]]
    assert len(first["selected"]) == 100
    assert first["achieved_stratum_counts"] == {
        "LOW": 25,
        "MEDIUM": 20,
        "HIGH_POSE_ACTION": 20,
        "HIGH_ANATOMY_ADULT": 20,
        "CRITICAL": 15,
    }
    excluded = {row["canonical"] for row in __import__("csv").DictReader((root / "translation_quarantine" / "phase1a_review.csv").open(encoding="utf-8"))}
    assert not excluded.intersection(row["canonical"] for row in first["selected"])
    assert {row["selection_stratum"] for row in first["selected"]} == set(first["requested_stratum_counts"])


def test_r3_run_blind_masking_and_protected_boundary(r3_fixture_root):
    root = _quarantine_fixture(r3_fixture_root)
    output = root / "translation_quarantine" / "r3"
    run(root, output)
    build(output)
    result = verify(root, output, rerun=True)
    assert result["ok"], result["errors"]
    assert result["deterministic_rerun_verification"] == "PASS"
    blind_rows = [json.loads(line) for line in (output / "blind30_input.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(blind_rows) == 30
    for row in blind_rows:
        assert not {"display_state", "search_state", "bridge32_state", "row_state", "reason_codes", "risk_class"}.intersection(row)
        assert all(set(term) == {"term", "term_class"} for term in row["search_terms"])
    summary = json.loads((output / "run_summary.json").read_text(encoding="utf-8"))
    assert summary["remaining_925_p0_processed"] is False
    assert summary["production_modified"] is False


def test_without_required_issue32_overlap_is_not_missing(r3_fixture_root):
    root = _quarantine_fixture(r3_fixture_root)
    output = root / "translation_quarantine" / "r3"
    run(root, output)
    pilot_rows = [json.loads(line) for line in (output / "pilot_rows.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(pilot_rows) == 100
    assert {row["bridge32_state"] for row in pilot_rows} == {"READY"}
    assert {row["bridge32_availability"] for row in pilot_rows} == {"NOT_REQUIRED"}
    assert all("NO_FROZEN_ISSUE32_OVERLAP" not in row["reason_codes"] for row in pilot_rows)


def test_frozen_issue32_snapshot_is_bridged_without_staling_generation_changes(r3_fixture_root):
    root = _quarantine_fixture(r3_fixture_root)
    selected = select_pilot(root)["selected"][0]["canonical"]
    snapshot = root / "translation_quarantine" / "issue32_snapshot.jsonl"
    snapshot_record = {
        "canonical": selected,
        "identity": selected,
        "entity_scope": "entity",
        "snapshot_ref": f"fixture://issue32/{selected}",
        "content_identity": "fixture-v1",
        "frozen": True,
        "pinned": True,
        "immutable": True,
        "special_tag": "fixture",
        "support_class": "CORE_SUPPORT",
        "semantic_support_used": True,
        "generation_test_status": "NOT_TESTED",
    }
    snapshot_record["meaning_fingerprint"] = issue32_fingerprint(snapshot_record)
    snapshot.write_text(json.dumps(snapshot_record) + "\n", encoding="utf-8", newline="\n")
    output = root / "translation_quarantine" / "r3"
    run(root, output, issue32_path=snapshot)
    assert json.loads((output / "pilot_selection.json").read_text(encoding="utf-8"))["issue32_overlap_counts"]["selected"] == 1
    bridge_rows = [json.loads(line) for line in (output / "bridge32.jsonl").read_text(encoding="utf-8").splitlines()]
    assert bridge_rows[0]["canonical"] == selected
    assert bridge_rows[0]["bridge32_state"] == "READY"
    assert bridge_rows[0]["bridge32_availability"] == "AVAILABLE"
    assert bridge_rows[0]["snapshot_ref"].startswith("fixture://")
    assert bridge_rows[0]["content_identity"] == "fixture-v1"


def _write_bridge_snapshot(root: Path, canonical: str, **updates) -> tuple[Path, dict]:
    record = {
        "canonical": canonical,
        "identity": canonical,
        "entity_scope": "entity",
        "snapshot_ref": f"fixture://issue32/{canonical}",
        "content_identity": "fixture-content-v1",
        "frozen": True,
        "pinned": True,
        "immutable": True,
        "bridge32_verdict": "PASS",
        "count_cardinality": 1,
        "action_state": "state",
        "required_modifier": "required",
        **updates,
    }
    record["meaning_fingerprint"] = issue32_fingerprint(record)
    path = root / "translation_quarantine" / f"issue32-{canonical}.jsonl"
    path.write_text(json.dumps(record, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return path, record


def _run_bridge_case(root: Path, updates: dict) -> dict:
    selected = select_pilot(root)["selected"][0]["canonical"]
    updates = {key: value for key, value in updates.items() if key != "canonical"}
    snapshot, _ = _write_bridge_snapshot(root, selected, **updates)
    output = root / "translation_quarantine" / "r3"
    run(root, output, issue32_path=snapshot)
    rows = [json.loads(line) for line in (output / "pilot_rows.jsonl").read_text(encoding="utf-8").splitlines()]
    return next(row for row in rows if row["canonical"] == selected)


def test_required_overlap_without_snapshot_is_bridge_missing_and_not_semantic_review(r3_fixture_root):
    root = _quarantine_fixture(r3_fixture_root)
    selected = select_pilot(root)["selected"][0]["canonical"]
    evidence = root / "translation_quarantine" / "required.jsonl"
    evidence.write_text(json.dumps({
        "evidence_id": "required:" + selected,
        "canonical": selected,
        "source_type": "frozen_bridge_requirement",
        "source_ref": "fixture://required",
        "scope_note": "#32 overlap is required; snapshot intentionally absent",
        "content_identity": "requirement-v1",
        "evidence_role": "BRIDGE32_REQUIREMENT",
        "frozen": True,
    }) + "\n", encoding="utf-8", newline="\n")
    output = root / "translation_quarantine" / "r3"
    run(root, output, evidence_path=evidence)
    row = next(json.loads(line) for line in (output / "pilot_rows.jsonl").read_text(encoding="utf-8").splitlines() if json.loads(line)["canonical"] == selected)
    assert row["bridge32_availability"] == "BRIDGE_MISSING"
    assert row["bridge32_state"] == "REVIEW"
    assert row["display_state"] == "REVIEW"
    assert row["row_state"] == "REVIEW"
    assert "BRIDGE32_MISSING_REQUIRED_SNAPSHOT" in row["reason_codes"]


def test_required_snapshot_without_pinned_immutable_metadata_is_blocked_bridge(r3_fixture_root):
    root = _quarantine_fixture(r3_fixture_root)
    row = _run_bridge_case(root, {"pinned": False})
    assert row["bridge32_availability"] == "BLOCKED_BRIDGE"
    assert row["bridge32_state"] == "REVIEW"
    assert row["row_state"] == "REVIEW"


def test_snapshot_first_evaluation_is_available_but_not_ui_ja_self_certified(r3_fixture_root):
    root = _quarantine_fixture(r3_fixture_root)
    row = _run_bridge_case(root, {})
    assert row["bridge32_availability"] == "AVAILABLE"
    assert row["bridge32_state"] == "READY"
    assert row["display_state"] == "REVIEW"
    assert row["search_state"] == "REVIEW"
    assert row["row_state"] == "REVIEW"


def test_same_fingerprint_rerun_is_ready_and_generation_only_change_does_not_stale(r3_fixture_root):
    root = _quarantine_fixture(r3_fixture_root)
    selected = select_pilot(root)["selected"][0]["canonical"]
    base = {"canonical": selected, "identity": selected, "entity_scope": "entity", "count_cardinality": 1, "action_state": "state", "required_modifier": "required"}
    evaluated = issue32_fingerprint(base)
    row = _run_bridge_case(root, {"evaluated_issue32_meaning_fingerprint": evaluated, "generation_test_status": "PASS"})
    assert row["issue32_meaning_fingerprint"] == evaluated
    assert row["bridge32_state"] == "READY"


@pytest.mark.parametrize(
    ("field", "before", "after"),
    [
        ("count_cardinality", 1, 2),
        ("action_state", "action", "state"),
        ("required_modifier", "left", "right"),
    ],
)
def test_translation_visible_fingerprint_change_is_stale(r3_fixture_root, field, before, after):
    root = _quarantine_fixture(r3_fixture_root)
    selected = select_pilot(root)["selected"][0]["canonical"]
    prior = {"canonical": selected, "identity": selected, "entity_scope": "entity", "count_cardinality": 1, "action_state": "state", "required_modifier": "required"}
    prior[field] = before
    current = dict(prior)
    current[field] = after
    current["evaluated_issue32_meaning_fingerprint"] = issue32_fingerprint(prior)
    row = _run_bridge_case(root, current)
    assert row["bridge32_availability"] == "AVAILABLE"
    assert row["bridge32_state"] == "STALE_REVIEW"
    assert row["row_state"] == "STALE_REVIEW"


def test_explicit_independent_conflict_is_contradiction(r3_fixture_root):
    root = _quarantine_fixture(r3_fixture_root)
    row = _run_bridge_case(root, {"independent_semantic_conflict": True})
    assert row["bridge32_availability"] == "AVAILABLE"
    assert row["bridge32_state"] == "CONTRADICTION"
    assert row["row_state"] == "CONTRADICTION"
    assert "EXPLICIT_INDEPENDENT_SEMANTIC_CONFLICT" in row["reason_codes"]


def test_verifier_accepts_bridge_audit_artifact_with_available_snapshot(r3_fixture_root):
    root = _quarantine_fixture(r3_fixture_root)
    selected = select_pilot(root)["selected"][0]["canonical"]
    snapshot, _ = _write_bridge_snapshot(root, selected)
    output = root / "translation_quarantine" / "r3"
    run(root, output, issue32_path=snapshot)
    build(output)
    result = verify(root, output, rerun=True)
    assert result["ok"], result["errors"]
    bridge = next(json.loads(line) for line in (output / "bridge32.jsonl").read_text(encoding="utf-8").splitlines() if json.loads(line)["canonical"] == selected)
    assert bridge["bridge32_availability"] == "AVAILABLE"
    assert bridge["frozen"] is True and bridge["pinned"] is True and bridge["immutable"] is True


def test_output_boundary_is_fail_closed(r3_fixture_root):
    with pytest.raises(ValueError):
        ensure_r3_output(r3_fixture_root, r3_fixture_root / "outside")
