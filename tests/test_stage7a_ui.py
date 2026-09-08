from collections import defaultdict
from dataclasses import replace
import hashlib
import inspect
from pathlib import Path

import pytest

from danbooru_tag_tool.generation_profile import GenerationProfileStore
from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.search import TagSearchEngine
from danbooru_tag_tool.stage7a_presenter import SpecialSearchPresenter
from danbooru_tag_tool.stage7a_session import Stage7ASession
from danbooru_tag_tool.stage7a_warnings import Stage7AWarningPresenter
from danbooru_tag_tool.ui import (
    Stage7AApp,
    bilingual_tag_label,
    create_window,
    set_general_results_visible,
    wire_vertical_scrollbar,
)


ROOT = Path(__file__).resolve().parents[1]


def test_bilingual_tag_label_uses_explicit_japanese_fallback():
    assert bilingual_tag_label("日本語", "sample_tag") == "日本語 / sample_tag"
    assert bilingual_tag_label("", "sample_tag") == "日本語未登録 / sample_tag"
    assert bilingual_tag_label(None, "sample_tag") == "日本語未登録 / sample_tag"
    assert bilingual_tag_label("   ", "sample_tag") == "日本語未登録 / sample_tag"
    assert bilingual_tag_label("  日本語  ", "sample_tag") == "日本語 / sample_tag"


def test_issue35_ui_uses_bilingual_identity_and_japanese_first_chrome():
    source = inspect.getsource(Stage7AApp)
    assert "bilingual_tag_label(item.japanese, item.original_term)" in source
    assert "bilingual_tag_label(item.display_japanese, item.canonical)" in source
    assert "bilingual_tag_label(display, candidate.canonical)" in source
    assert "owner = bilingual_tag_label(special.japanese, special.term)" in source
    assert "[選択Special] {bilingual_tag_label(special.japanese, special.term)}" in source
    assert "[手動追加] {bilingual_tag_label(display, canonical)}" in source
    assert "text=\"Specialタグ候補\"" in source
    assert "text=\"選択したSpecialタグ\"" in source
    assert "text=\"完成Prompt\"" in source
    assert "text=\"完成Promptをコピー\"" in source
    assert 'root.title("DanbooruTagTool")' in inspect.getsource(create_window)


def test_candidate_rows_render_evidence_before_raw_statistics():
    source = inspect.getsource(Stage7AApp._render_candidate_rows)
    assert source.index("decorated.generation_hint_ja") < source.index(
        "self._candidate_statistics(decorated, bucket)"
    )


@pytest.fixture(scope="module")
def knowledge():
    return TagKnowledgeCore.load(ROOT)


@pytest.fixture(scope="module")
def profile_store(knowledge):
    return knowledge.load_generation_profile_store(ROOT)


@pytest.fixture(scope="module")
def presenter(knowledge, profile_store):
    return SpecialSearchPresenter(knowledge, TagSearchEngine(knowledge), profile_store)


def session(knowledge, profile_store):
    return Stage7ASession(knowledge, Stage7AWarningPresenter(knowledge, profile_store))


def test_both_result_listboxes_have_vertical_scrollbars():
    class FakeListbox:
        def __init__(self):
            self.options = {}

        def configure(self, **options):
            self.options.update(options)

        def yview(self, *args):
            return args

    class FakeScrollbar:
        def __init__(self):
            self.options = {}

        def configure(self, **options):
            self.options.update(options)

        def set(self, *args):
            return args

    listbox = FakeListbox()
    scrollbar = FakeScrollbar()
    wire_vertical_scrollbar(listbox, scrollbar)
    assert listbox.options["yscrollcommand"] == scrollbar.set
    assert scrollbar.options["command"] == listbox.yview

    source = inspect.getsource(Stage7AApp._build)
    assert "wire_vertical_scrollbar(self.special_list, self.special_scrollbar)" in source
    assert "wire_vertical_scrollbar(self.general_list, self.general_scrollbar)" in source


def test_vertical_layout_contract_collapses_empty_general_results():
    class FakeResultsFrame:
        def __init__(self):
            self.rows = {}

        def rowconfigure(self, row, **options):
            self.rows[row] = options

    class FakeGeneralBox:
        def __init__(self):
            self.action = None

        def grid(self):
            self.action = "grid"

        def grid_remove(self):
            self.action = "grid_remove"

    results = FakeResultsFrame()
    general = FakeGeneralBox()
    set_general_results_visible(results, general, False)
    assert results.rows == {0: {"weight": 1}, 1: {"weight": 0}}
    assert general.action == "grid_remove"

    set_general_results_visible(results, general, True)
    assert results.rows == {0: {"weight": 3}, 1: {"weight": 2}}
    assert general.action == "grid"

    build_source = inspect.getsource(Stage7AApp._build)
    assert build_source.count("height=1") >= 2
    assert "self.prompt_bar" in build_source
    assert "self.recommendation_box.grid_remove()" in build_source
    assert "root.minsize(900, 540)" in inspect.getsource(create_window)


def test_special_search_keeps_id_and_original_term(presenter, knowledge, profile_store):
    special = knowledge.special["1"]
    item = next(item for item in presenter.search(special.term).special
                if item.special_id == special.special_id)
    state = session(knowledge, profile_store)
    assert state.add_special(item.special_id)
    assert state.selected_special_ids == (special.special_id,)
    assert state.prompt_preview == special.term.replace("_", " ")
    assert state.prompt_preview != (special.chosen_canonical or "").replace("_", " ") or \
        special.term == special.chosen_canonical


def test_alias_and_ambiguous_alias_export_original_identity(presenter, knowledge, profile_store):
    alias = next(item for item in knowledge.special.values() if item.layer == "Alias")
    card = next(item for item in presenter.search(alias.term).special
                if item.special_id == alias.special_id)
    state = session(knowledge, profile_store)
    state.add_special(card.special_id)
    assert state.prompt_preview == alias.term.replace("_", " ")

    ambiguous = next(item for item in knowledge.special.values()
                     if item.match_type == "alias_ambiguous_multiple")
    assert knowledge.resolve_exact(ambiguous.term).resolved_canonical is None
    card = next(item for item in presenter.search(ambiguous.term).special
                if item.special_id == ambiguous.special_id)
    state = session(knowledge, profile_store)
    state.add_special(card.special_id)
    assert state.prompt_preview == ambiguous.term.replace("_", " ")


def test_same_canonical_expands_and_selects_separate_special_ids(presenter, knowledge, profile_store):
    grouped = defaultdict(list)
    for special in knowledge.special.values():
        if special.chosen_canonical:
            grouped[special.chosen_canonical].append(special.special_id)
    canonical, ids = next((canonical, ids) for canonical, ids in grouped.items() if len(ids) > 1)
    cards = presenter.search(canonical).special
    card_ids = [item.special_id for item in cards if item.special_id in ids]
    assert set(card_ids) == set(ids)
    state = session(knowledge, profile_store)
    assert state.add_special(card_ids[0])
    assert state.add_special(card_ids[1])
    assert state.selected_special_ids == (card_ids[0], card_ids[1])
    assert any(item.code == "same_statistics_canonical" for item in state.warnings)
    assert state.selected_special_ids == (card_ids[0], card_ids[1])


def test_special_japanese_and_overlay_search_expand_to_special(presenter, knowledge):
    special = knowledge.special["1"]
    assert any(item.special_id == special.special_id
               for item in presenter.search(special.japanese).special)
    special_canonicals = {candidate for item in knowledge.special.values()
                          for candidate in item.canonical_candidates}
    term, canonicals = next((term, canonicals) for term, canonicals in knowledge.overlay_lookup.items()
                            if set(canonicals) & special_canonicals)
    result = presenter.search(term)
    assert any(item.matched_canonical in canonicals for item in result.special)


def test_search_only_japanese_is_not_promoted_to_general_display(presenter, knowledge):
    special_canonicals = {candidate for item in knowledge.special.values()
                          for candidate in item.canonical_candidates}
    term, canonicals = next(
        (term, canonicals) for term, canonicals in knowledge.overlay_lookup.items()
        if any(canonical not in special_canonicals
               and canonical not in knowledge.japanese_overlay.display_by_canonical
               for canonical in canonicals)
    )
    result = presenter.search(term)
    item = next(item for item in result.general if item.canonical in canonicals)
    assert item.display_japanese is None


def test_semantic_unmapped_has_no_fake_canonical_or_count(presenter, knowledge, profile_store):
    special = next(item for item in knowledge.special.values()
                   if item.match_type == "semantic_unmapped")
    card = next(item for item in presenter.search(special.term).special
                if item.special_id == special.special_id)
    assert card.matched_canonical is None
    assert special.chosen_canonical is None and special.canonical_candidates == ()
    state = session(knowledge, profile_store)
    state.add_special(card.special_id)
    assert state.prompt_preview == special.term.replace("_", " ")
    assert any(item.code == "statistics_unavailable" for item in state.warnings)


def test_duplicate_prevention_manual_auxiliary_and_prompt_order(knowledge, profile_store, presenter):
    state = session(knowledge, profile_store)
    special_ids = tuple(knowledge.special)[:2]
    assert state.add_special(special_ids[0]) and not state.add_special(special_ids[0])
    assert state.add_special(special_ids[1])
    special_canonicals = {candidate for item in knowledge.special.values()
                          for candidate in item.canonical_candidates}
    canonical = next(tag for tag in knowledge.canonical if tag not in special_canonicals)
    general = next(item for item in presenter.search(canonical).general if item.canonical == canonical)
    assert state.add_auxiliary(general.canonical) and not state.add_auxiliary(general.canonical)
    expected = [knowledge.special[sid].term.replace("_", " ") for sid in special_ids]
    expected.append(canonical.replace("_", " "))
    assert state.prompt_preview == ", ".join(expected)
    assert state.clipboard_text == state.prompt_preview
    assert state.automatic_injections == ()


def test_stage7b_statistics_core_requires_complete_special_identity(knowledge, profile_store):
    state = session(knowledge, profile_store)
    state.add_special("1")
    assert state.statistics_core_canonicals() == (knowledge.special["1"].chosen_canonical,)
    semantic = next(item for item in knowledge.special.values()
                    if item.match_type == "semantic_unmapped")
    state.add_special(semantic.special_id)
    assert state.statistics_core_canonicals() is None


def test_stage7b_ui_keeps_manual_auxiliary_and_no_automatic_injection():
    source = inspect.getsource(Stage7AApp)
    assert "RecommendationEngine" in source
    assert "RecommendationController" in source
    assert "_add_recommended" in source
    assert "self.session.add_auxiliary(canonical)" in source
    assert "candidate.role" not in inspect.getsource(Stage7AApp._render_candidate_rows)
    worker_callback = inspect.getsource(Stage7AApp._on_recommendation_result)
    assert "recommendation_queue.put" in worker_callback
    assert ".after(" not in worker_callback


def test_stage7b_candidate_add_is_manual_auxiliary_only(knowledge, profile_store):
    state = session(knowledge, profile_store)
    special_id = next(sid for sid, item in knowledge.special.items() if item.chosen_canonical)
    state.add_special(special_id)
    original_core = state.selected_special_ids
    assert state.add_auxiliary("1girl")
    assert not state.add_auxiliary("1girl")
    assert state.selected_special_ids == original_core
    assert state.manual_auxiliary_canonicals == ("1girl",)
    assert state.automatic_injections == ()
    assert state.prompt_preview.endswith("1girl")


def test_warning_messages_use_only_explicit_tag_values(knowledge, profile_store):
    true_id = next(sid for sid, profile in profile_store.profiles.items()
                   if profile.ActorRequirementOverride is True)
    notices = Stage7AWarningPresenter(knowledge, profile_store).notices([true_id])
    assert any(item.code == "needs_actor" and item.message == "誰が行うかを決める必要があります"
               for item in notices)

    actor_separation_id = next(sid for sid, profile in profile_store.profiles.items()
                               if "ACTOR_SEPARATION_REQUIRED" in profile.SpecialFlags)
    notices = Stage7AWarningPresenter(knowledge, profile_store).notices([actor_separation_id])
    assert any(item.code == "actor_separation_required"
               and item.message == "複数の人物を描き分ける必要があります" for item in notices)

    blank_id = next(sid for sid, profile in profile_store.profiles.items()
                    if profile.FamilyRuleId and all(getattr(profile, name) is None for name in (
                        "ActorRequirementOverride", "BodypartRequirementOverride",
                        "ImplementRequirementOverride", "PoseRequirementOverride",
                        "CameraRequirementOverride", "SpatialAssignmentOverride")))
    profile = profile_store.profiles[blank_id]
    original_rule = profile_store.family_rules[profile.FamilyRuleId]
    inferred_rule = replace(original_rule, DefaultNeedsActor=True)
    isolated_store = GenerationProfileStore(
        knowledge.special, {blank_id: profile}, {profile.FamilyRuleId: inferred_rule}, {}
    )
    notices = Stage7AWarningPresenter(knowledge, isolated_store).notices([blank_id])
    assert not any(item.code.startswith("needs_") for item in notices)

    shaped = replace(profile, ShapeConflictGroup="synthetic_shape_group")
    shaped_store = GenerationProfileStore(
        knowledge.special, {blank_id: shaped}, {profile.FamilyRuleId: original_rule}, {}
    )
    notices = Stage7AWarningPresenter(knowledge, shaped_store).notices([blank_id])
    assert not any("shape" in item.code or "conflict" in item.code for item in notices)


def test_provisional_and_model_dependent_notices_do_not_block_export(knowledge, profile_store):
    provisional_id = next(sid for sid, profile in profile_store.profiles.items()
                          if profile.PromotionStatus == "PROVISIONAL")
    state = session(knowledge, profile_store)
    state.add_special(provisional_id)
    assert state.prompt_preview
    assert any(item.code == "profile_not_final" for item in state.warnings)

    source = profile_store.profiles["1"]
    modified = replace(source, PromptUseMode="MODEL_DEPENDENT")
    isolated_store = GenerationProfileStore(
        knowledge.special,
        {"1": modified},
        {source.FamilyRuleId: profile_store.family_rules[source.FamilyRuleId]},
        {},
    )
    state = session(knowledge, isolated_store)
    state.add_special("1")
    assert state.prompt_preview
    assert any(item.code == "model_dependent" for item in state.warnings)


def test_stage4_search_results_are_untouched(knowledge, profile_store):
    baseline = TagSearchEngine(knowledge)
    adapter_engine = TagSearchEngine(knowledge)
    presenter = SpecialSearchPresenter(knowledge, adapter_engine, profile_store)
    for query in ("twintails", "sole_female", knowledge.special["1"].japanese,
                  "long h", "ng hai", "hair", "a", "nagatoro"):
        expected = baseline.search_one(query, limit=100)
        presenter.search(query, limit=100)
        assert adapter_engine.search_one(query, limit=100) == expected


def test_runtime_search_path_is_offline(monkeypatch, knowledge, profile_store):
    def fail(*args, **kwargs):
        raise AssertionError("network access is not allowed")

    monkeypatch.setattr("socket.create_connection", fail)
    presenter = SpecialSearchPresenter(knowledge, TagSearchEngine(knowledge), profile_store)
    assert presenter.search("拘束").special


@pytest.mark.parametrize(("relative", "expected"), (
    ("data/special2788/illustrious_tag_knowledge_base_2788.csv", "07584b365d5a68dbadd3f5e80859e768c2718b18746e32de02ce4b8bd60935e3"),
    ("data/source/danbooru-2026-09-02.csv", "9b32d5ac0713ab252e7470ba6af9cb34de56878b6b3b13dfbbf6a4a37d82d95b"),
    ("data/derived/danbooru_alias_normalized_index_VERIFIED_34417.csv", "3f942704a10bb342ae7368024337849d392d54745061cf9259e51b9f6080a394"),
    ("data/derived/special2788_VERIFIED_LINKAGE.csv", "d2691e774df0da762dbbf644c8aee4d68fe7d370ea91121c9ad083ccd3728ec2"),
    ("data/generation/special2788_generation_profile.csv", "3d3b7c16bee23c34892c6ac1a40b69208ef14199c5bae749ac8a22151c8dc835"),
    ("data/generation/generation_family_rules.csv", "0f0e2e9f1f001d12e421324a6356bab42293fb206fe53a3e642495d5765c6936"),
    ("data/generation/generation_model_observations.csv", "ee036aac810ef94b9f0376a23d0159f4275d6d2feac7ccd689ca297d361164c8"),
    ("data/runtime/japanese_overlay.json", "de1b375d79ef05f4c2477347b20b8a09115511d2ecbd39602bdebcdfa6d576dc"),
))
def test_protected_assets_are_unchanged(relative, expected):
    assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected
