"""Ordered in-memory selection and minimal prompt preview for Stage 7A."""
from __future__ import annotations

from .prompt_formatter import PromptFormatter


class Stage7ASession:
    def __init__(self, knowledge, warning_presenter):
        self.knowledge = knowledge
        self.warning_presenter = warning_presenter
        self._special_ids: list[str] = []
        self._auxiliary_canonicals: list[str] = []

    @property
    def selected_special_ids(self) -> tuple[str, ...]:
        return tuple(self._special_ids)

    @property
    def manual_auxiliary_canonicals(self) -> tuple[str, ...]:
        return tuple(self._auxiliary_canonicals)

    def statistics_core_canonicals(self) -> tuple[str, ...] | None:
        """Return a complete statistics identity, or None when unavailable.

        Ambiguous Alias and Semantic-only Specials intentionally do not become
        a partial recommendation query.  The Prompt still retains their
        original Special identity through ``prompt_preview``.
        """
        canonicals = []
        for special_id in self._special_ids:
            chosen = self.knowledge.special[special_id].statistics_canonical
            if not chosen:
                return None
            canonicals.append(chosen)
        return tuple(canonicals) if canonicals else None

    @property
    def automatic_injections(self) -> tuple:
        return ()

    def add_special(self, special_id: str) -> bool:
        if special_id not in self.knowledge.special:
            raise KeyError(special_id)
        if special_id in self._special_ids:
            return False
        self._special_ids.append(special_id)
        return True

    def remove_special(self, special_id: str) -> bool:
        if special_id not in self._special_ids:
            return False
        self._special_ids.remove(special_id)
        return True

    def add_auxiliary(self, canonical: str) -> bool:
        if canonical not in self.knowledge.canonical:
            raise KeyError(canonical)
        if canonical in self._auxiliary_canonicals:
            return False
        self._auxiliary_canonicals.append(canonical)
        return True

    def remove_auxiliary(self, canonical: str) -> bool:
        if canonical not in self._auxiliary_canonicals:
            return False
        self._auxiliary_canonicals.remove(canonical)
        return True

    @property
    def prompt_preview(self) -> str:
        parts = [PromptFormatter.format_special(self.knowledge.special[sid]).text
                 for sid in self._special_ids]
        parts.extend(PromptFormatter.format_tag(self.knowledge.canonical[canonical]).text
                     for canonical in self._auxiliary_canonicals)
        return ", ".join(parts)

    @property
    def clipboard_text(self) -> str:
        return self.prompt_preview

    @property
    def warnings(self):
        return self.warning_presenter.notices(self._special_ids)
