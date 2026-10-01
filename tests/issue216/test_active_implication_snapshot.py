from __future__ import annotations

import csv
import json
import tempfile
import unittest
from argparse import Namespace
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

from scripts.issue216 import apply_danbooru_active_implication_snapshot as implication
from scripts.issue216 import authority_coverage as coverage


class ActiveImplicationSnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="test-active-implications-")
        self.root = Path(self.temp.name)
        self.cohort = self.root / "cohort.csv"
        self.sources = self.root / "sources.csv"
        self.members = self.root / "members.csv"
        self.decisions = self.root / "decisions.csv"
        self.roots = self.root / "roots.csv"
        self.snapshot = self.root / "snapshot.csv"
        self.manifest = self.root / "manifest.json"
        self.aliases = self.root / "aliases.csv"
        self.catalog = self.root / "catalog.csv"

        self._write(self.cohort, coverage.COHORT_FIELDS, [{
            "cohort_id": "character_a", "canonical_character": "character_a",
            "baseline_state": "HOME_UNRESOLVED", "baseline_home": "",
        }])
        self._write(self.sources, coverage.SOURCE_FIELDS, [])
        self._write(self.members, coverage.MEMBER_FIELDS, [])
        self._write(self.decisions, coverage.DECISION_FIELDS, [{
            "cohort_id": "character_a", "canonical_character": "character_a",
            "research_state": "UNRESEARCHED", "home_copyright": "", "authority_type": "",
            "source_ids": "", "source_claim": "", "provenance": "", "reviewed_at": "",
            "reason_code": "", "reason_detail": "", "validated_home_candidates": "",
        }])
        self._write(self.roots, coverage.ROOT_FIELDS, [
            {"copyright_canonical": "series_a", "provenance": "frozen catalog"},
            {"copyright_canonical": "series_b", "provenance": "frozen catalog"},
        ])
        self._write(self.aliases, ["NormalizedAlias", "ResolutionStatus", "TargetCount", "CanonicalTargets"], [])
        self.catalog.write_text("character_a,4\nseries_a,3\nseries_b,3\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temp.cleanup()

    @staticmethod
    def _write(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def _build(self, relations: list[dict[str, str]], aliases: list[dict[str, str]] | None = None):
        fields = ["implication_id", "antecedent_tag", "consequent_tag", "status", "updated_at"]
        self._write(self.snapshot, fields, relations)
        if aliases is not None:
            self._write(self.aliases, ["NormalizedAlias", "ResolutionStatus", "TargetCount", "CanonicalTargets"], aliases)
        snapshot_hash = coverage.sha256(self.snapshot)
        self.manifest.write_text(json.dumps({
            "snapshot_sha256": snapshot_hash, "filter_status": "active",
            "filter_consequent_category_id": 3, "snapshot_fetched_at_utc": "2026-10-01T00:00:00Z",
            "row_count": len(relations), "page_count": 1,
        }), encoding="utf-8")
        args = Namespace(snapshot=self.snapshot, manifest=self.manifest,
                         alias_index=self.aliases, tag_catalog=self.catalog)
        with ExitStack() as stack:
            for name, value in {
                "COHORT": self.cohort, "SOURCES": self.sources, "MEMBERS": self.members,
                "DECISIONS": self.decisions, "ROOTS": self.roots,
                "RELATIONS": self.root / "normalized.csv",
                "BASELINE_SIZE": 1,
                "ALIAS_EXPECTED": coverage.sha256(self.aliases),
                "CATALOG_EXPECTED": coverage.sha256(self.catalog),
            }.items():
                stack.enter_context(patch.object(implication, name, value))
            return implication.build(args)

    @staticmethod
    def _relation(identifier: str, antecedent: str, consequent: str, status: str = "active") -> dict[str, str]:
        return {"implication_id": identifier, "antecedent_tag": antecedent,
                "consequent_tag": consequent, "status": status, "updated_at": "2026-09-30"}

    def test_exact_direct_character_implication_confirms_one_existing_root(self) -> None:
        _, _, members, decisions, census = self._build([self._relation("10", "character_a", "series_a")])
        self.assertEqual(decisions[0]["research_state"], "HOME_CONFIRMED")
        self.assertEqual(decisions[0]["home_copyright"], "series_a")
        self.assertEqual(members[0]["member_relation_id"], "10")
        self.assertEqual(census["direct_active_character_copyright"], 1)

    def test_independent_direct_copyrights_remain_conflict(self) -> None:
        _, _, _, decisions, census = self._build([
            self._relation("10", "character_a", "series_a"),
            self._relation("11", "character_a", "series_b"),
        ])
        self.assertEqual(decisions[0]["research_state"], "EVIDENCE_CONFLICT")
        self.assertEqual(decisions[0]["home_copyright"], "")
        self.assertEqual(census["direct_multiple_root_conflicts"], 1)

    def test_explicit_copyright_hierarchy_selects_specific_direct_work(self) -> None:
        _, _, members, decisions, _ = self._build([
            self._relation("10", "character_a", "series_a"),
            self._relation("11", "character_a", "series_b"),
            self._relation("12", "series_a", "series_b"),
        ])
        self.assertEqual(decisions[0]["research_state"], "HOME_CONFIRMED")
        self.assertEqual(decisions[0]["home_copyright"], "series_a")
        self.assertEqual({r["browse_home_tier"] for r in members}, {"1", "2"})

    def test_copyright_hierarchy_without_direct_character_edge_does_not_confirm_home(self) -> None:
        _, _, _, decisions, census = self._build([self._relation("12", "series_a", "series_b")])
        self.assertEqual(decisions[0]["research_state"], "UNRESEARCHED")
        self.assertEqual(census["direct_active_character_copyright"], 0)

    def test_ambiguous_alias_and_nonactive_relation_are_rejected(self) -> None:
        _, _, _, decisions, census = self._build(
            [self._relation("10", "character alias", "series_a")],
            [{"NormalizedAlias": "character alias", "ResolutionStatus": "AMBIGUOUS_ALIAS",
              "TargetCount": "2", "CanonicalTargets": "character_a|character_b"}],
        )
        self.assertEqual(decisions[0]["research_state"], "UNRESEARCHED")
        self.assertEqual(census["direct_active_character_copyright"], 0)
        with self.assertRaisesRegex(ValueError, "non-active row"):
            self._build([self._relation("13", "character_a", "series_a", "retired")])


if __name__ == "__main__":
    unittest.main()
