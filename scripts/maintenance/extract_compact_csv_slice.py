#!/usr/bin/env python3
"""Deterministically extract a compact CSV slice from a large authoritative CSV.

Issue #188 utility.

The source remains authoritative. The compact output is transport/cache only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_fields(value: str | None) -> list[str] | None:
    if value is None:
        return None
    fields = [x.strip() for x in value.split(",") if x.strip()]
    if not fields:
        raise SystemExit("--fields must contain at least one column")
    return fields


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--expected-sha256")
    ap.add_argument("--fields", help="comma-separated output fields; default=all")
    ap.add_argument("--start", type=int, default=1, help="1-based row within filtered population")
    ap.add_argument("--count", type=int, required=True)
    ap.add_argument("--key-column")
    ap.add_argument("--order-column")
    ap.add_argument("--lane-column")
    ap.add_argument("--lane-count", type=int)
    ap.add_argument("--lane", type=int)
    args = ap.parse_args()

    source = Path(args.input)
    output = Path(args.output)

    if args.start < 1:
        raise SystemExit("--start must be >= 1")
    if args.count < 1:
        raise SystemExit("--count must be >= 1")

    lane_args = [args.lane_column, args.lane_count, args.lane]
    if any(x is not None for x in lane_args) and not all(x is not None for x in lane_args):
        raise SystemExit("--lane-column, --lane-count and --lane must be supplied together")
    if args.lane_count is not None:
        if args.lane_count < 1:
            raise SystemExit("--lane-count must be >= 1")
        if not 1 <= args.lane <= args.lane_count:
            raise SystemExit("--lane must be within 1..lane-count")

    source_sha = sha256_file(source)
    if args.expected_sha256 and source_sha.lower() != args.expected_sha256.lower():
        raise SystemExit(
            f"source sha256 mismatch: {source_sha} != {args.expected_sha256.lower()}"
        )

    with source.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        rows = list(reader)

    requested_fields = parse_fields(args.fields) or list(header)
    required = set(requested_fields)
    for optional in (args.key_column, args.order_column, args.lane_column):
        if optional:
            required.add(optional)
    missing = sorted(required - set(header))
    if missing:
        raise SystemExit(f"missing columns: {missing}")

    if args.key_column:
        keys = [r[args.key_column] for r in rows]
        if any(k == "" for k in keys):
            raise SystemExit(f"blank key in {args.key_column}")
        if len(keys) != len(set(keys)):
            raise SystemExit(f"duplicate key in {args.key_column}")

    if args.order_column:
        try:
            order = [int(r[args.order_column]) for r in rows]
        except Exception as exc:
            raise SystemExit(f"non-integer order column {args.order_column}: {exc}")
        if any(b <= a for a, b in zip(order, order[1:])):
            raise SystemExit(f"{args.order_column} must be strictly increasing")

    filtered = rows
    if args.lane_column:
        selected = []
        for row in rows:
            try:
                value = int(row[args.lane_column])
            except Exception as exc:
                raise SystemExit(f"non-integer lane column {args.lane_column}: {exc}")
            lane = ((value - 1) % args.lane_count) + 1
            if lane == args.lane:
                selected.append(row)
        filtered = selected

    begin = args.start - 1
    end = min(begin + args.count, len(filtered))
    sliced = filtered[begin:end]

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=requested_fields, lineterminator="\n")
        writer.writeheader()
        for row in sliced:
            writer.writerow({k: row[k] for k in requested_fields})

    manifest = {
        "schema_version": "compact-csv-slice-v1",
        "source": str(source.as_posix()),
        "source_sha256": source_sha,
        "source_rows": len(rows),
        "source_fields": header,
        "lane_filter": (
            {
                "column": args.lane_column,
                "lane_count": args.lane_count,
                "lane": args.lane,
                "formula": "((int(value)-1)%lane_count)+1",
            }
            if args.lane_column
            else None
        ),
        "filtered_rows": len(filtered),
        "slice_start_1_based": args.start,
        "requested_count": args.count,
        "output_rows": len(sliced),
        "output_fields": requested_fields,
        "key_column": args.key_column,
        "order_column": args.order_column,
        "first_key": sliced[0][args.key_column] if sliced and args.key_column else None,
        "last_key": sliced[-1][args.key_column] if sliced and args.key_column else None,
        "first_order": sliced[0][args.order_column] if sliced and args.order_column else None,
        "last_order": sliced[-1][args.order_column] if sliced and args.order_column else None,
        "output_sha256": sha256_file(output),
        "authority_note": "transport/cache only; source remains authority",
    }
    manifest_path = output.with_suffix(output.suffix + ".manifest.json")
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
