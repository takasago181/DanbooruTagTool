from pathlib import Path
import csv
import hashlib
import json


ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def test_protected_source_files_match_hash_manifest():
    manifest = json.loads((ROOT / "FILE_HASHES.json").read_text(encoding="utf-8"))
    special_children = sorted((ROOT / "data/special2788").glob("*"))
    reference_dir = ROOT / "data/special2788/prompt_reference"
    assert [path for path in special_children if path.is_dir()] == [reference_dir]
    protected = sorted((ROOT / "data/source").glob("*"))
    protected += [path for path in special_children if path.is_file()]

    assert protected
    for path in protected:
        assert path.is_file()
        relative = path.relative_to(ROOT).as_posix()
        assert relative in manifest
        assert path.stat().st_size == manifest[relative]["bytes"]
        assert _sha256(path) == manifest[relative]["sha256"]


def test_package_manifest_sources_exist_and_declares_no_missing_files():
    manifest = json.loads((ROOT / "PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))

    assert manifest["missing_required_files"] == []
    for relative in manifest["source_of_truth"].values():
        assert (ROOT / relative).is_file()


def test_build_manifest_template_has_required_snapshot_fields():
    template = json.loads(
        (ROOT / "templates/BUILD_MANIFEST.template.json").read_text(encoding="utf-8")
    )
    required = {
        "app_version",
        "statistics_dataset_name",
        "statistics_dataset_snapshot_id",
        "statistics_dataset_hash",
        "statistics_total_posts",
        "statistics_max_post_id",
        "tag_dictionary_snapshot",
        "tag_dictionary_hash",
        "special2788_version",
        "special2788_hash",
        "semantic_bridge_version",
        "semantic_bridge_hash",
        "index_format_version",
        "index_build_timestamp",
        "total_canonical_tags",
    }

    assert required <= set(template)
    assert template["total_canonical_tags"] == 124016


def test_raw_source_canonical_and_post_count_integrity():
    path = ROOT / "data/source/danbooru-2026-09-02.csv"
    canonical = set()

    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        for row in csv.reader(stream):
            assert len(row) == 4
            assert row[0]
            assert row[0] not in canonical
            canonical.add(row[0])
            assert row[2].isdigit()
            assert int(row[2]) >= 0

    assert len(canonical) == 124016
