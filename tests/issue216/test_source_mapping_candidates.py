from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from scripts.issue216.generate_mapping_candidates import build, norm, read_csv


def write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


class SourceMappingCandidatesTests(unittest.TestCase):
    def test_normalization_only_applies_unicode_width_and_whitespace(self):
        self.assertEqual(norm(" 三峰　結華 "), norm("三峰結華"))
        self.assertNotEqual(norm("ゆいか"), norm("三峰結華"))

    def test_exact_unique_match_becomes_candidate_and_ambiguity_requires_review(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            roster_path = root / "roster.csv"
            catalog_path = root / "catalog.csv"
            cohort_path = root / "cohort.csv"
            decisions_path = root / "decisions.csv"
            sources_path = root / "sources.csv"
            members_path = root / "members.csv"
            write_csv(roster_path, ["source_id", "source_url", "source_scope", "matched_surface"], [
                {"source_id": "src-test", "source_url": "https://example.test/roster", "source_scope": "test roster", "matched_surface": "秋月律子"},
                {"source_id": "src-test", "source_url": "https://example.test/roster", "source_scope": "test roster", "matched_surface": "三峰 結華"},
                {"source_id": "src-test", "source_url": "https://example.test/roster", "source_scope": "test roster", "matched_surface": "未登録"},
                {"source_id": "src-test", "source_url": "https://example.test/roster", "source_scope": "test roster", "matched_surface": "Faust"},
                {"source_id": "src-test", "source_url": "https://example.test/roster", "source_scope": "test roster", "matched_surface": "Ritsuko Akizuki"},
                {"source_id": "src-test", "source_url": "https://example.test/roster", "source_scope": "test roster", "matched_surface": "Shiori Novella"},
            ])
            write_csv(catalog_path, ["canonical_tag", "category", "display_ja", "search_ja", "aliases"], [
                {"canonical_tag": "akizuki_ritsuko", "category": "4", "display_ja": "秋月律子", "search_ja": "", "aliases": ""},
                {"canonical_tag": "mitsumine_yuika", "category": "4", "display_ja": "三峰結華", "search_ja": "", "aliases": ""},
                {"canonical_tag": "yuika_variant", "category": "4", "display_ja": "三峰 結華", "search_ja": "", "aliases": ""},
                {"canonical_tag": "faust_(project_moon)", "category": "4", "display_ja": "ファウスト", "search_ja": "", "aliases": "faust (limbus company)"},
                {"canonical_tag": "yorick_(shiori_novella)", "category": "4", "display_ja": "ヨリック", "search_ja": "Yorick | Shiori Novella", "aliases": ""},
            ])
            write_csv(cohort_path, ["cohort_id", "canonical_character"], [
                {"cohort_id": "akizuki_ritsuko", "canonical_character": "akizuki_ritsuko"},
                {"cohort_id": "mitsumine_yuika", "canonical_character": "mitsumine_yuika"},
                {"cohort_id": "yuika_variant", "canonical_character": "yuika_variant"},
                {"cohort_id": "faust_(project_moon)", "canonical_character": "faust_(project_moon)"},
                {"cohort_id": "yorick_(shiori_novella)", "canonical_character": "yorick_(shiori_novella)"},
            ])
            write_csv(decisions_path, ["canonical_character", "research_state"], [
                {"canonical_character": "akizuki_ritsuko", "research_state": "UNRESEARCHED"},
                {"canonical_character": "mitsumine_yuika", "research_state": "UNRESEARCHED"},
                {"canonical_character": "yuika_variant", "research_state": "UNRESEARCHED"},
                {"canonical_character": "faust_(project_moon)", "research_state": "UNRESEARCHED"},
                {"canonical_character": "yorick_(shiori_novella)", "research_state": "UNRESEARCHED"},
            ])
            write_csv(sources_path, ["source_id", "source_url", "source_scope", "source_status"], [
                {"source_id": "src-test", "source_url": "https://example.test/roster", "source_scope": "test roster", "source_status": "ACCEPTED"},
            ])
            write_csv(members_path, ["source_id", "canonical_character", "matched_surface", "mapping_status"], [
                {"source_id": "src-test", "canonical_character": "akizuki_ritsuko", "matched_surface": "Ritsuko Akizuki", "mapping_status": "EXACT_COVERED"},
            ])
            candidates = build(
                roster=read_csv(roster_path),
                catalog_path=catalog_path, cohort_path=cohort_path,
                decisions_path=decisions_path, sources_path=sources_path, members_path=members_path,
            )
            self.assertEqual(candidates[0]["candidate_status"], "AUTO_MAPPING_CANDIDATE")
            self.assertEqual(candidates[0]["canonical_character"], "akizuki_ritsuko")
            self.assertEqual(candidates[1]["candidate_status"], "REVIEW_REQUIRED")
            self.assertEqual(candidates[1]["competing_tags"], "mitsumine_yuika | yuika_variant")
            self.assertEqual(candidates[2]["candidate_status"], "NO_MATCH")
            self.assertEqual(candidates[3]["candidate_status"], "REVIEW_REQUIRED")
            self.assertEqual(candidates[3]["canonical_character"], "")
            self.assertEqual(candidates[3]["competing_tags"], "faust_(project_moon)")
            self.assertEqual(candidates[4]["candidate_status"], "AUTO_MAPPING_CANDIDATE")
            self.assertEqual(candidates[4]["canonical_character"], "akizuki_ritsuko")
            self.assertEqual(candidates[5]["candidate_status"], "REVIEW_REQUIRED")
            self.assertEqual(candidates[5]["canonical_character"], "")
            self.assertEqual(candidates[5]["competing_tags"], "yorick_(shiori_novella)")


if __name__ == "__main__":
    unittest.main()
