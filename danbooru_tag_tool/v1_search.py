"""Issue #66 beginner-facing search policy.

This module deliberately wraps the legacy Stage 4 engine instead of rewriting the
knowledge index. The v1 UI is intent-first: exact/strong matches are not mixed
with substring noise.
"""
from __future__ import annotations

from dataclasses import dataclass

from .search import SearchResult, TagSearchEngine


_STRONG_MATCH_TYPES = frozenset({"canonical", "alias", "japanese", "semantic", "special"})


@dataclass(frozen=True, slots=True)
class V1SearchResponse:
    query: str
    results: tuple[SearchResult, ...]
    suppressed_loose_count: int = 0


class V1SearchService:
    """Beginner-facing search semantics over the existing search engine.

    The underlying index remains the source of truth. When at least one strong
    intent match exists, prefix/partial rows are hidden from the default v1
    result set. This prevents cases such as ``anal`` surfacing unrelated
    ``piano``/``analog...`` substring matches beside a strong intended match.
    """

    def __init__(self, engine: TagSearchEngine):
        self.engine = engine

    def search_one(self, text: str, *, limit: int = 50) -> V1SearchResponse:
        raw = self.engine.search_one(text, limit=limit, product_facing=True)
        strong = tuple(result for result in raw if result.match_type in _STRONG_MATCH_TYPES)
        if strong:
            return V1SearchResponse(text, strong[:limit], len(raw) - len(strong))
        return V1SearchResponse(text, raw[:limit], 0)
