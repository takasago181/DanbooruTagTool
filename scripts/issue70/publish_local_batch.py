#!/usr/bin/env python3
from __future__ import annotations

import base64
import csv
import gzip
import hashlib
import json
import sys
from pathlib import Path

RESULT_FIELDS = [
    "row_id",
    "canonical_tag",
    "category",
    "display_ja",
    "search_ja",
    "translation_status",
    "translation_note",
]
VALID_STATUSES = {"ACCEPTED_AI", "REVIEW_REQUIRED"}
PAYLOAD_ROOT = Path("docs/issue70/data/local_batch_payloads")


def load_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def source_for_result(repo: Path, rows):
    manifest = json.loads((repo / "docs/issue70/data/source_chunks_manifest.json").read_text(encoding="utf-8"))
    first = rows[0]["row_id"]
    for entry in manifest["chunks"]:
        if entry["first_row_id"] == first:
            p = repo / entry["file"]
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            if h != entry["sha256"]:
                raise SystemExit(f"source sha mismatch for {entry['chunk_index']}")
            return entry, p
    raise SystemExit(f"no source chunk for {first}")


def validate_result(repo: Path, path: Path):
    fields, rows = load_csv(path)
    if fields != RESULT_FIELDS:
        raise SystemExit(f"bad result fields: {path}: {fields}")
    if not rows:
        raise SystemExit(f"empty result: {path}")
    entry, source_path = source_for_result(repo, rows)
    _, source = load_csv(source_path)
    if len(rows) != entry["row_count"] or len(rows) != len(source):
        raise SystemExit(f"row count mismatch: {path}")
    src_ids = [(r["row_id"], r["canonical_tag"], r["category"]) for r in source]
    out_ids = [(r["row_id"], r["canonical_tag"], r["category"]) for r in rows]
    if src_ids != out_ids:
        raise SystemExit(f"identity/order mismatch: {path}")
    if len({r["row_id"] for r in rows}) != len(rows):
        raise SystemExit(f"duplicate row_id: {path}")
    if len({r["canonical_tag"] for r in rows}) != len(rows):
        raise SystemExit(f"duplicate canonical_tag: {path}")
    for i, r in enumerate(rows, 1):
        if r["translation_status"] not in VALID_STATUSES:
            raise SystemExit(f"bad status {path}:{i}")
        if not r["display_ja"].strip():
            raise SystemExit(f"empty display_ja {path}:{i}")
    return entry, rows


def read_encoded_payload(repo: Path, item: dict) -> bytes:
    if "gzip_base64" in item:
        encoded = item["gzip_base64"]
    else:
        parts = item.get("gzip_base64_parts")
        if not isinstance(parts, list) or not parts:
            raise SystemExit("payload item has neither gzip_base64 nor gzip_base64_parts")
        chunks = []
        for rel in parts:
            part = Path(rel)
            try:
                part.relative_to(PAYLOAD_ROOT)
            except ValueError:
                raise SystemExit(f"illegal payload part path: {part}")
            chunks.append((repo / part).read_text(encoding="ascii").strip())
        encoded = "".join(chunks)
    raw = gzip.decompress(base64.b64decode(encoded))
    expected = item.get("sha256")
    if expected and hashlib.sha256(raw).hexdigest() != expected:
        raise SystemExit(f"payload sha256 mismatch for {item.get('path')}")
    return raw


def referenced_parts(payload: dict) -> list[str]:
    found = []
    for item in payload.get("files") or []:
        for rel in item.get("gzip_base64_parts") or []:
            found.append(rel)
    return found


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: publish_local_batch.py PAYLOAD.json")
    repo = Path.cwd()
    payload_path = Path(sys.argv[1])
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    files = payload.get("files")
    if not isinstance(files, list) or not files:
        raise SystemExit("payload has no files")
    written = []
    for item in files:
        rel = Path(item["path"])
        if not str(rel).startswith("docs/issue70/data/results/queue/") or rel.suffix != ".csv":
            raise SystemExit(f"illegal result path: {rel}")
        dst = repo / rel
        if dst.exists():
            raise SystemExit(f"immutable result already exists: {rel}")
        raw = read_encoded_payload(repo, item)
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(raw)
        try:
            entry, rows = validate_result(repo, dst)
        except Exception:
            dst.unlink(missing_ok=True)
            raise
        written.append((rel, entry["chunk_index"], len(rows)))
    print(json.dumps({
        "batch_id": payload.get("batch_id"),
        "written": [(str(p), c, n) for p, c, n in written],
        "payload_parts": referenced_parts(payload),
    }, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
