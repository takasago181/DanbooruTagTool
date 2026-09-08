from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "translation_quarantine" / "r3"))
import exception_classifier_repair as repair  # noqa: E402


OUTPUT = ROOT / repair.OUTPUT_DIR


def test_all_1768_residuals_are_reclassified():
    result = repair._evaluate()
    assert len(result["residual"]) == 1768
    assert len(result["processed"]) == 1768
    assert all(row["final_state"] in repair.TERMINAL_STATES for row in result["processed"].values())


def test_ordinary_words_are_recovered_from_opaque_bucket():
    result = repair._evaluate()["processed"]
    expected = {"rectum": "直腸", "rug": "ラグ", "twerking": "トゥワーク", "february": "2月", "euphemism": "婉曲表現", "exorcism": "悪魔祓い", "flatbread": "平焼きパン", "floatplane": "水上機", "footrest": "足置き", "motorhome": "キャンピングカー", "monolids": "一重まぶた", "sternum": "胸骨", "suburb": "郊外", "sunroof": "サンルーフ", "taskbar": "タスクバー", "technology": "技術"}
    for canonical, label in expected.items():
        assert result[canonical]["display_ja"] == label
        assert result[canonical]["final_state"] != "ENGLISH_FALLBACK_EXCEPTION"


def test_ordinary_parenthetical_qualifiers_are_not_proper_fallbacks():
    result = repair._evaluate()["processed"]
    assert result["1980s_(style)"]["display_ja"] == "1980年代風"
    assert result["ace_(playing_card)"]["display_ja"] == "エース（トランプ）"
    assert result["breathing_(animated)"]["display_ja"] == "呼吸アニメーション"
    assert result["study_(room)"]["display_ja"] == "書斎"
    assert result["stop_(gesture)"]["display_ja"] == "ストップのジェスチャー"


def test_true_exception_reasons_are_specific_and_narrow():
    result = repair._evaluate()
    allowed = {"SYMBOL_OR_EMOTICON", "PROPER_NAME_OR_QUALIFIED_LABEL", "PRODUCT_OR_SERVICE_NAME", "CODE_OR_PRODUCT_IDENTIFIER", "OPAQUE_SOURCE_STRING"}
    assert all(row["reason"] in allowed for row in result["exceptions"])
    assert not any(row["reason"] in {"STRICT_UNRESOLVED", "INSUFFICIENT_EVIDENCE", "NO_SAFE_TRANSLATION", "ADULT_TERM", "COMPOUND_TAG"} for row in result["exceptions"])


def test_complete_merged_table_and_ledger_match_summary():
    summary = json.loads((OUTPUT / "run_summary.json").read_text(encoding="utf-8"))
    ledger = [json.loads(line) for line in (OUTPUT / "fallback_exceptions.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    with (OUTPUT / "final_translation_table.csv").open(encoding="utf-8", newline="") as stream:
        table = list(csv.DictReader(stream))
    assert len(table) == len({row["canonical"] for row in table}) == 30629
    assert summary["input_residual_fallback"] == 1768
    assert summary["fallback_ledger_count"] == len(ledger) == summary["residual_english_fallback"]
    assert summary["generic_review_pending"] == 0


def test_replay_and_protected_boundary_pass():
    replay = json.loads((OUTPUT / "replay_verification.json").read_text(encoding="utf-8"))
    protected = json.loads((OUTPUT / "protected_boundary.json").read_text(encoding="utf-8"))
    assert replay["verdict"] == "PASS"
    assert protected["verdict"] == "PASS"
    assert protected["production_modified"] is False
