from pathlib import Path

import pytest

from translation_quarantine.r3.r3_bulk_run import check_masked_rows
from translation_quarantine.r3.r3_bulk_select import CANARY_SEED, portable_csv_text_hash, select_canary, select_records
from translation_quarantine.r3.r3_common import stable_key


ROOT = Path(__file__).resolve().parents[1]


def test_canary_selection_is_200_unseen_and_seeded():
    queue = [{"canonical": f"canary_{index:03d}", "priority": "P0", "lanes": "general"} for index in range(240)]
    selected = select_records(queue, {f"canary_{index:03d}" for index in range(20)})
    assert len(selected) == 200
    assert len({row["canonical"] for row in selected}) == 200
    assert all(row["selection_key"] == stable_key(CANARY_SEED, row["canonical"]) for row in selected)


def test_canary_preflight_uses_portable_identity_for_frozen_git_sources():
    selection = select_canary(ROOT)
    assert selection["canary_size"] == 200
    assert selection["source_identity"]["missing_candidates.csv"]["current_git_blob"] == selection["source_identity"]["missing_candidates.csv"]["validated_git_blob"]
    assert selection["source_queue_portable_content_identity"]


def test_portable_source_identity_ignores_newlines_but_detects_field_change():
    lf = "canonical,priority\nfoo,P0\nbar,P1\n"
    crlf = lf.replace("\n", "\r\n")
    changed = "canonical,priority\nfoo,P0\nbar,P0\n"
    assert portable_csv_text_hash(lf) == portable_csv_text_hash(crlf)
    assert portable_csv_text_hash(lf) != portable_csv_text_hash(changed)


def test_masked_audit_leakage_checker_is_fail_closed():
    masked_rows = [{"canonical": "sample", "candidate_display": ""}]
    key = {"selected": [{"canonical": "sample", "audit_key": "secret"}]}
    result = check_masked_rows(masked_rows, key)
    assert result["ok"] is True
    assert check_masked_rows([{"canonical": "sample", "row_state": "READY"}], key)["ok"] is False
