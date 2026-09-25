#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
from pathlib import Path

from codex_runtime import (
    allowed_forward_end,
    direct_start,
    load_runtime,
    policy_blob,
    policy_id,
    reason_codes,
)
from parallel_overlay import apply_corrections, load_checkpoint_union
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
STAGE_RE = re.compile(r"^window_(\d{6})_(\d{6})\.json$")
SCHEMA_V1 = "issue132-pass-a-staging-window-v1"


def load_base():
    path = ROOT / "scripts/issue132/validate_luna_pass_a.py"
    spec = importlib.util.spec_from_file_location("issue132_flat_base", path)
    if spec is None or spec.loader is None:
        raise SystemExit("cannot load base validator")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


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


def normalize_v1_row(entry, fields):
    if isinstance(entry, dict):
        if set(entry) != set(fields):
            return None, "finalized row field-set mismatch"
        return {field: str(entry[field]) for field in fields}, None
    if isinstance(entry, list):
        if len(entry) != len(fields):
            return None, f"ordered finalized row must have exactly {len(fields)} fields"
        return {field: str(value) for field, value in zip(fields, entry)}, None
    return None, "finalized row must be object or ordered field array"


def validate_policy_trace(
    obj: dict,
    lane: int,
    start: int,
    end: int,
    row_indices: set[int],
    authority: dict,
    contract: dict,
) -> list[str]:
    boundary = direct_start(authority, lane)
    if end < boundary:
        return []
    if start < boundary <= end:
        return [f"window crosses direct-staging boundary {boundary}"]

    errors: list[str] = []
    sem = authority.get("semantic_contract", {})
    pid = obj.get("semantic_policy_id")
    pblob = obj.get("semantic_policy_git_blob_sha")
    allowed = sem.get("allowed_policies", {})
    meta = allowed.get(pid) if isinstance(allowed, dict) else None
    if not meta:
        errors.append("semantic_policy_id not registered")
    elif pblob != meta.get("git_blob_sha"):
        errors.append("semantic_policy_git_blob_sha mismatch")

    reason_map = obj.get("decision_reason_codes")
    if not isinstance(reason_map, dict):
        errors.append("decision_reason_codes must be object")
        return errors
    expected_keys = {str(i) for i in row_indices}
    if set(reason_map) != expected_keys:
        errors.append(
            "decision_reason_codes coverage mismatch "
            f"missing={sorted(expected_keys-set(reason_map))} "
            f"extra={sorted(set(reason_map)-expected_keys)}"
        )
        return errors

    allowed_codes = reason_codes(contract)
    for key, codes in reason_map.items():
        if (
            not isinstance(codes, list)
            or not codes
            or any(not isinstance(x, str) for x in codes)
            or any(x not in allowed_codes for x in codes)
            or len(codes) != len(set(codes))
        ):
            errors.append(f"decision_reason_codes[{key}] invalid")
    return errors


def validate_window(
    path: Path,
    lane: int,
    start: int,
    end: int,
    assigned: list[dict[str, str]],
    base,
    authority: dict,
    contract: dict,
) -> dict:
    errors: list[str] = []
    width = end - start + 1
    max_width = int(authority["fixed"]["forward_window_max"])
    if width < 1 or width > max_width:
        return {
            "errors": [f"range size {width} outside 1..{max_width}"],
            "holds": 0,
            "accepted_indices": set(),
            "repair_overlay": None,
        }

    repair_obj, repair_name, repair_errors = resolve_repair_overlay(path, lane, start, end)
    if repair_errors:
        return {
            "errors": repair_errors,
            "holds": 0,
            "accepted_indices": set(),
            "repair_overlay": repair_name,
        }

    if repair_obj is not None:
        obj = repair_obj
    else:
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            return {
                "errors": [f"invalid JSON: {exc}"],
                "holds": 0,
                "accepted_indices": set(),
                "repair_overlay": repair_name,
            }

    schema = obj.get("schema_version")
    if schema not in {SCHEMA_V1, SCHEMA_V2}:
        errors.append("schema mismatch")
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

    rows = obj.get("rows", [])
    holds = obj.get("holds", [])
    if not isinstance(rows, list) or not isinstance(holds, list):
        return {
            "errors": errors + ["rows/holds must be lists"],
            "holds": 0,
            "accepted_indices": set(),
            "repair_overlay": repair_name,
        }

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
            matches = [
                idx
                for idx in range(start, end + 1)
                if int(assigned[idx - 1]["review_seq"]) == seq
                and assigned[idx - 1]["identity_key"] == row.get("identity_key", "")
            ]
            if len(matches) != 1:
                errors.append("finalized row is not exact window identity")
                continue
            idx = matches[0]
            if idx in covered:
                errors.append(f"duplicate local index {idx}")
                continue
            covered[idx] = "row"
            errors.extend(
                f"local {idx}: {err2}" for err2 in base.validate_row(row, seq)
            )

        for hold in holds:
            if not isinstance(hold, dict):
                errors.append("non-object legacy hold")
                continue
            try:
                idx = int(hold["lane_local_index"])
                seq = int(hold["review_seq"])
            except Exception:
                errors.append("invalid legacy hold indices")
                continue
            if idx < start or idx > end:
                errors.append(f"legacy hold local {idx} outside range")
                continue
            expected = assigned[idx - 1]
            if (
                int(expected["review_seq"]) != seq
                or expected["identity_key"] != hold.get("identity_key")
            ):
                errors.append(f"legacy hold identity mismatch at local {idx}")
            if idx in covered:
                errors.append(f"duplicate row/hold at local {idx}")
            covered[idx] = "hold"

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
                errors.append(f"compact row local {idx} outside range")
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
            errors.extend(
                f"local {idx}: {err2}"
                for err2 in base.validate_row(full, int(expected["review_seq"]))
            )

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
                errors.append(f"compact hold local {idx} outside range")
                continue
            expected = assigned[idx - 1]
            errors.extend(
                f"hold local {idx}: {err}"
                for err in validate_compact_hold(hold, expected, idx)
            )
            if idx in covered:
                errors.append(f"duplicate row/hold at local {idx}")
            covered[idx] = "hold"

    expected_indices = set(range(start, end + 1))
    if set(covered) != expected_indices:
        errors.append(
            f"coverage mismatch missing={sorted(expected_indices-set(covered))} "
            f"extra={sorted(set(covered)-expected_indices)}"
        )

    row_indices = {idx for idx, kind in covered.items() if kind == "row"}
    errors.extend(
        validate_policy_trace(
            obj, lane, start, end, row_indices, authority, contract
        )
    )

    hold_count = len(holds)
    accepted = (
        expected_indices
        if not errors and hold_count == 0 and len(rows) == width
        else set()
    )
    return {
        "errors": errors,
        "holds": hold_count,
        "accepted_indices": accepted,
        "repair_overlay": repair_name,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input",
        default="docs/issue132/parallel/input/luna_neutral_review_input_v2.csv",
    )
    ap.add_argument("--parallel-dir", default="docs/issue132/parallel")
    args = ap.parse_args()

    authority, contract, qa, runtime_errors = load_runtime(ROOT)
    base = load_base()
    neutral = read_csv(ROOT / args.input)
    if len(neutral) != 31003:
        raise SystemExit(f"neutral identity count {len(neutral)} != 31003")

    fatal_errors = list(runtime_errors)
    lanes_summary: dict[str, dict] = {}
    accepted_total = 0
    invalid_total = 0
    hold_total = 0
    duplicate_total = 0
    qa_violation_total = 0

    for lane in LANES:
        assigned = [
            row
            for row in neutral
            if ((int(row["review_seq"]) - 1) % 3) + 1 == lane
        ]
        if len(assigned) != LANE_LENGTHS[lane]:
            fatal_errors.append(
                f"lane {lane}: neutral lane length {len(assigned)} != {LANE_LENGTHS[lane]}"
            )

        raw, checkpoint_ranges, checkpoint_load_errors = load_checkpoint_union(
            ROOT, lane, base.FIELDS
        )
        lane_fatal = list(checkpoint_load_errors)
        effective, correction_count, correction_errors = apply_corrections(
            ROOT, lane, raw, checkpoint_ranges, base.FIELDS
        )
        lane_fatal.extend(correction_errors)

        accepted: set[int] = set()
        for idx, row in enumerate(effective, start=1):
            if idx > len(assigned):
                lane_fatal.append(f"lane {lane}: checkpoint index {idx} exceeds lane")
                continue
            expected = assigned[idx - 1]
            try:
                seq = int(row.get("review_seq", ""))
            except Exception:
                seq = -1
            if (
                seq != int(expected["review_seq"])
                or row.get("identity_key") != expected["identity_key"]
            ):
                lane_fatal.append(
                    f"lane {lane} local {idx}: checkpoint identity binding mismatch"
                )
                continue
            row_errors = base.validate_row(row, seq)
            if row_errors:
                lane_fatal.extend(
                    f"lane {lane} local {idx}: {err}" for err in row_errors
                )
                continue
            accepted.add(idx)

        prefix = len(effective)
        seen_forward: set[int] = set()
        persisted: set[int] = set()
        invalid_windows: list[dict] = []
        hold_windows: list[dict] = []
        valid_windows: list[dict] = []
        qa_violation_indices: set[int] = set()

        stage_dir = ROOT / args.parallel_dir / f"lane-{lane}" / "staging"
        if stage_dir.exists():
            for path in sorted(stage_dir.glob("window_*.json")):
                match = STAGE_RE.match(path.name)
                if not match:
                    lane_fatal.append(
                        f"lane {lane}: invalid staging filename {path.name}"
                    )
                    continue
                start, end = map(int, match.groups())
                if start < 1 or end > len(assigned) or end < start:
                    invalid_windows.append(
                        {"path": path.name, "errors": ["range outside assigned lane"]}
                    )
                    continue
                if end <= prefix:
                    continue
                if start <= prefix:
                    invalid_windows.append(
                        {
                            "path": path.name,
                            "errors": ["range overlaps checkpoint seed boundary"],
                        }
                    )
                    continue

                indices = set(range(start, end + 1))
                dup = indices & seen_forward
                if dup:
                    duplicate_total += len(dup)
                    invalid_windows.append(
                        {
                            "path": path.name,
                            "errors": [
                                f"overlaps other forward output at {min(dup)}..{max(dup)}"
                            ],
                        }
                    )
                    continue
                seen_forward |= indices
                persisted |= indices

                result = validate_window(
                    path, lane, start, end, assigned, base, authority, contract
                )
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

                if start >= direct_start(authority, lane):
                    allowed = allowed_forward_end(qa, lane)
                    qa_violation_indices |= {
                        idx for idx in indices if idx > allowed
                    }

        full_indices = set(range(1, len(assigned) + 1))
        uncovered = full_indices - accepted
        accepted_count = len(accepted)
        accepted_total += accepted_count
        invalid_total += len(invalid_windows)
        hold_total += len(hold_windows)
        qa_violation_total += len(qa_violation_indices)
        fatal_errors.extend(lane_fatal)

        lanes_summary[str(lane)] = {
            "checkpoint_seed_count": prefix,
            "corrections_applied": correction_count,
            "accepted_count": accepted_count,
            "accepted_high_watermark": max(accepted, default=0),
            "forward_frontier": min(uncovered) if uncovered else None,
            "remaining_identity_count": len(uncovered),
            "uncovered_ranges": ranges_from_indices(uncovered),
            "valid_forward_window_count": len(valid_windows),
            "invalid_windows": invalid_windows,
            "hold_windows": hold_windows,
            "qa_allowed_forward_end": allowed_forward_end(qa, lane),
            "qa_watermark_violation_count": len(qa_violation_indices),
            "qa_watermark_violation_ranges": ranges_from_indices(
                qa_violation_indices
            ),
        }

    remaining_total = 31003 - accepted_total
    final_semantic_qa_passed = bool(qa.get("final_semantic_qa_passed", False))
    complete = (
        accepted_total == 31003
        and invalid_total == 0
        and hold_total == 0
        and duplicate_total == 0
        and qa_violation_total == 0
        and final_semantic_qa_passed
        and not fatal_errors
    )

    snapshot = {
        "schema_version": "issue132-flat-pass-a-snapshot-v2-direct",
        "accepted_total": accepted_total,
        "expected_total": 31003,
        "remaining_total": remaining_total,
        "accepted_by_lane": {
            lane: lanes_summary[lane]["accepted_count"]
            for lane in sorted(lanes_summary)
        },
        "frontiers": {
            lane: lanes_summary[lane]["forward_frontier"]
            for lane in sorted(lanes_summary)
        },
        "remaining_by_lane": {
            lane: lanes_summary[lane]["remaining_identity_count"]
            for lane in sorted(lanes_summary)
        },
        "invalid_window_count": invalid_total,
        "hold_window_count": hold_total,
        "duplicate_coverage_count": duplicate_total,
        "qa_watermark_violation_count": qa_violation_total,
        "fatal_contract_error_count": len(fatal_errors),
        "final_semantic_qa_passed": final_semantic_qa_passed,
        "complete": complete,
    }

    print(
        "FLAT_SNAPSHOT_JSON="
        + json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"))
    )
    print(
        json.dumps(
            {
                "snapshot": snapshot,
                "lanes": lanes_summary,
                "fatal_errors": fatal_errors,
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    if fatal_errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
