"""Stage9C local Composer session and Stage9D reversible variant boundary."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .prompt_composer import ComposerInput, ComposerProfile, PromptComposer
from .stage8a_semantics import DecoratedRecommendationCandidate
from .stage9b_runtime import (
    SelectionDecision,
    Stage9BRuntime,
    Stage9BSelectionState,
    cooccurrence_candidate,
    semantic_auxiliary_candidate,
)


@dataclass(frozen=True, slots=True)
class ComposerVariant:
    """A named, reversible Stage10 comparison input; it declares no winner."""
    variant_id: str
    profile: ComposerProfile
    comparison_metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self):
        if not self.variant_id:
            raise ValueError("Composer variant requires a stable identity")


class Stage9ComposerSession:
    """Local UI-facing state: Core, candidate review, preview, and copy."""
    def __init__(self, knowledge, warning_presenter, support):
        self.knowledge = knowledge
        self.warning_presenter = warning_presenter
        self.runtime = Stage9BRuntime(PromptComposer(knowledge, support))
        self._special_ids: list[str] = []
        self._manual_auxiliary: list[str] = []
        self._semantic_auxiliary = ()
        self._cooccurrence = ()
        self._selection_state = Stage9BSelectionState()
        self._variant = ComposerVariant("stage9_baseline", ComposerProfile())
        self._last_result = None

    @property
    def selected_special_ids(self):
        return tuple(self._special_ids)

    @property
    def manual_auxiliary_canonicals(self):
        return tuple(self._manual_auxiliary)

    @property
    def selection_state(self):
        return self._selection_state

    @property
    def active_variant(self):
        return self._variant

    @property
    def automatic_injections(self):
        return ()

    def set_variant(self, variant: ComposerVariant):
        self._variant = variant
        self._last_result = None

    def add_special(self, special_id):
        if special_id not in self.knowledge.special:
            raise KeyError(special_id)
        if special_id in self._special_ids:
            return False
        self._special_ids.append(special_id)
        self._last_result = None
        return True

    def remove_special(self, special_id):
        if special_id not in self._special_ids:
            return False
        self._special_ids.remove(special_id)
        self._last_result = None
        return True

    def add_auxiliary(self, canonical):
        if canonical not in self.knowledge.canonical:
            raise KeyError(canonical)
        if canonical in self._manual_auxiliary:
            return False
        self._manual_auxiliary.append(canonical)
        self._last_result = None
        return True

    def remove_auxiliary(self, canonical):
        if canonical not in self._manual_auxiliary:
            return False
        self._manual_auxiliary.remove(canonical)
        self._last_result = None
        return True

    def set_discovered_candidates(self, decorated: Iterable[DecoratedRecommendationCandidate], *, snapshot_id=None):
        """Register existing UI candidates in both independent review lanes."""
        decorated = tuple(decorated)
        self._semantic_auxiliary = tuple(semantic_auxiliary_candidate(item) for item in decorated)
        self._cooccurrence = tuple(cooccurrence_candidate(item.candidate, snapshot_id=snapshot_id)
                                   for item in decorated)
        self._last_result = None

    def choose_candidate(self, candidate_id, state, reason="user explicit choice"):
        known = {item.candidate_id for item in (*self._semantic_auxiliary, *self._cooccurrence)}
        if candidate_id not in known:
            raise KeyError(candidate_id)
        self._selection_state = self._selection_state.with_decision(
            SelectionDecision(candidate_id, state, reason)
        )
        self._last_result = None

    def include_cooccurrence(self, canonical, reason="user selected co-occurrence suggestion"):
        self.choose_candidate(f"cooccurrence:{canonical}", "INCLUDE", reason)

    def statistics_core_canonicals(self):
        canonicals = []
        for special_id in self._special_ids:
            canonical = self.knowledge.special[special_id].statistics_canonical
            if not canonical:
                return None
            canonicals.append(canonical)
        return tuple(canonicals) if canonicals else None

    def _compose(self):
        inputs = tuple(ComposerInput(f"manual:{canonical}", canonical=canonical)
                       for canonical in self._manual_auxiliary)
        self._last_result = self.runtime.compose(
            self.selected_special_ids,
            semantic_auxiliary=self._semantic_auxiliary,
            cooccurrence=self._cooccurrence,
            selection_state=self._selection_state,
            inputs=inputs,
            profile=self._variant.profile,
            model_family=self._variant.profile.model_family,
        )
        return self._last_result

    @property
    def compose_result(self):
        return self._last_result or self._compose()

    @property
    def prompt_preview(self):
        return self.compose_result.positive_prompt

    @property
    def clipboard_text(self):
        return self.prompt_preview

    @property
    def provenance_map(self):
        return self.compose_result.provenance_map

    @property
    def composer_warnings(self):
        return self.compose_result.warnings

    @property
    def warnings(self):
        return self.warning_presenter.notices(self._special_ids)
