from pathlib import Path

import pytest

from translation_quarantine.r3.r3_bulk_run import check_masked_rows
from translation_quarantine.r3.r3_bulk_select import CANARY_SEED, select_canary, select_records
from translation_quarantine.r3.r3_common import stable_key


ROOT = Path(__file__).resolve().parents[1]


def test_canary_selection_is_200_unseen_and_seeded():
    queue = [{"canonical": f"canary_{index:03d}", "priority": "P0", "lanes": "general"} for index in range(240)]
    selected = select_records(queue, {f"canary_{index:03d}" for index in range(20)})
    assert len(selected) == 200
    assert len({row["canonical"] for row in selected}) == 200
    assert all(row["selection_key"] == stable_key(CANARY_SEED, row["canonical"]) for row in selected)


def test_canary_preflight_rejects_protected_queue_drift():
    with pytest.raises(ValueError, match="queue hash"):
        select_canary(ROOT)


def test_masked_audit_leakage_checker_is_fail_closed():
    masked_rows = [{"canonical": "sample", "candidate_display": ""}]
    key = {"selected": [{"canonical": "sample", "audit_key": "secret"}]}
    result = check_masked_rows(masked_rows, key)
    assert result["ok"] is True
    assert check_masked_rows([{"canonical": "sample", "row_state": "READY"}], key)["ok"] is False
