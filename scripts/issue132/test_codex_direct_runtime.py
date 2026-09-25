#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/issue132"))

from codex_runtime import (  # noqa: E402
    allowed_forward_end,
    direct_start,
    load_runtime,
    policy_blob,
    policy_id,
)


def run_json(args: list[str]) -> tuple[subprocess.CompletedProcess[str], dict | None]:
    result = subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )
    try:
        obj = json.loads(result.stdout)
    except Exception:
        obj = None
    return result, obj


class CodexDirectRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.authority, cls.contract, cls.qa, cls.errors = load_runtime(ROOT)

    def test_runtime_is_self_consistent(self):
        self.assertEqual(self.errors, [])
        self.assertEqual(
            self.authority["schema_version"],
            "issue132-runtime-authority-v4-codex-direct",
        )
        self.assertEqual(
            self.authority["forward_persistence"]["mode"],
            "DIRECT_CANONICAL_STAGING",
        )
        self.assertEqual(
            self.authority["forward_persistence"]["next_batch_helper"],
            "scripts/issue132/codex_next_batch.py",
        )
        self.assertFalse(
            self.authority["forward_persistence"]["write_requests_for_new_work"]
        )
        self.assertFalse(
            self.authority["forward_persistence"]["checkpoint_promotion"]
        )
        self.assertFalse(
            self.authority["historical_compatibility"]["active_runtime_reads_old_history"]
        )

    def test_boundaries_and_watermarks(self):
        self.assertEqual(
            {lane: direct_start(self.authority, lane) for lane in (1, 2, 3)},
            {1: 1126, 2: 1226, 3: 1201},
        )
        for lane in (1, 2, 3):
            self.assertGreaterEqual(
                allowed_forward_end(self.qa, lane),
                direct_start(self.authority, lane) - 1,
            )

    def test_current_policy_is_registered(self):
        current = self.authority["semantic_contract"]["current_policy_id"]
        registered = self.authority["semantic_contract"]["allowed_policies"][current]
        self.assertEqual(current, policy_id(self.authority))
        self.assertEqual(registered["git_blob_sha"], policy_blob(self.authority))

    def _decision(self, lane: int, start: int) -> dict:
        return {
            "schema_version": "issue132-codex-decision-window-v1",
            "lane": lane,
            "lane_local_start": start,
            "lane_local_end": start,
            "rows": [
                {
                    "lane_local_index": start,
                    "discovery_mode": "SEARCH_ORIENTED",
                    "routes": [],
                    "local_refinement_ids": [],
                    "body_site_ids": [],
                    "theme_ids": [],
                    "route_vocabulary_gap": "NO",
                    "review_depth": "CHECKED",
                    "evidence_urls": [],
                }
            ],
            "holds": [],
        }

    def test_next_batch_matches_validator_frontier(self):
        validator = subprocess.run(
            [sys.executable, "scripts/issue132/validate_flat_pass_a.py"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(validator.returncode, 0, validator.stdout)
        marker = "FLAT_SNAPSHOT_JSON="
        line = next(x for x in validator.stdout.splitlines() if x.startswith(marker))
        snapshot = json.loads(line[len(marker):])

        for lane in (1, 2, 3):
            result, packet = run_json(
                ["scripts/issue132/codex_next_batch.py", "--lane", str(lane)]
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIsNotNone(packet)
            frontier = snapshot["frontiers"][str(lane)]
            if frontier is None:
                self.assertEqual(packet["status"], "LANE_COMPLETE")
            elif frontier > allowed_forward_end(self.qa, lane):
                self.assertEqual(packet["status"], "QA_GATE")
                self.assertEqual(packet["frontier"], frontier)
            else:
                self.assertEqual(packet["status"], "READY")
                self.assertEqual(packet["lane_local_start"], frontier)
                self.assertGreaterEqual(packet["count"], 1)
                self.assertLessEqual(packet["count"], 100)
                self.assertLessEqual(
                    packet["lane_local_end"], allowed_forward_end(self.qa, lane)
                )

    def test_direct_builder_accepts_current_ready_frontier(self):
        ready = None
        for lane in (1, 2, 3):
            result, packet = run_json(
                ["scripts/issue132/codex_next_batch.py", "--lane", str(lane), "--limit", "1"]
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            if packet and packet.get("status") == "READY":
                ready = (lane, int(packet["lane_local_start"]))
                break
        if ready is None:
            self.skipTest("all lanes currently at QA gate or complete")

        lane, start = ready
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "decision.json"
            path.write_text(
                json.dumps(self._decision(lane, start)),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/issue132/codex_stage_window.py",
                    "--decisions",
                    str(path),
                    "--check-only",
                ],
                cwd=ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
            )
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_builder_rejects_beyond_each_qa_watermark(self):
        for lane in (1, 2, 3):
            beyond = allowed_forward_end(self.qa, lane) + 1
            if beyond > int(self.authority["fixed"]["lane_lengths"][str(lane)]):
                continue
            decision = self._decision(lane, beyond)
            with tempfile.TemporaryDirectory() as td:
                path = Path(td) / "decision.json"
                path.write_text(json.dumps(decision), encoding="utf-8")
                result = subprocess.run(
                    [
                        sys.executable,
                        "scripts/issue132/codex_stage_window.py",
                        "--decisions",
                        str(path),
                        "--check-only",
                    ],
                    cwd=ROOT,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("exceeds ChatGPT QA watermark", result.stdout)

    def test_flat_validator_has_no_runtime_blocker(self):
        result = subprocess.run(
            [sys.executable, "scripts/issue132/validate_flat_pass_a.py"],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        marker = "FLAT_SNAPSHOT_JSON="
        line = next(x for x in result.stdout.splitlines() if x.startswith(marker))
        snapshot = json.loads(line[len(marker):])
        self.assertEqual(snapshot["fatal_contract_error_count"], 0)
        self.assertEqual(snapshot["qa_watermark_violation_count"], 0)
        self.assertEqual(snapshot["invalid_window_count"], 0)
        self.assertEqual(snapshot["duplicate_coverage_count"], 0)
        self.assertGreaterEqual(snapshot["baseline_hold_count"], 0)
        self.assertGreaterEqual(snapshot["baseline_semantic_lint_count"], 0)


if __name__ == "__main__":
    unittest.main()
