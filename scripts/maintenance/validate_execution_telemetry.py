#!/usr/bin/env python3
"""Validate a lightweight execution telemetry JSON object.

Issue #188 utility. Telemetry is operational cache, not semantic authority.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ALLOWED_PREFLIGHT = {"FAST", "FULL"}
NONNEGATIVE = {
    "rows_completed",
    "checkpoints_created",
    "researched_rows",
    "unresolved_rows",
    "research_batches",
    "semantic_input_rows",
    "structural_validation_failures",
}


def validate(obj: dict) -> list[str]:
    errors: list[str] = []
    if obj.get("schema_version") != "execution-telemetry-v1":
        errors.append("schema_version must be execution-telemetry-v1")

    for key in sorted(NONNEGATIVE):
        value = obj.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(f"{key} must be a non-negative integer")

    if obj.get("preflight_mode") not in ALLOWED_PREFLIGHT:
        errors.append("preflight_mode must be FAST or FULL")

    if not isinstance(obj.get("full_authority_fallback"), bool):
        errors.append("full_authority_fallback must be boolean")

    stop_reason = obj.get("stop_reason")
    if not isinstance(stop_reason, str) or not stop_reason.strip():
        errors.append("stop_reason must be a non-empty string")

    duration = obj.get("duration_seconds_observed")
    if duration is not None and (
        not isinstance(duration, (int, float))
        or isinstance(duration, bool)
        or duration < 0
    ):
        errors.append("duration_seconds_observed must be null or non-negative number")

    rows = obj.get("rows_completed")
    researched = obj.get("researched_rows")
    unresolved = obj.get("unresolved_rows")
    semantic_input = obj.get("semantic_input_rows")
    if isinstance(rows, int) and isinstance(researched, int) and researched > rows:
        errors.append("researched_rows cannot exceed rows_completed")
    if isinstance(rows, int) and isinstance(unresolved, int) and unresolved > rows:
        errors.append("unresolved_rows cannot exceed rows_completed")
    if isinstance(rows, int) and isinstance(semantic_input, int) and semantic_input < rows:
        errors.append("semantic_input_rows cannot be lower than rows_completed")

    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    args = ap.parse_args()

    path = Path(args.path)
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        print("ERROR: telemetry root must be object")
        return 1

    errors = validate(obj)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
