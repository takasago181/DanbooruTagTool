import json
from pathlib import Path

import pytest

from translation_quarantine.r3.r3_issue41_bridge_status import inspect_bridge_status


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def test_bridge_status_guard_blocks_unresolved_and_missing_status(tmp_path: Path):
    requirements = tmp_path / "requirements.jsonl"
    snapshot = tmp_path / "snapshot.jsonl"
    _write_jsonl(
        requirements,
        [{"canonical": "anal"}, {"canonical": "bound"}, {"canonical": "holding_weapon"}],
    )
    _write_jsonl(
        snapshot,
        [
            {"canonical": "anal", "meaning_relevant_status": "RESOLVED"},
            {"canonical": "bound", "meaning_relevant_status": "UNRESOLVED"},
            {"canonical": "holding_weapon"},
        ],
    )

    result = inspect_bridge_status(snapshot, requirements)
    assert result["state"] == "HOLD_BRIDGE"
    assert result["resolved_count"] == 1
    assert result["unresolved_count"] == 1
    assert result["status_missing_count"] == 1
    assert result["blocked_canonicals"] == ["bound", "holding_weapon"]


def test_bridge_status_guard_all_explicit_resolved_is_ready(tmp_path: Path):
    requirements = tmp_path / "requirements.jsonl"
    snapshot = tmp_path / "snapshot.jsonl"
    _write_jsonl(requirements, [{"canonical": "anal"}, {"canonical": "group_sex"}])
    _write_jsonl(
        snapshot,
        [
            {"canonical": "anal", "meaning_relevant_status": "RESOLVED"},
            {"canonical": "group_sex", "meaning_relevant_status": "RESOLVED"},
        ],
    )
    assert inspect_bridge_status(snapshot, requirements)["state"] == "READY"


def test_bridge_status_guard_rejects_unknown_status(tmp_path: Path):
    requirements = tmp_path / "requirements.jsonl"
    snapshot = tmp_path / "snapshot.jsonl"
    _write_jsonl(requirements, [{"canonical": "anal"}])
    _write_jsonl(snapshot, [{"canonical": "anal", "meaning_relevant_status": "PASS"}])
    with pytest.raises(ValueError, match="unknown meaning_relevant_status"):
        inspect_bridge_status(snapshot, requirements)
