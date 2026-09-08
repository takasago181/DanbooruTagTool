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
        PILOT_QUOTAS,
        STATES,
        TERM_CLASSES,
        file_hash,
        protected_snapshot,
        read_json,
        read_jsonl,
        write_json,
    )
    from .r3_run import run
except ImportError:  # pragma: no cover - supports direct CLI execution
    from r3_common import BLIND_QUOTAS, PILOT_QUOTAS, STATES, TERM_CLASSES, file_hash, protected_snapshot, read_json, read_jsonl, write_json
    from r3_run import run


PILOT_FIELDS = {
    "pilot_ordinal", "canonical", "lanes", "priority", "post_count_or_reference", "semantic_class",
    "risk_class", "semantic_scope_summary", "semantic_evidence_ids", "display_candidate",
    "display_state", "display_evidence_ids", "search_state", "bridge32_state", "row_state",
    "issue32_overlap", "issue32_snapshot_ref", "issue32_meaning_fingerprint", "reason_codes",
}
SEARCH_FIELDS = {
    "canonical", "term", "term_class", "term_state", "evidence_ids", "justification", "rejection_reason",
}
BLIND_INPUT_FIELDS = {"canonical", "candidate_display", "search_terms", "semantic_evidence", "issue32_snapshot_evidence"}
MASKED_FIELDS = {
    "risk_class", "display_state", "search_state", "bridge32_state", "row_state", "reason_codes",
    "issue32_meaning_fingerprint", "prior_review_state", "phase1a_qa", "review_state",
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
    errors.extend(_errors_for_fields(bridge_rows, {"canonical", "snapshot_ref", "meaning_fingerprint", "meaning_relevant_propositions", "bridge32_state", "reason_codes"}, "bridge32"))
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
    if rerun and not errors:
        temp = output / f".r3-verify-{uuid.uuid4().hex}"
        temp.mkdir(parents=True, exist_ok=False)
        try:
            first_dir = temp / "first"
            second_dir = temp / "second"
            first = run(root, first_dir, evidence_path=output / "evidence_manifest.jsonl")
            second = run(root, second_dir, evidence_path=output / "evidence_manifest.jsonl")
            first_hashes = _semantic_hashes(first["output"])
            second_hashes = _semantic_hashes(second["output"])
            rerun_result = "PASS" if first_hashes == second_hashes else "FAIL"
            if rerun_result != "PASS":
                errors.append("deterministic rerun semantic hashes differ")
        finally:
            shutil.rmtree(temp, ignore_errors=True)
        summary["deterministic_rerun_verification"] = rerun_result
        write_json(output / "run_summary.json", summary)
        manifest["generated_file_hashes"]["run_summary.json"] = file_hash(output / "run_summary.json")
        write_json(output / "run_manifest.json", manifest)

    return {
        "ok": not errors,
        "errors": errors,
        "deterministic_rerun_verification": rerun_result,
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
