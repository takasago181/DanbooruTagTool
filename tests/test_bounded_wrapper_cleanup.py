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
