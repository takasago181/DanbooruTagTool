#!/usr/bin/env python3
"""Materialize Issue #94 final candidate and exclusion artifacts.

The source of truth for the final 324-row human decision is:
  - docs/issue94/special_gap_final_review_queue_v1.csv
  - docs/issue94/SPECIAL_GAP_FINAL_REVIEW_v1.md

This script does not mutate production Special data. It only converts the recorded
review decision into deterministic candidate/exclusion deliverables.
"""

from __future__ import annotations

import csv
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUEUE = ROOT / "docs/issue94/special_gap_final_review_queue_v1.csv"
REVIEW = ROOT / "docs/issue94/SPECIAL_GAP_FINAL_REVIEW_v1.md"
CANDIDATES = ROOT / "docs/issue94/special_gap_candidates_v1.csv"
EXCLUSIONS = ROOT / "docs/issue94/special_gap_exclusion_ledger_v1.csv"
SUMMARY = ROOT / "docs/issue94/SPECIAL_GAP_FINAL_ARTIFACT_SUMMARY_v1.md"

EXPECTED_TOTAL = 324
EXPECTED_CANDIDATE = 195
EXPECTED_GENERAL = 124
EXPECTED_DUPLICATE = 5


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def collect_bullets(lines: list[str], section_header: str, subsection: str | None = None) -> set[str]:
    in_section = False
    in_subsection = subsection is None
    found_section = False
    found_subsection = subsection is None
    result: set[str] = set()

    for raw in lines:
        line = raw.strip()
        if line.startswith("## "):
            if in_section:
                break
            in_section = line == section_header
            if in_section:
                found_section = True
            continue
        if not in_section:
            continue
        if line.startswith("### "):
            if subsection is None:
                continue
            in_subsection = line == f"### {subsection}"
            if in_subsection:
                found_subsection = True
            continue
        if in_subsection and line.startswith("- `"):
            end = line.find("`", 3)
            if end != -1:
                result.add(line[3:end])

    if not found_section:
        raise RuntimeError(f"missing review section: {section_header}")
    if not found_subsection:
        raise RuntimeError(f"missing review subsection: {section_header} / {subsection}")
    return result


def bucket(count: int) -> str:
    if count >= 100_000:
        return ">=100k"
    if count >= 10_000:
        return "10k-99,999"
    if count >= 1_000:
        return "1k-9,999"
    if count >= 100:
        return "100-999"
    return "<100"


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    fields = [
        "canonical_tag",
        "post_count",
        "post_count_bucket",
        "aliases",
        "concept_area",
        "final_status",
        "final_reason",
        "v2_status",
        "v2_priority",
        "human_review_status",
        "nearest_special_identity",
        "queue_reason",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    queue = read_csv(QUEUE)
    if len(queue) != EXPECTED_TOTAL:
        raise RuntimeError(f"queue row count mismatch: {len(queue)} != {EXPECTED_TOTAL}")
    tags = [row["canonical_tag"] for row in queue]
    if len(tags) != len(set(tags)):
        raise RuntimeError("duplicate canonical_tag in final review queue")

    lines = REVIEW.read_text(encoding="utf-8").splitlines()
    demotions = collect_bullets(lines, "## Explicit v2 Candidate -> GENERAL_ONLY demotions (117)")
    boundary_candidate = collect_bullets(lines, "## Boundary rows resolved (9)", "CANDIDATE")
    boundary_general = collect_bullets(lines, "## Boundary rows resolved (9)", "GENERAL_ONLY")
    boundary_duplicate = collect_bullets(lines, "## Boundary rows resolved (9)", "DUPLICATE_ALREADY_COVERED")
    override_candidate = collect_bullets(lines, "## Human-override-protected rows resolved (14)", "CANDIDATE")
    override_general = collect_bullets(lines, "## Human-override-protected rows resolved (14)", "GENERAL_ONLY")
    overlap_duplicates = collect_bullets(lines, "## Existing overlap duplicates retained (4)")

    if len(demotions) != 117:
        raise RuntimeError(f"expected 117 explicit demotions, got {len(demotions)}")
    if (len(boundary_candidate), len(boundary_general), len(boundary_duplicate)) != (5, 3, 1):
        raise RuntimeError("boundary decision counts do not match recorded final review")
    if (len(override_candidate), len(override_general)) != (10, 4):
        raise RuntimeError("human-override decision counts do not match recorded final review")
    if len(overlap_duplicates) != 4:
        raise RuntimeError("expected four retained overlap duplicates")

    decision_sets = {
        "demotions": demotions,
        "boundary_candidate": boundary_candidate,
        "boundary_general": boundary_general,
        "boundary_duplicate": boundary_duplicate,
        "override_candidate": override_candidate,
        "override_general": override_general,
        "overlap_duplicates": overlap_duplicates,
    }
    known = set(tags)
    for name, values in decision_sets.items():
        missing = values - known
        if missing:
            raise RuntimeError(f"{name} contains tags absent from queue: {sorted(missing)}")

    explicit_sets = list(decision_sets.values())
    for i, left in enumerate(explicit_sets):
        for right in explicit_sets[i + 1 :]:
            overlap = left & right
            if overlap:
                raise RuntimeError(f"conflicting explicit final decisions: {sorted(overlap)}")

    materialized: list[dict[str, str]] = []
    for row in queue:
        tag = row["canonical_tag"]
        if tag in demotions:
            status = "GENERAL_ONLY"
            reason = "final human review: ordinary/general expansion; Special would become overly Cartesian or redundant"
        elif tag in boundary_candidate:
            status = "CANDIDATE"
            reason = row.get("human_review_reason") or "final human boundary review: deep discovery value retained"
        elif tag in boundary_general:
            status = "GENERAL_ONLY"
            reason = "final human boundary review: General discovery is sufficient"
        elif tag in boundary_duplicate:
            status = "DUPLICATE_ALREADY_COVERED"
            reason = row.get("human_review_reason") or "existing Special semantic surface already covers the concept"
        elif tag in override_candidate:
            status = "CANDIDATE"
            reason = row.get("human_review_reason") or "protected prior human review retained after v2 disagreement"
        elif tag in override_general:
            status = "GENERAL_ONLY"
            reason = row.get("human_review_reason") or "final human override review: General discovery is sufficient"
        elif tag in overlap_duplicates:
            status = "DUPLICATE_ALREADY_COVERED"
            reason = row.get("human_review_reason") or "existing Special semantic surface already covers the concept"
        elif row["v2_status"] == "LIKELY_CANDIDATE":
            status = "CANDIDATE"
            reason = row.get("human_review_reason") or row.get("v2_reason") or "final human review retained v2 candidate"
        else:
            raise RuntimeError(f"unresolved final queue row: {tag} ({row['v2_status']})")

        count = int(row["post_count"])
        materialized.append(
            {
                "canonical_tag": tag,
                "post_count": str(count),
                "post_count_bucket": bucket(count),
                "aliases": row.get("aliases", ""),
                "concept_area": row.get("concept_area", ""),
                "final_status": status,
                "final_reason": reason,
                "v2_status": row.get("v2_status", ""),
                "v2_priority": row.get("v2_priority", ""),
                "human_review_status": row.get("human_review_status", ""),
                "nearest_special_identity": row.get("nearest_special_identity", ""),
                "queue_reason": row.get("queue_reason", ""),
            }
        )

    counts = Counter(row["final_status"] for row in materialized)
    expected = {
        "CANDIDATE": EXPECTED_CANDIDATE,
        "GENERAL_ONLY": EXPECTED_GENERAL,
        "DUPLICATE_ALREADY_COVERED": EXPECTED_DUPLICATE,
    }
    if dict(counts) != expected:
        raise RuntimeError(f"final status count mismatch: {dict(counts)} != {expected}")

    candidates = [row for row in materialized if row["final_status"] == "CANDIDATE"]
    exclusions = [row for row in materialized if row["final_status"] != "CANDIDATE"]
    candidates.sort(key=lambda row: (-int(row["post_count"]), row["canonical_tag"]))
    exclusions.sort(key=lambda row: (row["final_status"], -int(row["post_count"]), row["canonical_tag"]))
    write_rows(CANDIDATES, candidates)
    write_rows(EXCLUSIONS, exclusions)

    candidate_counts = [int(row["post_count"]) for row in candidates]
    bucket_counts = Counter(row["post_count_bucket"] for row in candidates)
    area_counts = Counter(row["concept_area"] for row in candidates)
    top = candidates[:20]
    bottom = sorted(candidates, key=lambda row: (int(row["post_count"]), row["canonical_tag"]))[:20]

    summary = [
        "# Issue #94 final candidate/exclusion artifacts v1",
        "",
        "Status: **MATERIALIZED FROM 324/324 FINAL HUMAN REVIEW / NO PRODUCTION MUTATION**",
        "",
        f"- final candidates: **{len(candidates)}**",
        f"- exclusion ledger rows: **{len(exclusions)}**",
        f"  - `GENERAL_ONLY`: **{counts['GENERAL_ONLY']}**",
        f"  - `DUPLICATE_ALREADY_COVERED`: **{counts['DUPLICATE_ALREADY_COVERED']}**",
        "- `CONTENT_FILTER_USED=NO`",
        "- `PRODUCTION_FILES_CHANGED=NO`",
        "- `ISSUE70_MUTATED=NO`",
        "",
        "## Candidate post-count distribution",
        "",
        f"- maximum: **{max(candidate_counts):,}**",
        f"- median: **{statistics.median(candidate_counts):,.0f}**",
        f"- minimum: **{min(candidate_counts):,}**",
        "",
        "| post_count bucket | candidates |",
        "|---|---:|",
    ]
    for label in (">=100k", "10k-99,999", "1k-9,999", "100-999", "<100"):
        summary.append(f"| `{label}` | {bucket_counts[label]} |")

    summary += ["", "## Candidate concept areas", "", "| area | candidates |", "|---|---:|"]
    for area, count in sorted(area_counts.items(), key=lambda item: (-item[1], item[0])):
        summary.append(f"| `{area}` | {count} |")

    summary += ["", "## Highest post-count candidates", "", "| canonical | post_count | area |", "|---|---:|---|"]
    for row in top:
        summary.append(f"| `{row['canonical_tag']}` | {int(row['post_count']):,} | `{row['concept_area']}` |")

    summary += ["", "## Lowest post-count candidates", "", "Low frequency is retained when the concept still has deep discovery value; post_count is not an admission threshold.", "", "| canonical | post_count | area |", "|---|---:|---|"]
    for row in bottom:
        summary.append(f"| `{row['canonical_tag']}` | {int(row['post_count']):,} | `{row['concept_area']}` |")

    summary += [
        "",
        "## Outputs",
        "",
        "- `docs/issue94/special_gap_candidates_v1.csv` — 195 final candidate rows, sorted by post_count descending.",
        "- `docs/issue94/special_gap_exclusion_ledger_v1.csv` — 124 General-only + 5 substantive duplicate rows.",
        "",
        "These are audit deliverables only. They do not promote any candidate into the production Special dictionary.",
        "",
    ]
    SUMMARY.write_text("\n".join(summary), encoding="utf-8")

    print(f"TOTAL={len(materialized)}")
    print(f"CANDIDATE={len(candidates)}")
    print(f"GENERAL_ONLY={counts['GENERAL_ONLY']}")
    print(f"DUPLICATE_ALREADY_COVERED={counts['DUPLICATE_ALREADY_COVERED']}")
    print(f"CANDIDATE_MAX_POST_COUNT={max(candidate_counts)}")
    print(f"CANDIDATE_MEDIAN_POST_COUNT={statistics.median(candidate_counts):.0f}")
    print(f"CANDIDATE_MIN_POST_COUNT={min(candidate_counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
