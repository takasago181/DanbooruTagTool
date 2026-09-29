#!/usr/bin/env python3
"""Apply researched non-HOME terminal decisions to the additive #216 layer."""
from __future__ import annotations

import argparse
import csv
import tempfile
from pathlib import Path

from apply_reviewed_roster_batch import write_csv_atomic
from authority_coverage import (
    DECISION_FIELDS, MEMBER_FIELDS, SOURCE_FIELDS, deterministic_source_id, read_csv, validate,
)

ROOT = Path(__file__).resolve().parents[2]
ISSUE216 = ROOT / "docs/issue216"
INPUT_FIELDS = [
    "canonical_character", "research_state", "source_url", "source_type", "authority_owner",
    "source_status", "source_scope", "source_claim", "matched_surface", "mapping_method",
    "mapping_evidence", "mapping_status", "reason_code", "reason_detail",
]
TERMINAL_STATES = {"SOURCE_RESEARCHED_NO_SAFE_EVIDENCE", "POLICY_BLOCKED", "IDENTITY_BLOCKED"}
NON_ACCEPTED_STATUSES = {
    "PARTIAL", "SOURCE_UNAVAILABLE", "SOURCE_INSUFFICIENT", "REJECTED",
    # Input-only marker: reuse an already accepted exact source for a researched
    # non-HOME conclusion without downgrading or duplicating its registry row.
    "REUSE_ACCEPTED_FOR_NON_HOME",
}
REVIEWED_AT = "2026-09-30"
REVIEWER = "Codex independent authority-source review"


def build(batch_path: Path):
    batch = read_csv(batch_path)
    if not batch:
        raise ValueError("terminal research batch is empty")
    if list(batch[0]) != INPUT_FIELDS:
        raise ValueError(f"batch columns must be exactly {INPUT_FIELDS}")
    cohort = read_csv(ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv")
    decisions = read_csv(ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv")
    sources = read_csv(ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv")
    members = read_csv(ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv")
    cohort_by_tag = {row["canonical_character"]: row for row in cohort}
    decision_by_tag = {row["canonical_character"]: row for row in decisions}

    by_source: dict[tuple[str, str, str], list[dict[str, str]]] = {}
    tags: set[str] = set()
    for row in batch:
        if any(not row[field] for field in INPUT_FIELDS):
            raise ValueError(f"terminal batch row has a blank required field: {row}")
        tag = row["canonical_character"]
        if tag in tags:
            raise ValueError(f"duplicate Character in terminal research batch: {tag}")
        tags.add(tag)
        if tag not in cohort_by_tag:
            raise ValueError(f"terminal member is outside the frozen cohort: {tag}")
        if row["research_state"] not in TERMINAL_STATES:
            raise ValueError(f"unsupported non-HOME terminal state: {row['research_state']}")
        if row["source_status"] not in NON_ACCEPTED_STATUSES:
            raise ValueError("terminal research sources must not be ACCEPTED HOME authorities")
        if row["mapping_method"] not in {"EXACT_CANONICAL", "VALIDATED_ALIAS", "REVIEWED_NAME_MAPPING", "DOCUMENTED_IDENTITY_MAPPING"}:
            raise ValueError(f"invalid exact/reviewed mapping method: {row['mapping_method']}")
        if row["mapping_status"] not in {"EXACT_COVERED", "AMBIGUOUS_REVIEW", "REJECTED"}:
            raise ValueError(f"invalid mapping status: {row['mapping_status']}")
        if row["research_state"] == "IDENTITY_BLOCKED" and row["mapping_status"] == "EXACT_COVERED":
            raise ValueError(f"IDENTITY_BLOCKED requires an unresolved or rejected identity mapping: {tag}")
        by_source.setdefault((row["source_url"], row["authority_owner"], row["source_scope"]), []).append(row)

    merged_sources = {row["source_id"]: row for row in sources}
    merged_members = {(row["source_id"], row["canonical_character"]): row for row in members}
    proposed_decisions: dict[str, dict[str, str]] = {}
    new_source_count = 0
    for (url, owner, scope), source_rows in sorted(by_source.items()):
        invariant_fields = ("source_type", "source_status")
        if any(len({row[field] for row in source_rows}) != 1 for field in invariant_fields):
            raise ValueError(f"one source has inconsistent type/status: {url}")
        source_id = deterministic_source_id(url, owner, scope)
        reuse_accepted = source_rows[0]["source_status"] == "REUSE_ACCEPTED_FOR_NON_HOME"
        prior_source = merged_sources.get(source_id)
        if reuse_accepted:
            if not prior_source or any(prior_source[field] != expected for field, expected in {
                "source_url": url,
                "authority_owner": owner,
                "source_scope": scope,
                "source_type": source_rows[0]["source_type"],
                "source_status": "ACCEPTED",
                "exact_roster_available": "true",
            }.items()):
                raise ValueError(f"non-HOME reuse requires the same previously accepted exact source: {url}")
            source = prior_source
        else:
            claim = "Non-accepted research source reviewed for exact members: " + "; ".join(
                f"{row['canonical_character']} ({row['matched_surface']}): {row['source_claim']}"
                for row in sorted(source_rows, key=lambda item: item["canonical_character"])
            )
            source = {
                "source_id": source_id, "copyright_canonical": "", "source_url": url,
                "source_type": source_rows[0]["source_type"], "authority_owner": owner,
                "source_status": source_rows[0]["source_status"], "source_scope": scope,
                "exact_roster_available": "false", "reviewed_at": REVIEWED_AT,
                "source_claim": claim,
                "provenance": f"Independent source research recorded by {batch_path.name} on {REVIEWED_AT}.",
                "reusable": "true" if len(source_rows) > 1 else "false",
                "notes": "Research evidence only; no HOME root is assigned or implied.",
            }
            prior_source = merged_sources.get(source_id)
            if prior_source and prior_source != source:
                raise ValueError(f"source ID collision with different registry metadata: {source_id}")
            if not prior_source:
                new_source_count += 1
            merged_sources[source_id] = source
        for row in source_rows:
            tag = row["canonical_character"]
            member = {
                "source_id": source_id, "canonical_character": tag, "matched_surface": row["matched_surface"],
                "mapping_method": row["mapping_method"], "mapping_evidence": row["mapping_evidence"],
                "reviewed_at": REVIEWED_AT, "reviewer": REVIEWER, "mapping_status": row["mapping_status"],
            }
            key = (source_id, tag)
            prior_member = merged_members.get(key)
            if prior_member and prior_member != member:
                raise ValueError(f"source/member mapping collision: {key}")
            merged_members[key] = member
            decision = dict(decision_by_tag[tag])
            decision.update({
                "research_state": row["research_state"], "home_copyright": "", "authority_type": "",
                "source_ids": source_id, "source_claim": row["source_claim"],
                "provenance": f"Scoped non-HOME research in {batch_path.name}; source: {url}",
                "reviewed_at": REVIEWED_AT, "reason_code": row["reason_code"],
                "reason_detail": row["reason_detail"], "validated_home_candidates": "",
            })
            current = decision_by_tag[tag]
            if current["research_state"] != "UNRESEARCHED" and current != decision:
                raise ValueError(f"refusing to replace a different terminal decision: {tag}")
            proposed_decisions[tag] = decision

    merged_decisions = [proposed_decisions.get(row["canonical_character"], row) for row in decisions]
    return (
        sorted(merged_sources.values(), key=lambda row: row["source_id"]),
        sorted(merged_members.values(), key=lambda row: (row["source_id"], row["canonical_character"])),
        merged_decisions,
        new_source_count,
    )


def validate_proposed(sources, members, decisions) -> None:
    with tempfile.TemporaryDirectory(prefix=".issue216-terminal-check-", dir=ISSUE216) as folder:
        temp = Path(folder)
        paths = {name: temp / f"{name}.csv" for name in ("sources", "members", "decisions")}
        for name, rows, fields in (("sources", sources, SOURCE_FIELDS), ("members", members, MEMBER_FIELDS),
                                   ("decisions", decisions, DECISION_FIELDS)):
            with paths[name].open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
        validate(ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv", paths["sources"], paths["members"], paths["decisions"],
                 roots_path=ISSUE216 / "COPYRIGHT_ROOTS_V1.csv")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    sources, members, decisions, new_source_count = build(args.batch)
    validate_proposed(sources, members, decisions)
    if args.check:
        print(f"terminal batch valid: {len(read_csv(args.batch))} researched decisions, {new_source_count} new non-HOME sources")
        return
    write_csv_atomic(ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv", SOURCE_FIELDS, sources)
    write_csv_atomic(ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv", MEMBER_FIELDS, members)
    write_csv_atomic(ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv", DECISION_FIELDS, decisions)
    validate(ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv", ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv",
             ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv", ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv",
             roots_path=ISSUE216 / "COPYRIGHT_ROOTS_V1.csv")
    print(f"applied researched non-HOME terminal decisions: {len(read_csv(args.batch))}; new sources: {new_source_count}")


if __name__ == "__main__":
    main()
