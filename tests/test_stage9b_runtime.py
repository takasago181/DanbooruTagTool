"""Focused Stage9B runtime lane integration tests."""
from pathlib import Path

import pytest

from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.prompt_composer import ComposerProfile, NegativeRule, PromptComposer
from danbooru_tag_tool.recommendations import RecommendationCandidate
from danbooru_tag_tool.stage8a_semantics import DecoratedRecommendationCandidate
from danbooru_tag_tool.stage8b_support import SupportKnowledgeStore
from danbooru_tag_tool.stage9b_runtime import (
    SelectionDecision, Stage9BRuntime, Stage9BSelectionState,
    cooccurrence_candidate, semantic_auxiliary_candidate,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def composer():
    knowledge = TagKnowledgeCore.load(ROOT)
    store = SupportKnowledgeStore.load(ROOT, knowledge, knowledge.load_generation_profile_store(ROOT))
    return PromptComposer(knowledge, store)


@pytest.fixture(scope="module")
def runtime(composer):
    return Stage9BRuntime(composer)


def recommendation(canonical="solo", *, co_count=2, base_count=3):
    return RecommendationCandidate(canonical, "other", base_count, co_count, co_count / base_count,
                                   100, 0.01, 10.0, 0.2, 9.0)


def semantic(canonical="solo", role="BODY_PART"):
    return semantic_auxiliary_candidate(DecoratedRecommendationCandidate(
        recommendation(canonical), role, "分類", ("FLAG",), "BODY_TARGET", "理由",
        ("CORE_BASIS",), ("根拠",),
    ))


def warning_codes(result):
    return {item.code for item in result.warnings}


def test_semantic_lane_arrives_with_approved_reason_and_evidence(runtime):
    item = semantic("solo")
    result = runtime.compose(("311",), semantic_auxiliary=(item,))
    atom = next(atom for atom in result.plan.candidate_atoms if atom.atom_id == "input:semantic_aux:solo")
    assert atom.source_lanes == ("SEMANTIC_AUX",)
    assert atom.reason == "semantic/search auxiliary from approved role: BODY_PART"
    assert ("semantic_role", "BODY_PART") in atom.evidence
    assert not atom.selected


def test_cooccurrence_is_default_off_and_include_renders(runtime):
    item = cooccurrence_candidate(recommendation("solo"), snapshot_id="snapshot-1")
    initial = runtime.compose(("311",), cooccurrence=(item,))
    assert "solo" not in initial.provenance_map
    selected = runtime.compose(("311",), cooccurrence=(item,), selection_state=Stage9BSelectionState((
        SelectionDecision(item.candidate_id, "INCLUDE", "user selected statistic"),
    )))
    assert "solo" in selected.provenance_map
    assert selected.provenance_map["solo"].reason == "user selected statistic"


def test_include_exclude_persist_across_recompose_and_rank_order(runtime):
    first = cooccurrence_candidate(recommendation("solo"), candidate_id="co:solo")
    second = cooccurrence_candidate(recommendation("anus"), candidate_id="co:anus")
    state = Stage9BSelectionState((SelectionDecision("co:anus", "INCLUDE"),
                                   SelectionDecision("co:solo", "EXCLUDE")))
    forward = runtime.compose(("311",), cooccurrence=(first, second), selection_state=state)
    reverse = runtime.compose(("311",), cooccurrence=(second, first), selection_state=state)
    assert "anus" in forward.provenance_map and "solo" not in forward.provenance_map
    assert "anus" in reverse.provenance_map and "solo" not in reverse.provenance_map
    assert state.with_decision(SelectionDecision("co:anus", "EXCLUDE")).decision_for("co:anus").state == "EXCLUDE"


def test_same_canonical_multi_lane_merge_keeps_all_evidence_and_provenance(runtime):
    semantic_item = semantic("solo")
    stats = recommendation("solo", co_count=7, base_count=11)
    co_item = cooccurrence_candidate(stats, snapshot_id="snapshot-raw")
    state = Stage9BSelectionState((SelectionDecision(semantic_item.candidate_id, "INCLUDE"),
                                   SelectionDecision(co_item.candidate_id, "INCLUDE")))
    result = runtime.compose(("311",), semantic_auxiliary=(semantic_item,), cooccurrence=(co_item,),
                             selection_state=state)
    merged = result.provenance_map["solo"]
    assert merged.source_lanes == ("SEMANTIC_AUX", "COOCCURRENCE")
    assert "stage8a_semantics" in merged.provenance
    assert "stage6_true_and_cooccurrence" in merged.provenance
    assert ("co_count", 7) in merged.evidence
    assert ("base_count", 11) in merged.evidence
    assert ("snapshot_id", "snapshot-raw") in merged.evidence
    assert result.positive_prompt.split(", ").count("solo") == 1


def test_special_identity_survives_lane_exclusion(runtime, composer):
    item = cooccurrence_candidate(recommendation("solo"))
    result = runtime.compose(("311",), cooccurrence=(item,), selection_state=Stage9BSelectionState((
        SelectionDecision(item.candidate_id, "EXCLUDE"),
    )))
    baseline = composer.compose(("311",))
    assert result.plan.selected_special_ids == ("311",)
    assert result.positive_prompt == baseline.positive_prompt


def test_role_mapping_uses_approved_metadata_not_tag_text(runtime):
    item = semantic("solo", role="UNCLASSIFIED")
    assert item.block == "GENERAL_AUX"
    assert "role" not in item.canonical


def test_deterministic_and_no_score_mixing(runtime):
    semantic_item = semantic("solo")
    co_item = cooccurrence_candidate(recommendation("anus", co_count=5, base_count=8))
    state = Stage9BSelectionState((SelectionDecision(semantic_item.candidate_id, "INCLUDE"),
                                   SelectionDecision(co_item.candidate_id, "INCLUDE")))
    first = runtime.compose(("311",), semantic_auxiliary=(semantic_item,), cooccurrence=(co_item,), selection_state=state)
    second = runtime.compose(("311",), semantic_auxiliary=(semantic_item,), cooccurrence=(co_item,), selection_state=state)
    assert first == second
    atom = first.provenance_map["anus"]
    assert ("conditional_rate", 5 / 8) in atom.evidence
    assert ("raw_lift", 10.0) in atom.evidence
    source = (ROOT / "danbooru_tag_tool" / "stage9b_runtime.py").read_text(encoding="utf-8")
    assert "combined_score" not in source and "score(" not in source


def test_stage9a_negative_and_model_scope_are_preserved(runtime):
    item = semantic("solo")
    state = Stage9BSelectionState((SelectionDecision(item.candidate_id, "INCLUDE"),))
    result = runtime.compose(("311",), semantic_auxiliary=(item,), selection_state=state, negative_prompt="solo")
    assert "POSITIVE_NEGATIVE_EXACT" in warning_codes(result)
    rule = NegativeRule("anima_only", "ANIMA", profile_id="anima")
    wrong_profile = ComposerProfile("wai", "WAI_ILLUSTRIOUS", negative_rule_set=(rule,))
    scoped = runtime.compose(("311",), profile=wrong_profile, model_family="WAI_ILLUSTRIOUS",
                             negative_prompt="nsfw", adult_intent=True)
    assert "RULE_SCOPE_MISMATCH" in warning_codes(scoped)
    assert "ADULT_NEGATIVE_CONFLICT" not in warning_codes(scoped)


def test_no_network_or_llm_dependency(monkeypatch, runtime):
    def forbidden(*args, **kwargs):
        raise AssertionError("network forbidden")
    monkeypatch.setattr("socket.socket", forbidden)
    assert runtime.compose(("311",)).positive_prompt
    source = (ROOT / "danbooru_tag_tool" / "stage9b_runtime.py").read_text(encoding="utf-8")
    assert not any(name in source for name in ("requests", "openai", "urllib", "httpx"))
