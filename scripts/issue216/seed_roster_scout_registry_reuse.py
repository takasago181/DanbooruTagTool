#!/usr/bin/env python3
"""Rejoin already accepted roster scopes into the Issue #216 scout cache.

This does not claim a full roster harvest: completeness remains UNKNOWN. Existing
manual SCOUTED rows take precedence, so new registry rows can be added safely.
"""
from __future__ import annotations

import csv
import hashlib
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
ISSUE216 = ROOT / "docs/issue216"
SCOUT = ISSUE216 / "ROSTER_SCOUT_INVENTORY_V1.csv"
FIELDS = [
    "candidate_root", "source_id", "source_url", "source_owner", "source_domain", "source_family",
    "roster_scope", "roster_status", "completeness", "roster_surface_count", "exact_cohort_members",
    "exact_open_members", "ambiguous_members", "review_state", "source_fingerprint", "reviewed_at",
    "review_cost_class", "notes",
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build() -> list[dict[str, str]]:
    sources = read(ISSUE216 / "COPYRIGHT_AUTHORITY_REGISTRY_V1.csv")
    members = read(ISSUE216 / "AUTHORITY_SOURCE_MEMBERS_V1.csv")
    decisions = {r["canonical_character"]: r for r in read(ISSUE216 / "AUTHORITY_COVERAGE_DECISIONS_V1.csv")}
    existing = read(SCOUT) if SCOUT.exists() else []
    by_source: dict[str, set[str]] = defaultdict(set)
    for row in members:
        if row.get("mapping_status") == "EXACT_COVERED":
            by_source[row["source_id"]].add(row["canonical_character"])
    accepted_manual = {r.get("source_id", ""): r for r in existing if r.get("review_state") == "SCOUTED" and r.get("source_id")}
    rows = [r for r in existing if r.get("review_state") == "SCOUTED"]
    for source in sources:
        if (source.get("source_status") != "ACCEPTED" or source.get("exact_roster_available", "").lower() != "true"
                or source.get("reusable", "").lower() != "true"):
            continue
        sid = source["source_id"]
        if sid in accepted_manual:
            continue
        tags = by_source.get(sid, set())
        host = urlparse(source.get("source_url", "")).hostname or ""
        fingerprint = hashlib.sha256((source.get("source_url", "") + "\n" + source.get("source_scope", "")).encode()).hexdigest()
        open_tags = {tag for tag in tags if decisions.get(tag, {}).get("research_state") == "UNRESEARCHED"}
        rows.append({
            "candidate_root": source.get("copyright_canonical", ""), "source_id": sid,
            "source_url": source.get("source_url", ""), "source_owner": source.get("authority_owner", ""),
            "source_domain": host, "source_family": host, "roster_scope": source.get("source_scope", ""),
            "roster_status": "FOUND", "completeness": "UNKNOWN", "roster_surface_count": "",
            "exact_cohort_members": " | ".join(sorted(tags)), "exact_open_members": " | ".join(sorted(open_tags)),
            "ambiguous_members": "", "review_state": "REGISTRY_REJOIN", "source_fingerprint": fingerprint,
            "reviewed_at": source.get("reviewed_at", ""), "review_cost_class": "REUSE",
            "notes": "Existing accepted reusable roster scope rejoined from current source/member ledgers; this does not claim complete extraction. Roster completeness remains UNKNOWN.",
        })
    return sorted(rows, key=lambda r: (r["candidate_root"], r["source_url"], r["source_id"]))


if __name__ == "__main__":
    result = build()
    write(SCOUT, result)
    print(f"registry roster scopes rejoined: {len(result)}; completeness left UNKNOWN")
