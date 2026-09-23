#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

EXPECTED_PARENT_SHA = "ac0f888d02f19a440c63b3b9f695c58f9ba53b98ebe9756edec51db1c5ff8f7d"
EXPECTED_ORDER_SHA = "f80c63018ce19a8c7c5d8d6fd83d03cf760c510d8f6cfa455d1ab356fb31361b"
EXPECTED_POPULATION = 31_003
EXPECTED_FIELDS = ["review_seq", "identity_key", "source_surfaces"]
EXPECTED_LANE_COUNTS = {1: 10_335, 2: 10_334, 3: 10_334}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def identity_order_sha(rows: list[dict[str, str]]) -> str:
    payload = "".join(row["identity_key"] + "\n" for row in rows).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--shard-root", required=True)
    args = ap.parse_args()

    source = Path(args.input)
    root = Path(args.shard_root)

    fields, neutral = read_csv(source)
    errors: list[str] = []

    if fields != EXPECTED_FIELDS:
        errors.append("neutral header mismatch")
    if len(neutral) != EXPECTED_POPULATION:
        errors.append(f"neutral population mismatch: {len(neutral)}")
    if sha256_file(source) != EXPECTED_PARENT_SHA:
        errors.append("neutral SHA mismatch")
    if identity_order_sha(neutral) != EXPECTED_ORDER_SHA:
        errors.append("neutral identity-order SHA mismatch")

    index_path = root / "index.json"
    if not index_path.is_file():
        errors.append("missing shard index.json")
        index = {}
    else:
        try:
            index = json.loads(index_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid index.json: {exc}")
            index = {}

    if index.get("schema_version") != "issue132-worker-neutral-shard-index-v1":
        errors.append("shard index schema mismatch")
    if index.get("population") != EXPECTED_POPULATION:
        errors.append("shard index population mismatch")
    if index.get("parent_neutral_sha256") != EXPECTED_PARENT_SHA:
        errors.append("shard index parent neutral SHA mismatch")
    if index.get("parent_identity_order_sha256") != EXPECTED_ORDER_SHA:
        errors.append("shard index parent order SHA mismatch")

    entries = index.get("shards", [])
    if not isinstance(entries, list):
        errors.append("shard index shards must be a list")
        entries = []

    neutral_by_lane = {
        lane: [r for r in neutral if ((int(r["review_seq"]) - 1) % 3) + 1 == lane]
        for lane in (1, 2, 3)
    }

    seen_paths: set[str] = set()
    reconstructed: dict[int, list[dict[str, str]]] = {1: [], 2: [], 3: []}
    expected_local_next = {1: 1, 2: 1, 3: 1}

    for entry in entries:
        try:
            lane = int(entry["lane"])
            start = int(entry["lane_local_start"])
            end = int(entry["lane_local_end"])
            csv_rel = str(entry["csv_path"])
            meta_rel = str(entry["manifest_path"])
        except Exception as exc:
            errors.append(f"malformed shard index entry: {exc}")
            continue

        if lane not in (1, 2, 3):
            errors.append(f"invalid lane in index: {lane}")
            continue
        if csv_rel in seen_paths:
            errors.append(f"duplicate shard path: {csv_rel}")
        seen_paths.add(csv_rel)
        if start != expected_local_next[lane]:
            errors.append(f"lane {lane} shard start {start}, expected {expected_local_next[lane]}")
        expected_local_next[lane] = end + 1

        csv_path = Path(csv_rel)
        meta_path = Path(meta_rel)
        if not csv_path.is_file():
            errors.append(f"missing shard CSV: {csv_rel}")
            continue
        if not meta_path.is_file():
            errors.append(f"missing shard manifest: {meta_rel}")
            continue

        header, rows = read_csv(csv_path)
        if header != EXPECTED_FIELDS:
            errors.append(f"{csv_rel}: header mismatch")
        if len(rows) != end - start + 1:
            errors.append(f"{csv_rel}: row count/range mismatch")

        expected = neutral_by_lane[lane][start - 1 : end]
        if rows != expected:
            errors.append(f"{csv_rel}: rows differ from deterministic neutral lane slice")

        actual_sha = sha256_file(csv_path)
        if actual_sha != entry.get("csv_sha256"):
            errors.append(f"{csv_rel}: index SHA mismatch")

        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{meta_rel}: invalid JSON: {exc}")
            continue

        required_equal = {
            "schema_version": "issue132-worker-neutral-shard-v1",
            "lane": lane,
            "lane_local_start": start,
            "lane_local_end": end,
            "row_count": len(rows),
            "csv_path": csv_rel,
            "csv_sha256": actual_sha,
            "parent_neutral_sha256": EXPECTED_PARENT_SHA,
            "parent_identity_order_sha256": EXPECTED_ORDER_SHA,
            "parent_population": EXPECTED_POPULATION,
        }
        for key, expected_value in required_equal.items():
            if meta.get(key) != expected_value:
                errors.append(f"{meta_rel}: {key} mismatch")

        if identity_order_sha(rows) != meta.get("identity_order_sha256"):
            errors.append(f"{meta_rel}: shard identity-order SHA mismatch")

        reconstructed[lane].extend(rows)

    expected_shard_count = sum(
        (count + int(index.get("shard_size", 300)) - 1) // int(index.get("shard_size", 300))
        for count in EXPECTED_LANE_COUNTS.values()
    )
    if len(entries) != expected_shard_count:
        errors.append(f"shard count mismatch: {len(entries)} != {expected_shard_count}")

    for lane, expected_count in EXPECTED_LANE_COUNTS.items():
        if len(reconstructed[lane]) != expected_count:
            errors.append(f"lane {lane}: reconstructed count {len(reconstructed[lane])} != {expected_count}")
        if reconstructed[lane] != neutral_by_lane[lane]:
            errors.append(f"lane {lane}: reconstructed lane differs from neutral authority")

    result = {
        "schema_version": "issue132-worker-neutral-shard-validation-v1",
        "population": len(neutral),
        "shard_count": len(entries),
        "lane_counts": {str(k): len(v) for k, v in reconstructed.items()},
        "error_count": len(errors),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        for error in errors[:100]:
            print("ERROR:", error)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
