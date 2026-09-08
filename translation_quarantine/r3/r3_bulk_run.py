"""Run one bounded Issue #36 bulk canary around the unchanged R3 evaluator."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping

try:
    from .r3_common import RISK_ORDER, file_hash, json_hash, protected_snapshot, read_json, read_jsonl, stable_key, write_json, write_jsonl
    from .r3_issue41_bridge_status import inspect_bridge_status
    from .r3_run import _load_issue32_rows, _make_pilot_rows
    from .r3_bulk_select import CANARY_SIZE, CANARY_SEED, select_canary
    from .r3_bulk_evidence import acquire_and_freeze
except ImportError:  # pragma: no cover
    from r3_common import RISK_ORDER, file_hash, json_hash, protected_snapshot, read_json, read_jsonl, stable_key, write_json, write_jsonl
    from r3_issue41_bridge_status import inspect_bridge_status
    from r3_run import _load_issue32_rows, _make_pilot_rows
    from r3_bulk_select import CANARY_SIZE, CANARY_SEED, select_canary
    from r3_bulk_evidence import acquire_and_freeze


OUTPUT_NAME = "translation_quarantine/r3_bulk_canary"
AUDIT_SEED = "UIJA-R3-BULK-CANARY-AUDIT20-20260909-V1"
AUDIT_QUOTAS = {risk: 4 for risk in RISK_ORDER}
MASKED_FIELDS = {
    "risk_class", "display_state", "search_state", "bridge32_state", "bridge32_availability",
    "row_state", "reason_codes", "issue32_meaning_fingerprint", "issue32_content_identity",
    "issue32_conflict_signal", "prior_review_state", "review_state", "audit_key",
}


def _bulk_output(root: Path, output: Path) -> Path:
    allowed = (root / "translation_quarantine" / "r3_bulk_canary").resolve()
    output = output.resolve()
    try:
        output.relative_to(allowed)
    except ValueError as exc:
        raise ValueError(f"bulk output must stay below {allowed}") from exc
    output.mkdir(parents=True, exist_ok=True)
    return output


def _relative(root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


ISSUE32_V2_BLOB = "974bb9c971caf632f8ec73dff39fe4c55e60efaa"
ISSUE32_V2_CONTENT_IDENTITY = "sha256:7e46f7f3655846a4f6ea2d1990e015701cbff5b123bdf8ef1809668f8a375ef5"


def _git_output(root: Path, args: list[str]) -> str:
    import subprocess

    command = ["git", "-c", f"safe.directory={root}", *args]
    completed = subprocess.run(command, cwd=root, check=True, capture_output=True)
    return completed.stdout.decode("utf-8")


def _materialize_issue32_snapshot(root: Path, output: Path, git_ref: str) -> tuple[Path, dict[str, Any]]:
    if ":" not in git_ref:
        raise ValueError("--issue32-git-ref must be REF:PATH")
    ref, path = git_ref.split(":", 1)
    raw = _git_output(root, ["show", f"{ref}:{path}"]).encode("utf-8")
    blob = _git_output(root, ["rev-parse", f"{ref}:{path}"]).strip()
    if blob != ISSUE32_V2_BLOB:
        raise ValueError(f"official #32 v2 blob drifted: {blob}")
    target = output / "issue32_snapshot_v2.json"
    target.write_bytes(raw)
    value = json.loads(raw.decode("utf-8"))
    if not isinstance(value, dict) or value.get("snapshot_version") != "ui-ja-issue41-overlap7-v2":
        raise ValueError("official #32 v2 snapshot contract is invalid")
    rows = value.get("rows")
    if not isinstance(rows, list) or len(rows) != 7:
        raise ValueError("official #32 v2 snapshot must contain exactly 7 rows")
    if value.get("content_identity") != ISSUE32_V2_CONTENT_IDENTITY:
        raise ValueError("official #32 v2 content identity mismatch")
    if not all(
        row.get("meaning_relevant_status") == "RESOLVED"
        and row.get("snapshot_frozen") is True
        and row.get("snapshot_pinned") is True
        and row.get("snapshot_immutable") is True
        and row.get("conflict_signal") is False
        for row in rows
    ):
        raise ValueError("official #32 v2 rows are not all resolved/frozen/pinned/immutable")
    return target, {
        "origin_ref": git_ref,
        "origin_blob": blob,
        "origin_content_identity": value["content_identity"],
        "snapshot_version": value["snapshot_version"],
        "row_count": len(rows),
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
    }


def _snapshot_metadata(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists() or path.suffix.lower() != ".json":
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    return {
        "origin_ref": str(value.get("snapshot_ref", "")),
        "origin_blob": "",
        "origin_content_identity": str(value.get("content_identity", "")),
        "snapshot_version": str(value.get("snapshot_version", "")),
        "row_count": len(value.get("rows", [])) if isinstance(value, dict) else 0,
        "raw_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def _audit_package(rows: list[dict[str, Any]], search_rows: list[dict[str, Any]], evidence: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    by_search: dict[str, list[dict[str, Any]]] = {}
    for row in search_rows:
        by_search.setdefault(str(row["canonical"]), []).append({"term": row["term"], "term_class": row["term_class"]})
    by_evidence: dict[str, list[dict[str, Any]]] = {}
    for row in evidence:
        by_evidence.setdefault(str(row["canonical"]), []).append(row)
    grouped: dict[str, list[dict[str, Any]]] = {risk: [] for risk in RISK_ORDER}
    for row in rows:
        item = dict(row)
        item["audit_key"] = stable_key(AUDIT_SEED, str(row["canonical"]))
        grouped.setdefault(str(row["risk_class"]), []).append(item)
    overlap = {row["canonical"] for row in rows if row.get("issue32_overlap") == "YES"}
    for risk in grouped:
        grouped[risk].sort(key=lambda item: (
            0 if item.get("row_state") == "READY" else 1,
            0 if item["canonical"] in overlap else 1,
            item["audit_key"],
            item["canonical"],
        ))
    quotas = {
        risk: min(AUDIT_QUOTAS[risk], len(grouped.get(risk, [])))
        for risk in RISK_ORDER
    }
    remaining = 20 - sum(quotas.values())
    while remaining:
        progressed = False
        for risk in RISK_ORDER:
            if quotas[risk] >= len(grouped.get(risk, [])):
                continue
            quotas[risk] += 1
            remaining -= 1
            progressed = True
            if not remaining:
                break
        if not progressed:
            raise ValueError("canary has fewer than 20 rows for the masked audit20")

    selected: list[dict[str, Any]] = []
    for risk in RISK_ORDER:
        for row in grouped.get(risk, [])[: quotas[risk]]:
            selected.append(row)
    if len(selected) != 20:
        raise ValueError("cannot form the stratified audit20")
    selected.sort(key=lambda row: (row["audit_key"], row["canonical"]))
    masked = []
    key_rows = []
    for row in selected:
        canonical = str(row["canonical"])
        masked.append({
            "canonical": canonical,
            "candidate_display": row.get("display_candidate", ""),
            "search_terms": by_search.get(canonical, []),
            "semantic_evidence": [
                {"evidence_id": item["evidence_id"], "scope_note": item.get("scope_note", ""), "source_ref": item.get("source_ref", "")}
                for item in by_evidence.get(canonical, []) if item.get("evidence_role") == "SEMANTIC_SCOPE"
            ],
            "issue32_snapshot_evidence": [
                {"evidence_id": item["evidence_id"], "scope_note": item.get("scope_note", ""), "source_ref": item.get("source_ref", "")}
                for item in by_evidence.get(canonical, []) if item.get("evidence_role") == "BRIDGE32"
            ],
        })
        key_rows.append({
            "canonical": canonical,
            "audit_key": row["audit_key"],
            "effective_risk_class": row.get("risk_class", ""),
            "display_state": row.get("display_state", ""),
            "search_state": row.get("search_state", ""),
            "bridge32_state": row.get("bridge32_state", ""),
            "bridge32_availability": row.get("bridge32_availability", ""),
            "row_state": row.get("row_state", ""),
            "reason_codes": row.get("reason_codes", []),
        })
    key = {
        "schema_version": "issue36-bulk-audit20-key-1",
        "audit_seed": AUDIT_SEED,
        "requested_stratum_counts": dict(AUDIT_QUOTAS),
        "actual_stratum_counts": dict(quotas),
        "selected": key_rows,
    }
    return masked, key


def check_masked_rows(masked_rows: list[dict[str, Any]], key: dict[str, Any], serialized: str | None = None) -> dict[str, Any]:
    serialized = serialized if serialized is not None else json.dumps(masked_rows, ensure_ascii=False, sort_keys=True)
    leaked_fields = sorted(set().union(*(MASKED_FIELDS & set(row) for row in masked_rows))) if masked_rows else []
    key_hashes = [str(row.get("audit_key", "")) for row in key.get("selected", [])]
    leaked_key_values = sorted(value for value in key_hashes if value and value in serialized)
    forbidden_literals = sorted(value for value in ("READY", "STALE_REVIEW", "CONTRADICTION", "FALSE_APPROVAL", "REVIEW_PENDING") if value in serialized)
    return {
        "schema_version": "issue36-bulk-audit20-leakage-1",
        "masked_rows": len(masked_rows),
        "leaked_masked_fields": leaked_fields,
        "leaked_key_values": leaked_key_values,
        "forbidden_state_literals": forbidden_literals,
        "ok": not leaked_fields and not leaked_key_values and not forbidden_literals,
    }


def check_masked_leakage(masked_path: Path, key_path: Path) -> dict[str, Any]:
    masked_rows = read_jsonl(masked_path)
    key = read_json(key_path)
    return check_masked_rows(masked_rows, key, masked_path.read_text(encoding="utf-8"))


def run_campaign(
    root: Path,
    output_dir: Path,
    *,
    issue32_snapshot: Path | None = None,
    issue32_git_ref: str | None = None,
    evidence_path: Path | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    output = _bulk_output(root, output_dir)
    protected_before = protected_snapshot(root)
    snapshot_metadata: dict[str, Any] = _snapshot_metadata(issue32_snapshot)
    if issue32_git_ref:
        issue32_snapshot, snapshot_metadata = _materialize_issue32_snapshot(root, output, issue32_git_ref)
    selection = select_canary(root)
    selection_path = output / "canary_selection.json"
    write_json(selection_path, selection)
    selected = selection["selected"]
    queue_path = root / "translation_quarantine" / "missing_candidates.csv"
    frozen_evidence_path = evidence_path
    evidence_output_path = output / "evidence_manifest.jsonl"
    if frozen_evidence_path is not None and frozen_evidence_path.exists():
        evidence = read_jsonl(frozen_evidence_path)
        write_jsonl(evidence_output_path, evidence)
    else:
        evidence = acquire_and_freeze(root, selected, queue_path, evidence_output_path)
    requirements_path = root / "translation_quarantine" / "r3" / "issue41_issue32_overlap_requirements.jsonl"
    bridge_guard = inspect_bridge_status(issue32_snapshot, requirements_path if requirements_path.exists() else Path("missing-requirements.jsonl"))
    required_overlap = {str(row["canonical"]) for row in read_jsonl(requirements_path)} if requirements_path.exists() else set()
    issue32: dict[str, dict[str, Any]] = {}
    if issue32_snapshot and issue32_snapshot.exists():
        issue32 = _load_issue32_rows(issue32_snapshot)
    pilot_rows, search_rows, bridge_rows = _make_pilot_rows(selected, evidence, issue32, issue32_snapshot, required_overlap)
    rows_path = output / "rows.jsonl"
    search_path = output / "search_terms.jsonl"
    bridge_path = output / "bridge32.jsonl"
    write_jsonl(rows_path, pilot_rows)
    write_jsonl(search_path, search_rows)
    write_jsonl(bridge_path, bridge_rows)
    masked, key = _audit_package(pilot_rows, search_rows, evidence)
    masked_path = output / "masked_audit20_input.jsonl"
    key_path = output / "masked_audit20_key.json"
    write_jsonl(masked_path, masked)
    write_json(key_path, key)
    leakage = check_masked_leakage(masked_path, key_path)
    write_json(output / "leakage_check.json", leakage)
    after = protected_snapshot(root)
    if protected_before != after:
        raise RuntimeError("protected data boundary changed during bulk canary")
    counts = {
        "display": dict(sorted(Counter(row["display_state"] for row in pilot_rows).items())),
        "search": dict(sorted(Counter(row["search_state"] for row in pilot_rows).items())),
        "row": dict(sorted(Counter(row["row_state"] for row in pilot_rows).items())),
        "risk": dict(sorted(Counter(row["risk_class"] for row in pilot_rows).items())),
        "bridge_availability": dict(sorted(Counter(row["bridge32_availability"] for row in bridge_rows).items())),
        "bridge_state": dict(sorted(Counter(row["bridge32_state"] for row in bridge_rows).items())),
    }
    ready_rows = sum(row.get("row_state") == "READY" for row in pilot_rows)
    semantic_scope_rows = sum(row.get("evidence_role") == "SEMANTIC_SCOPE" for row in evidence)
    approval_evidence_state = (
        "APPROVAL_EVIDENCE_AVAILABLE"
        if ready_rows > 0 and semantic_scope_rows > 0
        else "HOLD_INSUFFICIENT_APPROVAL_EVIDENCE"
    )
    bridge_blocked = bridge_guard.get("state") != "READY"
    campaign_state = "HOLD_BRIDGE" if bridge_blocked else approval_evidence_state
    risk_coverage_gaps = [
        risk
        for risk in RISK_ORDER
        if selection["eligible_pool_effective_risk_distribution"].get(risk, 0)
        and selection["effective_risk_distribution"].get(risk, 0) == 0
    ]
    summary = {
        "schema_version": "issue36-bulk-canary-1",
        "campaign_id": selection["campaign_id"],
        "canary_rows": len(pilot_rows),
        "canary_membership_hash": selection["canary_membership_hash"],
        "effective_risk_distribution": counts["risk"],
        "eligible_pool_effective_risk_distribution": selection["eligible_pool_effective_risk_distribution"],
        "risk_coverage_gaps": risk_coverage_gaps,
        "representativeness_claim": "NOT_CLAIMED" if risk_coverage_gaps else "NATURAL_DISTRIBUTION_RECORDED",
        "counts": counts,
        "evidence": {
            "frozen_rows": sum(row.get("frozen") is True for row in evidence),
            "identity_only_rows": sum(row.get("evidence_role") == "IDENTITY_ONLY" for row in evidence),
            "semantic_scope_rows": sum(row.get("evidence_role") == "SEMANTIC_SCOPE" for row in evidence),
            "wording_candidate_rows": sum(row.get("evidence_role") == "WORDING_CANDIDATE" for row in evidence),
            "failures": [],
        },
        "bridge_status_guard": bridge_guard,
        "campaign_state": campaign_state,
        "approval_evidence_state": approval_evidence_state,
        "approval_capable_evidence_rows": semantic_scope_rows,
        "ready_rows": ready_rows,
        "audit20_rows": len(masked),
        "audit20_leakage_check": leakage,
        "semantic_rule_change_required": False,
        "production_modified": False,
        "remaining_full_p0_processed": False,
        "stage10_production_ab_started": False,
        "self_grade": "NOT_PERFORMED",
    }
    write_json(output / "run_summary.json", summary)
    write_json(output / "campaign_manifest.json", {
        "schema_version": "issue36-bulk-campaign-1",
        "campaign_id": selection["campaign_id"],
        "validated_r3_base": "53f02d9b3419db8fd9099b38204c29eed289ee8e",
        "validated_r3_head": "1c5a2cba7f8a0c5cd7c15ad510317c75d07d8851",
        "selection_seed": CANARY_SEED,
        "source_queue": selection["source_queue"],
        "source_queue_hash": selection["source_queue_hash"],
        "source_queue_portable_content_identity": selection["source_queue_portable_content_identity"],
        "exclusion_set_hash": selection["exclusion_set"]["hash"],
        "canary_membership_hash": selection["canary_membership_hash"],
        "artifact_hashes": {name: file_hash(output / name) for name in (
            "canary_selection.json", "evidence_manifest.jsonl", "rows.jsonl", "search_terms.jsonl",
            "bridge32.jsonl", "run_summary.json", "masked_audit20_input.jsonl", "masked_audit20_key.json", "leakage_check.json",
        )},
        "protected_snapshot_before": protected_before,
        "issue32_snapshot_ref": _relative(root, issue32_snapshot) if issue32_snapshot and issue32_snapshot.exists() else "",
        "issue32_snapshot_hash": file_hash(issue32_snapshot) if issue32_snapshot and issue32_snapshot.exists() else "",
        "issue32_snapshot_origin_ref": snapshot_metadata.get("origin_ref", ""),
        "issue32_snapshot_origin_blob": snapshot_metadata.get("origin_blob", ""),
        "issue32_snapshot_origin_content_identity": snapshot_metadata.get("origin_content_identity", ""),
        "issue32_snapshot_version": snapshot_metadata.get("snapshot_version", ""),
        "issue32_snapshot_row_count": snapshot_metadata.get("row_count", 0),
        "evidence_manifest_ref": _relative(root, evidence_output_path),
        "production_modified": False,
    })
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "r3_bulk_canary")
    parser.add_argument("--issue32-snapshot", type=Path)
    parser.add_argument("--issue32-git-ref", type=str)
    args = parser.parse_args()
    print(json.dumps(run_campaign(args.root, args.output, issue32_snapshot=args.issue32_snapshot, issue32_git_ref=args.issue32_git_ref), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
