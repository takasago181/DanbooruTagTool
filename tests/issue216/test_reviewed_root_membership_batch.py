from __future__ import annotations

import unittest

from scripts.issue216.integrate_reviewed_root_membership_batch import (
    exact_link_target,
    is_list_or_table_row,
    source_scope_for,
    tag_slug,
)


class ReviewedRootMembershipBatchTests(unittest.TestCase):
    def test_exact_linked_subwork_heading_supplies_root_instead_of_franchise_hint(self):
        row = {
            "source_title": "list_of_love_live!_characters",
            "source_root": "love_live!",
            "proposed_home_root": "love_live!_sunshine!!",
            "section": "[[Love Live! Sunshine!!]]",
            "page_id": "246964",
        }
        review = {
            "source_root": "love_live!",
            "source_scope": "Positive direct links from the franchise Character list only.",
        }

        root, scope = source_scope_for(row, review)

        self.assertEqual(root, "love_live!_sunshine!!")
        self.assertIn("[[Love Live! Sunshine!!]]", scope)

    def test_candidate_root_without_exact_source_heading_is_rejected(self):
        row = {
            "source_title": "list_of_love_live!_characters",
            "proposed_home_root": "love_live!_school_idol_project",
            "section": "School Idol Project members",
            "page_id": "246964",
        }
        review = {"source_root": "love_live!", "source_scope": "positive direct entries"}

        with self.assertRaisesRegex(ValueError, "exact linked work heading"):
            source_scope_for(row, review)

    def test_page_root_requires_exact_root_or_exact_character_list_title(self):
        review = {"source_root": "pokemon", "source_scope": "explicit human Character lists"}
        good = {"source_title": "list_of_pokemon_characters", "proposed_home_root": "pokemon"}
        bad = {"source_title": "list_of_pokemon_games", "proposed_home_root": "pokemon"}

        self.assertEqual(source_scope_for(good, review), ("pokemon", "explicit human Character lists"))
        with self.assertRaisesRegex(ValueError, "does not exactly scope"):
            source_scope_for(bad, review)

    def test_multiple_links_are_not_reduced_to_first_link(self):
        self.assertIsNone(exact_link_target("* [[Character A]] and [[Character B]]"))

    def test_only_list_or_table_rows_are_eligible(self):
        self.assertTrue(is_list_or_table_row("* [[Character A]]"))
        self.assertTrue(is_list_or_table_row("| [[Character A]] |"))
        self.assertFalse(is_list_or_table_row("Generic prose [[Character A]]"))

    def test_identity_normalization_is_exact_case_and_space_only(self):
        self.assertEqual(tag_slug("Kamen Rider Zi-O"), "kamen_rider_zi-o")
        self.assertNotEqual(tag_slug("Kamen Rider Zi-O Alter"), "kamen_rider_zi-o")


if __name__ == "__main__":
    unittest.main()
