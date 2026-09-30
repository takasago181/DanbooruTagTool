from __future__ import annotations

import unittest

from scripts.issue216.build_source_yield_queue import add_open_membership_routes


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


if __name__ == "__main__":
    unittest.main()
