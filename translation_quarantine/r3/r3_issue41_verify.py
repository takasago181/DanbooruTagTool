"""Fail-closed deterministic verifier for the Issue #41 v2 pilot pipeline.

The base #39 verifier intentionally validates the base R3 blind artifacts.
Issue #41 adds a frozen #32 bridge-v2 contract, an effective-risk overlay, and
its own blind30 artifacts, so deterministic replay must rerun that exact
pipeline rather than silently falling back to the base R3 path.
"""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

try:
    from .r3_common import file_hash, issue32_fingerprint, protected_snapshot, read_json, read_jsonl
    from .r3_issue41_pipeline import run_pipeline
except ImportError:  # pragma: no cover - supports direct CLI execution
    from r3_common import file_hash, issue32_fingerprint, protected_snapshot, read_json, read_jsonl
    from r3_issue41_pipeline import run_pipeline


EXPECTED_CANONICALS = ["bara", "fishnets", "loli", "fellatio", "pussy", "anal", "bound"]
EXPECTED_SNAPSHOT_VERSION = "ui-ja-issue41-overlap7-v2"
EXPECTED_CONTENT_IDENTITY = "sha256:7e46f7f3655846a4f6ea2d1990e015701cbff5b123bdf8ef1809668f8a375ef5"
MASKED_FIELDS = {
    "risk_class", "effective_risk_class", "selection_risk_class",
    "display_state", "search_state", "bridge32_state", "bridge32_availability",
    "row_state", "reason_codes", "issue32_meaning_fingerprint",
    "evaluated_issue32_meaning_fingerprint", "issue32_content_identity",
    "issue32_conflict_signal", "prior_review_state", "phase1a_qa", "review_state",
}
SEMANTIC_ARTIFACTS = (
    "pilot_selection.json",
    "evidence_manifest.jsonl",
    "pilot_rows.jsonl",
    "search_terms.jsonl",
    "bridge32.jsonl",
    "run_summary.json",
    "pilot_rows_effective.jsonl",
    "blind30_input_issue41.jsonl",
    "blind30_key_issue41.json",
    "issue41_pipeline_summary.json",
    "issue41_frozen_evidence_manifest.jsonl",
    "issue41_frozen_decision_ledger.jsonl",
    "issue41_issue32_overlap_requirements.jsonl",
)


def _snapshot_errors(snapshot_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except Exception as exc:  # fail closed on any malformed snapshot
        return [f"cannot read Issue #32 v2 snapshot: {exc}"]
    if not isinstance(payload, dict):
        return ["Issue #32 v2 snapshot must be a JSON object"]
    if payload.get("snapshot_version") != EXPECTED_SNAPSHOT_VERSION:
        errors.append("unexpected Issue #32 snapshot version")
    if payload.get("content_identity") != EXPECTED_CONTENT_IDENTITY:
        errors.append("unexpected Issue #32 snapshot content identity")
    if payload.get("snapshot_frozen") is not True or payload.get("snapshot_pinned") is not True or payload.get("snapshot_immutable") is not True:
        errors.append("Issue #32 v2 snapshot is not frozen/pinned/immutable")
    rows = payload.get("rows")
    if not isinstance(rows, list):
        return [*errors, "Issue #32 v2 snapshot rows are missing"]
    if [row.get("canonical") for row in rows if isinstance(row, dict)] != EXPECTED_CANONICALS:
        errors.append("Issue #32 v2 authoritative overlap order differs")
    if len(rows) != 7:
        errors.append("Issue #32 v2 snapshot must contain exactly 7 rows")
    for row in rows:
        if not isinstance(row, dict):
            errors.append("Issue #32 v2 snapshot contains a non-object row")
            continue
        canonical = str(row.get("canonical", ""))
        if row.get("meaning_relevant_status") != "RESOLVED":
            errors.append(f"Issue #32 v2 row is not RESOLVED: {canonical}")
        if row.get("conflict_signal") is not False:
            errors.append(f"Issue #32 v2 row has conflict signal: {canonical}")
        if row.get("snapshot_frozen") is not True or row.get("snapshot_pinned") is not True or row.get("snapshot_immutable") is not True:
            errors.append(f"Issue #32 v2 row is not frozen/pinned/immutable: {canonical}")
        semantics = row.get("translation_visible_semantics")
        stored = str(row.get("meaning_fingerprint", ""))
        if not isinstance(semantics, dict) or not semantics:
            errors.append(f"Issue #32 v2 row lacks translation-visible semantics: {canonical}")
        elif issue32_fingerprint({"translation_visible_semantics": semantics}) != stored:
            errors.append(f"Issue #32 v2 meaning fingerprint mismatch: {canonical}")
    return errors


def _artifact_hashes(output: Path) -> tuple[dict[str, str], list[str]]:
    hashes: dict[str, str] = {}
    errors: list[str] = []
    for name in SEMANTIC_ARTIFACTS:
        path = output / name
        if not path.exists():
            errors.append(f"missing Issue #41 semantic artifact: {name}")
        else:
            hashes[name] = file_hash(path)
    return hashes, errors


def _static_errors(root: Path, output: Path, snapshot_path: Path) -> list[str]:
    errors = _snapshot_errors(snapshot_path)
    hashes, artifact_errors = _artifact_hashes(output)
    errors.extend(artifact_errors)
    if artifact_errors:
        return errors

    summary = read_json(output / "issue41_pipeline_summary.json")
    guard = summary.get("bridge_status_guard", {})
    if guard.get("state") != "READY" or guard.get("required_count") != 7 or guard.get("resolved_count") != 7 or guard.get("blocked_count") != 0:
        errors.append("Issue #41 bridge status guard is not READY 7/7")
    availability = summary.get("bridge_availability_counts", {})
    if availability.get("AVAILABLE") != 7 or summary.get("bridge_availability_blocked_count") != 0:
        errors.append("Issue #41 R3 bridge availability is not AVAILABLE 7/7")
    if summary.get("blind30_state") != "BUILT" or summary.get("blind30_selected") != 30:
        errors.append("Issue #41 effective-risk blind30 is not BUILT with 30 rows")
    if summary.get("production_modified") is not False:
        errors.append("Issue #41 summary reports production modification")
    if summary.get("remaining_925_processed") is not False:
        errors.append("Issue #41 summary reports remaining P0 925 processing")
    if summary.get("stage10_production_ab_started") is not False:
        errors.append("Issue #41 summary reports Stage10 production A/B start")

    bridge_rows = read_jsonl(output / "bridge32.jsonl")
    available = [row for row in bridge_rows if row.get("bridge32_availability") == "AVAILABLE"]
    if [str(row.get("canonical", "")) for row in available] != [c for c in EXPECTED_CANONICALS if any(str(r.get("canonical", "")) == c for r in available)]:
        # Ordering in bridge32 follows pilot order, so set equality is authoritative here.
        if {str(row.get("canonical", "")) for row in available} != set(EXPECTED_CANONICALS):
            errors.append("bridge32 AVAILABLE canonical set differs from frozen overlap7")
    if len(available) != 7:
        errors.append("bridge32 must contain exactly 7 AVAILABLE rows")
    for row in available:
        canonical = str(row.get("canonical", ""))
        if row.get("frozen") is not True or row.get("pinned") is not True or row.get("immutable") is not True:
            errors.append(f"bridge32 AVAILABLE row is not frozen/pinned/immutable: {canonical}")
        if row.get("conflict_signal") is not False:
            errors.append(f"bridge32 AVAILABLE row has conflict signal: {canonical}")
        propositions = row.get("meaning_relevant_propositions")
        stored = str(row.get("meaning_fingerprint", ""))
        if not isinstance(propositions, dict) or not propositions:
            errors.append(f"bridge32 AVAILABLE row lacks meaning propositions: {canonical}")
        elif issue32_fingerprint({"translation_visible_semantics": propositions}) != stored:
            errors.append(f"bridge32 v2 fingerprint does not match semantics: {canonical}")

    blind_input = read_jsonl(output / "blind30_input_issue41.jsonl")
    blind_key = read_json(output / "blind30_key_issue41.json")
    selected = blind_key.get("selected", [])
    if len(blind_input) != 30 or len(selected) != 30:
        errors.append("Issue #41 blind30 must contain exactly 30 selected rows")
    input_canonicals = [str(row.get("canonical", "")) for row in blind_input]
    key_canonicals = [str(row.get("canonical", "")) for row in selected]
    if len(set(input_canonicals)) != 30 or set(input_canonicals) != set(key_canonicals):
        errors.append("Issue #41 blind30 input/key canonical sets differ or contain duplicates")
    for row in blind_input:
        leaked = MASKED_FIELDS & set(row)
        if leaked:
            errors.append(f"Issue #41 blind input leaks masked fields for {row.get('canonical')}: {sorted(leaked)}")
        for term in row.get("search_terms", []):
            if isinstance(term, dict) and set(term) - {"term", "term_class"}:
                errors.append(f"Issue #41 blind input leaks search state for {row.get('canonical')}")

    manifest = read_json(output / "run_manifest.json")
    if manifest.get("protected_snapshot_before", {}) != protected_snapshot(root):
        errors.append("protected production/#32/#35 boundary changed during Issue #41 run")
    if len(hashes) != len(SEMANTIC_ARTIFACTS):
        errors.append("Issue #41 semantic artifact hash set is incomplete")
    return errors


def _copy_root(source: Path, destination: Path) -> None:
    def ignore(_path: str, names: list[str]) -> set[str]:
        return {name for name in names if name in {".git", ".pytest_cache", "__pycache__"}}
    shutil.copytree(source, destination, ignore=ignore)


def verify(root: Path, output_dir: Path, snapshot_path: Path, *, rerun: bool = False) -> dict[str, Any]:
    root = root.resolve()
    output = output_dir.resolve()
    snapshot_path = snapshot_path.resolve()
    errors = _static_errors(root, output, snapshot_path)
    original_hashes, _ = _artifact_hashes(output)
    replay = {
        "original_vs_rerun1": "NOT_RUN",
        "rerun1_vs_rerun2": "NOT_RUN",
        "original_vs_rerun2": "NOT_RUN",
        "mismatches": {},
    }
    rerun_result = "NOT_RUN"

    if rerun and not errors:
        with tempfile.TemporaryDirectory(prefix="issue41-replay-") as temp_name:
            temp = Path(temp_name)
            shared_snapshot = temp / "ui_ja_issue41_overlap7_v2.json"
            shutil.copy2(snapshot_path, shared_snapshot)
            first_root = temp / "first-root"
            second_root = temp / "second-root"
            _copy_root(root, first_root)
            _copy_root(root, second_root)

            run_pipeline(first_root, issue32_snapshot=shared_snapshot)
            run_pipeline(second_root, issue32_snapshot=shared_snapshot)
            first_output = first_root / "translation_quarantine" / "r3"
            second_output = second_root / "translation_quarantine" / "r3"
            first_errors = _static_errors(first_root, first_output, shared_snapshot)
            second_errors = _static_errors(second_root, second_output, shared_snapshot)
            if first_errors:
                errors.extend(f"rerun1: {error}" for error in first_errors)
            if second_errors:
                errors.extend(f"rerun2: {error}" for error in second_errors)

            first_hashes, first_hash_errors = _artifact_hashes(first_output)
            second_hashes, second_hash_errors = _artifact_hashes(second_output)
            errors.extend(f"rerun1: {error}" for error in first_hash_errors)
            errors.extend(f"rerun2: {error}" for error in second_hash_errors)
            replay["original_vs_rerun1"] = "PASS" if original_hashes == first_hashes else "FAIL"
            replay["rerun1_vs_rerun2"] = "PASS" if first_hashes == second_hashes else "FAIL"
            replay["original_vs_rerun2"] = "PASS" if original_hashes == second_hashes else "FAIL"
            for name in SEMANTIC_ARTIFACTS:
                values = (original_hashes.get(name), first_hashes.get(name), second_hashes.get(name))
                if len(set(values)) != 1:
                    replay["mismatches"][name] = {
                        "original": values[0], "rerun1": values[1], "rerun2": values[2]
                    }
            rerun_result = "PASS" if all(
                replay[key] == "PASS"
                for key in ("original_vs_rerun1", "rerun1_vs_rerun2", "original_vs_rerun2")
            ) and not replay["mismatches"] and not first_errors and not second_errors else "FAIL"
            if rerun_result != "PASS":
                errors.append("Issue #41 deterministic replay semantic hashes differ")

    return {
        "ok": not errors,
        "errors": errors,
        "deterministic_rerun_verification": rerun_result,
        "deterministic_replay_comparison": replay,
        "production_modified": False,
        "bridge_rows_available": 7 if not errors or rerun_result == "PASS" else None,
        "blind30_rows": 30 if not errors or rerun_result == "PASS" else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--issue32-snapshot", type=Path, required=True)
    parser.add_argument("--rerun", action="store_true")
    args = parser.parse_args()
    result = verify(args.root, args.output, args.issue32_snapshot, rerun=args.rerun)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
