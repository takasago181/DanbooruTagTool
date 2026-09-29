#!/usr/bin/env python3
"""Build a source-first Issue #216 research queue from frozen #180 candidate hints.

Candidate edges and post counts are priority metadata only. They never confirm a HOME.
All ignored #180 inputs are read-only and must be supplied explicitly by the operator.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ISSUE216 = ROOT / "docs/issue216"
MASTER_SHA256 = "135463a5225b6501db923322284f8e309f217eb5359538088eb6de6d78b77071"
BASELINE = 13_983


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def stable(values) -> str:
    return " | ".join(sorted({str(v).strip() for v in values if str(v).strip()}))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build(master_path: Path, graph_path: Path, post_counts_path: Path):
    master_hash = sha256(master_path)
    if master_hash != MASTER_SHA256:
        raise ValueError(f"#180 master SHA mismatch: expected {MASTER_SHA256}, got {master_hash}")
    master = read_csv(master_path)
    unresolved = {
        row["canonical_tag"]: row for row in master if row["final_state"] == "HOME_UNRESOLVED"
    }
    if len(master) != 35_890 or len(unresolved) != BASELINE:
        raise ValueError("#180 master population or unresolved count differs from frozen baseline")

    cohort = {r["canonical_character"] for r in read_csv(ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv")}
    decisions = {r["canonical_character"]: r for r in read_csv(ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv")}
    if cohort != set(unresolved) or set(decisions) != cohort:
        raise ValueError("frozen #216 cohort/decisions do not equal the protected #180 unresolved set")
    open_tags = {tag for tag, row in decisions.items() if row["research_state"] == "UNRESEARCHED"}

    baseline_counts: dict[str, int] = {}
    joined_baseline_tags: set[str] = set()
    with gzip.open(post_counts_path, "rt", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            tag = row["character_tag"]
            if tag in unresolved:
                joined_baseline_tags.add(tag)
                baseline_counts[tag] = max(baseline_counts.get(tag, 0), int(row["character_post_count"]))
    if len(joined_baseline_tags) != 13_881:
        raise ValueError(f"unexpected frozen-baseline post-count join size: {len(joined_baseline_tags)}")
    ranks = {tag: rank for rank, (tag, _) in enumerate(sorted(baseline_counts.items(), key=lambda x: (-x[1], x[0])), 1)}
    counts = {tag: baseline_counts[tag] for tag in open_tags if tag in baseline_counts}

    roots = {r["copyright_canonical"] for r in read_csv(ISSUE216 / "COPYRIGHT_ROOTS_V1.csv")}
    hint_by_tag: dict[str, set[str]] = defaultdict(set)
    graph_rows = read_csv(graph_path)
    for edge in graph_rows:
        tag = edge.get("subject_key", "")
        root = edge.get("object_key", "")
        if tag in open_tags and root in roots and edge.get("relation_type") in {"DISCOVERY_HINT", "MEMBER_OF"}:
            hint_by_tag[tag].add(root)

    # The canonical terminal qualifier is a priority hint only when it names a catalog root.
    for tag in open_tags:
        match = re.search(r"_\(([^()]*)\)$", tag)
        if match and match.group(1) in roots:
            hint_by_tag[tag].add(match.group(1))

    source_rows = read_csv(ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv")
    member_rows = read_csv(ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv")
    sources = {r["source_id"]: r for r in source_rows}
    members_by_root: dict[str, set[str]] = defaultdict(set)
    source_ids_by_root: dict[str, set[str]] = defaultdict(set)
    roster_ids_by_root: dict[str, set[str]] = defaultdict(set)
    reviewed_source_ids: set[str] = set()
    safe_candidate_tags_by_root: dict[str, set[str]] = defaultdict(set)
    review_required_tags_by_root: dict[str, set[str]] = defaultdict(set)
    for source in source_rows:
        root = source["copyright_canonical"]
        if root in roots and source["source_status"] == "ACCEPTED":
            source_ids_by_root[root].add(source["source_id"])
            if (source["exact_roster_available"].lower() == "true"
                    and source["reusable"].lower() == "true"):
                roster_ids_by_root[root].add(source["source_id"])
    for member in member_rows:
        source = sources.get(member["source_id"])
        if (source and source["source_status"] == "ACCEPTED" and source["copyright_canonical"] in roots
                and member["mapping_status"] == "EXACT_COVERED"):
            members_by_root[source["copyright_canonical"]].add(member["canonical_character"])

    # A registered roster at a root does not imply that it covers every Character
    # hinted at that root. Count only exact, unique candidates from a retained source
    # inventory whose source ID, URL, and exact scope still match the accepted registry.
    for candidate_path in sorted(ISSUE216.glob("SOURCE_MAPPING_CANDIDATES_*.csv")):
        for candidate in read_csv(candidate_path):
            source = sources.get(candidate.get("source_id", ""))
            if not source or source["source_status"] != "ACCEPTED":
                continue
            if (candidate.get("source_url") != source["source_url"]
                    or candidate.get("source_scope") != source["source_scope"]):
                continue
            reviewed_source_ids.add(source["source_id"])
            tag = candidate.get("canonical_character", "")
            if tag not in open_tags:
                continue
            root = source["copyright_canonical"]
            if candidate.get("candidate_status") == "AUTO_MAPPING_CANDIDATE":
                safe_candidate_tags_by_root[root].add(tag)
            elif candidate.get("candidate_status") == "REVIEW_REQUIRED":
                review_required_tags_by_root[root].add(tag)

    root_members: dict[str, set[str]] = defaultdict(set)
    for tag in open_tags:
        for root in hint_by_tag.get(tag, set()):
            root_members[root].add(tag)
    # A source-derived candidate can expose a more specific root than a broad catalog
    # hint. Add it to the queue only; this never confirms HOME.
    for root, tags in safe_candidate_tags_by_root.items():
        for tag in tags:
            root_members[root].add(tag)
    for root, tags in review_required_tags_by_root.items():
        for tag in tags:
            root_members[root].add(tag)

    fields = [
        "candidate_root", "hint_kind", "unresolved_count", "top500_count", "top2000_count",
        "total_post_count_sum", "max_post_count", "known_official_source_count",
        "reusable_accepted_source_count", "reviewed_source_count", "likely_roster_availability",
        "existing_exact_mappings", "remaining_unmapped_count", "open_exact_candidate_count",
        "review_required_count", "expected_safe_yield", "source_yield_class", "priority_rank",
    ]
    queue = []
    for root, tags in root_members.items():
        mapped = members_by_root[root] & cohort
        roster_ids = roster_ids_by_root[root]
        counts_for_tags = [counts.get(tag, 0) for tag in tags]
        top500 = sum(ranks.get(tag, 10**9) <= 500 for tag in tags)
        top2000 = sum(ranks.get(tag, 10**9) <= 2000 for tag in tags)
        exact_candidates = safe_candidate_tags_by_root[root] & tags
        review_required = review_required_tags_by_root[root] & tags
        unreviewed_rosters = roster_ids - reviewed_source_ids
        if exact_candidates:
            source_class = "REUSE_SOURCE_EXACT_CANDIDATES"
            availability = "REVIEWED_ROSTER_HAS_EXACT_COHORT_CANDIDATES"
        elif review_required:
            source_class = "REVIEW_SOURCE_IDENTITY_CANDIDATES"
            availability = "REVIEWED_ROSTER_HAS_AMBIGUOUS_COHORT_CANDIDATES"
        elif unreviewed_rosters:
            source_class = "REVIEW_REGISTERED_SOURCE_SCOPE"
            availability = "REGISTERED_ROSTER_NOT_YET_IN_CANDIDATE_INVENTORY"
        elif roster_ids:
            source_class = "DISCOVER_ADDITIONAL_OFFICIAL_SOURCE"
            availability = "REGISTERED_ROSTER_REVIEWED_NO_OPEN_EXACT_MATCH"
        else:
            source_class = "DISCOVER_OFFICIAL_SOURCE"
            availability = "SOURCE_DISCOVERY_REQUIRED"
        queue.append({
            "candidate_root": root,
            "hint_kind": "Issue #180 DISCOVERY_HINT/MEMBER_OF and/or exact terminal qualifier; priority only",
            "unresolved_count": str(len(tags)), "top500_count": str(top500), "top2000_count": str(top2000),
            "total_post_count_sum": str(sum(counts_for_tags)), "max_post_count": str(max(counts_for_tags, default=0)),
            "known_official_source_count": str(len(source_ids_by_root[root])),
            "reusable_accepted_source_count": str(len(roster_ids)),
            "reviewed_source_count": str(len(source_ids_by_root[root] & reviewed_source_ids)),
            "likely_roster_availability": availability,
            "existing_exact_mappings": str(len(mapped)), "remaining_unmapped_count": str(len(tags)),
            "open_exact_candidate_count": str(len(exact_candidates)),
            "review_required_count": str(len(review_required)),
            "expected_safe_yield": str(len(exact_candidates)),
            "source_yield_class": source_class,
            "priority_rank": "",
        })
    # Safe source reuse is based on actual unique exact candidates, not merely the
    # presence of any roster at the same root. Then finish registered source review
    # before source discovery; cohort size/frequency only break ties.
    queue.sort(key=lambda r: (
        -int(r["expected_safe_yield"]),
        {"REUSE_SOURCE_EXACT_CANDIDATES": 0, "REVIEW_SOURCE_IDENTITY_CANDIDATES": 1,
         "REVIEW_REGISTERED_SOURCE_SCOPE": 2, "DISCOVER_ADDITIONAL_OFFICIAL_SOURCE": 3,
         "DISCOVER_OFFICIAL_SOURCE": 4}[r["source_yield_class"]],
        -int(r["remaining_unmapped_count"]), -int(r["top2000_count"]),
        -int(r["total_post_count_sum"]), r["candidate_root"],
    ))
    for i, row in enumerate(queue, 1):
        row["priority_rank"] = str(i)

    # Preserve candidate-root multiplicity for transparency; the same Character can appear under several hints.
    summary = {
        "schema_version": "issue216-source-yield-queue-v1",
        "baseline_unresolved": len(unresolved), "currently_unresearched": len(open_tags),
        "root_count": len(queue), "post_count_joined_open": len(counts),
        "post_count_joined_frozen_baseline": len(joined_baseline_tags),
        "post_count_missing_open": len(open_tags) - len(counts),
        "top500_open": sum(ranks.get(tag, 10**9) <= 500 for tag in open_tags),
        "top2000_open": sum(ranks.get(tag, 10**9) <= 2000 for tag in open_tags),
        "source_registry_count": len(source_rows), "accepted_roster_source_count": sum(
            source["source_status"] == "ACCEPTED" and source["exact_roster_available"].lower() == "true"
            and source["reusable"].lower() == "true"
            for source in source_rows
        ),
        "queue_order": "reviewed source exact-candidate yield, registered source review need, then unresolved/Top2000/post-count priority; candidate edges and frequency are priority-only",
        "protected_master_sha256": master_hash, "candidate_graph_sha256": sha256(graph_path),
        "post_count_sha256": sha256(post_counts_path),
        "note": "expected_safe_yield counts only AUTO_MAPPING_CANDIDATE rows from reviewed inventories matching an accepted source ID, URL, and exact scope; it is a priority estimate, never HOME evidence or a guaranteed decision count.",
    }
    return fields, queue, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", type=Path, required=True)
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--post-counts", type=Path, default=ROOT / "docs/issue70/data/source/character_copyright_evidence_full.csv.gz")
    parser.add_argument("--output", type=Path, default=ISSUE216 / "SOURCE_YIELD_QUEUE_V1.csv")
    parser.add_argument("--summary", type=Path, default=ISSUE216 / "SOURCE_YIELD_QUEUE_V1.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    fields, queue, summary = build(args.master, args.graph, args.post_counts)
    if args.check:
        if read_csv(args.output) != queue or json.loads(args.summary.read_text(encoding="utf-8")) != summary:
            raise SystemExit("source-yield queue differs from deterministic reconstruction")
        print(f"source-yield queue reproducibility: PASS ({len(queue)} roots; {summary['currently_unresearched']} open rows)")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_csv(args.output, fields, queue)
    args.summary.write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"source-yield queue built: {len(queue)} roots; top500 open={summary['top500_open']}; top2000 open={summary['top2000_open']}")


if __name__ == "__main__":
    main()
