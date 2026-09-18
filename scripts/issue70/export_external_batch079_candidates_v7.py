#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "docs/issue70/audit"
ROOT_QUEUE = AUDIT / "EXTERNAL_QUEUE_LIVE.csv"
PROGRESS = AUDIT / "EXTERNAL_PROGRESS_LIVE.json"
OUT_ALL = AUDIT / "EXTERNAL_QUEUE_BATCH079_CANDIDATES.csv"
OUT_COPYRIGHT = AUDIT / "EXTERNAL_QUEUE_BATCH079_COPYRIGHT_CANDIDATES.csv"

TOP_N = 600
CONCRETE = {"KEEP", "FIX_DISPLAY", "FIX_SEARCH", "FIX_BOTH"}
VALID_CATEGORIES = {"Copyright", "Character", "Artist"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    root_rows = read_csv(ROOT_QUEUE)
    progress = json.loads(PROGRESS.read_text(encoding="utf-8"))

    assert root_rows, "EXTERNAL_QUEUE_LIVE.csv is empty"
    root_ids = [r["row_id"].strip() for r in root_rows]
    assert len(root_ids) == len(set(root_ids)), "duplicate row_id in EXTERNAL_QUEUE_LIVE.csv"
    root_by_id = {r["row_id"].strip(): r for r in root_rows}

    assert progress["production_modified"] is False
    assert progress["conflicted_external_rows"] == 0
    assert progress["initial_external_rows"] == len(root_rows)
    assert progress["resolved_external_rows"] + progress["remaining_external_rows"] == progress["initial_external_rows"]

    decisions: dict[str, set[str]] = defaultdict(set)

    # Only concrete external-resolution overlays determine whether a root queue row is resolved.
    # Historical audit CSVs are intentionally NOT scanned.
    for path in sorted(AUDIT.glob("external_resolution_*.csv")):
        for row in read_csv(path):
            rid = (row.get("row_id") or "").strip()
            verdict = (row.get("audit_verdict") or "").strip()
            if not rid or verdict not in CONCRETE:
                continue
            assert rid in root_by_id, (path.name, rid, "resolution row not in root external queue")
            decisions[rid].add(verdict)

    conflicts = {rid: sorted(v) for rid, v in decisions.items() if len(v) > 1}
    assert not conflicts, f"conflicting external resolutions: {conflicts}"

    resolved_ids = set(decisions)
    unresolved = [r for r in root_rows if r["row_id"].strip() not in resolved_ids]

    assert len(resolved_ids) == progress["resolved_external_rows"], (
        "resolved_count_mismatch",
        len(resolved_ids),
        progress["resolved_external_rows"],
    )
    assert len(unresolved) == progress["remaining_external_rows"], (
        "remaining_count_mismatch",
        len(unresolved),
        progress["remaining_external_rows"],
    )

    remaining_by_category = {k: 0 for k in VALID_CATEGORIES}
    for row in unresolved:
        category = (row.get("category") or "").strip()
        assert category in VALID_CATEGORIES, (row.get("row_id"), category)
        remaining_by_category[category] += 1

    assert remaining_by_category == progress["remaining_by_category"], (
        "remaining_category_mismatch",
        remaining_by_category,
        progress["remaining_by_category"],
    )

    def post_count(row: dict[str, str]) -> int:
        return int((row.get("post_count") or "0").strip() or 0)

    unresolved.sort(key=lambda r: (-post_count(r), r["row_id"]))
    top = unresolved[: min(TOP_N, len(unresolved))]
    copyright_rows = [r for r in top if r["category"] == "Copyright"]

    fields_all = [
        "row_id","canonical_tag","post_count","display_ja","search_ja",
        "translation_note","reason_code","source_file","effective_source_file"
    ]
    with OUT_ALL.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields_all)
        w.writeheader()
        for r in top:
            source = (r.get("primary_source_file") or "").strip()
            w.writerow({
                "row_id": r["row_id"],
                "canonical_tag": r["canonical_tag"],
                "post_count": r["post_count"],
                "display_ja": r["display_ja"],
                "search_ja": r["search_ja"],
                "translation_note": r["translation_note"],
                "reason_code": "EFFECTIVE_NEEDS_EXTERNAL_CHECK",
                "source_file": source,
                "effective_source_file": source,
            })

    fields_c = [
        "row_id","canonical_tag","post_count","display_ja","search_ja",
        "translation_note","reason_code","source_file"
    ]
    with OUT_COPYRIGHT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields_c)
        w.writeheader()
        for r in copyright_rows:
            w.writerow({
                "row_id": r["row_id"],
                "canonical_tag": r["canonical_tag"],
                "post_count": r["post_count"],
                "display_ja": r["display_ja"],
                "search_ja": r["search_ja"],
                "translation_note": r["translation_note"],
                "reason_code": "EFFECTIVE_NEEDS_EXTERNAL_CHECK",
                "source_file": (r.get("primary_source_file") or "").strip(),
            })

    print({
        "initial_external_rows": len(root_rows),
        "resolved_external_rows": len(resolved_ids),
        "remaining_external_rows": len(unresolved),
        "remaining_by_category": remaining_by_category,
        "candidate_rows": len(top),
        "copyright_candidates": len(copyright_rows),
        "production_modified": False,
    })


if __name__ == "__main__":
    main()
