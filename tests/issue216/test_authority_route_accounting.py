from __future__ import annotations

import unittest

from scripts.issue216.build_character_authority_route_accounting import roster_route_state


class AuthorityRouteAccountingTests(unittest.TestCase):
    def test_exact_roster_member_is_positive_in_that_scope(self) -> None:
        state, _ = roster_route_state("character_a", {
            "exact_cohort_members": "character_a|character_b",
            "review_state": "SCOUTED",
            "completeness": "PARTIAL",
        })
        self.assertEqual(state, "POSITIVE")

    def test_complete_roster_absence_exhausts_only_its_exact_route(self) -> None:
        state, reason = roster_route_state("character_c", {
            "exact_cohort_members": "character_a|character_b",
            "review_state": "SCOUTED",
            "completeness": "COMPLETE",
        })
        self.assertEqual(state, "NEGATIVE_COMPLETE")
        self.assertIn("only this source route", reason)

    def test_partial_or_unreviewed_roster_absence_is_not_negative(self) -> None:
        for scope in (
            {"review_state": "SCOUTED", "completeness": "PARTIAL"},
            {"review_state": "SCOUTED", "completeness": "UNKNOWN"},
            {"review_state": "REGISTRY_REJOIN", "completeness": "COMPLETE"},
        ):
            with self.subTest(scope=scope):
                state, _ = roster_route_state("character_c", scope)
                self.assertEqual(state, "UNCHECKED")


if __name__ == "__main__":
    unittest.main()
