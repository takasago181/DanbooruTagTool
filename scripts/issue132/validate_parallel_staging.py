#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
from pathlib import Path

from parallel_overlay import load_checkpoint_union
from staging_v2 import (
    SCHEMA_V2,
    compact_row_to_full,
    validate_compact_hold,
    validate_identity_binding,
)
from staging_repair_overlay import resolve_repair_overlay

ROOT = Path(__file__).resolve().parents[2]
LANES = (1, 2, 3)
STAGE_RE = re.compile(r"^window_(\d{6})_(\d{6})\.json$")
QA_RE = re.compile(r"^qa_(\d{6})_(\d{6})\.json$")
SCHEMA_V1 = "issue132-pass-a-staging-window-v1"
EXPECTED_PARENT_SHA = "ac0f888d02f19a440c63b3b9f695c58f9ba53b98ebe9756edec51db1c5ff8f7d"
EXPECTED_ORDER_SHA = "f80c63018ce19a8c7c5d8d6fd83d03cf760c510d8f6cfa455d1ab356fb31361b"


def load_base():
    p = ROOT / "scripts/issue132/validate_luna_pass_a.py"
    s = importlib.util.spec_from_file_location("issue132_staging_base", p)
    if s is None or s.loader is None:
        raise SystemExit("cannot load base validator")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def normalize_row(entry, fields):
    if isinstance(entry, dict):
        if set(entry.keys()) != set(fields):
            return None, "finalized row field-set mismatch"
        return {field: str(entry[field]) for field in fields}, None
    if isinstance(entry, list):
        if len(entry) != len(fields):
            return None, f"ordered finalized row must have exactly {len(fields)} fields"
        return {field: str(value) for field, value in zip(fields, entry)}, None
    return None, "finalized row must be an object or ordered 22-field array"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--parallel-dir", default="docs/issue132/parallel")
    args = ap.parse_args()

    base = load_base()
    neutral = read_csv(Path(args.input))
    errors: list[str] = []
    summary: dict[str, object] = {}
    total_finalized = 0
    total_holds = 0

    qa_baseline_path = ROOT / args.parallel_dir / "QA_BASELINE.json"
    qa_baseline = {}
    if qa_baseline_path.is_file():
        try:
            qa_baseline = json.loads(qa_baseline_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"QA baseline unreadable: {exc}")
    else:
        errors.append("QA baseline missing")

    qa_root = ROOT / args.parallel_dir / "qa"

    for lane in LANES:
        assigned = [r for r in neutral if ((int(r["review_seq"]) - 1) % 3) + 1 == lane]
        raw, _, raw_errors = load_checkpoint_union(ROOT, lane, base.FIELDS)
        errors.extend(raw_errors)
        prefix = len(raw)

        stage_dir = ROOT / args.parallel_dir / f"lane-{lane}" / "staging"
        windows = []
        seen_indices: set[int] = set()
        lane_finalized = 0
        lane_holds = 0
        complete_staged_windows = 0

        if stage_dir.exists():
            for path in sorted(stage_dir.glob("window_*.json")):
                m = STAGE_RE.match(path.name)
                if not m:
                    errors.append(f"lane {lane}: invalid staging filename {path.name}")
                    continue
                start, end = map(int, m.groups())
                if end < start:
                    errors.append(f"lane {lane}: {path.name} invalid range")
                    continue
                if end - start + 1 > 25:
                    errors.append(f"lane {lane}: {path.name} exceeds 25-row staging window")
                if start < 1 or end > len(assigned):
                    errors.append(f"lane {lane}: {path.name} outside assigned lane")
                    continue

                repair_obj, repair_name, repair_errors = resolve_repair_overlay(
                    path, lane, start, end
                )
                errors.extend(f"lane {lane}: {err}" for err in repair_errors)
                if repair_errors:
                    continue

                if repair_obj is not None:
                    obj = repair_obj
                else:
                    try:
                        obj = json.loads(path.read_text(encoding="utf-8"))
                    except Exception as exc:
                        errors.append(f"lane {lane}: {path.name} invalid JSON: {exc}")
                        continue

                schema = obj.get("schema_version")
                if schema not in {SCHEMA_V1, SCHEMA_V2}:
                    errors.append(f"lane {lane}: {path.name} schema mismatch")
                    continue
                if obj.get("lane") != lane:
                    errors.append(f"lane {lane}: {path.name} lane mismatch")
                if obj.get("lane_local_start") != start or obj.get("lane_local_end") != end:
                    errors.append(f"lane {lane}: {path.name} range metadata mismatch")
                if obj.get("parent_neutral_sha256") != EXPECTED_PARENT_SHA:
                    errors.append(f"lane {lane}: {path.name} parent neutral SHA mismatch")
                if obj.get("parent_identity_order_sha256") != EXPECTED_ORDER_SHA:
                    errors.append(f"lane {lane}: {path.name} parent order SHA mismatch")

                rows = obj.get("rows", [])
                holds = obj.get("holds", [])
                if not isinstance(rows, list) or not isinstance(holds, list):
                    errors.append(f"lane {lane}: {path.name} rows/holds must be lists")
                    continue

                covered: dict[int, str] = {}
                row_by_index: dict[int, dict[str, str]] = {}

                if schema == SCHEMA_V1:
                    for raw_entry in rows:
                        entry, normalize_error = normalize_row(raw_entry, base.FIELDS)
                        if normalize_error:
                            errors.append(f"lane {lane}: {path.name} {normalize_error}")
                            continue
                        try:
                            seq = int(entry["review_seq"])
                        except Exception:
                            errors.append(f"lane {lane}: {path.name} invalid finalized review_seq")
                            continue
                        ident = entry.get("identity_key", "")
                        matches = [
                            i for i in range(start, end + 1)
                            if int(assigned[i - 1]["review_seq"]) == seq
                            and assigned[i - 1]["identity_key"] == ident
                        ]
                        if len(matches) != 1:
                            errors.append(f"lane {lane}: {path.name} finalized row {ident} not exact window identity")
                            continue
                        local_index = matches[0]
                        if local_index in covered:
                            errors.append(f"lane {lane}: {path.name} duplicate local index {local_index}")
                            continue
                        covered[local_index] = "row"
                        row_by_index[local_index] = entry
                        row_errors = base.validate_row(entry, seq)
                        errors.extend(
                            f"lane {lane} staging {path.name} local {local_index} review_seq {seq}: {err}"
                            for err in row_errors
                        )

                    for hold in holds:
                        if not isinstance(hold, dict):
                            errors.append(f"lane {lane}: {path.name} non-object hold")
                            continue
                        required = {"lane_local_index", "review_seq", "identity_key", "reason", "research_attempts"}
                        if not required.issubset(hold):
                            errors.append(f"lane {lane}: {path.name} hold missing required fields")
                            continue
                        try:
                            local_index = int(hold["lane_local_index"])
                            seq = int(hold["review_seq"])
                        except Exception:
                            errors.append(f"lane {lane}: {path.name} invalid hold indices")
                            continue
                        if local_index < start or local_index > end:
                            errors.append(f"lane {lane}: {path.name} hold local index outside window")
                            continue
                        expected = assigned[local_index - 1]
                        if int(expected["review_seq"]) != seq or expected["identity_key"] != hold["identity_key"]:
                            errors.append(f"lane {lane}: {path.name} hold identity mismatch at local {local_index}")
                        if local_index in covered:
                            errors.append(f"lane {lane}: {path.name} duplicate row/hold at local {local_index}")
                        covered[local_index] = "hold"
                        if not str(hold.get("reason", "")).strip():
                            errors.append(f"lane {lane}: {path.name} hold has blank reason")
                        attempts = hold.get("research_attempts")
                        if not isinstance(attempts, list) or not attempts:
                            errors.append(f"lane {lane}: {path.name} hold requires concrete research_attempts")

                else:
                    for raw_entry in rows:
                        if not isinstance(raw_entry, dict):
                            errors.append(f"lane {lane}: {path.name} compact finalized row must be an object")
                            continue
                        try:
                            local_index = int(raw_entry.get("lane_local_index"))
                        except Exception:
                            errors.append(f"lane {lane}: {path.name} compact row invalid lane_local_index")
                            continue
                        if local_index < start or local_index > end:
                            errors.append(f"lane {lane}: {path.name} compact row local index outside window")
                            continue
                        expected = assigned[local_index - 1]
                        bind_errors = validate_identity_binding(raw_entry, expected, local_index)
                        errors.extend(
                            f"lane {lane}: {path.name} compact row local {local_index}: {err}"
                            for err in bind_errors
                        )
                        if bind_errors:
                            continue
                        if local_index in covered:
                            errors.append(f"lane {lane}: {path.name} duplicate local index {local_index}")
                            continue
                        try:
                            entry = compact_row_to_full(raw_entry, expected, base.FIELDS)
                        except Exception as exc:
                            errors.append(f"lane {lane}: {path.name} compact row local {local_index}: {exc}")
                            continue
                        covered[local_index] = "row"
                        row_by_index[local_index] = entry
                        seq = int(expected["review_seq"])
                        row_errors = base.validate_row(entry, seq)
                        errors.extend(
                            f"lane {lane} staging {path.name} local {local_index} review_seq {seq}: {err}"
                            for err in row_errors
                        )

                    for hold in holds:
                        if not isinstance(hold, dict):
                            errors.append(f"lane {lane}: {path.name} compact hold must be an object")
                            continue
                        try:
                            local_index = int(hold.get("lane_local_index"))
                        except Exception:
                            errors.append(f"lane {lane}: {path.name} compact hold invalid lane_local_index")
                            continue
                        if local_index < start or local_index > end:
                            errors.append(f"lane {lane}: {path.name} compact hold local index outside window")
                            continue
                        expected = assigned[local_index - 1]
                        hold_errors = validate_compact_hold(hold, expected, local_index)
                        errors.extend(
                            f"lane {lane}: {path.name} compact hold local {local_index}: {err}"
                            for err in hold_errors
                        )
                        if local_index in covered:
                            errors.append(f"lane {lane}: {path.name} duplicate row/hold at local {local_index}")
                        covered[local_index] = "hold"

                expected_indices = set(range(start, end + 1))
                if set(covered) != expected_indices:
                    missing = sorted(expected_indices - set(covered))
                    extra = sorted(set(covered) - expected_indices)
                    errors.append(f"lane {lane}: {path.name} coverage mismatch missing={missing} extra={extra}")

                for idx in expected_indices:
                    if idx in seen_indices:
                        errors.append(f"lane {lane}: overlapping staging local index {idx}")
                    seen_indices.add(idx)

                if end <= prefix:
                    if holds:
                        errors.append(f"lane {lane}: {path.name} has holds inside committed prefix")
                    for idx, entry in row_by_index.items():
                        if idx <= len(raw) and raw[idx - 1] != entry:
                            errors.append(f"lane {lane}: {path.name} promoted staging row differs from raw checkpoint at local {idx}")

                finalized_count = len(rows)
                hold_count = len(holds)
                lane_finalized += finalized_count
                lane_holds += hold_count
                if hold_count == 0 and finalized_count == end - start + 1:
                    complete_staged_windows += 1

                windows.append({
                    "path": path.name,
                    "schema": schema,
                    "repair_overlay": repair_name,
                    "start": start,
                    "end": end,
                    "finalized": finalized_count,
                    "holds": hold_count,
                    "promotable_now": hold_count == 0 and finalized_count == end - start + 1 and start == prefix + 1,
                })

        total_finalized += lane_finalized
        total_holds += lane_holds

        staging_high_watermark = max((int(w["end"]) for w in windows), default=prefix)
        stage_ranges = {(int(w["start"]), int(w["end"])) for w in windows}
        write_gaps = []
        if staging_high_watermark > prefix:
            expected_start = prefix + 1
            while expected_start <= staging_high_watermark:
                expected_end = min(expected_start + 24, len(assigned))
                if (expected_start, expected_end) not in stage_ranges:
                    write_gaps.append({
                        "start": expected_start,
                        "end": expected_end,
                        "path": f"window_{expected_start:06d}_{expected_end:06d}.json",
                    })
                expected_start = expected_end + 1

        qa_markers = []
        qa_lane_dir = qa_root / f"lane-{lane}"
        if qa_lane_dir.exists():
            for qa_path in sorted(qa_lane_dir.glob("qa_*.json")):
                qm = QA_RE.match(qa_path.name)
                if qm:
                    qstart, qend = map(int, qm.groups())
                    qa_markers.append({
                        "path": qa_path.name,
                        "start": qstart,
                        "end": qend,
                    })

        marker_ends = {int(m["end"]) for m in qa_markers}
        next_post_boundary = (
            qa_baseline.get("post_baseline_next_qa_boundary", {}).get(str(lane))
            if isinstance(qa_baseline, dict) else None
        )
        post_baseline_due = None
        if isinstance(next_post_boundary, int):
            post_baseline_due = (
                next_post_boundary
                if staging_high_watermark >= next_post_boundary
                and next_post_boundary not in marker_ends
                else None
            )

        legacy_boundaries = (
            qa_baseline.get("legacy_backlog", {}).get(str(lane), [])
            if isinstance(qa_baseline, dict) else []
        )
        legacy_due = [
            int(boundary)
            for boundary in legacy_boundaries
            if isinstance(boundary, int) and boundary not in marker_ends
        ]

        summary[str(lane)] = {
            "checkpoint_prefix": prefix,
            "staging_window_count": len(windows),
            "staging_high_watermark": staging_high_watermark,
            "write_gaps": write_gaps,
            "staged_finalized_rows": lane_finalized,
            "active_holds": lane_holds,
            "complete_staged_windows": complete_staged_windows,
            "qa_markers": qa_markers,
            "post_baseline_qa_due": post_baseline_due,
            "legacy_qa_due": legacy_due,
            "windows": windows,
        }

    window_error_re = re.compile(
        r"^lane\s+(\d+)(?::| staging)\s+(window_\d{6}_\d{6}\.json)"
    )
    invalid_windows: dict[str, set[str]] = {str(lane): set() for lane in LANES}
    for error in errors:
        m = window_error_re.match(error)
        if m:
            invalid_windows[m.group(1)].add(m.group(2))

    invalid_window_summary = {
        lane: sorted(names) for lane, names in invalid_windows.items()
    }
    invalid_window_counts = {
        lane: len(names) for lane, names in invalid_windows.items()
    }

    promotion_blocking_holds: dict[str, int | None] = {}
    promotion_blocking_windows: dict[str, str | None] = {}
    for lane in LANES:
        lane_summary = summary[str(lane)]
        expected_start = int(lane_summary["checkpoint_prefix"]) + 1
        first = next(
            (w for w in lane_summary["windows"] if int(w["start"]) == expected_start),
            None,
        )
        if first is None:
            promotion_blocking_holds[str(lane)] = None
            promotion_blocking_windows[str(lane)] = None
        else:
            promotion_blocking_holds[str(lane)] = int(first["holds"])
            promotion_blocking_windows[str(lane)] = str(first["path"])

    known_promotion_hold_total = sum(
        count for count in promotion_blocking_holds.values() if count is not None
    )
    promotion_hold_counts_complete = all(
        count is not None for count in promotion_blocking_holds.values()
    )

    post_baseline_due = {
        lane: summary[lane]["post_baseline_qa_due"]
        for lane in sorted(summary)
        if summary[lane]["post_baseline_qa_due"] is not None
    }
    legacy_candidates = sorted(
        (
            int(boundary),
            int(lane),
        )
        for lane, lane_summary in summary.items()
        for boundary in lane_summary["legacy_qa_due"]
    )
    next_legacy_qa = (
        {"lane": legacy_candidates[0][1], "boundary": legacy_candidates[0][0]}
        if legacy_candidates else None
    )

    lane3_route_family_windows = []
    for name in invalid_window_summary.get("3", []):
        m = STAGE_RE.match(name)
        if not m:
            continue
        start, end = map(int, m.groups())
        if not (end < 751 or start > 1050):
            lane3_route_family_windows.append(name)

    coordinator_snapshot = {
        "checkpoint_prefixes": {
            lane: summary[lane]["checkpoint_prefix"] for lane in sorted(summary)
        },
        "staging_high_watermarks": {
            lane: summary[lane]["staging_high_watermark"] for lane in sorted(summary)
        },
        "write_gaps": {
            lane: summary[lane]["write_gaps"] for lane in sorted(summary)
        },
        "qa_marker_counts": {
            lane: len(summary[lane]["qa_markers"]) for lane in sorted(summary)
        },
        "post_baseline_qa_due": post_baseline_due,
        "next_legacy_qa": next_legacy_qa,
        "effective_invalid_windows": invalid_window_summary,
        "effective_invalid_window_counts": invalid_window_counts,
        "promotion_blocking_holds": promotion_blocking_holds,
        "promotion_blocking_holds_total": (
            known_promotion_hold_total if promotion_hold_counts_complete else None
        ),
        "lane3_route_family_range": [751, 1050],
        "lane3_route_family_effective_invalid_windows": lane3_route_family_windows,
        "lane3_route_family_state": (
            "OUTSTANDING" if lane3_route_family_windows else "NO_EFFECTIVE_INVALID_WINDOWS"
        ),
    }

    result = {
        "schema_version": "issue132-parallel-staging-validation-v3",
        "coordinator_snapshot": coordinator_snapshot,
        "staged_finalized_rows": total_finalized,
        "active_holds": total_holds,
        "lanes": summary,
        "effective_invalid_windows": invalid_window_summary,
        "effective_invalid_window_counts": invalid_window_counts,
        "promotion_blocking_windows": promotion_blocking_windows,
        "promotion_blocking_holds": promotion_blocking_holds,
        "promotion_blocking_holds_total": (
            known_promotion_hold_total if promotion_hold_counts_complete else None
        ),
        "error_count": len(errors),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        for error in errors[:100]:
            print("ERROR:", error)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
