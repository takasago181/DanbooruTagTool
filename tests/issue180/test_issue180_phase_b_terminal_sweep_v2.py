from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path

from scripts.issue180.terminalize_phase_b_unresolved_v2 import read, REVIEWS, SWEEP_AUDIT

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "docs/issue180/v3/reports/MIGRATION_GATE_SUMMARY_V3.json"


class PhaseBTerminalSweepTests(unittest.TestCase):
    def test_persisted_reviews_cover_every_current_unit_and_open_is_zero(self) -> None:
        gate = json.loads(GATE.read_text(encoding="utf-8"))
        self.assertEqual(gate["character_population"], 35890)
        self.assertEqual(gate["open_research_units"], 0)
        self.assertEqual(gate["pipeline_validation"], "PASS")
        reviews = read(REVIEWS)
        by_id = {row["unit_id"]: row for row in reviews}
        self.assertEqual(len(by_id), len(reviews))
        counts = Counter(row["terminal_status"] for row in reviews)
        self.assertEqual(counts["NO_SAFE_EVIDENCE"], 4282)
        self.assertEqual(counts["PARTIALLY_RESOLVED"], 12)
        self.assertEqual(counts["POLICY_BLOCKED"], 75)
        self.assertEqual(counts["IDENTITY_BLOCKED"], 7)
        unresolved_high_yield = {
            "ru3-5a64e861ef4dcfd2c9cb",
            "ru3-5a7d65cbb3bb62d11093",
            "ru3-674fb4829ec5a74bb8a3",
            "ru3-b5955ec185bea7e55cfc",
            "ru3-eaace9542f0bc17d2fc5",
        }
        self.assertTrue(all(by_id[unit_id]["terminal_status"] == "PARTIALLY_RESOLVED" for unit_id in unresolved_high_yield))
        sweep = read(SWEEP_AUDIT)
        self.assertEqual(len(sweep), 4279)
        self.assertEqual({row["unit_id"] for row in sweep}, {
            row["unit_id"] for row in reviews
            if row["review_provenance"].startswith("Phase B terminal sweep;")
        })
        for row in sweep:
            self.assertEqual(len(row["member_ids_sha256"]), 64)
            self.assertEqual(row["member_ids_sha256"], by_id[row["unit_id"]]["member_ids_sha256"])
            self.assertGreaterEqual(len(row["source_claim"]), 40)


if __name__ == "__main__":
    unittest.main()
