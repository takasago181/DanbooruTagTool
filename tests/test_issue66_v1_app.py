from types import SimpleNamespace

from danbooru_tag_tool.models import CanonicalTag, SpecialTag
from danbooru_tag_tool.search import SearchResult
from danbooru_tag_tool.v1_browse import PendingGeneralBrowseProvider
from danbooru_tag_tool.v1_search import V1SearchService
from danbooru_tag_tool.v1_workspace import PromptWorkspace


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
                "1", "special_pose", "特殊ポーズ", "desc", "Core", "pose",
                None, "semantic_unmapped", (), main_category="ポーズ",
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
                canonical_candidates=(), semantic_ids=(), special_ids=("1",))
        return SimpleNamespace(canonical_candidates=(), semantic_ids=(), special_ids=())


def result(canonical, match_type):
    return SearchResult(
        canonical, canonical.replace("_", " ") if canonical else None, (), 0, 1,
        False, (), match_type, (match_type,), "Exact", ("test",), (),
    )


def test_intent_first_search_hides_partial_noise_when_strong_match_exists():
    strong = result("solo", "canonical")
    piano = result("piano", "partial")
    analog = result("analog_clock", "partial")
    engine = SimpleNamespace(search_one=lambda *args, **kwargs: (strong, piano, analog))
    response = V1SearchService(engine).search_one("anal")
    assert response.results == (strong,)
    assert response.suppressed_loose_count == 2


def test_workspace_preview_is_exactly_visible_order_and_has_no_hidden_insertion():
    workspace = PromptWorkspace(FakeKnowledge())
    workspace.load_existing_prompt("school_uniform, unknown_tag")
    assert [item.english for item in workspace.items] == ["school uniform", "unknown_tag"]
    assert workspace.preview == "school uniform, unknown_tag"
    unknown_id = workspace.items[1].item_id
    workspace.remove(unknown_id)
    workspace.add_special("1")
    assert workspace.preview == "school uniform, special pose"
    assert workspace.clipboard_text == workspace.preview
    assert workspace.move(workspace.items[1].item_id, -1)
    assert workspace.preview == "special pose, school uniform"


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
