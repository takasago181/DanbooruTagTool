#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from codex_runtime import (
    direct_start,
    internal_forward_limit,
    last_codex_qa,
    load_baseline_lane,
    load_baseline_manifest,
    load_runtime,
    read_csv,
)
from codex_semantic import validate_compact_hold, validate_compact_row

ROOT = Path(__file__).resolve().parents[2]
WINDOW_RE = re.compile(r"^window_(\d{6})_(\d{6})\.json$")
STAGING_SCHEMA = "issue132-pass-a-staging-window-v2"


def ranges_from_indices(indices: set[int]) -> list[list[int]]:
    if not indices:
        return []
    values = sorted(indices)
    out: list[list[int]] = []
    start = prev = values[0]
    for value in values[1:]:
        if value == prev + 1:
            prev = value
            continue
        out.append([start, prev])
        start = prev = value
    out.append([start, prev])
    return out


def assigned_lane(neutral: list[dict[str, str]], lane: int) -> list[dict[str, str]]:
    return [
        row
        for row in neutral
        if ((int(row["review_seq"]) - 1) % 3) + 1 == lane
    ]


def validate_policy_trace(obj: dict, authority: dict) -> list[str]:
    sem = authority["semantic_contract"]
    pid = obj.get("semantic_policy_id")
    pblob = obj.get("semantic_policy_git_blob_sha")
    allowed = sem.get("allowed_policies", {})
    meta = allowed.get(pid) if isinstance(allowed, dict) else None
    if not meta:
        return ["semantic_policy_id is not registered"]
    if pblob != meta.get("git_blob_sha"):
        return ["semantic_policy_git_blob_sha mismatch"]
    return []

def validate_baseline_lane(
    obj: dict,
    lane: int,
    assigned: list[dict[str, str]],
    manifest_entry: dict,
    contract: dict,
) -> dict:
    fatal: list[str] = []
    lint: list[dict] = []
    hold_errors: list[dict] = []
    rows_valid: set[int] = set()
    rows_invalid: set[int] = set()
    holds_valid: set[int] = set()
    seen: set[int] = set()

    expected_end = int(manifest_entry["lane_local_end"])
    if obj.get("schema_version") != "issue132-codex-baseline-lane-v1":
        fatal.append("baseline lane schema mismatch")
    if obj.get("lane") != lane:
        fatal.append("baseline lane mismatch")
    if obj.get("lane_local_start") != 1 or obj.get("lane_local_end") != expected_end:
        fatal.append("baseline lane range mismatch")

    for row in obj.get("rows", []):
        try:
            idx = int(row.get("lane_local_index"))
        except Exception:
            idx = -1
        if idx < 1 or idx > expected_end or idx in seen:
            fatal.append(f"baseline duplicate/out-of-range row {idx}")
            continue
        seen.add(idx)
        errors = validate_compact_row(row, assigned[idx - 1], idx, contract)
        if errors:
            rows_invalid.add(idx)
            lint.append({
                "lane_local_index": idx,
                "review_seq": int(assigned[idx - 1]["review_seq"]),
                "identity_key": assigned[idx - 1]["identity_key"],
                "errors": errors,
            })
        else:
            rows_valid.add(idx)

    for hold in obj.get("holds", []):
        try:
            idx = int(hold.get("lane_local_index"))
        except Exception:
            idx = -1
        if idx < 1 or idx > expected_end or idx in seen:
            fatal.append(f"baseline duplicate/out-of-range hold {idx}")
            continue
        seen.add(idx)
        errors = validate_compact_hold(hold, assigned[idx - 1], idx)
        if errors:
            hold_errors.append({"lane_local_index": idx, "errors": errors})
        else:
            holds_valid.add(idx)

    expected_slots = set(range(1, expected_end + 1))
    if seen != expected_slots:
        fatal.append(
            f"baseline slot coverage mismatch missing={sorted(expected_slots-seen)[:50]}"
        )
    if hold_errors:
        fatal.extend(
            f"baseline hold {item['lane_local_index']}: {'; '.join(item['errors'])}"
            for item in hold_errors
        )

    return {
        "fatal": fatal,
        "valid_rows": rows_valid,
        "lint_rows": rows_invalid,
        "lint_diagnostics": lint,
        "holds": holds_valid,
        "saved_end": expected_end,
    }


def validate_direct_window(
    path: Path,
    lane: int,
    start: int,
    end: int,
    assigned: list[dict[str, str]],
    authority: dict,
    contract: dict,
) -> dict:
    errors: list[str] = []
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"errors": [f"invalid JSON: {exc}"], "rows": set(), "holds": set()}

    max_width = int(authority["fixed"]["forward_window_max"])
    if end < start or end - start + 1 > max_width:
        errors.append(f"window size outside 1..{max_width}")
    if obj.get("schema_version") != STAGING_SCHEMA:
        errors.append("staging schema mismatch")
    if obj.get("lane") != lane:
        errors.append("lane mismatch")
    if obj.get("lane_local_start") != start or obj.get("lane_local_end") != end:
        errors.append("range metadata mismatch")
    if obj.get("parent_neutral_sha256") != authority["fixed"]["parent_neutral_sha256"]:
        errors.append("parent neutral SHA mismatch")
    if (
        obj.get("parent_identity_order_sha256")
        != authority["fixed"]["parent_identity_order_sha256"]
    ):
        errors.append("parent identity-order SHA mismatch")

    rows = obj.get("rows")
    holds = obj.get("holds")
    if not isinstance(rows, list) or not isinstance(holds, list):
        errors.append("rows/holds must be lists")
        return {"errors": errors, "rows": set(), "holds": set()}

    seen: set[int] = set()
    row_indices: set[int] = set()
    hold_indices: set[int] = set()

    for row in rows:
        try:
            idx = int(row.get("lane_local_index"))
        except Exception:
            idx = -1
        if idx < start or idx > end or idx in seen:
            errors.append(f"duplicate/out-of-range row {idx}")
            continue
        seen.add(idx)
        row_indices.add(idx)
        errors.extend(
            f"local {idx}: {err}"
            for err in validate_compact_row(row, assigned[idx - 1], idx, contract)
        )

    for hold in holds:
        try:
            idx = int(hold.get("lane_local_index"))
        except Exception:
            idx = -1
        if idx < start or idx > end or idx in seen:
            errors.append(f"duplicate/out-of-range hold {idx}")
            continue
        seen.add(idx)
        hold_indices.add(idx)
        errors.extend(
            f"hold local {idx}: {err}"
            for err in validate_compact_hold(hold, assigned[idx - 1], idx)
        )

    expected = set(range(start, end + 1))
    if seen != expected:
        errors.append(
            f"coverage mismatch missing={sorted(expected-seen)} "
            f"extra={sorted(seen-expected)}"
        )

    errors.extend(validate_policy_trace(obj, authority))
    return {"errors": errors, "rows": row_indices, "holds": hold_indices}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input",
        default="docs/issue132/parallel/input/luna_neutral_review_input_v2.csv",
    )
    args = ap.parse_args()

    authority, contract, qa, runtime_errors = load_runtime(ROOT)
    fatal_errors = list(runtime_errors)
    neutral = read_csv(ROOT / args.input)
    baseline_manifest = load_baseline_manifest(ROOT, authority)

    accepted_total = 0
    processed_total = 0
    baseline_hold_total = 0
    baseline_lint_total = 0
    forward_hold_total = 0
    invalid_window_total = 0
    duplicate_total = 0
    internal_qa_violation_total = 0
    lanes: dict[str, dict] = {}

    for lane in (1, 2, 3):
        assigned = assigned_lane(neutral, lane)
        lane_length = int(authority["fixed"]["lane_lengths"][str(lane)])
        if len(assigned) != lane_length:
            fatal_errors.append(
                f"lane {lane}: neutral lane length {len(assigned)} != {lane_length}"
            )

        manifest_entry = baseline_manifest["lanes"][str(lane)]
        baseline_obj = load_baseline_lane(ROOT, baseline_manifest, lane)
        baseline = validate_baseline_lane(
            baseline_obj, lane, assigned, manifest_entry, contract
        )
        fatal_errors.extend(
            f"lane {lane}: {error}" for error in baseline["fatal"]
        )

        baseline_valid_rows = set(baseline["valid_rows"])
        baseline_lint_rows = set(baseline["lint_rows"])
        baseline_holds = set(baseline["holds"])
        saved_end = int(baseline["saved_end"])

        accepted_total += len(baseline_valid_rows)
        processed_total += saved_end
        baseline_hold_total += len(baseline_holds)
        baseline_lint_total += len(baseline_lint_rows)

        boundary = direct_start(authority, lane)
        if boundary != saved_end + 1:
            fatal_errors.append(
                f"lane {lane}: direct boundary {boundary} != baseline end+1 {saved_end+1}"
            )

        direct_seen: set[int] = set()
        direct_valid_rows: set[int] = set()
        direct_holds: set[int] = set()
        invalid_windows: list[dict] = []
        valid_windows: list[dict] = []
        internal_qa_violations: set[int] = set()

        stage_dir = ROOT / f"docs/issue132/parallel/lane-{lane}/staging"
        if stage_dir.exists():
            for path in sorted(stage_dir.glob("window_*.json")):
                match = WINDOW_RE.match(path.name)
                if not match:
                    continue
                start, end = map(int, match.groups())

                if end < boundary:
                    continue
                if start < boundary <= end:
                    invalid_windows.append({
                        "path": path.name,
                        "start": start,
                        "end": end,
                        "errors": ["window crosses frozen baseline boundary"],
                    })
                    continue
                if start < boundary:
                    continue
                if end > lane_length:
                    invalid_windows.append({
                        "path": path.name,
                        "start": start,
                        "end": end,
                        "errors": ["range exceeds lane length"],
                    })
                    continue

                indices = set(range(start, end + 1))
                overlap = indices & direct_seen
                if overlap:
                    duplicate_total += len(overlap)
                    invalid_windows.append({
                        "path": path.name,
                        "start": start,
                        "end": end,
                        "errors": [
                            f"overlaps direct window coverage {min(overlap)}..{max(overlap)}"
                        ],
                    })
                    continue

                result = validate_direct_window(
                    path, lane, start, end, assigned, authority, contract
                )
                if result["errors"]:
                    invalid_windows.append({
                        "path": path.name,
                        "start": start,
                        "end": end,
                        "errors": result["errors"][:30],
                    })
                    continue

                direct_seen |= indices
                direct_valid_rows |= result["rows"]
                direct_holds |= result["holds"]
                valid_windows.append({"path": path.name, "start": start, "end": end})

                internal_limit = internal_forward_limit(authority, qa, lane)
                internal_qa_violations |= {
                    idx for idx in indices if idx > internal_limit
                }

        # Direct work must be contiguous from the frozen boundary.
        if direct_seen:
            max_direct = max(direct_seen)
            gap = set(range(boundary, max_direct + 1)) - direct_seen
        else:
            gap = set()

        if gap:
            fatal_errors.append(
                f"lane {lane}: direct staging gap ranges={ranges_from_indices(gap)}"
            )

        processed_total += len(direct_seen)
        accepted_total += len(direct_valid_rows)
        forward_hold_total += len(direct_holds)
        invalid_window_total += len(invalid_windows)
        internal_qa_violation_total += len(internal_qa_violations)

        frontier = boundary
        while frontier <= lane_length and frontier in direct_seen:
            frontier += 1
        if frontier > lane_length:
            frontier = None

        remaining_unprocessed = lane_length - saved_end - len(direct_seen)

        lanes[str(lane)] = {
            "baseline_saved_end": saved_end,
            "baseline_valid_row_count": len(baseline_valid_rows),
            "baseline_hold_count": len(baseline_holds),
            "baseline_hold_indices": sorted(baseline_holds),
            "baseline_semantic_lint_count": len(baseline_lint_rows),
            "baseline_semantic_lint_diagnostics": baseline["lint_diagnostics"],
            "direct_valid_window_count": len(valid_windows),
            "direct_valid_row_count": len(direct_valid_rows),
            "direct_hold_count": len(direct_holds),
            "direct_hold_indices": sorted(direct_holds),
            "invalid_windows": invalid_windows,
            "forward_frontier": frontier,
            "last_codex_qa": last_codex_qa(qa, lane),
            "internal_forward_limit": internal_forward_limit(authority, qa, lane),
            "internal_qa_limit_violation_count": len(internal_qa_violations),
            "remaining_unprocessed_count": remaining_unprocessed,
        }

    unresolved_debt_total = (
        baseline_hold_total
        + baseline_lint_total
        + forward_hold_total
        + invalid_window_total
    )
    final_internal_qa = bool(qa.get("final_internal_qa_passed", False))
    final_chatgpt_qa = bool(qa.get("final_chatgpt_semantic_qa_passed", False))
    internal_qa_caught_up = all(
        last_codex_qa(qa, lane)
        >= int(authority["fixed"]["lane_lengths"][str(lane)])
        for lane in (1, 2, 3)
    )
    ready_for_final_chatgpt_audit = (
        processed_total == 31003
        and accepted_total == 31003
        and unresolved_debt_total == 0
        and duplicate_total == 0
        and internal_qa_violation_total == 0
        and internal_qa_caught_up
        and not fatal_errors
        and final_internal_qa
    )
    complete = (
        processed_total == 31003
        and accepted_total == 31003
        and unresolved_debt_total == 0
        and duplicate_total == 0
        and internal_qa_violation_total == 0
        and internal_qa_caught_up
        and not fatal_errors
        and final_internal_qa
        and final_chatgpt_qa
    )

    snapshot = {
        "schema_version": "issue132-flat-pass-a-snapshot-v4-codex-autonomous",
        "processed_slot_total": processed_total,
        "accepted_total": accepted_total,
        "expected_total": 31003,
        "remaining_unprocessed_total": 31003 - processed_total,
        "baseline_hold_count": baseline_hold_total,
        "baseline_semantic_lint_count": baseline_lint_total,
        "forward_hold_count": forward_hold_total,
        "invalid_window_count": invalid_window_total,
        "duplicate_coverage_count": duplicate_total,
        "internal_qa_limit_violation_count": internal_qa_violation_total,
        "fatal_contract_error_count": len(fatal_errors),
        "frontiers": {lane: lanes[lane]["forward_frontier"] for lane in sorted(lanes)},
        "last_codex_qa_by_lane": {
            str(lane): last_codex_qa(qa, lane) for lane in (1, 2, 3)
        },
        "internal_qa_caught_up": internal_qa_caught_up,
        "final_internal_qa_passed": final_internal_qa,
        "final_chatgpt_semantic_qa_passed": final_chatgpt_qa,
        "ready_for_final_chatgpt_audit": ready_for_final_chatgpt_audit,
        "complete": complete,
    }

    print(
        "FLAT_SNAPSHOT_JSON="
        + json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"))
    )
    print(json.dumps(
        {"snapshot": snapshot, "lanes": lanes, "fatal_errors": fatal_errors},
        ensure_ascii=False,
        indent=2,
    ))

    if fatal_errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
