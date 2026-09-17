#!/usr/bin/env python3
"""Summarize Issue #70 second-stage external verification progress.

Counts both legacy/root ``external_resolution_*.csv`` overlays and the canonical
``external_resolutions/*.csv`` directory. Emits an exact unresolved queue sorted
by impact so verification can continue without re-checking completed rows.
Production Issue #70 data is read-only.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "docs/issue70/audit"
EXT = AUDIT / "external_resolutions"
SOURCE = ROOT / "docs/issue70/data/source/issue70_translation_source_with_relations.csv"
RUNTIME = ROOT / "docs/issue70/data/runtime/issue70_translation_results.csv"
OUT = AUDIT / "EXTERNAL_PROGRESS_LIVE.json"
QUEUE = AUDIT / "EXTERNAL_QUEUE_LIVE.csv"
FINAL_VALID = {"KEEP", "FIX_DISPLAY", "FIX_SEARCH", "FIX_BOTH"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def decision_tuple(entry: dict[str, str]) -> tuple[str, str, str]:
    return (
        entry["external_verdict"],
        entry["proposed_display_ja"],
        entry["proposed_search_ja"],
    )


def main() -> int:
    source = {r["row_id"]: r for r in read_csv(SOURCE)}
    runtime = {r["row_id"]: r for r in read_csv(RUNTIME)}

    external_ids: dict[str, dict[str, str]] = {}
    # Primary audit files live at the audit root. External overlay files also live
    # there, but never contain NEEDS_EXTERNAL_CHECK and therefore do not seed the queue.
    for path in sorted(AUDIT.glob("*.csv")):
        try:
            rows = read_csv(path)
        except Exception:
            continue
        for row in rows:
            rid = (row.get("row_id") or "").strip()
            verdict = (row.get("audit_verdict") or "").strip()
            if not rid or verdict != "NEEDS_EXTERNAL_CHECK":
                continue
            s = source.get(rid, {})
            rt = runtime.get(rid, {})
            external_ids[rid] = {
                "row_id": rid,
                "canonical_tag": (row.get("canonical_tag") or s.get("canonical_tag") or rt.get("canonical_tag") or "").strip(),
                "category": (row.get("category_name") or row.get("category") or s.get("category_name") or s.get("category") or "").strip(),
                "post_count": (row.get("post_count") or s.get("post_count") or "0").strip(),
                "display_ja": (row.get("display_ja") or rt.get("display_ja") or "").strip(),
                "search_ja": (row.get("search_ja") or rt.get("search_ja") or "").strip(),
                "translation_note": (row.get("translation_note") or rt.get("translation_note") or "").strip(),
                "primary_source_file": path.name,
            }

    observations: dict[str, list[dict[str, str]]] = {}

    def add_overlay(path: Path, row: dict[str, str], verdict_field: str) -> None:
        rid = (row.get("row_id") or "").strip()
        verdict = (row.get(verdict_field) or "").strip()
        if rid not in external_ids or verdict not in FINAL_VALID:
            return
        observations.setdefault(rid, []).append({
            "external_verdict": verdict,
            "proposed_display_ja": (row.get("proposed_display_ja") or "").strip(),
            "proposed_search_ja": (row.get("proposed_search_ja") or "").strip(),
            "source_file": str(path.relative_to(AUDIT)),
        })

    # Root overlays (batches 065+ and legacy external-resolution files).
    for path in sorted(AUDIT.glob("external_resolution_*.csv")):
        for row in read_csv(path):
            add_overlay(path, row, "audit_verdict")

    # Canonical external-resolution directory. Accept either historical
    # external_verdict or audit_verdict column names.
    if EXT.exists():
        for path in sorted(EXT.glob("*.csv")):
            for row in read_csv(path):
                field = "external_verdict" if (row.get("external_verdict") or "").strip() else "audit_verdict"
                add_overlay(path, row, field)

    resolved: dict[str, dict[str, str]] = {}
    conflicts: list[dict[str, object]] = []
    duplicate_same_decision_rows = 0
    for rid, entries in observations.items():
        decisions = {decision_tuple(e) for e in entries}
        if len(decisions) == 1:
            resolved[rid] = entries[-1]
            if len(entries) > 1:
                duplicate_same_decision_rows += 1
        else:
            conflicts.append({"row_id": rid, "canonical_tag": external_ids[rid]["canonical_tag"], "entries": entries})

    remaining_ids = set(external_ids) - set(resolved)
    remaining = [external_ids[rid] for rid in remaining_ids]
    remaining.sort(key=lambda r: (-int(r.get("post_count") or 0), r["row_id"]))

    fields = ["row_id", "canonical_tag", "category", "post_count", "display_ja", "search_ja", "translation_note", "primary_source_file"]
    with QUEUE.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(remaining)

    by_verdict = Counter(e["external_verdict"] for e in resolved.values())
    by_cat_resolved = Counter(external_ids[rid]["category"] or "<unknown>" for rid in resolved)
    by_cat_remaining = Counter(r["category"] or "<unknown>" for r in remaining)
    result = {
        "format_version": 2,
        "issue": 70,
        "production_modified": False,
        "initial_external_rows": len(external_ids),
        "resolved_external_rows": len(resolved),
        "remaining_external_rows": len(remaining),
        "conflicted_external_rows": len(conflicts),
        "duplicate_same_decision_rows": duplicate_same_decision_rows,
        "resolved_verdict_counts": dict(sorted(by_verdict.items())),
        "resolved_by_category": dict(sorted(by_cat_resolved.items())),
        "remaining_by_category": dict(sorted(by_cat_remaining.items())),
        "top_remaining": remaining[:30],
        "conflicts": conflicts,
        "next_step": "continue official-source verification in EXTERNAL_QUEUE_LIVE.csv impact order; keep production read-only until external closure",
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not conflicts else 2


if __name__ == "__main__":
    raise SystemExit(main())
