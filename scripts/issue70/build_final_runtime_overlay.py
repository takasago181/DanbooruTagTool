#!/usr/bin/env python3
"""Build the final Issue #70 2D-only runtime overlay.

Inputs are immutable historical runtime data, the completed full-scope census,
and the compact final semantic-fix handoff. The original runtime files are never
rewritten; a new finalized overlay is emitted.
"""
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / "docs/issue70/data/runtime/issue70_catalog_overlay.csv"
SCOPE_EXCLUDE = ROOT / "docs/issue70/scope/runtime_exclude_real3d_candidates.csv"
FIXES = ROOT / "docs/issue70/finalization/FINAL_SEMANTIC_FIXES.csv"
OUT = ROOT / "docs/issue70/data/runtime/issue70_catalog_overlay_2d_final.csv"
MANIFEST = ROOT / "docs/issue70/finalization/runtime_final_manifest.json"

EXPECTED_ORIGINAL = 92739
EXPECTED_EXCLUDED = 1532
EXPECTED_FINAL = 91207
EXPECTED_FINAL_BY_CATEGORY = {"Character": 35278, "Copyright": 7616, "Artist": 48313}
EXPECTED_FIXES = 9080


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise SystemExit(f"missing CSV header: {path}")
        return list(reader.fieldnames), list(reader)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def split_pipe(value: str) -> list[str]:
    return [x.strip() for x in value.split("|") if x.strip()]


def main() -> int:
    fields, original = read_csv(ORIGINAL)
    _, scope_rows = read_csv(SCOPE_EXCLUDE)
    _, fix_rows = read_csv(FIXES)

    required = {
        "row_id", "canonical_tag", "category", "category_name", "post_count",
        "display_ja", "search_ja", "aliases", "related_copyright", "translation_status",
    }
    missing = required - set(fields)
    if missing:
        raise SystemExit(f"original overlay missing fields: {sorted(missing)}")
    if len(original) != EXPECTED_ORIGINAL:
        raise SystemExit(f"original row count drift: {len(original)} != {EXPECTED_ORIGINAL}")
    if not fix_rows or len(fix_rows) > 9080:
        raise SystemExit(f"semantic effective fix row count invalid: {len(fix_rows)}")

    original_by_id = {r["row_id"]: r for r in original}
    if len(original_by_id) != len(original):
        raise SystemExit("duplicate original row_id")

    excluded = {}
    for row in scope_rows:
        rid = (row.get("row_id") or "").strip()
        if not rid:
            continue
        if rid in excluded:
            raise SystemExit(f"duplicate scope exclusion: {rid}")
        if (row.get("media_scope") or "").strip() != "REAL_3D":
            raise SystemExit(f"non-REAL_3D row in exclusion registry: {rid}")
        if rid not in original_by_id:
            raise SystemExit(f"scope exclusion unknown row: {rid}")
        if original_by_id[rid]["category_name"] not in {"Character", "Copyright"}:
            raise SystemExit(f"scope exclusion category violation: {rid}")
        excluded[rid] = row
    if len(excluded) != EXPECTED_EXCLUDED:
        raise SystemExit(f"scope exclusion count drift: {len(excluded)} != {EXPECTED_EXCLUDED}")

    fixes = {}
    verdict_counts = Counter()
    for row in fix_rows:
        rid = (row.get("row_id") or "").strip()
        if not rid or rid in fixes:
            raise SystemExit(f"invalid/duplicate semantic fix row: {rid}")
        if rid not in original_by_id:
            raise SystemExit(f"semantic fix unknown row: {rid}")
        src = original_by_id[rid]
        if (row.get("canonical_tag") or "").strip() != src["canonical_tag"]:
            raise SystemExit(f"semantic fix canonical mismatch: {rid}")
        if (row.get("category") or "").strip() != src["category_name"]:
            raise SystemExit(f"semantic fix category mismatch: {rid}")
        if (row.get("current_display_ja") or "").strip() != src["display_ja"].strip():
            raise SystemExit(f"semantic fix display baseline mismatch: {rid}")
        if (row.get("current_search_ja") or "").strip() != src["search_ja"].strip():
            raise SystemExit(f"semantic fix search baseline mismatch: {rid}")
        action = (row.get("effective_action") or "").strip()
        if action not in {"FIX_DISPLAY", "FIX_SEARCH", "FIX_BOTH"}:
            raise SystemExit(f"invalid semantic effective action: {rid} {action}")
        proposed_display = (row.get("proposed_display_ja") or "").strip()
        proposed_search = (row.get("proposed_search_ja") or "").strip()
        if action in {"FIX_DISPLAY", "FIX_BOTH"} and (not proposed_display or proposed_display == src["display_ja"].strip()):
            raise SystemExit(f"invalid effective display change: {rid}")
        if action in {"FIX_SEARCH", "FIX_BOTH"} and (not proposed_search or proposed_search == src["search_ja"].strip()):
            raise SystemExit(f"invalid effective search change: {rid}")
        if action == "FIX_DISPLAY" and proposed_search:
            raise SystemExit(f"unexpected search proposal for FIX_DISPLAY: {rid}")
        if action == "FIX_SEARCH" and proposed_display:
            raise SystemExit(f"unexpected display proposal for FIX_SEARCH: {rid}")
        fixes[rid] = row
        verdict_counts[action] += 1

    included_original = [r for r in original if r["row_id"] not in excluded]
    copyright_canonicals = {
        r["canonical_tag"] for r in included_original if r["category_name"] == "Copyright"
    }

    out_rows: list[dict[str, str]] = []
    applied_fix_rows = 0
    excluded_fix_rows = 0
    removed_relation_refs = 0
    characters_with_relations = 0

    for source in original:
        rid = source["row_id"]
        if rid in excluded:
            if rid in fixes:
                excluded_fix_rows += 1
            continue

        row = dict(source)
        fix = fixes.get(rid)
        if fix is not None:
            action = fix["effective_action"].strip()
            if action in {"FIX_DISPLAY", "FIX_BOTH"}:
                row["display_ja"] = fix["proposed_display_ja"].strip()
            if action in {"FIX_SEARCH", "FIX_BOTH"}:
                row["search_ja"] = fix["proposed_search_ja"].strip()
            applied_fix_rows += 1

        if row["category_name"] == "Character":
            before = split_pipe(row["related_copyright"])
            after = [x for x in before if x in copyright_canonicals]
            removed_relation_refs += len(before) - len(after)
            row["related_copyright"] = "|".join(after)
            if after:
                characters_with_relations += 1
        elif row["related_copyright"].strip():
            raise SystemExit(f"non-Character relation in source overlay: {rid}")

        if not row["display_ja"].strip():
            raise SystemExit(f"empty final display_ja: {rid}")
        out_rows.append(row)

    if len(out_rows) != EXPECTED_FINAL:
        raise SystemExit(f"final row count drift: {len(out_rows)} != {EXPECTED_FINAL}")

    by_category = Counter(r["category_name"] for r in out_rows)
    if dict(by_category) != EXPECTED_FINAL_BY_CATEGORY:
        raise SystemExit(f"final category count drift: {dict(by_category)} != {EXPECTED_FINAL_BY_CATEGORY}")

    canonicals = [r["canonical_tag"] for r in out_rows]
    if len(set(canonicals)) != len(canonicals):
        raise SystemExit("duplicate canonical in finalized Issue70 overlay")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(out_rows)

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "format_version": 1,
        "issue": 70,
        "policy": "Character/Copyright 2D-only; Artist fully retained; semantic final fixes applied",
        "original_overlay": str(ORIGINAL.relative_to(ROOT)).replace("\\", "/"),
        "original_overlay_sha256": sha256(ORIGINAL),
        "scope_exclusion": str(SCOPE_EXCLUDE.relative_to(ROOT)).replace("\\", "/"),
        "scope_exclusion_sha256": sha256(SCOPE_EXCLUDE),
        "semantic_fixes": str(FIXES.relative_to(ROOT)).replace("\\", "/"),
        "semantic_fixes_sha256": sha256(FIXES),
        "final_overlay": str(OUT.relative_to(ROOT)).replace("\\", "/"),
        "final_overlay_sha256": sha256(OUT),
        "original_rows": len(original),
        "excluded_real3d_rows": len(excluded),
        "final_rows": len(out_rows),
        "final_category_counts": dict(sorted(by_category.items())),
        "semantic_fix_rows": len(fixes),
        "semantic_effective_action_counts": dict(sorted(verdict_counts.items())),
        "semantic_fix_rows_applied": applied_fix_rows,
        "semantic_fix_rows_excluded_by_scope": excluded_fix_rows,
        "removed_related_copyright_refs": removed_relation_refs,
        "characters_with_related_copyright": characters_with_relations,
        "production_modified": False,
    }
    MANIFEST.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
