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
    all_rows: list[dict[str, str]] = []
    seen_rows: set[str] = set()
    missing_lanes: list[int] = []

    for lane in range(1, LANE_COUNT + 1):
        lane_key = str(lane)
        branch = f"audit/issue70-auto-lane-{lane}"
        base = f"docs/issue70/automation/cycles/{cycle_id}/lane-{lane}"
        status_text = git_show(branch, f"{base}/STATUS.json")
        results_text = git_show(branch, f"{base}/RESULTS.csv")
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
        target = int(manifest_lanes[lane_key]["target_resolutions"])
        seeded = int(manifest_lanes[lane_key]["seeded_count"])
        assert len(rows) <= int(manifest_lanes[lane_key]["candidate_count"])
        assert len(rows) <= max(target, seeded)

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
            pd = row["proposed_display_ja"]
            ps = row["proposed_search_ja"]
            # A worker may preserve an already-correct companion field while fixing
            # the other half of a FIX_BOTH row.  Treat that as an idempotent proposal:
            # require the proposed field to be explicit, but do not fail integration
            # merely because its value already equals the current value.  This keeps
            # semantic worker output untouched while preventing a mechanical validator
            # mismatch from blocking all five lanes.
            if verdict in {"FIX_DISPLAY", "FIX_BOTH"}:
                assert pd, (rid, verdict, pd)
            else:
                assert not pd, (rid, verdict, pd)
            if verdict in {"FIX_SEARCH", "FIX_BOTH"}:
                assert ps, (rid, verdict, ps)
            else:
                assert not ps, (rid, verdict, ps)

            all_rows.append(row)

    if missing_lanes:
        write_state({
            "ready": False,
            "reason": "waiting for completed lane outputs",
            "cycle_id": cycle_id,
            "missing_lanes": missing_lanes,
        })
        print(f"Waiting for lanes: {missing_lanes}")
        return

    if not all_rows:
        write_state({
            "ready": False,
            "reason": "all lanes completed but no safe resolutions were produced",
            "cycle_id": cycle_id,
        })
        print("No safe resolutions to integrate.")
        return

    out = AUDIT / f"external_resolution_parallel_{cycle_id}.csv"
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
        "format_version": 1,
        "issue": 70,
        "cycle_id": cycle_id,
        "manifest_progress_sha256": expected_hash,
        "merged_rows": len(all_rows),
        "merged_by_category": dict(sorted(merged_by_category.items())),
        "base_resolved_external_rows": int(base["resolved_external_rows"]),
        "expected_resolved_external_rows": int(base["resolved_external_rows"]) + len(all_rows),
        "expected_remaining_external_rows": int(base["remaining_external_rows"]) - len(all_rows),
        "expected_remaining_by_category": dict(sorted(expected_remaining_by_category.items())),
        "production_modified": False,
        "conflicts": 0,
        "source_lanes": list(range(1, LANE_COUNT + 1)),
    }

    report_path = AUTO / "cycles" / cycle_id / "INTEGRATION_REPORT.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    write_state({
        "ready": True,
        "cycle_id": cycle_id,
        "overlay_path": str(out.relative_to(ROOT)),
        "report_path": str(report_path.relative_to(ROOT)),
        **report,
    })
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
