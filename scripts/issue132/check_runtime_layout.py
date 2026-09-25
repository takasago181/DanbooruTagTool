#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PARALLEL = ROOT / "docs/issue132/parallel"
AUTHORITY = PARALLEL / "RUNTIME_AUTHORITY.json"

EXPECTED = {
    "worker": "docs/issue132/parallel/RUNTIME_WORKER_CARD_V8.md",
    "repair": "docs/issue132/parallel/RUNTIME_REPAIR_CARD_V6.md",
    "coordinator": "docs/issue132/parallel/RUNTIME_COORDINATOR_CARD_V5.md",
}

FORBIDDEN_EXACT = [
    PARALLEL / "repair_status.json",
    PARALLEL / "coordinator_status.json",
    ROOT / ".github/workflows/issue132_staging_v2_migration.yml",
    ROOT / "scripts/issue132/migrate_staging_v1_to_v2.py",
    PARALLEL / "parallel_plan_v1.json",
    PARALLEL / "WORKER_EXECUTION_CARD_V1.md",
]

def main() -> None:
    errors: list[str] = []

    try:
        authority = json.loads(AUTHORITY.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"invalid runtime authority: {exc}")

    if authority.get("schema_version") != "issue132-runtime-authority-v1":
        errors.append("runtime authority schema mismatch")
    if authority.get("status") != "ACTIVE":
        errors.append("runtime authority must be ACTIVE")
    if authority.get("branch") != "research/taxonomy-usability-audit":
        errors.append("runtime authority branch mismatch")

    roles = authority.get("roles")
    if not isinstance(roles, dict):
        errors.append("runtime authority roles missing")
        roles = {}

    for role, expected_path in EXPECTED.items():
        entry = roles.get(role)
        if not isinstance(entry, dict) or entry.get("path") != expected_path:
            errors.append(f"{role}: active card path mismatch")
        if not (ROOT / expected_path).is_file():
            errors.append(f"{role}: active card missing: {expected_path}")

    active_paths = set(EXPECTED.values())

    runtime_patterns = [
        "RUNTIME_WORKER_CARD_V*.md",
        "RUNTIME_REPAIR_CARD_V*.md",
        "RUNTIME_REPAIR*_CARD_V*.md",
        "RUNTIME_COORDINATOR_CARD_V*.md",
    ]
    seen: set[Path] = set()
    for pattern in runtime_patterns:
        for path in PARALLEL.glob(pattern):
            if path in seen:
                continue
            seen.add(path)
            rel = path.relative_to(ROOT).as_posix()
            if rel not in active_paths:
                errors.append(f"superseded runtime card present: {rel}")

    for lane in (1, 2, 3):
        status = PARALLEL / f"lane-{lane}/status.json"
        if status.exists():
            errors.append(f"legacy status cache present: {status.relative_to(ROOT)}")

    for path in FORBIDDEN_EXACT:
        if path.exists():
            errors.append(f"obsolete runtime artifact present: {path.relative_to(ROOT)}")

    result = {
        "schema_version": "issue132-runtime-layout-check-v1",
        "active_cards": EXPECTED,
        "error_count": len(errors),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit(1)

if __name__ == "__main__":
    main()
