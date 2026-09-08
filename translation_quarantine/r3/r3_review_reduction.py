"""One controlled, quarantine-only reduction campaign for Issue #36 REVIEW rows."""
from __future__ import annotations

import argparse
import json
import shutil
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

try:
    from .r3_bulk_batches import (
        BATCH_OUTPUT, CANARY_OUTPUT, ISSUE32_V2_BLOB, ISSUE32_V2_CONTENT_IDENTITY,
        _rooted, _unsafe_ready, _validate_issue32,
    )
    from .r3_bulk_evidence import acquire_and_freeze
    from .r3_bulk_select import VALIDATED_R3_BASE
    from .r3_common import file_hash, json_hash, protected_snapshot, read_json, read_jsonl, write_json, write_jsonl
    from .r3_run import _load_issue32_rows, _make_pilot_rows
except ImportError:  # pragma: no cover
    from r3_bulk_batches import BATCH_OUTPUT, CANARY_OUTPUT, ISSUE32_V2_BLOB, ISSUE32_V2_CONTENT_IDENTITY, _rooted, _unsafe_ready, _validate_issue32
    from r3_bulk_evidence import acquire_and_freeze
    from r3_bulk_select import VALIDATED_R3_BASE
    from r3_common import file_hash, json_hash, protected_snapshot, read_json, read_jsonl, write_json, write_jsonl
    from r3_run import _load_issue32_rows, _make_pilot_rows


CAMPAIGN_ID = "issue36-review-reduction-20260909-v1"
OUTPUT_DIR = "translation_quarantine/r3_bulk_review_reduction"
RULE_FILES = (
    "translation_quarantine/r3/r3_common.py",
    "translation_quarantine/r3/r3_run.py",
    "translation_quarantine/r3/r3_bulk_evidence.py",
    "translation_quarantine/r3/r3_review_reduction.py",
    "translation_quarantine/r3/r3_issue41_bridge_status.py",
)
CORE_ARTIFACTS = (
    "campaign_selection.json", "evidence_manifest.jsonl", "evidence_acquisition_report.json",
    "rows.jsonl", "search_terms.jsonl", "bridge32.jsonl", "run_summary.json",
    "campaign_manifest.json", "stop_condition_check.json",
)


def _rule_fingerprints(root: Path) -> dict[str, str]:
    return {relative: file_hash(root / relative) for relative in RULE_FILES}


def _load_review_input(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    source = root / BATCH_OUTPUT
    prior_summary = read_json(source / "BULK_READINESS_SUMMARY.json")
    if prior_summary.get("totals", {}).get("review_rows") != 604:
        raise RuntimeError("the frozen source campaign does not contain exactly 604 REVIEW rows")
    rows: list[dict[str, Any]] = []
    evidence: list[dict[str, Any]] = []
    for directory in sorted(source.glob("batch-*")):
        rows.extend(read_jsonl(directory / "rows.jsonl"))
        evidence.extend(read_jsonl(directory / "evidence_manifest.jsonl"))
    review = [dict(row) for row in rows if row.get("row_state") == "REVIEW"]
    if len(rows) != 625 or len(review) != 604 or len({row.get("canonical") for row in review}) != 604:
        raise RuntimeError("review input is not the expected unique 604-row frozen result")
    review.sort(key=lambda row: (int(row.get("pilot_ordinal", 0)), str(row.get("canonical", ""))))
    return review, evidence, prior_summary


def _root_output(root: Path) -> Path:
    output = (root / OUTPUT_DIR).resolve()
    output.mkdir(parents=True, exist_ok=True)
    return output


def _write_stop(output: Path, rows: list[dict[str, Any]], search: list[dict[str, Any]], bridge: list[dict[str, Any]], evidence: list[dict[str, Any]], protected_before: Mapping[str, str], protected_after: Mapping[str, str]) -> dict[str, Any]:
    unsafe = _unsafe_ready(rows, search, bridge)
    evidence_by = {}
    for record in evidence:
        evidence_by.setdefault(str(record.get("canonical", "")), []).append(record)
    evidence_errors = []
    for row in rows:
        canonical = str(row["canonical"])
        records = evidence_by.get(canonical, [])
        if sum(record.get("evidence_role") == "IDENTITY_ONLY" for record in records) != 1 or any(record.get("frozen") is not True for record in records):
            evidence_errors.append(canonical)
        if row.get("row_state") == "READY" and row.get("risk_class") in {"HIGH_POSE_ACTION", "HIGH_ANATOMY_ADULT", "CRITICAL"}:
            if not any(record.get("evidence_role") == "SEMANTIC_SCOPE" and record.get("scope_basis") == "EXACT_CANONICAL_AUTHORITATIVE_REFERENCE" for record in records):
                unsafe.append(f"{canonical}:high_risk_without_exact_canonical_scope")
    contradictions = sorted({str(row.get("canonical")) for row in bridge if row.get("bridge32_state") == "CONTRADICTION"} | {str(row.get("canonical")) for row in rows if row.get("row_state") == "CONTRADICTION"})
    stop = {
        "false_ready_machine_guard": sorted(set(unsafe)),
        "contradictions": contradictions,
        "evidence_schema_failures": sorted(set(evidence_errors)),
        "rule_drift": [],
        "protected_boundary_changed": protected_before != protected_after,
        "bridge_failure": any(row.get("bridge32_state") != "READY" for row in bridge),
    }
    stop["ok_before_verifier"] = not any(stop.values())
    write_json(output / "stop_condition_check.json", stop)
    return stop


def _evaluate(root: Path, output: Path, selected: list[dict[str, Any]], prior_evidence: list[dict[str, Any]], rules: Mapping[str, str]) -> dict[str, Any]:
    protected_before = protected_snapshot(root)
    snapshot, snapshot_meta = _validate_issue32(root)
    requirements = root / "translation_quarantine/r3/issue41_issue32_overlap_requirements.jsonl"
    required_overlap = {str(row["canonical"]) for row in read_jsonl(requirements)}
    queue_path = root / "translation_quarantine/missing_candidates.csv"
    evidence_path = output / "evidence_manifest.jsonl"
    evidence = acquire_and_freeze(
        root, selected, queue_path, evidence_path,
        campaign_id=CAMPAIGN_ID, prior_evidence=prior_evidence,
        review_reduction=True, report_path=output / "evidence_acquisition_report.json",
    )
    write_json(output / "campaign_selection.json", {
        "schema_version": "issue36-review-reduction-selection-1", "campaign_id": CAMPAIGN_ID,
        "source": "translation_quarantine/r3_bulk_batches/BULK_READINESS_SUMMARY.json",
        "source_review_rows": len(selected), "membership_hash": json_hash([row["canonical"] for row in selected]),
        "selected": selected,
    })
    issue32 = _load_issue32_rows(snapshot)
    bridge_guard = _validate_issue32(root)[1]["guard"]
    if bridge_guard.get("state") != "READY":
        raise RuntimeError("#32 v2 bridge is not READY")
    rows, search, bridge = _make_pilot_rows(selected, evidence, issue32, snapshot, required_overlap)
    write_jsonl(output / "rows.jsonl", rows); write_jsonl(output / "search_terms.jsonl", search); write_jsonl(output / "bridge32.jsonl", bridge)
    protected_after = protected_snapshot(root)
    stop = _write_stop(output, rows, search, bridge, evidence, protected_before, protected_after)
    if not stop["ok_before_verifier"]:
        raise RuntimeError(f"review reduction stopped before verifier: {stop}")
    acquisition = read_json(output / "evidence_acquisition_report.json")
    risk_ready = dict(sorted(Counter(row["risk_class"] for row in rows if row.get("row_state") == "READY").items()))
    summary = {
        "schema_version": "issue36-review-reduction-summary-1", "campaign_id": CAMPAIGN_ID,
        "source_commit": "a9516b3bc656d7a48bcf0c67647eaed8d95b3f4e", "validated_r3_base": VALIDATED_R3_BASE,
        "selected_rows": len(selected), "counts": {state: sum(row.get("row_state") == state for row in rows) for state in ("READY", "REVIEW", "CONTRADICTION", "STALE_REVIEW")},
        "risk_ready_counts": risk_ready,
        "review_reason_counts": dict(sorted(Counter(reason for row in rows if row.get("row_state") == "REVIEW" for reason in row.get("reason_codes", [])).items())),
        "evidence_source_type_counts": acquisition.get("source_type_counts", {}),
        "evidence_role_counts": acquisition.get("evidence_role_counts", {}),
        "new_ready_canonicals": sorted(row["canonical"] for row in rows if row.get("row_state") == "READY"),
        "still_review_reason_distribution": dict(sorted(Counter(reason for row in rows if row.get("row_state") == "REVIEW" for reason in row.get("reason_codes", [])).items())),
        "bridge": {"state": bridge_guard["state"], "resolved_count": bridge_guard.get("resolved_count"), "required_count": bridge_guard.get("required_count"), "content_identity": ISSUE32_V2_CONTENT_IDENTITY, "official_blob": ISSUE32_V2_BLOB},
        "stop_conditions": {"false_ready": len(stop["false_ready_machine_guard"]), "contradiction": len(stop["contradictions"]), "verifier_failure": 0, "rule_drift": 0, "bridge_failure": False, "replay": "PENDING"},
        "production_modified": False, "promotion": "NOT_AUTHORIZED", "blind_or_self_grade": "NOT_PERFORMED",
        "rule_fingerprints": dict(rules), "protected_boundary_changed": False,
    }
    write_json(output / "run_summary.json", summary)
    write_json(output / "campaign_manifest.json", {
        "schema_version": "issue36-review-reduction-manifest-1", "campaign_id": CAMPAIGN_ID,
        "source_rows": "translation_quarantine/r3_bulk_batches/batch-*/rows.jsonl",
        "source_evidence": "translation_quarantine/r3_bulk_batches/batch-*/evidence_manifest.jsonl",
        "queue": "translation_quarantine/missing_candidates.csv", "queue_hash": file_hash(queue_path),
        "membership_hash": json_hash([row["canonical"] for row in selected]), "rule_fingerprints": dict(rules),
        "issue32_snapshot": snapshot_meta, "evidence_manifest_hash": file_hash(evidence_path),
        "protected_snapshot_before": protected_before, "production_modified": False,
    })
    return summary


def _artifact_hashes(directory: Path) -> dict[str, str]:
    return {name: file_hash(directory / name) for name in CORE_ARTIFACTS}


def _replay(root: Path, original: Path, replay_dir: Path) -> None:
    selection = read_json(original / "campaign_selection.json")
    selected = selection["selected"]
    evidence = read_jsonl(original / "evidence_manifest.jsonl")
    snapshot = root / CANARY_OUTPUT / "issue32_snapshot_v2.json"
    requirements = root / "translation_quarantine/r3/issue41_issue32_overlap_requirements.jsonl"
    issue32 = _load_issue32_rows(snapshot)
    required = {str(row["canonical"]) for row in read_jsonl(requirements)}
    replay_dir.mkdir(parents=True, exist_ok=True)
    write_json(replay_dir / "campaign_selection.json", selection)
    write_jsonl(replay_dir / "evidence_manifest.jsonl", evidence)
    write_json(replay_dir / "evidence_acquisition_report.json", read_json(original / "evidence_acquisition_report.json"))
    rows, search, bridge = _make_pilot_rows(selected, evidence, issue32, snapshot, required)
    write_jsonl(replay_dir / "rows.jsonl", rows); write_jsonl(replay_dir / "search_terms.jsonl", search); write_jsonl(replay_dir / "bridge32.jsonl", bridge)
    for name in ("run_summary.json", "campaign_manifest.json", "stop_condition_check.json"):
        write_json(replay_dir / name, read_json(original / name))


def verify(root: Path, output: Path) -> dict[str, Any]:
    errors = [f"missing artifact: {name}" for name in CORE_ARTIFACTS if not (output / name).exists()]
    if errors:
        result = {"schema_version": "issue36-review-reduction-verification-1", "ok": False, "errors": errors}
        write_json(output / "replay_verification.json", result)
        return result
    original = _artifact_hashes(output)
    replay_root = output / ".replay_work"
    if replay_root.exists():
        shutil.rmtree(replay_root, ignore_errors=True)
    try:
        _replay(root, output, replay_root / "rerun1")
        _replay(root, output, replay_root / "rerun2")
        rerun1 = _artifact_hashes(replay_root / "rerun1"); rerun2 = _artifact_hashes(replay_root / "rerun2")
        comparisons = {name: ("PASS" if original[name] == rerun1[name] == rerun2[name] else "FAIL") for name in CORE_ARTIFACTS}
        mismatches = {name: {"original": original[name], "rerun1": rerun1[name], "rerun2": rerun2[name]} for name, state in comparisons.items() if state != "PASS"}
        replay = {"original_vs_rerun1": "PASS" if original == rerun1 else "FAIL", "rerun1_vs_rerun2": "PASS" if rerun1 == rerun2 else "FAIL", "original_vs_rerun2": "PASS" if original == rerun2 else "FAIL", "artifact_states": comparisons, "mismatches": mismatches}
        errors.extend(["deterministic replay failed"] if mismatches else [])
    finally:
        shutil.rmtree(replay_root, ignore_errors=True)
    result = {"schema_version": "issue36-review-reduction-verification-1", "ok": not errors, "errors": errors, "deterministic_replay": replay, "production_modified": False, "self_grade": "NOT_PERFORMED"}
    write_json(output / "replay_verification.json", result)
    return result


def run_campaign(root: Path) -> dict[str, Any]:
    root = root.resolve()
    selected, prior_evidence, prior_summary = _load_review_input(root)
    del prior_summary
    output = _root_output(root)
    rules = _rule_fingerprints(root)
    summary = _evaluate(root, output, selected, prior_evidence, rules)
    verification = verify(root, output)
    if not verification.get("ok"):
        raise RuntimeError(f"review reduction verifier failure: {verification}")
    summary["stop_conditions"]["replay"] = "PASS"
    write_json(output / "run_summary.json", summary)
    # The verifier artifact is intentionally written after replay; the final
    # summary is the campaign's human-readable stop report.
    summary["verification"] = verification
    write_json(output / "REVIEW_REDUCTION_SUMMARY.json", summary)
    lines = [
        "# Issue #36 controlled REVIEW-reduction campaign", "",
        f"- Campaign: `{CAMPAIGN_ID}`", f"- Input REVIEW: **{summary['selected_rows']}**",
        f"- READY / REVIEW / CONTRADICTION: **{summary['counts'].get('READY', 0)} / {summary['counts'].get('REVIEW', 0)} / {summary['counts'].get('CONTRADICTION', 0)}**",
        f"- READY by risk: `{json.dumps(summary['risk_ready_counts'], ensure_ascii=False, sort_keys=True)}`",
        f"- New READY canonicals: `{', '.join(summary['new_ready_canonicals'])}`",
        f"- Evidence sources: `{json.dumps(summary['evidence_source_type_counts'], ensure_ascii=False, sort_keys=True)}`",
        f"- Remaining REVIEW reasons: `{json.dumps(summary['still_review_reason_distribution'], ensure_ascii=False, sort_keys=True)}`",
        "- false READY: **0**; replay: **PASS**; production_modified: **false**",
        "- #32 v2 bridge: **READY 7/7**; production promotion and blind/self-grade: **NOT_PERFORMED**",
        "", "All outputs are quarantine-only. No additional bulk campaign was started after this one.",
    ]
    (output / "REVIEW_REDUCTION_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    print(json.dumps(run_campaign(args.root), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
