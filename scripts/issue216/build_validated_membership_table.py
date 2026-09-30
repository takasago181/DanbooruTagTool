#!/usr/bin/env python3
"""Project accepted exact source memberships into a reusable, cohort-wide table.

This table is an evidence projection, not a candidate-root join. Only accepted
sources plus exact, reviewed source/member mappings can create membership rows.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

try:  # direct script execution
    from authority_coverage import BASELINE_SIZE, read_csv, validate
except ModuleNotFoundError:  # package import from tests/tools
    from scripts.issue216.authority_coverage import BASELINE_SIZE, read_csv, validate

ROOT = Path(__file__).resolve().parents[2]
ISSUE216 = ROOT / "docs/issue216"
TABLE_FIELDS = [
    "canonical_character", "semantic_root", "membership_scope", "evidence_class",
    "source_id", "identity_status", "competing_root_count", "validation_state",
    "provenance", "cohort_state", "next_action",
]
BROWSE_HOME_TIERS = {1, 2, 3, 4, 5}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def build(cohort_path: Path, sources_path: Path, members_path: Path, decisions_path: Path,
          roots_path: Path, expected_size: int = BASELINE_SIZE,
          candidates_dir: Path = ISSUE216) -> tuple[list[dict[str, str]], dict[str, object]]:
    validate(cohort_path, sources_path, members_path, decisions_path, expected_size=expected_size,
             roots_path=roots_path)
    cohort = read_csv(cohort_path)
    sources = {row["source_id"]: row for row in read_csv(sources_path)}
    members = read_csv(members_path)
    decisions = {row["canonical_character"]: row for row in read_csv(decisions_path)}
    roots = {row["copyright_canonical"] for row in read_csv(roots_path)}
    cohort_tags = {row["canonical_character"] for row in cohort}
    open_tags = {tag for tag, decision in decisions.items() if decision["research_state"] == "UNRESEARCHED"}

    accepted: dict[str, list[tuple[dict[str, str], dict[str, str]]]] = defaultdict(list)
    for member in members:
        source = sources.get(member["source_id"])
        if (source and source["source_status"] == "ACCEPTED"
                and member["mapping_status"] == "EXACT_COVERED"
                and member["canonical_character"] in cohort_tags
                and source["copyright_canonical"] in roots):
            accepted[member["canonical_character"]].append((source, member))

    candidates: dict[str, list[tuple[dict[str, str], dict[str, str], str]]] = defaultdict(list)
    candidate_paths = set(candidates_dir.glob("SOURCE_MAPPING_CANDIDATES_*.csv"))
    scratch_candidates = ROOT / ".tmp-issue216-work/tracked-mapping-artifacts-2026-09-30"
    if candidates_dir.resolve() == ISSUE216.resolve() and scratch_candidates.exists():
        candidate_paths.update(scratch_candidates.rglob("SOURCE_MAPPING_CANDIDATES_*.csv"))
    for candidate_path in sorted(candidate_paths):
        review_path = candidate_path.with_name(candidate_path.name.replace(
            "SOURCE_MAPPING_CANDIDATES_", "MAPPING_REVIEW_", 1))
        reviews: dict[tuple[str, str], str] = {}
        if review_path.is_file():
            for review in read_csv(review_path):
                surface = review.get("matched_surface", "")
                tag = review.get("canonical_character", "")
                status = review.get("review_outcome", review.get("review_status", ""))
                reviews[(surface, tag)] = status
        for candidate in read_csv(candidate_path):
            source = sources.get(candidate.get("source_id", ""))
            candidate_tags = {candidate.get("canonical_character", "").strip()}
            candidate_tags.update(
                tag.strip() for tag in candidate.get("competing_tags", "").split("|") if tag.strip()
            )
            candidate_tags.discard("")
            if (not source or source["source_status"] != "ACCEPTED"
                    or candidate.get("source_url") != source["source_url"]
                    or candidate.get("source_scope") != source["source_scope"]):
                continue
            for tag in sorted(candidate_tags & open_tags):
                review_status = reviews.get((candidate.get("matched_surface", ""), tag), "")
                if review_status.upper().startswith(("REJECT", "EXCLUDE")):
                    continue
                candidates[tag].append((source, candidate, review_status))

    rows: list[dict[str, str]] = []
    for tag, pairs in sorted(accepted.items()):
        roots_for_tag = {source["copyright_canonical"] for source, _ in pairs}
        root_count = len(roots_for_tag)
        selected_root = next(iter(roots_for_tag)) if root_count == 1 else ""
        priority_by_root: dict[str, set[int]] = defaultdict(set)
        priority_complete = True
        for source, member in pairs:
            tier = member.get("browse_home_tier", "").strip()
            basis = member.get("browse_home_basis", "").strip()
            if not tier or not basis:
                priority_complete = False
                continue
            try:
                tier_value = int(tier)
            except ValueError:
                priority_complete = False
                continue
            if tier_value not in BROWSE_HOME_TIERS:
                priority_complete = False
                continue
            priority_by_root[source["copyright_canonical"]].add(tier_value)
        priority_resolved = False
        if root_count == 1 and next(iter(priority_by_root.get(selected_root, set())), 0) == 5:
            selected_root = ""
        if root_count > 1 and priority_complete and all(len(priority_by_root[root]) == 1 for root in roots_for_tag):
            eligible_roots = {root for root in roots_for_tag if next(iter(priority_by_root[root])) < 5}
            if eligible_roots:
                best_tier = min(next(iter(priority_by_root[root])) for root in eligible_roots)
                winners = [root for root in eligible_roots if next(iter(priority_by_root[root])) == best_tier]
                if len(winners) == 1:
                    selected_root = winners[0]
                    priority_resolved = True
        validation_state = (
            "VALIDATED_UNIQUE" if root_count == 1 and selected_root else
            "MEMBERSHIP_ONLY_NOT_BROWSE_HOME" if root_count == 1 else
            "VALIDATED_PRIORITY" if priority_resolved else "VALIDATED_CONFLICT"
        )
        decision = decisions[tag]
        if decision["research_state"] == "HOME_CONFIRMED" and root_count > 1:
            if not priority_resolved or selected_root != decision["home_copyright"]:
                raise ValueError(f"confirmed Browse HOME does not match the unique highest-priority root: {tag}")
        for source, member in sorted(pairs, key=lambda pair: (pair[0]["copyright_canonical"], pair[0]["source_id"])):
            if decision["research_state"] == "HOME_CONFIRMED":
                if not selected_root:
                    raise ValueError(f"HOME_CONFIRMED is supported only by a secondary product membership: {tag}")
                next_action = ("TERMINAL_ACCOUNTED" if source["copyright_canonical"] == selected_root
                               else "LOWER_PRIORITY_MEMBERSHIP")
            elif decision["research_state"] != "UNRESEARCHED":
                next_action = "TERMINAL_BLOCKED"
            elif source["copyright_canonical"] == selected_root:
                next_action = "AUTO_ACCEPT_MEMBERSHIP"
            elif priority_resolved:
                next_action = "LOWER_PRIORITY_MEMBERSHIP"
            else:
                next_action = "DEEP_RESEARCH"
            rows.append({
                "canonical_character": tag,
                "semantic_root": source["copyright_canonical"],
                "membership_scope": source["source_scope"],
                "evidence_class": source["source_type"],
                "source_id": source["source_id"],
                "identity_status": "EXACT_REVIEWED" if member["mapping_status"] == "EXACT_COVERED" else "NOT_VALIDATED",
                "competing_root_count": str(root_count),
                "validation_state": validation_state,
                "provenance": f"{source['source_url']} | {source['source_claim']} | {member['mapping_evidence']}"
                               + (f" | Browse HOME priority P{member.get('browse_home_tier')}: {member.get('browse_home_basis')}"
                                  if member.get("browse_home_tier") else ""),
                "cohort_state": decision["research_state"],
                "next_action": next_action,
            })

    mapped_tags = set(accepted)
    for tag in sorted(cohort_tags - mapped_tags):
        state = decisions[tag]["research_state"]
        if state == "HOME_CONFIRMED":
            action, validation_state = "TERMINAL_ACCOUNTED", "NO_ADDITIONAL_MEMBERSHIP_REQUIRED"
        elif state != "UNRESEARCHED":
            action, validation_state = "TERMINAL_BLOCKED", "NO_ADDITIONAL_MEMBERSHIP_REQUIRED"
        elif candidates.get(tag):
            relevant = candidates[tag]
            needs_deep = any(candidate.get("candidate_status") == "REVIEW_REQUIRED" for _, candidate, _ in relevant)
            action = "DEEP_RESEARCH" if needs_deep else "FAST_REVIEW"
            validation_state = "REVIEW_REQUIRED_CANDIDATE" if needs_deep else "UNREVIEWED_EXACT_CANDIDATE"
            for source, candidate, review_status in sorted(relevant, key=lambda item: (item[0]["source_id"], item[1].get("matched_surface", ""))):
                rows.append({
                    "canonical_character": tag, "semantic_root": "", "membership_scope": source["source_scope"],
                    "evidence_class": source["source_type"], "source_id": source["source_id"],
                    "identity_status": candidate.get("candidate_status", "UNREVIEWED"),
                    "competing_root_count": "0", "validation_state": validation_state,
                    "provenance": f"Candidate only; not HOME evidence. Surface={candidate.get('matched_surface', '')}; competing_tags={candidate.get('competing_tags', '')}; review={review_status or 'pending'}",
                    "cohort_state": state, "next_action": action,
                })
            continue
        else:
            action, validation_state = "FAST_REVIEW", "NO_VALIDATED_MEMBERSHIP"
        rows.append({
            "canonical_character": tag, "semantic_root": "", "membership_scope": "",
            "evidence_class": "", "source_id": "", "identity_status": "NOT_VALIDATED",
            "competing_root_count": "0", "validation_state": validation_state,
            "provenance": "", "cohort_state": state, "next_action": action,
        })

    action_by_tag: dict[str, str] = {}
    action_rank = {"AUTO_ACCEPT_MEMBERSHIP": 0, "DEEP_RESEARCH": 1, "FAST_REVIEW": 2,
                   "TERMINAL_BLOCKED": 3, "TERMINAL_ACCOUNTED": 4, "LOWER_PRIORITY_MEMBERSHIP": 5}
    for row in rows:
        tag = row["canonical_character"]
        action = row["next_action"]
        if tag not in action_by_tag or action_rank.get(action, 99) < action_rank.get(action_by_tag[tag], 99):
            action_by_tag[tag] = action
    summary = {
        "schema_version": "issue216-validated-semantic-membership-v1",
        "cohort_count": len(cohort),
        "validated_membership_row_count": sum(row["validation_state"] in {"VALIDATED_UNIQUE", "VALIDATED_CONFLICT"} for row in rows),
        "over_research_check_row_count": len(rows),
        "unique_character_count": len(accepted),
        "AUTO_ACCEPT": sum(action == "AUTO_ACCEPT_MEMBERSHIP" for action in action_by_tag.values()),
        "FAST_REVIEW": sum(action == "FAST_REVIEW" for action in action_by_tag.values()),
        "DEEP_RESEARCH": sum(action == "DEEP_RESEARCH" for action in action_by_tag.values()),
        "TERMINAL_BLOCKED": sum(action == "TERMINAL_BLOCKED" for action in action_by_tag.values()),
        "TERMINAL_ACCOUNTED": sum(action == "TERMINAL_ACCOUNTED" for action in action_by_tag.values()),
        "character_specific_deep_research_count": sum(action == "DEEP_RESEARCH" for action in action_by_tag.values()),
        "character_specific_deep_research_rate": round(
            sum(action == "DEEP_RESEARCH" for action in action_by_tag.values()) / len(cohort), 6
        ),
        "cohort_sha256": sha256(cohort_path),
        "sources_sha256": sha256(sources_path),
        "members_sha256": sha256(members_path),
        "decisions_sha256": sha256(decisions_path),
        "roots_sha256": sha256(roots_path),
        "candidate_roots_are_evidence": False,
    }
    return rows, summary


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=TABLE_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", type=Path, default=ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv")
    parser.add_argument("--sources", type=Path, default=ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv")
    parser.add_argument("--members", type=Path, default=ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv")
    parser.add_argument("--decisions", type=Path, default=ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv")
    parser.add_argument("--roots", type=Path, default=ISSUE216 / "COPYRIGHT_ROOTS_V1.csv")
    parser.add_argument("--output", type=Path, default=ISSUE216 / "VALIDATED_SEMANTIC_MEMBERSHIPS_V1.csv")
    parser.add_argument("--summary", type=Path, default=ISSUE216 / "VALIDATED_SEMANTIC_MEMBERSHIPS_V1.json")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows, summary = build(args.cohort, args.sources, args.members, args.decisions, args.roots)
    if args.check:
        current_rows = read_csv(args.output)
        current_summary = json.loads(args.summary.read_text(encoding="utf-8"))
        if current_rows != rows or current_summary != summary:
            raise SystemExit("validated semantic membership table differs from deterministic reconstruction")
    else:
        write_csv(args.output, rows)
        args.summary.write_text(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"validated semantic memberships: {summary['validated_membership_row_count']} evidence rows; "
          f"{summary['AUTO_ACCEPT']} AUTO_ACCEPT; {summary['FAST_REVIEW']} FAST_REVIEW; "
          f"{summary['DEEP_RESEARCH']} DEEP_RESEARCH")


if __name__ == "__main__":
    main()
