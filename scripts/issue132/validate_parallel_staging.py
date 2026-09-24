#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
from pathlib import Path

from parallel_overlay import load_checkpoint_union

ROOT = Path(__file__).resolve().parents[2]
LANES = (1, 2, 3)
STAGE_RE = re.compile(r"^window_(\d{6})_(\d{6})\.json$")
SCHEMA = "issue132-pass-a-staging-window-v1"
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

                try:
                    obj = json.loads(path.read_text(encoding="utf-8"))
                except Exception as exc:
                    errors.append(f"lane {lane}: {path.name} invalid JSON: {exc}")
                    continue

                if obj.get("schema_version") != SCHEMA:
                    errors.append(f"lane {lane}: {path.name} schema mismatch")
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
                    "start": start,
                    "end": end,
                    "finalized": finalized_count,
                    "holds": hold_count,
                    "promotable_now": hold_count == 0 and finalized_count == end - start + 1 and start == prefix + 1,
                })

        total_finalized += lane_finalized
        total_holds += lane_holds
        summary[str(lane)] = {
            "checkpoint_prefix": prefix,
            "staging_window_count": len(windows),
            "staged_finalized_rows": lane_finalized,
            "active_holds": lane_holds,
            "complete_staged_windows": complete_staged_windows,
            "windows": windows,
        }

    result = {
        "schema_version": "issue132-parallel-staging-validation-v1",
        "staged_finalized_rows": total_finalized,
        "active_holds": total_holds,
        "lanes": summary,
        "error_count": len(errors),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        for error in errors[:100]:
            print("ERROR:", error)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
