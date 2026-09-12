"""Stage9C local Composer session and Stage9D reversible variant boundary."""
from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite
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
class WeightVariant:
    """Explicit model-scoped rendering supplied by the experiment caller."""
    canonical: str
    weight: float
    rendered_text: str

    def __post_init__(self):
        if not self.canonical or not isfinite(self.weight) or self.weight <= 0:
            raise ValueError("Weight requires a canonical and a finite positive value")
        if not self.rendered_text.strip():
            raise ValueError("Weight rendering must be supplied; grammar is not inferred")


@dataclass(frozen=True, slots=True)
class ComposerVariant:
    """A named, reversible Stage10 comparison input; it declares no winner."""
    variant_id: str
    profile: ComposerProfile
    comparison_metadata: tuple[tuple[str, str], ...] = ()
    broad_generic_support: tuple[ComposerInput, ...] = ()
    broad_generic_count: int = 0
    role_density_variant: str = "baseline"
    role_density_inputs: tuple[ComposerInput, ...] = ()
    weight_variant: tuple[WeightVariant, ...] = ()
    lora_inputs: tuple[ComposerInput, ...] = ()
    lora_contraction_variant: str = "none"
    lora_contraction_excluded_input_ids: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.variant_id:
            raise ValueError("Composer variant requires a stable identity")
        if self.broad_generic_count not in (0, 1, 2):
            raise ValueError("Broad generic count must be 0, 1, or 2")
        if self.broad_generic_count > len(self.broad_generic_support):
            raise ValueError("Explicit broad generic candidates are required")
        if not self.role_density_variant or not self.lora_contraction_variant:
            raise ValueError("Variant labels must be explicit")
        if any(item.canonical is None or item.block in {"SPECIAL", "LORA"}
               for item in (*self.broad_generic_support, *self.role_density_inputs)):
            raise ValueError("Support variants require explicitly classified canonical inputs")
        if any(item.block != "LORA" for item in self.lora_inputs):
            raise ValueError("LoRA inputs must remain in the LoRA block")
        if len({item.canonical for item in self.weight_variant}) != len(self.weight_variant):
            raise ValueError("Duplicate weight canonical")
        if self.weight_variant and self.profile.model_family == "GENERIC":
            raise ValueError("Explicit weight grammar requires a model-family profile")
        if self.lora_contraction_excluded_input_ids and (
                not self.lora_inputs or self.lora_contraction_variant == "none"):
            raise ValueError("Contraction requires an explicit variant and LoRA inputs")


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
        if not self.knowledge.product_fit.allows(special_id, 'selection'):
            raise ValueError('Special is retained for historical inspection only')
        if special_id in self._special_ids:
            return False
        self._special_ids.append(special_id)
        self.set_candidate_buckets()
        self._last_result = None
        return True

    def remove_special(self, special_id):
        if special_id not in self._special_ids:
            return False
        self._special_ids.remove(special_id)
        self.set_candidate_buckets()
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
        if self.has_cooccurrence(canonical):
            self.choose_candidate(f"cooccurrence:{canonical}", "EXCLUDE")
        self._last_result = None
        return True

    def set_discovered_candidates(self, decorated: Iterable[DecoratedRecommendationCandidate], *, snapshot_id=None):
        """Register existing UI candidates in both independent review lanes."""
        decorated = tuple(decorated)
        # Validate/build both lanes before committing either one. Invalid input
        # must leave the last usable result and user decisions intact.
        for item in decorated:
            if item.candidate.canonical not in self.knowledge.canonical:
                raise KeyError(item.candidate.canonical)
        decorated = tuple(item for item in decorated if self.knowledge.product_fit.canonical_allows(
            item.candidate.canonical, 'recommendation'))
        semantic = tuple(semantic_auxiliary_candidate(item) for item in decorated)
        cooccurrence = tuple(cooccurrence_candidate(item.candidate, snapshot_id=snapshot_id)
                             for item in decorated)
        self._semantic_auxiliary, self._cooccurrence = semantic, cooccurrence
        self._last_result = None

    def choose_candidate(self, candidate_id, state, reason="user explicit choice"):
        known = {item.candidate_id for item in (*self._semantic_auxiliary, *self._cooccurrence)}
        if candidate_id not in known:
            raise KeyError(candidate_id)
        self._selection_state = self._selection_state.with_decision(
            SelectionDecision(candidate_id, state, reason)
        )
        self._last_result = None

    def set_candidate_buckets(self, common=(), rare=(), *, snapshot_id=None):
        """Replace the complete result atomically; common wins identical duplicates."""
        combined = {}
        for item in (*tuple(common), *tuple(rare)):
            combined.setdefault(item.candidate.canonical, item)
        self.set_discovered_candidates(combined.values(), snapshot_id=snapshot_id)

    def has_cooccurrence(self, canonical):
        return any(item.canonical == canonical for item in self._cooccurrence)

    def include_cooccurrence(self, canonical, reason="user selected co-occurrence suggestion"):
        self.choose_candidate(f"cooccurrence:{canonical}", "INCLUDE", reason)

    def statistics_core_canonicals(self):
        canonicals = []
        for special_id in self._special_ids:
            if not self.knowledge.product_fit.allows(special_id, 'statistics'):
                return None
            canonical = self.knowledge.special[special_id].statistics_canonical
            if not canonical:
                return None
            canonicals.append(canonical)
        return tuple(canonicals) if canonicals else None

    def _compose(self):
        inputs = tuple(ComposerInput(f"manual:{canonical}", canonical=canonical)
                       for canonical in self._manual_auxiliary)
        variant = self._variant
        # Callers supply the exact support sets for density comparisons. There
        # is no guessed role, density threshold, winning weight, or LoRA rule.
        additions = (*variant.broad_generic_support[:variant.broad_generic_count],
                     *variant.role_density_inputs, *variant.lora_inputs)
        inputs = (*inputs, *(replace(item, selected=True) for item in additions))
        excluded = set(variant.lora_contraction_excluded_input_ids)
        if excluded - {item.input_id for item in inputs if item.block != "LORA"}:
            raise ValueError("Contraction can only address explicit non-LoRA inputs")
        inputs = tuple(item for item in inputs if item.input_id not in excluded)
        result = self.runtime.compose(
            self.selected_special_ids,
            semantic_auxiliary=self._semantic_auxiliary,
            cooccurrence=self._cooccurrence,
            selection_state=self._selection_state,
            inputs=inputs,
            profile=self._variant.profile,
            model_family=self._variant.profile.model_family,
        )
        if variant.weight_variant:
            weights = {self.runtime.composer._canonical(item.canonical): item
                       for item in variant.weight_variant}
            selected = []
            for atom in result.plan.selected_atoms:
                rule = weights.pop(atom.canonical, None)
                if rule:
                    if atom.special_owners:
                        raise ValueError("Support weighting cannot replace a Special token")
                    atom = replace(atom, text=rule.rendered_text, weight=rule.weight)
                selected.append(atom)
            if weights:
                raise ValueError("Weight target must be a rendered canonical support")
            if len({atom.text for atom in selected}) != len(selected):
                raise ValueError("Explicit weight rendering must not collide")
            selected = tuple(selected)
            plan = replace(result.plan, selected_atoms=selected)
            result = replace(
                result, plan=plan,
                positive_blocks=tuple((block, tuple(a for a in selected if a.block == block))
                                      for block in result.block_order),
                positive_prompt=", ".join(a.text for a in selected),
                provenance_map={a.text: a for a in selected},
            )
        self._last_result = result
        return result

    def comparison_snapshot(self):
        """Capture all reversible conditions together with the actual Prompt."""
        return self._variant, self.compose_result

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
