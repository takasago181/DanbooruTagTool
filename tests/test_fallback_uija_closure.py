from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "translation_quarantine" / "r3"))
import fallback_uija_closure as campaign  # noqa: E402


OUTPUT = ROOT / campaign.OUTPUT_DIR


def test_transparent_fallback_becomes_glanceable_japanese():
    result = campaign._evaluate()
    rows = result["processed"]
    assert rows["black_liquid"]["display_ja"] == "黒い液体"
    assert rows["gold_ring"]["display_ja"] == "金色の指輪"
    assert rows["black_liquid"]["final_state"] == "JA_ACCEPT_MACHINE"


def test_risky_relation_does_not_bypass_strict_route():
    result = campaign._evaluate()
    row = result["processed"]["ass-to-mouth"]
    assert row["route"] == "BOUNDED_STRICT_FALLBACK"
    assert row["final_state"] == "ENGLISH_FALLBACK_EXCEPTION"
    assert any(item["canonical"] == "ass-to-mouth" for item in result["residual"])


def test_obvious_attribute_inversion_is_rejected():
    accepted, reason = campaign._light_audit("black_liquid", "白い液体")
    assert accepted is False
    assert reason == "OBVIOUS_ATTRIBUTE_INVERSION"


def test_canonical_authority_and_terminal_states_are_preserved():
    result = campaign._evaluate()
    assert len(result["merged"]) == 30629
    assert len({row["canonical"] for row in result["merged"]}) == 30629
    assert all(row["canonical_authoritative"] for row in result["merged"])
    assert all(row["final_state"] in campaign.TERMINAL_STATES | {"JA_ACCEPT_EXISTING"} for row in result["merged"])
    assert not any(row["final_state"] in campaign.GENERIC_STATES for row in result["merged"])


def test_fallback_ledger_is_real_and_count_checked():
    summary = json.loads((OUTPUT / "run_summary.json").read_text(encoding="utf-8"))
    ledger = OUTPUT / "fallback_exceptions.jsonl"
    rows = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert ledger.exists()
    assert summary["fallback_ledger"] == "translation_quarantine/fallback_uija_closure_20260909/fallback_exceptions.jsonl"
    assert summary["fallback_ledger_count"] == len(rows) == summary["english_fallback"]
    assert all(row["terminal_state"] == "ENGLISH_FALLBACK_EXCEPTION" for row in rows)


def test_complete_output_table_and_boundary_evidence():
    summary = json.loads((OUTPUT / "run_summary.json").read_text(encoding="utf-8"))
    with (OUTPUT / "final_translation_table.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    protected = json.loads((OUTPUT / "protected_boundary.json").read_text(encoding="utf-8"))
    replay = json.loads((OUTPUT / "replay_verification.json").read_text(encoding="utf-8"))
    assert len(rows) == len({row["canonical"] for row in rows}) == 30629
    assert summary["input_fallback_count"] == 8048
    assert summary["generic_review_pending"] == 0
    assert protected["verdict"] == "PASS"
    assert protected["production_modified"] is False
    assert replay["verdict"] == "PASS"
