from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from scripts.issue216 import authority_coverage as coverage

ROOT = Path(__file__).resolve().parents[2]


class AuthorityCoverageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix=".test-authority-coverage-", dir=ROOT / "docs/issue216")
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

    def fixture(self, tags: list[str]) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
        cohort = [{"cohort_id": tag, "canonical_character": tag, "baseline_state": "HOME_UNRESOLVED", "baseline_home": ""} for tag in tags]
        decisions = [{
            "cohort_id": tag, "canonical_character": tag, "research_state": "UNRESEARCHED",
            "home_copyright": "", "authority_type": "", "source_ids": "", "source_claim": "",
            "provenance": "", "reviewed_at": "", "reason_code": "", "reason_detail": "",
            "validated_home_candidates": "",
        } for tag in tags]
        return cohort, [], [], decisions

    def persist(self, cohort, sources, members, decisions) -> None:
        self.write(self.cohort_path, coverage.COHORT_FIELDS, cohort)
        self.write(self.sources_path, coverage.SOURCE_FIELDS, sources)
        self.write(self.members_path, coverage.MEMBER_FIELDS, members)
        self.write(self.decisions_path, coverage.DECISION_FIELDS, decisions)
        self.write(self.roots_path, coverage.ROOT_FIELDS,
                   [{"copyright_canonical": "series_a", "provenance": "baseline confirmed HOME root"}])

    def test_13_983_rows_accounted_but_unresearched_is_not_complete(self) -> None:
        cohort, sources, members, decisions = self.fixture([f"character_{i:05}" for i in range(coverage.BASELINE_SIZE)])
        self.persist(cohort, sources, members, decisions)
        result = coverage.validate(self.cohort_path, self.sources_path, self.members_path,
                                   self.decisions_path, coverage.BASELINE_SIZE, self.roots_path)
        self.assertEqual(result["accounted"], 13_983)
        self.assertEqual(result["unresearched"], 13_983)
        self.assertFalse(result["complete"])

    def test_unresearched_cannot_carry_terminal_fields_or_home(self) -> None:
        cohort, sources, members, decisions = self.fixture(["character_a"])
        decisions[0]["home_copyright"] = "series_a"
        self.persist(cohort, sources, members, decisions)
        with self.assertRaisesRegex(ValueError, "UNRESEARCHED row cannot have HOME"):
            coverage.validate(self.cohort_path, self.sources_path, self.members_path, self.decisions_path, 1, self.roots_path)

    def test_no_safe_evidence_requires_actual_source_research(self) -> None:
        cohort, sources, members, decisions = self.fixture(["character_a"])
        decisions[0].update(research_state="SOURCE_RESEARCHED_NO_SAFE_EVIDENCE", reviewed_at="2026-09-30",
                            provenance="review log", reason_code="NO_UNIQUE_HOME", reason_detail="two root candidates")
        self.persist(cohort, sources, members, decisions)
        with self.assertRaisesRegex(ValueError, "requires a researched source"):
            coverage.validate(self.cohort_path, self.sources_path, self.members_path, self.decisions_path, 1, self.roots_path)

    def test_post_count_is_not_an_evidence_field(self) -> None:
        self.assertNotIn("post_count", coverage.DECISION_FIELDS)
        self.assertNotIn("post_count", coverage.SOURCE_FIELDS)
        self.assertNotIn("candidate_roots", coverage.DECISION_FIELDS)

    def test_candidate_root_alone_cannot_confirm_home(self) -> None:
        cohort, sources, members, decisions = self.fixture(["character_a"])
        decisions[0].update(research_state="HOME_CONFIRMED", home_copyright="series_a", authority_type="OFFICIAL_CHARACTER_ROSTER",
                            source_claim="listed", provenance="review", reviewed_at="2026-09-30",
                            reason_code="EXACT_ROSTER", reason_detail="member listed")
        self.persist(cohort, sources, members, decisions)
        with self.assertRaisesRegex(ValueError, "HOME_CONFIRMED lacks exact reviewed member mapping"):
            coverage.validate(self.cohort_path, self.sources_path, self.members_path, self.decisions_path, 1, self.roots_path)

    def test_existing_confirmed_home_in_cohort_is_rejected(self) -> None:
        cohort, sources, members, decisions = self.fixture(["character_a"])
        cohort[0]["baseline_state"] = "HOME_CONFIRMED"
        cohort[0]["baseline_home"] = "old_root"
        self.persist(cohort, sources, members, decisions)
        with self.assertRaisesRegex(ValueError, "only frozen baseline HOME_UNRESOLVED"):
            coverage.validate(self.cohort_path, self.sources_path, self.members_path, self.decisions_path, 1, self.roots_path)

    def test_one_accepted_roster_supports_multiple_exact_members_only(self) -> None:
        tags = ["character_a", "character_b", "character_c"]
        cohort, sources, members, decisions = self.fixture(tags)
        source_id = coverage.deterministic_source_id("https://example.org/roster", "Example Publisher", "official cast list")
        sources.append({
            "source_id": source_id, "copyright_canonical": "series_a", "source_url": "https://example.org/roster",
            "source_type": "OFFICIAL_CHARACTER_ROSTER", "authority_owner": "Example Publisher", "source_status": "ACCEPTED",
            "source_scope": "official cast list", "exact_roster_available": "true", "reviewed_at": "2026-09-30",
            "source_claim": "Roster explicitly names two characters", "provenance": "reviewed official page",
            "reusable": "true", "notes": "Partial roster; absence is not evidence",
        })
        for i, tag in enumerate(tags[:2]):
            members.append({"source_id": source_id, "canonical_character": tag, "matched_surface": tag,
                            "mapping_method": "EXACT_CANONICAL", "mapping_evidence": "exact canonical identity",
                            "reviewed_at": "2026-09-30", "reviewer": "reviewer", "mapping_status": "EXACT_COVERED"})
            decisions[i].update(research_state="HOME_CONFIRMED", home_copyright="series_a",
                                authority_type="OFFICIAL_CHARACTER_ROSTER", source_ids=source_id,
                                source_claim="Roster explicitly names this exact Character", provenance="source review",
                                reviewed_at="2026-09-30", reason_code="EXACT_ROSTER", reason_detail="exact member mapping")
        self.persist(cohort, sources, members, decisions)
        result = coverage.validate(self.cohort_path, self.sources_path, self.members_path, self.decisions_path, 3, self.roots_path)
        self.assertEqual(result["exact_member_mapping_count"], 2)
        self.assertEqual(result["source_reuse_ratio"], 1.0)
        self.assertFalse(result["complete"])

    def test_ambiguous_mapping_and_conflict_without_two_validated_roots_fail(self) -> None:
        cohort, sources, members, decisions = self.fixture(["character_a"])
        decisions[0].update(research_state="EVIDENCE_CONFLICT", reviewed_at="2026-09-30", provenance="two sources",
                            reason_code="COMPETING_HOMES", reason_detail="independent roots", validated_home_candidates="series_a")
        self.persist(cohort, sources, members, decisions)
        with self.assertRaisesRegex(ValueError, "requires exact member mappings from accepted sources"):
            coverage.validate(self.cohort_path, self.sources_path, self.members_path, self.decisions_path, 1, self.roots_path)

    def test_home_outside_frozen_copyright_roots_is_rejected(self) -> None:
        cohort, sources, members, decisions = self.fixture(["character_a"])
        source_id = coverage.deterministic_source_id("https://example.org/roster", "Example Publisher", "roster")
        sources.append({"source_id": source_id, "copyright_canonical": "unregistered_root",
                        "source_url": "https://example.org/roster", "source_type": "OFFICIAL_CHARACTER_ROSTER",
                        "authority_owner": "Example Publisher", "source_status": "ACCEPTED", "source_scope": "roster",
                        "exact_roster_available": "true", "reviewed_at": "2026-09-30", "source_claim": "listed",
                        "provenance": "official source", "reusable": "false", "notes": ""})
        members.append({"source_id": source_id, "canonical_character": "character_a", "matched_surface": "character_a",
                        "mapping_method": "EXACT_CANONICAL", "mapping_evidence": "exact identity", "reviewed_at": "2026-09-30",
                        "reviewer": "reviewer", "mapping_status": "EXACT_COVERED"})
        decisions[0].update(research_state="HOME_CONFIRMED", home_copyright="unregistered_root",
                            authority_type="OFFICIAL_CHARACTER_ROSTER", source_ids=source_id, source_claim="listed",
                            provenance="review", reviewed_at="2026-09-30", reason_code="ROSTER", reason_detail="listed")
        self.persist(cohort, sources, members, decisions)
        with self.assertRaisesRegex(ValueError, "missing baseline Copyright root"):
            coverage.validate(self.cohort_path, self.sources_path, self.members_path, self.decisions_path, 1, self.roots_path)


if __name__ == "__main__":
    unittest.main()
