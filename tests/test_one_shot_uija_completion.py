from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "translation_quarantine" / "r3"))
import one_shot_uija_completion as campaign  # noqa: E402


def test_completed_556_are_reused_once_and_deduplicated():
    result = campaign.evaluate()
    assert len(result["completed"]) == 556
    assert len(result["final"]) == 30629
    assert len({row["canonical"] for row in result["final"]}) == 30629
    assert sum(row["route"] == "DEDUP_COMPLETED_556" for row in result["final"]) == 556


def test_priority_remainder_is_processed_in_full():
    result = campaign.evaluate()
    assert {priority: sum(row["priority_class"] == priority for row in result["final"]) for priority in ("P0", "P1", "P2")} == {"P0": 1025, "P1": 4910, "P2": 24694}
    assert {priority: sum(row["priority_class"] == priority for row in result["final"] if row["route"] != "DEDUP_COMPLETED_556") for priority in ("P0", "P1", "P2")} == {"P0": 469, "P1": 4910, "P2": 24694}


def test_known_wording_corrections_and_terminal_states():
    rows = {row["canonical"]: row for row in campaign.evaluate()["final"]}
    assert rows["finger_to_mouth"]["display_ja"] == "口に指"
    assert rows["pauldrons"]["display_ja"] == "肩当て"
    assert rows["simple_background"]["display_ja"] == "シンプルな背景"
    assert all(row["final_state"] in campaign.TERMINAL_STATES for row in rows.values())
    assert not any(row["final_state"] in {"REVIEW", "PENDING"} for row in rows.values())
    assert all(row["canonical_authoritative"] for row in rows.values())


def test_unresolved_strict_routes_fallback_and_replay_is_frozen():
    result = campaign.evaluate()
    assert any(row["route"] == "BOUNDED_STRICT_FALLBACK" for row in result["final"])
    assert all(row["canonical"] for row in result["fallback"])
    assert campaign._rows_hash(result["final"]) == campaign._rows_hash(campaign.evaluate()["final"])


def test_protected_inputs_do_not_change_during_evaluation():
    before = campaign._protected_snapshot()
    campaign.evaluate()
    assert before == campaign._protected_snapshot()


def test_output_artifacts_are_complete_if_campaign_has_run():
    output = ROOT / campaign.OUTPUT_DIR
    summary = json.loads((output / "run_summary.json").read_text(encoding="utf-8"))
    assert summary["measurable_universe"] == 30629
    assert summary["generic_review_pending"] == 0
    with (output / "final_translation_table.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 30629
    assert {row["final_state"] for row in rows} <= campaign.TERMINAL_STATES
