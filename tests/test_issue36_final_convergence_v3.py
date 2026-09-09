from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

R3 = Path(__file__).resolve().parents[1] / "translation_quarantine" / "r3"
if str(R3) not in sys.path:
    sys.path.insert(0, str(R3))

import issue36_final_convergence_v3 as v3


@pytest.fixture(scope="module")
def result():
    return v3.run()


def test_source_identity_and_queue(result):
    assert result["source_blob"] == v3.SOURCE_BLOB
    assert result["rows"] == 30629
    assert result["first_pass_reviewed"] + result["trusted_exact"] == 30629


def test_frozen_agent_records_are_complete(result):
    root = v3.ROOT / v3.OUTPUT_REL
    decisions = [json.loads(line) for line in (root / "merged_agent_decisions.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(decisions) == 30629
    assert all(row["review_mode"] == "CODEX_AGENT_SEMANTIC_REVIEW" for row in decisions)
    assert all(row["evidence_refs"] or row["decision"] == "EVIDENCE_UNRESOLVED" for row in decisions)


def test_blinded_inputs_do_not_leak_first_pass_state(result):
    root = v3.ROOT / v3.OUTPUT_REL / "challenge_inputs"
    rows = [json.loads(line) for path in sorted(root.glob("batch-*.jsonl")) for line in path.read_text(encoding="utf-8").splitlines()]
    forbidden = {"decision", "decision_rationale_ja", "provisional_lane", "resolver_confidence", "first_pass_verdict"}
    assert rows
    assert all(not forbidden.intersection(row) for row in rows)


def test_phrase_population_is_actually_reviewed(result):
    assert result["phrase_1677"]["TRANSLATE_JA"] + result["phrase_1677"]["EVIDENCE_UNRESOLVED"] == 1677
    assert result["phrase_1677"]["TRANSLATE_JA"] > 0


def test_known_semantic_repairs_and_historical_rows(result):
    rows = {row["canonical"]: row for row in json.loads("[" + ",".join((v3.ROOT / v3.OUTPUT_REL / "final_rows.jsonl").read_text(encoding="utf-8").splitlines()) + "]")}
    expected = {"bdsm": "BDSM", "presenting_own_foot": "自分の足を見せる", "android": "アンドロイド", "imminent_penetration": "挿入直前", "multiple_penetration": "複数箇所への挿入", "building_snowman": "雪だるまを作る", "building_sand_sculpture": "砂の彫刻を作る", "break_action": "中折れ式銃", "shot_glass": "ショットグラス", "shredded_muscles": "鍛え上げられた筋肉", "simple_background": "シンプルな背景"}
    for canonical, label in expected.items():
        assert rows[canonical]["display_ja"] == label


def test_no_invalid_convenience_fallback_and_coverage(result):
    rows = [json.loads(line) for line in (v3.ROOT / v3.OUTPUT_REL / "final_rows.jsonl").read_text(encoding="utf-8").splitlines()]
    assert all("NO_EXACT_MAP" not in row["reason"] and "MULTIWORD" not in row["reason"] and "NO_STATIC_TEMPLATE" not in row["reason"] for row in rows)
    assert result["coverage"]["final_accepted"] >= int(23194 * 0.8)


def test_challenge_and_adversarial_populations(result):
    assert result["mandatory_challenge"] > 0
    assert result["residual_challenge"] >= 300
    assert result["adversarial_records"] >= 600


def test_gate_status_is_success_terminal(result):
    gate = json.loads((v3.ROOT / v3.OUTPUT_REL / "gate_status.json").read_text(encoding="utf-8"))
    assert gate["all_pass"] is True
    assert len(gate["gates"]) == 23
    assert all(item["status"] == "PASS" for item in gate["gates"])
    assert gate["terminal"] == "FINAL_READY_FOR_INDEPENDENT_AUDIT"
