from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "translation_quarantine" / "r3"))
import forced_ja_display_completion as campaign  # noqa: E402


OUTPUT = ROOT / campaign.OUTPUT_DIR


def test_entire_residual_input_is_processed_and_adult_compounds_get_japanese():
    result = campaign._evaluate()
    assert len(result["residual_input"]) == 7752
    assert len(result["processed"]) == 7752
    assert result["processed"]["ass-to-mouth"]["display_ja"] == "尻から口への接触"
    assert result["processed"]["futanari_masturbation"]["final_state"] != "ENGLISH_FALLBACK_EXCEPTION"


def test_token_gap_uses_japanese_identity_wrapper_instead_of_fallback():
    result = campaign._evaluate()
    row = result["processed"]["aran_legwear"]
    assert row["final_state"] != "ENGLISH_FALLBACK_EXCEPTION"
    assert "タグ" in row["display_ja"]
    assert "aran legwear" in row["display_ja"]


def test_only_narrow_exception_classes_remain():
    result = campaign._evaluate()
    allowed = {"SYMBOL_OR_EMOTICON", "PROPER_NAME_OR_QUALIFIED_LABEL", "PRODUCT_OR_SERVICE_NAME", "CODE_OR_PRODUCT_IDENTIFIER", "OPAQUE_SOURCE_STRING"}
    assert all(row["reason"] in allowed for row in result["fallback"])
    assert not any(row["reason"] in {"ADULT_TERM", "COMPOUND_TAG", "INSUFFICIENT_EVIDENCE", "NO_SAFE_TRANSLATION", "STRICT_UNRESOLVED"} for row in result["fallback"])


def test_obvious_attribute_inversion_is_corrected_or_rejected():
    result = campaign._evaluate()
    assert result["processed"]["blue_blush"]["display_ja"] == "青い頬染め"
    assert result["processed"]["black_vs_white"]["display_ja"] == "黒対白"


def test_output_ledger_and_complete_table_are_count_checked():
    summary = json.loads((OUTPUT / "run_summary.json").read_text(encoding="utf-8"))
    ledger = [json.loads(line) for line in (OUTPUT / "fallback_exceptions.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    with (OUTPUT / "final_translation_table.csv").open(encoding="utf-8", newline="") as stream:
        table = list(csv.DictReader(stream))
    assert summary["residual_fallback_input"] == 7752
    assert summary["fallback_ledger_count"] == len(ledger) == summary["english_fallback"]
    assert len(table) == len({row["canonical"] for row in table}) == 30629
    assert summary["generic_review_pending"] == 0


def test_replay_and_protected_boundary_pass():
    replay = json.loads((OUTPUT / "replay_verification.json").read_text(encoding="utf-8"))
    protected = json.loads((OUTPUT / "protected_boundary.json").read_text(encoding="utf-8"))
    assert replay["verdict"] == "PASS"
    assert protected["verdict"] == "PASS"
    assert protected["production_modified"] is False
