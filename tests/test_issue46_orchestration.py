from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools.issue36.orchestrator import (
    ADVERSARIAL_SAMPLE_STRATA,
    CONTRACT_COMMIT,
    MAX_REPAIR_CYCLES,
    SOURCE_BLOB,
    Orchestrator,
    assert_no_blind_leakage,
    collision_review_rows,
    load_source,
    mandatory_challenge_population,
    outcome_sample_candidates,
    pilot_queue,
    read_json,
    select_outcome_strata,
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


def test_sampling_uses_post_outcome_populations_not_source_proxies() -> None:
    rows, _ = load_source(REPO)
    queue = [source_queue_row(row, index) for index, row in enumerate(rows)]
    by_canonical = {row["canonical"]: row for row in queue}
    final_rows = []
    for canonical in ("1girl", "shot_glass", "!", "building_snowman"):
        row = by_canonical[canonical]
        final_rows.append(
            {
                "canonical": canonical,
                "decision": "KEEP_JA" if canonical == "1girl" else (
                    "REPAIR_JA" if canonical == "shot_glass" else (
                        "TRUE_EXCEPTION" if canonical == "!" else "EVIDENCE_UNRESOLVED"
                    )
                ),
                "final_display_ja": "既存表示" if canonical == "1girl" else (
                    "修復表示" if canonical == "shot_glass" else ""
                ),
                "final_search_ja": "既存表示" if canonical == "1girl" else "",
                "display_verdict": "ACCEPT" if canonical in {"1girl", "shot_glass"} else "ABSENT",
                "search_verdict": "ACCEPT" if canonical in {"1girl", "shot_glass"} else "ABSENT",
                "risk_class": "LOW",
            }
        )
    candidates = outcome_sample_candidates([by_canonical[row["canonical"]] for row in final_rows], final_rows)
    assert {row["canonical"] for row in candidates["random_accepted"]} == {"1girl", "shot_glass"}
    assert {row["canonical"] for row in candidates["repaired_or_new_translation_candidate"]} == {"shot_glass"}
    assert {row["canonical"] for row in candidates["true_exception"]} == {"!"}
    assert {row["canonical"] for row in candidates["ordinary_residual_fallback"]} == {"building_snowman"}
    assert "shot_glass" not in {row["canonical"] for row in candidates["ordinary_residual_fallback"]}


def test_stage0_freezes_seed_only_before_outcomes(tmp_path: Path) -> None:
    rows, _ = load_source(REPO)
    queue = pilot_queue({row["canonical"]: row for row in rows})
    orchestrator = Orchestrator(REPO, "pilot", tmp_path / "seed", "codex")
    orchestrator.root.mkdir(parents=True, exist_ok=True)
    orchestrator.materialize_sample_seed(queue)
    seed = read_json(orchestrator.root / "sample_plan.json")
    assert seed["selection_phase"] == "outcome_pending"
    assert seed["selection_population_identity"] == "external_final_decisions_required"
    assert seed["residual_fallback_sample"] == []
    assert seed["adversarial_sample"] == []
    assert "historical_blocker_candidates" not in seed


def test_additional_residual_excludes_mandatory_but_adversarial_does_not() -> None:
    queue = [
        {"canonical": "demoted_alpha", "source_state": "ACCEPTED", "source_reason": "WHOLE_LABEL_SCREENED_NO_BLOCKER", "source_risk_class": "LOW"},
        {"canonical": "alpha_neighbor", "source_state": "FALLBACK", "source_reason": "RAW_ENGLISH_SEMANTIC_CORE", "source_risk_class": "LOW"},
        {"canonical": "phrase_mandatory", "source_state": "FALLBACK", "source_reason": "PHRASE_SEMANTICS_UNRESOLVED", "source_risk_class": "LOW"},
        {"canonical": "phrase_legacy", "source_state": "FALLBACK", "source_reason": "PHRASE_SEMANTICS_UNRESOLVED", "source_risk_class": "LOW"},
        {"canonical": "ordinary_legacy", "source_state": "FALLBACK", "source_reason": "RAW_ENGLISH_SEMANTIC_CORE", "source_risk_class": "LOW"},
    ]
    final_rows = [
        {"canonical": "demoted_alpha", "decision": "EVIDENCE_UNRESOLVED", "final_display_ja": "", "display_verdict": "UNRESOLVED", "risk_class": "LOW"},
        {"canonical": "alpha_neighbor", "decision": "KEEP_JA", "final_display_ja": "", "display_verdict": "ABSENT", "risk_class": "LOW"},
        {"canonical": "phrase_mandatory", "decision": "EVIDENCE_UNRESOLVED", "final_display_ja": "", "display_verdict": "UNRESOLVED", "risk_class": "LOW"},
        {"canonical": "phrase_legacy", "decision": "KEEP_JA", "final_display_ja": "", "display_verdict": "ABSENT", "risk_class": "LOW"},
        {"canonical": "ordinary_legacy", "decision": "KEEP_JA", "final_display_ja": "", "display_verdict": "ABSENT", "risk_class": "LOW"},
    ]
    challenge = [{"canonical": "demoted_alpha", "root_cause": ""}, {"canonical": "phrase_mandatory", "root_cause": ""}]
    mandatory, artifact = mandatory_challenge_population(queue, final_rows, challenge)
    assert {row["canonical"] for row in artifact} == mandatory
    assert {"demoted_alpha", "phrase_mandatory"}.issubset(mandatory)

    additional = outcome_sample_candidates(queue, final_rows, mandatory)
    sibling_canonicals = {row["canonical"] for row in additional["accepted_demotion_root_cause_sibling"]}
    assert "demoted_alpha" not in sibling_canonicals
    assert "alpha_neighbor" in sibling_canonicals
    assert "demoted_alpha" not in {row["canonical"] for row in additional["ordinary_residual_fallback"]}
    assert "phrase_mandatory" not in {row["canonical"] for row in additional["prior_phrase_unresolved_residual"]}
    adversarial = outcome_sample_candidates(queue, final_rows)
    assert "demoted_alpha" in {row["canonical"] for row in adversarial["ordinary_residual_fallback"]}
    adversarial_entries, _ = select_outcome_strata(
        queue, final_rows, ADVERSARIAL_SAMPLE_STRATA, "adversarial", 1
    )
    assert "demoted_alpha" in {row["canonical"] for row in adversarial_entries}


def test_full_validator_receives_merged_rows_without_undefined_reference(tmp_path: Path) -> None:
    root = tmp_path / "full-validator"
    orchestrator = Orchestrator(REPO, "full", root, "codex")
    orchestrator.manifest = {"invocations": []}
    orchestrator.source_manifest = {
        "source_git_blob": SOURCE_BLOB,
        "source_counts": {"rows": 30_629, "accepted": 23_194},
    }
    queue = [{"canonical": "alpha", "source_state": "ACCEPTED"}]
    orchestrator.rows = [{"canonical": "alpha"}]
    resolver = [{"canonical": "alpha"}]
    challenge = [{"canonical": "alpha"}]
    merged = [{
        "canonical": "alpha",
        "decision": "KEEP_JA",
        "final_display_ja": "表示",
        "display_verdict": "ACCEPT",
    }]
    root.mkdir(parents=True, exist_ok=True)
    write_jsonl(root / "inputs" / "challenge_inputs.jsonl", [{"canonical": "alpha"}])
    write_jsonl(root / "collision_review.jsonl", [])
    write_jsonl(root / "mandatory_challenge_population.jsonl", [])
    (root / "sample_plan.json").write_text(json.dumps({
        "created_before_semantic_outcomes": True,
        "selection_phase": "outcomes_frozen",
        "selection_created_after_semantic_outcomes": True,
        "selection_population_identity": "external_final_decisions",
        "residual_fallback_sample": [],
        "adversarial_sample": [],
        "residual_fallback_strata": [],
        "adversarial_strata": [],
        "historical_blockers": [],
    }), encoding="utf-8")
    (root / "repair_manifest.json").write_text(json.dumps({"max_cycles": MAX_REPAIR_CYCLES}), encoding="utf-8")
    (root / "replay_verification.json").write_text(json.dumps({"pass": False}), encoding="utf-8")
    (root / "protected_boundary.json").write_text(json.dumps({"production_modified_no": True}), encoding="utf-8")
    result = orchestrator.deterministic_validate(
        queue, resolver, challenge, [], [], [], [], merged
    )
    assert result["mode"] == "full"
    assert result["terminal"] in {
        "BLOCKED_STRUCTURAL_DEFECT",
        "HOLD_COVERAGE_COLLAPSE",
        "FINAL_READY_FOR_INDEPENDENT_AUDIT",
    }


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
