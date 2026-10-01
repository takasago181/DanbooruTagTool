#!/usr/bin/env python3
"""Annotate the live Issue #216 queue with measured roster-yield signals.

Scout inventories are routing metadata only. They cannot establish HOME. Exact
open matches must be listed explicitly in the inventory and are rejoined to the
current decision ledger on every build so stale slices disappear automatically.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from urllib.parse import urlparse
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.issue216.build_source_yield_queue import ISSUE216, ROOT, build as build_v1, read_csv, write_csv

SCOUT_DEFAULT = ISSUE216 / "ROSTER_SCOUT_INVENTORY_V1.csv"
OUT_CSV = ISSUE216 / "SOURCE_YIELD_QUEUE_V2.csv"
OUT_JSON = ISSUE216 / "SOURCE_YIELD_QUEUE_V2.json"
FIELDS = [
    "candidate_root", "unresolved_count", "top500_count", "top2000_count",
    "total_post_count_sum", "max_post_count", "known_official_source_count",
    "reusable_accepted_source_count", "existing_exact_mappings", "remaining_unmapped_count",
    "open_exact_candidate_count", "review_required_count", "expected_safe_yield",
    "yield_state", "explicit_roster_status", "roster_scope_completeness",
    "roster_surface_count", "exact_cohort_match_count", "open_exact_roster_matches",
    "ambiguous_roster_matches", "source_scopes_reviewed", "terminalized_from_reviewed_sources",
    "empirical_terminalized_per_source", "zero_yield_source_count", "source_family",
    "source_family_empirical_yield", "route_exhausted", "priority_class", "priority_rank",
]


def split_set(value: str) -> set[str]:
    return {part.strip() for part in (value or "").split("|") if part.strip()}


def classify_yield(*, existing_open: int, roster_open: int, reviewed_scopes: int,
                   all_reviewed_complete: bool, family_positive: int, roster_found: bool,
                   registered_roster: bool, roster_likelihood: bool,
                   high_frequency: bool, unresolved: int) -> tuple[str, int]:
    """Classify measured/estimated yield without converting UNKNOWN into zero."""
    if existing_open:
        return "KNOWN_POSITIVE", 0
    if roster_open:
        return "KNOWN_POSITIVE", 1
    if reviewed_scopes and all_reviewed_complete:
        return "KNOWN_ZERO", 6
    if family_positive:
        return "ESTIMATED", 2
    if roster_found or registered_roster:
        return "UNKNOWN", 3
    if roster_likelihood and unresolved >= 20:
        return "UNKNOWN", 4
    if high_frequency:
        return "UNKNOWN", 5
    return "UNKNOWN", 6


def _source_family_yields() -> dict[str, tuple[float, int, int]]:
    sources = read_csv(ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv")
    members = read_csv(ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv")
    decisions = {r["canonical_character"]: r for r in read_csv(ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv")}
    by_family: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for source in sources:
        if (source.get("source_status") != "ACCEPTED" or source.get("reusable", "").lower() != "true"
                or source.get("exact_roster_available", "").lower() != "true"):
            continue
        host = urlparse(source.get("source_url", "")).hostname or ""
        keys = {source.get("source_type", ""), source.get("authority_owner", ""), host}
        for family in keys - {""}:
            by_family[family][source["source_id"]] = set()
    source_by_id = {r["source_id"]: r for r in sources}
    for member in members:
        source = source_by_id.get(member.get("source_id", ""))
        if (not source or source.get("source_status") != "ACCEPTED"
                or source.get("reusable", "").lower() != "true"
                or source.get("exact_roster_available", "").lower() != "true"
                or member.get("mapping_status") != "EXACT_COVERED"):
            continue
        decision = decisions.get(member.get("canonical_character", ""), {})
        if decision.get("research_state") == "UNRESEARCHED":
            continue
        host = urlparse(source.get("source_url", "")).hostname or ""
        keys = {source.get("source_type", ""), source.get("authority_owner", ""), host}
        for family in keys - {""}:
            by_family[family][source["source_id"]].add(member["canonical_character"])
    result = {}
    for family, source_members in by_family.items():
        yields = [len(tags) for tags in source_members.values()]
        if yields:
            result[family] = (sum(yields) / len(yields), sum(y > 0 for y in yields), sum(y == 0 for y in yields))
    return result


def build_v2(master: Path, graph: Path, post_counts: Path | None, scout_path: Path):
    _, base_queue, summary = build_v1(master, graph, post_counts)
    decisions = {r["canonical_character"]: r for r in read_csv(ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv")}
    open_tags = {tag for tag, row in decisions.items() if row["research_state"] == "UNRESEARCHED"}
    members_by_source: dict[str, set[str]] = defaultdict(set)
    for member in read_csv(ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv"):
        if member.get("mapping_status") == "EXACT_COVERED":
            state = decisions.get(member.get("canonical_character", ""), {}).get("research_state", "")
            if state and state != "UNRESEARCHED":
                members_by_source[member["source_id"]].add(member["canonical_character"])
    scouts = read_csv(scout_path) if scout_path.exists() else []
    scouts_by_root: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in scouts:
        root = row.get("candidate_root", "").strip()
        if root:
            scouts_by_root[root].append(row)
    family_yields = _source_family_yields()
    output = []
    for base in base_queue:
        root = base["candidate_root"]
        rows = scouts_by_root.get(root, [])
        open_roster_tags = set().union(*(split_set(r.get("exact_open_members", "")) for r in rows)) if rows else set()
        open_roster_tags &= open_tags
        exact_cohort_tags = set().union(*(split_set(r.get("exact_cohort_members", "")) for r in rows)) if rows else set()
        ambiguous_tags = set().union(*(split_set(r.get("ambiguous_members", "")) for r in rows)) if rows else set()
        reviewed_rows = [r for r in rows if r.get("review_state", "").upper() in {"SCOUTED", "REGISTRY_REJOIN"}]
        actual_scout_rows = [r for r in reviewed_rows if r.get("review_state", "").upper() == "SCOUTED"]
        explicit = "FOUND" if any(r.get("roster_status", "").upper() == "FOUND" for r in reviewed_rows) else (
            "NOT_FOUND" if reviewed_rows and all(r.get("roster_status", "").upper() == "NOT_FOUND" for r in reviewed_rows) else "UNKNOWN")
        completeness = "COMPLETE" if any(r.get("completeness", "").upper() == "COMPLETE" for r in reviewed_rows) else (
            "PARTIAL" if any(r.get("completeness", "").upper() == "PARTIAL" for r in reviewed_rows) else "UNKNOWN")
        known_surface_counts = [int(r["roster_surface_count"]) for r in reviewed_rows if r.get("roster_surface_count", "").strip()]
        surface_count = max(known_surface_counts, default="")
        family = next((r.get("source_family", "").strip() for r in rows if r.get("source_family", "").strip()), "")
        empirical, family_positive, family_zero = family_yields.get(family, (0.0, 0, 0))
        reviewed_source_ids = {r.get("source_id", "").strip() for r in reviewed_rows if r.get("source_id", "").strip()}
        member_source_by_id = {sid: members_by_source[sid] for sid in reviewed_source_ids if members_by_source.get(sid)}
        terminalized = len(set().union(*member_source_by_id.values())) if member_source_by_id else 0
        exact_existing_open = int(base.get("open_exact_candidate_count", "0") or 0)
        yield_state, priority = classify_yield(
            existing_open=exact_existing_open,
            roster_open=len(open_roster_tags),
            reviewed_scopes=len(reviewed_rows),
            all_reviewed_complete=bool(reviewed_rows) and all(r.get("completeness", "").upper() == "COMPLETE" for r in reviewed_rows),
            family_positive=family_positive,
            roster_found=explicit == "FOUND",
            registered_roster=base.get("source_yield_class") == "REVIEW_REGISTERED_SOURCE_SCOPE",
            roster_likelihood=int(base.get("known_official_source_count", "0") or 0) > 0,
            high_frequency=bool(int(base.get("top500_count", "0") or 0) or int(base.get("top2000_count", "0") or 0)),
            unresolved=int(base.get("unresolved_count", "0") or 0),
        )
        # A complete roster can exhaust a researched route, but does not terminalize
        # a Character or disprove its HOME. This flag is deliberately scope-local.
        route_exhausted = "SCOPE_EXHAUSTED" if reviewed_rows and completeness == "COMPLETE" and not open_roster_tags else "NO"
        values = {
            **{k: base.get(k, "") for k in ("candidate_root", "unresolved_count", "top500_count", "top2000_count",
                "total_post_count_sum", "max_post_count", "known_official_source_count", "reusable_accepted_source_count",
                "existing_exact_mappings", "remaining_unmapped_count", "open_exact_candidate_count", "review_required_count", "expected_safe_yield")},
            "yield_state": yield_state, "explicit_roster_status": explicit,
            "roster_scope_completeness": completeness, "roster_surface_count": str(surface_count),
            "exact_cohort_match_count": str(len(exact_cohort_tags)), "open_exact_roster_matches": str(len(open_roster_tags)),
            "ambiguous_roster_matches": str(len(ambiguous_tags)), "source_scopes_reviewed": str(len(reviewed_rows)),
            "terminalized_from_reviewed_sources": str(terminalized), "empirical_terminalized_per_source": f"{empirical:.3f}",
            "zero_yield_source_count": str(sum(not split_set(r.get("exact_open_members", "")) for r in reviewed_rows)), "source_family": family,
            "source_family_empirical_yield": f"{empirical:.3f}", "route_exhausted": route_exhausted,
            "priority_class": str(priority), "priority_rank": "",
        }
        output.append(values)
    output.sort(key=lambda r: (int(r["priority_class"]), -int(r["open_exact_roster_matches"]),
        -float(r["source_family_empirical_yield"]), -int(r["remaining_unmapped_count"]),
        -int(r["top500_count"] or 0), -int(r["top2000_count"] or 0),
        -int(r["total_post_count_sum"] or 0), r["candidate_root"]))
    for i, row in enumerate(output, 1):
        row["priority_rank"] = str(i)
    summary = {**summary,
        "schema_version": "issue216-source-yield-queue-v2",
        "yield_state_counts": {state: sum(r["yield_state"] == state for r in output) for state in ("KNOWN_POSITIVE", "KNOWN_ZERO", "ESTIMATED", "UNKNOWN")},
        "scouted_root_count": len({r.get("candidate_root", "") for r in scouts if r.get("review_state", "").upper() == "SCOUTED"}),
        "scouted_source_scope_count": sum(r.get("review_state", "").upper() == "SCOUTED" for r in scouts),
        "registry_rejoined_source_scope_count": sum(r.get("review_state", "").upper() == "REGISTRY_REJOIN" for r in scouts),
        "queue_order": "Current accepted exact open mappings; measured exact open roster overlap; empirical source-family yield; explicit roster found awaiting extraction; high unresolved/top cohort routes; unknown tail. Post counts are routing tie-breaks only; expected_safe_yield v1 is retained for history but ignored for order.",
        "scout_inventory": str(scout_path),
        "note": "Yield/status/route fields are scheduling metadata only. KNOWN_ZERO and SCOPE_EXHAUSTED are limited to the reviewed COMPLETE source scopes; they do not establish root-wide or Character-wide nonmembership and never establish or deny HOME.",
    }
    return output, summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", type=Path, required=True)
    parser.add_argument("--graph", type=Path, required=True)
    default_post_counts = ROOT / "docs/issue70/data/source/character_copyright_evidence_full.csv.gz"
    parser.add_argument("--post-counts", type=Path, default=default_post_counts if default_post_counts.exists() else None)
    parser.add_argument("--scout-inventory", type=Path, default=SCOUT_DEFAULT)
    parser.add_argument("--output", type=Path, default=OUT_CSV)
    parser.add_argument("--summary", type=Path, default=OUT_JSON)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    queue, summary = build_v2(args.master, args.graph, args.post_counts, args.scout_inventory)
    if args.check:
        if read_csv(args.output) != queue or json.loads(args.summary.read_text(encoding="utf-8")) != summary:
            raise SystemExit("source-yield queue v2 differs from deterministic reconstruction")
        print(f"source-yield queue v2 reproducibility: PASS ({len(queue)} roots; {summary['currently_unresearched']} open rows)")
        return
    write_csv(args.output, FIELDS, queue)
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"source-yield queue v2 built: {len(queue)} roots; open={summary['currently_unresearched']}; "
        f"scouted={summary['scouted_root_count']}; yields={summary['yield_state_counts']}")


if __name__ == "__main__":
    main()
