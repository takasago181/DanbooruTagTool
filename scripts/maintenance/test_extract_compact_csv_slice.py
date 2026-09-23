#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/maintenance/extract_compact_csv_slice.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CompactCsvSliceTests(unittest.TestCase):
    def make_source(self, root: Path) -> Path:
        path = root / "source.csv"
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(
                f,
                fieldnames=["review_seq", "identity_key", "source_surfaces", "ignored"],
                lineterminator="\n",
            )
            w.writeheader()
            for i in range(1, 11):
                w.writerow(
                    {
                        "review_seq": i,
                        "identity_key": f"id_{i:02d}",
                        "source_surfaces": json.dumps([f"id_{i:02d}"]),
                        "ignored": f"x{i}",
                    }
                )
        return path

    def run_tool(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_lane_slice_and_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = self.make_source(root)
            out = root / "lane.csv"
            result = self.run_tool(
                "--input", str(source),
                "--output", str(out),
                "--expected-sha256", sha256(source),
                "--fields", "review_seq,identity_key,source_surfaces",
                "--start", "2",
                "--count", "2",
                "--key-column", "identity_key",
                "--order-column", "review_seq",
                "--lane-column", "review_seq",
                "--lane-count", "3",
                "--lane", "1",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with out.open("r", encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual([r["review_seq"] for r in rows], ["4", "7"])
            self.assertEqual([r["identity_key"] for r in rows], ["id_04", "id_07"])
            manifest = json.loads((root / "lane.csv.manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["source_rows"], 10)
            self.assertEqual(manifest["filtered_rows"], 4)
            self.assertEqual(manifest["output_rows"], 2)
            self.assertEqual(manifest["first_key"], "id_04")
            self.assertEqual(manifest["last_key"], "id_07")

    def test_sha_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = self.make_source(root)
            out = root / "bad.csv"
            result = self.run_tool(
                "--input", str(source),
                "--output", str(out),
                "--expected-sha256", "0" * 64,
                "--count", "1",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(out.exists())

    def test_missing_field_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = self.make_source(root)
            out = root / "bad.csv"
            result = self.run_tool(
                "--input", str(source),
                "--output", str(out),
                "--fields", "review_seq,missing",
                "--count", "1",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
