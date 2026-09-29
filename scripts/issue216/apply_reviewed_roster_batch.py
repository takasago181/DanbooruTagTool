#!/usr/bin/env python3
"""Apply an exact-member, first-party roster batch to the additive #216 layer."""
from __future__ import annotations

import argparse
import csv
import json
import os
import tempfile
from pathlib import Path

from authority_coverage import (
    DECISION_FIELDS, MEMBER_FIELDS, SOURCE_FIELDS, deterministic_source_id, read_csv, validate,
)

ROOT = Path(__file__).resolve().parents[2]
ISSUE216 = ROOT / "docs/issue216"
INPUT_FIELDS = [
    "canonical_character", "home_copyright", "source_url", "source_type", "authority_owner",
    "source_scope", "source_claim", "matched_surface", "mapping_evidence", "reason_code", "reason_detail",
]
REVIEWED_AT = "2026-09-30"
REVIEWER = "Codex independent first-party source review"


def write_csv_atomic(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=path.parent,
                                         prefix=path.name + ".", suffix=".tmp", delete=False) as stream:
            temp_path = Path(stream.name)
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def build(batch_path: Path) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    batch = read_csv(batch_path)
    if not batch:
        raise ValueError("review batch is empty")
    if list(batch[0]) != INPUT_FIELDS:
        raise ValueError(f"review batch columns must be exactly {INPUT_FIELDS}")
    cohort = read_csv(ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv")
    decisions = read_csv(ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv")
    sources = read_csv(ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv")
    members = read_csv(ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv")
    known_roots = {row["copyright_canonical"] for row in read_csv(ISSUE216 / "COPYRIGHT_ROOTS_V1.csv")}
    cohort_by_tag = {row["canonical_character"]: row for row in cohort}
    decision_by_tag = {row["canonical_character"]: row for row in decisions}

    by_source: dict[tuple[str, str, str], list[dict[str, str]]] = {}
    tags: set[str] = set()
    for row in batch:
        if any(not row[field] for field in INPUT_FIELDS):
            raise ValueError(f"batch row has blank required fields: {row}")
        if row["canonical_character"] in tags:
            raise ValueError(f"duplicate member in review batch: {row['canonical_character']}")
        tags.add(row["canonical_character"])
        if row["canonical_character"] not in cohort_by_tag:
            raise ValueError(f"batch member is outside the frozen unresolved cohort: {row['canonical_character']}")
        if row["home_copyright"] not in known_roots:
            raise ValueError(f"batch HOME is not an Issue #70 canonical Copyright root: {row['home_copyright']}")
        if decision_by_tag[row["canonical_character"]]["research_state"] not in {"UNRESEARCHED", "HOME_CONFIRMED"}:
            raise ValueError(f"refusing to replace another terminal state: {row['canonical_character']}")
        key = (row["source_url"], row["authority_owner"], row["source_scope"])
        by_source.setdefault(key, []).append(row)

    new_sources: list[dict[str, str]] = []
    new_members: list[dict[str, str]] = []
    proposed_decisions: dict[str, dict[str, str]] = {}
    for (url, owner, scope), source_rows in sorted(by_source.items()):
        invariant_fields = ("home_copyright", "source_type")
        if any(len({row[field] for row in source_rows}) != 1 for field in invariant_fields):
            raise ValueError(f"one exact source has inconsistent HOME/type/claim: {url}")
        home = source_rows[0]["home_copyright"]
        source_type = source_rows[0]["source_type"]
        claim = "Official roster explicitly lists these reviewed exact members: " + "; ".join(
            f"{row['canonical_character']} ({row['matched_surface']})" for row in sorted(source_rows, key=lambda x: x["canonical_character"])
        )
        source_id = deterministic_source_id(url, owner, scope)
        new_sources.append({
            "source_id": source_id, "copyright_canonical": home, "source_url": url,
            "source_type": source_type, "authority_owner": owner, "source_status": "ACCEPTED",
            "source_scope": scope, "exact_roster_available": "true", "reviewed_at": REVIEWED_AT,
            "source_claim": claim,
            "provenance": f"Independent first-party roster review on {REVIEWED_AT}; exact cohort members recorded in this batch.",
            "reusable": "true" if len(source_rows) > 1 else "false",
            "notes": "Covers listed exact members only; absence is not evidence.",
        })
        for row in source_rows:
            tag = row["canonical_character"]
            new_members.append({
                "source_id": source_id, "canonical_character": tag,
                "matched_surface": row["matched_surface"], "mapping_method": "REVIEWED_NAME_MAPPING",
                "mapping_evidence": row["mapping_evidence"], "reviewed_at": REVIEWED_AT,
                "reviewer": REVIEWER, "mapping_status": "EXACT_COVERED",
            })
            current = decision_by_tag[tag]
            decision = dict(current)
            decision.update({
                "research_state": "HOME_CONFIRMED", "home_copyright": home,
                "authority_type": source_type, "source_ids": source_id, "source_claim": row["source_claim"],
                "provenance": f"Exact reviewed first-party roster member mapping in {batch_path.name}; source: {url}",
                "reviewed_at": REVIEWED_AT, "reason_code": row["reason_code"],
                "reason_detail": row["reason_detail"], "validated_home_candidates": "",
            })
            if current["research_state"] == "HOME_CONFIRMED" and current != decision:
                raise ValueError(f"refusing to replace a different HOME_CONFIRMED decision: {tag}")
            proposed_decisions[tag] = decision

    merged_sources = {row["source_id"]: row for row in sources}
    for row in new_sources:
        prior = merged_sources.get(row["source_id"])
        if prior and prior != row:
            raise ValueError(f"source ID collision with different registered metadata: {row['source_id']}")
        merged_sources[row["source_id"]] = row
    merged_members = {(row["source_id"], row["canonical_character"]): row for row in members}
    for row in new_members:
        key = (row["source_id"], row["canonical_character"])
        prior = merged_members.get(key)
        if prior and prior != row:
            raise ValueError(f"source/member mapping collision: {key}")
        merged_members[key] = row
    merged_decisions = [proposed_decisions.get(row["canonical_character"], row) for row in decisions]
    return (
        sorted(merged_sources.values(), key=lambda row: row["source_id"]),
        sorted(merged_members.values(), key=lambda row: (row["source_id"], row["canonical_character"])),
        merged_decisions,
        new_sources,
    )


def validate_proposed(sources: list[dict[str, str]], members: list[dict[str, str]],
                      decisions: list[dict[str, str]]) -> None:
    with tempfile.TemporaryDirectory(prefix=".issue216-batch-check-", dir=ISSUE216) as folder:
        temp = Path(folder)
        paths = {
            "sources": temp / "sources.csv", "members": temp / "members.csv",
            "decisions": temp / "decisions.csv",
        }
        for name, rows, fields in (("sources", sources, SOURCE_FIELDS), ("members", members, MEMBER_FIELDS),
                                   ("decisions", decisions, DECISION_FIELDS)):
            with paths[name].open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
                writer.writeheader()
                writer.writerows(rows)
        validate(ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv", paths["sources"], paths["members"],
                 paths["decisions"], roots_path=ISSUE216 / "COPYRIGHT_ROOTS_V1.csv")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=Path, required=True)
    parser.add_argument("--check", action="store_true", help="validate the proposed merge without writing")
    args = parser.parse_args()
    sources, members, decisions, new_sources = build(args.batch)
    validate_proposed(sources, members, decisions)
    if args.check:
        print(f"review batch valid: {len(decisions)} cohort decisions, {len(members)} exact mappings, {len(sources)} sources")
        return
    write_csv_atomic(ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv", SOURCE_FIELDS, sources)
    write_csv_atomic(ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv", MEMBER_FIELDS, members)
    write_csv_atomic(ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv", DECISION_FIELDS, decisions)
    validate(ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv", ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv",
             ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv", ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv",
             roots_path=ISSUE216 / "COPYRIGHT_ROOTS_V1.csv")
    print(f"applied exact reviewed roster members: {len(read_csv(args.batch))}; new sources: {len(new_sources)}")


if __name__ == "__main__":
    main()
