from __future__ import annotations

import unittest

from scripts.issue216.build_source_yield_queue_v2 import classify_yield, split_set


class SourceYieldQueueV2Tests(unittest.TestCase):
    def test_unknown_is_not_zero(self):
        self.assertEqual(classify_yield(
            existing_open=0, roster_open=0, reviewed_scopes=0,
            all_reviewed_complete=False, family_positive=0, roster_found=False,
            registered_roster=False, roster_likelihood=False, high_frequency=False, unresolved=100,
        ), ("UNKNOWN", 6))

    def test_frequency_routing_precedes_unknown_long_tail(self):
        self.assertEqual(classify_yield(
            existing_open=0, roster_open=0, reviewed_scopes=0,
            all_reviewed_complete=False, family_positive=0, roster_found=False,
            registered_roster=False, roster_likelihood=False, high_frequency=True, unresolved=3,
        ), ("UNKNOWN", 5))

    def test_complete_reviewed_zero_is_distinct_from_unknown(self):
        self.assertEqual(classify_yield(
            existing_open=0, roster_open=0, reviewed_scopes=1,
            all_reviewed_complete=True, family_positive=0, roster_found=True,
            registered_roster=False, roster_likelihood=True, high_frequency=True, unresolved=100,
        ), ("KNOWN_ZERO", 6))

    def test_partial_roster_absence_stays_unknown(self):
        self.assertEqual(classify_yield(
            existing_open=0, roster_open=0, reviewed_scopes=1,
            all_reviewed_complete=False, family_positive=0, roster_found=True,
            registered_roster=False, roster_likelihood=False, high_frequency=False, unresolved=100,
        ), ("UNKNOWN", 3))

    def test_measured_exact_open_overlap_outranks_estimates(self):
        measured = classify_yield(
            existing_open=0, roster_open=12, reviewed_scopes=1,
            all_reviewed_complete=False, family_positive=3, roster_found=True,
            registered_roster=False, roster_likelihood=True, high_frequency=False, unresolved=200,
        )
        estimated = classify_yield(
            existing_open=0, roster_open=0, reviewed_scopes=0,
            all_reviewed_complete=False, family_positive=3, roster_found=False,
            registered_roster=False, roster_likelihood=True, high_frequency=False, unresolved=200,
        )
        self.assertEqual(measured, ("KNOWN_POSITIVE", 1))
        self.assertEqual(estimated, ("ESTIMATED", 2))

    def test_pipe_separated_exact_member_lists(self):
        self.assertEqual(split_set("a | b | | a"), {"a", "b"})


if __name__ == "__main__":
    unittest.main()
