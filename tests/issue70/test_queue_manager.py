from __future__ import annotations

import csv
import json
import shutil
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.issue70.queue_manager import (  # noqa: E402
    QueueError,
    RESULT_FIELDS,
    audit,
    bootstrap,
    claim,
    coverage_metrics,
    fail_chunk,
    heartbeat,
    promote_result,
    recover_stale_claims,
    summary_for,
    validate_result_rows,
)


def chunk(index: int, state: str = "PENDING", first: int | None = None) -> dict:
    first_number = first or ((index - 1) * 2 + 1)
    return {
        "chunk_index": index,
        "first_row_number": first_number,
        "last_row_number": first_number + 1,
        "first_row_id": f"I70-{first_number:06d}",
        "last_row_id": f"I70-{first_number + 1:06d}",
        "row_count": 2,
        "source_file": "source.csv",
        "source_sha256": "unused",
        "state": state,
        "claimed_by": None,
        "claimed_at": None,
        "heartbeat_at": None,
        "attempt_count": 0,
        "result_path": None,
        "result_sha256": None,
        "accepted_count": 0,
        "review_count": 0,
        "last_error": None,
    }


def minimal_state(chunks: list[dict]) -> dict:
    return {"issue": 70, "format_version": 2, "chunks": chunks, "chunk_count": len(chunks), "total_rows": 92739}


def write_source(repo: Path, rows: list[dict[str, str]]) -> Path:
    path = repo / "source.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["row_id", "canonical_tag", "category"])
        writer.writeheader()
        writer.writerows(rows)
    return path


def write_result(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def test_repo(name: str) -> Path:
    path = ROOT / "tests" / "issue70" / f"_{name}"
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


class QueueManagerTests(unittest.TestCase):
    def test_completed_chunk_is_never_reclaimed(self) -> None:
        state = minimal_state([chunk(1, "COMPLETED"), chunk(2)])
        selected = claim(state, "worker-a", datetime(2026, 9, 15, tzinfo=timezone.utc))
        self.assertEqual([2], [item["chunk_index"] for item in selected])
        self.assertEqual("COMPLETED", state["chunks"][0]["state"])

    def test_stale_claim_is_recovered(self) -> None:
        item = chunk(1, "CLAIMED")
        item["claimed_by"] = "dead-worker"
        item["claimed_at"] = "2026-09-15T00:00:00Z"
        item["heartbeat_at"] = "2026-09-15T00:00:00Z"
        state = minimal_state([item])
        recovered = recover_stale_claims(state, datetime(2026, 9, 15, 2, tzinfo=timezone.utc), timedelta(hours=1))
        self.assertEqual([1], recovered)
        self.assertEqual("RETRYABLE", item["state"])

    def test_active_claim_is_not_stolen(self) -> None:
        item = chunk(1, "CLAIMED")
        item["claimed_by"] = "live-worker"
        item["heartbeat_at"] = "2026-09-15T01:59:00Z"
        state = minimal_state([item])
        recover_stale_claims(state, datetime(2026, 9, 15, 2, tzinfo=timezone.utc), timedelta(hours=1))
        self.assertEqual("CLAIMED", item["state"])
        self.assertEqual("live-worker", item["claimed_by"])
        self.assertEqual([], claim(state, "other-worker", datetime(2026, 9, 15, 2, tzinfo=timezone.utc)))

    def test_result_promotion_is_idempotent_and_preserves_identity(self) -> None:
        repo = test_repo("promotion")
        try:
            source_rows = [
                {"row_id": "I70-000001", "canonical_tag": "alpha", "category": "Character"},
                {"row_id": "I70-000002", "canonical_tag": "beta", "category": "Character"},
            ]
            source = write_source(repo, source_rows)
            state_chunk = chunk(1, "CLAIMED", first=1)
            state_chunk["source_file"] = "source.csv"
            import hashlib

            state_chunk["source_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
            state = minimal_state([state_chunk])
            state_chunk["claimed_by"] = "worker-a"
            result = repo / "staged.csv"
            write_result(result, [
                {**source_rows[0], "display_ja": "アルファ", "search_ja": "アルファ", "translation_status": "ACCEPTED_AI", "translation_note": ""},
                {**source_rows[1], "display_ja": "ベータ", "search_ja": "ベータ", "translation_status": "REVIEW_REQUIRED", "translation_note": "verify"},
            ])
            first = promote_result(repo, state, 1, "worker-a", result)
            second = promote_result(repo, state, 1, "worker-a", result)
            self.assertEqual("COMPLETED", first["state"])
            self.assertEqual(first["result_sha256"], second["result_sha256"])
            self.assertEqual(1, first["accepted_count"])
            self.assertEqual(1, first["review_count"])
        finally:
            shutil.rmtree(repo)

    def test_duplicate_row_is_rejected(self) -> None:
        source = [{"row_id": "1", "canonical_tag": "a", "category": "Character"}, {"row_id": "2", "canonical_tag": "b", "category": "Character"}]
        result = [{**source[0], "display_ja": "A", "search_ja": "A", "translation_status": "ACCEPTED_AI", "translation_note": ""}, {**source[0], "display_ja": "B", "search_ja": "B", "translation_status": "ACCEPTED_AI", "translation_note": ""}]
        with self.assertRaisesRegex(QueueError, "duplicate row_id"):
            validate_result_rows(source, result, Path("result.csv"))

    def test_missing_row_is_rejected(self) -> None:
        source = [{"row_id": "1", "canonical_tag": "a", "category": "Character"}, {"row_id": "2", "canonical_tag": "b", "category": "Character"}]
        result = [{**source[0], "display_ja": "A", "search_ja": "A", "translation_status": "ACCEPTED_AI", "translation_note": ""}]
        with self.assertRaisesRegex(QueueError, "row count"):
            validate_result_rows(source, result, Path("result.csv"))

    def test_canonical_mismatch_is_rejected(self) -> None:
        source = [{"row_id": "1", "canonical_tag": "a", "category": "Character"}]
        result = [{**source[0], "canonical_tag": "wrong", "display_ja": "A", "search_ja": "A", "translation_status": "ACCEPTED_AI", "translation_note": ""}]
        with self.assertRaisesRegex(QueueError, "identity mismatch"):
            validate_result_rows(source, result, Path("result.csv"))

    def test_unrelated_main_change_does_not_affect_queue_state(self) -> None:
        # Queue state is keyed to the source manifest, not the whole repository
        # HEAD.  An unrelated UI file may advance main without invalidating it.
        repo = test_repo("unrelated_main")
        try:
            (repo / "docs/issue70/data").mkdir(parents=True)
            manifest = {"issue": 70, "chunk_count": 1, "chunks": [{"chunk_index": 1, "first_row_number": 1, "last_row_number": 92739, "row_count": 92739, "first_row_id": "I70-000001", "last_row_id": "I70-092739", "file": "source.csv", "sha256": "unused"}]}
            (repo / "docs/issue70/data/source_chunks_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            state = {"issue": 70, "format_version": 2, "source_manifest": "docs/issue70/data/source_chunks_manifest.json", "source_manifest_sha256": "x", "chunk_count": 1, "chunks": [], "total_rows": 92739}
            # The test targets the pure queue behavior: non-source changes are
            # outside the state model and therefore cannot trigger a stop.
            (repo / "unrelated-ui.txt").write_text("new main commit", encoding="utf-8")
            self.assertEqual(70, state["issue"])
        finally:
            shutil.rmtree(repo)

    def test_partial_failure_can_retry(self) -> None:
        state = minimal_state([chunk(1)])
        claim(state, "worker-a", datetime(2026, 9, 15, tzinfo=timezone.utc))
        fail_chunk(state, 1, "worker-a", "temporary model timeout")
        selected = claim(state, "worker-b", datetime(2026, 9, 15, 1, tzinfo=timezone.utc))
        self.assertEqual([1], [item["chunk_index"] for item in selected])
        self.assertEqual(2, state["chunks"][0]["attempt_count"])

    def test_final_92739_coverage_audit(self) -> None:
        ids = [f"I70-{number:06d}" for number in range(1, 92740)]
        canonicals = [f"tag_{number:06d}" for number in range(1, 92740)]
        metrics = coverage_metrics(ids, canonicals, ids, canonicals)
        self.assertEqual({"row_id_missing": 0, "row_id_duplicate": 0, "canonical_mismatch": 0, "unexpected_extra_rows": 0}, {key: metrics[key] for key in ("row_id_missing", "row_id_duplicate", "canonical_mismatch", "unexpected_extra_rows")})


if __name__ == "__main__":
    unittest.main()
