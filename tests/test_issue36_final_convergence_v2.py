from __future__ import annotations

import sys
from pathlib import Path

import pytest


R3 = Path(__file__).resolve().parents[1] / "translation_quarantine" / "r3"
if str(R3) not in sys.path:
    sys.path.insert(0, str(R3))

import issue36_final_convergence_v2 as v2


@pytest.fixture(scope="module")
def result():
    return v2.evaluate()


def _row(result, canonical):
    return next(row for row in result["final"] if row["canonical"] == canonical)


def test_full_queue_and_partition(result):
    assert len(result["work_queue"]) == 30629
    assert len({item["canonical"] for item in result["work_queue"]}) == 30629
    assert len(result["final"]) == 30629
    assert [item["canonical"] for item in result["work_queue"]] == [row["canonical"] for row in result["final"]]


def test_resolver_verifier_are_separate_and_cover_all_rows(result):
    assert len(result["resolver_results"]) == 30629
    assert len(result["verifier_results"]) == 30629
    assert all(item["semantic_facets"] for item in result["resolver_results"])
    assert all(item["verdict"] in {"PASS", "FALLBACK_REQUIRED"} for item in result["verifier_results"])
    assert all(row["final_state"] in v2.ACCEPTED_STATES | {"ENGLISH_FALLBACK_EXCEPTION"} for row in result["final"])


def test_pattern_level_semantic_risk_is_not_fixture_only(result):
    for canonical in ("bdsm", "building_snowman", "building_sand_sculpture", "break_action", "shooting_star_(symbol)", "shot_glass", "shredded_muscles", "simple_background"):
        row = _row(result, canonical)
        assert row["final_state"] in v2.ACCEPTED_STATES | {"ENGLISH_FALLBACK_EXCEPTION"}
    assert _row(result, "bdsm")["display_ja"] == "BDSM"
    assert _row(result, "building_snowman")["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"
    assert _row(result, "building_sand_sculpture")["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"
    assert _row(result, "break_action")["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"
    assert _row(result, "shooting_star_(symbol)")["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"


def test_phrase_homework_has_individual_attempts(result):
    assert len(result["phrase_results"]) == 1677
    assert all(item["evidence_refs"] for item in result["phrase_results"])
    assert all(item["unresolved_reason"] or item["decision"] in {"RESOLVED_JA", "TRUE_EXCEPTION"} for item in result["phrase_results"])
    assert result["phrase_outcomes"]["RESOLVED_JA"] == 21
    assert result["phrase_outcomes"]["EVIDENCE_UNRESOLVED_FALLBACK"] == 1656


def test_prior_repairs_and_qualified_controls(result):
    expected = {
        "painting_fingernails": "爪に色を塗る",
        "painting_toenails": "足の爪に色を塗る",
        "hydraulic_press": "油圧プレス",
        "press_conference": "記者会見",
        "taking_notes": "メモを取る",
        "no_magazine_(weapon)": "弾倉なし（武器）",
        "newt": "イモリ",
        "human_(warcraft)": "人間（Warcraft）",
        "hydro_symbol_(genshin_impact)": "水元素のシンボル（Genshin Impact）",
        "advanced_ship_(eve_online)": "先進型艦船（EVE Online）",
    }
    for canonical, label in expected.items():
        row = _row(result, canonical)
        assert row["display_ja"] == label
        assert row["search_ja"] == label
        assert row["final_state"] in v2.ACCEPTED_STATES


def test_historical_language_and_malformed_controls(result):
    for canonical in (":p", "^_^", "anal_object_insertion", "imminent_anal", "presenting_own_anus", "presenting_own_ass", "presenting_own_pussy", "vibrator_bulge", "vibrator_cord", "vibrator_in_anus", "vibrator_on_clitoris", "vibrator_on_nipple", "vibrator_on_penis", "presenting_own_foot", "a_(phrase)", "imminent_penetration", "android"):
        row = _row(result, canonical)
        assert row["final_state"] in v2.ACCEPTED_STATES | {"ENGLISH_FALLBACK_EXCEPTION"}
        if row["final_state"] == "ENGLISH_FALLBACK_EXCEPTION":
            assert row["display_ja"] == ""
        else:
            assert row["display_ja"] and not v2._language_flags(canonical, row["display_ja"])


def test_collision_and_adversarial_results_pass(result):
    assert len(result["collision_review"]) >= sum(row["final_state"] in v2.ACCEPTED_STATES for row in result["final"])
    assert all(item["verdict"] == "PASS" for item in result["collision_review"])
    assert len(result["adversarial"]) >= 400
    assert all(item["verifier_verdict"] == "PASS" for item in result["adversarial"])


def test_all_gates_are_pass(result):
    assert len(result["gates"]) == 16
    assert all(gate["status"] == "PASS" for gate in result["gates"])


def test_emitted_gate_status_is_terminal():
    gate_path = Path(v2.ROOT) / v2.OUTPUT_DIR / "gate_status.json"
    assert gate_path.exists()
    data = gate_path.read_text(encoding="utf-8")
    assert '"all_pass": true' in data
    assert "FINAL_READY_FOR_INDEPENDENT_AUDIT" in data
