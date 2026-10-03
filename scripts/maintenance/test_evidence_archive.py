import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("archive", Path(__file__).with_name("evidence_archive.py"))
archive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(archive)

class EvidenceArchiveTests(unittest.TestCase):
    def test_retained_oracles_match_frozen_git_bytes(self):
        manifest = json.loads(archive.MANIFEST.read_text(encoding="utf-8"))
        for item in manifest["files"]:
            if "retained_path" not in item: continue
            path = archive.ROOT / item["retained_path"]
            self.assertEqual(item["retained_bytes"], path.stat().st_size, item["path"])
            self.assertEqual(item["retained_sha256"], hashlib.sha256(path.read_bytes()).hexdigest(), item["path"])

    def test_reject_existing_checkout_and_userdata_targets(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for path in (root, archive.ROOT / "scratch", root / "UserData" / "new"):
                with self.assertRaises(ValueError): archive.safe_destination(path)
            (root / ".git").write_text("gitdir: protected")
            with self.assertRaises(ValueError): archive.safe_destination(root / "new")

    def test_exact_hash_detects_changed_or_missing_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "evidence.csv"
            path.write_bytes(b"original\n")
            manifest = {"files": [{"path": path.name, "bytes": 9, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}]}
            self.assertEqual(1, archive.verify(root, manifest))
            path.write_bytes(b"modified\n")
            with self.assertRaises(ValueError): archive.verify(root, manifest)
            path.unlink()
            with self.assertRaises(FileNotFoundError): archive.verify(root, manifest)

if __name__ == "__main__": unittest.main()
