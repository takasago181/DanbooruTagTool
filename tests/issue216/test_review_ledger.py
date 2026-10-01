from __future__ import annotations

import csv
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COHORT_PATH = ROOT / "docs/issue216/TOP500_COHORT_V1.csv"
LEDGER_PATH = ROOT / "docs/issue216/HIGH_FREQUENCY_RESCUE_LEDGER_V1.csv"
LINKAGE_PATH = ROOT / "docs/issue216/TOP500_RESEARCH_UNIT_LINKAGE_V1.csv"
BASELINE = "9c0db59c0f1dc56402c955e718a37d9de1849d7e"
MASTER_SHA256 = "135463a5225b6501db923322284f8e309f217eb5359538088eb6de6d78b77071"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


class HighFrequencyRescueLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cohort = read_csv(COHORT_PATH)
        cls.ledger = read_csv(LEDGER_PATH)
        cls.linkage = read_csv(LINKAGE_PATH)

    def test_frozen_cohort_is_500_unique_unresolved_characters(self) -> None:
        self.assertEqual(len(self.cohort), 500)
        self.assertEqual([int(r["rank"]) for r in self.cohort], list(range(1, 501)))
        self.assertEqual(len({r["canonical_character"] for r in self.cohort}), 500)
        self.assertTrue(all(r["previous_state"] == "HOME_UNRESOLVED" for r in self.cohort))
        metadata = (ROOT / "docs/issue216/TOP500_COHORT_V1.json").read_text(encoding="utf-8")
        self.assertIn(BASELINE, metadata)
        self.assertIn(MASTER_SHA256, metadata)

    def test_ledger_exactly_covers_frozen_cohort_and_keeps_baseline_separate(self) -> None:
        self.assertEqual(len(self.ledger), 500)
        self.assertEqual(
            [(r["rank"], r["canonical_character"]) for r in self.ledger],
            [(r["rank"], r["canonical_character"]) for r in self.cohort],
        )
        for row in self.ledger:
            self.assertEqual(row["baseline_state"], "HOME_UNRESOLVED")
            if row["audit_disposition"] == "PROPOSED_HOME_CONFIRMED":
                self.assertTrue(row["proposed_home"])
                self.assertTrue(row["source_url"].startswith("https://"))
                self.assertTrue(row["source_claim"])
                self.assertEqual(row["review_status"], "EXACT_MEMBER_SOURCE_CHECKED")
            else:
                self.assertEqual(row["proposed_home"], "")
                self.assertIn(row["audit_disposition"], {"REMAINS_HOME_UNRESOLVED"})

    def test_rank_101_to_500_distinguishes_checked_from_unresearched(self) -> None:
        rows = [r for r in self.ledger if 101 <= int(r["rank"]) <= 500]
        self.assertEqual(len(rows), 400)
        for row in rows:
            if row["review_status"] == "EXACT_MEMBER_SOURCE_CHECKED":
                self.assertEqual(row["audit_lane"], "HIGH_FREQUENCY_SOURCE_CHECK")
            else:
                self.assertEqual(row["review_status"], "NOT_EXTERNALLY_RESEARCHED")
                self.assertEqual(row["audit_disposition"], "REMAINS_HOME_UNRESOLVED")

    def test_linkage_fingerprints_are_exact_sha256_values(self) -> None:
        expected = {(r["rank"], r["canonical_character"]) for r in self.cohort}
        linked = {(r["rank"], r["canonical_character"]) for r in self.linkage}
        self.assertEqual(linked, expected)
        for row in self.linkage:
            if row["unit_id"]:
                self.assertRegex(row["member_ids_sha256"], re.compile(r"^[0-9a-f]{64}$"))
                self.assertTrue(row["terminal_status"])
            else:
                self.assertEqual(row["member_ids_sha256"], "")
                self.assertEqual(row["terminal_status"], "")


if __name__ == "__main__":
    unittest.main()
