#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/issue132"))

from codex_runtime_guards import (  # noqa: E402
    allowed_forward_end,
    effective_start,
    load_authority_and_qa,
    policy_trace_required,
    validate_policy_trace,
)


class CodexRuntimeGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.authority, cls.qa, cls.errors = load_authority_and_qa(ROOT)

    def test_authority_and_policy_files_match(self):
        self.assertEqual(self.errors, [])

    def test_effective_boundaries(self):
        self.assertEqual(effective_start(self.authority, 1), 1126)
        self.assertEqual(effective_start(self.authority, 2), 1226)
        self.assertEqual(effective_start(self.authority, 3), 1201)
        self.assertFalse(policy_trace_required(self.authority, 1, 1101, 1125))
        self.assertTrue(policy_trace_required(self.authority, 1, 1126, 1150))
        with self.assertRaises(ValueError):
            policy_trace_required(self.authority, 1, 1125, 1149)

    def test_qa_watermarks(self):
        self.assertEqual(allowed_forward_end(self.qa, 1), 1225)
        self.assertEqual(allowed_forward_end(self.qa, 2), 1325)
        self.assertEqual(allowed_forward_end(self.qa, 3), 1300)

    def test_valid_policy_trace(self):
        guard = self.authority["contracts"]["semantic_guardrails"]
        policy_id = guard["current_policy_id"]
        policy_blob = guard["allowed_policies"][policy_id]["git_blob_sha"]
        obj = {
            "semantic_policy_id": policy_id,
            "semantic_policy_git_blob_sha": policy_blob,
            "decision_reason_codes": {
                "1126": ["OTHER_DIRECT_VISUAL"],
                "1127": ["CLOTHING_STATE"],
            },
        }
        self.assertEqual(
            validate_policy_trace(obj, self.authority, 1, 1126, 1127, {1126, 1127}),
            [],
        )

    def test_invalid_reason_code_rejected(self):
        guard = self.authority["contracts"]["semantic_guardrails"]
        policy_id = guard["current_policy_id"]
        policy_blob = guard["allowed_policies"][policy_id]["git_blob_sha"]
        obj = {
            "semantic_policy_id": policy_id,
            "semantic_policy_git_blob_sha": policy_blob,
            "decision_reason_codes": {"1126": ["NOT_A_REAL_CODE"]},
        }
        errors = validate_policy_trace(obj, self.authority, 1, 1126, 1126, {1126})
        self.assertTrue(any("invalid codes" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
