#!/usr/bin/env python3
"""Rejoin retained source candidate inventories to the live Issue #216 cohort."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

try:
    from authority_coverage import read_csv
except ModuleNotFoundError:
    from scripts.issue216.authority_coverage import read_csv

ROOT = Path(__file__).resolve().parents[2]
ISSUE216 = ROOT / "docs/issue216"
FIELDS = [
    "source_id", "copyright_canonical", "source_url", "source_type", "scope_sha256",
    "matching_inventory_files", "open_auto_candidates", "open_review_required", "open_no_match",
    "open_outside_or_terminal", "open_candidate_characters", "existing_exact_member_count",
    "reuse_reaudit_disposition",
]


def read(path: Path) -> list[dict[str, str]]:
    return read_csv(path)


def write(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def audit(directory: Path = ISSUE216) -> list[dict[str, str]]:
    sources = read(directory / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv")
    members = read(directory / "AUTHORITY_SOURCE_MEMBERS_V1.csv")
    decisions = {row["canonical_character"]: row for row in read(directory / "AUTHORITY_COVERAGE_DECISIONS_V1.csv")}
    cohort = {row["canonical_character"] for row in read(directory / "AUTHORITY_COVERAGE_COHORT_V1.csv")}
    scratch_inventory_dir = ROOT / ".tmp-issue216-work/tracked-mapping-artifacts-2026-09-30"
    inventories = sorted({
        *directory.glob("SOURCE_MAPPING_CANDIDATES_*.csv"),
        *(scratch_inventory_dir.rglob("SOURCE_MAPPING_CANDIDATES_*.csv") if scratch_inventory_dir.exists() else []),
    })
    rows: list[dict[str, str]] = []
    for source in sources:
        matching = []
        counts = {"AUTO_MAPPING_CANDIDATE": 0, "REVIEW_REQUIRED": 0, "NO_MATCH": 0, "outside": 0}
        open_tags: set[str] = set()
        for inventory in inventories:
            review_file_rows = read(inventory)
            relevant = [item for item in review_file_rows if
                        item.get("source_id") == source["source_id"]
                        and item.get("source_url") == source["source_url"]
                        and item.get("source_scope") == source["source_scope"]]
            if not relevant:
                continue
            matching.append(inventory.name)
            review_path = inventory.with_name(inventory.name.replace("SOURCE_MAPPING_CANDIDATES_", "MAPPING_REVIEW_", 1))
            review_status = {}
            if review_path.is_file():
                for item in read(review_path):
                    review_status[(item.get("matched_surface", ""), item.get("canonical_character", ""))] = item.get("review_outcome", item.get("review_status", ""))
            seen_surfaces = set()
            for item in relevant:
                surface_key = (item.get("matched_surface", ""), item.get("candidate_status", ""), item.get("competing_tags", ""))
                if surface_key in seen_surfaces:
                    continue
                seen_surfaces.add(surface_key)
                possible = {item.get("canonical_character", "").strip()}
                possible.update(value.strip() for value in item.get("competing_tags", "").split("|") if value.strip())
                possible.discard("")
                open_possible = {tag for tag in possible if tag in cohort and decisions.get(tag, {}).get("research_state") == "UNRESEARCHED"}
                status = item.get("candidate_status", "")
                accepted_review_tags = {tag for tag in possible if not review_status.get((item.get("matched_surface", ""), tag), "").upper().startswith(("REJECT", "EXCLUDE"))}
                open_possible &= accepted_review_tags
                if open_possible:
                    if status == "AUTO_MAPPING_CANDIDATE":
                        counts["AUTO_MAPPING_CANDIDATE"] += 1
                    elif status == "REVIEW_REQUIRED":
                        counts["REVIEW_REQUIRED"] += 1
                    else:
                        counts["outside"] += 1
                    open_tags.update(open_possible)
                elif status == "NO_MATCH":
                    counts["NO_MATCH"] += 1
                elif status not in {"NO_MATCH", ""}:
                    counts["outside"] += 1
        exact_count = sum(1 for item in members if item["source_id"] == source["source_id"] and item["mapping_status"] == "EXACT_COVERED")
        disposition = "open candidate requires mapping/conflict review" if counts["AUTO_MAPPING_CANDIDATE"] or counts["REVIEW_REQUIRED"] else "no open mapped cohort candidate in retained exact-scope inventories"
        rows.append({
            "source_id": source["source_id"], "copyright_canonical": source["copyright_canonical"],
            "source_url": source["source_url"], "source_type": source["source_type"],
            "scope_sha256": __import__("hashlib").sha256(source["source_scope"].encode("utf-8")).hexdigest(),
            "matching_inventory_files": "|".join(matching),
            "open_auto_candidates": str(counts["AUTO_MAPPING_CANDIDATE"]),
            "open_review_required": str(counts["REVIEW_REQUIRED"]),
            "open_no_match": str(counts["NO_MATCH"]), "open_outside_or_terminal": str(counts["outside"]),
            "open_candidate_characters": "|".join(sorted(open_tags)),
            "existing_exact_member_count": str(exact_count), "reuse_reaudit_disposition": disposition,
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ISSUE216 / "SOURCE_REGISTRY_REAUDIT_2026-09-30.csv")
    args = parser.parse_args()
    rows = audit()
    write(args.output, rows)
    print(f"audited {len(rows)} sources; open AUTO={sum(int(r['open_auto_candidates']) for r in rows)}, "
          f"open REVIEW_REQUIRED={sum(int(r['open_review_required']) for r in rows)}; "
          f"mapped exact rows={sum(int(r['existing_exact_member_count']) for r in rows)}")


if __name__ == "__main__":
    main()
