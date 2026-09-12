from pathlib import Path
from types import SimpleNamespace

from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.models import CanonicalTag, SpecialTag
from danbooru_tag_tool.search import SearchResult, TagSearchEngine
from danbooru_tag_tool.v1_browse import PendingGeneralBrowseProvider
from danbooru_tag_tool.v1_search import V1SearchService
from danbooru_tag_tool.v1_workspace import PromptWorkspace


ROOT = Path(__file__).resolve().parents[1]


class FakeProductFit:
    def allows(self, special_id, surface):
        return True


class FakeKnowledge:
    def __init__(self):
        self.canonical = {
            "school_uniform": CanonicalTag("school_uniform", 0, 100),
            "solo": CanonicalTag("solo", 0, 1000),
        }
        self.special = {
            "1": SpecialTag(
                "1", "special_pose", "特殊ポーズ", "desc", "Alias", "pose",
                "solo", "alias_unique", ("solo",), main_category="ポーズ",
            ),
            "2": SpecialTag(
                "2", "unmapped_concept", "未対応概念", "desc", "Semantic", "other",
                None, "semantic_unmapped", (), main_category="その他",
            ),
        }
        self.product_fit = FakeProductFit()
        self.japanese_overlay = SimpleNamespace(display_by_canonical={"school_uniform": "制服"})
        self.translations = ()

    def resolve_exact(self, text):
        normalized = text.strip().replace("_", " ").lower()
        if normalized == "school uniform":
            return SimpleNamespace(
                canonical_candidates=("school_uniform",), semantic_ids=(), special_ids=())
        if normalized == "special pose":
            return SimpleNamespace(
                canonical_candidates=("solo",), semantic_ids=(), special_ids=("1",))
        if normalized == "unmapped concept":
            return SimpleNamespace(
                canonical_candidates=(), semantic_ids=("SEM1",), special_ids=("2",))
        return SimpleNamespace(canonical_candidates=(), semantic_ids=(), special_ids=())


def result(canonical, match_type, *, special=False):
    return SearchResult(
        canonical, canonical.replace("_", " ") if canonical else None, (), 0, 1,
        special, (), match_type, (match_type,), "Exact", ("test",), (),
    )


def test_intent_first_search_hides_partial_noise_when_strong_match_exists():
    strong = result("solo", "canonical")
    piano = result("piano", "partial")
    analog = result("analog_clock", "prefix")
    engine = SimpleNamespace(search_one=lambda *args, **kwargs: (strong, piano, analog))
    response = V1SearchService(engine).search_one("anal")
    assert response.results == (strong,)
    assert response.suppressed_loose_count == 2


def test_prefix_intent_hides_embedded_partial_noise_without_strong_match():
    prefix = result("long_hair", "prefix")
    partial = result("very_long_hair", "partial")
    engine = SimpleNamespace(search_one=lambda *args, **kwargs: (prefix, partial))
    response = V1SearchService(engine).search_one("long h")
    assert response.results == (prefix,)
    assert response.suppressed_loose_count == 1


def test_mixed_japanese_english_query_uses_one_workflow_and_dedupes_identity():
    canonical = result("school_uniform", "canonical")
    japanese = SearchResult(
        "school_uniform", "school uniform", ("制服",), 0, 100, False, (),
        "japanese", ("japanese",), "Exact", ("test",), (),
    )
    noise = result("school_bag", "partial")
    calls = []
    def search(text, **kwargs):
        calls.append(text)
        if text == "制服 school uniform":
            return (noise,)
        if text == "制服":
            return (japanese,)
        if text == "school uniform":
            return (canonical,)
        return ()
    response = V1SearchService(SimpleNamespace(search_one=search)).search_one("制服 school uniform")
    assert response.mixed_fallback_used
    assert response.results == (canonical,)
    assert calls == ["制服 school uniform", "制服", "school uniform"]


def test_workspace_preview_is_exactly_visible_order_and_has_no_hidden_insertion():
    workspace = PromptWorkspace(FakeKnowledge())
    workspace.load_existing_prompt("school_uniform, unknown_tag")
    assert [item.english for item in workspace.items] == ["school uniform", "unknown_tag"]
    assert workspace.preview == "school uniform, unknown_tag"
    unknown_id = workspace.items[1].item_id
    workspace.remove(unknown_id)
    added = workspace.add_special("1")
    assert added.english == "solo"
    assert workspace.preview == "school uniform, solo"
    assert workspace.clipboard_text == workspace.preview
    assert workspace.move(workspace.items[1].item_id, -1)
    assert workspace.preview == "solo, school uniform"


def test_unmapped_special_is_preserved_but_explicitly_unresolved():
    workspace = PromptWorkspace(FakeKnowledge())
    item = workspace.add_special("2")
    assert item.english == "unmapped concept"
    assert not item.resolved
    assert item.special_id == "2"


def test_unknown_existing_prompt_is_preserved_instead_of_dropped():
    workspace = PromptWorkspace(FakeKnowledge())
    workspace.load_existing_prompt("made_up_tag")
    assert len(workspace.items) == 1
    assert not workspace.items[0].resolved
    assert workspace.items[0].english == "made_up_tag"


def test_general_browse_provider_is_explicit_issue64_empty_state():
    provider = PendingGeneralBrowseProvider()
    assert not provider.available
    assert provider.categories() == ()
    assert provider.browse() == ()
    assert "Issue #64" in provider.status_text


def test_real_anal_query_does_not_surface_known_piano_or_analog_noise():
    knowledge = TagKnowledgeCore.load(ROOT)
    response = V1SearchService(TagSearchEngine(knowledge)).search_one("anal", limit=50)
    assert response.results
    canonicals = tuple(result.canonical or "" for result in response.results)
    assert not any("piano" in canonical for canonical in canonicals)
    assert not any(canonical.startswith("analog") for canonical in canonicals)
