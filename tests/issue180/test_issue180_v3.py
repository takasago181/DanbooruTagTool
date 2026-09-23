from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/issue180"))
from _issue180_v3_common import evidence_id, is_valid_citation, canonical_family_candidates, select_home


class EvidenceDrivenV3Tests(unittest.TestCase):
    def test_evidence_id_is_stable_and_provenance_independent(self):
        a = evidence_id("Character", "pikachu", "DIRECT_HOME", "pokemon", "OFFICIAL", "https://example.test/pikachu", "Official page names Pikachu.")
        b = evidence_id("Character", "pikachu", "DIRECT_HOME", "pokemon", "OFFICIAL", "https://example.test/pikachu", "Official page names Pikachu.")
        self.assertEqual(a, b)
        self.assertTrue(a.startswith("ev3-"))

    def test_candidate_qualifier_never_marks_membership_validated(self):
        edges = canonical_family_candidates([{"canonical_tag": "pikachu_(pokemon)"}])
        self.assertEqual(len(edges), 1)
        self.assertEqual(edges[0]["relation_type"], "MEMBER_OF")
        self.assertEqual(edges[0]["review_state"], "CANDIDATE")
        self.assertEqual(edges[0]["evidence_id"], "")

    def test_decision_without_grounded_url_is_not_evidence(self):
        self.assertFalse(is_valid_citation("", "Reviewed reusable qualifier-family authority"))
        self.assertFalse(is_valid_citation("https://example.test", "too short"))
        self.assertTrue(is_valid_citation("https://example.test/source", "A sufficiently detailed grounded claim from source."))

    def test_same_home_paths_corroborate_with_deterministic_direct_precedence(self):
        paths = [
            {"home": "pokemon", "kind": "VARIANT_INHERITANCE", "evidence_ids": ["v"]},
            {"home": "pokemon", "kind": "DIRECT_HOME", "evidence_ids": ["d"]},
        ]
        home, homes, ordered = select_home(paths)
        self.assertEqual(home, "pokemon")
        self.assertEqual(homes, ["pokemon"])
        self.assertEqual(ordered[0]["kind"], "DIRECT_HOME")
        self.assertEqual(len(ordered), 2)

    def test_different_home_paths_are_not_scored_or_selected(self):
        paths = [
            {"home": "pokemon", "kind": "DIRECT_HOME", "evidence_ids": ["a"]},
            {"home": "vocaloid", "kind": "FAMILY_HOME", "evidence_ids": ["b"]},
        ]
        home, homes, ordered = select_home(paths)
        self.assertEqual(home, "")
        self.assertEqual(homes, ["pokemon", "vocaloid"])
        self.assertEqual(ordered, [])


if __name__ == "__main__":
    unittest.main()
