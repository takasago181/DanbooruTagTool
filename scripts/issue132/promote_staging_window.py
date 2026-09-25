#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
from pathlib import Path

from parallel_overlay import load_checkpoint_union
from staging_v2 import SCHEMA_V2, compact_row_to_full, validate_identity_binding

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_V1 = "issue132-pass-a-staging-window-v1"
NEUTRAL = ROOT / "docs/issue132/parallel/input/luna_neutral_review_input_v2.csv"


def load_base():
    p = ROOT / "scripts/issue132/validate_luna_pass_a.py"
    s = importlib.util.spec_from_file_location("issue132_promote_base", p)
    if s is None or s.loader is None:
        raise SystemExit("cannot load base validator")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def normalize_row(entry, fields):
    if isinstance(entry, dict):
        if set(entry.keys()) != set(fields):
            raise SystemExit("staging finalized row field-set mismatch")
        return {field: str(entry[field]) for field in fields}
    if isinstance(entry, list):
        if len(entry) != len(fields):
            raise SystemExit(f"ordered staging row must have exactly {len(fields)} fields")
        return {field: str(value) for field, value in zip(fields, entry)}
    raise SystemExit("staging finalized row must be object or ordered 22-field array")


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", type=int, required=True, choices=(1, 2, 3))
    ap.add_argument("--start", type=int, required=True)
    ap.add_argument("--end", type=int, required=True)
    args = ap.parse_args()

    base = load_base()
    lane, start, end = args.lane, args.start, args.end
    if end < start or end - start + 1 > 25:
        raise SystemExit("promotion range must be 1..25 rows")

    stage_path = ROOT / f"docs/issue132/parallel/lane-{lane}/staging/window_{start:06d}_{end:06d}.json"
    if not stage_path.is_file():
        raise SystemExit(f"missing staging window: {stage_path}")

    obj = json.loads(stage_path.read_text(encoding="utf-8"))
    schema = obj.get("schema_version")
    if schema not in {SCHEMA_V1, SCHEMA_V2}:
        raise SystemExit("staging schema mismatch")
    if obj.get("lane") != lane:
        raise SystemExit("staging lane mismatch")
    if obj.get("lane_local_start") != start or obj.get("lane_local_end") != end:
        raise SystemExit("staging range metadata mismatch")

    holds = obj.get("holds", [])
    raw_rows = obj.get("rows", [])
    if holds:
        raise SystemExit(f"staging window still has {len(holds)} active hold(s)")
    if not isinstance(raw_rows, list) or len(raw_rows) != end - start + 1:
        raise SystemExit("staging window is not fully finalized")

    if schema == SCHEMA_V1:
        rows = [normalize_row(entry, base.FIELDS) for entry in raw_rows]
    else:
        neutral = read_csv(NEUTRAL)
        assigned = [
            r for r in neutral
            if ((int(r["review_seq"]) - 1) % 3) + 1 == lane
        ]
        rows_by_index: dict[int, dict[str, str]] = {}
        for entry in raw_rows:
            if not isinstance(entry, dict):
                raise SystemExit("compact staging finalized row must be an object")
            try:
                local_index = int(entry.get("lane_local_index"))
            except Exception:
                raise SystemExit("compact row invalid lane_local_index")
            if local_index < start or local_index > end:
                raise SystemExit("compact row lane_local_index outside promotion window")
            expected = assigned[local_index - 1]
            bind_errors = validate_identity_binding(entry, expected, local_index)
            if bind_errors:
                raise SystemExit("; ".join(bind_errors))
            if local_index in rows_by_index:
                raise SystemExit(f"duplicate compact row local index {local_index}")
            try:
                rows_by_index[local_index] = compact_row_to_full(entry, expected, base.FIELDS)
            except Exception as exc:
                raise SystemExit(f"compact row local {local_index}: {exc}")
        expected_indices = set(range(start, end + 1))
        if set(rows_by_index) != expected_indices:
            missing = sorted(expected_indices - set(rows_by_index))
            raise SystemExit(f"compact staging coverage mismatch missing={missing}")
        rows = [rows_by_index[i] for i in range(start, end + 1)]

    raw, _, errors = load_checkpoint_union(ROOT, lane, base.FIELDS)
    if errors:
        raise SystemExit("\n".join(errors))
    expected_start = len(raw) + 1
    if start != expected_start:
        raise SystemExit(f"promotion must begin at checkpoint prefix {expected_start}, got {start}")

    ordered = sorted(rows, key=lambda r: int(r["review_seq"]))
    for row in ordered:
        row_errors = base.validate_row(row, int(row["review_seq"]))
        if row_errors:
            raise SystemExit("\n".join(row_errors))

    checkpoint_dir = ROOT / f"docs/issue132/parallel/lane-{lane}/checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    out = checkpoint_dir / f"checkpoint_{start:06d}_{end:06d}.csv"
    if out.exists():
        raise SystemExit(f"checkpoint already exists: {out}")

    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=base.FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(ordered)

    with out.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        parsed = list(reader)
    if header != base.FIELDS:
        out.unlink(missing_ok=True)
        raise SystemExit("parse-back header mismatch")
    if parsed != ordered:
        out.unlink(missing_ok=True)
        raise SystemExit("parse-back row mismatch")

    print(json.dumps({
        "schema_version": "issue132-staging-promotion-v2",
        "source_staging_schema": schema,
        "lane": lane,
        "lane_local_start": start,
        "lane_local_end": end,
        "rows": len(ordered),
        "checkpoint": str(out.relative_to(ROOT)),
        "staging_source": str(stage_path.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
