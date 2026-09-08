import json
from pathlib import Path

from translation_quarantine.r3.r3_bulk_batches import BATCH_SIZE, _make_batches, _ordered_records, _unsafe_ready


def test_remaining_batches_are_deterministic_and_last_batch_is_remainder():
    queue = [{"canonical": f"tag_{index:03d}", "priority": "P0"} for index in range(625)]
    first = _ordered_records(queue, set())
    second = _ordered_records(queue, set())
    assert [row["canonical"] for row in first] == [row["canonical"] for row in second]
    assert [len(batch) for batch in _make_batches(first)] == [200, 200, 200, 25]
    assert BATCH_SIZE == 200


def test_unsafe_ready_guard_is_fail_closed():
    rows = [{"canonical": "adult_action", "row_state": "READY", "display_state": "READY", "risk_class": "CRITICAL", "semantic_evidence_ids": [], "reason_codes": []}]
    search = [{"canonical": "adult_action", "term_state": "ACCEPTED"}]
    bridge = [{"canonical": "adult_action", "bridge32_state": "READY", "bridge32_availability": "NOT_REQUIRED"}]
    assert _unsafe_ready(rows, search, bridge) == ["adult_action:high_risk_without_scope"]
