#!/usr/bin/env python3
"""Build per-character accounting for exact Issue #216 authority routes.

Route outcomes are local to the named route. In particular, a complete roster
can exhaust that source scope only; it cannot negate other HOME possibilities.
Candidate Copyright roots are routing data and remain UNCHECKED until an
accepted membership source proves an exact relationship.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

try:
    from scripts.issue216.authority_coverage import read_csv
except ModuleNotFoundError:  # direct script execution from the repository checkout
    from authority_coverage import read_csv

ROOT = Path(__file__).resolve().parents[2]
ISSUE216 = ROOT / "docs/issue216"
ISSUE180 = ROOT / "docs/issue180"
COHORT = ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv"
DECISIONS = ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv"
SOURCES = ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv"
MEMBERS = ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv"
ROOTS = ISSUE216 / "COPYRIGHT_ROOTS_V1.csv"
SCOUTS = ISSUE216 / "ROSTER_SCOUT_INVENTORY_V1.csv"
RELATIONS = ISSUE216 / "DANBOORU_NORMALIZED_SEMANTIC_RELATIONS_V1.csv"
IMPLICATION_MANIFEST = ISSUE216 / "DANBOORU_ACTIVE_COPYRIGHT_IMPLICATIONS_SNAPSHOT_V1.json"
VARIANTS = ISSUE180 / "autonomous/decisions/variants_verified_v4.csv"
SEED = ISSUE180 / "v3/migrated_evidence_seed_v3.csv"
ROOT_MAP = ISSUE180 / "evidence/exact_root_semantic_authority_batch02.csv"
OUT_CSV = ISSUE216 / "AUTHORITY_ROUTE_ACCOUNTING_V1.csv"
OUT_JSON = ISSUE216 / "AUTHORITY_ROUTE_ACCOUNTING_V1.json"
EXPECTED_GRAPH_SHA256 = "218cf30cb21695472e276cce327cd96a132665f3473c8925954059c3432c4bea"
FIELDS = [
    "canonical_character", "route_type", "route_key", "route_state", "candidate_root",
    "source_id", "source_url", "source_scope", "scope_fingerprint", "source_fingerprint",
    "reviewed_at", "evidence_copyright_root", "evidence_ref", "route_reason",
]
ALLOWED_STATES = {"POSITIVE", "NEGATIVE_COMPLETE", "AMBIGUOUS", "CONFLICT", "NOT_APPLICABLE", "UNCHECKED"}


def split_set(value: str) -> set[str]:
    return {part.strip() for part in (value or "").split("|") if part.strip()}


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _root_routes(graph_path: Path, open_tags: set[str], root_set: set[str]) -> tuple[dict[str, set[str]], dict[str, set[str]]]:
    graph = read_csv(graph_path)
    family_home: dict[str, set[str]] = defaultdict(set)
    for row in graph:
        if (row.get("subject_type") == "Family" and row.get("relation_type") == "FAMILY_HOME"
                and row.get("object_type") == "Copyright" and row.get("review_state") == "VALIDATED"
                and row.get("object_key") in root_set):
            family_home[row.get("subject_key", "")].add(row["object_key"])
    routes: dict[str, set[str]] = defaultdict(set)
    variant_routes: dict[str, set[str]] = defaultdict(set)
    for row in graph:
        tag = row.get("subject_key", "").strip()
        if tag not in open_tags:
            continue
        relation = row.get("relation_type", "")
        if (row.get("subject_type") == "Character" and relation in {"DISCOVERY_HINT", "DIRECT_HOME"}
                and row.get("object_key", "") in root_set):
            routes[tag].add(row["object_key"])
        if (row.get("subject_type") == "Character" and relation == "MEMBER_OF"
                and row.get("object_type") == "Family"):
            family = row.get("object_key", "")
            if family in root_set:
                routes[tag].add(family)
            routes[tag].update(family_home.get(family, set()))
        if (row.get("subject_type") == "Character" and relation == "VARIANT_OF"
                and row.get("object_type") == "Character"):
            variant_routes[tag].add(row.get("object_key", ""))
    return routes, variant_routes


def _validated_family_homes() -> dict[str, set[str]]:
    homes: dict[str, set[str]] = defaultdict(set)
    for row in read_csv(SEED):
        if (row.get("subject_type") == "Family" and row.get("relation_type") == "FAMILY_HOME"
                and row.get("review_state") == "VALIDATED"):
            homes[row.get("subject_key", "").strip()].add(row.get("object_key", "").strip())
    for row in read_csv(ROOT_MAP):
        if row.get("root_review") == "PASS":
            homes[row.get("family", "").strip()].add(row.get("home_copyright", "").strip())
    return {key: {value for value in values if value} for key, values in homes.items()}


def qualifier_memberships(tag: str, family_homes: dict[str, set[str]], root_set: set[str]) -> set[str]:
    homes: set[str] = set()
    for family, values in family_homes.items():
        suffix = f"_({family})"
        if len(values) == 1 and tag.endswith(suffix) and ")_(" not in tag[:-len(suffix)]:
            home = next(iter(values))
            if home in root_set:
                homes.add(home)
    return homes


def roster_route_state(tag: str, scope: dict[str, str]) -> tuple[str, str]:
    if tag in split_set(scope.get("exact_cohort_members", "")):
        return "POSITIVE", "Exact canonical cohort member appears in the extracted roster surface."
    if tag in split_set(scope.get("ambiguous_members", "")):
        return "AMBIGUOUS", "Roster surface has competing or unresolved canonical identities."
    if scope.get("review_state", "").upper() == "SCOUTED" and scope.get("completeness", "").upper() == "COMPLETE":
        return "NEGATIVE_COMPLETE", "No exact cohort identity in this explicitly COMPLETE roster scope; this exhausts only this source route."
    return "UNCHECKED", "Roster scope is partial, unknown, or only rejoined from retained member records; absence is not evidence."


def build(graph_path: Path) -> tuple[list[dict[str, str]], dict[str, object]]:
    graph_hash = file_hash(graph_path)
    if graph_hash != EXPECTED_GRAPH_SHA256:
        raise ValueError(f"frozen Issue #180 structure graph hash mismatch: {graph_hash}")
    cohort = read_csv(COHORT)
    decisions = {row["canonical_character"]: row for row in read_csv(DECISIONS)}
    sources = {row["source_id"]: row for row in read_csv(SOURCES)}
    members = read_csv(MEMBERS)
    roots = {row["copyright_canonical"] for row in read_csv(ROOTS)}
    open_tags = {tag for tag, row in decisions.items() if row["research_state"] == "UNRESEARCHED"}
    if len(cohort) != 13_983 or len(open_tags) != sum(row["research_state"] == "UNRESEARCHED" for row in decisions.values()):
        raise ValueError("frozen cohort or current decision ledger is inconsistent")

    graph_routes, graph_variants = _root_routes(graph_path, open_tags, roots)
    family_homes = _validated_family_homes()
    implication = json.loads(IMPLICATION_MANIFEST.read_text(encoding="utf-8-sig"))
    snapshot_hash = implication["snapshot_sha256"]
    snapshot_source = next((row for row in sources.values()
                            if row.get("source_type") == "DANBOORU_ACTIVE_COPYRIGHT_IMPLICATION"
                            and snapshot_hash in row.get("provenance", "")), None)
    if not snapshot_source:
        raise ValueError("active implication snapshot source is missing from the authority registry")
    direct_by_tag: dict[str, set[str]] = defaultdict(set)
    for row in read_csv(RELATIONS):
        if (row.get("status") == "active" and row.get("antecedent_category") == "4"
                and row.get("consequent_category") == "3" and row.get("antecedent_canonical") in open_tags
                and row.get("consequent_canonical") in roots):
            direct_by_tag[row["antecedent_canonical"]].add(row["consequent_canonical"])

    exact_members_by_tag: dict[str, list[tuple[dict[str, str], dict[str, str]]]] = defaultdict(list)
    for member in members:
        source = sources.get(member.get("source_id", ""))
        if (source and source.get("source_status") == "ACCEPTED" and member.get("mapping_status") == "EXACT_COVERED"
                and member.get("canonical_character") in open_tags):
            exact_members_by_tag[member["canonical_character"]].append((source, member))

    variant_by_tag: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_csv(VARIANTS):
        if (row.get("scope") == "VARIANT_CHARACTER" and row.get("validation_state") == "PASS"
                and row.get("key", "").strip() in open_tags):
            variant_by_tag[row["key"].strip()].append(row)

    scouts_by_root: dict[str, list[dict[str, str]]] = defaultdict(list)
    for scope in read_csv(SCOUTS):
        if scope.get("candidate_root", "").strip() in roots:
            scouts_by_root[scope["candidate_root"].strip()].append(scope)

    rows: list[dict[str, str]] = []

    def add(tag: str, route_type: str, route_key: str, state: str, *, root: str = "", source: dict[str, str] | None = None,
            fingerprint: str = "", evidence_root: str = "", evidence_ref: str = "", reason: str = "") -> None:
        if state not in ALLOWED_STATES:
            raise ValueError(f"invalid route state {state}")
        source = source or {}
        scope = source.get("source_scope", "")
        rows.append({
            "canonical_character": tag, "route_type": route_type, "route_key": route_key,
            "route_state": state, "candidate_root": root, "source_id": source.get("source_id", ""),
            "source_url": source.get("source_url", ""), "source_scope": scope,
            "scope_fingerprint": hashlib.sha256(scope.encode("utf-8")).hexdigest() if scope else "",
            "source_fingerprint": fingerprint, "reviewed_at": source.get("reviewed_at", ""),
            "evidence_copyright_root": evidence_root, "evidence_ref": evidence_ref, "route_reason": reason,
        })

    for tag in sorted(open_tags):
        direct = direct_by_tag.get(tag, set())
        if direct:
            for home in sorted(direct):
                add(tag, "DANBOORU_ACTIVE_COPYRIGHT_IMPLICATION", f"{snapshot_hash}:{home}", "POSITIVE",
                    root=home, source=snapshot_source, fingerprint=snapshot_hash,
                    evidence_root=home, evidence_ref="active implication ID recorded in normalized relation table",
                    reason="Exact active direct Character-to-Copyright relationship in a frozen reusable snapshot.")
        else:
            add(tag, "DANBOORU_ACTIVE_COPYRIGHT_IMPLICATION", snapshot_hash, "NEGATIVE_COMPLETE",
                source=snapshot_source, fingerprint=snapshot_hash,
                evidence_ref="complete active consequent-Copyright snapshot and exact canonical join",
                reason="No exact active direct Character-to-Copyright relation; this does not deny membership established by another route.")

        qualifier_homes = qualifier_memberships(tag, family_homes, roots)
        if qualifier_homes:
            for home in sorted(qualifier_homes):
                add(tag, "VALIDATED_QUALIFIER", home, "POSITIVE", root=home, evidence_root=home,
                    evidence_ref="exact terminal qualifier joined through validated Issue #180 FAMILY_HOME",
                    reason="Validated exact qualifier route; candidate tag text alone was not used.")
        else:
            add(tag, "VALIDATED_QUALIFIER", "issue180-validated-family-qualifier-index", "NOT_APPLICABLE",
                evidence_ref="deterministic exhaustive join against validated Issue #180 FAMILY_HOME rows",
                reason="No unique exact supported terminal Copyright qualifier applies to this Character.")

        variants = variant_by_tag.get(tag, [])
        if variants:
            for variant in variants:
                base = variant.get("base_character", "").strip()
                base_decision = decisions.get(base, {})
                home = variant.get("home_copyright", "").strip()
                state = "POSITIVE" if (base_decision.get("research_state") == "HOME_CONFIRMED"
                                        and base_decision.get("home_copyright") == home and home in roots) else "UNCHECKED"
                add(tag, "VALIDATED_VARIANT_BASE", f"{tag}->{base}", state, root=home,
                    source={"source_url": variant.get("evidence_url", ""),
                            "source_scope": variant.get("evidence_claim", ""),
                            "reviewed_at": variant.get("reviewed_at", "")},
                    fingerprint=file_hash(VARIANTS), evidence_root=home if state == "POSITIVE" else "",
                    evidence_ref=f"PASS variant ledger row; base decision state={base_decision.get('research_state', 'missing')}",
                    reason="Validated exact variant identity; HOME inheritance requires the same confirmed base root.")
        elif graph_variants.get(tag):
            for base in sorted(filter(None, graph_variants[tag])):
                add(tag, "CANDIDATE_VARIANT_IDENTITY", f"{tag}->{base}", "UNCHECKED",
                    evidence_ref=f"frozen graph VARIANT_OF route to {base}",
                    reason="Structural edge is routing context; exact variant identity and base HOME require validation.")
        else:
            add(tag, "VALIDATED_VARIANT_BASE", "issue180-validated-variant-ledger", "NOT_APPLICABLE",
                evidence_ref=f"complete validated variant ledger SHA-256 {file_hash(VARIANTS)}",
                reason="No exact PASS variant/base edge is present for this Character.")

        exact = exact_members_by_tag.get(tag, [])
        if exact:
            for source, member in exact:
                home = member.get("canonical_home_root", "").strip() or source.get("copyright_canonical", "")
                member_route_key = f"{source['source_id']}:{member.get('member_relation_id', '')}"
                add(tag, "ACCEPTED_EXACT_MEMBERSHIP", member_route_key, "POSITIVE", root=home,
                    source=source, fingerprint=member.get("member_relation_id", ""), evidence_root=home,
                    evidence_ref=member.get("mapping_evidence", ""),
                    reason="Existing accepted exact source/member mapping rejoined to a currently open cohort Character.")
        else:
            add(tag, "ACCEPTED_EXACT_MEMBERSHIP", "current-accepted-source-member-join", "UNCHECKED",
                evidence_ref=f"deterministic join over {len(sources)} registry records and {len(members)} member rows",
                reason="No exact member row was retained for this Character; incomplete or unlisted sources do not exhaust this route.")

        for candidate_root in sorted(graph_routes.get(tag, set())):
            add(tag, "CANDIDATE_ROOT_ROUTE", candidate_root, "UNCHECKED", root=candidate_root,
                evidence_ref="frozen #180 structural graph candidate route",
                reason="Routing hint only; no HOME authority is implied.")
            for scope in scouts_by_root.get(candidate_root, []):
                state, reason = roster_route_state(tag, scope)
                source = sources.get(scope.get("source_id", ""), {
                    "source_id": scope.get("source_id", ""), "source_url": scope.get("source_url", ""),
                    "source_scope": scope.get("roster_scope", ""), "reviewed_at": scope.get("reviewed_at", ""),
                })
                scope_route_key = ":".join(filter(None, (
                    candidate_root,
                    scope.get("source_id", ""),
                    scope.get("source_fingerprint", ""),
                    hashlib.sha256(scope.get("roster_scope", "").encode("utf-8")).hexdigest()[:12],
                )))
                add(tag, "OFFICIAL_OR_CURATED_ROSTER_SCOPE", scope_route_key, state,
                    root=candidate_root, source=source,
                    fingerprint=scope.get("source_fingerprint", ""),
                    # An exact roster identity proves membership in its reviewed scope;
                    # the candidate root remains routing metadata until root normalization.
                    evidence_ref=scope.get("source_url", ""), reason=reason)

    rows.sort(key=lambda row: (row["canonical_character"], row["route_type"], row["route_key"], row["source_id"]))
    duplicates = [(r["canonical_character"], r["route_type"], r["route_key"], r["source_id"]) for r in rows]
    if len(duplicates) != len(set(duplicates)):
        seen: set[tuple[str, str, str, str]] = set()
        repeated = []
        for key in duplicates:
            if key in seen:
                repeated.append(key)
            seen.add(key)
        raise ValueError(f"duplicate Character/route rows: {repeated[:10]}")
    summary = {
        "cohort_size": len(cohort), "current_unresearched": len(open_tags),
        "route_row_count": len(rows), "unique_characters_with_routes": len({row["canonical_character"] for row in rows}),
        "route_state_counts": {state: sum(row["route_state"] == state for row in rows) for state in sorted(ALLOWED_STATES)},
        "route_type_counts": {kind: sum(row["route_type"] == kind for row in rows)
                              for kind in sorted({row["route_type"] for row in rows})},
        "snapshot_sha256": snapshot_hash, "structure_graph_sha256": graph_hash,
        "candidate_root_is_not_HOME_evidence": True,
        "complete_roster_absence_scope": "Only that exact source_id route; never global Character HOME denial.",
        "unresearched_terminalized_by_route_build": 0,
    }
    return rows, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUT_CSV)
    parser.add_argument("--summary", type=Path, default=OUT_JSON)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output, summary = build(args.graph)
    if args.check:
        if read_csv(args.output) != output or json.loads(args.summary.read_text(encoding="utf-8-sig")) != summary:
            raise SystemExit("per-character authority route ledger differs from deterministic rebuild")
        print(f"route accounting deterministic rebuild: PASS ({summary['route_row_count']} rows / {summary['current_unresearched']} open)")
        return
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(output)
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"built {summary['route_row_count']} per-character route rows for {summary['current_unresearched']} open Characters")


if __name__ == "__main__":
    main()
