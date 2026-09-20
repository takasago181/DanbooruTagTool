#!/usr/bin/env python3
"""Export the final effective Issue #70 semantic FIX decisions.

This is a compact promotion handoff derived from the read-only semantic audit.
It does not modify source/runtime Issue #70 data.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import summarize_semantic_audit_progress as sap

OUT = sap.AUDIT_DIR / "FINAL_SEMANTIC_FIXES.csv"
SUMMARY = sap.AUDIT_DIR / "FINAL_SEMANTIC_FIXES_SUMMARY.json"
FIX_VERDICTS = {"FIX_DISPLAY", "FIX_SEARCH", "FIX_BOTH"}
EXPECTED = {"FIX_BOTH": 766, "FIX_DISPLAY": 8054, "FIX_SEARCH": 260}


def main() -> int:
    ledger = sap.run_census()
    ledger_by_id = {row["row_id"]: row for row in ledger}
    if len(ledger_by_id) != len(ledger):
        raise SystemExit("v3 ledger row_id is not unique")

    observations: dict[str, list[dict[str, str]]] = defaultdict(list)
    for path in sorted(sap.AUDIT_DIR.glob("*.csv")):
        # The exported handoff itself must never feed back into decision resolution.
        if path.name == OUT.name:
            continue
        is_external = path.name.startswith(sap.EXTERNAL_PREFIX)
        try:
            rows = sap.read_csv(path)
        except Exception:
            continue
        for row in rows:
            rid = (row.get("row_id") or "").strip()
            verdict = (row.get("audit_verdict") or "").strip()
            if not rid or verdict not in sap.VALID_VERDICTS or rid not in ledger_by_id:
                continue
            observations[rid].append({
                "source_file": path.name,
                "audit_verdict": verdict,
                "proposed_display_ja": (row.get("proposed_display_ja") or "").strip(),
                "proposed_search_ja": (row.get("proposed_search_ja") or "").strip(),
                "reason_code": (row.get("reason_code") or "").strip(),
                "confidence": (row.get("confidence") or "").strip(),
                "is_external_resolution": "1" if is_external else "0",
            })

    resolved: dict[str, dict[str, str]] = {}
    conflicts: list[str] = []
    for rid, entries in observations.items():
        entry, is_conflict, _ = sap.resolve_entries(entries)
        if is_conflict or entry is None:
            conflicts.append(rid)
        else:
            resolved[rid] = entry
    if conflicts:
        raise SystemExit(f"semantic decision conflicts remain: {len(conflicts)}")

    fixes: list[dict[str, str]] = []
    for rid in sorted(resolved):
        entry = resolved[rid]
        verdict = entry["audit_verdict"]
        if verdict not in FIX_VERDICTS:
            continue
        src = ledger_by_id[rid]
        current_display = (src.get("display_ja") or "").strip()
        current_search = (src.get("search_ja") or "").strip()
        proposed_display = entry["proposed_display_ja"]
        proposed_search = entry["proposed_search_ja"]

        if verdict == "FIX_DISPLAY":
            if not proposed_display or proposed_display == current_display or proposed_search:
                raise SystemExit(f"invalid FIX_DISPLAY proposal: {rid}")
        elif verdict == "FIX_SEARCH":
            if not proposed_search or proposed_search == current_search or proposed_display:
                raise SystemExit(f"invalid FIX_SEARCH proposal: {rid}")
        elif verdict == "FIX_BOTH":
            if (not proposed_display or not proposed_search or
                    proposed_display == current_display or proposed_search == current_search):
                raise SystemExit(f"invalid FIX_BOTH proposal: {rid}")

        fixes.append({
            "row_id": rid,
            "canonical_tag": (src.get("canonical_tag") or "").strip(),
            "category": (src.get("category_name") or "").strip(),
            "post_count": (src.get("post_count") or "").strip(),
            "audit_verdict": verdict,
            "current_display_ja": current_display,
            "current_search_ja": current_search,
            "proposed_display_ja": proposed_display,
            "proposed_search_ja": proposed_search,
            "reason_code": entry.get("reason_code", ""),
            "confidence": entry.get("confidence", ""),
            "decision_source": entry.get("source_file", ""),
        })

    counts = Counter(row["audit_verdict"] for row in fixes)
    if dict(sorted(counts.items())) != dict(sorted(EXPECTED.items())):
        raise SystemExit(f"fix verdict count drift: {dict(counts)} != {EXPECTED}")
    if len(fixes) != sum(EXPECTED.values()):
        raise SystemExit(f"fix row count drift: {len(fixes)}")

    fields = [
        "row_id", "canonical_tag", "category", "post_count", "audit_verdict",
        "current_display_ja", "current_search_ja",
        "proposed_display_ja", "proposed_search_ja",
        "reason_code", "confidence", "decision_source",
    ]
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(fixes)

    summary = {
        "format_version": 1,
        "issue": 70,
        "production_modified": False,
        "semantic_ledger_rows": len(ledger),
        "effective_resolved_rows": len(resolved),
        "conflicted_rows": 0,
        "fix_rows": len(fixes),
        "fix_verdict_counts": dict(sorted(counts.items())),
        "keep_rows": sum(1 for e in resolved.values() if e["audit_verdict"] == "KEEP"),
        "unresolved_rows": sum(1 for e in resolved.values() if e["audit_verdict"] in {"NEEDS_EXTERNAL_CHECK", "NEEDS_USER_DECISION"}),
        "purpose": "compact promotion handoff; original accepted Issue70 result rows remain immutable",
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
