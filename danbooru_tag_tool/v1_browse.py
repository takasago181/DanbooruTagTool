"""Browse providers for the Issue #66 v1 application shell."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .knowledge import TagKnowledgeCore
from .normalization import normalize_lookup
from .prompt_formatter import PromptFormatter


@dataclass(frozen=True, slots=True)
class BrowseEntry:
    item_id: str
    japanese: str
    english: str
    canonical: str | None
    source: str
    category: str = ""


class BrowseProvider(Protocol):
    @property
    def available(self) -> bool: ...

    @property
    def status_text(self) -> str: ...

    def categories(self) -> tuple[str, ...]: ...

    def browse(self, *, category: str = "", query: str = "", limit: int = 200) -> tuple[BrowseEntry, ...]: ...


class SpecialBrowseProvider:
    """Read-only browse view over the accepted Special dictionary."""

    def __init__(self, knowledge: TagKnowledgeCore):
        self.knowledge = knowledge

    @property
    def available(self) -> bool:
        return True

    @property
    def status_text(self) -> str:
        return "Special Core Dictionary"

    def categories(self) -> tuple[str, ...]:
        values = {self._category(tag) for tag in self.knowledge.special.values()}
        return tuple(sorted(value for value in values if value))

    def browse(self, *, category: str = "", query: str = "", limit: int = 200) -> tuple[BrowseEntry, ...]:
        if limit < 1:
            raise ValueError("limit must be positive")
        key = normalize_lookup(query)
        rows: list[BrowseEntry] = []
        for special in self.knowledge.special.values():
            if not self.knowledge.product_fit.allows(special.special_id, "search"):
                continue
            item_category = self._category(special)
            if category and category != item_category:
                continue
            if key:
                haystacks = (special.term, special.japanese, special.description, *special.search_keys)
                if not any(key in normalize_lookup(value) for value in haystacks if value):
                    continue
            rows.append(BrowseEntry(
                special.special_id,
                special.japanese,
                PromptFormatter.format_special(special).text,
                special.chosen_canonical,
                "Special",
                item_category,
            ))
        rows.sort(key=lambda row: (normalize_lookup(row.japanese), row.english, row.item_id))
        return tuple(rows[:limit])

    @staticmethod
    def _category(special) -> str:
        return special.main_category or special.source_category or special.layer


class PendingGeneralBrowseProvider:
    """Stable v1 boundary for the parallel Issue #64 accepted sidecar.

    Issue #66 must not invent or edit #64 classification data. The app can ship
    this provider now and replace it with a sidecar-backed implementation later.
    """

    @property
    def available(self) -> bool:
        return False

    @property
    def status_text(self) -> str:
        return "General browse は Issue #64 の accepted sidecar 待ちです。検索は利用できます。"

    def categories(self) -> tuple[str, ...]:
        return ()

    def browse(self, *, category: str = "", query: str = "", limit: int = 200) -> tuple[BrowseEntry, ...]:
        if limit < 1:
            raise ValueError("limit must be positive")
        return ()
