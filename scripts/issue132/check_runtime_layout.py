#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from codex_runtime_guards import load_authority_and_qa

ROOT = Path(__file__).resolve().parents[2]
PARALLEL = ROOT / "docs/issue132/parallel"
AUTHORITY = PARALLEL / "RUNTIME_AUTHORITY.json"

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

    schema = authority.get("schema_version")
    if schema not in {
        "issue132-runtime-authority-v2-flat",
        "issue132-runtime-authority-v3-codex-guarded",
    }:
        errors.append("runtime authority schema mismatch")

    status = authority.get("status")
    if schema == "issue132-runtime-authority-v2-flat":
        if status != "ACTIVE":
            errors.append("v2 runtime authority must be ACTIVE")
    elif schema == "issue132-runtime-authority-v3-codex-guarded":
        if status not in {
            "READY_FOR_CODEX_CALIBRATION",
            "ACTIVE_CODEX",
            "PAUSED_FOR_CODEX_HANDOFF",
        }:
            errors.append("v3 runtime authority has invalid Codex status")
    if authority.get("branch") != "research/taxonomy-usability-audit":
        errors.append("runtime authority branch mismatch")

    model = authority.get("execution_model")
    if not isinstance(model, str) or not (ROOT / model).is_file():
        errors.append("active execution model missing")

    fixed = authority.get("fixed")
    if not isinstance(fixed, dict):
        errors.append("runtime authority fixed section missing")
        fixed = {}
    if fixed.get("lane_count") != 3:
        errors.append("Issue132 lane_count must be exactly 3")
    if schema == "issue132-runtime-authority-v2-flat":
        if fixed.get("task_count") != 5:
            errors.append("Issue132 v2 task_count must be exactly 5")
    elif schema == "issue132-runtime-authority-v3-codex-guarded":
        if fixed.get("legacy_chatgpt_task_count") != 5:
            errors.append("Issue132 legacy ChatGPT task count must be 5")
        if fixed.get("codex_parallel_role_count") != 4:
            errors.append("Issue132 Codex parallel role count must be 4")
        if fixed.get("max_unresolved_persistence_debt_per_lane") != 100:
            errors.append("Issue132 persistence debt limit must be 100")
        if authority.get("execution_driver") != "CODEX":
            errors.append("Issue132 v3 execution driver must be CODEX")
        automation = authority.get("chatgpt_automation")
        if not isinstance(automation, dict) or automation.get("state") != "PAUSED":
            errors.append("Issue132 ChatGPT automations must remain PAUSED during Codex execution")

    roles = authority.get("roles")
    if not isinstance(roles, dict):
        errors.append("runtime authority roles missing")
        roles = {}

    active_cards = {}
    for role in ("worker", "repair", "coordinator"):
        entry = roles.get(role)
        path = entry.get("path") if isinstance(entry, dict) else None
        if not isinstance(path, str):
            errors.append(f"{role}: active card path missing")
            continue
        active_cards[role] = path
        if not (ROOT / path).is_file():
            errors.append(f"{role}: active card missing: {path}")

    worker = roles.get("worker")
    if not isinstance(worker, dict) or worker.get("lanes") != [1, 2, 3]:
        errors.append("worker lanes must be exactly [1,2,3]")

    contracts = authority.get("contracts")
    if not isinstance(contracts, dict):
        errors.append("runtime authority contracts missing")
        contracts = {}
    semantic_path = contracts.get("semantic_vocabulary_path")
    if semantic_path != "docs/issue132/parallel/pass_a_contract_manifest_v1.json":
        errors.append("semantic vocabulary path mismatch")
    elif not (ROOT / semantic_path).is_file():
        errors.append("semantic vocabulary file missing")
    else:
        try:
            semantic = json.loads((ROOT / semantic_path).read_text(encoding="utf-8"))
            if semantic.get("schema_version") != contracts.get("semantic_vocabulary_schema_version"):
                errors.append("semantic vocabulary schema mismatch")
            required = contracts.get("required_keys")
            if not isinstance(required, list) or any(key not in semantic for key in required):
                errors.append("semantic vocabulary required keys missing")
        except Exception as exc:
            errors.append(f"semantic vocabulary unreadable: {exc}")

    if schema == "issue132-runtime-authority-v3-codex-guarded":
        _, qa_state, guard_errors = load_authority_and_qa(ROOT)
        errors.extend(guard_errors)
        codex = authority.get("codex")
        if not isinstance(codex, dict):
            errors.append("Codex runtime section missing")
        else:
            runbook = codex.get("runbook")
            if not isinstance(runbook, str) or not (ROOT / runbook).is_file():
                errors.append("Codex runbook missing")
        if not qa_state:
            errors.append("Codex QA state missing")

    progress = authority.get("progress")
    if not isinstance(progress, dict):
        errors.append("flat progress section missing")
    else:
        validator = progress.get("validator")
        if validator != "scripts/issue132/validate_flat_pass_a.py":
            errors.append("flat validator path mismatch")
        elif not (ROOT / validator).is_file():
            errors.append("flat validator missing")
        if progress.get("checkpoint_prefix_is_progress_gate") is not False:
            errors.append("checkpoint prefix must not be the flat progress gate")
        if progress.get("checkpoint_promotion_required") is not False:
            errors.append("checkpoint promotion must be disabled")

    for lane in (1, 2, 3):
        status = PARALLEL / f"lane-{lane}/status.json"
        if status.exists():
            errors.append(f"legacy status cache present: {status.relative_to(ROOT)}")

    for path in FORBIDDEN_EXACT:
        if path.exists():
            errors.append(f"obsolete runtime artifact present: {path.relative_to(ROOT)}")

    result = {
        "schema_version": "issue132-runtime-layout-check-v2-flat",
        "active_cards": active_cards,
        "task_count": fixed.get("task_count"),
        "legacy_chatgpt_task_count": fixed.get("legacy_chatgpt_task_count"),
        "codex_parallel_role_count": fixed.get("codex_parallel_role_count"),
        "execution_driver": authority.get("execution_driver"),
        "runtime_status": authority.get("status"),
        "progress_model": progress.get("model") if isinstance(progress, dict) else None,
        "error_count": len(errors),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        for error in errors:
            print("ERROR:", error)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
