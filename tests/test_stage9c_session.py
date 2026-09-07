from pathlib import Path
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import Mock
import pytest

from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.stage7a_warnings import Stage7AWarningPresenter
from danbooru_tag_tool.stage8a_semantics import DecoratedRecommendationCandidate
from danbooru_tag_tool.stage8b_support import SupportKnowledgeStore
from danbooru_tag_tool.recommendations import RecommendationCandidate
from danbooru_tag_tool.stage9c_session import ComposerVariant, Stage9ComposerSession, WeightVariant
from danbooru_tag_tool.prompt_composer import ComposerProfile, ComposerInput
from danbooru_tag_tool.ui import Stage7AApp
from danbooru_tag_tool.stage7b_recommendations import RecommendationResult

ROOT = Path(__file__).resolve().parents[1]


def make_session():
    knowledge = TagKnowledgeCore.load(ROOT)
    profiles = knowledge.load_generation_profile_store(ROOT)
    support = SupportKnowledgeStore.load(ROOT, knowledge, profiles)
    return Stage9ComposerSession(knowledge, Stage7AWarningPresenter(knowledge, profiles), support)


def decorated(canonical="solo", role="UNCLASSIFIED"):
    candidate = RecommendationCandidate(canonical, "other", 11, 7, 7 / 11, 100, .01, 10., .2, 9.)
    return DecoratedRecommendationCandidate(candidate, role, None, (), None, None, (), ())


def test_local_session_composes_core_and_manual_auxiliary():
    session = make_session()
    session.add_special("311")
    session.add_auxiliary("solo")
    assert "riding machine" in session.prompt_preview
    assert "solo" in session.prompt_preview
    assert session.clipboard_text == session.prompt_preview
    assert session.provenance_map["solo"].source_lanes == ("USER_EXPLICIT",)


def test_review_lanes_are_default_off_and_selection_persists():
    session = make_session()
    session.add_special("311")
    session.set_discovered_candidates((decorated(),), snapshot_id="snapshot-1")
    assert "solo" not in session.provenance_map
    session.include_cooccurrence("solo")
    assert "solo" in session.provenance_map
    session.set_discovered_candidates((decorated(),), snapshot_id="snapshot-1")
    assert session.selection_state.decision_for("cooccurrence:solo").state == "INCLUDE"
    assert ("snapshot_id", "snapshot-1") in session.provenance_map["solo"].evidence


def test_stage9d_variant_is_reversible_and_does_not_decide_a_winner():
    session = make_session()
    session.add_special("311")
    baseline = session.prompt_preview
    variant = ComposerVariant("special_last", ComposerProfile(special_slot_position=9), (("purpose", "A/B"),))
    session.set_variant(variant)
    assert session.active_variant == variant
    assert session.prompt_preview.endswith("riding machine")
    session.set_variant(ComposerVariant("baseline", ComposerProfile()))
    assert session.prompt_preview == baseline


@pytest.mark.parametrize("common,rare", [
    (("solo",), ("blush",)), (("solo",), ()), ((), ("blush",)), ((), ()),
    (("solo",), ("solo",)),
])
def test_ui_receives_both_buckets_atomically_and_adds_from_either(common, rare):
    session = make_session()
    session.add_special("1")
    core = session.statistics_core_canonicals()
    result = RecommendationResult(
        1, core, 11, tuple(decorated(c).candidate for c in common),
        tuple(decorated(c).candidate for c in rare),
    )
    app = SimpleNamespace(
        session=session, active_recommendation_request=1,
        stage8a_semantics=SimpleNamespace(
            decorate_many=lambda candidates, **kw: tuple(decorated(c.canonical) for c in candidates)),
        recommendation_box=Mock(), recommendation_status=Mock(),
        common_recommendations=Mock(), rare_recommendations=Mock(),
        _refresh_state=Mock(), _clear_recommendation_rows=Mock(),
        statistics_snapshot_id="test-snapshot",
    )
    def render(frame, candidates, **kw):
        # Even while the first tab is rendered, both sets must already exist.
        assert all(session.has_cooccurrence(c.canonical)
                   for c in (*app.recommendation_result.common, *app.recommendation_result.rare))
    app._render_candidate_rows = render
    app._show_recommendation_result = lambda r: Stage7AApp._show_recommendation_result(app, r)
    app._show_recommendation_result(result)
    for canonical in dict.fromkeys((*common, *rare)):
        Stage7AApp._add_recommended(app, canonical)
        assert canonical.replace("_", " ") in session.provenance_map
        assert session.selection_state.decision_for("cooccurrence:" + canonical).state == "INCLUDE"
    app._show_recommendation_result(replace(result, common=(), rare=()))
    assert not any(session.has_cooccurrence(c) for c in (*common, *rare))


def test_semantic_only_add_does_not_require_cooccurrence():
    session = make_session()
    session.add_special("311")
    app = SimpleNamespace(session=session, _refresh_state=Mock(),
                          _show_recommendation_result=Mock(), recommendation_result=None)
    Stage7AApp._add_recommended(app, "solo")
    assert "solo" in session.provenance_map


def test_core_change_clears_candidates_but_not_stable_decisions():
    session = make_session()
    session.add_special("311")
    session.set_candidate_buckets((decorated(),), ())
    session.include_cooccurrence("solo")
    session.add_special("1")
    assert not session.has_cooccurrence("solo")
    assert session.selection_state.decision_for("cooccurrence:solo").state == "INCLUDE"


def test_remove_included_candidate_excludes_its_lane():
    session = make_session()
    session.add_special("311")
    session.set_candidate_buckets((decorated(),), ())
    session.add_auxiliary("solo")
    session.include_cooccurrence("solo")
    session.remove_auxiliary("solo")
    assert "solo" not in session.provenance_map


@pytest.mark.parametrize("count", [0, 1, 2])
def test_broad_generic_knob_changes_actual_prompt_and_restores(count):
    session = make_session()
    session.add_special("311")
    original = session.comparison_snapshot()
    supports = tuple(ComposerInput("broad:" + c, canonical=c) for c in ("solo", "blush"))
    session.set_variant(ComposerVariant("broad", ComposerProfile(),
                                       broad_generic_support=supports, broad_generic_count=count))
    assert len(session.compose_result.plan.selected_atoms) == 1 + count
    session.set_variant(original[0])
    assert session.compose_result == original[1]


def test_all_six_knobs_are_reversible_and_capture_actual_prompt():
    session = make_session()
    session.add_special("311")
    session.add_auxiliary("blush")
    original = session.comparison_snapshot()
    variant = ComposerVariant(
        "explicit-comparison", ComposerProfile("noob-test", "NOOBAI", special_slot_position=9),
        (("frontend", "test"), ("runtime", "local")),
        broad_generic_support=(ComposerInput("broad:solo", canonical="solo"),),
        broad_generic_count=1,
        role_density_variant="explicit-pose-set",
        role_density_inputs=(ComposerInput("density:sitting", canonical="sitting",
                                          block="POSE_COMPOSITION"),),
        weight_variant=(WeightVariant("sitting", 1.25, "(sitting:1.25)"),),
        lora_inputs=(ComposerInput("lora:fixture", text="<lora:fixture:0.8>", block="LORA"),),
        lora_contraction_variant="explicit-style-removal",
        lora_contraction_excluded_input_ids=("manual:blush",),
    )
    session.set_variant(variant)
    chosen, result = session.comparison_snapshot()
    assert chosen == variant
    assert result.positive_prompt == "(sitting:1.25), solo, <lora:fixture:0.8>, riding machine"
    assert result.provenance_map["(sitting:1.25)"].weight == 1.25
    assert session.manual_auxiliary_canonicals == ("blush",)
    assert session.clipboard_text == result.positive_prompt
    session.set_variant(original[0])
    assert session.comparison_snapshot() == original
    session.set_variant(variant)
    assert session.compose_result == result


def test_lora_alone_never_contracts_and_density_has_no_implicit_limit():
    session = make_session()
    session.add_special("311")
    session.add_auxiliary("blush")
    session.set_variant(ComposerVariant(
        "lora-only", ComposerProfile(),
        lora_inputs=(ComposerInput("lora", text="<lora:x:1>", block="LORA"),)))
    assert "blush" in session.provenance_map
    assert "riding machine" in session.provenance_map


@pytest.mark.parametrize("family", ["NOOBAI", "WAI_ILLUSTRIOUS", "ILLUSTRIOUS", "ANIMA"])
def test_weight_grammar_is_explicit_and_profile_scoped(family):
    session = make_session()
    session.add_auxiliary("solo")
    variant = ComposerVariant("weights", ComposerProfile("test-" + family, family),
                              weight_variant=(WeightVariant("solo", 1.2, family + ":solo"),))
    session.set_variant(variant)
    assert session.prompt_preview == family + ":solo"
    assert session.compose_result.plan.profile.model_family == family


def test_invalid_variants_fail_without_caching_partial_result():
    with pytest.raises(ValueError):
        ComposerVariant("bad", ComposerProfile(), broad_generic_count=2)
    with pytest.raises(ValueError):
        ComposerVariant("bad", ComposerProfile(),
                        weight_variant=(WeightVariant("solo", 1.2, "weighted"),))
    session = make_session()
    session.set_variant(ComposerVariant("missing", ComposerProfile("test", "ANIMA"),
                                       weight_variant=(WeightVariant("solo", 1.2, "weighted"),)))
    for _ in range(2):
        with pytest.raises(ValueError):
            session.compose_result
