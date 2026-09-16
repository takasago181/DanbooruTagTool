#!/usr/bin/env python3
"""Deterministic, restart-safe queue manager for Issue #70.

The translation itself is intentionally supplied by the worker (human, Codex,
or another approved development-time tool).  This module owns the durable
identity, lease, promotion, and coverage invariants around that work.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


ISSUE = 70
DEFAULT_STATE = Path("docs/issue70/data/queue_state.json")
RESULT_FIELDS = (
    "row_id",
    "canonical_tag",
    "category",
    "display_ja",
    "search_ja",
    "translation_status",
    "translation_note",
)
SOURCE_ID_FIELDS = ("row_id", "canonical_tag", "category")
VALID_STATUSES = {"ACCEPTED_AI", "REVIEW_REQUIRED"}
TERMINAL_STATES = {"COMPLETED"}
ACTIVE_STATES = {"CLAIMED"}
RETRY_STATES = {"PENDING", "RETRYABLE"}


class QueueError(RuntimeError):
    """A safe-to-report queue or validation failure."""


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().isoformat().replace("+00:00", "Z")


def parse_time(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise QueueError(f"invalid timestamp: {value}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8-sig") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise QueueError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise QueueError(f"JSON root must be an object: {path}")
    return value


def write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class StateLock:
    """Small cross-process lock for workers sharing one checkout.

    Git push remains the cross-checkout compare-and-swap boundary; this lock
    only prevents two local worker processes from editing the same JSON file.
    """

    def __init__(self, path: Path, timeout: float = 30.0, stale_after: float = 900.0):
        self.path = path
        self.timeout = timeout
        self.stale_after = stale_after
        self._fd: int | None = None

    def __enter__(self) -> "StateLock":
        deadline = time.monotonic() + self.timeout
        self.path.parent.mkdir(parents=True, exist_ok=True)
        while True:
            try:
                self._fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(self._fd, f"pid={os.getpid()}\n".encode("ascii"))
                return self
            except FileExistsError:
                try:
                    age = time.time() - self.path.stat().st_mtime
                    if age > self.stale_after:
                        self.path.unlink()
                        continue
                except FileNotFoundError:
                    continue
                if time.monotonic() >= deadline:
                    raise QueueError(f"queue state lock is busy: {self.path}")
                time.sleep(0.05)

    def __exit__(self, *_: Any) -> None:
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass


def read_csv(path: Path) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise QueueError(f"CSV has no header: {path}")
            return [dict(row) for row in reader]
    except OSError as exc:
        raise QueueError(f"cannot read CSV {path}: {exc}") from exc


def require_fields(rows: list[dict[str, str]], fields: Iterable[str], path: Path) -> None:
    actual = set(rows[0]) if rows else set()
    missing = set(fields) - actual
    if missing:
        raise QueueError(f"{path}: missing CSV fields: {sorted(missing)}")


def validate_source_chunk(repo: Path, entry: dict[str, Any]) -> list[dict[str, str]]:
    path = repo / entry["file"]
    if not path.is_file():
        raise QueueError(f"source chunk is missing: {entry['file']}")
    actual_hash = sha256_file(path)
    if actual_hash != entry["sha256"]:
        raise QueueError(f"source hash mismatch for chunk {entry['chunk_index']}: {path}")
    rows = read_csv(path)
    require_fields(rows, SOURCE_ID_FIELDS, path)
    if len(rows) != entry["row_count"]:
        raise QueueError(f"source row count mismatch for chunk {entry['chunk_index']}")
    expected_first = entry["first_row_id"]
    expected_last = entry["last_row_id"]
    if rows[0]["row_id"] != expected_first or rows[-1]["row_id"] != expected_last:
        raise QueueError(f"source row range mismatch for chunk {entry['chunk_index']}")
    return rows


def validate_result_rows(
    source_rows: list[dict[str, str]], result_rows: list[dict[str, str]], path: Path
) -> dict[str, int]:
    actual_fields = set(result_rows[0]) if result_rows else set()
    if actual_fields != set(RESULT_FIELDS):
        missing = sorted(set(RESULT_FIELDS) - actual_fields)
        extra = sorted(actual_fields - set(RESULT_FIELDS))
        raise QueueError(f"{path}: result schema mismatch; missing={missing}, extra={extra}")
    if len(result_rows) != len(source_rows):
        raise QueueError(f"{path}: result row count {len(result_rows)} != source {len(source_rows)}")
    source_ids = [(row["row_id"], row["canonical_tag"], row["category"]) for row in source_rows]
    result_ids = [(row["row_id"], row["canonical_tag"], row["category"]) for row in result_rows]
    if len({row["row_id"] for row in result_rows}) != len(result_rows):
        raise QueueError(f"{path}: duplicate row_id")
    if len({row["canonical_tag"] for row in result_rows}) != len(result_rows):
        raise QueueError(f"{path}: duplicate canonical identity")
    if result_ids != source_ids:
        for index, (expected, actual) in enumerate(zip(source_ids, result_ids), start=1):
            if expected != actual:
                raise QueueError(f"{path}: identity mismatch at result row {index}: expected={expected}, actual={actual}")
        raise QueueError(f"{path}: result identity/order mismatch")
    counts = {"ACCEPTED_AI": 0, "REVIEW_REQUIRED": 0}
    for index, row in enumerate(result_rows, start=1):
        status = row["translation_status"].strip()
        if status not in VALID_STATUSES:
            raise QueueError(f"{path}: invalid translation_status at row {index}: {status!r}")
        if not (row.get("display_ja") or "").strip():
            raise QueueError(f"{path}: empty display_ja at row {index}")
        counts[status] += 1
    return counts


def validate_result_file(repo: Path, entry: dict[str, Any], result_path: Path) -> dict[str, int]:
    source_rows = validate_source_chunk(repo, entry)
    result_rows = read_csv(result_path)
    return validate_result_rows(source_rows, result_rows, result_path)


def manifest_entries(repo: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest_path = repo / "docs/issue70/data/source_chunks_manifest.json"
    manifest = load_json(manifest_path)
    chunks = manifest.get("chunks")
    if manifest.get("issue") not in (None, ISSUE) or not isinstance(chunks, list) or not chunks:
        raise QueueError("source_chunks_manifest.json is not a valid Issue #70 manifest")
    previous_last = 0
    normalized: list[dict[str, Any]] = []
    for expected_index, raw in enumerate(chunks, start=1):
        entry = dict(raw)
        if entry.get("chunk_index") != expected_index:
            raise QueueError(f"manifest chunk index gap at {expected_index}")
        if entry.get("first_row_number") != previous_last + 1:
            raise QueueError(f"manifest row-number gap before chunk {expected_index}")
        if entry.get("last_row_number") - entry.get("first_row_number") + 1 != entry.get("row_count"):
            raise QueueError(f"manifest row count arithmetic mismatch at chunk {expected_index}")
        previous_last = entry["last_row_number"]
        normalized.append(entry)
    if previous_last != 92739:
        raise QueueError(f"manifest total rows {previous_last} != 92739")
    return manifest, normalized


def result_candidates(repo: Path) -> list[Path]:
    root = repo / "docs/issue70/data/results"
    return sorted(root.rglob("*.csv")) if root.is_dir() else []


def discover_valid_results(repo: Path, chunks: list[dict[str, Any]]) -> dict[int, tuple[Path, dict[str, int]]]:
    by_first_id = {entry["first_row_id"]: entry for entry in chunks}
    discovered: dict[int, tuple[Path, dict[str, int]]] = {}
    seen_row_ids: dict[str, Path] = {}
    seen_canonicals: dict[str, Path] = {}
    for path in result_candidates(repo):
        rows = read_csv(path)
        if not rows:
            raise QueueError(f"result file is empty: {path}")
        entry = by_first_id.get(rows[0].get("row_id"))
        if entry is None:
            raise QueueError(f"result file does not start with a manifest row_id: {path}")
        counts = validate_result_file(repo, entry, path)
        for row in rows:
            row_id = row.get("row_id", "")
            canonical = row.get("canonical_tag", "")
            if row_id in seen_row_ids:
                raise QueueError(f"duplicate result row_id {row_id}: {seen_row_ids[row_id]} and {path}")
            if canonical in seen_canonicals:
                raise QueueError(f"duplicate result canonical_tag {canonical}: {seen_canonicals[canonical]} and {path}")
            seen_row_ids[row_id] = path
            seen_canonicals[canonical] = path
        chunk_index = entry["chunk_index"]
        if chunk_index in discovered:
            previous = discovered[chunk_index][0]
            raise QueueError(f"multiple valid result files for chunk {chunk_index}: {previous} and {path}")
        discovered[chunk_index] = (path, counts)
    return discovered


def summary_for(chunks: list[dict[str, Any]]) -> dict[str, int]:
    summary = {
        "completed_chunks": 0,
        "claimed_chunks": 0,
        "pending_chunks": 0,
        "retryable_chunks": 0,
        "failed_validation_chunks": 0,
        "completed_rows": 0,
        "accepted_count": 0,
        "review_count": 0,
        "remaining_rows": 0,
    }
    for chunk in chunks:
        state = chunk["state"]
        if state == "COMPLETED":
            summary["completed_chunks"] += 1
            summary["completed_rows"] += chunk["row_count"]
            summary["accepted_count"] += chunk.get("accepted_count", 0)
            summary["review_count"] += chunk.get("review_count", 0)
        elif state == "CLAIMED":
            summary["claimed_chunks"] += 1
            summary["remaining_rows"] += chunk["row_count"]
        elif state == "RETRYABLE":
            summary["retryable_chunks"] += 1
            summary["remaining_rows"] += chunk["row_count"]
        elif state == "FAILED_VALIDATION":
            summary["failed_validation_chunks"] += 1
            summary["remaining_rows"] += chunk["row_count"]
        else:
            summary["pending_chunks"] += 1
            summary["remaining_rows"] += chunk["row_count"]
    return summary


def bootstrap(repo: Path, state_path: Path) -> dict[str, Any]:
    if state_path.is_file():
        state = load_state(repo, state_path)
        with StateLock(state_path.with_suffix(state_path.suffix + ".lock")):
            state = load_state(repo, state_path)
            if reconcile_queue_results(repo, state):
                write_json_atomic(state_path, state)
        return state
    manifest, entries = manifest_entries(repo)
    for entry in entries:
        validate_source_chunk(repo, entry)
    discovered = discover_valid_results(repo, entries)
    chunks: list[dict[str, Any]] = []
    for entry in entries:
        index = entry["chunk_index"]
        path_and_counts = discovered.get(index)
        if path_and_counts:
            result_path, counts = path_and_counts
            state = "COMPLETED"
            result_hash = sha256_file(result_path)
            accepted = counts["ACCEPTED_AI"]
            review = counts["REVIEW_REQUIRED"]
            attempt_count = 1
        else:
            result_path = None
            result_hash = None
            state = "PENDING"
            accepted = 0
            review = 0
            attempt_count = 0
        chunks.append(
            {
                "chunk_index": index,
                "first_row_number": entry["first_row_number"],
                "last_row_number": entry["last_row_number"],
                "first_row_id": entry["first_row_id"],
                "last_row_id": entry["last_row_id"],
                "row_count": entry["row_count"],
                "source_file": entry["file"],
                "source_sha256": entry["sha256"],
                "state": state,
                "claimed_by": None,
                "claimed_at": None,
                "heartbeat_at": None,
                "attempt_count": attempt_count,
                "result_path": str(result_path.relative_to(repo)).replace("\\", "/") if result_path else None,
                "result_sha256": result_hash,
                "accepted_count": accepted,
                "review_count": review,
                "last_error": None,
            }
        )
    state: dict[str, Any] = {
        "format_version": 2,
        "issue": ISSUE,
        "queue_mode": "dynamic_claim",
        "source_manifest": "docs/issue70/data/source_chunks_manifest.json",
        "source_manifest_sha256": sha256_file(repo / "docs/issue70/data/source_chunks_manifest.json"),
        "total_rows": 92739,
        "chunk_size": 500,
        "chunk_count": len(chunks),
        "chunks": chunks,
        "bootstrap": {
            "created_at": iso_now(),
            "source_results_validated": len(discovered),
            "legacy_progress_files": [
                f"docs/issue70/data/progress_lane{lane}.json" for lane in range(1, 5)
            ] + ["docs/issue70/data/progress.json"],
            "legacy_results_preserved": True,
        },
    }
    state["summary"] = summary_for(chunks)
    write_json_atomic(state_path, state)
    return state


def load_state(repo: Path, state_path: Path) -> dict[str, Any]:
    state = load_json(state_path)
    if state.get("issue") != ISSUE or state.get("format_version") != 2:
        raise QueueError(f"unsupported queue state: {state_path}")
    manifest_path = repo / state["source_manifest"]
    if sha256_file(manifest_path) != state["source_manifest_sha256"]:
        raise QueueError("source manifest changed since queue bootstrap; refusing to continue")
    chunks = state.get("chunks")
    if not isinstance(chunks, list) or len(chunks) != state.get("chunk_count"):
        raise QueueError("queue state chunk list is invalid")
    return state


def chunk_map(state: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {int(chunk["chunk_index"]): chunk for chunk in state["chunks"]}


def queue_result_path(repo: Path, chunk: dict[str, Any]) -> Path:
    return repo / "docs/issue70/data/results/queue" / (
        f"chunk{chunk['chunk_index']:03d}_{chunk['first_row_id']}_{chunk['last_row_id']}.csv"
    )


def reconcile_queue_results(repo: Path, state: dict[str, Any]) -> bool:
    manifest, entries = manifest_entries(repo)
    del manifest
    for entry in entries:
        validate_source_chunk(repo, entry)
    discovered = discover_valid_results(repo, entries)
    by_index = chunk_map(state)
    expected_indices = {entry["chunk_index"] for entry in entries}
    if set(by_index) != expected_indices:
        raise QueueError("queue state chunk indices do not match source manifest")

    changed = False
    for entry in entries:
        chunk = by_index[entry["chunk_index"]]
        result_info = discovered.get(entry["chunk_index"])
        if result_info is None:
            if chunk["state"] == "COMPLETED":
                raise QueueError(
                    f"queue state marks chunk {entry['chunk_index']} completed but no tracked result exists"
                )
            if chunk.get("result_path") or chunk.get("result_sha256"):
                raise QueueError(
                    f"queue state has result metadata without a tracked result for chunk {entry['chunk_index']}"
                )
            continue

        result_path, counts = result_info
        result_hash = sha256_file(result_path)
        relative_path = str(result_path.relative_to(repo)).replace("\\", "/")
        desired = {
            "state": "COMPLETED",
            "claimed_by": None,
            "claimed_at": None,
            "heartbeat_at": None,
            "result_path": relative_path,
            "result_sha256": result_hash,
            "accepted_count": counts["ACCEPTED_AI"],
            "review_count": counts["REVIEW_REQUIRED"],
            "last_error": None,
        }
        if any(chunk.get(key) != value for key, value in desired.items()):
            chunk.update(desired)
            changed = True

    summary = summary_for(state["chunks"])
    if state.get("summary") != summary:
        state["summary"] = summary
        changed = True
    return changed


def recover_stale_claims(state: dict[str, Any], now: datetime, stale_after: timedelta) -> list[int]:
    recovered: list[int] = []
    cutoff = now - stale_after
    for chunk in state["chunks"]:
        if chunk["state"] != "CLAIMED":
            continue
        heartbeat = chunk.get("heartbeat_at") or chunk.get("claimed_at")
        if not heartbeat or parse_time(heartbeat) >= cutoff:
            continue
        chunk.update({
            "state": "RETRYABLE",
            "claimed_by": None,
            "claimed_at": None,
            "heartbeat_at": None,
            "last_error": f"stale claim recovered at {now.isoformat()}",
        })
        recovered.append(chunk["chunk_index"])
    if recovered:
        state["summary"] = summary_for(state["chunks"])
    return recovered


def claim(state: dict[str, Any], worker_id: str, now: datetime, count: int = 1) -> list[dict[str, Any]]:
    if not worker_id.strip():
        raise QueueError("worker_id cannot be empty")
    if count < 1:
        raise QueueError("claim count must be positive")
    claimed: list[dict[str, Any]] = []
    for chunk in sorted(state["chunks"], key=lambda item: item["chunk_index"]):
        if chunk["state"] not in RETRY_STATES:
            continue
        chunk.update({
            "state": "CLAIMED",
            "claimed_by": worker_id,
            "claimed_at": now.isoformat().replace("+00:00", "Z"),
            "heartbeat_at": now.isoformat().replace("+00:00", "Z"),
            "attempt_count": int(chunk.get("attempt_count", 0)) + 1,
            "last_error": None,
        })
        claimed.append(chunk)
        if len(claimed) == count:
            break
    state["summary"] = summary_for(state["chunks"])
    return claimed


def heartbeat(state: dict[str, Any], chunk_index: int, worker_id: str, now: datetime) -> None:
    chunk = chunk_map(state).get(chunk_index)
    if chunk is None:
        raise QueueError(f"unknown chunk: {chunk_index}")
    if chunk["state"] != "CLAIMED" or chunk.get("claimed_by") != worker_id:
        raise QueueError(f"chunk {chunk_index} is not claimed by {worker_id}")
    chunk["heartbeat_at"] = now.isoformat().replace("+00:00", "Z")


def promote_result(repo: Path, state: dict[str, Any], chunk_index: int, worker_id: str, staged: Path) -> dict[str, Any]:
    chunk = chunk_map(state).get(chunk_index)
    if chunk is None:
        raise QueueError(f"unknown chunk: {chunk_index}")
    entry = {
        "chunk_index": chunk["chunk_index"],
        "file": chunk["source_file"],
        "sha256": chunk["source_sha256"],
        "row_count": chunk["row_count"],
        "first_row_id": chunk["first_row_id"],
        "last_row_id": chunk["last_row_id"],
    }
    counts = validate_result_file(repo, entry, staged)
    result_hash = sha256_file(staged)
    final_path = queue_result_path(repo, chunk)
    if chunk["state"] == "COMPLETED":
        if chunk.get("result_sha256") == result_hash:
            return chunk
        raise QueueError(f"chunk {chunk_index} is already completed; accepted result is immutable")
    if chunk["state"] != "CLAIMED" or chunk.get("claimed_by") != worker_id:
        raise QueueError(f"chunk {chunk_index} is not claimed by {worker_id}")
    if final_path.exists():
        existing_hash = sha256_file(final_path)
        if existing_hash != result_hash:
            raise QueueError(f"final result exists with a different hash for chunk {chunk_index}")
    else:
        final_path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=f".{final_path.name}.", suffix=".tmp", dir=final_path.parent)
        os.close(fd)
        try:
            shutil.copyfile(staged, temporary)
            os.replace(temporary, final_path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    chunk.update({
        "state": "COMPLETED",
        "claimed_by": None,
        "claimed_at": None,
        "heartbeat_at": None,
        "result_path": str(final_path.relative_to(repo)).replace("\\", "/"),
        "result_sha256": result_hash,
        "accepted_count": counts["ACCEPTED_AI"],
        "review_count": counts["REVIEW_REQUIRED"],
        "last_error": None,
    })
    state["summary"] = summary_for(state["chunks"])
    return chunk


def fail_chunk(state: dict[str, Any], chunk_index: int, worker_id: str, error: str) -> None:
    chunk = chunk_map(state).get(chunk_index)
    if chunk is None:
        raise QueueError(f"unknown chunk: {chunk_index}")
    if chunk["state"] != "CLAIMED" or chunk.get("claimed_by") != worker_id:
        raise QueueError(f"chunk {chunk_index} is not claimed by {worker_id}")
    chunk.update({
        "state": "RETRYABLE",
        "claimed_by": None,
        "claimed_at": None,
        "heartbeat_at": None,
        "last_error": error[:2000] or "worker failure",
    })
    state["summary"] = summary_for(state["chunks"])


def coverage_metrics(
    expected_ids: Iterable[str],
    expected_canonicals: Iterable[str],
    result_ids: list[str],
    result_canonicals: list[str],
) -> dict[str, Any]:
    expected_id_set = set(expected_ids)
    expected_canonical_set = set(expected_canonicals)
    duplicate_ids = sorted(item for item, count in Counter(result_ids).items() if count > 1)
    duplicate_canonicals = sorted(item for item, count in Counter(result_canonicals).items() if count > 1)
    missing = sorted(expected_id_set - set(result_ids))
    unexpected = sorted(set(result_ids) - expected_id_set)
    return {
        "row_id_missing": len(missing),
        "row_id_duplicate": len(duplicate_ids),
        "canonical_mismatch": int(len(result_canonicals) != len(expected_canonical_set) or set(result_canonicals) != expected_canonical_set),
        "unexpected_extra_rows": len(unexpected),
        "missing_row_ids_sample": missing[:20],
        "duplicate_row_ids_sample": duplicate_ids[:20],
        "duplicate_canonical_sample": duplicate_canonicals[:20],
        "unexpected_row_ids_sample": unexpected[:20],
    }


def audit(repo: Path, state: dict[str, Any], write_final: bool = False) -> dict[str, Any]:
    manifest, entries = manifest_entries(repo)
    if sha256_file(repo / "docs/issue70/data/source_chunks_manifest.json") != state["source_manifest_sha256"]:
        raise QueueError("audit source manifest hash mismatch")
    by_index = chunk_map(state)
    errors: list[str] = []
    covered_rows = 0
    result_row_ids: list[str] = []
    result_canonicals: list[str] = []
    status_totals = {"ACCEPTED_AI": 0, "REVIEW_REQUIRED": 0}
    for entry in entries:
        chunk = by_index.get(entry["chunk_index"])
        if chunk is None:
            errors.append(f"missing queue chunk {entry['chunk_index']}")
            continue
        if chunk["state"] != "COMPLETED" or not chunk.get("result_path"):
            errors.append(f"chunk {entry['chunk_index']} state is {chunk['state']}")
            continue
        result_path = repo / chunk["result_path"]
        try:
            counts = validate_result_file(repo, entry, result_path)
        except QueueError as exc:
            errors.append(str(exc))
            continue
        if chunk.get("result_sha256") != sha256_file(result_path):
            errors.append(f"result hash mismatch for chunk {entry['chunk_index']}")
        if chunk.get("accepted_count") != counts["ACCEPTED_AI"] or chunk.get("review_count") != counts["REVIEW_REQUIRED"]:
            errors.append(f"status count mismatch for chunk {entry['chunk_index']}")
        rows = read_csv(result_path)
        covered_rows += len(rows)
        result_row_ids.extend(row["row_id"] for row in rows)
        result_canonicals.extend(row["canonical_tag"] for row in rows)
        for status, count in counts.items():
            status_totals[status] += count
    expected_ids = [f"I70-{number:06d}" for number in range(1, 92740)]
    expected_canonicals = [row["canonical_tag"] for entry in entries for row in read_csv(repo / entry["file"])]
    coverage = coverage_metrics(expected_ids, expected_canonicals, result_row_ids, result_canonicals)
    report: dict[str, Any] = {
        "format_version": 1,
        "issue": ISSUE,
        "source_manifest_sha256": state["source_manifest_sha256"],
        "expected_rows": 92739,
        "covered_rows": covered_rows,
        "row_id_missing": coverage["row_id_missing"],
        "row_id_duplicate": coverage["row_id_duplicate"],
        "canonical_mismatch": coverage["canonical_mismatch"],
        "unexpected_extra_rows": coverage["unexpected_extra_rows"],
        "result_schema_errors": len(errors),
        "status_totals": status_totals,
        "queue_summary": summary_for(state["chunks"]),
        "pass": not errors and not coverage["row_id_missing"] and not coverage["row_id_duplicate"] and not coverage["duplicate_canonical_sample"] and not coverage["unexpected_extra_rows"] and not coverage["canonical_mismatch"] and covered_rows == 92739,
        "errors": errors[:20],
        "missing_row_ids_sample": coverage["missing_row_ids_sample"],
        "duplicate_row_ids_sample": coverage["duplicate_row_ids_sample"],
        "duplicate_canonical_sample": coverage["duplicate_canonical_sample"],
        "unexpected_row_ids_sample": coverage["unexpected_row_ids_sample"],
    }
    if write_final:
        if not report["pass"]:
            raise QueueError("final completion marker refused because coverage audit is not PASS")
        report["completed_at"] = iso_now()
        write_json_atomic(repo / "docs/issue70/data/final_completion.json", report)
    return report


def state_path_arg(value: str | None) -> Path:
    return Path(value) if value else DEFAULT_STATE


def command(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    state_path = repo / state_path_arg(args.state)
    if args.action == "bootstrap":
        state = bootstrap(repo, state_path)
        print(json.dumps(state["summary"], ensure_ascii=False, indent=2))
        return 0
    if args.action == "status":
        state = load_state(repo, state_path)
        print(json.dumps({"source_manifest_sha256": state["source_manifest_sha256"], "summary": summary_for(state["chunks"])}, ensure_ascii=False, indent=2))
        return 0
    if args.action == "audit":
        state = load_state(repo, state_path)
        report = audit(repo, state, args.write_final)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["pass"] else 2
    with StateLock(state_path.with_suffix(state_path.suffix + ".lock")):
        state = load_state(repo, state_path)
        changed = reconcile_queue_results(repo, state)
        if args.action == "reconcile":
            if changed:
                write_json_atomic(state_path, state)
            print(json.dumps({"changed": changed, "summary": state["summary"]}, ensure_ascii=False, indent=2))
            return 0
        if args.action == "claim":
            recovered = recover_stale_claims(state, utc_now(), timedelta(seconds=args.stale_after_seconds))
            selected = claim(state, args.worker_id, utc_now(), args.count)
            state["summary"] = summary_for(state["chunks"])
            write_json_atomic(state_path, state)
            print(json.dumps({"recovered_chunk_indices": recovered, "claimed": selected, "summary": state["summary"]}, ensure_ascii=False, indent=2))
            return 0
        if args.action == "recover-stale":
            recovered = recover_stale_claims(state, utc_now(), timedelta(seconds=args.stale_after_seconds))
            state["summary"] = summary_for(state["chunks"])
            write_json_atomic(state_path, state)
            print(json.dumps({"recovered_chunk_indices": recovered, "summary": state["summary"]}, ensure_ascii=False, indent=2))
            return 0
        if args.action == "heartbeat":
            heartbeat(state, args.chunk_index, args.worker_id, utc_now())
            write_json_atomic(state_path, state)
            return 0
        if args.action == "complete":
            chunk = promote_result(repo, state, args.chunk_index, args.worker_id, Path(args.result).resolve())
            write_json_atomic(state_path, state)
            print(json.dumps(chunk, ensure_ascii=False, indent=2))
            return 0
        if args.action == "fail":
            fail_chunk(state, args.chunk_index, args.worker_id, args.error)
            write_json_atomic(state_path, state)
            return 0
        if changed:
            write_json_atomic(state_path, state)
    raise QueueError(f"unsupported action: {args.action}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="repository root")
    parser.add_argument("--state", help="queue state path relative to repository")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("bootstrap")
    sub.add_parser("status")
    audit_parser = sub.add_parser("audit")
    audit_parser.add_argument("--write-final", action="store_true")
    claim_parser = sub.add_parser("claim")
    claim_parser.add_argument("--worker-id", required=True)
    claim_parser.add_argument("--count", type=int, default=1)
    claim_parser.add_argument("--stale-after-seconds", type=int, default=21600)
    recover_parser = sub.add_parser("recover-stale")
    recover_parser.add_argument("--stale-after-seconds", type=int, default=21600)
    heartbeat_parser = sub.add_parser("heartbeat")
    heartbeat_parser.add_argument("--chunk-index", type=int, required=True)
    heartbeat_parser.add_argument("--worker-id", required=True)
    complete_parser = sub.add_parser("complete")
    complete_parser.add_argument("--chunk-index", type=int, required=True)
    complete_parser.add_argument("--worker-id", required=True)
    complete_parser.add_argument("--result", required=True)
    fail_parser = sub.add_parser("fail")
    fail_parser.add_argument("--chunk-index", type=int, required=True)
    fail_parser.add_argument("--worker-id", required=True)
    fail_parser.add_argument("--error", required=True)
    sub.add_parser("reconcile")
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        return command(build_parser().parse_args(argv))
    except QueueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
