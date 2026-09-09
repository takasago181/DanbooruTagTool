from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "translation_quarantine" / "r3"))
import bounded_wrapper_cleanup as cleanup  # noqa: E402


OUTPUT = ROOT / cleanup.OUTPUT_DIR


def test_required_wrapper_examples_are_meaningful_japanese():
    processed = cleanup._evaluate()["processed"]
    expected = {
        "kickstand": "キックスタンド",
        "legjob": "レッグジョブ",
        "dominator_(bdsm)": "支配する側（BDSM）",
        "implied_cheating_(relationship)": "浮気を示唆する関係",
        "alternate_ass_size_(larger)": "大きめの尻差分",
    }
    for canonical, label in expected.items():
        assert processed[canonical]["display_ja"] == label
        assert processed[canonical]["final_state"] != "ENGLISH_FALLBACK_EXCEPTION"


def test_audit_blocking_partial_english_labels_are_repaired_or_not_accepted():
    result = cleanup._evaluate()
    expected = {
        "heavy_chromatic_aberration": "強い色収差",
        "knees_together_feet_apart": "膝をつけて足を開く",
        "fictional_aircraft": "架空の航空機",
        "finger_counting_duo": "指で数える2人組",
        "father_and_son_threesome": "父親と息子を含む3人での性行為",
        "nipples_pressed_together": "乳首を押し付け合う",
        "no_genitals": "性器なし",
        "tank_gun": "戦車砲",
        "tears_of_joy_emoji": "嬉し涙の絵文字",
        "the_fool_(tarot)": "愚者（タロット）",
    }
    for canonical, label in expected.items():
        row = result["processed"][canonical]
        assert row["display_ja"] == label
        assert cleanup._meaningful(label, canonical)


def test_unknown_common_word_is_translated_and_company_identity_is_narrow_exception():
    result = cleanup._evaluate()["processed"]
    assert result["newt"]["display_ja"] == "イモリ"
    assert result["newt"]["final_state"] != "ENGLISH_FALLBACK_EXCEPTION"
    assert result["fender_musical_instruments_corporation"]["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"
    assert result["fender_musical_instruments_corporation"]["reason"] == "PRODUCT_OR_SERVICE_NAME"


def test_weapon_qualifier_does_not_use_publication_sense_for_magazine():
    row = cleanup._evaluate()["processed"]["no_magazine_(weapon)"]
    assert row["display_ja"] == "弾倉なし（武器）"
    assert row["final_state"] != "ENGLISH_FALLBACK_EXCEPTION"


def test_phrase_level_semantic_repairs_preserve_action_and_object_sense():
    result = cleanup._evaluate()["processed"]
    expected = {
        "painting_fingernails": "爪に色を塗る",
        "painting_toenails": "足の爪に色を塗る",
        "hydraulic_press": "油圧プレス",
        "press_conference": "記者会見",
        "taking_notes": "メモを取る",
        "hugging_ass": "尻を抱く",
        "opening_window": "窓を開ける",
        "riding_motorcycle": "オートバイに乗る",
        "two-handed_masturbation": "両手での自慰",
        "three-finger_salute": "3本指の敬礼",
        "two-page_spread": "見開き2ページ",
    }
    for canonical, label in expected.items():
        row = result[canonical]
        assert row["display_ja"] == label
        assert row["final_state"] != "ENGLISH_FALLBACK_EXCEPTION"
        assert cleanup._meaningful(label, canonical)


def test_accepted_bounded_labels_have_no_untranslated_semantic_base_token():
    result = cleanup._evaluate()
    allowed_reasons = {
        "CODE_OR_PRODUCT_IDENTIFIER",
        "OPAQUE_SOURCE_STRING",
        "PRODUCT_OR_SERVICE_NAME",
        "PROPER_NAME_OR_QUALIFIED_LABEL",
        "SYMBOL_OR_EMOTICON",
    }
    for row in result["processed"].values():
        if row["final_state"] != "ENGLISH_FALLBACK_EXCEPTION":
            assert cleanup._meaningful(row["display_ja"], row["canonical"])
        else:
            assert row["reason"] in allowed_reasons


def test_qualified_identity_is_not_translated_away():
    merged = {row["canonical"]: row for row in cleanup._evaluate()["merged"]}
    assert merged["hu_tao_(genshin_impact)_(cosplay)"]["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"
    assert merged["vogue_(magazine)"]["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"
    assert merged["mig-29"]["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"


def test_all_bounded_targets_are_terminal_and_wrapper_free():
    result = cleanup._evaluate()
    assert len(result["targets"]) == 2434
    assert len(result["processed"]) == 2434
    for row in result["processed"].values():
        assert row["final_state"] in {"JA_ACCEPT_MACHINE", "JA_ACCEPT_STRICT", "ENGLISH_FALLBACK_EXCEPTION"}
        assert not (row["final_state"] != "ENGLISH_FALLBACK_EXCEPTION" and row["display_ja"].startswith("タグ「"))


def test_complete_table_and_fallback_ledger_are_counted():
    result = cleanup._evaluate()
    assert len(result["merged"]) == len({row["canonical"] for row in result["merged"]}) == 30629
    assert len(result["exceptions"]) == len([row for row in result["merged"] if row["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"])


def test_no_generic_review_or_pending_reasons():
    result = cleanup._evaluate()
    assert not any(row["reason"] in {"REVIEW", "PENDING", "STRICT_UNRESOLVED", "INSUFFICIENT_EVIDENCE"} for row in result["merged"])


def test_replay_and_protected_boundary_pass():
    replay = json.loads((OUTPUT / "replay_verification.json").read_text(encoding="utf-8"))
    protected = json.loads((OUTPUT / "protected_boundary.json").read_text(encoding="utf-8"))
    assert replay["verdict"] == "PASS"
    assert protected["verdict"] == "PASS"
    assert protected["production_modified"] is False


def test_artifacts_match_summary():
    summary = json.loads((OUTPUT / "run_summary.json").read_text(encoding="utf-8"))
    ledger = (OUTPUT / "bounded_target_ledger.jsonl").read_text(encoding="utf-8").splitlines()
    fallback = (OUTPUT / "fallback_exceptions.jsonl").read_text(encoding="utf-8").splitlines()
    with (OUTPUT / "final_translation_table.csv").open(encoding="utf-8", newline="") as stream:
        table = list(csv.DictReader(stream))
    assert len(ledger) == summary["bounded_target_count"] == 2434
    assert len(fallback) == summary["fallback_ledger_count"]
    assert len(table) == summary["final_table_rows"] == 30629
