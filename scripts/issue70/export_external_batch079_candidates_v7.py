#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "docs/issue70/audit"
ROOT_QUEUE = AUDIT / "EXTERNAL_QUEUE_LIVE.csv"
PROGRESS = AUDIT / "EXTERNAL_PROGRESS_LIVE.json"
OUT_ALL = AUDIT / "EXTERNAL_QUEUE_BATCH079_CANDIDATES.csv"
OUT_COPYRIGHT = AUDIT / "EXTERNAL_QUEUE_BATCH079_COPYRIGHT_CANDIDATES.csv"

TOP_N = 600
VALID = {"KEEP","FIX_DISPLAY","FIX_SEARCH","FIX_BOTH","NEEDS_EXTERNAL_CHECK","NEEDS_USER_DECISION"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> None:
    progress = json.loads(PROGRESS.read_text(encoding="utf-8"))
    assert progress["production_modified"] is False
    assert progress["conflicted_external_rows"] == 0
    assert progress["resolved_external_rows"] + progress["remaining_external_rows"] == progress["initial_external_rows"]

    base: dict[str, dict[str, str]] = {}
    overlays: dict[str, dict[str, str]] = {}

    # Historical audit CSVs define the original external population.
    # Category is intentionally NOT inferred here.
    for path in sorted(AUDIT.glob("*.csv")):
        if path.name in {OUT_ALL.name, OUT_COPYRIGHT.name}:
            continue
        is_overlay = path.name.startswith("external_resolution_")
        try:
            rows = read_csv(path)
        except Exception:
            continue

        for r in rows:
            rid = (r.get("row_id") or "").strip()
            verdict = (r.get("audit_verdict") or "").strip()
            if not rid or verdict not in VALID:
                continue

            item = {
                "row_id": rid,
                "canonical_tag": (r.get("canonical_tag") or "").strip(),
                "post_count": (r.get("post_count") or "0").strip(),
                "display_ja": (r.get("display_ja") or "").strip(),
                "search_ja": (r.get("search_ja") or "").strip(),
                "translation_note": (r.get("translation_note") or "").strip(),
                "audit_verdict": verdict,
                "source_file": path.name,
                "reason_code": (r.get("reason_code") or "").strip(),
            }

            if is_overlay:
                overlays[rid] = item
            elif rid not in base:
                base[rid] = item

    unresolved: list[dict[str, str]] = []
    for rid, b in base.items():
        effective = overlays.get(rid, b)
        if effective["audit_verdict"] != "NEEDS_EXTERNAL_CHECK":
            continue
        unresolved.append({
            "row_id": b["row_id"],
            "canonical_tag": b["canonical_tag"],
            "post_count": b["post_count"],
            "display_ja": b["display_ja"],
            "search_ja": b["search_ja"],
            "translation_note": b["translation_note"],
            "reason_code": b["reason_code"],
            "source_file": b["source_file"],
            "effective_source_file": effective["source_file"],
        })

    assert len(unresolved) == progress["remaining_external_rows"], (
        "remaining_external_mismatch",
        len(unresolved),
        progress["remaining_external_rows"],
    )

    unresolved.sort(key=lambda r: (-int(r.get("post_count") or 0), r["row_id"]))
    top = unresolved[: min(TOP_N, len(unresolved))]

    # EXTERNAL_QUEUE_LIVE is authoritative for category where a row is present.
    # Missing rows are not guessed and therefore cannot enter Copyright-only output.
    root = {r["row_id"]: r for r in read_csv(ROOT_QUEUE)}
    copyright_rows = [
        r for r in top
        if r["row_id"] in root and (root[r["row_id"]].get("category") or "").strip() == "Copyright"
    ]

    fields_all = [
        "row_id","canonical_tag","post_count","display_ja","search_ja",
        "translation_note","reason_code","source_file","effective_source_file"
    ]
    with OUT_ALL.open("w", encoding="utf-8-sig", newline="") as f:
        w=csv.DictWriter(f, fieldnames=fields_all)
        w.writeheader(); w.writerows(top)

    fields_c = [
        "row_id","canonical_tag","post_count","display_ja","search_ja",
        "translation_note","reason_code","source_file"
    ]
    with OUT_COPYRIGHT.open("w", encoding="utf-8-sig", newline="") as f:
        w=csv.DictWriter(f, fieldnames=fields_c)
        w.writeheader()
        w.writerows([{k:r[k] for k in fields_c} for r in copyright_rows])

    print({
        "audited_base_rows": len(base),
        "initial_external_rows": progress["initial_external_rows"],
        "remaining_external_rows": len(unresolved),
        "candidate_rows": len(top),
        "copyright_candidates": len(copyright_rows),
        "root_queue_rows": len(root),
        "top_rows_missing_from_root": sum(r["row_id"] not in root for r in top),
        "production_modified": False,
    })


if __name__ == "__main__":
    main()
