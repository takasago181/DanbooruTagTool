#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "docs/issue70/audit"
AUTO = ROOT / "docs/issue70/automation"
CURRENT = AUTO / "CURRENT_MANIFEST.json"
REVIEWED = AUTO / "REVIEWED_UNRESOLVED.csv"
SCOPE_SKIPPED = AUTO / "SCOPE_SKIPPED_NON_2D.csv"
STATE = ROOT / "artifacts/issue70-parallel/integrator_state.json"

FINAL = {"KEEP", "FIX_DISPLAY", "FIX_SEARCH", "FIX_BOTH"}
LANE_COUNT = 5

RESULT_FIELDS = [
    "cycle_id", "lane", "manifest_progress_sha256", "row_id", "canonical_tag", "category",
    "post_count", "display_ja", "search_ja", "prior_audit_verdict", "audit_verdict",
    "proposed_display_ja", "proposed_search_ja", "reason_code", "confidence",
    "evidence_refs", "audit_note", "approval_status",
]

OVERLAY_FIELDS = [
    "row_id", "canonical_tag", "post_count", "display_ja", "search_ja",
    "prior_audit_verdict", "audit_verdict", "proposed_display_ja", "proposed_search_ja",
    "reason_code", "confidence", "evidence_refs", "audit_note", "approval_status",
]

REVIEW_FIELDS = [
    "cycle_id", "lane", "manifest_progress_sha256", "row_id", "canonical_tag", "category",
    "post_count", "review_status", "review_reason", "evidence_refs", "audit_note",
]

REGISTRY_FIELDS = [
    "row_id", "canonical_tag", "category", "post_count", "first_review_cycle",
    "last_review_cycle", "review_count", "last_lane", "review_reason", "evidence_refs", "audit_note",
]

SCOPE_FIELDS = [
    "cycle_id", "lane", "manifest_progress_sha256", "row_id", "canonical_tag", "category",
    "post_count", "media_scope", "scope_reason", "evidence_refs", "audit_note",
]

SCOPE_REGISTRY_FIELDS = [
    "row_id", "canonical_tag", "category", "post_count", "media_scope",
    "first_skip_cycle", "last_skip_cycle", "skip_count", "last_lane",
    "scope_reason", "evidence_refs", "audit_note",
]


def progress_hash() -> str:
    return hashlib.sha256((AUDIT / "EXTERNAL_PROGRESS_LIVE.json").read_bytes()).hexdigest()


def git_show(branch: str, path: str) -> str | None:
    proc = subprocess.run(
        ["git", "show", f"origin/{branch}:{path}"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    return proc.stdout if proc.returncode == 0 else None


def write_state(data: dict[str, object]) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    manifest = json.loads(CURRENT.read_text(encoding="utf-8"))
    cycle_id = manifest["cycle_id"]
    expected_hash = manifest["progress_sha256"]
    current_hash = progress_hash()

    if current_hash != expected_hash:
        write_state({
            "ready": False,
            "reason": "authority progress changed; current manifest is stale",
            "cycle_id": cycle_id,
            "expected_progress_sha256": expected_hash,
            "current_progress_sha256": current_hash,
        })
        print("Current manifest is stale; no integration performed.")
        return

    manifest_lanes = manifest["lanes"]

    # Readiness preflight: partial/checkpoint pushes from lane 1 are normal.
    # If any lane is absent or incomplete, wait successfully BEFORE parsing
    # semantic artifacts from any completed lane. This prevents harmless
    # intermediate pushes from surfacing validation failures before the cycle
    # is actually ready to integrate.
    preflight_missing: list[int] = []
    for lane in range(1, LANE_COUNT + 1):
        branch = f"audit/issue70-auto-lane-{lane}"
        base = f"docs/issue70/automation/cycles/{cycle_id}/lane-{lane}"
        status_text = git_show(branch, f"{base}/STATUS.json")
        if status_text is None:
            preflight_missing.append(lane)
            continue
        try:
            status = json.loads(status_text)
        except Exception:
            preflight_missing.append(lane)
            continue
        if status.get("complete") is not True:
            preflight_missing.append(lane)

    if preflight_missing:
        write_state({
            "ready": False,
            "reason": "waiting for completed lane outputs",
            "cycle_id": cycle_id,
            "missing_lanes": preflight_missing,
        })
        print(f"Waiting for lanes: {preflight_missing}")
        return

    all_rows: list[dict[str, str]] = []
    all_reviewed: list[dict[str, str]] = []
    auto_normalized_rows = 0
    all_scope_skipped: list[dict[str, str]] = []
    seen_rows: set[str] = set()
    seen_reviewed: set[str] = set()
    seen_scope_skipped: set[str] = set()
    missing_lanes: list[int] = []

    for lane in range(1, LANE_COUNT + 1):
        lane_key = str(lane)
        branch = f"audit/issue70-auto-lane-{lane}"
        base = f"docs/issue70/automation/cycles/{cycle_id}/lane-{lane}"
        status_text = git_show(branch, f"{base}/STATUS.json")
        results_text = git_show(branch, f"{base}/RESULTS.csv")
        reviewed_text = git_show(branch, f"{base}/REVIEWED_UNRESOLVED.csv")
        scope_text = git_show(branch, f"{base}/SCOPE_SKIPPED.csv")
        if status_text is None or results_text is None:
            missing_lanes.append(lane)
            continue

        status = json.loads(status_text)
        if status.get("complete") is not True:
            missing_lanes.append(lane)
            continue
        assert status.get("issue") == 70
        assert status.get("cycle_id") == cycle_id
        assert int(status.get("lane")) == lane
        assert status.get("manifest_progress_sha256") == expected_hash

        rows = list(csv.DictReader(io.StringIO(results_text.lstrip("\ufeff"))))
        assert int(status.get("resolved_count", -1)) == len(rows)

        assigned = {r["row_id"]: r for r in manifest_lanes[lane_key]["candidates"]}
        assert len(rows) <= int(manifest_lanes[lane_key]["candidate_count"])

        for row in rows:
            assert set(RESULT_FIELDS) <= set(row), (lane, sorted(row))
            rid = row["row_id"].strip()
            assert rid in assigned, (lane, rid, "row not assigned to lane")
            assert rid not in seen_rows, (lane, rid, "duplicate across lanes")
            seen_rows.add(rid)

            source = assigned[rid]
            assert row["cycle_id"] == cycle_id
            assert int(row["lane"]) == lane
            assert row["manifest_progress_sha256"] == expected_hash
            assert row["canonical_tag"] == source["canonical_tag"]
            assert row["category"] == source["category"]
            assert int(row["post_count"] or 0) == int(source["post_count"])
            assert row["display_ja"] == source["display_ja"]
            assert row["search_ja"] == source["search_ja"]
            assert row["prior_audit_verdict"] == "NEEDS_EXTERNAL_CHECK"
            assert row["audit_verdict"] in FINAL
            assert row["confidence"] == "HIGH"
            assert row["approval_status"] == "PROPOSED"
            assert row["evidence_refs"].startswith("http")

            verdict = row["audit_verdict"]
            pd = row["proposed_display_ja"].strip()
            ps = row["proposed_search_ja"].strip()
            current_display = row["display_ja"]
            current_search = row["search_ja"]

            # Mechanical self-heal only: workers sometimes echo the current value
            # into a proposal field.  That carries no semantic change, so clear it
            # rather than failing the entire cycle.  Any genuinely different
            # proposal/verdict mismatch still fails below.
            normalized = False
            if verdict in {"KEEP", "FIX_SEARCH"} and pd == current_display and pd:
                row["proposed_display_ja"] = ""
                pd = ""
                normalized = True
            if verdict in {"KEEP", "FIX_DISPLAY"} and ps == current_search and ps:
                row["proposed_search_ja"] = ""
                ps = ""
                normalized = True
            if normalized:
                auto_normalized_rows += 1

            if verdict == "KEEP":
                assert not pd and not ps, (rid, verdict, pd, ps)
            elif verdict == "FIX_DISPLAY":
                assert pd and pd != current_display, (rid, verdict, pd, current_display)
                assert not ps, (rid, verdict, ps)
            elif verdict == "FIX_SEARCH":
                assert not pd, (rid, verdict, pd)
                assert ps and ps != current_search, (rid, verdict, ps, current_search)
            elif verdict == "FIX_BOTH":
                assert pd and pd != current_display, (rid, verdict, pd, current_display)
                assert ps and ps != current_search, (rid, verdict, ps, current_search)

            all_rows.append(row)

        if scope_text is not None:
            scope_rows = list(csv.DictReader(io.StringIO(scope_text.lstrip("\ufeff"))))
            for row in scope_rows:
                assert set(SCOPE_FIELDS) <= set(row), (lane, "scope_schema", sorted(row))
                rid = row["row_id"].strip()
                assert rid in assigned, (lane, rid, "scope-skipped row not assigned to lane")
                assert rid not in seen_rows, (lane, rid, "row cannot be both resolved and scope-skipped")
                assert rid not in seen_scope_skipped, (lane, rid, "duplicate scope-skipped row across lanes")
                seen_scope_skipped.add(rid)

                source = assigned[rid]
                assert row["cycle_id"] == cycle_id
                assert int(row["lane"]) == lane
                assert row["manifest_progress_sha256"] == expected_hash
                assert row["canonical_tag"] == source["canonical_tag"]
                assert row["category"] == source["category"]
                assert row["category"] in {"Character", "Copyright"}
                assert int(row["post_count"] or 0) == int(source["post_count"])
                assert row["media_scope"] == "REAL_3D"
                assert row["scope_reason"].strip()
                assert row["audit_note"].strip()
                all_scope_skipped.append(row)

        if reviewed_text is not None:
            reviewed_rows = list(csv.DictReader(io.StringIO(reviewed_text.lstrip("\ufeff"))))
            for row in reviewed_rows:
                assert set(REVIEW_FIELDS) <= set(row), (lane, "reviewed_schema", sorted(row))
                rid = row["row_id"].strip()
                assert rid in assigned, (lane, rid, "reviewed row not assigned to lane")
                assert rid not in seen_rows, (lane, rid, "row cannot be both resolved and reviewed-unresolved")
                assert rid not in seen_scope_skipped, (lane, rid, "row cannot be both scope-skipped and reviewed-unresolved")
                assert rid not in seen_reviewed, (lane, rid, "duplicate reviewed row across lanes")
                seen_reviewed.add(rid)

                source = assigned[rid]
                assert row["cycle_id"] == cycle_id
                assert int(row["lane"]) == lane
                assert row["manifest_progress_sha256"] == expected_hash
                assert row["canonical_tag"] == source["canonical_tag"]
                assert row["category"] == source["category"]
                assert int(row["post_count"] or 0) == int(source["post_count"])
                assert row["review_status"] == "REVIEWED_UNRESOLVED"
                assert row["review_reason"].strip()
                assert row["audit_note"].strip()
                all_reviewed.append(row)

    if missing_lanes:
        write_state({
            "ready": False,
            "reason": "waiting for completed lane outputs",
            "cycle_id": cycle_id,
            "missing_lanes": missing_lanes,
        })
        print(f"Waiting for lanes: {missing_lanes}")
        return

    existing_registry: dict[str, dict[str, str]] = {}
    if REVIEWED.exists():
        with REVIEWED.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                rid = (row.get("row_id") or "").strip()
                if rid:
                    existing_registry[rid] = row

    resolved_now = {row["row_id"] for row in all_rows}
    scope_now = {row["row_id"] for row in all_scope_skipped}
    for rid in resolved_now | scope_now:
        existing_registry.pop(rid, None)

    for row in all_reviewed:
        rid = row["row_id"]
        prev = existing_registry.get(rid)
        if prev:
            first_cycle = prev.get("first_review_cycle") or cycle_id
            count = int(prev.get("review_count") or 0) + 1
        else:
            first_cycle = cycle_id
            count = 1
        existing_registry[rid] = {
            "row_id": rid,
            "canonical_tag": row["canonical_tag"],
            "category": row["category"],
            "post_count": row["post_count"],
            "first_review_cycle": first_cycle,
            "last_review_cycle": cycle_id,
            "review_count": str(count),
            "last_lane": row["lane"],
            "review_reason": row["review_reason"],
            "evidence_refs": row["evidence_refs"],
            "audit_note": row["audit_note"],
        }

    REVIEWED.parent.mkdir(parents=True, exist_ok=True)
    with REVIEWED.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=REGISTRY_FIELDS)
        writer.writeheader()
        writer.writerows(sorted(
            existing_registry.values(),
            key=lambda r: (r["category"], -int(r["post_count"] or 0), r["row_id"]),
        ))

    scope_registry: dict[str, dict[str, str]] = {}
    if SCOPE_SKIPPED.exists():
        with SCOPE_SKIPPED.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                rid = (row.get("row_id") or "").strip()
                if rid:
                    scope_registry[rid] = row

    for row in all_scope_skipped:
        rid = row["row_id"]
        prev = scope_registry.get(rid)
        if prev:
            first_cycle = prev.get("first_skip_cycle") or cycle_id
            count = int(prev.get("skip_count") or 0) + 1
        else:
            first_cycle = cycle_id
            count = 1
        scope_registry[rid] = {
            "row_id": rid,
            "canonical_tag": row["canonical_tag"],
            "category": row["category"],
            "post_count": row["post_count"],
            "media_scope": "REAL_3D",
            "first_skip_cycle": first_cycle,
            "last_skip_cycle": cycle_id,
            "skip_count": str(count),
            "last_lane": row["lane"],
            "scope_reason": row["scope_reason"],
            "evidence_refs": row["evidence_refs"],
            "audit_note": row["audit_note"],
        }

    SCOPE_SKIPPED.parent.mkdir(parents=True, exist_ok=True)
    with SCOPE_SKIPPED.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SCOPE_REGISTRY_FIELDS)
        writer.writeheader()
        writer.writerows(sorted(
            scope_registry.values(),
            key=lambda r: (r["category"], -int(r["post_count"] or 0), r["row_id"]),
        ))

    out = AUDIT / f"external_resolution_parallel_{cycle_id}.csv"
    if all_rows:
        assert not out.exists(), f"overlay already exists: {out}"
        with out.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=OVERLAY_FIELDS)
            writer.writeheader()
            for row in all_rows:
                writer.writerow({k: row[k] for k in OVERLAY_FIELDS})

    base = manifest["progress_snapshot"]
    merged_by_category = Counter(row["category"] for row in all_rows)
    expected_remaining_by_category = dict(base["remaining_by_category"])
    for category, count in merged_by_category.items():
        expected_remaining_by_category[category] = int(expected_remaining_by_category.get(category, 0)) - count

    report = {
        "format_version": 2,
        "issue": 70,
        "cycle_id": cycle_id,
        "manifest_progress_sha256": expected_hash,
        "merged_rows": len(all_rows),
        "auto_normalized_rows": auto_normalized_rows,
        "merged_by_category": dict(sorted(merged_by_category.items())),
        "reviewed_unresolved_rows_this_cycle": len(all_reviewed),
        "reviewed_unresolved_registry_rows": len(existing_registry),
        "scope_skipped_rows_this_cycle": len(all_scope_skipped),
        "scope_skipped_registry_rows": len(scope_registry),
        "base_resolved_external_rows": int(base["resolved_external_rows"]),
        "expected_resolved_external_rows": int(base["resolved_external_rows"]) + len(all_rows),
        "expected_remaining_external_rows": int(base["remaining_external_rows"]) - len(all_rows),
        "expected_remaining_by_category": dict(sorted(expected_remaining_by_category.items())),
        "production_modified": False,
        "conflicts": 0,
        "lanes": LANE_COUNT,
    }
    report_path = AUTO / "cycles" / cycle_id / "INTEGRATION_REPORT.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    write_state({
        "ready": True,
        "cycle_id": cycle_id,
        "merged_rows": len(all_rows),
        "auto_normalized_rows": auto_normalized_rows,
        "reviewed_unresolved_rows_this_cycle": len(all_reviewed),
        "scope_skipped_rows_this_cycle": len(all_scope_skipped),
        "overlay": str(out.relative_to(ROOT)) if all_rows else None,
        "reviewed_registry": str(REVIEWED.relative_to(ROOT)),
        "scope_skipped_registry": str(SCOPE_SKIPPED.relative_to(ROOT)),
        "integration_report": str(report_path.relative_to(ROOT)),
    })
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
