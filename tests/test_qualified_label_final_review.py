from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "translation_quarantine" / "r3"))
import qualified_label_final_review as review  # noqa: E402


OUTPUT = ROOT / review.OUTPUT_DIR


def test_required_qualified_concepts_are_translated():
    result = review._evaluate()["processed"]
    assert result["human_(warcraft)"]["display_ja"] == "人間（Warcraft）"
    assert result["hydro_symbol_(genshin_impact)"]["display_ja"] == "水元素のシンボル（Genshin Impact）"
    assert result["advanced_ship_(eve_online)"]["display_ja"] == "先進型艦船（EVE Online）"
    assert all(result[key]["final_state"] != "ENGLISH_FALLBACK_EXCEPTION" for key in ("human_(warcraft)", "hydro_symbol_(genshin_impact)", "advanced_ship_(eve_online)"))


def test_true_character_and_cosplay_identity_remains_original():
    result = review._evaluate()["processed"]
    for canonical in ("hu_tao_(genshin_impact)_(cosplay)", "jeanne_d'arc_alter_(fate)_(cosplay)", "cynthia_(pokemon)_(cosplay)"):
        assert result[canonical]["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"
        assert result[canonical]["reason"] == "PROPER_NAME_OR_QUALIFIED_LABEL"


def test_named_artifact_and_identifier_fallbacks_remain_narrow():
    result = review._evaluate()["processed"]
    assert result["balmung_(fate)"]["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"
    assert result["vogue_(magazine)"]["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"
    assert result["iphone"]["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"
    assert result["mig-29"]["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"


def test_all_876_inputs_are_terminal_and_no_generic_review_exists():
    result = review._evaluate()
    assert len(result["residual"]) == 876
    assert len(result["processed"]) == 876
    assert all(row["final_state"] in {"JA_ACCEPT_MACHINE", "JA_ACCEPT_STRICT", "ENGLISH_FALLBACK_EXCEPTION"} for row in result["processed"].values())
    assert not any(row["reason"] in {"REVIEW", "PENDING", "STRICT_UNRESOLVED", "INSUFFICIENT_EVIDENCE"} for row in result["processed"].values())


def test_qualified_review_output_is_complete_and_ledger_matches():
    summary = json.loads((OUTPUT / "run_summary.json").read_text(encoding="utf-8"))
    ledger = [json.loads(line) for line in (OUTPUT / "fallback_exceptions.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    with (OUTPUT / "final_translation_table.csv").open(encoding="utf-8", newline="") as stream:
        table = list(csv.DictReader(stream))
    assert len(table) == len({row["canonical"] for row in table}) == 30629
    assert summary["qualified_rows_reviewed"] == 731
    assert summary["fallback_ledger_count"] == len(ledger) == summary["residual_english_fallback"]
    assert summary["generic_review_pending"] == 0


def test_replay_and_protected_boundary_pass():
    replay = json.loads((OUTPUT / "replay_verification.json").read_text(encoding="utf-8"))
    protected = json.loads((OUTPUT / "protected_boundary.json").read_text(encoding="utf-8"))
    assert replay["verdict"] == "PASS"
    assert protected["verdict"] == "PASS"
    assert protected["production_modified"] is False


def test_outputs_are_quarantine_only():
    assert review.OUTPUT_DIR.startswith("translation_quarantine/")
    assert "production" not in review.OUTPUT_DIR
