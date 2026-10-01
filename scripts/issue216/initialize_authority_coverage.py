#!/usr/bin/env python3
"""Create the complete additive coverage ledger with explicit UNRESEARCHED rows."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COHORT_FIELDS = ["cohort_id", "canonical_character", "baseline_state", "baseline_home"]
SOURCE_FIELDS = [
    "source_id", "copyright_canonical", "source_url", "source_type", "authority_owner",
    "source_status", "source_scope", "exact_roster_available", "reviewed_at", "source_claim",
    "provenance", "reusable", "notes",
]
MEMBER_FIELDS = [
    "source_id", "canonical_character", "matched_surface", "mapping_method", "mapping_evidence",
    "reviewed_at", "reviewer", "mapping_status",
]
DECISION_FIELDS = [
    "cohort_id", "canonical_character", "research_state", "home_copyright", "authority_type",
    "source_ids", "source_claim", "provenance", "reviewed_at", "reason_code", "reason_detail",
    "validated_home_candidates",
]


def write_new(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    if path.exists():
        raise SystemExit(f"refusing to overwrite existing coverage artifact: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", type=Path, default=ROOT / "docs/issue216/AUTHORITY_COVERAGE_COHORT_V1.csv")
    parser.add_argument("--manifest", type=Path, default=ROOT / "docs/issue216/AUTHORITY_COVERAGE_COHORT_V1.json")
    parser.add_argument("--sources", type=Path, default=ROOT / "docs/issue216/COPYRIGHT_AUTHORITY_REGISTRY_V1.csv")
    parser.add_argument("--members", type=Path, default=ROOT / "docs/issue216/AUTHORITY_SOURCE_MEMBERS_V1.csv")
    parser.add_argument("--decisions", type=Path, default=ROOT / "docs/issue216/AUTHORITY_COVERAGE_DECISIONS_V1.csv")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if manifest.get("baseline_home_unresolved") != 13_983:
        raise SystemExit("cohort manifest does not describe the frozen 13,983-row baseline")
    with args.cohort.open(encoding="utf-8-sig", newline="") as stream:
        cohort = list(csv.DictReader(stream))
    if len(cohort) != 13_983 or any(row["baseline_state"] != "HOME_UNRESOLVED" for row in cohort):
        raise SystemExit("refusing to initialize from a non-baseline or incomplete cohort")
    decisions = [{
        "cohort_id": row["cohort_id"], "canonical_character": row["canonical_character"],
        "research_state": "UNRESEARCHED", "home_copyright": "", "authority_type": "", "source_ids": "",
        "source_claim": "", "provenance": "", "reviewed_at": "", "reason_code": "", "reason_detail": "",
        "validated_home_candidates": "",
    } for row in cohort]
    write_new(args.sources, SOURCE_FIELDS, [])
    write_new(args.members, MEMBER_FIELDS, [])
    write_new(args.decisions, DECISION_FIELDS, decisions)
    print(f"initialized full cohort: {len(cohort)} UNRESEARCHED; no HOME evidence added")


if __name__ == "__main__":
    main()
