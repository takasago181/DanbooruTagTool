"""Stage 8B explicit Support Knowledge Layer.

Only reviewed sidecar rows can produce candidates. No tag text, substring,
regular expression, severity, or statistical score participates in resolution.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal


SUPPORT_SLOTS = frozenset({
    "SUBJECT_BASIC", "BODY_PART", "IMPLEMENT", "ACTION_SUPPORT", "POSE",
    "CAMERA_COMPOSITION", "STATE_REACTION", "SPATIAL_ASSIGNMENT",
})
SUPPORT_SLOT_LABELS_JA = {
    "SUBJECT_BASIC": "人物・人数",
    "BODY_PART": "身体部位",
    "IMPLEMENT": "器具・物体",
    "ACTION_SUPPORT": "行為補強",
    "POSE": "姿勢・体位",
    "CAMERA_COMPOSITION": "構図・見せ方",
    "STATE_REACTION": "状態・反応",
    "SPATIAL_ASSIGNMENT": "配置",
}
SUPPORT_CLASSES = frozenset({"CORE_SUPPORT", "OPTIONAL_VARIATION"})
SUPPORT_CLASS_LABELS_JA = {
    "CORE_SUPPORT": "基本補助",
    "OPTIONAL_VARIATION": "変化候補",
}
INTENT_AXES = frozenset({
    "STRUCTURE", "INTENSITY", "VISIBILITY", "SPECIFICITY", "REACTION",
    "COMPOSITION", "MULTIPLICITY",
})
INTENT_DIRECTIONS = frozenset({"UP", "DOWN", "NEUTRAL"})
COMBINATION_MODES = frozenset({"ADDITIVE", "ALTERNATIVE", "CONTEXTUAL"})
COMBINATION_LABELS_JA = {
    "ADDITIVE": "追加型",
    "ALTERNATIVE": "代替候補",
    "CONTEXTUAL": "条件付き",
}
EVIDENCE_LEVELS = frozenset({
    "SOURCE_VERIFIED", "SEMANTIC_CURATED", "MODEL_OBSERVED",
    "USER_ENV_VERIFIED",
})
PROFILE_FIELDS = (
    "support_slot", "support_class", "candidate_canonical", "priority",
    "reason_ja", "evidence_level", "evidence_source",
    "generation_test_status", "enabled", "intent_axis", "intent_direction",
    "combination_mode", "choice_group", "evidence_ref", "test_profile_id",
    "model_scope", "note",
)


@dataclass(frozen=True, slots=True)
class SupportKnowledgeRow:
    owner_kind: Literal["special", "family"]
    owner_id: str
    support_slot: str
    support_class: str | None
    candidate_canonical: str
    priority: int
    reason_ja: str
    evidence_level: str
    evidence_source: str
    generation_test_status: str
    enabled: bool
    intent_axis: str | None
    intent_direction: str | None
    combination_mode: str | None
    choice_group: str | None
    evidence_ref: str | None
    test_profile_id: str | None
    model_scope: str | None
    note: str


@dataclass(frozen=True, slots=True)
class SemanticSupportRelation:
    owner_special_id: str
    source_kind: Literal["special", "family"]
    source_id: str
    support_slot: str
    support_class: str
    priority: int
    reason_ja: str
    evidence_level: str
    evidence_source: str
    generation_test_status: str
    intent_axis: str | None
    intent_direction: str | None
    combination_mode: str | None
    choice_group: str | None
    evidence_ref: str | None
    test_profile_id: str | None
    model_scope: str | None
    note: str

    @property
    def provenance(self) -> str:
        return f"{self.source_kind}:{self.source_id} / {self.evidence_source}"


@dataclass(frozen=True, slots=True)
class SemanticSupportCandidate:
    canonical: str
    priority: int
    relations: tuple[SemanticSupportRelation, ...]


def _parse_bool(value: str, *, owner: str) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"{owner}: enabled must be true or false")


def _optional_enum(value: str, allowed: frozenset[str], *, field: str,
                   owner: str) -> str | None:
    normalized = value.strip() or None
    if normalized is not None and normalized not in allowed:
        raise ValueError(f"{owner}: invalid {field}: {normalized!r}")
    return normalized


def _load_rows(path: Path, *, owner_field: str, owner_kind: str,
               valid_owners: set[str], valid_canonicals: set[str]) -> tuple[SupportKnowledgeRow, ...]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        expected = [owner_field, *PROFILE_FIELDS]
        if reader.fieldnames != expected:
            raise ValueError(f"Invalid {owner_kind} support schema: {reader.fieldnames!r}")
        rows = []
        keys = set()
        for line, raw in enumerate(reader, start=2):
            owner_id = raw[owner_field].strip()
            owner_label = f"{owner_kind}:{owner_id or '<blank>'} line {line}"
            if owner_id not in valid_owners:
                raise ValueError(f"{owner_label}: unknown {owner_field}")
            canonical = raw["candidate_canonical"].strip()
            if canonical not in valid_canonicals:
                raise ValueError(f"{owner_label}: unknown candidate canonical: {canonical!r}")
            slot = raw["support_slot"].strip()
            if slot not in SUPPORT_SLOTS:
                raise ValueError(f"{owner_label}: invalid support_slot: {slot!r}")
            enabled = _parse_bool(raw["enabled"], owner=owner_label)
            support_class = _optional_enum(
                raw["support_class"], SUPPORT_CLASSES,
                field="support_class", owner=owner_label,
            )
            if enabled and support_class is None:
                raise ValueError(f"{owner_label}: enabled row requires support_class")
            intent_axis = _optional_enum(
                raw["intent_axis"], INTENT_AXES, field="intent_axis", owner=owner_label
            )
            intent_direction = _optional_enum(
                raw["intent_direction"], INTENT_DIRECTIONS,
                field="intent_direction", owner=owner_label,
            )
            combination_mode = _optional_enum(
                raw["combination_mode"], COMBINATION_MODES,
                field="combination_mode", owner=owner_label,
            )
            choice_group = raw["choice_group"].strip() or None
            if enabled and combination_mode == "ALTERNATIVE" and not choice_group:
                raise ValueError(f"{owner_label}: ALTERNATIVE row requires choice_group")
            evidence_level = raw["evidence_level"].strip()
            if evidence_level not in EVIDENCE_LEVELS:
                raise ValueError(f"{owner_label}: invalid evidence_level: {evidence_level!r}")
            test_profile_id = raw["test_profile_id"].strip() or None
            model_scope = raw["model_scope"].strip() or None
            if evidence_level in {"MODEL_OBSERVED", "USER_ENV_VERIFIED"}:
                if not test_profile_id or not model_scope:
                    raise ValueError(
                        f"{owner_label}: {evidence_level} requires test_profile_id and model_scope"
                    )
            try:
                priority = int(raw["priority"])
            except ValueError as exc:
                raise ValueError(f"{owner_label}: priority must be an integer") from exc
            if priority < 0:
                raise ValueError(f"{owner_label}: priority must be non-negative")
            reason = raw["reason_ja"].strip()
            source = raw["evidence_source"].strip()
            generation_status = raw["generation_test_status"].strip()
            if enabled and (not reason or not source or not generation_status):
                raise ValueError(
                    f"{owner_label}: enabled row requires reason, evidence source, and test status"
                )
            key = (owner_id, canonical)
            if key in keys:
                raise ValueError(f"{owner_label}: duplicate candidate canonical: {canonical}")
            keys.add(key)
            rows.append(SupportKnowledgeRow(
                owner_kind=owner_kind,
                owner_id=owner_id,
                support_slot=slot,
                support_class=support_class,
                candidate_canonical=canonical,
                priority=priority,
                reason_ja=reason,
                evidence_level=evidence_level,
                evidence_source=source,
                generation_test_status=generation_status,
                enabled=enabled,
                intent_axis=intent_axis,
                intent_direction=intent_direction,
                combination_mode=combination_mode,
                choice_group=choice_group,
                evidence_ref=raw["evidence_ref"].strip() or None,
                test_profile_id=test_profile_id,
                model_scope=model_scope,
                note=raw["note"].strip(),
            ))
    return tuple(rows)


def load_special_support_profiles(path: Path, knowledge) -> tuple[SupportKnowledgeRow, ...]:
    return _load_rows(
        path,
        owner_field="special_id", owner_kind="special",
        valid_owners=set(knowledge.special), valid_canonicals=set(knowledge.canonical),
    )


def load_family_support_rules(path: Path, knowledge, profile_store) -> tuple[SupportKnowledgeRow, ...]:
    return _load_rows(
        path,
        owner_field="family_rule_id", owner_kind="family",
        valid_owners=set(profile_store.family_rules),
        valid_canonicals=set(knowledge.canonical),
    )


class SupportKnowledgeStore:
    """Validated explicit support profiles and deterministic union resolver."""

    def __init__(self, special_rows: Iterable[SupportKnowledgeRow],
                 family_rows: Iterable[SupportKnowledgeRow], profile_store):
        self.special_rows = tuple(special_rows)
        self.family_rows = tuple(family_rows)
        self.profile_store = profile_store
        self._special: dict[str, tuple[SupportKnowledgeRow, ...]] = {}
        self._family: dict[str, tuple[SupportKnowledgeRow, ...]] = {}
        for owner_id in {row.owner_id for row in self.special_rows}:
            self._special[owner_id] = tuple(sorted(
                (row for row in self.special_rows if row.owner_id == owner_id and row.enabled),
                key=lambda row: (row.priority, row.candidate_canonical),
            ))
        for owner_id in {row.owner_id for row in self.family_rows}:
            self._family[owner_id] = tuple(sorted(
                (row for row in self.family_rows if row.owner_id == owner_id and row.enabled),
                key=lambda row: (row.priority, row.candidate_canonical),
            ))

    @classmethod
    def load(cls, root_path: Path, knowledge, profile_store) -> "SupportKnowledgeStore":
        directory = root_path / "data" / "semantic"
        special_rows = load_special_support_profiles(
            directory / "semantic_support_profiles.csv", knowledge
        )
        family_rows = load_family_support_rules(
            directory / "family_support_rules.csv", knowledge, profile_store
        )
        return cls(special_rows, family_rows, profile_store)

    def candidates(self, selected_special_ids: Iterable[str]) -> tuple[SemanticSupportCandidate, ...]:
        selected = tuple(dict.fromkeys(selected_special_ids))
        gathered: dict[str, list[tuple[int, str, SupportKnowledgeRow]]] = {}
        for special_id in selected:
            explicit = self._special.get(special_id, ())
            profile = self.profile_store.profiles.get(special_id)
            family_id = profile.FamilyRuleId if profile is not None else None
            family = self._family.get(family_id, ()) if family_id else ()
            explicit_canonicals = {row.candidate_canonical for row in explicit}
            for source_rank, rows in ((0, explicit), (1, family)):
                for row in rows:
                    if source_rank and row.candidate_canonical in explicit_canonicals:
                        continue
                    gathered.setdefault(row.candidate_canonical, []).append(
                        (source_rank, special_id, row)
                    )
        candidates = []
        order_keys = {}
        for canonical, entries in gathered.items():
            entries.sort(key=lambda item: (
                item[0], item[2].priority, item[1], item[2].owner_id
            ))
            order_keys[canonical] = (
                entries[0][0], min(entry[2].priority for entry in entries), canonical
            )
            relations = []
            for _, owner_special_id, row in entries:
                if row.support_class is None:  # guarded by loader validation
                    raise RuntimeError("enabled support row has no support_class")
                relations.append(SemanticSupportRelation(
                    owner_special_id=owner_special_id,
                    source_kind=row.owner_kind,
                    source_id=row.owner_id,
                    support_slot=row.support_slot,
                    support_class=row.support_class,
                    priority=row.priority,
                    reason_ja=row.reason_ja,
                    evidence_level=row.evidence_level,
                    evidence_source=row.evidence_source,
                    generation_test_status=row.generation_test_status,
                    intent_axis=row.intent_axis,
                    intent_direction=row.intent_direction,
                    combination_mode=row.combination_mode,
                    choice_group=row.choice_group,
                    evidence_ref=row.evidence_ref,
                    test_profile_id=row.test_profile_id,
                    model_scope=row.model_scope,
                    note=row.note,
                ))
            candidates.append(SemanticSupportCandidate(
                canonical=canonical,
                priority=min(entry[2].priority for entry in entries),
                relations=tuple(relations),
            ))
        return tuple(sorted(candidates, key=lambda item: order_keys[item.canonical]))
