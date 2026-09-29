#!/usr/bin/env python3
"""Turn a manually reviewed exact-roster candidate file into the existing batch contract."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

from authority_coverage import read_csv

ROOT = Path(__file__).resolve().parents[2]
ISSUE216 = ROOT / "docs/issue216"
INPUT_FIELDS = [
    "canonical_character", "home_copyright", "source_url", "source_type", "authority_owner",
    "source_scope", "source_claim", "matched_surface", "mapping_evidence", "reason_code", "reason_detail",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--source-id", required=True)
    parser.add_argument("--proposed-source", type=Path,
                        help="single independently reviewed REVIEWED_PENDING_ACCEPTANCE source row for a new source batch")
    parser.add_argument("--source-type", default="OFFICIAL_CHARACTER_ROSTER")
    parser.add_argument("--reviewer-claim", required=True, help="source-level claim after official page review")
    parser.add_argument("--reason-code", required=True)
    parser.add_argument("--reason-detail", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    candidates = read_csv(args.candidates)
    sources = {row["source_id"]: row for row in read_csv(ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv")}
    source = sources.get(args.source_id)
    if not source and args.proposed_source:
        proposed = read_csv(args.proposed_source)
        if len(proposed) != 1:
            raise SystemExit("proposed source input must contain exactly one source row")
        source = proposed[0] if proposed[0]["source_id"] == args.source_id else None
        if source and source["source_status"] != "REVIEWED_PENDING_ACCEPTANCE":
            raise SystemExit("proposed source must be REVIEWED_PENDING_ACCEPTANCE")
    if not source or source["source_status"] != "ACCEPTED" or source["exact_roster_available"].lower() != "true":
        if not source or source["source_status"] != "REVIEWED_PENDING_ACCEPTANCE" or source["exact_roster_available"].lower() != "true":
            raise SystemExit("source must be ACCEPTED or explicitly reviewed pending acceptance, with an exact roster")
    cohort = {r["canonical_character"] for r in read_csv(ISSUE216 / "AUTHORITY_COVERAGE_COHORT_V1.csv")}
    decisions = {r["canonical_character"]: r for r in read_csv(ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv")}

    output = []
    seen = set()
    for candidate in candidates:
        if candidate["source_id"] != args.source_id:
            continue
        if candidate["candidate_status"] != "AUTO_MAPPING_CANDIDATE":
            continue
        tag = candidate["canonical_character"]
        if not tag or tag in seen or tag not in cohort or decisions[tag]["research_state"] != "UNRESEARCHED":
            raise SystemExit(f"candidate is duplicate/outside/open-state mismatch: {tag}")
        seen.add(tag)
        surface = candidate["matched_surface"]
        output.append({
            "canonical_character": tag, "home_copyright": source["copyright_canonical"],
            "source_url": source["source_url"], "source_type": args.source_type,
            "authority_owner": source["authority_owner"], "source_scope": source["source_scope"],
            "source_claim": f"{args.reviewer_claim} Exact official roster entry: {surface}.",
            "matched_surface": surface,
            "mapping_evidence": f"Official page lists exact surface {surface}. Reviewed candidate basis: {candidate['candidate_basis']}",
            "reason_code": args.reason_code, "reason_detail": args.reason_detail,
        })
    if not output:
        raise SystemExit("no AUTO_MAPPING_CANDIDATE rows passed reviewed scope/state checks")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=INPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(output, key=lambda row: row["canonical_character"]))
    print(f"reviewed exact roster batch compiled: {len(output)} exact unique cohort members; source remains {args.source_id}")


if __name__ == "__main__":
    main()
