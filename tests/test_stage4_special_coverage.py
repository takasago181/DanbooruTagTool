"""Audit the real snapshot for the Stage 4 Special-only exact precondition."""
from collections import Counter
from pathlib import Path

from danbooru_tag_tool.knowledge import TagKnowledgeCore


def test_real_special_terms_are_all_absorbed_by_existing_exact_routes():
    knowledge = TagKnowledgeCore.load(Path(__file__).resolve().parents[1])
    resolutions = [knowledge.resolve_exact(item.term)
                   for item in knowledge.special.values()]
    assert len(resolutions) == 2788
    assert Counter(result.match_type for result in resolutions) == {
        "canonical": 1674, "alias": 778, "semantic": 336,
    }
    # The search engine's Special-only fallback requires match_type == "none".
    # Do not fabricate a real-data fixture or delete an alias to exercise it.
    assert not any(result.match_type == "none" and result.special_ids
                   for result in resolutions)
