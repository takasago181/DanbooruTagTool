#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "docs/issue70/data/source_chunks_manifest.json"
QUEUE_PATH = ROOT / "docs/issue70/data/queue_state.json"
OUT_ROOT = ROOT / "docs/issue70/data/source_shards"
OUT_MANIFEST = ROOT / "docs/issue70/data/source_shards_manifest.json"
BOOTSTRAP_PATH = ROOT / "docs/issue70/data/automation_bootstrap.json"
SHARD_SIZE = 50

FIELDS = [
    "row_id",
    "canonical_tag",
    "category",
    "category_name",
    "source_aliases",
    "verified_aliases",
    "existing_display_ja",
    "existing_search_ja",
    "existing_candidate_ja",
    "existing_rejected_ja",
    "related_copyright_top3",
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path: Path):
    with path.open(encoding="utf-8-sig") as f:
        return json.load(f)


def read_rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def top3_context(raw: str) -> str:
    if not raw:
        return "[]"
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return "[]"
    names = []
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                name = item.get("copyright")
                if isinstance(name, str) and name and name not in names:
                    names.append(name)
            if len(names) >= 3:
                break
    return json.dumps(names, ensure_ascii=False, separators=(",", ":"))


def compact(row: dict[str, str]) -> dict[str, str]:
    return {
        "row_id": row.get("row_id", ""),
        "canonical_tag": row.get("canonical_tag", ""),
        "category": row.get("category", ""),
        "category_name": row.get("category_name", ""),
        "source_aliases": row.get("source_aliases", ""),
        "verified_aliases": row.get("verified_aliases", ""),
        "existing_display_ja": row.get("existing_display_ja", ""),
        "existing_search_ja": row.get("existing_search_ja", ""),
        "existing_candidate_ja": row.get("existing_candidate_ja", ""),
        "existing_rejected_ja": row.get("existing_rejected_ja", ""),
        "related_copyright_top3": top3_context(row.get("related_copyright_candidates", "")),
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main() -> None:
    manifest = load_json(MANIFEST_PATH)
    queue = load_json(QUEUE_PATH)
    chunks = manifest["chunks"]

    shard_manifest = {
        "format_version": 2,
        "issue": 70,
        "shard_size": SHARD_SIZE,
        "source_manifest": "docs/issue70/data/source_chunks_manifest.json",
        "source_manifest_sha256": sha256(MANIFEST_PATH),
        "chunk_manifest_pattern": "docs/issue70/data/source_shards/chunk_{chunk_index:03d}/manifest.json",
        "chunks": [],
    }

    total_rows = 0
    for chunk in chunks:
        chunk_index = int(chunk["chunk_index"])
        source_path = ROOT / chunk["file"]
        rows = read_rows(source_path)
        expected = int(chunk["row_count"])
        if len(rows) != expected:
            raise SystemExit(f"chunk {chunk_index}: row count {len(rows)} != {expected}")
        if sha256(source_path) != chunk["sha256"]:
            raise SystemExit(f"chunk {chunk_index}: source sha mismatch")
        if rows[0]["row_id"] != chunk["first_row_id"] or rows[-1]["row_id"] != chunk["last_row_id"]:
            raise SystemExit(f"chunk {chunk_index}: row range mismatch")

        compact_rows = [compact(r) for r in rows]
        shard_entries = []
        chunk_dir = OUT_ROOT / f"chunk_{chunk_index:03d}"
        for offset in range(0, len(compact_rows), SHARD_SIZE):
            part = compact_rows[offset : offset + SHARD_SIZE]
            shard_no = offset // SHARD_SIZE + 1
            rel = Path("docs/issue70/data/source_shards") / f"chunk_{chunk_index:03d}" / f"shard_{shard_no:02d}.csv"
            out = ROOT / rel
            write_csv(out, part)
            shard_entries.append({
                "shard_index": shard_no,
                "path": rel.as_posix(),
                "row_count": len(part),
                "first_row_id": part[0]["row_id"],
                "last_row_id": part[-1]["row_id"],
                "sha256": sha256(out),
            })

        chunk_manifest = {
            "format_version": 1,
            "issue": 70,
            "chunk_index": chunk_index,
            "source_file": chunk["file"],
            "source_sha256": chunk["sha256"],
            "row_count": len(rows),
            "first_row_id": rows[0]["row_id"],
            "last_row_id": rows[-1]["row_id"],
            "shard_size": SHARD_SIZE,
            "shards": shard_entries,
        }
        chunk_manifest_path = chunk_dir / "manifest.json"
        write_json(chunk_manifest_path, chunk_manifest)

        shard_manifest["chunks"].append({
            "chunk_index": chunk_index,
            "manifest": str(chunk_manifest_path.relative_to(ROOT)).replace("\\", "/"),
            "source_file": chunk["file"],
            "source_sha256": chunk["sha256"],
            "row_count": len(rows),
            "first_row_id": rows[0]["row_id"],
            "last_row_id": rows[-1]["row_id"],
        })
        total_rows += len(rows)

    if total_rows != 92739:
        raise SystemExit(f"total rows {total_rows} != 92739")

    write_json(OUT_MANIFEST, shard_manifest)

    completed = [int(c["chunk_index"]) for c in queue["chunks"] if c.get("state") == "COMPLETED"]
    completed_rows = sum(int(c["row_count"]) for c in queue["chunks"] if c.get("state") == "COMPLETED")
    bootstrap = {
        "format_version": 2,
        "issue": 70,
        "source_manifest_sha256": sha256(MANIFEST_PATH),
        "source_shards_manifest_sha256": sha256(OUT_MANIFEST),
        "queue_state_sha256_at_generation": sha256(QUEUE_PATH),
        "completed_chunks_at_generation": completed,
        "completed_rows_at_generation": completed_rows,
        "total_rows": 92739,
        "chunk_count": len(chunks),
        "claim_protocol": "per_chunk_create_file",
        "claim_directory": "docs/issue70/data/automation_claims",
        "result_directory": "docs/issue70/data/results/queue",
        "chunk_manifest_pattern": "docs/issue70/data/source_shards/chunk_{chunk_index:03d}/manifest.json",
    }
    write_json(BOOTSTRAP_PATH, bootstrap)

    if completed_rows != 10500:
        raise SystemExit(f"bootstrap completed rows changed unexpectedly: {completed_rows}")
    if len(completed) != 21:
        raise SystemExit(f"bootstrap completed chunk count changed unexpectedly: {len(completed)}")

    print(f"generated compact shards + per-chunk manifests for {len(chunks)} chunks / {total_rows} rows")
    print(f"bootstrap completed: {len(completed)} chunks / {completed_rows} rows")


if __name__ == "__main__":
    main()
