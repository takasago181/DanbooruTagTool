#!/usr/bin/env python3
from __future__ import annotations

import unittest

from scripts.maintenance.validate_execution_telemetry import validate


class TelemetryTests(unittest.TestCase):
    def base(self):
        return {
            "schema_version": "execution-telemetry-v1",
            "rows_completed": 25,
            "checkpoints_created": 1,
            "researched_rows": 5,
            "unresolved_rows": 1,
            "research_batches": 2,
            "preflight_mode": "FAST",
            "full_authority_fallback": False,
            "semantic_input_rows": 300,
            "structural_validation_failures": 0,
            "stop_reason": "EXECUTION_LIMIT",
            "duration_seconds_observed": None,
        }

    def test_valid(self):
        self.assertEqual(validate(self.base()), [])

    def test_researched_cannot_exceed_rows(self):
        x = self.base()
        x["researched_rows"] = 26
        self.assertTrue(any("researched_rows" in e for e in validate(x)))

    def test_semantic_input_cannot_be_lower_than_completed(self):
        x = self.base()
        x["semantic_input_rows"] = 20
        self.assertTrue(any("semantic_input_rows" in e for e in validate(x)))


if __name__ == "__main__":
    unittest.main()
