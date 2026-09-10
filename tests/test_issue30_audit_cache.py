import json
from pathlib import Path

import pytest

from tools.issue30_audit_cache import (
    AuditCacheSafetyError,
    SENTINEL_NAME,
    cleanup_owned,
    initialize_cache_root,
    write_ownership_manifest,
)


def _cache(tmp_path: Path) -> Path:
    return initialize_cache_root(tmp_path / "audit-cache")


def test_owned_cleanup_deletes_only_manifested_files(tmp_path):
    root = _cache(tmp_path)
    machine = root / "wave1" / "image-a.png"
    human = root / "wave1" / "image-b.png"
    machine.parent.mkdir()
    machine.write_bytes(b"a")
    human.write_bytes(b"b")
    manifest = write_ownership_manifest(root, "wave1", [machine, human])

    result = cleanup_owned(root, "wave1", [machine], manifest_path=manifest)

    assert result.deleted == (machine.resolve(),)
    assert not machine.exists()
    assert human.exists()


def test_unknown_target_fails_closed_before_any_delete(tmp_path):
    root = _cache(tmp_path)
    owned = root / "owned.png"
    unknown = root / "unknown.png"
    owned.write_bytes(b"owned")
    unknown.write_bytes(b"unknown")
    manifest = write_ownership_manifest(root, "wave1", [owned])

    with pytest.raises(AuditCacheSafetyError, match="not owned"):
        cleanup_owned(root, "wave1", [owned, unknown], manifest_path=manifest)

    assert owned.exists()
    assert unknown.exists()


def test_root_sentinel_and_manifest_identity_are_required(tmp_path):
    root = tmp_path / "audit-cache"
    root.mkdir()
    with pytest.raises(AuditCacheSafetyError, match="sentinel"):
        cleanup_owned(root, "wave1", [])

    (root / SENTINEL_NAME).write_text("wrong\n", encoding="utf-8")
    with pytest.raises(AuditCacheSafetyError, match="sentinel"):
        initialize_cache_root(root)


def test_outside_path_and_root_itself_are_rejected(tmp_path):
    root = _cache(tmp_path)
    owned = root / "owned.png"
    outside = tmp_path / "outside.png"
    owned.write_bytes(b"owned")
    outside.write_bytes(b"outside")
    manifest = write_ownership_manifest(root, "wave1", [owned])

    with pytest.raises(AuditCacheSafetyError, match="strict descendant"):
        cleanup_owned(root, "wave1", [outside], manifest_path=manifest)
    with pytest.raises(AuditCacheSafetyError, match="strict descendant"):
        cleanup_owned(root, "wave1", [root], manifest_path=manifest)
    assert owned.exists()
    assert outside.exists()


def test_protected_root_is_rejected_even_with_a_valid_sentinel(tmp_path):
    root = _cache(tmp_path / "protected")
    protected_parent = root.parent

    with pytest.raises(AuditCacheSafetyError, match="protected"):
        initialize_cache_root(root, protected_roots=[protected_parent])


def test_relative_cache_paths_are_rejected(tmp_path):
    with pytest.raises(AuditCacheSafetyError, match="absolute path"):
        initialize_cache_root(Path("relative-audit-cache"))


def test_manifest_rejects_traversal_before_cleanup(tmp_path):
    root = _cache(tmp_path)
    owned = root / "owned.png"
    owned.write_bytes(b"owned")
    manifest = write_ownership_manifest(root, "wave1", [owned])
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    payload["files"].append("../outside.png")
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(AuditCacheSafetyError, match="unsafe ownership"):
        cleanup_owned(root, "wave1", [owned], manifest_path=manifest)
    assert owned.exists()


def test_mixed_route_fixture_can_own_individual_audit_copies(tmp_path):
    root = _cache(tmp_path)
    machine = root / "machine" / "pair-a.png"
    human = root / "human" / "pair-b.png"
    blocked = root / "blocked" / "pair-c.png"
    for path in (machine, human, blocked):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(path.name.encode())
    manifest = write_ownership_manifest(root, "mixed-routes", [machine, human, blocked])

    result = cleanup_owned(root, "mixed-routes", [machine, human], manifest_path=manifest)

    assert len(result.deleted) == 2
    assert not machine.exists()
    assert not human.exists()
    assert blocked.exists()
