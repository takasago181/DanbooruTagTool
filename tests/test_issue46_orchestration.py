from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.issue36.orchestrator import (
    CONTRACT_COMMIT,
    SOURCE_BLOB,
    Orchestrator,
    assert_no_blind_leakage,
    load_source,
    pilot_queue,
    strict_agent_schema,
    write_jsonl,
)


REPO = Path(__file__).resolve().parents[1]


def test_immutable_source_gate_and_mixed_pilot_fixture() -> None:
    rows, manifest = load_source(REPO)
    assert manifest["contract_commit"] == CONTRACT_COMMIT
    assert manifest["source_git_blob"] == SOURCE_BLOB
    assert manifest["source_counts"] == {
        "rows": 30_629,
        "unique_canonicals": 30_629,
        "accepted": 23_194,
        "fallback": 7_435,
        "phrase_homework": 1_677,
    }
    queue = pilot_queue({row["canonical"]: row for row in rows})
    assert {row["pilot_case"] for row in queue} == {
        "valid_japanese_candidate",
        "semantic_mismatch",
        "translatable_fallback",
        "true_exception",
        "display_valid_search_too_broad",
        "historical_polysemy_multiword",
    }


def test_blinded_input_rejects_resolver_fields() -> None:
    with pytest.raises(ValueError, match="resolver fields"):
        assert_no_blind_leakage({"canonical": "x", "decision": "KEEP_JA"})


def test_role_schemas_are_strict_and_role_specific() -> None:
    resolver = strict_agent_schema("RESOLVER")
    challenger = strict_agent_schema("CHALLENGER")
    assert resolver["properties"]["records"]["items"]["additionalProperties"] is False
    assert challenger["properties"]["records"]["items"]["additionalProperties"] is False
    assert "decision" in resolver["properties"]["records"]["items"]["required"]
    assert "decision" not in challenger["properties"]["records"]["items"]["required"]


def test_failed_child_is_fail_closed_and_manifest_is_resumable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import tools.issue36.orchestrator as module

    root = tmp_path / "run"
    orchestrator = Orchestrator(REPO, "pilot", root, "codex")
    orchestrator.manifest = {
        "schema_version": 1,
        "mode": "pilot",
        "contract_commit": CONTRACT_COMMIT,
        "source_git_blob": SOURCE_BLOB,
        "invocations": [],
    }
    input_path = root / "input.jsonl"
    write_jsonl(input_path, [{"canonical": "x"}])

    class FailedChild:
        pid = 12345
        returncode = 17

        def communicate(self, prompt: str) -> tuple[str, str]:
            return '{"type":"thread.started","thread_id":"fresh-failed-thread"}\n', "forced failure"

    monkeypatch.setattr(module.subprocess, "Popen", lambda *args, **kwargs: FailedChild())
    with pytest.raises(RuntimeError, match="failed closed"):
        orchestrator.run_agent("CHALLENGER", "failure_0001", [{"canonical": "x"}], input_path)
    manifest = json.loads((root / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["invocations"][0]["status"] == "FAILED"
    assert manifest["invocations"][0]["invocation_id"] == "fresh-failed-thread"
    assert manifest["invocations"][0]["child_process_id"] == 12345


def test_repair_bound_is_two() -> None:
    # The executable contract constant is intentionally checked without creating a child run.
    from tools.issue36.orchestrator import MAX_REPAIR_CYCLES

    assert MAX_REPAIR_CYCLES == 2
