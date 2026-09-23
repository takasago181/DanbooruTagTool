from __future__ import annotations

import sys
import json
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/issue180"))
from _issue180_v3_common import evidence_id, is_valid_citation, canonical_family_candidates, safe_structural_variant_bases, safe_terminal_family_membership, select_home
import build_residual_units_v3 as residual_planner


class EvidenceDrivenV3Tests(unittest.TestCase):
    def test_terminal_review_is_bound_to_exact_member_set_and_issue179_unknown(self):
        tag = "curakuru_(character)"
        row = {
            "unit_id": "ru3-test", "member_ids_sha256": residual_planner.member_hash([tag]),
            "terminal_status": "IDENTITY_BLOCKED", "authority_source": "docs/issue180/evidence/ISSUE179_ORIGIN_HANDOFF_V1.csv",
            "source_claim": "Issue179 explicitly records this exact Character as UNKNOWN; no HOME is inferred.",
            "review_provenance": "I70-018786 handoff row inspected; unresolved identity preserved.",
        }
        unit = {"unit_id": "ru3-test", "member_ids/tags": json.dumps([tag]), "status": "OPEN"}
        original_read_csv = residual_planner.read_csv
        with patch.object(residual_planner, "read_csv", side_effect=lambda path: [row] if path == residual_planner.REVIEWS else original_read_csv(path)):
            residual_planner.apply_terminal_reviews([unit])
        self.assertEqual(unit["status"], "IDENTITY_BLOCKED")

    def test_terminal_review_rejects_stale_member_set(self):
        tag = "curakuru_(character)"
        row = {
            "unit_id": "ru3-test", "member_ids_sha256": "stale",
            "terminal_status": "IDENTITY_BLOCKED", "authority_source": "docs/issue180/evidence/ISSUE179_ORIGIN_HANDOFF_V1.csv",
            "source_claim": "Issue179 explicitly records this exact Character as UNKNOWN; no HOME is inferred.",
            "review_provenance": "I70-018786 handoff row inspected; unresolved identity preserved.",
        }
        unit = {"unit_id": "ru3-test", "member_ids/tags": json.dumps([tag]), "status": "OPEN"}
        original_read_csv = residual_planner.read_csv
        with patch.object(residual_planner, "read_csv", side_effect=lambda path: [row] if path == residual_planner.REVIEWS else original_read_csv(path)), \
             self.assertRaises(SystemExit):
            residual_planner.apply_terminal_reviews([unit])

    def test_superseded_terminal_review_is_retained_without_applying_to_new_unit(self):
        row = {
            "unit_id": "ru3-old", "member_ids_sha256": "prior-fingerprint",
            "terminal_status": "SUPERSEDED_BY_NEW_UNIT", "authority_source": "docs/issue180/v3/research_unit_review_notes_v3.csv",
            "source_claim": "A changed residual member set is represented by a new deterministic unit identifier.",
            "review_provenance": "Retain prior accounting; regenerate and review the new unit fingerprint.",
        }
        unit = {"unit_id": "ru3-new", "member_ids/tags": json.dumps(["curakuru_(character)"]), "status": "OPEN"}
        original_read_csv = residual_planner.read_csv
        with patch.object(residual_planner, "read_csv", side_effect=lambda path: [row] if path == residual_planner.REVIEWS else original_read_csv(path)):
            residual_planner.apply_terminal_reviews([unit])
        self.assertEqual(unit["status"], "OPEN")

    def test_superseded_terminal_review_requires_provenance(self):
        row = {
            "unit_id": "ru3-old", "member_ids_sha256": "prior-fingerprint",
            "terminal_status": "SUPERSEDED_BY_NEW_UNIT", "authority_source": "unknown.csv",
            "source_claim": "A changed residual member set is represented by a new deterministic unit identifier.",
            "review_provenance": "Retain prior accounting; regenerate and review the new unit fingerprint.",
        }
        original_read_csv = residual_planner.read_csv
        with patch.object(residual_planner, "read_csv", side_effect=lambda path: [row] if path == residual_planner.REVIEWS else original_read_csv(path)), \
             self.assertRaises(SystemExit):
            residual_planner.apply_terminal_reviews([])

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

    def test_safe_structural_variant_accepts_known_costume_and_exact_reviewed_outer_family(self):
        policy = {"variant_qualifier_families": ["bunny"], "attribute_families": [],
                  "broad_families": [], "non_home_families": []}
        keys = {"akane_(bunny)_(blue_archive)", "akane_(blue_archive)"}
        result = safe_structural_variant_bases("akane_(bunny)_(blue_archive)", keys, {"blue_archive": {"blue_archive"}}, policy)
        self.assertEqual(result, [("akane_(blue_archive)", "bunny", "blue_archive")])

    def test_safe_structural_variant_supports_variant_qualifier_outermost(self):
        policy = {"variant_qualifier_families": ["swimsuit"], "attribute_families": [],
                  "broad_families": [], "non_home_families": []}
        keys = {"akashi_(kancolle)_(swimsuit)", "akashi_(kancolle)"}
        result = safe_structural_variant_bases("akashi_(kancolle)_(swimsuit)", keys, {"kancolle": {"kantai_collection"}}, policy)
        self.assertEqual(result, [("akashi_(kancolle)", "swimsuit", "kancolle")])

    def test_safe_structural_variant_rejects_unreviewed_or_blocked_family(self):
        policy = {"variant_qualifier_families": ["bunny"], "attribute_families": [],
                  "broad_families": ["blue_archive"], "non_home_families": []}
        keys = {"akane_(bunny)_(blue_archive)", "akane_(blue_archive)"}
        self.assertEqual(safe_structural_variant_bases("akane_(bunny)_(blue_archive)", keys, {"blue_archive": {"blue_archive"}}, policy), [])

    def test_structural_variant_accepts_unlisted_variant_label_only_with_catalog_root_and_exact_base(self):
        policy = {"variant_qualifier_families": [], "attribute_families": [],
                  "broad_families": [], "non_home_families": []}
        keys = {"callie_(grand_festival)_(splatoon)", "callie_(splatoon)"}
        aliases = {"splatoon": {"splatoon_(series)"}}
        result = safe_structural_variant_bases("callie_(grand_festival)_(splatoon)", keys, {}, policy, aliases)
        self.assertEqual(result, [("callie_(splatoon)", "grand_festival", "splatoon")])

    def test_structural_variant_rejects_outer_alias_collision_and_crossover_labels(self):
        policy = {"variant_qualifier_families": [], "attribute_families": [],
                  "broad_families": [], "non_home_families": []}
        keys = {"foo_(crossover)_(pokemon)", "foo_(pokemon)"}
        aliases = {"pokemon": {"pokemon"}}
        self.assertEqual(safe_structural_variant_bases("foo_(crossover)_(pokemon)", keys, {}, policy, aliases), [])

    def test_exact_terminal_work_qualifier_allows_nested_variant_label(self):
        policy = {"variant_qualifier_families": ["bunny"], "attribute_families": [],
                  "broad_families": [], "non_home_families": []}
        homes = {"blue_archive": {"blue_archive"}}
        self.assertTrue(safe_terminal_family_membership("akane_(bunny)_(blue_archive)", "blue_archive", homes, policy))

    def test_exact_terminal_family_rejects_known_cross_family_collision(self):
        policy = {"variant_qualifier_families": [], "attribute_families": [],
                  "broad_families": [], "non_home_families": []}
        homes = {"pokemon": {"pokemon"}, "fate": {"fate_(series)"}}
        self.assertFalse(safe_terminal_family_membership("crossover_(fate)_(pokemon)", "pokemon", homes, policy))

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
