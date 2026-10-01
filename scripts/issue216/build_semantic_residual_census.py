#!/usr/bin/env python3
"""Create a routing-only census of #216 rows left after semantic bulk passes."""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from authority_coverage import BASELINE_SIZE, read_csv, validate

ROOT = Path(__file__).resolve().parents[2]
ISSUE216 = ROOT / "docs/issue216"
COHORT = ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv"
SOURCES = ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv"
MEMBERS = ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv"
DECISIONS = ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv"
ROOTS = ISSUE216 / "COPYRIGHT_ROOTS_V1.csv"
GRAPH = ROOT / ".tmp-issue216-work/restored-frozen-inputs/issue180-final/structure_graph_v3.csv"
VARIANTS = ROOT / "docs/issue180/autonomous/decisions/variants_verified_v4.csv"
OUT_CSV = ISSUE216 / "SEMANTIC_RESIDUAL_CENSUS_V1.csv"
OUT_JSON = ISSUE216 / "SEMANTIC_RESIDUAL_CENSUS_V1.json"
FIELDS = ["canonical_character", "category", "route_signal", "candidate_roots", "source_routes", "terminal_state"]


def catalog(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return {row[0]: row[1] for row in csv.reader(stream) if len(row) >= 2 and row[0]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, default=GRAPH)
    parser.add_argument("--tag-catalog", type=Path,
                        default=Path(r"C:\Codex\DanbooruTagTool\data\source\danbooru-2026-09-02.csv"))
    args = parser.parse_args()
    validate(COHORT, SOURCES, MEMBERS, DECISIONS, expected_size=BASELINE_SIZE, roots_path=ROOTS)
    decisions = {r["canonical_character"]: r for r in read_csv(DECISIONS)}
    open_tags = {tag for tag, r in decisions.items() if r["research_state"] == "UNRESEARCHED"}
    root_set = {r["copyright_canonical"] for r in read_csv(ROOTS)}
    catalog_by_tag = catalog(args.tag_catalog)
    member_routes: dict[str, set[str]] = defaultdict(set)
    candidate_home_routes: dict[str, set[str]] = defaultdict(set)
    graph_root_hints: dict[str, set[str]] = defaultdict(set)
    variant_routes: dict[str, set[str]] = defaultdict(set)
    graph_rows = read_csv(args.graph)
    family_home_routes: dict[str, set[str]] = defaultdict(set)
    for row in graph_rows:
        if (row.get("subject_type") == "Family" and row.get("relation_type") == "FAMILY_HOME"
                and row.get("object_type") == "Copyright" and row.get("object_key") in root_set
                and row.get("review_state") in {"VALIDATED", "CANDIDATE"}):
            family_home_routes[row["subject_key"]].add(row["object_key"])
    for row in graph_rows:
        tag = row.get("subject_key", "").strip()
        relation, review = row.get("relation_type", ""), row.get("review_state", "")
        if tag not in open_tags:
            continue
        if row.get("subject_type") == "Character" and relation == "MEMBER_OF" and row.get("object_type") == "Family":
            family = row.get("object_key", "")
            member_routes[tag].add(family)
            if family in root_set:
                graph_root_hints[tag].add(family)
            graph_root_hints[tag].update(family_home_routes.get(family, set()))
        if (row.get("subject_type") == "Character" and relation in {"DISCOVERY_HINT", "MEMBER_OF"}
                and row.get("object_key", "") in root_set):
            graph_root_hints[tag].add(row["object_key"])
        if (row.get("subject_type") == "Character" and relation == "DIRECT_HOME"
                and row.get("object_type") == "Copyright" and review == "CANDIDATE"):
            root = row.get("object_key", "")
            if root in root_set:
                candidate_home_routes[tag].add(root)
        if (row.get("subject_type") == "Character" and relation == "VARIANT_OF"
                and row.get("object_type") == "Character"):
            variant_routes[tag].add(row.get("object_key", ""))

    validated_variant_bases: dict[str, set[str]] = defaultdict(set)
    if VARIANTS.exists():
        for row in read_csv(VARIANTS):
            if row.get("scope") == "VARIANT_CHARACTER" and row.get("validation_state") == "PASS":
                validated_variant_bases[row.get("key", "")].add(row.get("base_character", ""))
    direct_rows = [r for r in read_csv(ISSUE216 / "DANBOORU_NORMALIZED_SEMANTIC_RELATIONS_V1.csv")
                   if r.get("antecedent_category") == "4" and r.get("consequent_category") == "3"
                   and r.get("antecedent_canonical") in open_tags and r.get("consequent_canonical") in root_set]
    direct_roots: dict[str, set[str]] = defaultdict(set)
    for row in direct_rows:
        direct_roots[row["antecedent_canonical"]].add(row["consequent_canonical"])

    # Exact qualifier signals are routing-only. A validated Issue #180 FAMILY_HOME
    # must exist; parsing by itself never creates authority or closes a row.
    family_homes: dict[str, set[str]] = defaultdict(set)
    seed = ROOT / "docs/issue180/v3/migrated_evidence_seed_v3.csv"
    if seed.exists():
        for row in read_csv(seed):
            if (row.get("subject_type") == "Family" and row.get("relation_type") == "FAMILY_HOME"
                    and row.get("review_state") == "VALIDATED"):
                family_homes[row["subject_key"].strip()].add(row["object_key"].strip())
    qualifier_routes: dict[str, set[str]] = defaultdict(set)
    artist_qualified: set[str] = set()
    for tag in open_tags:
        if tag.endswith(")") and "_(" in tag:
            family = tag.rsplit("_(", 1)[1][:-1]
            if family in catalog_by_tag and catalog_by_tag[family] == "1":
                artist_qualified.add(tag)
            if len(family_homes.get(family, set())) == 1:
                qualifier_routes[tag].add(family)

    rows: list[dict[str, str]] = []
    counts: Counter[str] = Counter()
    for tag in sorted(open_tags):
        direct = direct_roots.get(tag, set())
        accepted_conflict = decisions[tag].get("validated_home_candidates", "")
        if len(direct) > 1:
            category, signal = "C_MULTIPLE_COPYRIGHT_IMPLICATION_CONFLICT", "exact active direct relations; no ranked HOME"
        elif tag in validated_variant_bases or variant_routes.get(tag):
            category, signal = "B_VARIANT_IDENTITY_MISSING", "existing variant ledger or graph edge; base relation must be reviewed"
        elif tag in artist_qualified:
            category, signal = "D_CREATOR_ARTIST_QUALIFIED_OC", "exact artist-category terminal qualifier; routing signal only"
        elif candidate_home_routes.get(tag) or graph_root_hints.get(tag):
            category, signal = "A_DIRECT_IMPLICATION_MISSING_BUT_STRONG_IP_ROUTE", "Issue #180 family/direct-home/discovery route; routing only, not HOME evidence"
        elif qualifier_routes.get(tag):
            category, signal = "A_DIRECT_IMPLICATION_MISSING_BUT_STRONG_IP_ROUTE", "validated Issue #180 family qualifier route; routing only"
        elif member_routes.get(tag):
            category, signal = "H_OTHER_LONG_TAIL", "exact family relation exists but no canonical HOME root route is available"
        elif not (candidate_home_routes.get(tag) or graph_root_hints.get(tag) or variant_routes.get(tag)
                  or qualifier_routes.get(tag) or direct):
            category, signal = "G_ROOTLESS_IN_FROZEN_STRUCTURAL_GRAPH", "no exact route in frozen structure graph or implication snapshot"
        else:
            category, signal = "H_OTHER_LONG_TAIL", "requires route-specific census"
        # E/F require explicit non-work or platform/company evidence. This input set
        # has no such accepted relation; keep those classifications unresolved.
        route_roots = set(candidate_home_routes.get(tag, set())) | set(graph_root_hints.get(tag, set())) | set(direct)
        route_text = []
        if member_routes.get(tag):
            route_text.append("family=" + "|".join(sorted(filter(None, member_routes[tag]))))
        if graph_root_hints.get(tag):
            route_text.append("root_hint=" + "|".join(sorted(graph_root_hints[tag])))
        if qualifier_routes.get(tag):
            route_text.append("qualifier=" + "|".join(sorted(qualifier_routes[tag])))
        if validated_variant_bases.get(tag):
            route_text.append("validated_variant_base=" + "|".join(sorted(filter(None, validated_variant_bases[tag]))))
        if variant_routes.get(tag):
            route_text.append("variant_edge=" + "|".join(sorted(filter(None, variant_routes[tag]))))
        if accepted_conflict:
            route_text.append("decision_conflict=" + accepted_conflict)
        rows.append({
            "canonical_character": tag, "category": category, "route_signal": signal,
            "candidate_roots": "|".join(sorted(filter(None, route_roots))),
            "source_routes": "; ".join(route_text), "terminal_state": "UNRESEARCHED",
        })
        counts[category] += 1

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    all_categories = [
        "A_DIRECT_IMPLICATION_MISSING_BUT_STRONG_IP_ROUTE", "B_VARIANT_IDENTITY_MISSING",
        "C_MULTIPLE_COPYRIGHT_IMPLICATION_CONFLICT", "D_CREATOR_ARTIST_QUALIFIED_OC",
        "E_REAL_PERSON_MASCOT_NON_WORK_CANDIDATE", "F_PLATFORM_COMPANY_GENERIC_FAMILY_CANDIDATE",
        "G_ROOTLESS_IN_FROZEN_STRUCTURAL_GRAPH", "H_OTHER_LONG_TAIL",
    ]
    summary = {
        "cohort_size": BASELINE_SIZE, "unresearched": len(rows),
        "category_counts": {category: counts.get(category, 0) for category in all_categories},
        "classified_rows": len(rows), "creator_artist_qualified_candidate_count": len(artist_qualified),
        "real_person_mascot_nonwork_classified": 0,
        "platform_company_generic_family_classified": 0,
        "nonwork_note": "No Character was closed based on a name/category signal. E/F classifications require accepted explicit semantic authority and are not established by the current input set; possible cases remain in A/G/H for route research.",
        "rootless_note": "G means no exact root/member/variant route in the frozen #180 structural graph or implication snapshot. It does not claim that external/curated authority is unavailable.",
        "routing_only": True, "candidate_root_is_not_HOME_evidence": True,
        "source_file": "DANBOORU_NORMALIZED_SEMANTIC_RELATIONS_V1.csv",
        "structure_graph_sha256": __import__("hashlib").sha256(args.graph.read_bytes()).hexdigest(),
    }
    OUT_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"wrote {OUT_CSV}")


if __name__ == "__main__":
    main()
