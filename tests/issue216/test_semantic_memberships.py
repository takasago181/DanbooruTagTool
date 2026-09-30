from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from scripts.issue216 import authority_coverage as coverage
from scripts.issue216.apply_validated_membership_batch import build_decisions
from scripts.issue216.build_validated_membership_table import build

class SemanticMembershipTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="test-semantic-memberships-")
        self.root = Path(self.temp.name)
        self.cohort_path = self.root / "cohort.csv"
        self.sources_path = self.root / "sources.csv"
        self.members_path = self.root / "members.csv"
        self.decisions_path = self.root / "decisions.csv"
        self.roots_path = self.root / "roots.csv"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write(self, path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def fixture(self, tags: list[str], roots: list[str] | None = None):
        cohort = [{"cohort_id": tag, "canonical_character": tag, "baseline_state": "HOME_UNRESOLVED", "baseline_home": ""} for tag in tags]
        decisions = [{
            "cohort_id": tag, "canonical_character": tag, "research_state": "UNRESEARCHED",
            "home_copyright": "", "authority_type": "", "source_ids": "", "source_claim": "",
            "provenance": "", "reviewed_at": "", "reason_code": "", "reason_detail": "",
            "validated_home_candidates": "",
        } for tag in tags]
        self.write(self.cohort_path, coverage.COHORT_FIELDS, cohort)
        self.write(self.sources_path, coverage.SOURCE_FIELDS, [])
        self.write(self.members_path, coverage.MEMBER_FIELDS, [])
        self.write(self.decisions_path, coverage.DECISION_FIELDS, decisions)
        self.write(self.roots_path, coverage.ROOT_FIELDS, [
            {"copyright_canonical": root, "provenance": "frozen catalog"} for root in (roots or ["series_a", "series_b"])
        ])
        return decisions

    def add_source(self, source_id: str, root: str, tags: list[str], mapping_status: str = "EXACT_COVERED") -> None:
        url = f"https://example.test/{source_id}"
        scope = f"closed curated roster {source_id}"
        expected_id = coverage.deterministic_source_id(url, "Accepted curator", scope)
        source = {
            "source_id": expected_id, "copyright_canonical": root, "source_url": url,
            "source_type": "ACCEPTED_CURATED_ROSTER", "authority_owner": "Accepted curator",
            "source_status": "ACCEPTED", "source_scope": scope, "exact_roster_available": "true",
            "reviewed_at": "2026-09-30", "source_claim": "Explicit named Character membership list",
            "provenance": "Previously reviewed, accepted curated source", "reusable": "true",
            "notes": "Closed roster scope",
        }
        sources = coverage.read_csv(self.sources_path) if self.sources_path.exists() else []
        members = coverage.read_csv(self.members_path) if self.members_path.exists() else []
        sources.append(source)
        for tag in tags:
            members.append({
                "source_id": expected_id, "canonical_character": tag, "matched_surface": tag,
                "mapping_method": "EXACT_CANONICAL", "mapping_evidence": "Exact canonical tag in explicit curated roster",
                "reviewed_at": "2026-09-30", "reviewer": "curation review", "mapping_status": mapping_status,
            })
        self.write(self.sources_path, coverage.SOURCE_FIELDS, sources)
        self.write(self.members_path, coverage.MEMBER_FIELDS, members)

    def test_accepted_curated_roster_bulk_accepts_exact_members_without_individual_sources(self) -> None:
        self.fixture(["otonashi_kotori", "character_b"])
        self.add_source("765pro-roster", "series_a", ["otonashi_kotori", "character_b"])
        rows, summary = build(self.cohort_path, self.sources_path, self.members_path,
                              self.decisions_path, self.roots_path, expected_size=2)
        self.assertEqual(summary["AUTO_ACCEPT"], 2)
        self.assertTrue(all(row["next_action"] == "AUTO_ACCEPT_MEMBERSHIP" for row in rows))
        decisions, count = build_decisions(self.cohort_path, self.sources_path, self.members_path,
                                           self.decisions_path, self.roots_path, expected_size=2)
        self.assertEqual(count, 2)
        kotori = next(row for row in decisions if row["canonical_character"] == "otonashi_kotori")
        self.assertEqual(kotori["home_copyright"], "series_a")
        self.assertIn("No Character-specific source lookup required", kotori["reason_detail"])

    def test_candidate_root_without_membership_does_not_confirm_home(self) -> None:
        self.fixture(["character_a"])
        # Candidate-root hints are deliberately not an input to membership construction.
        rows, summary = build(self.cohort_path, self.sources_path, self.members_path,
                              self.decisions_path, self.roots_path, expected_size=1)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source_id"], "")
        self.assertEqual(rows[0]["next_action"], "FAST_REVIEW")
        self.assertEqual(summary["AUTO_ACCEPT"], 0)

    def test_ambiguous_competing_tags_are_counted_as_deep_research_candidates(self) -> None:
        self.fixture(["character_a", "character_b"])
        self.add_source("ambiguous-roster", "series_a", [])
        source = coverage.read_csv(self.sources_path)[0]
        candidate_path = self.root / "SOURCE_MAPPING_CANDIDATES_TEST.csv"
        self.write(candidate_path, [
            "source_id", "source_url", "source_scope", "matched_surface", "canonical_character",
            "candidate_status", "candidate_basis", "competing_tags",
        ], [{
            "source_id": source["source_id"], "source_url": source["source_url"],
            "source_scope": source["source_scope"], "matched_surface": "shared name",
            "canonical_character": "", "candidate_status": "REVIEW_REQUIRED",
            "candidate_basis": "two exact identities", "competing_tags": "character_a|character_b",
        }])
        rows, summary = build(self.cohort_path, self.sources_path, self.members_path,
                              self.decisions_path, self.roots_path, expected_size=2,
                              candidates_dir=self.root)
        by_tag = {row["canonical_character"]: row for row in rows}
        self.assertEqual(set(by_tag), {"character_a", "character_b"})
        self.assertTrue(all(row["next_action"] == "DEEP_RESEARCH" for row in rows))
        self.assertEqual(summary["DEEP_RESEARCH"], 2)
        self.assertTrue(all(row["semantic_root"] == "" for row in rows))

    def test_competing_membership_roots_block_auto_accept(self) -> None:
        self.fixture(["character_a"])
        self.add_source("roster-a", "series_a", ["character_a"])
        self.add_source("roster-b", "series_b", ["character_a"])
        rows, summary = build(self.cohort_path, self.sources_path, self.members_path,
                              self.decisions_path, self.roots_path, expected_size=1)
        self.assertEqual(summary["AUTO_ACCEPT"], 0)
        self.assertEqual({row["next_action"] for row in rows}, {"DEEP_RESEARCH"})
        self.assertEqual({row["competing_root_count"] for row in rows}, {"2"})

    def test_fuzzy_or_ambiguous_membership_is_excluded(self) -> None:
        self.fixture(["character_a"])
        self.add_source("review-only", "series_a", ["character_a"], mapping_status="AMBIGUOUS_REVIEW")
        rows, summary = build(self.cohort_path, self.sources_path, self.members_path,
                              self.decisions_path, self.roots_path, expected_size=1)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source_id"], "")
        self.assertEqual(summary["AUTO_ACCEPT"], 0)

    def test_scope_member_outside_frozen_cohort_cannot_leak_into_membership_join(self) -> None:
        self.fixture(["character_a"])
        self.add_source("closed-roster", "series_a", ["outside_cohort_character"])
        rows, summary = build(self.cohort_path, self.sources_path, self.members_path,
                              self.decisions_path, self.roots_path, expected_size=1)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["canonical_character"], "character_a")
        self.assertEqual(rows[0]["source_id"], "")
        self.assertEqual(summary["AUTO_ACCEPT"], 0)

    def test_membership_projection_is_deterministic(self) -> None:
        self.fixture(["character_a", "character_b"])
        self.add_source("closed-roster", "series_a", ["character_a", "character_b"])
        first = build(self.cohort_path, self.sources_path, self.members_path,
                      self.decisions_path, self.roots_path, expected_size=2)
        second = build(self.cohort_path, self.sources_path, self.members_path,
                       self.decisions_path, self.roots_path, expected_size=2)
        self.assertEqual(first, second)

    def test_existing_home_is_not_replaced_by_bulk_reuse(self) -> None:
        self.fixture(["character_a"])
        self.add_source("roster", "series_a", ["character_a"])
        decisions = coverage.read_csv(self.decisions_path)
        decisions[0].update(
            research_state="HOME_CONFIRMED", home_copyright="series_a", authority_type="ACCEPTED_CURATED_ROSTER",
            source_ids=coverage.read_csv(self.sources_path)[0]["source_id"],
            source_claim="Existing HOME", provenance="Existing validated decision", reviewed_at="2026-09-30",
            reason_code="EXISTING", reason_detail="Existing decision",
        )
        self.write(self.decisions_path, coverage.DECISION_FIELDS, decisions)
        result, count = build_decisions(self.cohort_path, self.sources_path, self.members_path,
                                        self.decisions_path, self.roots_path, expected_size=1)
        self.assertEqual(count, 0)
        self.assertEqual(result[0]["source_claim"], "Existing HOME")
        self.assertEqual(result[0]["provenance"], "Existing validated decision")


if __name__ == "__main__":
    unittest.main()
