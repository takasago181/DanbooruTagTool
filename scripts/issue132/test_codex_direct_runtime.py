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
        self.assertFalse(
            self.authority["forward_persistence"]["write_requests_for_new_work"]
        )
        self.assertFalse(
            self.authority["forward_persistence"]["checkpoint_promotion"]
        )

    def test_boundaries_and_watermarks(self):
        self.assertEqual(
            {lane: direct_start(self.authority, lane) for lane in (1, 2, 3)},
            {1: 1126, 2: 1226, 3: 1201},
        )
        self.assertEqual(
            {lane: allowed_forward_end(self.qa, lane) for lane in (1, 2, 3)},
            {1: 1225, 2: 1325, 3: 1300},
        )

    def test_current_policy_is_registered(self):
        current = self.authority["semantic_contract"]["current_policy_id"]
        registered = self.authority["semantic_contract"]["allowed_policies"][current]
        self.assertEqual(current, policy_id(self.authority))
        self.assertEqual(registered["git_blob_sha"], policy_blob(self.authority))

    def _run_stage(self, start: int) -> subprocess.CompletedProcess[str]:
        decision = {
            "schema_version": "issue132-codex-decision-window-v1",
            "lane": 1,
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
                    "decision_reason_codes": ["SEARCH_BY_NAME_ONLY"],
                }
            ],
            "holds": [],
        }
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "decision.json"
            path.write_text(json.dumps(decision), encoding="utf-8")
            return subprocess.run(
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

    def test_direct_builder_accepts_first_calibration_row(self):
        result = self._run_stage(1126)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('"policy": "issue132-pass-a-semantic-contract-v2"', result.stdout)

    def test_direct_builder_rejects_beyond_qa_watermark(self):
        result = self._run_stage(1226)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exceeds ChatGPT QA watermark", result.stdout)

    def test_flat_validator_current_state(self):
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
        self.assertEqual(snapshot["frontiers"], {"1":1126, "2":1226, "3":1201})
        self.assertEqual(snapshot["fatal_contract_error_count"], 0)
        self.assertEqual(snapshot["qa_watermark_violation_count"], 0)


if __name__ == "__main__":
    unittest.main()
