"""Fail-closed validation and deterministic rerun verification for R3."""
from __future__ import annotations

import argparse
import shutil
import uuid
from pathlib import Path
from typing import Any, Iterable

try:
    from .r3_common import (
        BLIND_QUOTAS,
        BRIDGE_AVAILABILITIES,
        PILOT_QUOTAS,
        STATES,
        TERM_CLASSES,
        file_hash,
        issue32_fingerprint,
        protected_snapshot,
        read_json,
        read_jsonl,
        write_json,
    )
    from .r3_run import run
except ImportError:  # pragma: no cover - supports direct CLI execution
    from r3_common import BLIND_QUOTAS, BRIDGE_AVAILABILITIES, PILOT_QUOTAS, STATES, TERM_CLASSES, file_hash, issue32_fingerprint, protected_snapshot, read_json, read_jsonl, write_json
    from r3_run import run
try:
    from .r3_build_blind_audit import build
except ImportError:  # pragma: no cover - supports direct CLI execution
    from r3_build_blind_audit import build


PILOT_FIELDS = {
    "pilot_ordinal", "canonical", "lanes", "priority", "post_count_or_reference", "semantic_class",
    "risk_class", "semantic_scope_summary", "semantic_evidence_ids", "display_candidate",
    "display_state", "display_evidence_ids", "search_state", "bridge32_state", "bridge32_availability", "row_state",
    "issue32_overlap", "issue32_snapshot_ref", "issue32_content_identity", "issue32_meaning_fingerprint",
    "evaluated_issue32_meaning_fingerprint", "issue32_conflict_signal", "reason_codes",
}
SEARCH_FIELDS = {
    "canonical", "term", "term_class", "term_state", "evidence_ids", "justification", "rejection_reason",
}
BLIND_INPUT_FIELDS = {"canonical", "candidate_display", "search_terms", "semantic_evidence", "issue32_snapshot_evidence"}
MASKED_FIELDS = {
    "risk_class", "display_state", "search_state", "bridge32_state", "bridge32_availability", "row_state", "reason_codes",
    "issue32_meaning_fingerprint", "evaluated_issue32_meaning_fingerprint", "issue32_content_identity",
    "issue32_conflict_signal", "prior_review_state", "phase1a_qa", "review_state",
}
SEMANTIC_ARTIFACTS = (
    "pilot_selection.json", "evidence_manifest.jsonl", "pilot_rows.jsonl", "search_terms.jsonl",
    "bridge32.jsonl", "blind30_input.jsonl", "blind30_key.json", "blind30_review.jsonl", "run_summary.json",
)


def _errors_for_fields(rows: Iterable[dict[str, Any]], required: set[str], label: str) -> list[str]:
    errors: list[str] = []
    for index, row in enumerate(rows, 1):
        missing = required - set(row)
        if missing:
            errors.append(f"{label}[{index}] missing {sorted(missing)}")
    return errors


def _semantic_hashes(directory: Path) -> dict[str, str]:
    return {name: file_hash(directory / name) for name in SEMANTIC_ARTIFACTS}


def _align_replay_metadata(directory: Path, original_summary: dict[str, Any]) -> None:
    """Copy only verifier-owned metadata so it cannot cause replay drift."""

    summary_path = directory / "run_summary.json"
    summary = read_json(summary_path)
    for field in ("deterministic_rerun_verification", "deterministic_replay_comparison"):
        if field in original_summary:
            summary[field] = original_summary[field]
        else:
            summary.pop(field, None)
    write_json(summary_path, summary)


def verify(root: Path, output_dir: Path, *, rerun: bool = False) -> dict[str, Any]:
    root = root.resolve()
    output = output_dir.resolve()
    errors: list[str] = []
    if not output.is_dir() or output.parent != (root / "translation_quarantine").resolve():
        errors.append("output directory must be exactly root/translation_quarantine/r3")
    required_files = set(SEMANTIC_ARTIFACTS) | {"run_manifest.json"}
    for name in sorted(required_files):
        if not (output / name).exists():
            errors.append(f"missing artifact: {name}")
    if errors:
        return {"ok": False, "errors": errors}

    manifest = read_json(output / "run_manifest.json")
    selection = read_json(output / "pilot_selection.json")
    pilot_rows = read_jsonl(output / "pilot_rows.jsonl")
    search_rows = read_jsonl(output / "search_terms.jsonl")
    evidence_rows = read_jsonl(output / "evidence_manifest.jsonl")
    bridge_rows = read_jsonl(output / "bridge32.jsonl")
    blind_input = read_jsonl(output / "blind30_input.jsonl")
    blind_key = read_json(output / "blind30_key.json")
    blind_review = read_jsonl(output / "blind30_review.jsonl")
    summary = read_json(output / "run_summary.json")

    errors.extend(_errors_for_fields(pilot_rows, PILOT_FIELDS, "pilot_rows"))
    errors.extend(_errors_for_fields(search_rows, SEARCH_FIELDS, "search_terms"))
    required_evidence = {"evidence_id", "canonical", "source_type", "source_ref", "scope_note", "content_identity", "evidence_role", "frozen"}
    errors.extend(_errors_for_fields(evidence_rows, required_evidence, "evidence_manifest"))
    errors.extend(_errors_for_fields(bridge_rows, {
        "canonical", "snapshot_ref", "content_identity", "frozen", "pinned", "immutable",
        "meaning_fingerprint", "evaluated_issue32_meaning_fingerprint", "meaning_relevant_propositions",
        "bridge32_state", "bridge32_availability", "conflict_signal", "reason_codes",
    }, "bridge32"))
    errors.extend(_errors_for_fields(blind_input, BLIND_INPUT_FIELDS, "blind30_input"))
    errors.extend(_errors_for_fields(blind_review, {"canonical", "display_judgement", "search_judgement", "bridge32_judgement", "review_note"}, "blind30_review"))

    canonicals = [str(row.get("canonical", "")) for row in pilot_rows]
    if len(pilot_rows) != 100 or len(set(canonicals)) != 100:
        errors.append("pilot_rows must contain exactly 100 unique canonicals")
    ordinals = [row.get("pilot_ordinal") for row in pilot_rows]
    if sorted(ordinals) != list(range(1, 101)):
        errors.append("pilot ordinals must be 1..100")
    if set(row.get("row_state") for row in pilot_rows) - STATES:
        errors.append("pilot row has an invalid row_state")
    if set(row.get("display_state") for row in pilot_rows) - STATES:
        errors.append("pilot row has an invalid display_state")
    if set(row.get("search_state") for row in pilot_rows) - STATES:
        errors.append("pilot row has an invalid search_state")
    if set(row.get("bridge32_availability") for row in pilot_rows) - BRIDGE_AVAILABILITIES:
        errors.append("pilot row has an invalid bridge32_availability")
    if set(row.get("bridge32_availability") for row in bridge_rows) - BRIDGE_AVAILABILITIES:
        errors.append("bridge32 has an invalid bridge32_availability")
    if set(row.get("term_class") for row in search_rows) - TERM_CLASSES:
        errors.append("search_terms contains an invalid term_class")
    if set(row.get("risk_class") for row in pilot_rows) - set(PILOT_QUOTAS):
        errors.append("pilot row has an invalid risk_class")
    if len(selection.get("selected", [])) != 100:
        errors.append("pilot_selection must contain 100 selected rows")
    selected_canonicals = {row.get("canonical") for row in selection.get("selected", [])}
    if selected_canonicals != set(canonicals):
        errors.append("pilot_selection and pilot_rows canonical sets differ")
    if selection.get("eligible_pool", {}).get("excluded_count") != 100:
        errors.append("the existing Phase1A 100 regression fixtures were not preserved")
    if selection.get("selection_seed") != "UIJA-R3-PILOT-20260908-V1":
        errors.append("unexpected pilot selection seed")
    if summary.get("selected_stratum_counts") != selection.get("achieved_stratum_counts"):
        errors.append("run_summary selected stratum counts do not match pilot selection")
    if len(bridge_rows) != len(pilot_rows) or {row.get("canonical") for row in bridge_rows} != set(canonicals):
        errors.append("bridge32 must contain exactly one audit row per pilot canonical")
    bridge_by_canonical = {str(row.get("canonical")): row for row in bridge_rows}
    for row in pilot_rows:
        canonical = str(row.get("canonical"))
        bridge = bridge_by_canonical.get(canonical, {})
        availability = row.get("bridge32_availability")
        if bridge.get("bridge32_availability") != availability:
            errors.append(f"pilot/bridge availability mismatch for {canonical}")
        if availability == "NOT_REQUIRED" and row.get("issue32_overlap") != "NO":
            errors.append(f"NOT_REQUIRED row is marked as overlap for {canonical}")
        if availability != "NOT_REQUIRED" and row.get("issue32_overlap") != "YES":
            errors.append(f"required bridge row is not marked as overlap for {canonical}")
        if availability == "AVAILABLE":
            if any(not bridge.get(field) for field in ("snapshot_ref", "content_identity", "meaning_fingerprint")):
                errors.append(f"available bridge lacks immutable identity fields for {canonical}")
            if bridge.get("frozen") is not True or bridge.get("pinned") is not True or bridge.get("immutable") is not True:
                errors.append(f"available bridge is not frozen/pinned/immutable for {canonical}")
        propositions = bridge.get("meaning_relevant_propositions")
        stored_fingerprint = str(bridge.get("meaning_fingerprint", ""))
        if propositions and stored_fingerprint and issue32_fingerprint(propositions) != stored_fingerprint:
            errors.append(f"bridge fingerprint does not match propositions for {canonical}")
        if availability in {"BRIDGE_MISSING", "BLOCKED_BRIDGE"} and row.get("row_state") == "READY":
            errors.append(f"bridge failure allowed row READY for {canonical}")
    expected_audit = {
        "required_overlap_count": sum(row.get("bridge32_availability") != "NOT_REQUIRED" for row in bridge_rows),
        "available_count": sum(row.get("bridge32_availability") == "AVAILABLE" for row in bridge_rows),
        "not_required_count": sum(row.get("bridge32_availability") == "NOT_REQUIRED" for row in bridge_rows),
        "bridge_missing_count": sum(row.get("bridge32_availability") == "BRIDGE_MISSING" for row in bridge_rows),
        "blocked_bridge_count": sum(row.get("bridge32_availability") == "BLOCKED_BRIDGE" for row in bridge_rows),
        "stale_count": sum(row.get("bridge32_state") == "STALE_REVIEW" for row in bridge_rows),
        "contradiction_count": sum(row.get("bridge32_state") == "CONTRADICTION" for row in bridge_rows),
    }
    actual_audit = summary.get("bridge32_audit", {})
    for field, value in expected_audit.items():
        if actual_audit.get(field) != value:
            errors.append(f"run_summary bridge32_audit mismatch for {field}")
    audit_records = {str(row.get("canonical")): row for row in actual_audit.get("records", []) if isinstance(row, dict)}
    if set(audit_records) != set(bridge_by_canonical):
        errors.append("run_summary bridge32_audit records do not cover bridge32 rows")
    for canonical, bridge in bridge_by_canonical.items():
        audit = audit_records.get(canonical, {})
        expected_record = {
            "bridge32_availability": bridge.get("bridge32_availability"),
            "bridge32_state": bridge.get("bridge32_state"),
            "current_fingerprint": bridge.get("meaning_fingerprint"),
            "evaluated_fingerprint": bridge.get("evaluated_issue32_meaning_fingerprint"),
            "snapshot_ref": bridge.get("snapshot_ref"),
            "content_identity": bridge.get("content_identity"),
        }
        if any(audit.get(field) != value for field, value in expected_record.items()):
            errors.append(f"run_summary bridge32_audit record mismatch for {canonical}")
    if len(blind_input) != 30 or len(blind_key.get("selected", [])) != 30:
        errors.append("blind30 must contain exactly 30 selected rows")
    for row in blind_input:
        leaked = MASKED_FIELDS & set(row)
        if leaked:
            errors.append(f"blind30 input leaks masked fields: {sorted(leaked)}")
        for term in row.get("search_terms", []):
            if set(term) - {"term", "term_class"}:
                errors.append(f"blind30 input leaks search state for {row.get('canonical')}")
    if any(row.get("frozen") is not True for row in evidence_rows):
        errors.append("evidence manifest must be frozen")
    if summary.get("remaining_925_p0_processed") is not False:
        errors.append("remaining_925_p0_processed must be false")
    if summary.get("production_modified") is not False or manifest.get("production_modified") is not False:
        errors.append("production_modified must be false")

    before = manifest.get("protected_snapshot_before", {})
    after = protected_snapshot(root)
    if before != after:
        errors.append("protected production/#32/#35 files changed during the run")
    manifest_hashes = manifest.get("generated_file_hashes", {})
    for name in SEMANTIC_ARTIFACTS:
        if manifest_hashes.get(name) != file_hash(output / name):
            errors.append(f"manifest hash mismatch: {name}")

    rerun_result = "NOT_RUN"
    replay_comparison = {
        "original_vs_rerun1": "NOT_RUN",
        "rerun1_vs_rerun2": "NOT_RUN",
        "original_vs_rerun2": "NOT_RUN",
        "mismatches": {},
    }
    if rerun and not errors:
        original_hashes = _semantic_hashes(output)
        original_summary = dict(summary)
        temp = output / f".r3-verify-{uuid.uuid4().hex}"
        temp.mkdir(parents=True, exist_ok=False)
        try:
            first_dir = temp / "first"
            second_dir = temp / "second"
            first = run(root, first_dir, evidence_path=output / "evidence_manifest.jsonl")
            build(first["output"], root=root)
            second = run(root, second_dir, evidence_path=output / "evidence_manifest.jsonl")
            build(second["output"], root=root)
            _align_replay_metadata(first["output"], original_summary)
            _align_replay_metadata(second["output"], original_summary)
            first_hashes = _semantic_hashes(first["output"])
            second_hashes = _semantic_hashes(second["output"])
            replay_comparison["original_vs_rerun1"] = "PASS" if original_hashes == first_hashes else "FAIL"
            replay_comparison["rerun1_vs_rerun2"] = "PASS" if first_hashes == second_hashes else "FAIL"
            replay_comparison["original_vs_rerun2"] = "PASS" if original_hashes == second_hashes else "FAIL"
            for name in SEMANTIC_ARTIFACTS:
                if not (original_hashes[name] == first_hashes[name] == second_hashes[name]):
                    replay_comparison["mismatches"][name] = {
                        "original": original_hashes[name],
                        "rerun1": first_hashes[name],
                        "rerun2": second_hashes[name],
                    }
            rerun_result = "PASS" if all(
                replay_comparison[key] == "PASS"
                for key in ("original_vs_rerun1", "rerun1_vs_rerun2", "original_vs_rerun2")
            ) and not replay_comparison["mismatches"] else "FAIL"
            if rerun_result != "PASS":
                errors.append("deterministic replay semantic hashes differ")
        finally:
            shutil.rmtree(temp, ignore_errors=True)
        summary["deterministic_rerun_verification"] = rerun_result
        summary["deterministic_replay_comparison"] = replay_comparison
        write_json(output / "run_summary.json", summary)
        manifest["generated_file_hashes"]["run_summary.json"] = file_hash(output / "run_summary.json")
        write_json(output / "run_manifest.json", manifest)

    return {
        "ok": not errors,
        "errors": errors,
        "deterministic_rerun_verification": rerun_result,
        "deterministic_replay_comparison": replay_comparison,
        "production_modified": False,
        "pilot_rows": len(pilot_rows),
        "blind30_rows": len(blind_input),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--rerun", action="store_true")
    args = parser.parse_args()
    result = verify(args.root, args.output, rerun=args.rerun)
    print(result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
