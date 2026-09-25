#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
from pathlib import Path

from parallel_overlay import load_checkpoint_union
from staging_repair_overlay import resolve_repair_overlay
from staging_v2 import (
    SCHEMA_V2,
    compact_row_to_full,
    validate_compact_hold,
    validate_identity_binding,
)

ROOT = Path(__file__).resolve().parents[2]
LANES = (1, 2, 3)
LANE_LENGTHS = {1: 10335, 2: 10334, 3: 10334}
STAGE_RE = re.compile(r"^window_(\\d{6})_(\\d{6})\\.json$")
REQUEST_RE = re.compile(r"^request_(\\d{6})_(\\d{6})\\.json$")
DEFERRED_RE = re.compile(r"^deferred_(\\d{6})_(\\d{6})\\.json$")
SCHEMA_V1 = "issue132-pass-a-staging-window-v1"
EXPECTED_PARENT_SHA = "ac0f888d02f19a440c63b3b9f695c58f9ba53b98ebe9756edec51db1c5ff8f7d"
EXPECTED_ORDER_SHA = "f80c63018ce19a8c7c5d8d6fd83d03cf760c510d8f6cfa455d1ab356fb31361b"
MAX_FORWARD_WINDOW = 100


def load_base():
    p = ROOT / "scripts/issue132/validate_luna_pass_a.py"
    spec = importlib.util.spec_from_file_location("issue132_flat_base", p)
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load base validator")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def normalize_v1_row(entry, fields):
    if isinstance(entry, dict):
        if set(entry) != set(fields):
            return None, "finalized row field-set mismatch"
        return {field: str(entry[field]) for field in fields}, None
    if isinstance(entry, list):
        if len(entry) != len(fields):
            return None, f"ordered finalized row must have exactly {len(fields)} fields"
        return {field: str(value) for field, value in zip(fields, entry)}, None
    return None, "finalized row must be an object or ordered field array"


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


def validate_window(path: Path, lane: int, start: int, end: int, assigned, base):
    errors: list[str] = []
    width = end - start + 1
    if width < 1 or width > MAX_FORWARD_WINDOW:
        errors.append(f"range size {width} outside 1..{MAX_FORWARD_WINDOW}")
        return {"errors": errors, "holds": 0, "accepted_indices": set(), "repair_overlay": None}

    repair_obj, repair_name, repair_errors = resolve_repair_overlay(path, lane, start, end)
    errors.extend(repair_errors)
    if repair_errors:
        return {"errors": errors, "holds": 0, "accepted_indices": set(), "repair_overlay": repair_name}

    if repair_obj is not None:
        obj = repair_obj
    else:
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid JSON: {exc}")
            return {"errors": errors, "holds": 0, "accepted_indices": set(), "repair_overlay": repair_name}

    schema = obj.get("schema_version")
    if schema not in {SCHEMA_V1, SCHEMA_V2}:
        errors.append("schema mismatch")
    if obj.get("lane") != lane:
        errors.append("lane mismatch")
    if obj.get("lane_local_start") != start or obj.get("lane_local_end") != end:
        errors.append("range metadata mismatch")
    if obj.get("parent_neutral_sha256") != EXPECTED_PARENT_SHA:
        errors.append("parent neutral SHA mismatch")
    if obj.get("parent_identity_order_sha256") != EXPECTED_ORDER_SHA:
        errors.append("parent identity-order SHA mismatch")

    rows = obj.get("rows", [])
    holds = obj.get("holds", [])
    if not isinstance(rows, list) or not isinstance(holds, list):
        errors.append("rows/holds must be lists")
        return {"errors": errors, "holds": 0, "accepted_indices": set(), "repair_overlay": repair_name}

    covered: dict[int, str] = {}

    if schema == SCHEMA_V1:
        for raw in rows:
            row, err = normalize_v1_row(raw, base.FIELDS)
            if err:
                errors.append(err)
                continue
            try:
                seq = int(row["review_seq"])
            except Exception:
                errors.append("invalid finalized review_seq")
                continue
            ident = row.get("identity_key", "")
            matches = [
                idx for idx in range(start, end + 1)
                if int(assigned[idx - 1]["review_seq"]) == seq
                and assigned[idx - 1]["identity_key"] == ident
            ]
            if len(matches) != 1:
                errors.append(f"finalized row {ident} not exact window identity")
                continue
            idx = matches[0]
            if idx in covered:
                errors.append(f"duplicate local index {idx}")
                continue
            covered[idx] = "row"
            for err2 in base.validate_row(row, seq):
                errors.append(f"local {idx} review_seq {seq}: {err2}")

        for hold in holds:
            if not isinstance(hold, dict):
                errors.append("non-object hold")
                continue
            required = {"lane_local_index", "review_seq", "identity_key", "reason", "research_attempts"}
            if not required.issubset(hold):
                errors.append("legacy hold missing required fields")
                continue
            try:
                idx = int(hold["lane_local_index"])
                seq = int(hold["review_seq"])
            except Exception:
                errors.append("invalid legacy hold indices")
                continue
            if idx < start or idx > end:
                errors.append(f"legacy hold local index {idx} outside range")
                continue
            expected = assigned[idx - 1]
            if int(expected["review_seq"]) != seq or expected["identity_key"] != hold["identity_key"]:
                errors.append(f"legacy hold identity mismatch at local {idx}")
            if idx in covered:
                errors.append(f"duplicate row/hold at local {idx}")
            covered[idx] = "hold"
            if not str(hold.get("reason", "")).strip():
                errors.append(f"legacy hold blank reason at local {idx}")
            attempts = hold.get("research_attempts")
            if not isinstance(attempts, list) or not attempts:
                errors.append(f"legacy hold missing research attempts at local {idx}")

    elif schema == SCHEMA_V2:
        for raw in rows:
            if not isinstance(raw, dict):
                errors.append("compact finalized row must be object")
                continue
            try:
                idx = int(raw.get("lane_local_index"))
            except Exception:
                errors.append("compact row invalid lane_local_index")
                continue
            if idx < start or idx > end:
                errors.append(f"compact row local index {idx} outside range")
                continue
            expected = assigned[idx - 1]
            bind_errors = validate_identity_binding(raw, expected, idx)
            errors.extend(f"local {idx}: {err}" for err in bind_errors)
            if bind_errors:
                continue
            if idx in covered:
                errors.append(f"duplicate local index {idx}")
                continue
            try:
                full = compact_row_to_full(raw, expected, base.FIELDS)
            except Exception as exc:
                errors.append(f"local {idx}: {exc}")
                continue
            covered[idx] = "row"
            seq = int(expected["review_seq"])
            for err2 in base.validate_row(full, seq):
                errors.append(f"local {idx} review_seq {seq}: {err2}")

        for hold in holds:
            if not isinstance(hold, dict):
                errors.append("compact hold must be object")
                continue
            try:
                idx = int(hold.get("lane_local_index"))
            except Exception:
                errors.append("compact hold invalid lane_local_index")
                continue
            if idx < start or idx > end:
                errors.append(f"compact hold local index {idx} outside range")
                continue
            expected = assigned[idx - 1]
            hold_errors = validate_compact_hold(hold, expected, idx)
            errors.extend(f"hold local {idx}: {err}" for err in hold_errors)
            if idx in covered:
                errors.append(f"duplicate row/hold at local {idx}")
            covered[idx] = "hold"

    expected_indices = set(range(start, end + 1))
    if set(covered) != expected_indices:
        missing = sorted(expected_indices - set(covered))
        extra = sorted(set(covered) - expected_indices)
        errors.append(f"coverage mismatch missing={missing} extra={extra}")

    hold_count = len(holds)
    accepted = expected_indices if not errors and hold_count == 0 and len(rows) == width else set()
    return {
        "errors": errors,
        "holds": hold_count,
        "accepted_indices": accepted,
        "repair_overlay": repair_name,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--parallel-dir", default="docs/issue132/parallel")
    args = ap.parse_args()

    base = load_base()
    neutral = read_csv(Path(args.input))
    if len(neutral) != 31003:
        raise SystemExit(f"fatal neutral identity count {len(neutral)} != 31003")

    lanes_summary = {}
    fatal_errors: list[str] = []
    accepted_total = 0
    invalid_total = 0
    hold_total = 0
    missing_total = 0
    duplicate_total = 0

    for lane in LANES:
        assigned = [r for r in neutral if ((int(r["review_seq"]) - 1) % 3) + 1 == lane]
        if len(assigned) != LANE_LENGTHS[lane]:
            fatal_errors.append(f"lane {lane}: neutral lane length {len(assigned)} != {LANE_LENGTHS[lane]}")

        raw, _, checkpoint_errors = load_checkpoint_union(ROOT, lane, base.FIELDS)
        fatal_errors.extend(checkpoint_errors)
        prefix = len(raw)
        accepted = set(range(1, prefix + 1))
        persisted = set()
        seen_post_prefix: set[int] = set()
        invalid_windows = []
        hold_windows = []
        valid_windows = []
        pending_materialization = []
        deferred_ranges = []
        requested_indices: set[int] = set()
        deferred_indices: set[int] = set()

        stage_dir = ROOT / args.parallel_dir / f"lane-{lane}" / "staging"
        if stage_dir.exists():
            for path in sorted(stage_dir.glob("window_*.json")):
                m = STAGE_RE.match(path.name)
                if not m:
                    fatal_errors.append(f"lane {lane}: invalid staging filename {path.name}")
                    continue
                start, end = map(int, m.groups())
                if start < 1 or end > len(assigned) or end < start:
                    invalid_windows.append({"path": path.name, "errors": ["range outside assigned lane"]})
                    continue

                if end <= prefix:
                    # Historical duplicate of already accepted checkpoint seed.
                    continue
                if start <= prefix:
                    invalid_windows.append({"path": path.name, "errors": ["range overlaps checkpoint seed boundary"]})
                    continue

                indices = set(range(start, end + 1))
                dup = indices & seen_post_prefix
                if dup:
                    duplicate_total += len(dup)
                    invalid_windows.append({"path": path.name, "errors": [f"overlaps other forward output at {min(dup)}..{max(dup)}"]})
                    continue
                seen_post_prefix |= indices
                persisted |= indices

                result = validate_window(path, lane, start, end, assigned, base)
                item = {
                    "path": path.name,
                    "start": start,
                    "end": end,
                    "repair_overlay": result["repair_overlay"],
                }
                if result["errors"]:
                    item["errors"] = result["errors"][:20]
                    invalid_windows.append(item)
                elif result["holds"]:
                    item["holds"] = result["holds"]
                    hold_windows.append(item)
                else:
                    accepted |= result["accepted_indices"]
                    valid_windows.append(item)

        request_dir = ROOT / args.parallel_dir / f"lane-{lane}" / "write-requests"
        if request_dir.exists():
            for path in sorted(request_dir.glob("request_*.json")):
                m = REQUEST_RE.match(path.name)
                if not m:
                    fatal_errors.append(f"lane {lane}: invalid write-request filename {path.name}")
                    continue
                start, end = map(int, m.groups())
                if start < 1 or end > len(assigned) or end < start:
                    fatal_errors.append(f"lane {lane}: write-request {path.name} outside assigned lane")
                    continue
                requested_indices |= set(range(start, end + 1))
                stage_path = stage_dir / f"window_{start:06d}_{end:06d}.json"
                if not stage_path.exists():
                    pending_materialization.append({
                        "path": path.name,
                        "start": start,
                        "end": end,
                    })

        deferred_dir = ROOT / args.parallel_dir / f"lane-{lane}" / "deferred"
        if deferred_dir.exists():
            for path in sorted(deferred_dir.glob("deferred_*.json")):
                m = DEFERRED_RE.match(path.name)
                if not m:
                    fatal_errors.append(f"lane {lane}: invalid deferred filename {path.name}")
                    continue
                start, end = map(int, m.groups())
                if start < 1 or end > len(assigned) or end < start:
                    fatal_errors.append(f"lane {lane}: deferred {path.name} outside assigned lane")
                    continue
                deferred_indices |= set(range(start, end + 1))
                deferred_ranges.append({"path": path.name, "start": start, "end": end})

        high_watermark = max(persisted, default=prefix)
        frontier_high_watermark = max(
            [prefix]
            + list(persisted)
            + list(requested_indices)
            + list(deferred_indices)
        )
        gap_indices = set(range(prefix + 1, high_watermark + 1)) - persisted
        missing_ranges = ranges_from_indices(gap_indices)
        missing_total += len(gap_indices)

        accepted_count = len(accepted)
        accepted_total += accepted_count
        invalid_total += len(invalid_windows)
        hold_total += len(hold_windows)

        lanes_summary[str(lane)] = {
            "checkpoint_seed_count": prefix,
            "accepted_count": accepted_count,
            "persisted_high_watermark": high_watermark,
            "frontier_high_watermark": frontier_high_watermark,
            "forward_frontier": frontier_high_watermark + 1 if frontier_high_watermark < len(assigned) else None,
            "pending_materialization": pending_materialization,
            "pending_materialization_count": len(pending_materialization),
            "deferred_ranges": deferred_ranges,
            "deferred_range_count": len(deferred_ranges),
            "remaining_identity_count": len(assigned) - accepted_count,
            "valid_forward_window_count": len(valid_windows),
            "invalid_windows": invalid_windows,
            "hold_windows": hold_windows,
            "missing_written_range_count": len(gap_indices),
            "missing_written_ranges": missing_ranges,
        }

    complete = (
        accepted_total == 31003
        and invalid_total == 0
        and hold_total == 0
        and missing_total == 0
        and duplicate_total == 0
        and not fatal_errors
    )

    snapshot = {
        "schema_version": "issue132-flat-pass-a-snapshot-v1",
        "accepted_total": accepted_total,
        "expected_total": 31003,
        "accepted_by_lane": {lane: lanes_summary[lane]["accepted_count"] for lane in sorted(lanes_summary)},
        "high_watermarks": {lane: lanes_summary[lane]["persisted_high_watermark"] for lane in sorted(lanes_summary)},
        "frontier_high_watermarks": {lane: lanes_summary[lane]["frontier_high_watermark"] for lane in sorted(lanes_summary)},
        "frontiers": {lane: lanes_summary[lane]["forward_frontier"] for lane in sorted(lanes_summary)},
        "pending_materialization_count": sum(lanes_summary[lane]["pending_materialization_count"] for lane in lanes_summary),
        "pending_materialization": {lane: lanes_summary[lane]["pending_materialization"] for lane in sorted(lanes_summary)},
        "deferred_range_count": sum(lanes_summary[lane]["deferred_range_count"] for lane in lanes_summary),
        "deferred_ranges": {lane: lanes_summary[lane]["deferred_ranges"] for lane in sorted(lanes_summary)},
        "invalid_window_count": invalid_total,
        "invalid_windows": {lane: [x["path"] for x in lanes_summary[lane]["invalid_windows"]] for lane in sorted(lanes_summary)},
        "hold_window_count": hold_total,
        "hold_windows": {lane: [x["path"] for x in lanes_summary[lane]["hold_windows"]] for lane in sorted(lanes_summary)},
        "missing_written_range_count": missing_total,
        "missing_written_ranges": {lane: lanes_summary[lane]["missing_written_ranges"] for lane in sorted(lanes_summary)},
        "duplicate_coverage_count": duplicate_total,
        "fatal_contract_error_count": len(fatal_errors),
        "complete": complete,
    }

    print("FLAT_SNAPSHOT_JSON=" + json.dumps(snapshot, ensure_ascii=False, separators=(",", ":")))
    print(json.dumps({
        "snapshot": snapshot,
        "lanes": lanes_summary,
        "fatal_errors": fatal_errors,
    }, ensure_ascii=False, indent=2))

    if fatal_errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
