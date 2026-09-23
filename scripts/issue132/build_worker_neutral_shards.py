#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path

EXPECTED_PARENT_SHA = "ac0f888d02f19a440c63b3b9f695c58f9ba53b98ebe9756edec51db1c5ff8f7d"
EXPECTED_ORDER_SHA = "f80c63018ce19a8c7c5d8d6fd83d03cf760c510d8f6cfa455d1ab356fb31361b"
EXPECTED_POPULATION = 31_003
EXPECTED_FIELDS = ["review_seq", "identity_key", "source_surfaces"]
LANES = (1, 2, 3)
EXPECTED_LANE_COUNTS = {1: 10_335, 2: 10_334, 3: 10_334}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def identity_order_sha(rows: list[dict[str, str]]) -> str:
    payload = "".join(row["identity_key"] + "\n" for row in rows).encode("utf-8")
    return sha256_bytes(payload)


def read_neutral(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []
        rows = list(reader)
    return fields, rows


def serialize_rows(fields: list[str], rows: list[dict[str, str]]) -> bytes:
    from io import StringIO

    buf = StringIO(newline="")
    writer = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue().encode("utf-8")


def validate_parent(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    if fields != EXPECTED_FIELDS:
        raise SystemExit(f"neutral header mismatch: {fields!r}")
    if len(rows) != EXPECTED_POPULATION:
        raise SystemExit(f"neutral population mismatch: {len(rows)}")
    if sha256_file(path) != EXPECTED_PARENT_SHA:
        raise SystemExit("neutral SHA256 mismatch")
    if identity_order_sha(rows) != EXPECTED_ORDER_SHA:
        raise SystemExit("neutral identity-order SHA256 mismatch")

    seen: set[str] = set()
    for expected_seq, row in enumerate(rows, start=1):
        try:
            seq = int(row["review_seq"])
        except Exception as exc:
            raise SystemExit(f"invalid review_seq at row {expected_seq}: {exc}")
        if seq != expected_seq:
            raise SystemExit(f"review_seq discontinuity: got {seq}, expected {expected_seq}")
        ident = row["identity_key"]
        if not ident:
            raise SystemExit(f"blank identity_key at review_seq {seq}")
        if ident in seen:
            raise SystemExit(f"duplicate identity_key: {ident}")
        seen.add(ident)


def parse_back(path: Path, fields: list[str], expected_rows: list[dict[str, str]]) -> None:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        rows = list(reader)
    if header != fields:
        raise SystemExit(f"{path}: header mismatch after write")
    if rows != expected_rows:
        raise SystemExit(f"{path}: parse-back mismatch")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--shard-size", type=int, default=300)
    args = ap.parse_args()

    source = Path(args.input)
    out = Path(args.out)
    shard_size = args.shard_size
    if shard_size <= 0:
        raise SystemExit("--shard-size must be > 0")

    fields, rows = read_neutral(source)
    validate_parent(source, fields, rows)

    lane_rows: dict[int, list[dict[str, str]]] = {lane: [] for lane in LANES}
    for row in rows:
        seq = int(row["review_seq"])
        lane = ((seq - 1) % 3) + 1
        lane_rows[lane].append(row)

    for lane in LANES:
        if len(lane_rows[lane]) != EXPECTED_LANE_COUNTS[lane]:
            raise SystemExit(
                f"lane {lane} count mismatch: {len(lane_rows[lane])} != {EXPECTED_LANE_COUNTS[lane]}"
            )

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    shard_index: list[dict[str, object]] = []

    for lane in LANES:
        lane_dir = out / f"lane-{lane}"
        lane_dir.mkdir(parents=True, exist_ok=True)
        source_rows = lane_rows[lane]

        for zero_start in range(0, len(source_rows), shard_size):
            local_start = zero_start + 1
            local_end = min(zero_start + shard_size, len(source_rows))
            shard_rows = source_rows[zero_start:local_end]

            name = f"shard_{local_start:06d}_{local_end:06d}.csv"
            path = lane_dir / name
            raw = serialize_rows(fields, shard_rows)
            path.write_bytes(raw)
            parse_back(path, fields, shard_rows)

            shard_sha = sha256_bytes(raw)
            global_review_seqs = [int(r["review_seq"]) for r in shard_rows]
            identity_sha = identity_order_sha(shard_rows)

            meta = {
                "schema_version": "issue132-worker-neutral-shard-v1",
                "lane": lane,
                "lane_count": 3,
                "assignment_rule": "((review_seq-1)%3)+1",
                "lane_local_start": local_start,
                "lane_local_end": local_end,
                "row_count": len(shard_rows),
                "global_review_seq_first": global_review_seqs[0],
                "global_review_seq_last": global_review_seqs[-1],
                "csv_path": str(path.as_posix()),
                "csv_sha256": shard_sha,
                "identity_order_sha256": identity_sha,
                "parent_neutral_sha256": EXPECTED_PARENT_SHA,
                "parent_identity_order_sha256": EXPECTED_ORDER_SHA,
                "parent_population": EXPECTED_POPULATION,
            }
            meta_path = path.with_suffix(".manifest.json")
            meta_path.write_text(
                json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            shard_index.append(
                {
                    "lane": lane,
                    "lane_local_start": local_start,
                    "lane_local_end": local_end,
                    "row_count": len(shard_rows),
                    "csv_path": str(path.as_posix()),
                    "manifest_path": str(meta_path.as_posix()),
                    "csv_sha256": shard_sha,
                    "identity_order_sha256": identity_sha,
                    "global_review_seq_first": global_review_seqs[0],
                    "global_review_seq_last": global_review_seqs[-1],
                }
            )

    index = {
        "schema_version": "issue132-worker-neutral-shard-index-v1",
        "purpose": "Small deterministic operational windows for ChatGPT Automation workers; semantic authority remains the frozen neutral input.",
        "shard_size": shard_size,
        "lane_count": 3,
        "assignment_rule": "((review_seq-1)%3)+1",
        "population": EXPECTED_POPULATION,
        "lane_counts": {str(k): v for k, v in EXPECTED_LANE_COUNTS.items()},
        "parent_neutral_sha256": EXPECTED_PARENT_SHA,
        "parent_identity_order_sha256": EXPECTED_ORDER_SHA,
        "shard_count": len(shard_index),
        "shards": shard_index,
    }
    (out / "index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "schema_version": "issue132-worker-neutral-shard-build-v1",
                "population": EXPECTED_POPULATION,
                "shard_size": shard_size,
                "shard_count": len(shard_index),
                "lane_counts": EXPECTED_LANE_COUNTS,
                "parent_neutral_sha256": EXPECTED_PARENT_SHA,
                "parent_identity_order_sha256": EXPECTED_ORDER_SHA,
                "output": str(out),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
