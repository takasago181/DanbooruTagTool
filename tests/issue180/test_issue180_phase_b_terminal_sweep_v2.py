from __future__ import annotations

import json
import hashlib
import unittest
from collections import Counter

from scripts.issue180.terminalize_phase_b_unresolved_v2 import build_reviews, read, REVIEWS, SWEEP_AUDIT, UNITS


class PhaseBTerminalSweepTests(unittest.TestCase):
    def test_persisted_reviews_cover_every_current_unit_and_open_is_zero(self) -> None:
        units = {row["unit_id"]: row for row in read(UNITS)}
        open_units = [row for row in units.values() if row["status"] == "OPEN"]
        self.assertEqual(open_units, [])
        self.assertEqual(build_reviews(), [])
        reviews = read(REVIEWS)
        by_id = {row["unit_id"]: row for row in reviews if row["unit_id"] in units}
        self.assertEqual(set(by_id), set(units))
        self.assertEqual(len(by_id), sum(row["unit_id"] in units for row in reviews))
        counts = Counter(row["terminal_status"] for row in by_id.values())
        self.assertEqual(counts, {
            "NO_SAFE_EVIDENCE": 4282,
            "PARTIALLY_RESOLVED": 12,
            "POLICY_BLOCKED": 75,
            "IDENTITY_BLOCKED": 7,
        })
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
        for unit_id, unit in units.items():
            row = by_id[unit_id]
            tags = json.loads(unit["member_ids/tags"])
            expected_hash = hashlib.sha256("\n".join(sorted(tags)).encode("utf-8")).hexdigest()
            self.assertEqual(row["member_ids_sha256"], expected_hash)
            self.assertGreaterEqual(len(row["source_claim"]), 40)


if __name__ == "__main__":
    unittest.main()
