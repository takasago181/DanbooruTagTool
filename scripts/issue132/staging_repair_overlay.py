#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

SCHEMA = "issue132-pass-a-staging-repair-overlay-v1"
REPAIR_RE = re.compile(r"^repair_(\d{6})_(\d{6})_([0-9a-f]{12,64})\.json$")
ALLOWED_REASON_CODES = {
    "IDENTITY_REBIND",
    "MALFORMED_JSON",
    "STRUCTURAL_REBUILD",
    "SEMANTIC_LINT",
    "ROUTE_FAMILY_REMEDIATION",
}


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def canonical_window_bytes(window: dict[str, Any]) -> bytes:
    return json.dumps(
        window,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _load_overlay(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, [f"{path.name}: invalid repair overlay JSON: {exc}"]
    if not isinstance(obj, dict):
        return None, [f"{path.name}: repair overlay must be an object"]
    if obj.get("schema_version") != SCHEMA:
        errors.append(f"{path.name}: repair overlay schema mismatch")
    return obj, errors


def resolve_repair_overlay(
    source_path: Path,
    lane: int,
    start: int,
    end: int,
) -> tuple[dict[str, Any] | None, str | None, list[str]]:
    """Return (effective_window, overlay_name, errors).

    None effective_window means no valid overlay should replace the source.
    Repair overlays are append-only and bind to the exact original staging bytes.
    If more than one overlay exists, exactly one unsuperseded leaf must remain.
    """
    repair_dir = source_path.parent / "repairs"
    if not repair_dir.exists():
        return None, None, []

    candidates = sorted(repair_dir.glob(f"repair_{start:06d}_{end:06d}_*.json"))
    if not candidates:
        return None, None, []

    source_bytes = source_path.read_bytes()
    expected_blob = git_blob_sha(source_bytes)
    expected_sha256 = hashlib.sha256(source_bytes).hexdigest()

    loaded: dict[str, dict[str, Any]] = {}
    errors: list[str] = []

    for path in candidates:
        m = REPAIR_RE.match(path.name)
        if not m:
            errors.append(f"{path.name}: invalid repair overlay filename")
            continue
        file_start, file_end = int(m.group(1)), int(m.group(2))
        if file_start != start or file_end != end:
            errors.append(f"{path.name}: filename range mismatch")
            continue

        obj, obj_errors = _load_overlay(path)
        errors.extend(obj_errors)
        if obj is None:
            continue

        if obj.get("lane") != lane:
            errors.append(f"{path.name}: lane mismatch")
        if obj.get("lane_local_start") != start or obj.get("lane_local_end") != end:
            errors.append(f"{path.name}: range metadata mismatch")
        expected_source_path = source_path.as_posix()
        root_marker = "docs/issue132/parallel/"
        if root_marker in expected_source_path:
            expected_source_path = root_marker + expected_source_path.split(root_marker, 1)[1]
        if obj.get("source_staging_path") != expected_source_path:
            errors.append(f"{path.name}: source_staging_path mismatch")
        if obj.get("source_staging_blob_sha") != expected_blob:
            errors.append(f"{path.name}: source staging blob SHA mismatch")
        if obj.get("source_staging_sha256") != expected_sha256:
            errors.append(f"{path.name}: source staging SHA-256 mismatch")

        reasons = obj.get("repair_reason_codes")
        if not isinstance(reasons, list) or not reasons:
            errors.append(f"{path.name}: repair_reason_codes must be a non-empty list")
        elif any(r not in ALLOWED_REASON_CODES for r in reasons):
            errors.append(f"{path.name}: unsupported repair_reason_codes")

        supersedes = obj.get("supersedes", [])
        if not isinstance(supersedes, list) or any(not isinstance(x, str) for x in supersedes):
            errors.append(f"{path.name}: supersedes must be a list of filenames")

        window = obj.get("effective_window")
        if not isinstance(window, dict):
            errors.append(f"{path.name}: effective_window must be an object")
        else:
            payload_sha = hashlib.sha256(canonical_window_bytes(window)).hexdigest()
            if obj.get("effective_window_sha256") != payload_sha:
                errors.append(f"{path.name}: effective_window_sha256 mismatch")
            suffix = m.group(3)
            if not payload_sha.startswith(suffix):
                errors.append(f"{path.name}: filename hash prefix does not match effective window")

        loaded[path.name] = obj

    if errors:
        return None, None, errors

    superseded: set[str] = set()
    for name, obj in loaded.items():
        for old in obj.get("supersedes", []):
            if old not in loaded:
                errors.append(f"{name}: supersedes unknown overlay {old}")
            else:
                superseded.add(old)

    active = [name for name in loaded if name not in superseded]
    if len(active) != 1:
        errors.append(
            f"repair overlays for lane {lane} {start}-{end}: expected exactly one active leaf, got {active}"
        )
        return None, None, errors

    active_name = active[0]
    return loaded[active_name]["effective_window"], active_name, errors
