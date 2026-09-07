"""Stage9B adapters for existing auxiliary candidate lanes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

from .prompt_composer import ComposerInput, ComposeResult, PromptComposer
from .recommendations import RecommendationCandidate
from .stage8a_semantics import DecoratedRecommendationCandidate

Selection = Literal["INCLUDE", "EXCLUDE"]
RUNTIME_LANES = frozenset({"SEMANTIC_AUX", "COOCCURRENCE"})
ROLE_BLOCKS = {
    "SUBJECT_BASIC": "SUPPORT_STRUCTURE", "BODY_PART": "SUPPORT_STRUCTURE",
    "IMPLEMENT": "SUPPORT_STRUCTURE", "ACTION_SUPPORT": "SUPPORT_STRUCTURE",
    "STATE_REACTION": "SUPPORT_STRUCTURE", "POSE": "POSE_COMPOSITION",
    "CAMERA_COMPOSITION": "POSE_COMPOSITION", "APPEARANCE_CLOTHING": "GENERAL_AUX",
    "SITUATION_RELATION": "GENERAL_AUX", "UNCLASSIFIED": "GENERAL_AUX",
}


def _statistics_evidence(candidate: RecommendationCandidate, snapshot_id: str | None):
    """Copy raw Stage6 facts exactly; no score is calculated or combined."""
    evidence = (
        ("base_count", candidate.base_count), ("co_count", candidate.co_count),
        ("conditional_rate", candidate.conditional_rate),
        ("runtime_global_count", candidate.runtime_global_count),
        ("global_rate", candidate.global_rate), ("raw_lift", candidate.raw_lift),
        ("wilson_lower_bound", candidate.wilson_lower_bound),
        ("shrunk_lift", candidate.shrunk_lift),
    )
    return evidence if snapshot_id is None else (*evidence, ("snapshot_id", snapshot_id))


@dataclass(frozen=True, slots=True)
class LaneCandidate:
    """A classified candidate ready for the Composer, not a ranking type."""
    candidate_id: str
    canonical: str
    lane: str
    block: str
    provenance: tuple[str, ...]
    evidence: tuple[tuple[str, str | int | float], ...]
    reason: str

    def __post_init__(self):
        if not self.candidate_id or not self.canonical or self.lane not in RUNTIME_LANES:
            raise ValueError("Lane candidate requires stable identity, canonical, and supported lane")
        if self.block not in {"SUPPORT_STRUCTURE", "POSE_COMPOSITION", "GENERAL_AUX", "BACKGROUND_LIGHT"}:
            raise ValueError("Lane candidate requires an explicit non-Special Composer block")
        if not self.reason:
            raise ValueError("Lane candidate reason is required")


@dataclass(frozen=True, slots=True)
class SelectionDecision:
    """A user decision keyed by stable candidate identity, never rank position."""
    candidate_id: str
    state: Selection
    reason: str = "user explicit choice"

    def __post_init__(self):
        if not self.candidate_id or self.state not in {"INCLUDE", "EXCLUDE"}:
            raise ValueError("Selection decision requires identity and INCLUDE or EXCLUDE")
        if not self.reason:
            raise ValueError("Selection decision reason is required")


@dataclass(frozen=True, slots=True)
class Stage9BSelectionState:
    """Persistable value object callers retain across recompose calls."""
    decisions: tuple[SelectionDecision, ...] = ()

    def __post_init__(self):
        if len({item.candidate_id for item in self.decisions}) != len(self.decisions):
            raise ValueError("Only one final selection decision is allowed per candidate")

    def decision_for(self, candidate_id: str) -> SelectionDecision | None:
        return next((item for item in self.decisions if item.candidate_id == candidate_id), None)

    def with_decision(self, decision: SelectionDecision) -> "Stage9BSelectionState":
        return Stage9BSelectionState((*tuple(item for item in self.decisions
                                               if item.candidate_id != decision.candidate_id), decision))


def semantic_auxiliary_candidate(decorated: DecoratedRecommendationCandidate, *, candidate_id: str | None = None) -> LaneCandidate:
    """Adapt an existing Stage8A classified candidate; never infer from tag text."""
    role = decorated.semantic_role
    if role not in ROLE_BLOCKS:
        raise ValueError(f"Unsupported approved semantic role: {role!r}")
    candidate = decorated.candidate
    provenance = ["stage8a_semantics", f"semantic_role:{role}"]
    if decorated.semantic_label_ja:
        provenance.append(f"semantic_label:{decorated.semantic_label_ja}")
    provenance.extend(f"relation_flag:{flag}" for flag in decorated.relation_flags)
    evidence = list(_statistics_evidence(candidate, None))
    evidence.append(("semantic_role", role))
    if decorated.generation_hint_kind:
        evidence.append(("generation_hint_kind", decorated.generation_hint_kind))
    evidence.extend(("evidence_note_kind", kind) for kind in decorated.evidence_note_kinds)
    return LaneCandidate(
        candidate_id or f"semantic_aux:{candidate.canonical}", candidate.canonical,
        "SEMANTIC_AUX", ROLE_BLOCKS[role], tuple(provenance), tuple(evidence),
        f"semantic/search auxiliary from approved role: {role}",
    )


def cooccurrence_candidate(candidate: RecommendationCandidate, *, snapshot_id: str | None = None,
                            candidate_id: str | None = None, block: str = "GENERAL_AUX") -> LaneCandidate:
    """Adapt one true-AND Stage6 candidate as a default-off suggestion."""
    return LaneCandidate(
        candidate_id or f"cooccurrence:{candidate.canonical}", candidate.canonical,
        "COOCCURRENCE", block, ("stage6_true_and_cooccurrence",),
        _statistics_evidence(candidate, snapshot_id),
        "true-AND co-occurrence suggestion; user choice required",
    )


class Stage9BRuntime:
    """Connect discovered lanes to Stage9A without changing their ranks or scores."""
    def __init__(self, composer: PromptComposer):
        self.composer = composer

    @staticmethod
    def _inputs(candidates: Iterable[LaneCandidate], state: Stage9BSelectionState) -> tuple[ComposerInput, ...]:
        candidates = tuple(candidates)
        if len({item.candidate_id for item in candidates}) != len(candidates):
            raise ValueError("Lane candidate identities must be unique")
        result = []
        for candidate in candidates:
            decision = state.decision_for(candidate.candidate_id)
            result.append(ComposerInput(
                input_id=candidate.candidate_id, canonical=candidate.canonical,
                block=candidate.block, lane=candidate.lane,
                selected=(decision.state == "INCLUDE" if decision else False),
                provenance=candidate.provenance, evidence=candidate.evidence,
                reason=decision.reason if decision else candidate.reason,
            ))
        return tuple(result)

    def compose(self, selected_special_ids, *, semantic_auxiliary: Iterable[LaneCandidate] = (),
                cooccurrence: Iterable[LaneCandidate] = (),
                selection_state: Stage9BSelectionState = Stage9BSelectionState(),
                inputs: tuple[ComposerInput, ...] = (), **compose_kwargs) -> ComposeResult:
        semantic_auxiliary, cooccurrence = tuple(semantic_auxiliary), tuple(cooccurrence)
        if any(item.lane != "SEMANTIC_AUX" for item in semantic_auxiliary):
            raise ValueError("semantic_auxiliary accepts only SEMANTIC_AUX lane candidates")
        if any(item.lane != "COOCCURRENCE" for item in cooccurrence):
            raise ValueError("cooccurrence accepts only COOCCURRENCE lane candidates")
        return self.composer.compose(
            selected_special_ids,
            inputs=(*self._inputs((*semantic_auxiliary, *cooccurrence), selection_state), *inputs),
            **compose_kwargs,
        )
