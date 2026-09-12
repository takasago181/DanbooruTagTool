"""Visible-state prompt workspace for the Issue #66 v1 application."""
from __future__ import annotations

from dataclasses import dataclass, replace

from .knowledge import TagKnowledgeCore
from .normalization import split_prompt_input
from .prompt_formatter import PromptFormatter
from .search import SearchResult
from .v1_browse import BrowseEntry


@dataclass(frozen=True, slots=True)
class PromptItem:
    item_id: str
    japanese: str
    english: str
    canonical: str | None
    special_id: str | None
    source: str
    original_text: str
    resolved: bool


class PromptWorkspace:
    """Authoritative visible prompt state.

    No support tag is inserted unless it is represented by a PromptItem. Preview
    and clipboard text are derived only from ``items`` and therefore always match
    what the user can see, delete, and reorder.
    """

    def __init__(self, knowledge: TagKnowledgeCore):
        self.knowledge = knowledge
        self._items: tuple[PromptItem, ...] = ()
        self._sequence = 0

    @property
    def items(self) -> tuple[PromptItem, ...]:
        return self._items

    @property
    def preview(self) -> str:
        return ", ".join(item.english for item in self._items if item.english)

    @property
    def clipboard_text(self) -> str:
        return self.preview

    def clear(self) -> None:
        self._items = ()

    def load_existing_prompt(self, text: str) -> tuple[PromptItem, ...]:
        items = tuple(self._resolve_existing(part) for part in split_prompt_input(text))
        self._items = items
        return items

    def add_search_result(self, result: SearchResult) -> PromptItem:
        if result.canonical is not None and result.prompt_representation:
            item = PromptItem(
                self._new_id("search"),
                result.japanese[0] if result.japanese else "",
                result.prompt_representation,
                result.canonical,
                result.special_ids[0] if len(result.special_ids) == 1 else None,
                "検索",
                result.canonical,
                True,
            )
        elif len(result.special_ids) == 1:
            return self.add_special(result.special_ids[0], source="検索")
        else:
            raise ValueError("This search result cannot be safely added to the prompt")
        return self._append(item)

    def add_browse_entry(self, entry: BrowseEntry) -> PromptItem:
        if entry.source == "Special":
            return self.add_special(entry.item_id, source="Special browse")
        item = PromptItem(
            self._new_id("browse"), entry.japanese, entry.english, entry.canonical,
            None, entry.source, entry.english, bool(entry.canonical),
        )
        return self._append(item)

    def add_special(self, special_id: str, *, source: str = "Special browse") -> PromptItem:
        special = self.knowledge.special[special_id]
        item = PromptItem(
            self._new_id("special"), special.japanese,
            PromptFormatter.format_special(special).text,
            special.chosen_canonical, special.special_id, source, special.term, True,
        )
        return self._append(item)

    def remove(self, item_id: str) -> None:
        self._items = tuple(item for item in self._items if item.item_id != item_id)

    def move(self, item_id: str, delta: int) -> bool:
        if delta not in {-1, 1}:
            raise ValueError("delta must be -1 or 1")
        index = next((i for i, item in enumerate(self._items) if item.item_id == item_id), None)
        if index is None:
            raise KeyError(item_id)
        target = index + delta
        if target < 0 or target >= len(self._items):
            return False
        items = list(self._items)
        items[index], items[target] = items[target], items[index]
        self._items = tuple(items)
        return True

    def replace_english(self, item_id: str, english: str) -> PromptItem:
        """Explicit user edit hook; still visible state, never hidden insertion."""
        cleaned = english.strip()
        if not cleaned:
            raise ValueError("english text required")
        for index, item in enumerate(self._items):
            if item.item_id == item_id:
                updated = replace(item, english=cleaned, source="手動編集")
                items = list(self._items)
                items[index] = updated
                self._items = tuple(items)
                return updated
        raise KeyError(item_id)

    def _resolve_existing(self, text: str) -> PromptItem:
        resolution = self.knowledge.resolve_exact(text)
        if len(resolution.canonical_candidates) == 1 and not resolution.semantic_ids:
            canonical = resolution.canonical_candidates[0]
            tag = self.knowledge.canonical[canonical]
            japanese = self._japanese_for(canonical, resolution.special_ids)
            return PromptItem(
                self._new_id("existing"), japanese,
                PromptFormatter.format_tag(tag).text, canonical,
                resolution.special_ids[0] if len(resolution.special_ids) == 1 else None,
                "既存Prompt", text, True,
            )
        if len(resolution.special_ids) == 1:
            special = self.knowledge.special[resolution.special_ids[0]]
            return PromptItem(
                self._new_id("existing-special"), special.japanese,
                PromptFormatter.format_special(special).text, special.chosen_canonical,
                special.special_id, "既存Prompt", text, True,
            )
        return PromptItem(
            self._new_id("existing-raw"), "未解決", text.strip(), None, None,
            "既存Prompt（未解決）", text, False,
        )

    def _japanese_for(self, canonical: str, special_ids: tuple[str, ...]) -> str:
        for special_id in special_ids:
            value = self.knowledge.special[special_id].japanese
            if value:
                return value
        overlay = self.knowledge.japanese_overlay.display_by_canonical.get(canonical)
        if overlay:
            return overlay
        for translation in self.knowledge.translations:
            if translation.canonical_tag == canonical and translation.japanese:
                return translation.japanese
        return ""

    def _append(self, item: PromptItem) -> PromptItem:
        self._items = (*self._items, item)
        return item

    def _new_id(self, prefix: str) -> str:
        self._sequence += 1
        return f"{prefix}:{self._sequence}"
