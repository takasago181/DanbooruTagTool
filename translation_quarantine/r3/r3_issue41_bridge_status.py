"""Fail-closed Issue #41 guard for #32 meaning-relevant bridge status.

This is an orchestration-only guard.  It does not interpret Japanese wording,
change #32 verdicts, or add fields to the translation-visible meaning
fingerprint.  It only prevents a structurally valid snapshot from being
mistaken for a meaning-resolved bridge row when #32 explicitly says the
translation-relevant state is unresolved (or fails to state it).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


STATUS_FIELD = "meaning_relevant_status"
ALLOWED_STATUSES = {"RESOLVED", "UNRESOLVED"}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"expected JSON object rows in {path}")
    return rows


def _read_snapshot_rows(path: Path) -> list[dict[str, Any]]:
    """Read either the frozen #32 JSON snapshot contract or legacy JSONL rows.

    The authoritative Issue #41 bridge v2 is a single JSON object with a
    top-level ``rows`` array.  Earlier #41 fixtures were JSONL.  Both remain
    readable, but malformed/ambiguous JSON fails closed instead of being
    interpreted as an empty or partially-resolved bridge.
    """
    if not path.exists():
        return []
    if path.suffix.lower() == ".json":
        value = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(value, list):
            rows = value
        elif isinstance(value, dict):
            rows = value.get("rows")
            if not isinstance(rows, list):
                raise ValueError("#32 bridge JSON snapshot must contain a rows array")
        else:
            raise ValueError("#32 bridge JSON snapshot must be an object or row list")
        if not all(isinstance(row, dict) for row in rows):
            raise ValueError("#32 bridge snapshot rows must be JSON objects")
        return [dict(row) for row in rows]
    return _read_jsonl(path)


def inspect_bridge_status(
    snapshot_path: Path | None,
    requirements_path: Path,
) -> dict[str, Any]:
    requirements = _read_jsonl(requirements_path)
    required = [
        str(row.get("canonical", "")).strip()
        for row in requirements
        if str(row.get("canonical", "")).strip()
    ]
    if len(required) != len(set(required)):
        raise ValueError("duplicate canonical in Issue #41 bridge requirements")

    if snapshot_path is None or not snapshot_path.exists():
        return {
            "state": "NO_SNAPSHOT",
            "required_count": len(required),
            "resolved_count": 0,
            "unresolved_count": 0,
            "missing_count": len(required),
            "status_missing_count": 0,
            "blocked_count": len(required),
            "blocked_canonicals": sorted(required),
            "rows": [],
        }

    snapshot_rows = _read_snapshot_rows(snapshot_path)
    by_canonical: dict[str, dict[str, Any]] = {}
    for row in snapshot_rows:
        canonical = str(row.get("canonical", row.get("candidate_canonical", ""))).strip()
        if not canonical:
            continue
        if canonical in by_canonical:
            raise ValueError(f"duplicate canonical in #32 bridge snapshot: {canonical}")
        by_canonical[canonical] = row

    rows: list[dict[str, Any]] = []
    blocked: list[str] = []
    resolved_count = 0
    unresolved_count = 0
    missing_count = 0
    status_missing_count = 0

    for canonical in required:
        snapshot = by_canonical.get(canonical)
        if snapshot is None:
            state = "BRIDGE_MISSING"
            status = ""
            missing_count += 1
            blocked.append(canonical)
        else:
            raw_status = str(snapshot.get(STATUS_FIELD, "")).strip().upper()
            if not raw_status:
                state = "STATUS_MISSING"
                status = ""
                status_missing_count += 1
                blocked.append(canonical)
            elif raw_status not in ALLOWED_STATUSES:
                raise ValueError(
                    f"unknown {STATUS_FIELD} for {canonical}: {raw_status}"
                )
            elif raw_status == "UNRESOLVED":
                state = "MEANING_UNRESOLVED"
                status = raw_status
                unresolved_count += 1
                blocked.append(canonical)
            else:
                state = "RESOLVED"
                status = raw_status
                resolved_count += 1
        rows.append(
            {
                "canonical": canonical,
                STATUS_FIELD: status,
                "bridge_status_state": state,
            }
        )

    return {
        "state": "READY" if not blocked else "HOLD_BRIDGE",
        "required_count": len(required),
        "resolved_count": resolved_count,
        "unresolved_count": unresolved_count,
        "missing_count": missing_count,
        "status_missing_count": status_missing_count,
        "blocked_count": len(blocked),
        "blocked_canonicals": sorted(blocked),
        "rows": rows,
    }
