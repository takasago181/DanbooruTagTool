"""Check the bounded formatting optimization against the previous full sort."""
from pathlib import Path

from danbooru_tag_tool.knowledge import TagKnowledgeCore
from danbooru_tag_tool.search import TagSearchEngine, _QUALITY


class FullSortSearch(TagSearchEngine):
    def _deduplicate_and_rank(self, entries, limit):
        grouped = {}
        for entry in entries:
            identity = (("canonical", entry.canonical) if entry.canonical else
                        ("semantic", entry.semantic_id or "", entry.special_id or ""))
            grouped.setdefault(identity, []).append(entry)
        results = [self._result_for(group) for group in grouped.values()]
        results.sort(key=lambda r: (
            _QUALITY[r.match_type], not r.is_special,
            -(r.current_post_count if r.current_post_count is not None else -1),
            r.canonical or (r.semantic_relations[0].semantic_id if r.semantic_relations else ""),
        ))
        return tuple(results[:limit])


def test_topk_preserves_complete_results_against_full_sort():
    knowledge = TagKnowledgeCore.load(Path(__file__).resolve().parents[1])
    engine = TagSearchEngine(knowledge)
    reference = FullSortSearch(knowledge)
    for query in ("twintails", "sole_female", knowledge.special["1"].japanese,
                  "long h", "ng hai", "hair", "a", "nagatoro",
                  knowledge.semantic["SEM0001"].semantic_term):
        expected = reference.search_one(query, limit=100)
        for limit in (1, 50, 100):
            assert engine.search_one(query, limit=limit) == expected[:limit]
