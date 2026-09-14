"""Stage 6 raw co-occurrence statistics, transparent ranking, and diagnostics.

Scores only determine presentation order.  The counts and rates on each
candidate always remain the unmodified values from the statistics snapshot.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from time import perf_counter
from typing import Iterable, Literal, Mapping

from .models import AUXILIARY_ROLES


RankingMethod = Literal["conditional_rate", "raw_lift", "wilson_lower_bound", "shrunk_lift"]
RANKING_METHODS: tuple[RankingMethod, ...] = (
    "conditional_rate", "raw_lift", "wilson_lower_bound", "shrunk_lift",
)
WILSON_Z = 1.959963984540054
DEFAULT_SHRINKAGE_PRIOR = 20.0


@dataclass(frozen=True, slots=True)
class RecommendationCandidate:
    """One current-General auxiliary candidate and its snapshot-consistent facts."""
    canonical: str
    role: str
    base_count: int
    co_count: int
    conditional_rate: float
    runtime_global_count: int
    global_rate: float
    raw_lift: float
    wilson_lower_bound: float
    shrunk_lift: float

    def score(self, method: RankingMethod) -> float:
        return float(getattr(self, method))


@dataclass(frozen=True, slots=True)
class DropOneDiagnostic:
    canonical: str
    full_base_count: int
    without_base_count: int


@dataclass(frozen=True, slots=True)
class CombinationSpecificity:
    canonical: str
    full_conditional_rate: float
    singleton_conditional_rates: tuple[tuple[str, float], ...]


def wilson_lower_bound(successes: int, trials: int, *, z: float = WILSON_Z) -> float:
    if trials < 0 or successes < 0 or successes > trials:
        raise ValueError("successes must be between zero and trials")
    if trials == 0:
        return 0.0
    rate = successes / trials
    z2 = z * z
    result = (rate + z2 / (2 * trials) - z * sqrt((rate * (1 - rate) + z2 / (4 * trials)) / trials)) / (1 + z2 / trials)
    # Floating point cancellation can produce an insignificant positive value
    # for 0/n; the mathematical lower bound is exactly zero.
    return 0.0 if successes == 0 else result


def support_aware_shrunk_lift(co_count: int, base_count: int, global_rate: float,
                               *, prior_strength: float = DEFAULT_SHRINKAGE_PRIOR) -> float:
    """Beta-prior conditional rate divided by the unmodified global rate."""
    if base_count < 0 or co_count < 0 or co_count > base_count or global_rate < 0:
        raise ValueError("invalid count/rate")
    if base_count == 0 or global_rate == 0:
        return 0.0
    if prior_strength < 0:
        raise ValueError("prior_strength must be non-negative")
    posterior_rate = (co_count + prior_strength * global_rate) / (base_count + prior_strength)
    return posterior_rate / global_rate


class RecommendationEngine:
    """Calculates logical-canonical recommendations over a Stage 5 overlay."""

    def __init__(self, overlay, knowledge, *, roles: Mapping[str, str] | None = None,
                 shrinkage_prior: float = DEFAULT_SHRINKAGE_PRIOR):
        self.overlay = overlay
        self.knowledge = knowledge
        self.roles = dict(roles or {})
        if any(role not in AUXILIARY_ROLES for role in self.roles.values()):
            raise ValueError("Unknown auxiliary role")
        if shrinkage_prior < 0:
            raise ValueError("shrinkage_prior must be non-negative")
        self.shrinkage_prior = shrinkage_prior

    def _current_general(self, canonical: str) -> bool:
        tag = self.knowledge.canonical.get(canonical)
        return tag is not None and tag.category == 0 and bool(self.overlay.source_tag_ids(canonical))

    def candidates(self, core_canonicals: Iterable[str]) -> tuple[RecommendationCandidate, ...]:
        core = tuple(dict.fromkeys(core_canonicals))
        if not core:
            raise ValueError("At least one Core canonical is required")
        if not all(self._current_general(tag) for tag in core):
            raise ValueError("Core must contain current General canonicals available in the overlay")
        base = self.overlay.intersect(core)
        base_count = base.base_count
        if not base_count:
            return ()
        counts = self.overlay.aggregate(base, exclude=core)
        total_posts = self.overlay.index.total_posts
        result = []
        for canonical, co_count in counts.items():
            # raw-only, non-General, ambiguous, and semantic identities remain
            # in overlay data but are intentionally not normal recommendations.
            if not self._current_general(canonical):
                continue
            runtime_global_count = self.overlay.global_count(canonical)
            global_rate = runtime_global_count / total_posts
            conditional_rate = co_count / base_count
            raw_lift = conditional_rate / global_rate if global_rate else 0.0
            result.append(RecommendationCandidate(
                canonical=canonical, role=self.roles.get(canonical, "other"),
                base_count=base_count, co_count=co_count,
                conditional_rate=conditional_rate, runtime_global_count=runtime_global_count,
                global_rate=global_rate, raw_lift=raw_lift,
                wilson_lower_bound=wilson_lower_bound(co_count, base_count),
                shrunk_lift=support_aware_shrunk_lift(
                    co_count, base_count, global_rate, prior_strength=self.shrinkage_prior),
            ))
        return tuple(result)

    @staticmethod
    def rank(candidates: Iterable[RecommendationCandidate], method: RankingMethod) -> tuple[RecommendationCandidate, ...]:
        if method not in RANKING_METHODS:
            raise ValueError("Unknown ranking method")
        return tuple(sorted(candidates, key=lambda item: (-item.score(method), -item.co_count, item.canonical)))

    def drop_one(self, core_canonicals: Iterable[str]) -> tuple[DropOneDiagnostic, ...]:
        core = tuple(dict.fromkeys(core_canonicals))
        if not core:
            raise ValueError("At least one Core canonical is required")
        full = self.overlay.intersect(core).base_count
        return tuple(DropOneDiagnostic(
            canonical=tag, full_base_count=full,
            without_base_count=(self.overlay.intersect(core[:index] + core[index + 1:]).base_count if len(core) > 1
                                else self.overlay.index.total_posts),
        ) for index, tag in enumerate(core))

    def combination_specificity(self, core_canonicals: Iterable[str], candidate: RecommendationCandidate | str) -> CombinationSpecificity:
        core = tuple(dict.fromkeys(core_canonicals))
        target = candidate.canonical if isinstance(candidate, RecommendationCandidate) else candidate
        full_base = self.overlay.intersect(core)
        full_rate = 0.0 if not full_base.base_count else self._co_count(full_base, target) / full_base.base_count
        singletons = []
        for core_tag in core:
            base = self.overlay.intersect([core_tag])
            rate = 0.0 if not base.base_count else self._co_count(base, target) / base.base_count
            singletons.append((core_tag, rate))
        return CombinationSpecificity(target, full_rate, tuple(singletons))

    def _co_count(self, base, target: str) -> int:
        # Canonical posting intersection is exact and avoids candidate-policy
        # filtering for diagnostics.
        return int(__import__("numpy").intersect1d(base.post_ordinals, self.overlay.canonical_postings(target), assume_unique=True).size)

    def timed_candidates(self, core_canonicals: Iterable[str]) -> tuple[tuple[RecommendationCandidate, ...], float]:
        started = perf_counter()
        result = self.candidates(core_canonicals)
        return result, (perf_counter() - started) * 1000
