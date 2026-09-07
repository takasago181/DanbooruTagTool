from dataclasses import replace
from pathlib import Path

import pytest

from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.models import Translation
from danbooru_tag_tool.search import TagSearchEngine


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def knowledge():
    return TagKnowledgeCore.load(ROOT)


@pytest.fixture(scope="module")
def engine(knowledge):
    return TagSearchEngine(knowledge)


def first(results, canonical):
    return next(result for result in results if result.canonical == canonical)


def test_canonical_exact_underscore_space_and_prompt_representation(engine):
    for query in ("twintails", "school_uniform", "school uniform"):
        result = engine.search_one(query)[0]
        expected = query.replace(" ", "_")
        assert result.canonical == expected
        assert result.match_type == "canonical"
        assert result.prompt_representation == result.canonical.replace("_", " ")
        assert result.category is not None and result.current_post_count is not None


def test_canonical_precedence_beats_alias_collision(engine):
    result = engine.search_one("aboleuk")[0]
    assert result.canonical == "aboleuk"
    assert result.match_type == "canonical"
    assert "alias" not in result.match_types


def test_unique_and_ambiguous_aliases(engine):
    assert engine.search_one("sole_female")[0].canonical == "1girl"
    assert engine.search_one("sole_female")[0].match_type == "alias"
    candidates = {result.canonical for result in engine.search_one("nagatoro")
                  if result.match_type == "alias"}
    assert candidates == {"ijiranaide_nagatoro-san", "nagatoro_hayase"}


def test_japanese_exact_and_special_badge(knowledge):
    special = next(item for item in knowledge.special.values()
                   if item.chosen_canonical == "anus")
    engine = TagSearchEngine(knowledge)
    result = first(engine.search_one(special.japanese), "anus")
    assert result.match_type == "japanese"
    assert result.is_special and special.special_id in result.special_ids
    assert special.japanese in result.japanese


def test_translation_japanese_exact(knowledge):
    core = TagKnowledgeCore(knowledge.canonical, knowledge.aliases, knowledge.special,
                            knowledge.semantic,
                            [Translation("school_uniform", "制服", "test", "UNREVIEWED")])
    result = TagSearchEngine(core).search_one("制服")[0]
    assert result.canonical == "school_uniform" and result.match_type == "japanese"
    assert "translation" in result.provenance


def test_semantic_unmapped_keeps_no_fake_canonical(engine, knowledge):
    item = knowledge.semantic["SEM0001"]
    result = engine.search_one(item.semantic_term)[0]
    assert result.match_type == "semantic" and result.group == "Semantic"
    assert result.canonical is None and result.current_post_count is None
    assert result.semantic_relations[0].relation_type == "UNMAPPED"


def test_semantic_mapped_result_retains_relation(knowledge):
    item = replace(knowledge.semantic["SEM0001"], candidate_canonical="school_uniform",
                   relation_type="related", review_status="REVIEWED")
    core = TagKnowledgeCore(knowledge.canonical, knowledge.aliases, knowledge.special,
                            {item.semantic_id: item})
    result = first(TagSearchEngine(core).search_one(item.semantic_term), "school_uniform")
    assert result.match_type == "semantic"
    assert result.semantic_relations[0].candidate_canonical == "school_uniform"
    assert result.semantic_relations[0].relation_type == "related"


def test_prefix_partial_and_exact_ordering(engine):
    results = engine.search_one("long h")
    assert first(results, "long_hair").match_type == "prefix"
    assert all(result.match_type != "partial" for result in results
               if result.canonical == "long_hair")
    # Exact canonical stays ahead of any lower-quality Special candidate.
    results = engine.search_one("school uniform")
    exact = first(results, "school_uniform")
    assert exact.match_type == "canonical"
    assert all(results.index(exact) < index for index, result in enumerate(results)
               if result.match_type in {"prefix", "partial"})
    partial = first(engine.search_one("ng hai"), "long_hair")
    assert partial.match_type == "partial"

    # ``anus`` is a canonical exact while Special terms such as ``spread_anus``
    # are only partial matches; the badge must not reverse that relevance order.
    results = engine.search_one("anus")
    assert results[0].canonical == "anus" and results[0].match_type == "canonical"
    assert any(result.is_special and result.match_type == "partial" for result in results)


def test_same_quality_special_priority_and_deduplication(engine):
    results = engine.search_one("long h")
    prefix = [result for result in results if result.match_type == "prefix"]
    assert prefix
    special_positions = [index for index, result in enumerate(prefix) if result.is_special]
    ordinary_positions = [index for index, result in enumerate(prefix) if not result.is_special]
    if special_positions and ordinary_positions:
        assert max(special_positions) < min(ordinary_positions)
    assert len([result for result in results if result.canonical == "long_hair"]) == 1


def test_multiple_input_comma_newline_and_spaces_are_not_tokens(engine):
    result_sets = engine.search("twintails, 制服\nlong h")
    assert len(result_sets) == 3
    assert result_sets[0][0].canonical == "twintails"
    assert first(engine.search("school uniform")[0], "school_uniform").match_type == "canonical"
