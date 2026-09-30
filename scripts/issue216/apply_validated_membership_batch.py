#!/usr/bin/env python3
"""Bulk-apply unique HOME decisions from the validated membership projection."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

try:  # direct script execution
    from authority_coverage import BASELINE_SIZE, DECISION_FIELDS, read_csv, validate
    from build_validated_membership_table import build
except ModuleNotFoundError:  # package import from tests/tools
    from scripts.issue216.authority_coverage import BASELINE_SIZE, DECISION_FIELDS, read_csv, validate
    from scripts.issue216.build_validated_membership_table import build

ROOT = Path(__file__).resolve().parents[2]
ISSUE216 = ROOT / "docs/issue216"
REVIEWED_AT = "2026-09-30"


def build_decisions(cohort_path: Path, sources_path: Path, members_path: Path,
                    decisions_path: Path, roots_path: Path,
                    expected_size: int = BASELINE_SIZE) -> tuple[list[dict[str, str]], int]:
    table, _ = build(cohort_path, sources_path, members_path, decisions_path, roots_path, expected_size)
    decisions = read_csv(decisions_path)
    decision_by_tag = {row["canonical_character"]: row for row in decisions}
    sources = {row["source_id"]: row for row in read_csv(sources_path)}
    by_tag: dict[str, list[dict[str, str]]] = {}
    for row in table:
        if row["next_action"] == "AUTO_ACCEPT_MEMBERSHIP":
            by_tag.setdefault(row["canonical_character"], []).append(row)

    applied = 0
    for tag, memberships in by_tag.items():
        roots = {row["semantic_root"] for row in memberships}
        if len(roots) != 1 or any(row["identity_status"] != "EXACT_REVIEWED" for row in memberships):
            raise ValueError(f"membership is not unique and exact: {tag}")
        root = next(iter(roots))
        source_ids = sorted({row["source_id"] for row in memberships})
        if any(sources[source_id]["source_status"] != "ACCEPTED"
               or sources[source_id]["copyright_canonical"] != root for source_id in source_ids):
            raise ValueError(f"source status/scope mismatch for {tag}")
        current = decision_by_tag[tag]
        if current["research_state"] != "UNRESEARCHED":
            continue
        types = sorted({sources[source_id]["source_type"] for source_id in source_ids})
        claims = sorted({sources[source_id]["source_claim"] for source_id in source_ids})
        scopes = sorted({sources[source_id]["source_scope"] for source_id in source_ids})
        current.update({
            "research_state": "HOME_CONFIRMED", "home_copyright": root,
            "authority_type": types[0], "source_ids": "|".join(source_ids),
            "source_claim": "Validated semantic membership: " + " | ".join(claims),
            "provenance": "Bulk exact-identity join from VALIDATED_SEMANTIC_MEMBERSHIPS_V1.csv; scopes: " + " | ".join(scopes),
            "reviewed_at": REVIEWED_AT, "reason_code": "VALIDATED_SEMANTIC_MEMBERSHIP_BULK",
            "reason_detail": "Accepted exact membership evidence resolves one canonical root; competing root count is zero. No Character-specific source lookup required.",
            "validated_home_candidates": "",
        })
        applied += 1
    return decisions, applied


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=DECISION_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", type=Path, default=ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv")
    parser.add_argument("--sources", type=Path, default=ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv")
    parser.add_argument("--members", type=Path, default=ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv")
    parser.add_argument("--decisions", type=Path, default=ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv")
    parser.add_argument("--roots", type=Path, default=ISSUE216 / "COPYRIGHT_ROOTS_V1.csv")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    decisions, applied = build_decisions(args.cohort, args.sources, args.members, args.decisions, args.roots)
    if args.check:
        print(f"validated membership batch: {applied} new HOME decisions; dry run")
        return
    with __import__("tempfile").TemporaryDirectory(prefix=".issue216-membership-check-", dir=ISSUE216) as folder:
        proposed = Path(folder) / "decisions.csv"
        write_csv(proposed, decisions)
        validate(args.cohort, args.sources, args.members, proposed, expected_size=BASELINE_SIZE,
                 roots_path=args.roots)
    write_csv(args.decisions, decisions)
    validate(args.cohort, args.sources, args.members, args.decisions, expected_size=BASELINE_SIZE,
             roots_path=args.roots)
    print(f"applied validated semantic memberships: {applied} new HOME decisions")


if __name__ == "__main__":
    main()
