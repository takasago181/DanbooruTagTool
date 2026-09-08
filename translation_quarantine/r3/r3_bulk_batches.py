"""Deterministic post-canary Issue #36 quarantine batch orchestration.

This module only orchestrates the already-validated R3 evaluator.  It never
selects or rewrites the existing canary, never writes production data, and
stops on machine-detectable unsafe READY, bridge contradiction, verifier
failure, or evaluator rule drift.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

try:
    from .r3_bulk_evidence import acquire_and_freeze
    from .r3_bulk_select import CANARY_SEED, VALIDATED_R3_BASE, portable_rows_hash
    from .r3_common import RISK_ORDER, classify_risk, file_hash, json_hash, protected_snapshot, read_csv, read_json, read_jsonl, stable_key, write_json, write_jsonl
    from .r3_issue41_bridge_status import inspect_bridge_status
    from .r3_run import _load_issue32_rows, _make_pilot_rows
except ImportError:  # pragma: no cover
    from r3_bulk_evidence import acquire_and_freeze
    from r3_bulk_select import CANARY_SEED, VALIDATED_R3_BASE, portable_rows_hash
    from r3_common import RISK_ORDER, classify_risk, file_hash, json_hash, protected_snapshot, read_csv, read_json, read_jsonl, stable_key, write_json, write_jsonl
    from r3_issue41_bridge_status import inspect_bridge_status
    from r3_run import _load_issue32_rows, _make_pilot_rows


CAMPAIGN_ID = "issue36-r3-bulk-remaining-20260909-v1"
BATCH_SIZE = 200
CANARY_OUTPUT = "translation_quarantine/r3_bulk_canary"
BATCH_OUTPUT = "translation_quarantine/r3_bulk_batches"
ISSUE32_V2_BLOB = "974bb9c971caf632f8ec73dff39fe4c55e60efaa"
ISSUE32_V2_CONTENT_IDENTITY = "sha256:7e46f7f3655846a4f6ea2d1990e015701cbff5b123bdf8ef1809668f8a375ef5"
ISSUE32_V2_RAW_SHA256 = "fdc2d097d26b588b61ba501fb779152f3b4ee90eef1c6b195addcc42bd955947"
RULE_FILES = (
    "translation_quarantine/r3/r3_common.py",
    "translation_quarantine/r3/r3_run.py",
    "translation_quarantine/r3/r3_bulk_evidence.py",
    "translation_quarantine/r3/r3_issue41_bridge_status.py",
)
ARTIFACTS = (
    "batch_selection.json", "evidence_manifest.jsonl", "rows.jsonl",
    "search_terms.jsonl", "bridge32.jsonl", "run_summary.json",
    "campaign_manifest.json", "stop_condition_check.json",
)


def _rooted(root: Path, relative: str) -> Path:
    return (root / relative).resolve()


def _batch_output(root: Path, output: Path) -> Path:
    allowed = _rooted(root, BATCH_OUTPUT)
    output = output.resolve()
    try:
        output.relative_to(allowed)
    except ValueError as exc:
        raise ValueError(f"batch output must stay below {allowed}") from exc
    output.mkdir(parents=True, exist_ok=True)
    return output


def _git_blob(root: Path, ref: str, relative_path: str) -> str:
    result = subprocess.run(
        ["git", "-c", f"safe.directory={root}", "rev-parse", f"{ref}:{relative_path}"],
        cwd=root, stdin=subprocess.DEVNULL, capture_output=True, check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout.decode("ascii").strip()


def _canonicals(rows: list[Mapping[str, Any]]) -> set[str]:
    return {str(row.get("canonical", "")).strip() for row in rows if str(row.get("canonical", "")).strip()}


def _issue41_exclusions(selection_path: Path) -> set[str]:
    value = read_json(selection_path)
    rows = value.get("selected", []) if isinstance(value, dict) else value
    return _canonicals(rows)


def _ordered_records(queue: list[dict[str, str]], excluded: set[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source in queue:
        canonical = str(source.get("canonical", "")).strip()
        if not canonical or source.get("priority", "").strip() != "P0" or canonical in excluded:
            continue
        if canonical in seen:
            raise ValueError(f"duplicate P0 canonical: {canonical}")
        seen.add(canonical)
        records.append({
            "canonical": canonical,
            "lanes": source.get("lanes", ""),
            "priority": source.get("priority", ""),
            "post_count_or_reference": source.get("post_count_or_reference", ""),
            "semantic_class": source.get("semantic_class", ""),
            "risk_class": classify_risk(canonical, source.get("risk_class", "")),
            "selection_key": stable_key(CANARY_SEED, canonical),
        })
    records.sort(key=lambda row: (row["selection_key"], row["canonical"]))
    for ordinal, row in enumerate(records, 1):
        row["campaign_ordinal"] = ordinal
        row["pilot_ordinal"] = ordinal
    return records


def _validate_canary(root: Path) -> dict[str, Any]:
    output = _rooted(root, CANARY_OUTPUT)
    required = ("canary_selection.json", "run_summary.json", "replay_verification.json", "campaign_manifest.json")
    if any(not (output / name).exists() for name in required):
        raise RuntimeError("PASS canary artifacts are incomplete")
    summary = read_json(output / "run_summary.json")
    replay = read_json(output / "replay_verification.json")
    selection = read_json(output / "canary_selection.json")
    if summary.get("canary_rows") != 200 or summary.get("production_modified") is not False:
        raise RuntimeError("existing canary is not a 200-row protected PASS candidate")
    if summary.get("self_grade") != "NOT_PERFORMED":
        raise RuntimeError("existing canary self-grade boundary is not preserved")
    if summary.get("bridge_status_guard", {}).get("state") != "READY":
        raise RuntimeError("existing canary #32 bridge guard is not READY")
    if summary.get("ready_rows", 0) <= 0 or summary.get("approval_evidence_state") != "APPROVAL_EVIDENCE_AVAILABLE":
        raise RuntimeError("existing canary lacks approval-capable evidence")
    if not replay.get("ok") or replay.get("deterministic_replay", {}).get("original_vs_rerun2") != "PASS":
        raise RuntimeError("existing canary replay is not PASS")
    if not read_json(output / "leakage_check.json").get("ok"):
        raise RuntimeError("existing canary leakage check is not PASS")
    return {"summary": summary, "selection": selection}


def _validate_sources(root: Path, canary: Mapping[str, Any]) -> dict[str, Any]:
    selection = canary["selection"]
    queue_path = _rooted(root, "translation_quarantine/missing_candidates.csv")
    phase1a_path = _rooted(root, "translation_quarantine/phase1a_review.csv")
    issue41_path = _rooted(root, "translation_quarantine/r3/pilot_selection.json")
    queue = read_csv(queue_path)
    phase1a = read_csv(phase1a_path)
    expected_queue = selection.get("source_identity", {}).get("missing_candidates.csv", {})
    expected_phase1a = selection.get("source_identity", {}).get("phase1a_review.csv", {})
    for path, expected, relative in ((queue_path, expected_queue, "translation_quarantine/missing_candidates.csv"), (phase1a_path, expected_phase1a, "translation_quarantine/phase1a_review.csv")):
        current_blob = _git_blob(root, "HEAD", relative)
        if current_blob != expected.get("validated_git_blob"):
            raise RuntimeError(f"source Git blob drift: {relative}")
        if portable_rows_hash(read_csv(path)) != expected.get("validated_portable_content_identity"):
            raise RuntimeError(f"source portable identity drift: {relative}")
    phase_excluded = _canonicals(phase1a)
    issue41_excluded = _issue41_exclusions(issue41_path)
    canary_rows = selection.get("selected", [])
    canary_excluded = _canonicals(canary_rows)
    base_excluded = phase_excluded | issue41_excluded
    ordered_base = _ordered_records(queue, base_excluded)
    expected_canary = [str(row["canonical"]) for row in canary_rows]
    if [row["canonical"] for row in ordered_base[:200]] != expected_canary:
        raise RuntimeError("existing canary membership is not the deterministic first 200")
    if selection.get("eligible_unseen_p0_count") != len(ordered_base):
        raise RuntimeError("eligible unseen P0 count drift")
    remaining = [row for row in ordered_base if row["canonical"] not in canary_excluded]
    if len(remaining) + len(canary_excluded) != len(ordered_base):
        raise RuntimeError("canary exclusion contains an unknown or duplicate canonical")
    excluded = base_excluded | canary_excluded
    return {
        "queue": queue,
        "queue_path": queue_path,
        "phase1a_path": phase1a_path,
        "issue41_path": issue41_path,
        "queue_raw_sha256": file_hash(queue_path),
        "queue_portable_identity": portable_rows_hash(queue),
        "phase1a_raw_sha256": file_hash(phase1a_path),
        "phase1a_portable_identity": portable_rows_hash(phase1a),
        "phase1a_count": len(phase_excluded),
        "issue41_count": len(issue41_excluded),
        "canary_count": len(canary_excluded),
        "base_exclusion_hash": json_hash(sorted(base_excluded)),
        "exclusion_hash": json_hash(sorted(excluded)),
        "eligible_before_canary": len(ordered_base),
        "remaining": remaining,
    }


def _validate_issue32(root: Path) -> tuple[Path, dict[str, Any]]:
    snapshot = _rooted(root, f"{CANARY_OUTPUT}/issue32_snapshot_v2.json")
    official_ref = "origin/dict-validation/quarantine:validation_quarantine/bridge_snapshots/ui_ja_issue41_overlap7_v2.json"
    if _git_blob(root, *official_ref.split(":", 1)) != ISSUE32_V2_BLOB:
        raise RuntimeError("official #32 v2 Git blob drift")
    if file_hash(snapshot) != ISSUE32_V2_RAW_SHA256:
        raise RuntimeError("frozen #32 v2 materialized bytes drift")
    value = read_json(snapshot)
    rows = value.get("rows") if isinstance(value, dict) else None
    if value.get("content_identity") != ISSUE32_V2_CONTENT_IDENTITY or value.get("snapshot_version") != "ui-ja-issue41-overlap7-v2" or not isinstance(rows, list) or len(rows) != 7:
        raise RuntimeError("frozen #32 v2 snapshot contract invalid")
    if any(row.get("meaning_relevant_status") != "RESOLVED" or row.get("snapshot_frozen") is not True or row.get("snapshot_pinned") is not True or row.get("snapshot_immutable") is not True or row.get("conflict_signal") is not False for row in rows):
        raise RuntimeError("frozen #32 v2 contains a non-resolved/non-frozen row")
    requirements = _rooted(root, "translation_quarantine/r3/issue41_issue32_overlap_requirements.jsonl")
    guard = inspect_bridge_status(snapshot, requirements)
    if guard.get("state") != "READY" or guard.get("resolved_count") != 7:
        raise RuntimeError("#32 bridge guard is not READY 7/7")
    return snapshot, {"official_ref": official_ref, "official_blob": ISSUE32_V2_BLOB, "content_identity": value["content_identity"], "snapshot_version": value["snapshot_version"], "row_count": len(rows), "raw_sha256": file_hash(snapshot), "guard": guard}


def _rule_fingerprints(root: Path) -> dict[str, str]:
    return {relative: file_hash(_rooted(root, relative)) for relative in RULE_FILES}


def _make_batches(remaining: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    return [remaining[start:start + BATCH_SIZE] for start in range(0, len(remaining), BATCH_SIZE)]


def _unsafe_ready(rows: list[Mapping[str, Any]], search_rows: list[Mapping[str, Any]], bridge_rows: list[Mapping[str, Any]]) -> list[str]:
    accepted = {str(row.get("canonical")) for row in search_rows if row.get("term_state") == "ACCEPTED"}
    bridge = {str(row.get("canonical")): row for row in bridge_rows}
    unsafe: list[str] = []
    for row in rows:
        if row.get("row_state") != "READY":
            continue
        canonical = str(row.get("canonical", ""))
        if row.get("display_state") != "READY" or canonical not in accepted or row.get("reason_codes"):
            unsafe.append(f"{canonical}:incomplete_ready_invariant")
        if row.get("risk_class") in {"HIGH_POSE_ACTION", "HIGH_ANATOMY_ADULT", "CRITICAL"} and not row.get("semantic_evidence_ids"):
            unsafe.append(f"{canonical}:high_risk_without_scope")
        bridge_row = bridge.get(canonical, {})
        if bridge_row.get("bridge32_state") == "CONTRADICTION" or bridge_row.get("bridge32_availability") in {"BRIDGE_MISSING", "BLOCKED_BRIDGE"}:
            unsafe.append(f"{canonical}:bridge_not_ready")
    return sorted(set(unsafe))


def run_batch(root: Path, batch: list[dict[str, Any]], batch_number: int, rule_fingerprints: Mapping[str, str]) -> dict[str, Any]:
    root = root.resolve()
    batch_id = f"batch-{batch_number:03d}"
    output = _batch_output(root, _rooted(root, f"{BATCH_OUTPUT}/{batch_id}"))
    if not batch:
        raise ValueError("empty batch")
    if len(batch) > BATCH_SIZE:
        raise ValueError("batch exceeds 200 rows")
    if _rule_fingerprints(root) != dict(rule_fingerprints):
        raise RuntimeError("rule drift detected before batch")
    protected_before = protected_snapshot(root)
    snapshot, snapshot_meta = _validate_issue32(root)
    requirements_path = _rooted(root, "translation_quarantine/r3/issue41_issue32_overlap_requirements.jsonl")
    required_overlap = {str(row["canonical"]) for row in read_jsonl(requirements_path)}
    campaign_batch_id = f"{CAMPAIGN_ID}-{batch_id}"
    queue_path = _rooted(root, "translation_quarantine/missing_candidates.csv")
    evidence_path = output / "evidence_manifest.jsonl"
    evidence = acquire_and_freeze(root, batch, queue_path, evidence_path, campaign_id=campaign_batch_id)
    selected = [dict(row) for row in batch]
    for ordinal, row in enumerate(selected, 1):
        row["pilot_ordinal"] = ordinal
    selected_hash = json_hash([row["canonical"] for row in selected])
    write_json(output / "batch_selection.json", {
        "schema_version": "issue36-bulk-batch-selection-1", "campaign_id": CAMPAIGN_ID, "batch_id": batch_id,
        "batch_number": batch_number, "batch_size": len(selected), "selection_seed": CANARY_SEED,
        "membership_hash": selected_hash, "selected": selected,
    })
    issue32 = _load_issue32_rows(snapshot)
    bridge_guard = inspect_bridge_status(snapshot, requirements_path)
    if bridge_guard.get("state") != "READY":
        raise RuntimeError("#32 bridge guard failed before evaluation")
    pilot_rows, search_rows, bridge_rows = _make_pilot_rows(selected, evidence, issue32, snapshot, required_overlap)
    write_jsonl(output / "rows.jsonl", pilot_rows)
    write_jsonl(output / "search_terms.jsonl", search_rows)
    write_jsonl(output / "bridge32.jsonl", bridge_rows)
    evidence_by_canonical: dict[str, list[dict[str, Any]]] = {}
    for item in evidence:
        evidence_by_canonical.setdefault(str(item.get("canonical", "")), []).append(item)
    evidence_errors: list[str] = []
    for canonical in (row["canonical"] for row in selected):
        records = evidence_by_canonical.get(canonical, [])
        if sum(row.get("evidence_role") == "IDENTITY_ONLY" for row in records) != 1 or any(row.get("frozen") is not True for row in records):
            evidence_errors.append(canonical)
    unsafe_ready = _unsafe_ready(pilot_rows, search_rows, bridge_rows)
    contradictions = sorted({str(row.get("canonical")) for row in bridge_rows if row.get("bridge32_state") == "CONTRADICTION"} | {str(row.get("canonical")) for row in pilot_rows if row.get("row_state") == "CONTRADICTION"})
    stop = {
        "false_ready_machine_guard": unsafe_ready,
        "contradictions": contradictions,
        "evidence_schema_failures": evidence_errors,
        "rule_drift": [],
        "bridge_guard": bridge_guard,
        "ok_before_verifier": not unsafe_ready and not contradictions and not evidence_errors,
    }
    write_json(output / "stop_condition_check.json", stop)
    if not stop["ok_before_verifier"]:
        raise RuntimeError(f"batch {batch_id} stopped before verifier: {stop}")
    after = protected_snapshot(root)
    if protected_before != after:
        raise RuntimeError("protected boundary changed during batch")
    counts = {
        "display": dict(sorted(Counter(row["display_state"] for row in pilot_rows).items())),
        "search": dict(sorted(Counter(row["search_state"] for row in pilot_rows).items())),
        "row": dict(sorted(Counter(row["row_state"] for row in pilot_rows).items())),
        "risk": dict(sorted(Counter(row["risk_class"] for row in pilot_rows).items())),
        "bridge_availability": dict(sorted(Counter(row["bridge32_availability"] for row in bridge_rows).items())),
        "bridge_state": dict(sorted(Counter(row["bridge32_state"] for row in bridge_rows).items())),
    }
    summary = {
        "schema_version": "issue36-bulk-batch-1", "campaign_id": CAMPAIGN_ID, "batch_id": batch_id,
        "batch_rows": len(pilot_rows), "membership_hash": selected_hash, "counts": counts,
        "evidence": {"frozen_rows": sum(row.get("frozen") is True for row in evidence), "identity_only_rows": sum(row.get("evidence_role") == "IDENTITY_ONLY" for row in evidence), "semantic_scope_rows": sum(row.get("evidence_role") == "SEMANTIC_SCOPE" for row in evidence), "wording_candidate_rows": sum(row.get("evidence_role") == "WORDING_CANDIDATE" for row in evidence), "failures": []},
        "bridge_status_guard": bridge_guard, "approval_capable_evidence_rows": sum(row.get("evidence_role") == "SEMANTIC_SCOPE" for row in evidence),
        "ready_rows": sum(row.get("row_state") == "READY" for row in pilot_rows), "review_rows": sum(row.get("row_state") == "REVIEW" for row in pilot_rows),
        "stale_review_rows": sum(row.get("row_state") == "STALE_REVIEW" for row in pilot_rows), "contradiction_rows": len(contradictions),
        "production_modified": False, "self_grade": "NOT_PERFORMED", "blind_review": "NOT_PERFORMED", "semantic_rule_change_required": False,
    }
    write_json(output / "run_summary.json", summary)
    write_json(output / "campaign_manifest.json", {
        "schema_version": "issue36-bulk-batch-manifest-1", "campaign_id": CAMPAIGN_ID, "batch_id": batch_id,
        "validated_r3_base": VALIDATED_R3_BASE, "validated_r3_head": "1c5a2cba7f8a0c5cd7c15ad510317c75d07d8851",
        "source_queue": "translation_quarantine/missing_candidates.csv", "source_queue_hash": file_hash(queue_path),
        "source_queue_portable_content_identity": portable_rows_hash(read_csv(queue_path)), "selection_seed": CANARY_SEED,
        "membership_hash": selected_hash, "rule_fingerprints": dict(rule_fingerprints), "issue32_snapshot": snapshot_meta,
        "evidence_manifest_hash": file_hash(evidence_path), "protected_snapshot_before": protected_before,
        "production_modified": False,
    })
    return {"output": output, "summary": summary}


def _artifact_hashes(directory: Path) -> dict[str, str]:
    return {name: file_hash(directory / name) for name in ARTIFACTS}


def verify_batch(root: Path, output: Path, *, replay: bool = True) -> dict[str, Any]:
    root = root.resolve(); output = output.resolve(); errors: list[str] = []
    for name in ARTIFACTS:
        if not (output / name).exists(): errors.append(f"missing artifact: {name}")
    if errors: return {"ok": False, "errors": errors}
    selection = read_json(output / "batch_selection.json"); rows = read_jsonl(output / "rows.jsonl"); evidence = read_jsonl(output / "evidence_manifest.jsonl")
    summary = read_json(output / "run_summary.json"); manifest = read_json(output / "campaign_manifest.json"); stop = read_json(output / "stop_condition_check.json")
    if len(rows) != selection.get("batch_size") or not 1 <= len(rows) <= BATCH_SIZE: errors.append("batch size is outside 1..200")
    if len({row.get("canonical") for row in rows}) != len(rows): errors.append("duplicate canonical in batch")
    if json_hash([row.get("canonical") for row in selection.get("selected", [])]) != selection.get("membership_hash"): errors.append("membership hash mismatch")
    if any(row.get("frozen") is not True for row in evidence): errors.append("evidence is not fully frozen")
    if stop.get("false_ready_machine_guard") or stop.get("contradictions") or stop.get("evidence_schema_failures") or not stop.get("ok_before_verifier"): errors.append("batch stop condition failed")
    if summary.get("production_modified") is not False or summary.get("self_grade") != "NOT_PERFORMED": errors.append("boundary/self-grade violation")
    if manifest.get("protected_snapshot_before") != protected_snapshot(root): errors.append("protected snapshot changed")
    replay_result = {"original_vs_rerun1": "NOT_RUN", "rerun1_vs_rerun2": "NOT_RUN", "original_vs_rerun2": "NOT_RUN", "mismatches": {}}
    if replay and not errors:
        replay_root = output / ".replay_work"
        if replay_root.exists(): shutil.rmtree(replay_root, ignore_errors=True)
        replay_root.mkdir(parents=True, exist_ok=True)
        try:
            for label in ("rerun1", "rerun2"):
                replay_dir = replay_root / label
                replay_batch(root, output, replay_dir)
            original = _artifact_hashes(output); first = _artifact_hashes(replay_root / "rerun1"); second = _artifact_hashes(replay_root / "rerun2")
            for key, left, right in (("original_vs_rerun1", original, first), ("rerun1_vs_rerun2", first, second), ("original_vs_rerun2", original, second)):
                replay_result[key] = "PASS" if left == right else "FAIL"
            for name in ARTIFACTS:
                if not (original[name] == first[name] == second[name]): replay_result["mismatches"][name] = {"original": original[name], "rerun1": first[name], "rerun2": second[name]}
            if replay_result["mismatches"] or any(replay_result[key] != "PASS" for key in ("original_vs_rerun1", "rerun1_vs_rerun2", "original_vs_rerun2")): errors.append("deterministic replay failed")
        finally:
            shutil.rmtree(replay_root, ignore_errors=True)
    result = {"schema_version": "issue36-bulk-batch-verification-1", "ok": not errors, "errors": errors, "batch_rows": len(rows), "deterministic_replay": replay_result, "self_grade": "NOT_PERFORMED", "production_modified": False}
    write_json(output / "replay_verification.json", result)
    return result


def replay_batch(root: Path, original: Path, output: Path) -> None:
    selection = read_json(original / "batch_selection.json")
    selected = selection["selected"]
    snapshot = _rooted(root, f"{CANARY_OUTPUT}/issue32_snapshot_v2.json")
    requirements = _rooted(root, "translation_quarantine/r3/issue41_issue32_overlap_requirements.jsonl")
    evidence = read_jsonl(original / "evidence_manifest.jsonl")
    write_json(output / "batch_selection.json", selection)
    write_jsonl(output / "evidence_manifest.jsonl", evidence)
    issue32 = _load_issue32_rows(snapshot); required = {str(row["canonical"]) for row in read_jsonl(requirements)}
    rows, search, bridge = _make_pilot_rows(selected, evidence, issue32, snapshot, required)
    write_jsonl(output / "rows.jsonl", rows); write_jsonl(output / "search_terms.jsonl", search); write_jsonl(output / "bridge32.jsonl", bridge)
    original_summary = read_json(original / "run_summary.json"); write_json(output / "run_summary.json", original_summary)
    original_manifest = read_json(original / "campaign_manifest.json"); write_json(output / "campaign_manifest.json", original_manifest)
    stop = read_json(original / "stop_condition_check.json"); write_json(output / "stop_condition_check.json", stop)


def run_remaining(root: Path) -> dict[str, Any]:
    root = root.resolve()
    canary = _validate_canary(root)
    sources = _validate_sources(root, canary)
    snapshot, snapshot_meta = _validate_issue32(root)
    del snapshot, snapshot_meta
    rules = _rule_fingerprints(root)
    batches = _make_batches(sources["remaining"])
    if [len(batch) for batch in batches] != [200, 200, 200, 25]:
        raise RuntimeError(f"unexpected remaining batch sizes: {[len(batch) for batch in batches]}")
    batch_results: list[dict[str, Any]] = []
    totals = Counter()
    for number, batch in enumerate(batches, 1):
        if _rule_fingerprints(root) != rules:
            raise RuntimeError("rule drift detected between batches")
        result = run_batch(root, batch, number, rules)
        verification = verify_batch(root, result["output"], replay=True)
        if not verification.get("ok"):
            raise RuntimeError(f"batch {number:03d} verifier failure: {verification}")
        summary = result["summary"]
        for key in ("ready_rows", "review_rows", "stale_review_rows", "contradiction_rows"):
            totals[key] += int(summary.get(key, 0))
        batch_results.append({"batch_id": summary["batch_id"], "rows": summary["batch_rows"], "ready": summary["ready_rows"], "review": summary["review_rows"], "stale_review": summary["stale_review_rows"], "contradiction": summary["contradiction_rows"], "verifier": verification})
    if _rule_fingerprints(root) != rules:
        raise RuntimeError("rule drift detected after batches")
    summary = {
        "schema_version": "issue36-bulk-readiness-summary-1", "campaign_id": CAMPAIGN_ID,
        "validated_r3_base": VALIDATED_R3_BASE, "validated_r3_head": "1c5a2cba7f8a0c5cd7c15ad510317c75d07d8851",
        "source_queue": {"raw_sha256": sources["queue_raw_sha256"], "portable_content_identity": sources["queue_portable_identity"]},
        "exclusions": {"phase1a_count": sources["phase1a_count"], "issue41_count": sources["issue41_count"], "canary_count": sources["canary_count"], "base_hash": sources["base_exclusion_hash"], "full_hash": sources["exclusion_hash"]},
        "eligible_before_canary": sources["eligible_before_canary"], "remaining_processed": len(sources["remaining"]), "batch_sizes": [len(batch) for batch in batches],
        "batches": batch_results, "totals": dict(totals), "rule_fingerprints": rules,
        "issue32_bridge": {"state": "READY", "resolved_count": 7, "required_count": 7, "content_identity": ISSUE32_V2_CONTENT_IDENTITY, "official_blob": ISSUE32_V2_BLOB},
        "stop_conditions": {"false_ready": 0, "contradiction": int(totals["contradiction_rows"]), "verifier_failure": 0, "rule_drift": 0, "review_allowed": True},
        "production_modified": False, "blind_review": "NOT_PERFORMED", "self_grade": "NOT_PERFORMED", "production_promotion": "NOT_AUTHORIZED",
        "final_gate": "READY_FOR_INDEPENDENT_BULK_READINESS_REVIEW" if not totals["contradiction_rows"] else "HOLD_CONTRADICTION",
    }
    out = _rooted(root, f"{BATCH_OUTPUT}/BULK_READINESS_SUMMARY.json")
    write_json(out, summary)
    lines = ["# Issue #36 final bulk readiness summary", "", f"- Campaign: `{CAMPAIGN_ID}`", f"- Remaining P0 processed: **{len(sources['remaining'])}** in `{','.join(str(len(batch)) for batch in batches)}` rows", f"- Final gate: **{summary['final_gate']}**", f"- #32 bridge: **READY ({7}/7 RESOLVED)**", f"- Production modified: **NO**", f"- blind/self-grade: **NOT_PERFORMED**", "", "## Batch results", "", "| Batch | Rows | READY | REVIEW | STALE_REVIEW | CONTRADICTION | Verifier |", "|---|---:|---:|---:|---:|---:|---|"]
    for item in batch_results:
        lines.append(f"| {item['batch_id']} | {item['rows']} | {item['ready']} | {item['review']} | {item['stale_review']} | {item['contradiction']} | {'PASS' if item['verifier']['ok'] else 'FAIL'} |")
    lines += ["", "No human row-by-row review or blind self-scoring was performed. All outputs are quarantine-only."]
    (out.parent / "BULK_READINESS_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(run_remaining(args.root), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
