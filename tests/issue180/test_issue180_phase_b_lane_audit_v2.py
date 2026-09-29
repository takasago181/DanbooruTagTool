from __future__ import annotations

import collections
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/issue180"))
import audit_phase_b_lanes_v2 as audit


class PhaseBLaneAuditV2Tests(unittest.TestCase):
    def test_only_existing_validated_structure_is_auto_safe(self) -> None:
        self.assertEqual(
            audit.classify_lane("AUTO_RESOLVE_STRUCTURE", False, False),
            ("AUTO_SAFE", "current v3 closure has one validated structural HOME path"),
        )

    def test_accepted_source_requires_exact_member_scope_for_auto_safe(self) -> None:
        self.assertTrue(audit.exact_positive_scope_match("Exact current Character: muten_roushi", "muten_roushi"))
        self.assertFalse(audit.exact_positive_scope_match("muten_roushi is not named on this page", "muten_roushi"))
        self.assertFalse(audit.exact_positive_scope_match("Generic names muten_roushi were withheld", "muten_roushi"))

    def test_migration_and_conflict_routes_are_high_yield(self) -> None:
        self.assertEqual(audit.classify_lane("BATCH_AUTHORITY_RESEARCH", False, True)[0], "HIGH_YIELD_RESEARCH")
        self.assertEqual(audit.classify_lane("CONFLICT_REVIEW", True, False)[0], "HIGH_YIELD_RESEARCH")

    def test_candidate_only_roots_do_not_create_a_research_route(self) -> None:
        lane, _ = audit.classify_lane("BATCH_AUTHORITY_RESEARCH", False, False)
        self.assertEqual(lane, "FINAL_UNRESOLVED")

    def test_routes_from_accepted_relation_rows_are_not_repeated(self) -> None:
        routes = audit.checked_routes([{
            "campaign_key": "authority:sample",
            "campaign_fingerprint": "old-fingerprint",
            "decision": "ACCEPT_RELATIONS",
            "research_routes_json": '[{"review_url":"https://official.example/roster"}]',
        }], [])
        self.assertEqual(
            routes["authority:sample"][0]["review_url"],
            "https://official.example/roster",
        )
        self.assertEqual(
            routes["authority:sample"][0]["checked_campaign_fingerprint"],
            "old-fingerprint",
        )

    def test_accepted_source_url_is_not_scheduled_for_a_repeat(self) -> None:
        routes = audit.checked_routes([], [{
            "review_status": "ACCEPTED",
            "source_url": "https://official.example/profile",
            "source_review_id": "src-approved",
            "source_type": "OFFICIAL_CHARACTER_PROFILE",
            "campaign_keys": '["authority:sample"]',
        }])
        self.assertEqual(routes["authority:sample"][0]["url_or_query"], "https://official.example/profile")
        self.assertEqual(routes["authority:sample"][0]["source_review_id"], "src-approved")

    def test_member_audit_uses_exact_positive_scope_and_preserves_unit_fingerprint(self) -> None:
        rows = audit.build_member_audit()
        self.assertEqual(rows, [])
        self.assertEqual(
            [row for row in audit.read_csv(audit.UNITS) if row["status"] == "OPEN"],
            [],
        )

    def test_current_snapshot_is_exactly_mapped_and_fingerprint_bound(self) -> None:
        rows = audit.build_audit()
        self.assertEqual(rows, [])
        self.assertEqual(
            [row for row in audit.read_csv(audit.UNITS) if row["status"] == "OPEN"],
            [],
        )


if __name__ == "__main__":
    unittest.main()
