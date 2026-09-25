#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from codex_runtime import load_runtime

ROOT = Path(__file__).resolve().parents[2]

ACTIVE_FILES = [
    "docs/issue132/parallel/RUNTIME_AUTHORITY.json",
    "docs/issue132/CODEX_RUNTIME_V3.md",
    "docs/issue132/parallel/pass_a_semantic_contract_v2.json",
    "docs/issue132/parallel/CODEX_QA_STATE.json",
    "docs/issue132/parallel/codex-baseline/manifest.json",
    "scripts/issue132/codex_runtime.py",
    "scripts/issue132/codex_semantic.py",
    "scripts/issue132/codex_stage_window.py",
    "scripts/issue132/codex_repair_baseline.py",
    "scripts/issue132/validate_flat_pass_a.py",
]

LEGACY_EXECUTION_TOKENS = [
    "RUNTIME_WORKER_CARD_V",
    "RUNTIME_COORDINATOR_CARD_V",
    "RUNTIME_REPAIR_CARD_V",
    "WRITE_REQUEST_PROTOCOL_V",
    "CURRENT_AUTOMATION_OPERATION.md",
    "LUNA_PARALLEL_AUTOMATION_PROTOCOL.md",
    "promote_staging_window.py",
    "materialize_write_requests.py",
]


def main() -> None:
    authority, _, _, errors = load_runtime(ROOT)

    for rel in ACTIVE_FILES:
        if not (ROOT / rel).is_file():
            errors.append(f"active runtime file missing: {rel}")

    guide_path = ROOT / authority.get("runtime_guide", {}).get("path", "")
    guide = guide_path.read_text(encoding="utf-8") if guide_path.is_file() else ""
    for token in LEGACY_EXECUTION_TOKENS:
        if token in guide:
            errors.append(f"runtime guide references legacy execution component: {token}")

    persistence = authority.get("forward_persistence", {})
    if persistence.get("mode") != "DIRECT_CANONICAL_STAGING":
        errors.append("forward persistence must be DIRECT_CANONICAL_STAGING")
    if persistence.get("write_requests_for_new_work") is not False:
        errors.append("new forward work must not use write requests")
    if persistence.get("deferred_markers_for_new_work") is not False:
        errors.append("new forward work must not use deferred markers")
    if persistence.get("checkpoint_promotion") is not False:
        errors.append("checkpoint promotion must be disabled")
    if authority.get("historical_compatibility", {}).get("active_runtime_reads_old_history") is not False:
        errors.append("active runtime must not reconstruct legacy history")

    baseline = authority.get("baseline", {})
    if baseline.get("mode") != "MUTABLE_EFFECTIVE_SEED_WITH_GIT_HISTORY":
        errors.append("baseline mode mismatch")
    if baseline.get("holds_block_forward_progress") is not False:
        errors.append("historical holds must not block forward progress")
    if baseline.get("semantic_lint_debt_blocks_forward_progress") is not False:
        errors.append("historical lint debt must not block forward progress")

    result = {
        "schema_version": "issue132-runtime-layout-check-v4-codex-direct",
        "runtime_status": authority.get("status"),
        "execution_driver": authority.get("execution_driver"),
        "forward_persistence": persistence.get("mode"),
        "active_file_count": len(ACTIVE_FILES),
        "legacy_history_in_active_runtime": authority.get(
            "historical_compatibility", {}
        ).get("active_runtime_reads_old_history"),
        "error_count": len(errors),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
