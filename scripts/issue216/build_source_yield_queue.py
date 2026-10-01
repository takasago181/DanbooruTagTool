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
SUMMARY_ALIAS = ISSUE216 / "SOURCE_YIELD_QUEUE_SUMMARY_V1.json"
MASTER_SHA256 = "135463a5225b6501db923322284f8e309f217eb5359538088eb6de6d78b77071"
GRAPH_SHA256 = "218cf30cb21695472e276cce327cd96a132665f3473c8925954059c3432c4bea"
POST_COUNTS_SHA256 = "893fbf07c7d0250e1c30d43b9e01aca69d56e2e6f3d742dcc233e889dfec5aec"
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


def add_open_membership_routes(root_members: dict[str, set[str]], members_by_root: dict[str, set[str]],
                               open_tags: set[str]) -> dict[str, set[str]]:
    """Route only open exact members and omit roots whose mapped members are terminal."""
    for root, tags in members_by_root.items():
        open_members = tags & open_tags
        if open_members:
            root_members.setdefault(root, set()).update(open_members)
    return defaultdict(set, {root: tags for root, tags in root_members.items() if tags})


def queue_priority_key(row: dict[str, str]) -> tuple:
    """Order exact reuse and batchable authority work before discovery/long-tail work."""
    source_class_priority = {
        "REUSE_SOURCE_EXACT_CANDIDATES": 0,
        "REVIEW_REGISTERED_SOURCE_SCOPE": 1,
        "REVIEW_SOURCE_IDENTITY_CANDIDATES": 2,
        "DISCOVER_ADDITIONAL_OFFICIAL_SOURCE": 3,
        "DISCOVER_OFFICIAL_SOURCE": 4,
        "NO_CANDIDATE_ROOT_SOURCE_DISCOVERY": 5,
    }
    return (
        source_class_priority[row["source_yield_class"]],
        -int(row["expected_safe_yield"]),
        -int(row["remaining_unmapped_count"]),
        -int(row["reusable_accepted_source_count"]),
        -int(row["known_official_source_count"]),
        -int(row["top500_count"] or 0),
        -int(row["top2000_count"] or 0),
        -int(row["total_post_count_sum"] or 0),
        row["candidate_root"],
    )


def build(master_path: Path, graph_path: Path, post_counts_path: Path | None):
    master_hash = sha256(master_path)
    if master_hash != MASTER_SHA256:
        raise ValueError(f"#180 master SHA mismatch: expected {MASTER_SHA256}, got {master_hash}")
    graph_hash = sha256(graph_path)
    if graph_hash != GRAPH_SHA256:
        raise ValueError(f"#180 structure graph SHA mismatch: expected {GRAPH_SHA256}, got {graph_hash}")
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
    top500_meta = json.loads((ISSUE216 / "TOP500_COHORT_V1.json").read_text(encoding="utf-8-sig"))
    if (top500_meta.get("baseline_commit") != "9c0db59c0f1dc56402c955e718a37d9de1849d7e"
            or top500_meta.get("baseline_master_sha256") != MASTER_SHA256
            or top500_meta.get("post_count_file_sha256") != POST_COUNTS_SHA256
            or top500_meta.get("cohort_size") != 500):
        raise ValueError("frozen Top500 metadata does not match the #180 baseline")
    top500_rows = read_csv(ISSUE216 / "TOP500_COHORT_V1.csv")
    top500_tags = {row["canonical_character"] for row in top500_rows}
    top500_ranks = {int(row["rank"]) for row in top500_rows}
    if len(top500_rows) != 500 or len(top500_tags) != 500 or top500_ranks != set(range(1, 501)):
        raise ValueError("frozen Top500 cohort must contain exactly ranks 1..500")
    if not top500_tags <= cohort:
        raise ValueError("frozen Top500 cohort contains members outside the #180 unresolved baseline")

    baseline_counts: dict[str, int] = {}
    joined_baseline_tags: set[str] = set()
    post_count_hash = ""
    if post_counts_path is not None:
        post_count_hash = sha256(post_counts_path)
        if post_count_hash != POST_COUNTS_SHA256:
            raise ValueError(
                f"#180 post-count SHA mismatch: expected {POST_COUNTS_SHA256}, got {post_count_hash}"
            )
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
        if root in roots and source["source_type"] in {
                "OFFICIAL_CHARACTER_ROSTER", "OFFICIAL_CHARACTER_PROFILE", "OFFICIAL_GAME_ROSTER",
                "OFFICIAL_SERIES_DIRECTORY", "OFFICIAL_PUBLISHER_ROSTER", "FIRST_PARTY_OTHER",
                "DANBOORU_ACTIVE_COPYRIGHT_IMPLICATION"}:
            source_ids_by_root[root].add(source["source_id"])
        if root in roots and source["source_status"] == "ACCEPTED":
            if (source["exact_roster_available"].lower() == "true"
                    and source["reusable"].lower() == "true"):
                roster_ids_by_root[root].add(source["source_id"])
    for member in member_rows:
        source = sources.get(member["source_id"])
        home = (member.get("canonical_home_root", "").strip() or source.get("copyright_canonical", "").strip()) if source else ""
        if (source and source["source_status"] == "ACCEPTED" and home in roots
                and member["mapping_status"] == "EXACT_COVERED"):
            members_by_root[home].add(member["canonical_character"])
            if source["source_type"] == "DANBOORU_ACTIVE_COPYRIGHT_IMPLICATION":
                source_ids_by_root[home].add(source["source_id"])

    # A registered roster at a root does not imply that it covers every Character
    # hinted at that root. Count only exact, unique candidates from a retained source
    # inventory whose source ID, URL, and exact scope still match the accepted registry.
    candidate_paths = set(ISSUE216.glob("SOURCE_MAPPING_CANDIDATES_*.csv"))
    scratch_candidates = ROOT / ".tmp-issue216-work/tracked-mapping-artifacts-2026-09-30"
    if scratch_candidates.exists():
        candidate_paths.update(scratch_candidates.rglob("SOURCE_MAPPING_CANDIDATES_*.csv"))
    for candidate_path in sorted(candidate_paths):
        for candidate in read_csv(candidate_path):
            source = sources.get(candidate.get("source_id", ""))
            if not source or source["source_status"] != "ACCEPTED":
                continue
            if (candidate.get("source_url") != source["source_url"]
                    or candidate.get("source_scope") != source["source_scope"]):
                continue
            reviewed_source_ids.add(source["source_id"])
            root = source["copyright_canonical"]
            candidate_tags = {candidate.get("canonical_character", "").strip()}
            candidate_tags.update(
                tag.strip() for tag in candidate.get("competing_tags", "").split("|") if tag.strip()
            )
            for tag in candidate_tags & open_tags:
                if candidate.get("candidate_status") == "AUTO_MAPPING_CANDIDATE":
                    safe_candidate_tags_by_root[root].add(tag)
                elif candidate.get("candidate_status") == "REVIEW_REQUIRED":
                    review_required_tags_by_root[root].add(tag)

    root_members: dict[str, set[str]] = defaultdict(set)
    for tag in open_tags:
        for root in hint_by_tag.get(tag, set()):
            root_members[root].add(tag)
    # Accepted exact roster membership is already a validated routing surface. Include
    # it in the queue even when the original #180 hint omitted that root; membership
    # remains evidence only through the accepted source/member rows, not through this
    # priority projection.
    root_members = add_open_membership_routes(root_members, members_by_root, open_tags)
    # A source-derived candidate can expose a more specific root than a broad catalog
    # hint. Add it to the queue only; this never confirms HOME.
    for root, tags in safe_candidate_tags_by_root.items():
        for tag in tags:
            root_members[root].add(tag)
    for root, tags in review_required_tags_by_root.items():
        for tag in tags:
            root_members[root].add(tag)

    # Candidate sources can cover only terminal members. Do not emit empty root rows:
    # they are not research queue work and would distort rank ownership/sharding.
    root_members = {root: tags for root, tags in root_members.items() if tags}

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
        counts_for_tags = [counts[tag] for tag in tags if tag in counts]
        top500 = len(tags & open_tags & top500_tags)
        top2000 = sum(ranks.get(tag, 10**9) <= 2000 for tag in tags) if post_counts_path else None
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
            "unresolved_count": str(len(tags)), "top500_count": str(top500),
            "top2000_count": "" if top2000 is None else str(top2000),
            "total_post_count_sum": "" if not post_counts_path else str(sum(counts_for_tags)),
            "max_post_count": "" if not post_counts_path else str(max(counts_for_tags, default=0)),
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
    rooted_tags = set().union(*root_members.values()) if root_members else set()
    rootless_tags = open_tags - rooted_tags
    if rootless_tags:
        rootless_counts = [counts[tag] for tag in rootless_tags if tag in counts]
        queue.append({
            "candidate_root": "",
            "hint_kind": "No candidate root/family/source hint; source discovery only",
            "unresolved_count": str(len(rootless_tags)),
            "top500_count": str(len(rootless_tags & open_tags & top500_tags)),
            "top2000_count": "" if not post_counts_path else str(sum(ranks.get(tag, 10**9) <= 2000 for tag in rootless_tags)),
            "total_post_count_sum": "" if not post_counts_path else str(sum(rootless_counts)),
            "max_post_count": "" if not post_counts_path else str(max(rootless_counts, default=0)),
            "known_official_source_count": "0", "reusable_accepted_source_count": "0",
            "reviewed_source_count": "0", "likely_roster_availability": "NO_CANDIDATE_ROOT_OR_REGISTERED_SOURCE",
            "existing_exact_mappings": "0", "remaining_unmapped_count": str(len(rootless_tags)),
            "open_exact_candidate_count": "0", "review_required_count": "0", "expected_safe_yield": "0",
            "source_yield_class": "NO_CANDIDATE_ROOT_SOURCE_DISCOVERY", "priority_rank": "",
        })
    # Prioritize exact candidates from accepted sources, then registered roster review
    # and roster discovery. Current unresolved cohort yield dominates; post counts only
    # break ties when the exact frozen snapshot is available.
    queue.sort(key=queue_priority_key)
    for i, row in enumerate(queue, 1):
        row["priority_rank"] = str(i)

    # Preserve candidate-root multiplicity for transparency; the same Character can appear under several hints.
    summary = {
        "schema_version": "issue216-source-yield-queue-v1",
        "baseline_unresolved": len(unresolved), "currently_unresearched": len(open_tags),
        "root_count": len(queue), "post_count_joined_open": len(counts),
        "post_count_joined_frozen_baseline": len(joined_baseline_tags),
        "post_count_missing_open": len(open_tags) - len(counts) if post_counts_path else None,
        "post_count_snapshot_current_for_decision_set": bool(post_counts_path),
        "top500_open": len(open_tags & top500_tags),
        "top2000_open": sum(ranks.get(tag, 10**9) <= 2000 for tag in open_tags) if post_counts_path else None,
        "rootless_open_count": len(rootless_tags),
        "rootless_top500_open": len(rootless_tags & open_tags & top500_tags),
        "rootless_top2000_open": sum(ranks.get(tag, 10**9) <= 2000 for tag in rootless_tags) if post_counts_path else None,
        "rootless_tags": sorted(rootless_tags),
        "candidate_root_count": len(queue) - bool(rootless_tags),
        "source_registry_count": len(source_rows), "accepted_roster_source_count": sum(
            source["source_status"] == "ACCEPTED" and source["exact_roster_available"].lower() == "true"
            and source["reusable"].lower() == "true"
            for source in source_rows
        ),
        "queue_order": "accepted exact-source candidates; registered roster review; source discovery; within class expected safe yield, current unresolved count and reusable source count; frozen Top500 then hash-validated Top2000/post-count as tie-breaks. Candidate edges and frequency are priority-only.",
        "protected_master_sha256": master_hash, "candidate_graph_sha256": graph_hash,
        "post_count_sha256": post_count_hash or None,
        "post_count_status": "HASH_VALIDATED_CURRENT" if post_counts_path else "UNAVAILABLE_NOT_USED",
        "note": "expected_safe_yield counts only AUTO_MAPPING_CANDIDATE rows from reviewed inventories matching an accepted source ID, URL, and exact scope; it is a priority estimate, never HOME evidence or a guaranteed decision count.",
    }
    return fields, queue, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--master", type=Path, required=True)
    parser.add_argument("--graph", type=Path, required=True)
    default_post_counts = ROOT / "docs/issue70/data/source/character_copyright_evidence_full.csv.gz"
    parser.add_argument("--post-counts", type=Path, default=default_post_counts if default_post_counts.exists() else None)
    parser.add_argument("--output", type=Path, default=ISSUE216 / "SOURCE_YIELD_QUEUE_V1.csv")
    parser.add_argument("--summary", type=Path, default=ISSUE216 / "SOURCE_YIELD_QUEUE_V1.json")
    parser.add_argument("--summary-alias", type=Path, default=SUMMARY_ALIAS)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    fields, queue, summary = build(args.master, args.graph, args.post_counts)
    if args.check:
        if (read_csv(args.output) != queue
                or json.loads(args.summary.read_text(encoding="utf-8")) != summary
                or json.loads(args.summary_alias.read_text(encoding="utf-8")) != summary):
            raise SystemExit("source-yield queue differs from deterministic reconstruction")
        print(f"source-yield queue reproducibility: PASS ({len(queue)} roots; {summary['currently_unresearched']} open rows)")
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_csv(args.output, fields, queue)
    summary_text = json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    args.summary.write_text(summary_text, encoding="utf-8")
    args.summary_alias.write_text(summary_text, encoding="utf-8")
    print(f"source-yield queue built: {len(queue)} roots; open={summary['currently_unresearched']}; "
          f"top500={summary['top500_open']}; top2000={summary['top2000_open']}; "
          f"post_count_status={summary['post_count_status']}")


if __name__ == "__main__":
    main()
