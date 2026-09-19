#!/usr/bin/env python3
"""Summarize Issue #70 second-stage external verification progress.

The external queue must contain only rows whose *effective primary audit verdict*
is NEEDS_EXTERNAL_CHECK. A later broad defer batch must not reopen a row that
already has a concrete KEEP/FIX decision. Among concrete primary decisions, the
latest numbered batch supersedes older concrete decisions; disagreement inside
the same latest batch is surfaced as a primary conflict.

External verification overlays are then applied with the same later-batch
supersession rule. Production Issue #70 data is read-only.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "docs/issue70/audit"
EXT = AUDIT / "external_resolutions"
SOURCE = ROOT / "docs/issue70/data/source/issue70_translation_source_with_relations.csv"
RUNTIME = ROOT / "docs/issue70/data/runtime/issue70_translation_results.csv"
OUT = AUDIT / "EXTERNAL_PROGRESS_LIVE.json"
QUEUE = AUDIT / "EXTERNAL_QUEUE_LIVE.csv"
FINAL_VALID = {"KEEP", "FIX_DISPLAY", "FIX_SEARCH", "FIX_BOTH"}
PRIMARY_VALID = FINAL_VALID | {"NEEDS_EXTERNAL_CHECK", "NEEDS_USER_DECISION"}
BATCH_RE = re.compile(r"batch(\d+)", re.I)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def batch_number(path: Path) -> int:
    m = BATCH_RE.search(path.name)
    return int(m.group(1)) if m else 0


def decision_tuple(entry: dict[str, str], verdict_key: str) -> tuple[str, str, str]:
    return (
        entry[verdict_key],
        entry["proposed_display_ja"],
        entry["proposed_search_ja"],
    )


def is_external_overlay(path: Path) -> bool:
    return path.name.startswith("external_resolution_") or EXT in path.parents


def main() -> int:
    source = {r["row_id"]: r for r in read_csv(SOURCE)}
    runtime = {r["row_id"]: r for r in read_csv(RUNTIME)}

    # 1) Resolve effective PRIMARY audit decisions.
    primary_obs: dict[str, list[dict[str, object]]] = defaultdict(list)
    for path in sorted(AUDIT.glob("*.csv")):
        if is_external_overlay(path):
            continue
        try:
            rows = read_csv(path)
        except Exception:
            continue
        for row in rows:
            rid = (row.get("row_id") or "").strip()
            verdict = (row.get("audit_verdict") or "").strip()
            if not rid or verdict not in PRIMARY_VALID:
                continue
            primary_obs[rid].append({
                "audit_verdict": verdict,
                "proposed_display_ja": (row.get("proposed_display_ja") or "").strip(),
                "proposed_search_ja": (row.get("proposed_search_ja") or "").strip(),
                "source_file": path.name,
                "batch": batch_number(path),
                "post_count": (row.get("post_count") or source.get(rid, {}).get("post_count") or "0").strip(),
            })

    effective_primary: dict[str, dict[str, object]] = {}
    primary_conflicts: list[dict[str, object]] = []
    primary_defer_suppressed_by_concrete = 0
    for rid, entries in primary_obs.items():
        concrete = [e for e in entries if e["audit_verdict"] in FINAL_VALID]
        if concrete:
            # A concrete semantic decision is stronger than a broad defer marker.
            primary_defer_suppressed_by_concrete += sum(e["audit_verdict"] == "NEEDS_EXTERNAL_CHECK" for e in entries)
            latest_batch = max(int(e["batch"]) for e in concrete)
            latest = [e for e in concrete if int(e["batch"]) == latest_batch]
            decisions = {decision_tuple(e, "audit_verdict") for e in latest}
            if len(decisions) == 1:
                effective_primary[rid] = latest[-1]
            else:
                primary_conflicts.append({
                    "row_id": rid,
                    "canonical_tag": source.get(rid, {}).get("canonical_tag", ""),
                    "latest_concrete_batch": latest_batch,
                    "entries": latest,
                })
        else:
            # No concrete decision exists: keep the latest defer/user-decision state.
            latest_batch = max(int(e["batch"]) for e in entries)
            latest = [e for e in entries if int(e["batch"]) == latest_batch]
            verdicts = {str(e["audit_verdict"]) for e in latest}
            if len(verdicts) == 1:
                effective_primary[rid] = latest[-1]
            else:
                primary_conflicts.append({
                    "row_id": rid,
                    "canonical_tag": source.get(rid, {}).get("canonical_tag", ""),
                    "latest_defer_batch": latest_batch,
                    "entries": latest,
                })

    external_ids: dict[str, dict[str, str]] = {}
    for rid, decision in effective_primary.items():
        if decision["audit_verdict"] != "NEEDS_EXTERNAL_CHECK":
            continue
        s = source.get(rid, {})
        rt = runtime.get(rid, {})
        external_ids[rid] = {
            "row_id": rid,
            "canonical_tag": (s.get("canonical_tag") or rt.get("canonical_tag") or "").strip(),
            "category": (s.get("category_name") or s.get("category") or "").strip(),
            "post_count": (s.get("post_count") or decision.get("post_count") or "0").strip(),
            "display_ja": (rt.get("display_ja") or "").strip(),
            "search_ja": (rt.get("search_ja") or "").strip(),
            "translation_note": (rt.get("translation_note") or "").strip(),
            "primary_source_file": str(decision["source_file"]),
        }

    # 2) Apply EXTERNAL verification overlays.
    observations: dict[str, list[dict[str, object]]] = defaultdict(list)

    def add_overlay(path: Path, row: dict[str, str], verdict_field: str) -> None:
        rid = (row.get("row_id") or "").strip()
        verdict = (row.get(verdict_field) or "").strip()
        if rid not in external_ids or verdict not in FINAL_VALID:
            return
        observations[rid].append({
            "external_verdict": verdict,
            "proposed_display_ja": (row.get("proposed_display_ja") or "").strip(),
            "proposed_search_ja": (row.get("proposed_search_ja") or "").strip(),
            "source_file": str(path.relative_to(AUDIT)),
            "batch": batch_number(path),
        })

    for path in sorted(AUDIT.glob("external_resolution_*.csv")):
        for row in read_csv(path):
            add_overlay(path, row, "audit_verdict")
    if EXT.exists():
        for path in sorted(EXT.glob("*.csv")):
            for row in read_csv(path):
                field = "external_verdict" if (row.get("external_verdict") or "").strip() else "audit_verdict"
                add_overlay(path, row, field)

    resolved: dict[str, dict[str, object]] = {}
    external_conflicts: list[dict[str, object]] = []
    duplicate_same_decision_rows = 0
    superseded_external_rows = 0
    for rid, entries in observations.items():
        latest_batch = max(int(e["batch"]) for e in entries)
        latest = [e for e in entries if int(e["batch"]) == latest_batch]
        superseded_external_rows += len(entries) - len(latest)
        decisions = {decision_tuple(e, "external_verdict") for e in latest}
        if len(decisions) == 1:
            resolved[rid] = latest[-1]
            if len(latest) > 1:
                duplicate_same_decision_rows += 1
        else:
            external_conflicts.append({
                "row_id": rid,
                "canonical_tag": external_ids[rid]["canonical_tag"],
                "latest_batch": latest_batch,
                "entries": latest,
            })

    remaining = [external_ids[rid] for rid in set(external_ids) - set(resolved)]
    remaining.sort(key=lambda r: (-int(r.get("post_count") or 0), r["row_id"]))

    fields = ["row_id", "canonical_tag", "category", "post_count", "display_ja", "search_ja", "translation_note", "primary_source_file"]
    with QUEUE.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(remaining)

    by_verdict = Counter(str(e["external_verdict"]) for e in resolved.values())
    by_cat_resolved = Counter(external_ids[rid]["category"] or "<unknown>" for rid in resolved)
    by_cat_remaining = Counter(r["category"] or "<unknown>" for r in remaining)
    result = {
        "format_version": 3,
        "issue": 70,
        "production_modified": False,
        "primary_rows_with_observations": len(primary_obs),
        "effective_primary_rows": len(effective_primary),
        "primary_conflicted_rows": len(primary_conflicts),
        "primary_defer_markers_suppressed_by_concrete": primary_defer_suppressed_by_concrete,
        "initial_external_rows": len(external_ids),
        "resolved_external_rows": len(resolved),
        "remaining_external_rows": len(remaining),
        "conflicted_external_rows": len(external_conflicts),
        "duplicate_same_decision_rows": duplicate_same_decision_rows,
        "superseded_external_rows": superseded_external_rows,
        "resolved_verdict_counts": dict(sorted(by_verdict.items())),
        "resolved_by_category": dict(sorted(by_cat_resolved.items())),
        "remaining_by_category": dict(sorted(by_cat_remaining.items())),
        "top_remaining": remaining[:30],
        "primary_conflicts": primary_conflicts,
        "conflicts": external_conflicts,
        "next_step": "resolve only effective NEEDS_EXTERNAL_CHECK rows from EXTERNAL_QUEUE_LIVE.csv; keep production read-only until external closure",
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not primary_conflicts and not external_conflicts else 2


if __name__ == "__main__":
    raise SystemExit(main())
