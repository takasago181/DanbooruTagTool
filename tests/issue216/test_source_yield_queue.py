from __future__ import annotations

import unittest

from scripts.issue216.build_source_yield_queue import add_open_membership_routes, queue_priority_key


class SourceYieldQueueTests(unittest.TestCase):
    def test_existing_membership_routes_only_open_exact_members(self):
        routes = {"hint_root": {"open_character"}}
        existing_members = {
            "terminal_only_root": {"already_terminal"},
            "open_member_root": {"open_character", "already_terminal"},
        }

        result = add_open_membership_routes(routes, existing_members, {"open_character"})

        self.assertEqual(result, {
            "hint_root": {"open_character"},
            "open_member_root": {"open_character"},
        })
        self.assertNotIn("terminal_only_root", result)

    def test_no_open_routes_returns_empty_root_map(self):
        result = add_open_membership_routes({}, {"terminal_only_root": {"done"}}, set())
        self.assertEqual(result, {})

    def test_exact_reuse_precedes_roster_review_and_discovery(self):
        def row(root, source_class, safe_yield, unresolved):
            return {
                "candidate_root": root,
                "source_yield_class": source_class,
                "expected_safe_yield": str(safe_yield),
                "remaining_unmapped_count": str(unresolved),
                "reusable_accepted_source_count": "1",
                "known_official_source_count": "1",
                "top500_count": "0",
                "top2000_count": "",
                "total_post_count_sum": "",
            }

        exact = row("exact", "REUSE_SOURCE_EXACT_CANDIDATES", 2, 2)
        roster = row("roster", "REVIEW_REGISTERED_SOURCE_SCOPE", 0, 100)
        discovery = row("discovery", "DISCOVER_OFFICIAL_SOURCE", 0, 1000)
        self.assertLess(queue_priority_key(exact), queue_priority_key(roster))
        self.assertLess(queue_priority_key(roster), queue_priority_key(discovery))

    def test_post_count_unknown_is_a_valid_priority_input(self):
        row = {
            "candidate_root": "root",
            "source_yield_class": "REVIEW_REGISTERED_SOURCE_SCOPE",
            "expected_safe_yield": "0",
            "remaining_unmapped_count": "50",
            "reusable_accepted_source_count": "1",
            "known_official_source_count": "2",
            "top500_count": "0",
            "top2000_count": "",
            "total_post_count_sum": "",
        }
        self.assertEqual(queue_priority_key(row)[-1], "root")


if __name__ == "__main__":
    unittest.main()
