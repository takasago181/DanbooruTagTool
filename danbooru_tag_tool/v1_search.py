"""Issue #66 beginner-facing search policy.

This module wraps the accepted Stage 4 search engine instead of rewriting the
knowledge index.  The v1 UI is intent-first: exact/strong and word-prefix intent
are not visually swamped by incidental embedded-substring noise.
"""
from __future__ import annotations

from dataclasses import dataclass
import re

from .search import SearchResult, TagSearchEngine


_STRONG_MATCH_TYPES = frozenset({"canonical", "alias", "japanese", "semantic", "special"})
_JAPANESE_RE = re.compile(r"[ぁ-んァ-ヶ一-龯々ー]")
_LATIN_RE = re.compile(r"[A-Za-z]")


@dataclass(frozen=True, slots=True)
class V1SearchResponse:
    query: str
    results: tuple[SearchResult, ...]
    suppressed_loose_count: int = 0
    mixed_fallback_used: bool = False


class V1SearchService:
    """Beginner-facing search semantics over the existing search engine."""

    def __init__(self, engine: TagSearchEngine):
        self.engine = engine

    def search_one(self, text: str, *, limit: int = 50) -> V1SearchResponse:
        if limit < 1:
            raise ValueError("limit must be positive")
        raw = self.engine.search_one(text, limit=limit, product_facing=True)
        mixed_used = False

        # A bilingual query such as ``制服 school uniform`` should stay in the
        # same search field. If the combined surface has no strong hit, search
        # its Japanese and Latin parts through the same engine and merge by
        # canonical/Special identity. No translation or new identity is made up.
        if not self._strong(raw):
            mixed_parts = self._mixed_parts(text)
            if mixed_parts:
                mixed_used = True
                combined = list(raw)
                for part in mixed_parts:
                    combined.extend(self.engine.search_one(part, limit=limit, product_facing=True))
                raw = self._dedupe(combined)

        filtered, suppressed = self._intent_filter(raw, limit)
        return V1SearchResponse(text, filtered, suppressed, mixed_used)

    @staticmethod
    def _strong(results: tuple[SearchResult, ...] | list[SearchResult]) -> tuple[SearchResult, ...]:
        return tuple(result for result in results if result.match_type in _STRONG_MATCH_TYPES)

    @classmethod
    def _intent_filter(cls, raw, limit: int) -> tuple[tuple[SearchResult, ...], int]:
        raw = tuple(raw)
        strong = cls._strong(raw)
        if strong:
            return strong[:limit], len(raw) - len(strong)
        prefix = tuple(result for result in raw if result.match_type == "prefix")
        if prefix:
            return prefix[:limit], len(raw) - len(prefix)
        return raw[:limit], 0

    @staticmethod
    def _identity(result: SearchResult):
        if result.canonical is not None:
            return ("canonical", result.canonical)
        if result.semantic_relations:
            return ("semantic", tuple(relation.semantic_id for relation in result.semantic_relations))
        return ("special", result.special_ids)

    @classmethod
    def _dedupe(cls, results) -> tuple[SearchResult, ...]:
        values = {}
        quality = {"canonical": 0, "alias": 1, "japanese": 2, "semantic": 3,
                   "special": 3, "prefix": 4, "partial": 5}
        for result in results:
            key = cls._identity(result)
            current = values.get(key)
            if current is None or quality[result.match_type] < quality[current.match_type]:
                values[key] = result
        return tuple(sorted(values.values(), key=lambda result: (
            quality[result.match_type],
            not result.is_special,
            -(result.current_post_count if result.current_post_count is not None else -1),
            result.canonical or "",
        )))

    @staticmethod
    def _mixed_parts(text: str) -> tuple[str, str] | ():
        if not (_JAPANESE_RE.search(text) and _LATIN_RE.search(text)):
            return ()
        japanese = " ".join("".join(ch if _JAPANESE_RE.match(ch) else " " for ch in text).split())
        latin = " ".join("".join(ch if not _JAPANESE_RE.match(ch) else " " for ch in text).split())
        if not japanese or not _LATIN_RE.search(latin):
            return ()
        return japanese, latin
