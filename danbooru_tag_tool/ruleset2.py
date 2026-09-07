"""Validated Ruleset2 dictionary and policy overlays.

The immutable ``data/special2788`` source remains the historical source snapshot.
Ruleset2 is an audited derived overlay: it may change curated metadata and search
text, but it must preserve every source ``ID + Tag`` identity.
"""
from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass, replace
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
import re

from .models import SpecialTag


CANDIDATE_SHA256 = "12f6ccdc5d2dba33123cdfa97a636b2fdd49a519ed89d327d330471696762e02"
SOURCE_IDENTITY_SHA256 = "b2f126ae9d49493034245fe006aad8eceb12eb2bf08a45160995b8da10b07763"


def _rows(path: Path) -> tuple[dict[str, str], ...]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return tuple(csv.DictReader(stream))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _identity_hash(rows) -> str:
    text = "".join(
        f"{int(row['ID'])}\t{row['Tag']}\n"
        for row in sorted(rows, key=lambda item: int(item["ID"]))
    )
    return hashlib.sha256(text.encode()).hexdigest()


def _expected_search_keys(row: dict[str, str]) -> tuple[str, ...]:
    values: list[str] = []

    def add(value: str) -> None:
        value = value.strip()
        if value and value not in values:
            values.append(value)

    term = row["Tag"]
    add(term)
    if " " in term:
        add(term.replace(" ", "_"))
    elif "_" in term:
        add(term.replace("_", " "))
    add(row["日本語"])
    target = row["canonical_target"]
    add(target)
    if "_" in target:
        add(target.replace("_", " "))
    elif " " in target:
        add(target.replace(" ", "_"))
    return tuple(values)


def _integral_count(value: str) -> int | None:
    if not value.strip():
        return None
    try:
        number = Decimal(value)
    except InvalidOperation as error:
        raise ValueError(f"Invalid Ruleset2 dictionary post_count: {value}") from error
    if number != number.to_integral_value() or number < 0:
        raise ValueError(f"Invalid Ruleset2 dictionary post_count: {value}")
    return int(number)


@dataclass(frozen=True, slots=True)
class AliasSemanticPolicy:
    special_id: str
    source_term: str
    official_canonical_target: str
    semantic_equivalence_status: str
    semantic_role: str
    semantic_anchor: str
    semantic_reason_ja: str
    prompt_route_authority: str
    automatic_prompt_replacement: str


@dataclass(frozen=True, slots=True)
class AliasStatisticsPolicy:
    special_id: str
    source_term: str
    official_canonical_target: str
    statistics_policy: str
    default_full_semantic_stats_allowed: str
    related_evidence_allowed: str
    context_requirement: str
    automatic_prompt_replacement: str
    policy_provenance: str
    reason_ja: str


@dataclass(frozen=True, slots=True)
class SemanticRoute:
    special_id: str
    special_term_snapshot: str
    semantic_subtype: str
    anchor_kind: str
    anchor_value: str
    ambiguity_flag: str
    match_policy: str
    default_prompt_mode: str


@dataclass(frozen=True, slots=True)
class Ruleset2Store:
    special: dict[str, SpecialTag]
    alias_semantic: dict[str, AliasSemanticPolicy]
    alias_statistics: dict[str, AliasStatisticsPolicy]
    semantic_routes: dict[str, SemanticRoute]
    migration_rows: tuple[dict[str, str], ...]

    @classmethod
    def load(cls, directory: Path, baseline: dict[str, SpecialTag]) -> "Ruleset2Store":
        manifest = json.loads((directory / "RULESET2_MANIFEST.json").read_text(encoding="utf-8"))
        for name, expected_hash in manifest["artifacts"].items():
            if _sha256(directory / name) != expected_hash:
                raise ValueError(f"Ruleset2 authority hash mismatch: {name}")
        if (manifest["source_id_tag_identity_sha256"] != SOURCE_IDENTITY_SHA256
                or manifest["pilot001_acceptance"] != "NOT COMPLETE"
                or manifest["stage9"] != "NOT STARTED"
                or manifest["stage10"] != "NOT STARTED"
                or manifest["production_applied"] is not False):
            raise ValueError("Ruleset2 manifest stage/identity gate mismatch")
        candidate_path = directory / "01_SPECIAL2788_JAPANESE_COMPLETE_CANDIDATE.csv"
        if _sha256(candidate_path) != CANDIDATE_SHA256:
            raise ValueError("Ruleset2 candidate SHA-256 mismatch")
        candidate = _rows(candidate_path)
        if len(candidate) != 2788 or _identity_hash(candidate) != SOURCE_IDENTITY_SHA256:
            raise ValueError("Ruleset2 source ID+Tag identity mismatch")
        by_id = {row["ID"]: row for row in candidate}
        if len(by_id) != len(candidate) or set(by_id) != set(baseline):
            raise ValueError("Ruleset2/baseline Special ID sets differ")

        overlaid: dict[str, SpecialTag] = {}
        for special_id, source in baseline.items():
            row = by_id[special_id]
            if row["Tag"] != source.term or row["Layer"] != source.layer:
                raise ValueError(f"Ruleset2 source identity/layer changed: {special_id}")
            if row["元カテゴリ"] != source.source_category:
                raise ValueError(f"Ruleset2 source category changed: {special_id}")
            # The source table stores ``canonical_target`` only for Alias rows;
            # canonical Core/Extended linkage is owned by the protected linkage table.
            expected_target = source.chosen_canonical if source.layer == "Alias" else None
            if source.match_type == "alias_ambiguous_multiple":
                expected_target = "複数正規化先"
            if (row["canonical_target"] or None) != expected_target:
                raise ValueError(f"Ruleset2 canonical identity changed: {special_id}")
            expected_keys = _expected_search_keys(row)
            actual_keys = tuple(part.strip() for part in row["検索キー"].split(" | ") if part.strip())
            if actual_keys != expected_keys:
                raise ValueError(f"Ruleset2 search derivation mismatch: {special_id}")
            overlaid[special_id] = replace(
                source,
                japanese=row["日本語"],
                description=row["元の日本語説明"],
                main_category=row["主カテゴリ"],
                related_category=row["関連カテゴリ"],
                gender_scope=row["性別スコープ"],
                danbooru_kind=row["Danbooru種別"],
                dictionary_post_count=_integral_count(row["post_count"]),
                count_band=row["件数帯"],
                search_keys=actual_keys,
            )

        alias_ids = {sid for sid, tag in overlaid.items() if tag.layer == "Alias"}
        semantic_rows = _rows(directory / "37_ALIAS_SEMANTIC_RELATIONSHIP_v3.0.csv")
        statistics_rows = _rows(directory / "38_ALIAS_STATISTICS_POLICY_v3.0.csv")
        if len(semantic_rows) != 778 or len(statistics_rows) != 778:
            raise ValueError("Ruleset2 Alias authorities must each contain 778 rows")
        alias_semantic = {row["special_id"]: AliasSemanticPolicy(**row) for row in semantic_rows}
        alias_statistics = {row["special_id"]: AliasStatisticsPolicy(**row) for row in statistics_rows}
        if set(alias_semantic) != alias_ids or set(alias_statistics) != alias_ids:
            raise ValueError("Ruleset2 Alias authority coverage mismatch")
        for special_id in alias_ids:
            tag = overlaid[special_id]
            semantic = alias_semantic[special_id]
            statistics = alias_statistics[special_id]
            if not (semantic.source_term == statistics.source_term == tag.term):
                raise ValueError(f"Ruleset2 Alias source mismatch: {special_id}")
            if not (semantic.official_canonical_target == statistics.official_canonical_target
                    == by_id[special_id]["canonical_target"]):
                raise ValueError(f"Ruleset2 Alias target mismatch: {special_id}")
            if (semantic.prompt_route_authority != "NO"
                    or semantic.automatic_prompt_replacement != "NEVER"
                    or statistics.automatic_prompt_replacement != "NEVER"):
                raise ValueError(f"Ruleset2 Alias attempted Prompt ownership: {special_id}")
            allowed = statistics.default_full_semantic_stats_allowed
            if allowed not in {"YES", "NO"}:
                raise ValueError(f"Invalid Ruleset2 Alias statistics flag: {special_id}")
            overlaid[special_id] = replace(
                tag,
                alias_semantic_status=semantic.semantic_equivalence_status,
                alias_semantic_role=semantic.semantic_role,
                alias_statistics_policy=statistics.statistics_policy,
                default_full_semantic_stats_allowed=allowed == "YES",
                related_evidence_allowed=statistics.related_evidence_allowed == "YES",
                automatic_prompt_replacement=statistics.automatic_prompt_replacement,
            )
        if Counter(item.statistics_policy for item in alias_statistics.values())[
                "FULL_DEFAULT_SEMANTIC_STATS"] != 496:
            raise ValueError("Ruleset2 full-default Alias statistics count mismatch")

        route_rows = _rows(directory / "06_SEMANTIC336_ROUTING_OVERLAY.csv")
        semantic_ids = {sid for sid, tag in overlaid.items() if tag.layer == "Semantic"}
        if len(route_rows) != 336 or {row["special_id"] for row in route_rows} != semantic_ids:
            raise ValueError("Ruleset2 Semantic336 coverage mismatch")
        routes: dict[str, SemanticRoute] = {}
        allowed_routes = {
            "SEARCH_ALIAS": ({"SPECIAL", "GENERAL_CANONICAL"}, {"SEARCH_ONLY"}),
            "MODEL_NEUTRAL_CONCEPT": ({"SELF_SPECIAL"}, {"SPECIAL_CORE_ELIGIBLE"}),
            "PRACTICAL_PHRASE": ({"PRACTICAL_PHRASE"}, {"PRACTICAL_OPTIONAL"}),
            "MODEL_PROFILE": ({"MODEL_PROFILE"}, {"MODEL_PROFILE"}),
            "SCOPE_REFERENCE": ({"SCOPE_REFERENCE"}, {"SCOPE_ONLY"}),
        }
        for row in route_rows:
            special_id = row["special_id"]
            tag = overlaid[special_id]
            if (row["special_term_snapshot"] != tag.term or row["japanese"] != tag.japanese
                    or row["main_category"] != tag.main_category):
                raise ValueError(f"Ruleset2 Semantic route identity mismatch: {special_id}")
            subtype = row["semantic_subtype"]
            if subtype not in allowed_routes:
                raise ValueError(f"Unknown Ruleset2 Semantic subtype: {subtype}")
            kinds, modes = allowed_routes[subtype]
            if row["anchor_kind"] not in kinds or row["default_prompt_mode"] not in modes:
                raise ValueError(f"Invalid Ruleset2 Semantic route: {special_id}")
            if subtype == "MODEL_NEUTRAL_CONCEPT":
                if row["anchor_value"] != f"{special_id}:{tag.term}":
                    raise ValueError(f"Invalid Ruleset2 self anchor: {special_id}")
            elif subtype == "SEARCH_ALIAS" and not row["anchor_value"]:
                raise ValueError(f"Missing Ruleset2 search anchor: {special_id}")
            routes[special_id] = SemanticRoute(
                special_id=special_id,
                special_term_snapshot=row["special_term_snapshot"],
                semantic_subtype=subtype,
                anchor_kind=row["anchor_kind"],
                anchor_value=row["anchor_value"],
                ambiguity_flag=row["ambiguity_flag"],
                match_policy=row["match_policy"],
                default_prompt_mode=row["default_prompt_mode"],
            )

        migrations = _rows(directory / "31_METADATA_RULESET2_MIGRATIONS_v3.0.csv")
        if len(migrations) != 3076:
            raise ValueError("Ruleset2 metadata migration row count mismatch")
        for row in migrations:
            if row["ID"] not in overlaid or row["Tag"] != overlaid[row["ID"]].term:
                raise ValueError("Ruleset2 migration source identity mismatch")
            if not row["field"].strip() or not row["basis"].strip():
                raise ValueError("Ruleset2 migration lacks field/basis provenance")

        return cls(overlaid, alias_semantic, alias_statistics, routes, migrations)
