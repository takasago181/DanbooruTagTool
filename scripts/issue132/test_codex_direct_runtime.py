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
    direct_start,
    internal_forward_limit,
    last_codex_qa,
    load_runtime,
    policy_blob,
    policy_id,
    qa_epoch_size,
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


def validator_snapshot() -> dict:
    result = subprocess.run(
        [sys.executable, "scripts/issue132/validate_flat_pass_a.py"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise AssertionError(result.stdout)
    marker = "FLAT_SNAPSHOT_JSON="
    line = next(x for x in result.stdout.splitlines() if x.startswith(marker))
    return json.loads(line[len(marker):])


class CodexAutonomousRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.authority, cls.contract, cls.qa, cls.errors = load_runtime(ROOT)

    def test_runtime_is_autonomous_and_self_consistent(self):
        self.assertEqual(self.errors, [])
        self.assertEqual(
            self.authority["schema_version"],
            "issue132-runtime-authority-v5-codex-autonomous",
        )
        self.assertEqual(self.authority["status"], "ACTIVE_CODEX_AUTONOMOUS")
        self.assertEqual(
            self.authority["qa"]["mode"],
            "AUTONOMOUS_INTERNAL_EPOCHS",
        )
        self.assertFalse(self.authority["qa"]["human_intermediate_watermarks"])
        self.assertEqual(
            self.authority["fixed"]["codex_parallel_roles"],
            ["CODEX-L1", "CODEX-L2", "CODEX-L3", "CODEX-QA-REPAIR"],
        )
        self.assertNotIn("allowed_forward_end_by_lane", self.qa)
        self.assertNotIn("last_chatgpt_semantic_qa_by_lane", self.qa)

    def test_boundaries_and_internal_limits(self):
        self.assertEqual(
            {lane: direct_start(self.authority, lane) for lane in (1, 2, 3)},
            {1: 1126, 2: 1226, 3: 1201},
        )
        self.assertEqual(qa_epoch_size(self.qa), 1000)
        for lane in (1, 2, 3):
            baseline_end = direct_start(self.authority, lane) - 1
            cursor = last_codex_qa(self.qa, lane)
            lane_length = int(self.authority["fixed"]["lane_lengths"][str(lane)])
            self.assertGreaterEqual(cursor, baseline_end)
            self.assertLessEqual(cursor, lane_length)
            if cursor < lane_length:
                self.assertEqual(
                    (cursor - baseline_end) % qa_epoch_size(self.qa),
                    0,
                )
            self.assertEqual(
                internal_forward_limit(self.authority, self.qa, lane),
                min(
                    lane_length,
                    cursor + int(self.qa["max_unqaed_per_lane"]),
                ),
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

    def test_next_batch_matches_current_frontier_without_human_gate(self):
        snapshot = validator_snapshot()
        for lane in (1, 2, 3):
            result, packet = run_json(
                ["scripts/issue132/codex_next_batch.py", "--lane", str(lane)]
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIsNotNone(packet)
            frontier = snapshot["frontiers"][str(lane)]
            if frontier is None:
                self.assertEqual(packet["status"], "LANE_COMPLETE")
            elif frontier > internal_forward_limit(self.authority, self.qa, lane):
                self.assertEqual(packet["status"], "INTERNAL_QA_GATE")
            else:
                self.assertEqual(packet["status"], "READY")
                self.assertEqual(packet["lane_local_start"], frontier)
                self.assertGreaterEqual(packet["count"], 1)
                self.assertLessEqual(packet["count"], 100)

    def test_direct_builder_accepts_current_ready_frontier(self):
        ready = None
        for lane in (1, 2, 3):
            result, packet = run_json(
                [
                    "scripts/issue132/codex_next_batch.py",
                    "--lane",
                    str(lane),
                    "--limit",
                    "1",
                ]
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            if packet and packet.get("status") == "READY":
                ready = (lane, int(packet["lane_local_start"]))
                break
        if ready is None:
            self.skipTest("all lanes at internal QA gate or complete")

        lane, start = ready
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "decision.json"
            path.write_text(json.dumps(self._decision(lane, start)), encoding="utf-8")
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
        self.assertNotIn("ChatGPT QA watermark", result.stdout)

    def test_qa_packet_reports_due_state_without_human_input(self):
        for lane in (1, 2, 3):
            result, packet = run_json(
                ["scripts/issue132/codex_qa_packet.py", "--lane", str(lane)]
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIsNotNone(packet)
            self.assertIn(
                packet["status"],
                {"NOT_DUE", "READY", "LANE_QA_COMPLETE"},
            )

    def test_flat_validator_has_no_runtime_blocker(self):
        snapshot = validator_snapshot()
        self.assertEqual(snapshot["fatal_contract_error_count"], 0)
        self.assertEqual(snapshot["internal_qa_limit_violation_count"], 0)
        self.assertEqual(snapshot["invalid_window_count"], 0)
        self.assertEqual(snapshot["duplicate_coverage_count"], 0)
        self.assertFalse(snapshot["final_chatgpt_semantic_qa_passed"])
        self.assertFalse(snapshot["complete"])


if __name__ == "__main__":
    unittest.main()
