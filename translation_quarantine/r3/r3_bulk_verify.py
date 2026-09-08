"""Verify Issue #36 canary artifacts and deterministic three-way replay."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

try:
    from .r3_common import file_hash, protected_snapshot, read_json, read_jsonl, write_json
    from .r3_bulk_run import run_campaign
except ImportError:  # pragma: no cover
    from r3_common import file_hash, protected_snapshot, read_json, read_jsonl, write_json
    from r3_bulk_run import run_campaign


REPLAY_ARTIFACTS = (
    "canary_selection.json", "evidence_manifest.jsonl", "rows.jsonl", "search_terms.jsonl",
    "bridge32.jsonl", "run_summary.json", "masked_audit20_input.jsonl", "masked_audit20_key.json", "leakage_check.json",
)


def _hashes(directory: Path) -> dict[str, str]:
    return {name: file_hash(directory / name) for name in REPLAY_ARTIFACTS}


def verify(root: Path, output: Path, *, replay: bool = True) -> dict[str, object]:
    root = root.resolve()
    output = output.resolve()
    errors: list[str] = []
    for name in REPLAY_ARTIFACTS + ("campaign_manifest.json",):
        if not (output / name).exists():
            errors.append(f"missing artifact: {name}")
    if errors:
        return {"ok": False, "errors": errors}
    summary = read_json(output / "run_summary.json")
    selection = read_json(output / "canary_selection.json")
    rows = read_jsonl(output / "rows.jsonl")
    evidence = read_jsonl(output / "evidence_manifest.jsonl")
    masked = read_jsonl(output / "masked_audit20_input.jsonl")
    key = read_json(output / "masked_audit20_key.json")
    leakage = read_json(output / "leakage_check.json")
    if len(rows) != selection.get("canary_size") or len(rows) != 200:
        errors.append("canary must contain exactly 200 rows")
    if len({row.get("canonical") for row in rows}) != len(rows):
        errors.append("canary contains duplicate canonicals")
    canary_canonicals = {str(row.get("canonical", "")) for row in rows}
    identity_canonicals = {
        str(row.get("canonical", ""))
        for row in evidence
        if row.get("evidence_role") == "IDENTITY_ONLY"
    }
    if (
        not canary_canonicals
        or identity_canonicals != canary_canonicals
        or any(row.get("frozen") is not True for row in evidence)
        or len({(str(row.get("canonical", "")), str(row.get("evidence_id", ""))) for row in evidence}) != len(evidence)
    ):
        errors.append("evidence manifest lacks one frozen identity record per canary canonical")
    if len(masked) != 20 or len(key.get("selected", [])) != 20:
        errors.append("masked audit20 must contain exactly 20 rows and 20 key rows")
    if not leakage.get("ok"):
        errors.append("masked audit20 leakage check failed")
    if summary.get("self_grade") != "NOT_PERFORMED":
        errors.append("self-grade must remain NOT_PERFORMED")
    if summary.get("production_modified") is not False or summary.get("remaining_full_p0_processed") is not False:
        errors.append("bulk canary crossed a forbidden completion boundary")
    before = read_json(output / "campaign_manifest.json").get("protected_snapshot_before", {})
    if before != protected_snapshot(root):
        errors.append("protected snapshot changed during canary verification")

    run_replay = replay
    replay_result = {
        "original_vs_rerun1": "NOT_RUN",
        "rerun1_vs_rerun2": "NOT_RUN",
        "original_vs_rerun2": "NOT_RUN",
        "mismatches": {},
    }
    manifest = read_json(output / "campaign_manifest.json")
    issue32_snapshot: Path | None = None
    snapshot_ref = str(manifest.get("issue32_snapshot_ref", "")).strip()
    if snapshot_ref:
        candidate = Path(snapshot_ref)
        issue32_snapshot = candidate if candidate.is_absolute() else root / candidate
        if not issue32_snapshot.exists():
            errors.append("frozen #32 snapshot from the original campaign is missing")
    evidence_ref = str(manifest.get("evidence_manifest_ref", "")).strip()
    frozen_evidence = root / evidence_ref if evidence_ref else output / "evidence_manifest.jsonl"
    if not frozen_evidence.exists():
        errors.append("frozen evidence manifest from the original campaign is missing")

    if run_replay and not errors:
        temp_root = output / ".replay_work"
        if temp_root.exists():
            shutil.rmtree(temp_root, ignore_errors=True)
        temp_root.mkdir(parents=True, exist_ok=True)
        try:
            first_dir = temp_root / "rerun1"
            second_dir = temp_root / "rerun2"
            run_campaign(root, first_dir, issue32_snapshot=issue32_snapshot, evidence_path=frozen_evidence)
            run_campaign(root, second_dir, issue32_snapshot=issue32_snapshot, evidence_path=frozen_evidence)
            original_hashes = _hashes(output)
            first_hashes = _hashes(first_dir)
            second_hashes = _hashes(second_dir)
            replay_result["original_vs_rerun1"] = "PASS" if original_hashes == first_hashes else "FAIL"
            replay_result["rerun1_vs_rerun2"] = "PASS" if first_hashes == second_hashes else "FAIL"
            replay_result["original_vs_rerun2"] = "PASS" if original_hashes == second_hashes else "FAIL"
            for name in REPLAY_ARTIFACTS:
                if not (original_hashes[name] == first_hashes[name] == second_hashes[name]):
                    replay_result["mismatches"][name] = {
                        "original": original_hashes[name], "rerun1": first_hashes[name], "rerun2": second_hashes[name],
                    }
            if replay_result["mismatches"] or any(replay_result[key] != "PASS" for key in ("original_vs_rerun1", "rerun1_vs_rerun2", "original_vs_rerun2")):
                errors.append("deterministic three-way replay failed")
        finally:
            shutil.rmtree(temp_root, ignore_errors=True)
    result = {
        "schema_version": "issue36-bulk-replay-verification-1",
        "ok": not errors,
        "errors": errors,
        "canary_rows": len(rows),
        "masked_audit20_rows": len(masked),
        "deterministic_replay": replay_result,
        "self_grade": "NOT_PERFORMED",
        "production_modified": False,
        "remaining_full_p0_processed": False,
    }
    write_json(output / "replay_verification.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--no-replay", action="store_true")
    args = parser.parse_args()
    result = verify(args.root, args.output, replay=not args.no_replay)
    print(result)
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
