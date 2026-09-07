from pathlib import Path

from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.stage7a_warnings import Stage7AWarningPresenter
from danbooru_tag_tool.stage8a_semantics import DecoratedRecommendationCandidate
from danbooru_tag_tool.stage8b_support import SupportKnowledgeStore
from danbooru_tag_tool.recommendations import RecommendationCandidate
from danbooru_tag_tool.stage9c_session import ComposerVariant, Stage9ComposerSession
from danbooru_tag_tool.prompt_composer import ComposerProfile

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
