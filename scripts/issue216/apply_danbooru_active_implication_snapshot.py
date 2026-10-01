#!/usr/bin/env python3
"""Normalize one live Danbooru implication snapshot and join it to #216.

Only active exact Character -> Copyright implications are HOME evidence. The
Copyright -> Copyright edges in the same snapshot are used only to rank an
explicitly direct set of Copyright memberships. No transitive Character HOME
is inferred.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

try:
    from authority_coverage import (
        BASELINE_SIZE, DECISION_FIELDS, MEMBER_FIELDS, MULTI_ROOT_SOURCE_TYPES,
        SOURCE_FIELDS, deterministic_source_id, member_home_root, read_csv, sha256,
        validate,
    )
except ModuleNotFoundError:
    from scripts.issue216.authority_coverage import (
        BASELINE_SIZE, DECISION_FIELDS, MEMBER_FIELDS, MULTI_ROOT_SOURCE_TYPES,
        SOURCE_FIELDS, deterministic_source_id, member_home_root, read_csv, sha256,
        validate,
    )

ROOT = Path(__file__).resolve().parents[2]
ISSUE216 = ROOT / "docs/issue216"
COHORT = ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv"
SOURCES = ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv"
MEMBERS = ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv"
DECISIONS = ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv"
ROOTS = ISSUE216 / "COPYRIGHT_ROOTS_V1.csv"
SNAPSHOT = ISSUE216 / "DANBOORU_ACTIVE_COPYRIGHT_IMPLICATIONS_SNAPSHOT_V1.csv"
MANIFEST = ISSUE216 / "DANBOORU_ACTIVE_COPYRIGHT_IMPLICATIONS_SNAPSHOT_V1.json"
RELATIONS = ISSUE216 / "DANBOORU_NORMALIZED_SEMANTIC_RELATIONS_V1.csv"
RELATION_FIELDS = [
    "implication_id", "status", "antecedent_surface", "antecedent_canonical",
    "antecedent_category", "antecedent_resolution", "consequent_surface",
    "consequent_canonical", "consequent_category", "consequent_resolution",
    "updated_at", "snapshot_sha256",
]
REVIEW_DATE = "2026-10-01"
REVIEWER = "Codex deterministic active implication snapshot join"
SOURCE_URL = "https://danbooru.donmai.us/tag_implications.json?search%5Bstatus%5D=active&search%5Bcategory%5D=3"
ALIAS_EXPECTED = "3f942704a10bb342ae7368024337849d392d54745061cf9259e51b9f6080a394"
CATALOG_EXPECTED = "9b32d5ac0713ab252e7470ba6af9cb34de56878b6b3b13dfbbf6a4a37d82d95b"


def write_atomic(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=path.parent,
                                     prefix=path.name + ".", suffix=".tmp", delete=False) as stream:
        tmp = Path(stream.name)
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def norm_surface(value: str) -> str:
    return " ".join(value.replace("_", " ").casefold().split())


def targets(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def index_aliases(path: Path) -> tuple[dict[str, str], set[str]]:
    unique: dict[str, str] = {}
    ambiguous: set[str] = set()
    for row in read_csv(path):
        key = row["NormalizedAlias"].strip().casefold()
        if row["ResolutionStatus"] == "ALIAS_UNIQUE" and row["TargetCount"] == "1":
            values = targets(row["CanonicalTargets"])
            if len(values) == 1:
                unique[key] = values[0]
        elif row["ResolutionStatus"] == "AMBIGUOUS_ALIAS":
            ambiguous.add(key)
    return unique, ambiguous


def build(args: argparse.Namespace) -> tuple[list[dict[str, str]], list[dict[str, str]],
                                               list[dict[str, str]], list[dict[str, str]],
                                               dict[str, object]]:
    snapshot_hash = sha256(args.snapshot)
    manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    if manifest.get("snapshot_sha256") != snapshot_hash:
        raise ValueError("snapshot hash does not match its manifest")
    if manifest.get("filter_status") != "active" or manifest.get("filter_consequent_category_id") != 3:
        raise ValueError("snapshot manifest is not the active consequent-Copyright snapshot")
    if sha256(args.alias_index) != ALIAS_EXPECTED:
        raise ValueError("verified Issue #70 alias snapshot hash mismatch")
    if sha256(args.tag_catalog) != CATALOG_EXPECTED:
        raise ValueError("verified Issue #70 tag catalog hash mismatch")

    validate(COHORT, SOURCES, MEMBERS, DECISIONS, expected_size=BASELINE_SIZE, roots_path=ROOTS)
    cohort = read_csv(COHORT)
    source_rows = read_csv(SOURCES)
    member_rows = read_csv(MEMBERS)
    decision_rows = read_csv(DECISIONS)
    cohort_tags = {row["canonical_character"] for row in cohort}
    decision_by_tag = {row["canonical_character"]: dict(row) for row in decision_rows}
    open_tags = {tag for tag, row in decision_by_tag.items() if row["research_state"] == "UNRESEARCHED"}
    roots = {row["copyright_canonical"] for row in read_csv(ROOTS)}
    sources_by_id = {row["source_id"]: dict(row) for row in source_rows}

    catalog: dict[str, str] = {}
    with args.tag_catalog.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.reader(stream):
            if len(row) >= 2 and row[0]:
                catalog[row[0]] = row[1]
    alias_map, ambiguous_aliases = index_aliases(args.alias_index)

    def resolve(surface: str, required_category: str) -> tuple[str, str, str]:
        if surface in catalog:
            return surface, catalog[surface], "EXACT_CANONICAL"
        key = norm_surface(surface)
        if key in ambiguous_aliases:
            return "", "", "AMBIGUOUS_ALIAS"
        canonical = alias_map.get(key, "")
        if not canonical:
            return "", "", "NO_EXACT_ALIAS"
        return canonical, catalog.get(canonical, ""), "VALIDATED_UNIQUE_ALIAS"

    raw_rows = read_csv(args.snapshot)
    if len(raw_rows) != manifest.get("row_count"):
        raise ValueError("snapshot row count does not match manifest")
    relation_ids: set[str] = set()
    normalized_rows: list[dict[str, str]] = []
    character_edges: dict[str, list[dict[str, str]]] = defaultdict(list)
    copyright_edges: set[tuple[str, str]] = set()
    normalization_counts: dict[str, int] = defaultdict(int)
    for raw in raw_rows:
        rid = raw["implication_id"]
        if rid in relation_ids:
            raise ValueError(f"duplicate implication ID {rid}")
        relation_ids.add(rid)
        if raw["status"] != "active":
            raise ValueError(f"non-active row present in filtered snapshot: {rid}")
        ante, ante_cat, ante_resolution = resolve(raw["antecedent_tag"], "")
        cons, cons_cat, cons_resolution = resolve(raw["consequent_tag"], "3")
        normalized_rows.append({
            "implication_id": rid, "status": raw["status"],
            "antecedent_surface": raw["antecedent_tag"], "antecedent_canonical": ante,
            "antecedent_category": ante_cat, "antecedent_resolution": ante_resolution,
            "consequent_surface": raw["consequent_tag"], "consequent_canonical": cons,
            "consequent_category": cons_cat, "consequent_resolution": cons_resolution,
            "updated_at": raw["updated_at"], "snapshot_sha256": snapshot_hash,
        })
        normalization_counts[f"antecedent_{ante_resolution}"] += 1
        normalization_counts[f"consequent_{cons_resolution}"] += 1
        if ante_cat == "4" and cons_cat == "3" and cons in roots and ante in cohort_tags:
            character_edges[ante].append({
                "id": rid, "root": cons, "surface": raw["antecedent_tag"],
                "mapping_method": "EXACT_CANONICAL" if ante_resolution == "EXACT_CANONICAL" else "VALIDATED_ALIAS",
                "mapping_evidence": (
                    f"Danbooru active implication ID {rid}: exact canonical Character {ante} -> exact canonical Copyright {cons}; "
                    f"antecedent identity via {ante_resolution}; consequent category=Copyright; snapshot_sha256={snapshot_hash}."
                ), "updated_at": raw["updated_at"],
            })
        if ante_cat == "3" and cons_cat == "3" and ante in roots and cons in roots:
            copyright_edges.add((ante, cons))

    source_scope = "All active tag implications whose consequent tag is category Copyright (3); cohort use is exact canonical Character antecedent to exact canonical Copyright consequent, with category validation from the verified tag catalog."
    snapshot_source_id = deterministic_source_id(
        SOURCE_URL, "Danbooru", source_scope,
    )
    if snapshot_source_id in sources_by_id:
        prior = sources_by_id[snapshot_source_id]
        if prior["source_type"] != "DANBOORU_ACTIVE_COPYRIGHT_IMPLICATION" or prior["source_url"] != SOURCE_URL:
            raise ValueError("snapshot source id collides with a different authority source")
    else:
        sources_by_id[snapshot_source_id] = {
            "source_id": snapshot_source_id, "copyright_canonical": "", "source_url": SOURCE_URL,
            "source_type": "DANBOORU_ACTIVE_COPYRIGHT_IMPLICATION", "authority_owner": "Danbooru",
            "source_status": "ACCEPTED", "source_scope": source_scope, "exact_roster_available": "false",
            "reviewed_at": manifest["snapshot_fetched_at_utc"][:10],
            "source_claim": "Snapshot filter returns active tag implications with a Copyright consequent; HOME evidence is only an exact direct Character->Copyright relation in this snapshot.",
            "provenance": f"{SOURCE_URL} | snapshot {manifest['snapshot_fetched_at_utc']} | SHA-256 {snapshot_hash} | {manifest['row_count']} rows / {manifest['page_count']} pages",
            "reusable": "true", "notes": "Single multi-root relation snapshot. Each direct relation is separately identified by implication ID in the member table.",
        }

    exact_members = {
        (row["source_id"], row["canonical_character"], row.get("member_relation_id", "")): dict(row)
        for row in member_rows
    }
    existing_roots: dict[str, set[str]] = defaultdict(set)
    existing_sources_by_tag_root: dict[tuple[str, str], set[str]] = defaultdict(set)
    for member in member_rows:
        source = sources_by_id.get(member["source_id"])
        if source and source["source_status"] == "ACCEPTED" and member["mapping_status"] == "EXACT_COVERED":
            home = member_home_root(source, member)
            if home in roots:
                existing_roots[member["canonical_character"]].add(home)
                existing_sources_by_tag_root[(member["canonical_character"], home)].add(source["source_id"])

    def reaches(start: str, goal: str) -> bool:
        stack = [start]
        seen = {start}
        while stack:
            node = stack.pop()
            if node == goal:
                return True
            for child, parent in copyright_edges:
                if child == node and parent not in seen:
                    seen.add(parent)
                    stack.append(parent)
        return False

    def hierarchy_priority(candidates: set[str]) -> tuple[str, dict[str, int], str]:
        if len(candidates) == 1:
            root = next(iter(candidates))
            return root, {root: 1}, "Single exact direct Copyright root in the active implication snapshot."
        winners = [candidate for candidate in candidates
                   if all(candidate == other or reaches(candidate, other) for other in candidates)]
        if len(winners) != 1:
            return "", {}, "Independent or non-unique active Copyright hierarchy; unresolved conflict."
        if any(not (a == b or reaches(a, b) or reaches(b, a)) for a in candidates for b in candidates):
            return "", {}, "Direct Copyright roots are not all comparable in the active hierarchy."
        home = winners[0]
        tiers = {root: 1 + sum(1 for other in candidates if other != root and reaches(other, root))
                 for root in candidates}
        if max(tiers.values(), default=0) > 4:
            return "", {}, "Hierarchy depth exceeds Browse HOME priority tiers 1-4."
        return home, tiers, "Active direct Copyright implication hierarchy uniquely places this root below its broader direct memberships."

    # Every exact direct cohort relation becomes a reusable member row. Relation IDs
    # preserve multiple active edges for the same Character in this one snapshot.
    for tag, edges in character_edges.items():
        for edge in edges:
            key = (snapshot_source_id, tag, edge["id"])
            row = {
                "source_id": snapshot_source_id, "canonical_character": tag,
                "member_relation_id": edge["id"], "canonical_home_root": edge["root"],
                "matched_surface": edge["surface"], "mapping_method": edge["mapping_method"],
                "mapping_evidence": edge["mapping_evidence"], "reviewed_at": manifest["snapshot_fetched_at_utc"][:10],
                "reviewer": REVIEWER, "mapping_status": "EXACT_COVERED",
                "browse_home_tier": "", "browse_home_basis": "",
            }
            if key in exact_members and exact_members[key] != row:
                raise ValueError(f"existing member row differs from current snapshot relation {key}")
            exact_members[key] = row

    proposed_home: dict[str, str] = {}
    conflicts: dict[str, set[str]] = {}
    for tag in sorted(open_tags):
        direct = {row["root"] for row in character_edges.get(tag, [])}
        if not direct:
            continue
        known = direct | existing_roots.get(tag, set())
        chosen, tiers, basis = hierarchy_priority(known)
        if not chosen:
            conflicts[tag] = known
            continue
        if existing_roots.get(tag, set()) - direct:
            # A new implication snapshot cannot silently outrank unrelated accepted
            # membership evidence. Preserve both routes as an explicit conflict.
            conflicts[tag] = known
            continue
        proposed_home[tag] = chosen
        for member in exact_members.values():
            if member["canonical_character"] == tag:
                home = member_home_root(sources_by_id[member["source_id"]], member)
                if home in tiers:
                    member["browse_home_tier"] = str(tiers[home])
                    member["browse_home_basis"] = basis

    decision_by_tag = {row["canonical_character"]: dict(row) for row in decision_rows}
    terminalized_home = 0
    terminalized_conflict = 0
    for tag, home in proposed_home.items():
        decision = decision_by_tag[tag]
        if decision["research_state"] != "UNRESEARCHED":
            continue
        source_ids = {snapshot_source_id} | existing_sources_by_tag_root.get((tag, home), set())
        evidence_rows = [row for row in exact_members.values()
                         if row["canonical_character"] == tag and row["source_id"] in source_ids]
        decision.update({
            "research_state": "HOME_CONFIRMED", "home_copyright": home,
            "authority_type": "DANBOORU_ACTIVE_COPYRIGHT_IMPLICATION",
            "source_ids": "|".join(sorted(source_ids)),
            "source_claim": f"Danbooru current active direct Character->Copyright implication set gives unique Browse HOME {home}; no popularity/co-occurrence evidence used.",
            "provenance": " || ".join(sorted({f"{snapshot_hash}: implication {row['member_relation_id']} {row['canonical_character']} -> {member_home_root(sources_by_id[row['source_id']], row)}" for row in evidence_rows})),
            "reviewed_at": REVIEW_DATE, "reason_code": "DANBOORU_ACTIVE_DIRECT_IMPLICATION",
            "reason_detail": "Exact active Character->Copyright implication with validated canonical categories and root; Copyright hierarchy used only for explicitly direct alternative roots.",
            "validated_home_candidates": "",
        })
        terminalized_home += 1

    for tag, candidate_roots in conflicts.items():
        decision = decision_by_tag[tag]
        if decision["research_state"] != "UNRESEARCHED":
            continue
        conflict_sources = {snapshot_source_id}
        for root in candidate_roots:
            conflict_sources.update(existing_sources_by_tag_root.get((tag, root), set()))
        decision.update({
            "research_state": "EVIDENCE_CONFLICT", "home_copyright": "",
            "authority_type": "DANBOORU_ACTIVE_COPYRIGHT_IMPLICATION",
            "source_ids": "|".join(sorted(conflict_sources)),
            "source_claim": "Exact active direct Copyright relations or accepted exact memberships yield multiple non-ranked Browse HOME candidates.",
            "provenance": f"Danbooru implication snapshot SHA-256 {snapshot_hash}; direct roots: {'|'.join(sorted({r['root'] for r in character_edges.get(tag, [])}))}; accepted exact roots: {'|'.join(sorted(existing_roots.get(tag, set())))}.",
            "reviewed_at": REVIEW_DATE, "reason_code": "MULTIPLE_UNRANKED_EXACT_COPYRIGHT_RELATIONS",
            "reason_detail": "Multiple exact active direct Copyright memberships lack one safe unique Browse HOME under explicit active Copyright hierarchy; no majority/popularity/candidate scoring applied.",
            "validated_home_candidates": "|".join(sorted(candidate_roots)),
        })
        terminalized_conflict += 1

    sources_out = sorted(sources_by_id.values(), key=lambda row: row["source_id"])
    members_out = sorted(exact_members.values(), key=lambda row: (row["source_id"], row["canonical_character"], row.get("member_relation_id", "")))
    decisions_out = [decision_by_tag[row["canonical_character"]] for row in decision_rows]
    open_after = sum(row["research_state"] == "UNRESEARCHED" for row in decisions_out)
    census = {
        "census_as_of_utc": manifest["snapshot_fetched_at_utc"],
        "snapshot_sha256": snapshot_hash, "snapshot_rows": len(raw_rows),
        "open_before": len(open_tags), "direct_active_character_copyright": len(character_edges),
        "direct_unique_root_candidates": len(proposed_home),
        "direct_multiple_root_conflicts": len(conflicts),
        "no_direct_implication": len(open_tags - set(character_edges)),
        "new_home_confirmed": terminalized_home,
        "new_evidence_conflict": terminalized_conflict,
        "open_after": open_after,
        "normalized_direct_member_relations": sum(len(edges) for edges in character_edges.values()),
        "copyright_hierarchy_edges": len(copyright_edges),
        "normalization_counts": dict(sorted(normalization_counts.items())),
        "alias_sha256": sha256(args.alias_index), "tag_catalog_sha256": sha256(args.tag_catalog),
        "existing_home_mutations": 0,
        "missing_roots": 0,
        "external_web_research_needed_after_semantic_pass": None,
        "state_note": (
            f"Remaining UNRESEARCHED is {open_after}; how many need external Web Research is not yet determined "
            "because source-scope/roster and route-level review remains."
        ),
    }
    return normalized_rows, sources_out, members_out, decisions_out, census


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--alias-index", type=Path,
                        default=Path(r"C:\Codex\DanbooruTagTool\data\derived\danbooru_alias_normalized_index_VERIFIED_34417.csv"))
    parser.add_argument("--tag-catalog", type=Path,
                        default=Path(r"C:\Codex\DanbooruTagTool\data\source\danbooru-2026-09-02.csv"))
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    normalized, sources, members, decisions, census = build(args)
    print(json.dumps(census, ensure_ascii=False, indent=2))
    if args.check:
        expected_tables = (
            (RELATIONS, RELATION_FIELDS, normalized), (SOURCES, SOURCE_FIELDS, sources),
            (MEMBERS, MEMBER_FIELDS, members), (DECISIONS, DECISION_FIELDS, decisions),
        )
        for path, fields, expected in expected_tables:
            actual = read_csv(path)
            if actual != expected:
                raise SystemExit(f"deterministic implication rebuild differs: {path}")
        actual_census = json.loads((ISSUE216 / "DANBOORU_ACTIVE_IMPLICATION_COHORT_CENSUS_V1.json").read_text(encoding="utf-8"))
        if actual_census != census:
            raise SystemExit("deterministic implication census differs")
        print("deterministic implication snapshot join: PASS")
        return
    write_atomic(RELATIONS, RELATION_FIELDS, normalized)
    write_atomic(SOURCES, SOURCE_FIELDS, sources)
    write_atomic(MEMBERS, MEMBER_FIELDS, members)
    write_atomic(DECISIONS, DECISION_FIELDS, decisions)
    validate(COHORT, SOURCES, MEMBERS, DECISIONS, expected_size=BASELINE_SIZE, roots_path=ROOTS)
    summary_path = ISSUE216 / "DANBOORU_ACTIVE_IMPLICATION_COHORT_CENSUS_V1.json"
    summary_path.write_text(json.dumps(census, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote normalized relation table: {RELATIONS}")
    print(f"wrote one reusable source and {sum(row['source_id'] == deterministic_source_id(SOURCE_URL, 'Danbooru active tag implication API', 'One live snapshot of all active implications filtered by consequent category=Copyright; direct Character->Copyright rows only support membership; Copyright hierarchy only ranks explicitly direct Character roots.') for row in members)} direct cohort relation members")


if __name__ == "__main__":
    main()
