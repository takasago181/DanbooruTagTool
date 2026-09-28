from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/issue180"))

import _issue180_v3_common as common
import build_structure_v3
import migrate_evidence_v3


SCHEMA = list(common.DECISION_SCHEMA)
OLD_SHARDS = [
    "direct_and_exceptions_v2.csv",
    "discovery_roster_reviews_v2.csv",
    "family_terminal_reviews_v2.csv",
    "roster_verified_v4.csv",
    "variant_pattern_reviews_v2.csv",
    "variants_verified_v4.csv",
]


def row(scope: str, key: str, home: str = "home", state: str = "PASS") -> dict[str, str]:
    return {
        "scope": scope, "key": key, "home_copyright": home, "base_character": "",
        "authority_type": "OFFICIAL_CHARACTER_ROSTER", "evidence_url": "https://example.test/roster",
        "evidence_claim": "An exact reviewed roster row identifies this character and its HOME Copyright.",
        "validation_state": state, "officiality_state": "OFFICIAL_CONFIRMED", "notes": "fixture",
    }


def write_shard(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=SCHEMA, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


class DecisionShardDiscoveryTests(unittest.TestCase):
    def test_current_active_shards_are_schema_clean_and_duplicate_free(self):
        paths = common.decision_paths()
        self.assertEqual(paths, sorted(paths, key=lambda path: path.name))
        self.assertNotIn(common.PROTECTED_DECISION_BASE, [path.name for path in paths])
        decisions = common.load_decisions()
        expected_count = 0
        for path in paths:
            with path.open("r", encoding="utf-8-sig", newline="") as stream:
                expected_count += sum(1 for _ in csv.DictReader(stream, strict=True))
        self.assertEqual(len(decisions), expected_count)
        self.assertTrue(all(item["scope"].strip() and item["key"].strip() for item in decisions))
        self.assertEqual(
            [path.name for path in paths],
            [
                "direct_and_exceptions_v2.csv", "discovery_roster_reviews_v2.csv",
                "family_terminal_reviews_v2.csv", "roster_serial_inazuma_codex_20260929.csv",
                "roster_verified_v4.csv", "serial_forward_qa_wave_02_20260929.csv",
                "serial_forward_qa_wave_03_20260929.csv", "serial_forward_qa_wave_04_20260929.csv",
                "street_fighter_serial_20260929.csv",
                "variant_pattern_reviews_v2.csv", "variants_verified_v4.csv",
            ],
        )

    def test_repair_audit_machine_checks_all_91_rows_and_semantic_values(self):
        audit_path = ROOT / "docs/issue180/serial/DECISION_SHARD_SERIALIZATION_REPAIR_V1.json"
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        self.assertEqual(audit["repaired_row_count"], 91)
        self.assertFalse(audit["decision_contents_changed"])
        repaired_total = 0
        for file_record in audit["files"]:
            path = ROOT / file_record["path"]
            self.assertEqual(common.sha256_file(path), file_record["repaired_file_sha256"])
            with path.open("r", encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream, strict=True))
            self.assertTrue(all(tuple(row.keys()) == common.DECISION_SCHEMA for row in rows))
            for row_record in file_record["repaired_rows"]:
                repaired_total += 1
                before = row_record["semantic_values_before"]
                after = row_record["semantic_values_after"]
                self.assertTrue(row_record["semantic_values_identical"])
                self.assertEqual(before, after)
                row_values = [rows[row_record["record_number"] - 2][field] for field in common.DECISION_SCHEMA]
                self.assertEqual(row_values, [before[field] for field in common.DECISION_SCHEMA])
                expected_hash = common.sha256_text(json.dumps(row_values, ensure_ascii=False, separators=(",", ":")))
                self.assertEqual(row_record["semantic_sha256_before"], expected_hash)
                self.assertEqual(row_record["semantic_sha256_after"], expected_hash)
        self.assertEqual(repaired_total, 91)

    def test_arbitrary_shard_is_discovered_and_protected_base_is_excluded(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            write_shard(directory / "z_new_campaign.csv", [row("DIRECT_CHARACTER", "new_character")])
            write_shard(directory / common.PROTECTED_DECISION_BASE, [row("DIRECT_CHARACTER", "protected")])
            self.assertEqual([p.name for p in common.decision_paths(directory)], ["z_new_campaign.csv"])
            decisions = common.load_decisions(directory)
            self.assertEqual([d["key"] for d in decisions], ["new_character"])

    def test_duplicate_scope_key_fails_closed_across_active_shards(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            write_shard(directory / "a.csv", [row("DIRECT_CHARACTER", "same")])
            write_shard(directory / "b.csv", [row("DIRECT_CHARACTER", "same")])
            with self.assertRaisesRegex(ValueError, "duplicate decision"):
                common.load_decisions(directory)

    def test_schema_blank_keys_and_malformed_csv_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            malformed = directory / "bad.csv"
            malformed.write_text(",".join(SCHEMA) + "\n" + ",".join(["DIRECT_CHARACTER", "", *([""] * 8)]) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "blank scope/key"):
                common.load_decisions(directory)
            malformed.write_text("wrong,header\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "expected exact schema"):
                common.load_decisions(directory)
            malformed.write_text(",".join(SCHEMA) + '\n"unterminated\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "malformed decision shard"):
                common.load_decisions(directory)

    def test_shard_and_row_order_are_deterministic_and_old_six_order_is_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            for name in reversed(OLD_SHARDS):
                write_shard(directory / name, [row("DIRECT_CHARACTER", name)])
            first = common.load_decisions(directory)
            expected_names = sorted(OLD_SHARDS)
            self.assertEqual([Path(d["_source_file"]).name for d in first], expected_names)
            self.assertEqual([d["key"] for d in first], expected_names)
            # Rewriting/creating the same six shards in another order cannot affect output.
            for path in directory.glob("*.csv"):
                path.unlink()
            for name in OLD_SHARDS:
                write_shard(directory / name, [row("DIRECT_CHARACTER", name)])
            self.assertEqual(common.load_decisions(directory), first)

    def test_new_pass_shard_reaches_v3_evidence_ledger(self):
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            decisions = temp_path / "decisions"
            write_shard(decisions / "campaign_added_after_freeze.csv", [row("DIRECT_CHARACTER", "new_character", "home")])
            ledger = temp_path / "evidence_ledger_v3.csv"
            with patch.object(common, "DECISION_DIR", decisions), \
                 patch.object(migrate_evidence_v3, "OUT", temp_path), \
                 patch.object(migrate_evidence_v3, "LEDGER", ledger), \
                 patch.object(migrate_evidence_v3, "V3_SEED", temp_path / "empty_seed.csv"), \
                 patch.object(migrate_evidence_v3, "EVIDENCE_DIR", temp_path / "evidence"), \
                 patch.object(migrate_evidence_v3, "load_catalog", return_value=(
                     [{"canonical_tag": "new_character"}], [{"canonical_tag": "home"}], {"new_character": {"canonical_tag": "new_character"}}
                 )), \
                 patch.object(migrate_evidence_v3, "read_csv", return_value=[]):
                migrate_evidence_v3.main()
            with ledger.open("r", encoding="utf-8-sig", newline="") as stream:
                evidence = list(csv.DictReader(stream))
            self.assertEqual([(e["subject_key"], e["object_key"]) for e in evidence], [("new_character", "home")])
            self.assertIn("campaign_added_after_freeze.csv:2", evidence[0]["source_provenance"])

    def test_new_shard_hash_is_in_source_manifest_input_set(self):
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            decisions = temp_path / "decisions"
            shard = decisions / "manifest_new_campaign.csv"
            write_shard(shard, [row("DIRECT_CHARACTER", "manifest_character")])
            out = temp_path / "out"
            with patch.object(common, "DECISION_DIR", decisions), \
                 patch.object(build_structure_v3, "OUT", out), \
                 patch.object(build_structure_v3, "GRAPH", out / "structure_graph_v3.csv"), \
                 patch.object(build_structure_v3, "MANIFEST", out / "source_manifest_v3.json"), \
                 patch.object(build_structure_v3, "load_catalog", return_value=([], [], {})), \
                 patch.object(build_structure_v3, "canonical_family_candidates", return_value=[]):
                build_structure_v3.main()
            manifest = json.loads((out / "source_manifest_v3.json").read_text(encoding="utf-8"))
            inputs = {item["path"]: item["sha256"] for item in manifest["inputs"]}
            self.assertEqual(inputs[common.relpath(shard)], common.sha256_file(shard))
            with patch.object(common, "DECISION_DIR", decisions):
                self.assertEqual(common.decision_paths(), [shard])


if __name__ == "__main__":
    unittest.main()
