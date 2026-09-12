"""Stage 4 unified JP/EN search, built only from ``TagKnowledgeCore`` data."""
from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from heapq import nsmallest
from typing import Iterable

from .knowledge import ExactResolution, TagKnowledgeCore
from .normalization import normalize_lookup, split_prompt_input
from .prompt_formatter import PromptFormatter


@dataclass(frozen=True, slots=True)
class SemanticRelation:
    """A static bridge row; it is never an inferred Danbooru tag."""

    semantic_id: str
    semantic_term: str
    candidate_canonical: str | None
    relation_type: str
    review_status: str
    semantic_subtype: str = ""
    anchor_kind: str = ""
    anchor_value: str = ""
    default_prompt_mode: str = ""


@dataclass(frozen=True, slots=True)
class SearchResult:
    """UI-independent presentation record for one canonical or semantic entity."""

    canonical: str | None
    prompt_representation: str | None
    japanese: tuple[str, ...]
    category: int | None
    current_post_count: int | None
    is_special: bool
    special_ids: tuple[str, ...]
    match_type: str
    match_types: tuple[str, ...]
    group: str
    provenance: tuple[str, ...]
    semantic_relations: tuple[SemanticRelation, ...] = ()


@dataclass(frozen=True, slots=True)
class _Entry:
    key: str
    canonical: str | None
    special_id: str | None
    semantic_id: str | None
    match_type: str
    provenance: str


_QUALITY = {"canonical": 0, "alias": 1, "japanese": 2, "semantic": 3,
            "special": 3, "prefix": 4, "partial": 5}


class TagSearchEngine:
    """Small in-memory search index; no post data, statistics, or external engine."""

    def __init__(self, knowledge: TagKnowledgeCore):
        self.knowledge = knowledge
        self._canonical_special_ids: dict[str, tuple[str, ...]] = {}
        special_by_canonical: dict[str, list[str]] = {}
        for special in knowledge.special.values():
            for canonical in special.canonical_candidates:
                special_by_canonical.setdefault(canonical, []).append(special.special_id)
        self._canonical_special_ids = {
            canonical: tuple(ids) for canonical, ids in special_by_canonical.items()
        }
        entries: list[_Entry] = []
        for tag in knowledge.canonical.values():
            entries.append(_Entry(tag.lookup_key, tag.canonical_tag, None, None,
                                  "canonical", "canonical_dictionary"))
        for special in knowledge.special.values():
            for canonical in self._special_targets(special.special_id):
                entries.append(_Entry(normalize_lookup(special.term), canonical, special.special_id,
                                      None, "prefix", "special2788"))
        for key, ids in knowledge.special_search_lookup.items():
            for special_id in ids:
                for canonical in self._special_targets(special_id):
                    entries.append(_Entry(key, canonical, special_id, None,
                                          "special", "ruleset2_search_key"))
        for key, candidates in knowledge.aliases.items():
            for canonical in candidates:
                entries.append(_Entry(key, canonical, None, None, "alias", "alias_index"))
        for key, ids in knowledge.japanese_lookup.items():
            for special_id in ids:
                special = knowledge.special[special_id]
                for canonical in self._special_targets(special_id):
                    entries.append(_Entry(key, canonical, special_id, None,
                                          "japanese", "special2788"))
        for key, candidates in knowledge.translation_lookup.items():
            for canonical in candidates:
                entries.append(_Entry(key, canonical, None, None,
                                      "japanese", "translation"))
        for key, candidates in knowledge.overlay_lookup.items():
            for canonical in candidates:
                entries.append(_Entry(key, canonical, None, None,
                                      "japanese", "japanese_overlay"))
        for key, ids in knowledge.semantic_lookup.items():
            for semantic_id in ids:
                semantic = knowledge.semantic[semantic_id]
                entries.append(_Entry(key, semantic.candidate_canonical, semantic.special_id,
                                      semantic_id, "semantic", "semantic_bridge"))
        self._entries = tuple(entries)
        self._entries_by_key = tuple(sorted(entries, key=lambda entry: entry.key))
        self._keys = tuple(entry.key for entry in self._entries_by_key)

    def search(self, text: str, *, limit: int = 50) -> tuple[tuple[SearchResult, ...], ...]:
        """Split a prompt-level input on commas/newlines and search each complete part."""
        if limit < 1:
            raise ValueError("limit must be positive")
        return tuple(self.search_one(query, limit=limit) for query in split_prompt_input(text))

    def search_one(self, text: str, *, limit: int = 50,
                   product_facing: bool = False) -> tuple[SearchResult, ...]:
        if limit < 1:
            raise ValueError("limit must be positive")
        key = normalize_lookup(text)
        if not key:
            return ()
        matches: list[_Entry] = []
        exact = self.knowledge.resolve_exact(text)
        matches.extend(self._exact_entries(exact, key))

        # Prefix is indexed; partial is deliberately a bounded Stage-4 fallback scan.
        left = bisect_left(self._keys, key)
        right = bisect_right(self._keys, key + "\U0010ffff")
        matches.extend(
            _Entry(entry.key, entry.canonical, entry.special_id, entry.semantic_id,
                   "prefix", entry.provenance)
            for entry in self._entries_by_key[left:right] if entry.key != key
        )
        matches.extend(
            _Entry(entry.key, entry.canonical, entry.special_id, entry.semantic_id,
                   "partial", entry.provenance)
            for entry in self._entries if key in entry.key and not entry.key.startswith(key)
        )
        if product_facing:
            policy = self.knowledge.product_fit
            matches = [entry for entry in matches
                       if (entry.special_id is None or policy.allows(entry.special_id, 'search'))
                       and (entry.canonical is None or policy.canonical_allows(entry.canonical, 'search'))]
        return self._deduplicate_and_rank(matches, limit)

    def _special_targets(self, special_id: str) -> tuple[str, ...]:
        special = self.knowledge.special[special_id]
        return ((special.chosen_canonical,) if special.chosen_canonical else special.canonical_candidates)

    def _exact_entries(self, resolution: ExactResolution, key: str) -> list[_Entry]:
        entries: list[_Entry] = []
        provenance = {"canonical": "canonical_dictionary", "alias": "alias_index",
                      "japanese": "special2788"}
        for canonical in resolution.canonical_candidates:
            sources = (provenance.get(resolution.match_type, "canonical_dictionary"),)
            if resolution.match_type == "japanese":
                sources = tuple(dict.fromkeys(
                    (["special2788"] if any(canonical in self._special_targets(sid)
                                            for sid in self.knowledge.japanese_lookup.get(key, ())) else []) +
                    (["translation"] if canonical in self.knowledge.translation_lookup.get(key, ()) else []) +
                    (["japanese_overlay"] if canonical in self.knowledge.overlay_lookup.get(key, ()) else [])
                ))
            for source in sources:
                entries.append(_Entry("", canonical, None, None, resolution.match_type, source))
        for special_id in resolution.special_ids:
            targets = self._special_targets(special_id)
            if targets and resolution.match_type == "none":
                for canonical in targets:
                    entries.append(_Entry("", canonical, special_id, None, "special", "special2788"))
            elif not targets and not self.knowledge.special_to_semantic_ids.get(special_id):
                entries.append(_Entry("", None, special_id, None, resolution.match_type, "special2788"))
        for semantic_id in resolution.semantic_ids:
            semantic = self.knowledge.semantic[semantic_id]
            entries.append(_Entry("", semantic.candidate_canonical, semantic.special_id,
                                  semantic_id, "semantic", "semantic_bridge"))
        return entries

    def _deduplicate_and_rank(self, entries: Iterable[_Entry], limit: int) -> tuple[SearchResult, ...]:
        grouped: dict[tuple[str, str] | tuple[str, str, str], list[_Entry]] = {}
        for entry in entries:
            # A mapped semantic candidate is folded into its canonical result.  An unmapped
            # semantic remains its own entity, never a fake canonical tag.
            identity = (("canonical", entry.canonical) if entry.canonical else
                        ("semantic", entry.semantic_id or "", entry.special_id or ""))
            grouped.setdefault(identity, []).append(entry)
        # Use the same ranking fields before constructing presentation records.
        # Retain all evidence in each group, but format only the returned top K.
        def rank(item):
            identity, group = item
            canonical = identity[1] if identity[0] == "canonical" else None
            is_special = bool(self._canonical_special_ids.get(canonical)) or any(
                entry.special_id for entry in group)
            count = self.knowledge.canonical[canonical].current_post_count if canonical else -1
            semantic_id = next((entry.semantic_id for entry in group if entry.semantic_id), "")
            return (min(_QUALITY[entry.match_type] for entry in group),
                    not is_special, -count, canonical or semantic_id)

        selected = nsmallest(limit, grouped.items(), key=rank)
        return tuple(self._result_for(group) for _, group in selected)

    def _result_for(self, entries: list[_Entry]) -> SearchResult:
        match_types = tuple(sorted({entry.match_type for entry in entries}, key=_QUALITY.__getitem__))
        match_type = match_types[0]
        canonical = next((entry.canonical for entry in entries if entry.canonical), None)
        semantic_ids = tuple(dict.fromkeys(entry.semantic_id for entry in entries if entry.semantic_id))
        special_ids = list(self._canonical_special_ids.get(canonical, ()) if canonical else ())
        special_ids.extend(entry.special_id for entry in entries if entry.special_id)
        special_ids = list(dict.fromkeys(special_ids))
        relations = tuple(self._semantic_relation(semantic_id) for semantic_id in semantic_ids)
        provenance = tuple(dict.fromkeys(entry.provenance for entry in entries))
        if canonical is None:
            japanese = tuple(self.knowledge.special[sid].japanese for sid in special_ids)
            return SearchResult(None, None, tuple(dict.fromkeys(japanese)), None, None,
                                bool(special_ids), tuple(special_ids), match_type, match_types,
                                "Semantic", provenance, relations)
        tag = self.knowledge.canonical[canonical]
        japanese = self._japanese_for(canonical, special_ids)
        group = "Exact" if _QUALITY[match_type] < 4 else (
            "Special" if special_ids else "All Danbooru")
        return SearchResult(canonical, PromptFormatter.format_tag(tag).text, japanese,
                            tag.category, tag.current_post_count, bool(special_ids),
                            tuple(special_ids), match_type, match_types, group,
                            provenance, relations)

    def _japanese_for(self, canonical: str, special_ids: list[str]) -> tuple[str, ...]:
        values = [self.knowledge.special[sid].japanese for sid in special_ids]
        display = self.knowledge.japanese_overlay.display_by_canonical.get(canonical)
        if display:
            values.append(display)
        values.extend(item.japanese for item in self.knowledge.translations
                      if item.canonical_tag == canonical)
        return tuple(dict.fromkeys(value for value in values if value))

    def _semantic_relation(self, semantic_id: str) -> SemanticRelation:
        item = self.knowledge.semantic[semantic_id]
        route = self.knowledge.semantic_routes.get(item.special_id)
        return SemanticRelation(item.semantic_id, item.semantic_term, item.candidate_canonical,
                                item.relation_type, item.review_status,
                                route.semantic_subtype if route else "",
                                route.anchor_kind if route else "",
                                route.anchor_value if route else "",
                                route.default_prompt_mode if route else "")
