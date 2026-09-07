"""Build the Stage 5 packed runtime index from the fixed Approved Parquet."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time
import gc

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pyarrow.parquet as pq

from danbooru_tag_tool.runtime_index import INDEX_FORMAT_VERSION

SNAPSHOT_ID = "nyanko-devs/danbooru2026@ebb02a630201c7b51487e45fb90b3fcf4cbedc20:metadata/posts-snapshot.parquet"
EXPECTED_SHA256 = "5b6b2671dc0fa966de71af76dfd342f485f76581447cec9e26c313ba9fb1c2fd"
RAW_ROWS = 11_740_666
RAW_MAX_POST_ID = 11_786_128


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dictionary_general(root: Path) -> set[str]:
    with (root / "data/source/danbooru-2026-09-02.csv").open(encoding="utf-8", newline="") as source:
        return {row[0] for row in csv.reader(source) if int(row[1]) == 0}


def scan_batches(parquet: Path):
    reader = pq.ParquetFile(parquet)
    return reader.iter_batches(batch_size=65_536, columns=["id", "is_deleted", "tag_string_general"])


def included_and_tags(batch):
    rows = batch.to_pylist()
    included = []
    states = {"true": 0, "false": 0, "null": 0}
    for row in rows:
        deleted = row["is_deleted"]
        states["null" if deleted is None else str(bool(deleted)).lower()] += 1
        if deleted is not True:
            included.append((int(row["id"]), tuple(row["tag_string_general"].split()) if row["tag_string_general"] else ()))
    return included, states


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build(root: Path, source: Path, output: Path) -> dict:
    started = time.perf_counter()
    if sha256(source) != EXPECTED_SHA256:
        raise SystemExit("Approved Parquet SHA-256 mismatch; refusing to build")
    dictionary = dictionary_general(root)
    unique_tags: set[str] = set()
    states = {"true": 0, "false": 0, "null": 0}
    population_rows = 0
    max_post_id = 0
    for batch in scan_batches(source):
        included, batch_states = included_and_tags(batch)
        for key in states:
            states[key] += batch_states[key]
        population_rows += len(included)
        if included:
            max_post_id = max(max_post_id, included[-1][0], max(post_id for post_id, _ in included))
            for _, tags in included:
                unique_tags.update(tags)
    if sum(states.values()) != RAW_ROWS or population_rows != RAW_ROWS - states["true"]:
        raise RuntimeError("Source row/population validation failed")
    tags = sorted(unique_tags)
    tag_to_id = {tag: i for i, tag in enumerate(tags)}
    unknown = sorted(unique_tags - dictionary)
    temp = output.with_name(output.name + ".building")
    if temp.exists():
        shutil.rmtree(temp)
    temp.mkdir(parents=True)
    post_ids = np.memmap(temp / "post_ids.u32", mode="w+", dtype=np.uint32, shape=population_rows)
    offsets = np.memmap(temp / "post_tag_offsets.u64", mode="w+", dtype=np.uint64, shape=population_rows + 1)
    global_counts = np.zeros(len(tags), dtype=np.uint64)
    ordinal = 0
    tag_entries = 0
    offsets[0] = 0
    for batch in scan_batches(source):
        included, _ = included_and_tags(batch)
        for post_id, row_tags in included:
            tag_ids = np.fromiter((tag_to_id[tag] for tag in row_tags), dtype=np.uint32, count=len(row_tags))
            post_ids[ordinal] = post_id
            tag_entries += len(tag_ids)
            offsets[ordinal + 1] = tag_entries
            if len(tag_ids):
                global_counts[tag_ids] += 1
            ordinal += 1
    if ordinal != population_rows:
        raise RuntimeError("Second scan population changed")
    post_ids.flush(); offsets.flush()
    post_tags = np.memmap(temp / "post_tag_ids.u32", mode="w+", dtype=np.uint32, shape=tag_entries)
    # Repeat source scan only to materialize compact reverse tag lists.
    ordinal = 0; cursor = 0
    for batch in scan_batches(source):
        included, _ = included_and_tags(batch)
        for _, row_tags in included:
            count = len(row_tags)
            if count:
                post_tags[cursor:cursor + count] = [tag_to_id[tag] for tag in row_tags]
            cursor += count; ordinal += 1
    post_tags.flush()
    tag_offsets = np.empty(len(tags) + 1, dtype=np.uint64)
    tag_offsets[0] = 0
    np.cumsum(global_counts, out=tag_offsets[1:])
    postings = np.memmap(temp / "tag_post_ordinals.u32", mode="w+", dtype=np.uint32, shape=tag_entries)
    write_positions = tag_offsets[:-1].copy()
    # Process ordinal blocks.  A stable tag sort retains ordinal order inside
    # each posting list while avoiding Python objects for every tag occurrence.
    block_posts = 250_000
    for block_start in range(0, population_rows, block_posts):
        block_end = min(block_start + block_posts, population_rows)
        entry_start, entry_end = int(offsets[block_start]), int(offsets[block_end])
        block_tag_ids = np.asarray(post_tags[entry_start:entry_end])
        lengths = np.diff(offsets[block_start:block_end + 1]).astype(np.intp, copy=False)
        block_ordinals = np.repeat(np.arange(block_start, block_end, dtype=np.uint32), lengths)
        order = np.argsort(block_tag_ids, kind="stable")
        sorted_ids = block_tag_ids[order]
        sorted_ordinals = block_ordinals[order]
        boundaries = np.flatnonzero(np.r_[True, sorted_ids[1:] != sorted_ids[:-1], True])
        for start, end in zip(boundaries[:-1], boundaries[1:]):
            tag_id = int(sorted_ids[start])
            position = int(write_positions[tag_id])
            postings[position:position + end - start] = sorted_ordinals[start:end]
            write_positions[tag_id] += end - start
    np.asarray(tag_offsets, dtype=np.uint64).tofile(temp / "tag_post_offsets.u64")
    np.asarray(global_counts, dtype=np.uint32).tofile(temp / "runtime_global_counts.u32")
    postings.flush()
    write_json(temp / "tags.json", tags)
    unknown_examples = unknown[:20]
    metadata = {
        "index_format_version": INDEX_FORMAT_VERSION,
        "statistics_dataset_snapshot_id": SNAPSHOT_ID,
        "statistics_population_rows": population_rows,
        "runtime_global_total_posts": population_rows,
        "unique_general_tags": len(tags),
        "dictionary_resolved_general_tags": len(unique_tags & dictionary),
        "dictionary_unresolved_general_tags": len(unknown),
        "dictionary_unresolved_examples": unknown_examples,
    }
    write_json(temp / "index_metadata.json", metadata)
    hashes = {name: sha256(temp / name) for name in ("post_ids.u32", "post_tag_offsets.u64", "post_tag_ids.u32", "tag_post_offsets.u64", "tag_post_ordinals.u32", "runtime_global_counts.u32", "tags.json", "index_metadata.json")}
    dictionary_hash = sha256(root / "data/source/danbooru-2026-09-02.csv")
    special_hash = sha256(root / "data/special2788/illustrious_tag_knowledge_base_2788.csv")
    semantic_hash = sha256(root / "data/semantic/semantic_bridge_v1.csv")
    manifest = {
        "app_version": "1.3-stage5",
        "statistics_dataset_name": "nyanko-devs/danbooru2026",
        "statistics_dataset_revision": "ebb02a630201c7b51487e45fb90b3fcf4cbedc20",
        "statistics_dataset_snapshot_id": SNAPSHOT_ID,
        "statistics_dataset_sha256": EXPECTED_SHA256,
        "statistics_dataset_hash": EXPECTED_SHA256,
        "statistics_raw_rows": RAW_ROWS,
        "statistics_population_rows": population_rows,
        "statistics_total_posts": population_rows,
        "statistics_max_post_id": max_post_id,
        "tag_dictionary_snapshot": "2026-09-02",
        "tag_dictionary_sha256": dictionary_hash,
        "tag_dictionary_hash": dictionary_hash,
        "special2788_version": "2026-09-02",
        "special2788_hash": special_hash,
        "semantic_bridge_version": "v1",
        "semantic_bridge_hash": semantic_hash,
        "index_format_version": INDEX_FORMAT_VERSION,
        "index_build_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_canonical_tags": 124016,
        "is_deleted_true_count": states["true"],
        "is_deleted_false_count": states["false"],
        "is_deleted_null_count": states["null"],
        "runtime_global_total_posts": population_rows,
        "index_file_sha256": hashes,
    }
    write_json(temp / "BUILD_MANIFEST.json", manifest)
    report = {**metadata, "build_seconds": time.perf_counter() - started, "tag_entries": tag_entries, "source_sha256_verified": EXPECTED_SHA256}
    write_json(temp / "build_report.json", report)
    # Windows does not allow a directory rename while these mmap-backed files
    # remain open.  Release every view only after all validation/report writes.
    del postings, post_tags, offsets, post_ids
    # The final block's ndarray views may retain a Windows mmap handle too.
    del block_tag_ids, lengths, block_ordinals, order, sorted_ids, sorted_ordinals, boundaries
    gc.collect()
    if output.exists():
        raise SystemExit(f"Refusing to overwrite existing final index: {output}")
    temp.replace(output)
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(build(Path.cwd(), args.source, args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
