"""Fail-closed safety helpers for disposable Issue #30 audit artifacts.

The cache is intentionally separate from generated source images and textual
evidence.  This module only permits file-level cleanup of paths explicitly
listed in a per-batch ownership manifest under a sentinel-protected root.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable


SENTINEL_NAME = ".danbooru_audit_cache_v1"
SENTINEL_CONTENT = "DanbooruTagTool disposable audit cache v1\n"
MANIFEST_SCHEMA = "issue30.audit_cache_ownership.v1"
_BATCH_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")


class AuditCacheSafetyError(RuntimeError):
    """Raised whenever a cache safety precondition is not proven."""


@dataclass(frozen=True)
class CleanupResult:
    batch_id: str
    requested: int
    deleted: tuple[Path, ...]


def _require_absolute(path: Path, label: str) -> Path:
    if not path.is_absolute():
        raise AuditCacheSafetyError(f"{label} must be an absolute path: {path}")
    return path.absolute()


def _is_reparse_or_symlink(path: Path) -> bool:
    try:
        if os.path.islink(path):
            return True
        attributes = getattr(os.lstat(path), "st_file_attributes", 0)
    except FileNotFoundError:
        return False
    # FILE_ATTRIBUTE_REPARSE_POINT on Windows; harmlessly zero elsewhere.
    return bool(attributes & 0x400)


def _has_reparse_component(path: Path) -> Path | None:
    """Return the first existing symlink/reparse component, if any."""
    current = path
    components = [current, *current.parents]
    for component in components:
        if component.exists() or component.is_symlink():
            if _is_reparse_or_symlink(component):
                return component
    return None


def _canonical(path: Path, label: str) -> Path:
    absolute = _require_absolute(path, label)
    reparse = _has_reparse_component(absolute)
    if reparse is not None:
        raise AuditCacheSafetyError(f"{label} contains a symlink/reparse component: {reparse}")
    return absolute.resolve(strict=False)


def _is_strict_descendant(root: Path, candidate: Path) -> bool:
    return candidate != root and root in candidate.parents


def _validate_batch_id(batch_id: str) -> str:
    if not isinstance(batch_id, str) or not _BATCH_ID.fullmatch(batch_id):
        raise AuditCacheSafetyError(f"invalid batch id: {batch_id!r}")
    return batch_id


def _protected(path: Path, protected_roots: Iterable[Path]) -> Path | None:
    for raw in protected_roots:
        protected = _canonical(Path(raw), "protected root")
        if path == protected or protected in path.parents:
            return protected
    return None


def validate_cache_root(root: Path, *, protected_roots: Iterable[Path] = ()) -> Path:
    """Validate and return a canonical, existing, sentinel-owned cache root."""
    root = _canonical(Path(root), "audit cache root")
    if not root.is_dir():
        raise AuditCacheSafetyError(f"audit cache root is not a directory: {root}")
    if _protected(root, protected_roots) is not None:
        raise AuditCacheSafetyError(f"audit cache root is protected: {root}")
    if root == Path(root.anchor):
        raise AuditCacheSafetyError("audit cache root may not be a drive/root directory")
    sentinel = root / SENTINEL_NAME
    if _has_reparse_component(sentinel) is not None:
        raise AuditCacheSafetyError("audit cache sentinel is a symlink/reparse point")
    if not sentinel.is_file():
        raise AuditCacheSafetyError(f"missing audit cache sentinel: {sentinel}")
    try:
        content = sentinel.read_text(encoding="utf-8")
    except OSError as exc:
        raise AuditCacheSafetyError(f"cannot read audit cache sentinel: {sentinel}") from exc
    if content != SENTINEL_CONTENT:
        raise AuditCacheSafetyError(f"audit cache sentinel content mismatch: {sentinel}")
    return root


def initialize_cache_root(root: Path, *, protected_roots: Iterable[Path] = ()) -> Path:
    """Create a new cache root and sentinel, or validate an existing one."""
    raw = _require_absolute(Path(root), "audit cache root")
    if _has_reparse_component(raw) is not None:
        raise AuditCacheSafetyError("audit cache root contains a symlink/reparse component")
    if raw.exists():
        return validate_cache_root(raw, protected_roots=protected_roots)
    if _protected(raw.resolve(strict=False), protected_roots) is not None:
        raise AuditCacheSafetyError(f"audit cache root is protected: {raw}")
    try:
        raw.mkdir(parents=True, exist_ok=False)
        (raw / SENTINEL_NAME).write_text(SENTINEL_CONTENT, encoding="utf-8", newline="")
    except OSError as exc:
        raise AuditCacheSafetyError(f"cannot initialize audit cache root: {raw}") from exc
    return validate_cache_root(raw, protected_roots=protected_roots)


def _target_under_root(root: Path, target: Path, label: str) -> Path:
    absolute = _require_absolute(Path(target), label)
    reparse = _has_reparse_component(absolute)
    if reparse is not None:
        raise AuditCacheSafetyError(f"{label} contains a symlink/reparse component: {reparse}")
    canonical = absolute.resolve(strict=False)
    if not _is_strict_descendant(root, canonical):
        raise AuditCacheSafetyError(f"{label} is not a strict descendant of audit root: {canonical}")
    return canonical


def _manifest_path(root: Path, batch_id: str, manifest_path: Path | None) -> Path:
    batch_id = _validate_batch_id(batch_id)
    candidate = manifest_path or (root / f"{batch_id}.ownership.json")
    return _target_under_root(root, Path(candidate), "ownership manifest")


def _relative_file(root: Path, file_path: Path) -> str:
    candidate = _target_under_root(root, file_path, "owned audit file")
    if not candidate.is_file():
        raise AuditCacheSafetyError(f"owned audit file is not an existing file: {candidate}")
    return candidate.relative_to(root).as_posix()


def write_ownership_manifest(
    root: Path,
    batch_id: str,
    owned_files: Iterable[Path],
    *,
    manifest_path: Path | None = None,
    protected_roots: Iterable[Path] = (),
) -> Path:
    """Record exactly which disposable files a batch may later remove."""
    root = validate_cache_root(root, protected_roots=protected_roots)
    batch_id = _validate_batch_id(batch_id)
    manifest = _manifest_path(root, batch_id, manifest_path)
    relatives = sorted({_relative_file(root, Path(item)) for item in owned_files})
    if manifest.relative_to(root).as_posix() in relatives:
        raise AuditCacheSafetyError("ownership manifest may not own itself")
    payload = {
        "schema_version": MANIFEST_SCHEMA,
        "project": "DanbooruTagTool",
        "batch_id": batch_id,
        "root": str(root),
        "files": relatives,
    }
    try:
        manifest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError as exc:
        raise AuditCacheSafetyError(f"cannot write ownership manifest: {manifest}") from exc
    return manifest


def _load_owned_files(root: Path, batch_id: str, manifest_path: Path | None) -> tuple[Path, set[str]]:
    manifest = _manifest_path(root, batch_id, manifest_path)
    if not manifest.is_file():
        raise AuditCacheSafetyError(f"missing ownership manifest: {manifest}")
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AuditCacheSafetyError(f"unreadable ownership manifest: {manifest}") from exc
    if payload.get("schema_version") != MANIFEST_SCHEMA or payload.get("project") != "DanbooruTagTool":
        raise AuditCacheSafetyError("ownership manifest identity/schema mismatch")
    if payload.get("batch_id") != batch_id or payload.get("root") != str(root):
        raise AuditCacheSafetyError("ownership manifest batch/root mismatch")
    files = payload.get("files")
    if not isinstance(files, list) or len(files) != len(set(files)) or any(not isinstance(item, str) for item in files):
        raise AuditCacheSafetyError("ownership manifest files must be a unique string list")
    owned: set[str] = set()
    for relative in files:
        pure = PurePosixPath(relative)
        if pure.is_absolute() or not pure.parts or any(part in {"", ".", ".."} for part in pure.parts) or "\\" in relative:
            raise AuditCacheSafetyError(f"unsafe ownership manifest path: {relative!r}")
        candidate = _target_under_root(root, root.joinpath(*pure.parts), "owned manifest entry")
        if candidate == manifest:
            raise AuditCacheSafetyError("ownership manifest may not own itself")
        owned.add(candidate.relative_to(root).as_posix())
    return manifest, owned


def cleanup_owned(
    root: Path,
    batch_id: str,
    targets: Iterable[Path],
    *,
    manifest_path: Path | None = None,
    protected_roots: Iterable[Path] = (),
) -> CleanupResult:
    """Delete only existing, file targets explicitly owned by ``batch_id``.

    All containment, reparse, type, and ownership checks happen before the
    first unlink.  Any validation failure therefore performs zero deletions.
    Directories and recursive cleanup are intentionally unsupported.
    """
    root = validate_cache_root(root, protected_roots=protected_roots)
    batch_id = _validate_batch_id(batch_id)
    manifest, owned = _load_owned_files(root, batch_id, manifest_path)
    del manifest
    raw_targets = list(targets)
    canonical_targets = [_target_under_root(root, Path(item), "cleanup target") for item in raw_targets]
    relative_targets = [item.relative_to(root).as_posix() for item in canonical_targets]
    if len(relative_targets) != len(set(relative_targets)):
        raise AuditCacheSafetyError("cleanup target list contains duplicates")
    unknown = sorted(set(relative_targets) - owned)
    if unknown:
        raise AuditCacheSafetyError(f"cleanup target is not owned by batch {batch_id}: {unknown}")
    for target in canonical_targets:
        if target.exists() and not target.is_file():
            raise AuditCacheSafetyError(f"cleanup target is not a regular file: {target}")
        if target.is_symlink() or _has_reparse_component(target) is not None:
            raise AuditCacheSafetyError(f"cleanup target is a symlink/reparse point: {target}")
    deleted: list[Path] = []
    try:
        for target in canonical_targets:
            if target.exists():
                target.unlink()
                deleted.append(target)
    except OSError as exc:
        raise AuditCacheSafetyError(f"cleanup failed after {len(deleted)} deletions") from exc
    return CleanupResult(batch_id=batch_id, requested=len(canonical_targets), deleted=tuple(deleted))
