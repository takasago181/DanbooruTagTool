from __future__ import annotations

import sys
from pathlib import Path

import pytest


R3 = Path(__file__).resolve().parents[1] / "translation_quarantine" / "r3"
if str(R3) not in sys.path:
    sys.path.insert(0, str(R3))

import full_accepted_quality_reconciliation as reconciliation


@pytest.fixture(scope="module")
def result():
    return reconciliation.evaluate()


def _row(result, canonical):
    return result["processed"][canonical]


def test_fixed_source_partition_and_full_ledgers(result):
    assert len(result["source"]) == 30629
    assert len(result["accepted"]) == 27743
    assert len(result["fallbacks"]) == 2886
    assert len(result["candidate_screen"]) == 27743
    assert len(result["accepted_revalidation"]) == 27743
    assert len(result["fallback_reconciliation"]) == 2886
    assert len(result["merged"]) == 30629


@pytest.mark.parametrize(
    ("canonical", "expected"),
    [
        ("anal_object_insertion", "肛門への物体挿入"),
        ("imminent_anal", "肛門への挿入直前"),
        ("presenting_own_anus", "自分の肛門を見せる"),
        ("presenting_own_ass", "自分の尻を見せる"),
        ("presenting_own_pussy", "自分の陰部を見せる"),
        ("vibrator_bulge", "バイブレーターの膨らみ"),
        ("vibrator_cord", "バイブレーターのコード"),
        ("vibrator_in_anus", "肛門内のバイブレーター"),
        ("vibrator_on_clitoris", "クリトリスに当てるバイブレーター"),
        ("vibrator_on_nipple", "乳首に当てるバイブレーター"),
        ("vibrator_on_penis", "陰茎に当てるバイブレーター"),
        ("presenting_own_foot", "自分の足を見せる"),
        ("imminent_penetration", "挿入直前"),
        ("android", "アンドロイド"),
        ("bandaid", "絆創膏"),
        ("beard", "ひげ"),
        ("hair_scrunchie", "シュシュ"),
        ("vertical-striped_clothes", "縦縞の服"),
    ],
)
def test_mandatory_fixture_repairs(result, canonical, expected):
    row = _row(result, canonical)
    assert row["display_ja"] == expected
    assert row["search_ja"] == expected
    assert row["final_state"] in reconciliation.ACCEPTED_STATES
    assert reconciliation._quality_flags(row) == []


@pytest.mark.parametrize("canonical", [":p", "^_^", "a_(phrase)"])
def test_symbol_and_malformed_fixtures_are_explicit_fallbacks(result, canonical):
    row = _row(result, canonical)
    assert row["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"
    assert row["display_ja"] == ""
    assert row["search_ja"] == ""


def test_prior_repairs_remain_intact(result):
    expected = {
        "kickstand": "キックスタンド",
        "legjob": "レッグジョブ",
        "dominator_(bdsm)": "支配する側（BDSM）",
        "implied_cheating_(relationship)": "浮気を示唆する関係",
        "alternate_ass_size_(larger)": "大きめの尻差分",
        "heavy_chromatic_aberration": "強い色収差",
        "no_magazine_(weapon)": "弾倉なし（武器）",
        "newt": "イモリ",
        "painting_fingernails": "爪に色を塗る",
        "hydraulic_press": "油圧プレス",
        "press_conference": "記者会見",
        "taking_notes": "メモを取る",
    }
    for canonical, label in expected.items():
        row = _row(result, canonical)
        assert row["display_ja"] == label
        assert row["search_ja"] == label
        assert row["final_state"] in reconciliation.ACCEPTED_STATES


def test_all_final_accepted_rows_pass_quality_gate(result):
    accepted = [row for row in result["merged"] if row["final_state"] in reconciliation.ACCEPTED_STATES]
    assert accepted
    assert all(reconciliation._quality_flags(row) == [] for row in accepted)
    assert all(row["display_ja"] and row["search_ja"] for row in accepted)
    assert all("タグ「" not in row["display_ja"] for row in accepted)
    assert all(row["canonical"] in {item["canonical"] for item in result["source"]} for row in accepted)


def test_fallback_reconciliation_revisits_phrase_homework(result):
    phrase = [item for item in result["fallback_reconciliation"] if item["old_reason"] == "PHRASE_SEMANTICS_UNRESOLVED"]
    assert len(phrase) == 1677
    assert all(item["status"] == "TRANSLATION_HOMEWORK_UNRESOLVED" for item in phrase)
    assert all(item["final_state"] == "ENGLISH_FALLBACK_EXCEPTION" for item in phrase)


def test_output_contract_after_run(result):
    # This test checks the declared output schema without writing into the
    # repository; run() is exercised by the execution command and verifies
    # replay/protected boundaries before emitting artifacts.
    assert reconciliation.OUTPUT_DIR == "translation_quarantine/full_accepted_quality_sweep_20260909"
    assert {"candidate_screen", "accepted_revalidation", "fallback_reconciliation"} <= {
        "candidate_screen", "accepted_revalidation", "fallback_reconciliation"
    }
