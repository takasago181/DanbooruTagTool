import hashlib
import json

import numpy as np
import pytest

from danbooru_tag_tool.runtime_index import INDEX_FORMAT_VERSION, RuntimeIndex, RuntimeIndexError
from danbooru_tag_tool.canonical_overlay import CanonicalOverlay, OverlayError
from danbooru_tag_tool.knowledge import TagKnowledgeCore
from pathlib import Path


SNAPSHOT = "fixture@revision:posts.parquet"


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_index(tmp_path):
    # post IDs 10, 11, 12, 13, 14 and tags a=0,b=1,c=2,d=3
    tags = ["a", "b", "c", "d"]
    post_ids = np.array([10, 11, 12, 13, 14], dtype=np.uint32)
    post_tag_offsets = np.array([0, 3, 5, 7, 9, 12], dtype=np.uint64)
    post_tag_ids = np.array([0, 1, 2, 0, 1, 0, 2, 1, 2, 0, 1, 3], dtype=np.uint32)
    tag_post_offsets = np.array([0, 4, 8, 11, 12], dtype=np.uint64)
    tag_post_ordinals = np.array([0, 1, 2, 4, 0, 1, 3, 4, 0, 2, 3, 4], dtype=np.uint32)
    counts = np.array([4, 4, 3, 1], dtype=np.uint32)
    arrays = {
        "post_ids.u32": post_ids, "post_tag_offsets.u64": post_tag_offsets,
        "post_tag_ids.u32": post_tag_ids, "tag_post_offsets.u64": tag_post_offsets,
        "tag_post_ordinals.u32": tag_post_ordinals, "runtime_global_counts.u32": counts,
    }
    for name, array in arrays.items():
        array.tofile(tmp_path / name)
    (tmp_path / "tags.json").write_text(json.dumps(tags), encoding="utf-8")
    metadata = {"index_format_version": INDEX_FORMAT_VERSION, "statistics_dataset_snapshot_id": SNAPSHOT}
    (tmp_path / "index_metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    files = list(arrays) + ["tags.json", "index_metadata.json"]
    manifest = {"statistics_dataset_snapshot_id": SNAPSHOT, "index_file_sha256": {name: _sha(tmp_path / name) for name in files}}
    (tmp_path / "BUILD_MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path


def test_true_one_two_three_and_five_and_post_ids(tmp_path):
    index = RuntimeIndex(make_index(tmp_path), verify_hashes=True)
    assert index.intersect(["a"]).post_ids.tolist() == [10, 11, 12, 14]
    assert index.intersect(["a", "b"]).post_ids.tolist() == [10, 11, 14]
    assert index.intersect(["a", "b", "c"]).post_ids.tolist() == [10]
    assert index.intersect(["a", "b", "c", "d", "a"]).post_ids.tolist() == []


def test_empty_and_unknown_tag_handling(tmp_path):
    index = RuntimeIndex(make_index(tmp_path))
    with pytest.raises(ValueError):
        index.intersect([])
    with pytest.raises(KeyError):
        index.intersect(["not_a_canonical"])


def test_candidate_aggregation_input_exclusion_and_global_counts(tmp_path):
    index = RuntimeIndex(make_index(tmp_path))
    result = index.intersect(["a", "b"])
    assert result.base_count == 3
    assert index.aggregate(result, exclude=["a", "b"]) == {"c": 1, "d": 1}
    assert dict(zip(index.tags, index.runtime_global_counts.tolist())) == {"a": 4, "b": 4, "c": 3, "d": 1}


def test_snapshot_mismatch_and_corruption_are_rejected(tmp_path):
    directory = make_index(tmp_path)
    with pytest.raises(RuntimeIndexError, match="Requested statistics snapshot"):
        RuntimeIndex(directory, expected_snapshot_id="other")
    with (directory / "post_ids.u32").open("ab") as output:
        output.write(b"x")
    with pytest.raises(RuntimeIndexError, match="byte length"):
        RuntimeIndex(directory)


def test_manifest_snapshot_mixing_and_hash_corruption_are_rejected(tmp_path):
    directory = make_index(tmp_path)
    manifest_path = directory / "BUILD_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["statistics_dataset_snapshot_id"] = "mixed"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(RuntimeIndexError, match="Snapshot mismatch"):
        RuntimeIndex(directory)
    manifest["statistics_dataset_snapshot_id"] = SNAPSHOT
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with (directory / "tags.json").open("a", encoding="utf-8") as output:
        output.write(" ")
    with pytest.raises(RuntimeIndexError, match="SHA-256 mismatch"):
        RuntimeIndex(directory, verify_hashes=True)


def test_real_overlay_alias_union_and_metadata():
    index = RuntimeIndex("data/runtime_index")
    overlay = CanonicalOverlay(index, "data/runtime_index/canonical_overlay.json")
    overlay.validate()
    assert overlay.source_status("china_dress") == "unique_alias_to_current_general"
    assert overlay.source_canonical("china_dress") == "qipao"
    assert overlay.global_count("qipao") == 73589
    # The audited holding_unworn_shoes merge has one same-post duplicate;
    # union count must therefore be 4,206 rather than the 4,207 sum.
    assert overlay.global_count("holding_unworn_shoes") == 4206
    source_ids = overlay.source_tag_ids("holding_unworn_shoes")
    overlap = np.intersect1d(index.postings("holding_unworn_shoes"), index.postings("holding_shoes"))
    assert overlap.size == 1
    aggregate = overlay.aggregate(type("Result", (), {"post_ordinals": overlap})())
    assert aggregate["holding_unworn_shoes"] == 1


def test_overlay_preserves_runtime_only_category_and_semantic_identity():
    index = RuntimeIndex("data/runtime_index")
    overlay = CanonicalOverlay(index, "data/runtime_index/canonical_overlay.json")
    assert overlay.source_status("areolae") == "runtime_only"
    assert overlay.source_canonical("areolae") is None
    assert overlay.source_status("listen!!") == "exact_current_non_general"
    assert overlay.metadata["statistics_tag_scope"] == "general"
    assert overlay.metadata["model_agnostic_statistics"] is True
    assert "current_post_count" not in overlay.metadata
    core = TagKnowledgeCore.load(Path("."))
    assert hasattr(core.canonical["qipao"], "current_post_count")
    assert not hasattr(overlay, "current_post_count")
    assert overlay.global_count("qipao") == 73589  # runtime count is a separate API
    with pytest.raises(OverlayError, match="snapshot"):
        CanonicalOverlay(index, "data/runtime_index/canonical_overlay.json", expected_snapshot_id="other")


def test_overlay_payload_hash_and_file_hash_have_distinct_roles():
    path = Path("data/runtime_index/canonical_overlay.json")
    document = json.loads(path.read_text(encoding="utf-8"))
    payload = {
        "canonical_to_source_tag_ids": {key: list(value) for key, value in sorted(document["canonical_to_source_tag_ids"].items())},
        "source_tag_identities": document["source_tag_identities"],
    }
    payload_hash = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    file_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    assert document["metadata"]["overlay_payload_sha256"] == payload_hash
    assert file_hash != payload_hash
    assert "overlay_sha256" not in document["metadata"]
