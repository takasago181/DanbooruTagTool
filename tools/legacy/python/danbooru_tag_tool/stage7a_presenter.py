"""UI-facing adapters that preserve Special identity over canonical search results."""
from __future__ import annotations

from dataclasses import dataclass

from .normalization import normalize_lookup
from .prompt_formatter import PromptFormatter


@dataclass(frozen=True, slots=True)
class SpecialSearchItem:
    special_id: str
    original_term: str
    japanese: str
    layer: str
    matched_canonical: str | None
    promotion_status: str | None
    generation_role: str | None
    prompt_use_mode: str | None
    match_reason: str
    parent_search_rank: int
    product_fit_verdict: str = 'KEEP'
    product_fit_label: str = ''


@dataclass(frozen=True, slots=True)
class GeneralSearchItem:
    canonical: str
    display_japanese: str | None
    prompt_text: str
    parent_search_rank: int


@dataclass(frozen=True, slots=True)
class SearchPresentation:
    special: tuple[SpecialSearchItem, ...]
    general: tuple[GeneralSearchItem, ...]


class SpecialSearchPresenter:
    """Expands canonical-deduplicated Stage 4 results into Special-ID cards."""

    def __init__(self, knowledge, search_engine, profile_store):
        self.knowledge = knowledge
        self.search_engine = search_engine
        self.profile_store = profile_store

    def search(self, query: str, *, limit: int = 50) -> SearchPresentation:
        results = self.search_engine.search_one(query, limit=limit, product_facing=True)
        special_items = []
        general_items = []
        seen_special_ids = set()
        for parent_rank, result in enumerate(results):
            parent_ids = sorted(
                result.special_ids,
                key=lambda sid: self._special_tie_break(query, sid),
            )
            for special_id in parent_ids:
                if special_id in seen_special_ids:
                    continue
                if not self.knowledge.product_fit.allows(special_id, 'search'):
                    continue
                seen_special_ids.add(special_id)
                special = self.knowledge.special[special_id]
                profile = self.profile_store.profiles.get(special_id)
                special_items.append(SpecialSearchItem(
                    special_id=special_id,
                    original_term=special.term,
                    japanese=special.japanese,
                    layer=special.layer,
                    matched_canonical=(result.canonical if self.knowledge.product_fit.allows(
                        special_id, 'statistics') else None),
                    promotion_status=profile.PromotionStatus if profile else None,
                    generation_role=(profile.GenerationRole or None) if profile else None,
                    prompt_use_mode=(profile.PromptUseMode or None) if profile else None,
                    match_reason=result.match_type,
                    parent_search_rank=parent_rank,
                    product_fit_verdict=self.knowledge.product_fit.verdict(special_id),
                    product_fit_label=self.knowledge.product_fit.label(special_id),
                ))
            if result.canonical is not None and not result.special_ids:
                display = self.knowledge.japanese_overlay.display_by_canonical.get(result.canonical)
                general_items.append(GeneralSearchItem(
                    canonical=result.canonical,
                    display_japanese=display,
                    prompt_text=PromptFormatter.format_tag(
                        self.knowledge.canonical[result.canonical]
                    ).text,
                    parent_search_rank=parent_rank,
                ))
        return SearchPresentation(tuple(special_items), tuple(general_items))

    def browse(self, *, limit: int = 50) -> tuple[SpecialSearchItem, ...]:
        """Default ID-based browse exposes only independent product choices."""
        if limit < 1:
            raise ValueError('limit must be positive')
        items = []
        for sid in sorted(self.knowledge.special, key=int):
            if not self.knowledge.product_fit.allows(sid, 'browse'):
                continue
            special = self.knowledge.special[sid]
            profile = self.profile_store.profiles.get(sid)
            items.append(SpecialSearchItem(
                sid, special.term, special.japanese, special.layer, special.chosen_canonical,
                profile.PromotionStatus if profile else None,
                (profile.GenerationRole or None) if profile else None,
                (profile.PromptUseMode or None) if profile else None,
                'browse', len(items), self.knowledge.product_fit.verdict(sid),
                self.knowledge.product_fit.label(sid)))
            if len(items) == limit:
                break
        return tuple(items)

    def _special_tie_break(self, query: str, special_id: str):
        key = normalize_lookup(query)
        special = self.knowledge.special[special_id]
        term_key = normalize_lookup(special.term)
        japanese_key = normalize_lookup(special.japanese)
        if key == term_key:
            quality = 0
        elif key == japanese_key:
            quality = 1
        elif term_key.startswith(key) or japanese_key.startswith(key):
            quality = 2
        else:
            quality = 3
        return quality, special_id
