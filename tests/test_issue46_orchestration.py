from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.issue36.orchestrator import (
    ADVERSARIAL_SAMPLE_STRATA,
    CONTRACT_COMMIT,
    MAX_REPAIR_CYCLES,
    RESIDUAL_SAMPLE_STRATA,
    SOURCE_BLOB,
    Orchestrator,
    assert_no_blind_leakage,
    collision_review_rows,
    freeze_stratified_sample,
    load_source,
    pilot_queue,
    read_json,
    source_queue_row,
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
    assert MAX_REPAIR_CYCLES == 2


def test_full_sampling_freezes_required_v31_strata() -> None:
    rows, _ = load_source(REPO)
    queue = [source_queue_row(row, index) for index, row in enumerate(rows)]
    residual, residual_details = freeze_stratified_sample(
        queue, RESIDUAL_SAMPLE_STRATA, "residual_fallback", 300
    )
    adversarial, adversarial_details = freeze_stratified_sample(
        queue, ADVERSARIAL_SAMPLE_STRATA, "adversarial", 600
    )
    assert len(residual) == 300
    assert len(adversarial) == 600
    assert {entry["name"] for entry in residual_details} == {name for name, _ in RESIDUAL_SAMPLE_STRATA}
    assert {entry["name"] for entry in adversarial_details} == {name for name, _ in ADVERSARIAL_SAMPLE_STRATA}
    assert all(entry["selected_count"] >= min(target, entry["candidate_count"]) for entry, (_, target) in zip(residual_details, RESIDUAL_SAMPLE_STRATA))
    assert all(entry["selected_count"] >= min(target, entry["candidate_count"]) for entry, (_, target) in zip(adversarial_details, ADVERSARIAL_SAMPLE_STRATA))


def test_collision_review_contains_external_challenge_results() -> None:
    merged = [
        {"canonical": "alpha", "final_display_ja": "同じ表示"},
        {"canonical": "beta", "final_display_ja": "同じ表示"},
    ]
    challenge = [
        {"canonical": "alpha", "display_challenge": "CONFIRM", "search_challenge": "CONFIRM", "rationale_ja": "a", "root_cause": ""},
        {"canonical": "beta", "display_challenge": "REPAIR_REQUIRED", "search_challenge": "REMOVE_SEARCH", "rationale_ja": "b", "root_cause": "collision"},
    ]
    artifact = collision_review_rows(merged, challenge)
    assert len(artifact) == 1
    assert artifact[0]["review_artifact_origin"] == "external_codex_final_response"
    assert artifact[0]["canonicals"] == ["alpha", "beta"]
    assert {row["canonical"] for row in artifact[0]["external_challenge_reviews"]} == {"alpha", "beta"}


def test_two_repair_cycles_rechallenge_and_no_third_cycle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    root = tmp_path / "repair-bound"
    orchestrator = Orchestrator(REPO, "pilot", root, "codex")
    orchestrator.manifest = {
        "schema_version": 1,
        "mode": "pilot",
        "contract_commit": CONTRACT_COMMIT,
        "source_git_blob": SOURCE_BLOB,
        "invocations": [],
    }
    queue = [{
        "canonical": "alpha",
        "source_state": "FALLBACK",
        "source_display_ja": "",
        "source_search_ja": "",
        "priority_class": "P1",
        "source_reason": "PHRASE_SEMANTICS_UNRESOLVED",
        "source_risk_class": "HIGH",
    }]
    repair_seed = [{
        "canonical": "alpha",
        "candidate_display_ja": "候補",
        "candidate_search_ja": "候補",
        "source_state": "FALLBACK",
        "source_display_ja": "",
        "source_search_ja": "",
        "priority_class": "P1",
        "source_reason": "PHRASE_SEMANTICS_UNRESOLVED",
        "source_risk_class": "HIGH",
        "challenge_verdict": {"display_challenge": "REPAIR_REQUIRED", "search_challenge": "REPAIR_REQUIRED"},
    }]
    monkeypatch.setattr(orchestrator, "build_repairs", lambda queue, resolver, challenge: repair_seed)
    calls: list[tuple[str, str]] = []

    def fake_run_agent(role: str, batch_id: str, input_rows: list[dict[str, object]], input_path: Path) -> list[dict[str, object]]:
        calls.append((role, batch_id))
        if role == "REPAIR":
            return [{
                "canonical": "alpha",
                "final_display_ja": "候補",
                "final_search_ja": "候補",
                "decision": "REPAIR_JA",
                "display_verdict": "ACCEPT",
                "search_verdict": "ACCEPT",
                "review_mode": "CODEX_AGENT_SEMANTIC_REVIEW",
                "batch_id": batch_id,
            }]
        return [{
            "canonical": "alpha",
            "display_challenge": "REPAIR_REQUIRED",
            "search_challenge": "REPAIR_REQUIRED",
        }]

    monkeypatch.setattr(orchestrator, "run_agent", fake_run_agent)
    repair_one = orchestrator.run_repairs(queue, [], [{"canonical": "alpha"}], cycle=1)
    challenge_one = orchestrator.run_rechallenge(queue, repair_one, cycle=1)
    repair_two = orchestrator.run_repairs(queue, repair_one, challenge_one, cycle=2)
    challenge_two = orchestrator.run_rechallenge(queue, repair_two, cycle=2)
    assert repair_one and challenge_one and repair_two and challenge_two
    with pytest.raises(RuntimeError, match="cycle bound exceeded"):
        orchestrator.run_repairs(queue, repair_two, challenge_two, cycle=3)
    with pytest.raises(RuntimeError, match="cycle bound exceeded"):
        orchestrator.run_rechallenge(queue, repair_two, cycle=3)
    manifest = read_json(root / "repair_manifest.json")
    assert [entry["cycle"] for entry in manifest["cycles"]] == [1, 2]
    assert manifest["completed_cycles"] == 2
    assert manifest["third_cycle_attempted"] is False
    assert [batch_id for role, batch_id in calls if role == "REPAIR"] == [
        "repair_cycle_1_0001", "repair_cycle_2_0001"
    ]
