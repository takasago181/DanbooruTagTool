#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "docs/issue70/audit"
ROOT_QUEUE = AUDIT / "EXTERNAL_QUEUE_LIVE.csv"
OUT_ALL = AUDIT / "EXTERNAL_QUEUE_BATCH079_CANDIDATES.csv"
OUT_COPYRIGHT = AUDIT / "EXTERNAL_QUEUE_BATCH079_COPYRIGHT_CANDIDATES.csv"
TOP_N = 600
VALID = {"KEEP","FIX_DISPLAY","FIX_SEARCH","FIX_BOTH","NEEDS_EXTERNAL_CHECK","NEEDS_USER_DECISION"}
VALID_CATEGORIES = {"Copyright","Character","Artist"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def infer_category(root_category: str, source_file: str) -> str:
    category = (root_category or "").strip()
    if category in VALID_CATEGORIES:
        return category
    name = (source_file or "").lower()
    if name.startswith("copyright_") or name.startswith("external_resolution_copyright_"):
        return "Copyright"
    if name.startswith("character_") or name.startswith("external_resolution_character_"):
        return "Character"
    if name.startswith("artist_") or name.startswith("external_resolution_artist_"):
        return "Artist"
    raise AssertionError(("category_unresolved", source_file, root_category))


def main() -> None:
    root_rows = read_csv(ROOT_QUEUE)
    root_by_id = {r["row_id"]: r for r in root_rows}
    base: dict[str, dict[str, str]] = {}
    overlays: dict[str, dict[str, str]] = {}

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
            root = root_by_id.get(rid, {})
            source_file = path.name
            category = (root.get("category") or r.get("category") or "").strip()
            if not is_overlay:
                category = infer_category(category, source_file)
            item = {
                "row_id": rid,
                "canonical_tag": (r.get("canonical_tag") or root.get("canonical_tag") or "").strip(),
                "category": category,
                "post_count": (r.get("post_count") or root.get("post_count") or "0").strip(),
                "display_ja": (r.get("display_ja") or root.get("display_ja") or "").strip(),
                "search_ja": (r.get("search_ja") or root.get("search_ja") or "").strip(),
                "translation_note": (r.get("translation_note") or root.get("translation_note") or "").strip(),
                "audit_verdict": verdict,
                "source_file": source_file,
                "reason_code": (r.get("reason_code") or "").strip(),
            }
            if is_overlay:
                overlays[rid] = item
            elif rid not in base:
                base[rid] = item

    unresolved: list[dict[str, str]] = []
    for rid, b in base.items():
        eff = overlays.get(rid, b)
        if eff["audit_verdict"] != "NEEDS_EXTERNAL_CHECK":
            continue
        root = root_by_id.get(rid, {})
        category = infer_category(root.get("category") or "", b["source_file"])
        unresolved.append({
            "row_id": b["row_id"],
            "canonical_tag": b["canonical_tag"],
            "category": category,
            "post_count": b["post_count"],
            "display_ja": b["display_ja"],
            "search_ja": b["search_ja"],
            "translation_note": b["translation_note"],
            "reason_code": b["reason_code"],
            "source_file": b["source_file"],
            "effective_source_file": eff["source_file"],
        })

    unresolved.sort(key=lambda r: (-int(r.get("post_count") or 0), r["row_id"]))
    top = unresolved[:TOP_N]
    copyright_rows = [r for r in top if r["category"] == "Copyright"]

    fields_all = ["row_id","canonical_tag","category","post_count","display_ja","search_ja","translation_note","reason_code","source_file","effective_source_file"]
    with OUT_ALL.open("w", encoding="utf-8-sig", newline="") as f:
        w=csv.DictWriter(f, fieldnames=fields_all)
        w.writeheader(); w.writerows(top)

    fields_c = ["row_id","canonical_tag","post_count","display_ja","search_ja","translation_note","reason_code","source_file"]
    with OUT_COPYRIGHT.open("w", encoding="utf-8-sig", newline="") as f:
        w=csv.DictWriter(f, fieldnames=fields_c)
        w.writeheader()
        w.writerows([{k:r[k] for k in fields_c} for r in copyright_rows])

    print({
        "unresolved_external": len(unresolved),
        "candidate_rows": len(top),
        "copyright_candidates": len(copyright_rows),
        "production_modified": False,
    })


if __name__ == "__main__":
    main()
