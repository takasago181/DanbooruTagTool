"""Stage 8A deterministic meaning and generation-hint decoration.

The decorator adds display-only metadata to Stage 6 recommendation facts. It
does not filter, rank, copy, or mutate :class:`RecommendationCandidate`.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal

from .recommendations import RecommendationCandidate


SemanticRole = Literal[
    "SUBJECT_BASIC", "BODY_PART", "IMPLEMENT", "ACTION_SUPPORT", "POSE",
    "CAMERA_COMPOSITION", "STATE_REACTION", "APPEARANCE_CLOTHING",
    "SITUATION_RELATION", "UNCLASSIFIED",
]
RecommendationBucket = Literal["common", "rare"]

SEMANTIC_LABELS_JA: dict[str, str] = {
    "SUBJECT_BASIC": "人物・人数",
    "BODY_PART": "身体部位",
    "IMPLEMENT": "器具・物体",
    "ACTION_SUPPORT": "行為補強",
    "POSE": "姿勢・体位",
    "CAMERA_COMPOSITION": "構図・見せ方",
    "STATE_REACTION": "状態・反応",
    "APPEARANCE_CLOTHING": "外見・衣装",
    "SITUATION_RELATION": "状況・関係",
    "UNCLASSIFIED": "未分類",
}
VALID_SEMANTIC_ROLES = frozenset(SEMANTIC_LABELS_JA)
VALID_HINT_KINDS = frozenset({
    "CORE_BASIS", "BODY_TARGET", "IMPLEMENT_SPECIFIER", "ACTION_CLARIFIER",
    "POSE_GUIDE", "CAMERA_GUIDE", "STATE_EXPRESSION", "APPEARANCE_BASIS",
    "RELATION_BASIS", "INDIRECT_SUPPORT", "LOW_ADDITIONAL_VALUE",
    "DISCOVERY_CANDIDATE",
})
VALID_BUCKETS = frozenset({"common", "rare"})
LOW_SUPPORT_MAX_CO_COUNT = 2


@dataclass(frozen=True, slots=True)
class SemanticLabel:
    canonical_tag: str
    semantic_role: str
    source: str
    note: str


@dataclass(frozen=True, slots=True)
class GenerationHintRule:
    rule_id: str
    priority: int
    when_semantic_role: str | None
    when_same_stat_canonical: bool | None
    when_bucket: str | None
    when_low_support: bool | None
    kind: str
    message_ja: str
    source: str
    note: str

    def matches(self, *, semantic_role: str, same_stat_canonical: bool,
                bucket: str, low_support: bool) -> bool:
        return all((
            self.when_semantic_role is None or self.when_semantic_role == semantic_role,
            self.when_same_stat_canonical is None
            or self.when_same_stat_canonical is same_stat_canonical,
            self.when_bucket is None or self.when_bucket == bucket,
            self.when_low_support is None or self.when_low_support is low_support,
        ))


@dataclass(frozen=True, slots=True)
class DecoratedRecommendationCandidate:
    candidate: RecommendationCandidate
    semantic_role: str
    semantic_label_ja: str | None
    relation_flags: tuple[str, ...]
    generation_hint_kind: str | None
    generation_hint_ja: str | None
    evidence_note_kinds: tuple[str, ...]
    evidence_notes_ja: tuple[str, ...]


def _optional_bool(value: str, *, field: str, rule_id: str) -> bool | None:
    normalized = value.strip().lower()
    if not normalized:
        return None
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"{rule_id}: invalid {field}: {value!r}")


def load_semantic_labels(path: Path) -> dict[str, SemanticLabel]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        expected = ["canonical_tag", "semantic_role", "source", "note"]
        if reader.fieldnames != expected:
            raise ValueError(f"Invalid semantic label schema: {reader.fieldnames!r}")
        labels: dict[str, SemanticLabel] = {}
        for line, row in enumerate(reader, start=2):
            canonical = row["canonical_tag"].strip()
            role = row["semantic_role"].strip()
            if not canonical:
                raise ValueError(f"line {line}: canonical_tag is required")
            if role not in VALID_SEMANTIC_ROLES:
                raise ValueError(f"line {line}: invalid semantic_role: {role!r}")
            if canonical in labels:
                raise ValueError(f"line {line}: duplicate canonical_tag: {canonical}")
            labels[canonical] = SemanticLabel(
                canonical, role, row["source"].strip(), row["note"].strip()
            )
    return labels


def load_generation_hint_rules(path: Path) -> tuple[GenerationHintRule, ...]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        expected = [
            "rule_id", "priority", "when_semantic_role",
            "when_same_stat_canonical", "when_bucket", "when_low_support",
            "kind", "message_ja", "source", "note",
        ]
        if reader.fieldnames != expected:
            raise ValueError(f"Invalid generation hint schema: {reader.fieldnames!r}")
        rules = []
        rule_ids = set()
        for line, row in enumerate(reader, start=2):
            rule_id = row["rule_id"].strip()
            if not rule_id or rule_id in rule_ids:
                raise ValueError(f"line {line}: missing or duplicate rule_id: {rule_id!r}")
            role = row["when_semantic_role"].strip() or None
            if role is not None and role not in VALID_SEMANTIC_ROLES:
                raise ValueError(f"{rule_id}: invalid semantic role: {role!r}")
            bucket = row["when_bucket"].strip() or None
            if bucket is not None and bucket not in VALID_BUCKETS:
                raise ValueError(f"{rule_id}: invalid bucket: {bucket!r}")
            kind = row["kind"].strip()
            if kind not in VALID_HINT_KINDS:
                raise ValueError(f"{rule_id}: invalid hint kind: {kind!r}")
            message = row["message_ja"].strip()
            if not message:
                raise ValueError(f"{rule_id}: message_ja is required")
            try:
                priority = int(row["priority"])
            except ValueError as exc:
                raise ValueError(f"{rule_id}: priority must be an integer") from exc
            rules.append(GenerationHintRule(
                rule_id=rule_id,
                priority=priority,
                when_semantic_role=role,
                when_same_stat_canonical=_optional_bool(
                    row["when_same_stat_canonical"],
                    field="when_same_stat_canonical", rule_id=rule_id,
                ),
                when_bucket=bucket,
                when_low_support=_optional_bool(
                    row["when_low_support"], field="when_low_support", rule_id=rule_id,
                ),
                kind=kind,
                message_ja=message,
                source=row["source"].strip(),
                note=row["note"].strip(),
            ))
            rule_ids.add(rule_id)
    return tuple(sorted(rules, key=lambda rule: (rule.priority, rule.rule_id)))


class Stage8ASemantics:
    """Decorate Stage 6 candidates without changing their facts or order."""

    def __init__(self, labels: dict[str, SemanticLabel],
                 rules: Iterable[GenerationHintRule]):
        self.labels = dict(labels)
        self.rules = tuple(rules)

    @classmethod
    def load(cls, root_path: Path) -> "Stage8ASemantics":
        semantic_dir = root_path / "data" / "semantic"
        return cls(
            load_semantic_labels(semantic_dir / "recommendation_semantic_labels.csv"),
            load_generation_hint_rules(
                semantic_dir / "recommendation_generation_hints.csv"
            ),
        )

    @staticmethod
    def _most_specific(rules: Iterable[GenerationHintRule]) -> GenerationHintRule | None:
        rules = tuple(rules)
        if not rules:
            return None
        return min(rules, key=lambda rule: (
            -sum(condition is not None for condition in (
                rule.when_semantic_role, rule.when_same_stat_canonical,
                rule.when_bucket, rule.when_low_support,
            )),
            rule.priority,
            rule.rule_id,
        ))

    def decorate(self, candidate: RecommendationCandidate, *,
                 core_canonicals: Iterable[str],
                 bucket: RecommendationBucket) -> DecoratedRecommendationCandidate:
        if bucket not in VALID_BUCKETS:
            raise ValueError(f"Unknown recommendation bucket: {bucket!r}")
        label = self.labels.get(candidate.canonical)
        role = label.semantic_role if label is not None else "UNCLASSIFIED"
        same_stat = candidate.canonical in frozenset(core_canonicals)
        low_support = candidate.co_count <= LOW_SUPPORT_MAX_CO_COUNT
        matching = [
            rule for rule in self.rules
            if rule.matches(
                semantic_role=role,
                same_stat_canonical=same_stat,
                bucket=bucket,
                low_support=low_support,
            )
        ]
        # A generation hint always comes from the classified semantic role's
        # unconditional default. Statistical/relation rules are additive
        # evidence notes and never replace that role-derived explanation.
        generation_rule = self._most_specific(
            rule for rule in matching
            if rule.when_semantic_role == role
            and rule.when_same_stat_canonical is None
            and rule.when_bucket is None
            and rule.when_low_support is None
        )
        evidence_rules = []
        same_stat_rule = self._most_specific(
            rule for rule in matching
            if rule.when_same_stat_canonical is not None
        )
        if same_stat_rule is not None:
            evidence_rules.append(same_stat_rule)
        bucket_rule = self._most_specific(
            rule for rule in matching
            if rule.when_same_stat_canonical is None
            and (rule.when_bucket is not None or rule.when_low_support is not None)
        )
        if bucket_rule is not None:
            evidence_rules.append(bucket_rule)
        return DecoratedRecommendationCandidate(
            candidate=candidate,
            semantic_role=role,
            semantic_label_ja=(None if role == "UNCLASSIFIED" else SEMANTIC_LABELS_JA[role]),
            relation_flags=(("SAME_STAT_CANONICAL",) if same_stat else ()),
            generation_hint_kind=(generation_rule.kind if generation_rule else None),
            generation_hint_ja=(generation_rule.message_ja if generation_rule else None),
            evidence_note_kinds=tuple(rule.kind for rule in evidence_rules),
            evidence_notes_ja=tuple(rule.message_ja for rule in evidence_rules),
        )

    def decorate_many(self, candidates: Iterable[RecommendationCandidate], *,
                      core_canonicals: Iterable[str],
                      bucket: RecommendationBucket) -> tuple[DecoratedRecommendationCandidate, ...]:
        core = tuple(core_canonicals)
        return tuple(
            self.decorate(candidate, core_canonicals=core, bucket=bucket)
            for candidate in candidates
        )
