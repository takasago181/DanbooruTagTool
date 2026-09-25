#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

AUTHORITY_REL = Path("docs/issue132/parallel/RUNTIME_AUTHORITY.json")


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    payload = f"blob {len(data)}\0".encode("ascii") + data
    return hashlib.sha1(payload).hexdigest()


def load_authority_and_qa(root: Path) -> tuple[dict, dict, list[str]]:
    errors: list[str] = []
    authority_path = root / AUTHORITY_REL
    try:
        authority = json.loads(authority_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {}, {}, [f"runtime authority unreadable: {exc}"]

    guard = authority.get("contracts", {}).get("semantic_guardrails", {})
    current = guard.get("current_policy_id")
    allowed = guard.get("allowed_policies", {})
    if not isinstance(allowed, dict) or not allowed:
        errors.append("semantic guardrail allowed_policies missing")
    elif current not in allowed:
        errors.append("current semantic policy is not registered")

    for policy_id, meta in allowed.items() if isinstance(allowed, dict) else []:
        if not isinstance(meta, dict):
            errors.append(f"semantic policy {policy_id}: metadata must be object")
            continue
        rel = meta.get("path")
        declared = meta.get("git_blob_sha")
        if not rel or not declared:
            errors.append(f"semantic policy {policy_id}: path/blob missing")
            continue
        path = root / rel
        if not path.exists():
            errors.append(f"semantic policy {policy_id}: file missing: {rel}")
            continue
        actual = git_blob_sha(path)
        if actual != declared:
            errors.append(
                f"semantic policy {policy_id}: git blob mismatch {actual} != {declared}"
            )

    qa_rel = authority.get("qa", {}).get("state_path")
    qa: dict = {}
    if not qa_rel:
        errors.append("QA state path missing from runtime authority")
    else:
        try:
            qa = json.loads((root / qa_rel).read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"QA state unreadable: {exc}")

    if qa:
        if qa.get("schema_version") != "issue132-codex-qa-state-v1":
            errors.append("QA state schema mismatch")
        for key in ("last_chatgpt_semantic_qa_by_lane", "allowed_forward_end_by_lane"):
            value = qa.get(key)
            if not isinstance(value, dict) or any(str(lane) not in value for lane in (1, 2, 3)):
                errors.append(f"QA state {key} missing lane entries")

    return authority, qa, errors


def effective_start(authority: dict, lane: int) -> int:
    guard = authority["contracts"]["semantic_guardrails"]
    return int(guard["effective_from_lane_local"][str(lane)])


def policy_trace_required(authority: dict, lane: int, start: int, end: int) -> bool:
    boundary = effective_start(authority, lane)
    if start < boundary <= end:
        raise ValueError(
            f"range {start}-{end} crosses semantic-policy boundary {boundary}; split the range"
        )
    return start >= boundary


def validate_policy_trace(
    obj: dict,
    authority: dict,
    lane: int,
    start: int,
    end: int,
    semantic_row_indices: set[int],
) -> list[str]:
    errors: list[str] = []
    try:
        required = policy_trace_required(authority, lane, start, end)
    except ValueError as exc:
        return [str(exc)]

    policy_id = obj.get("semantic_policy_id")
    policy_blob = obj.get("semantic_policy_git_blob_sha")
    reason_map = obj.get("decision_reason_codes")

    if not required and policy_id is None and policy_blob is None and reason_map is None:
        return errors

    guard = authority.get("contracts", {}).get("semantic_guardrails", {})
    allowed = guard.get("allowed_policies", {})
    meta = allowed.get(policy_id) if isinstance(allowed, dict) else None
    if not meta:
        errors.append("semantic_policy_id is not registered in runtime authority")
    elif policy_blob != meta.get("git_blob_sha"):
        errors.append("semantic_policy_git_blob_sha does not match registered policy")

    if not isinstance(reason_map, dict):
        errors.append("decision_reason_codes must be an object")
        return errors

    expected_keys = {str(i) for i in semantic_row_indices}
    if set(reason_map) != expected_keys:
        missing = sorted(expected_keys - set(reason_map))
        extra = sorted(set(reason_map) - expected_keys)
        errors.append(f"decision_reason_codes coverage mismatch missing={missing} extra={extra}")
        return errors

    allowed_codes = set(guard.get("allowed_decision_reason_codes", []))
    for key, codes in reason_map.items():
        if not isinstance(codes, list) or not codes or any(not isinstance(x, str) for x in codes):
            errors.append(f"decision_reason_codes[{key}] must be a non-empty string list")
            continue
        if len(codes) != len(set(codes)):
            errors.append(f"decision_reason_codes[{key}] contains duplicates")
        bad = [code for code in codes if code not in allowed_codes]
        if bad:
            errors.append(f"decision_reason_codes[{key}] invalid codes={bad}")

    return errors


def allowed_forward_end(qa: dict, lane: int) -> int:
    return int(qa["allowed_forward_end_by_lane"][str(lane)])


def persistence_debt_limit(authority: dict) -> int:
    return int(authority["fixed"]["max_unresolved_persistence_debt_per_lane"])
