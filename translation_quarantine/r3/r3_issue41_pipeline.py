"""One-command Issue #41 quarantine pipeline.

Order:
1. normalize the frozen 69-approved + 31-review input decisions;
2. discover exact fresh100 overlap with the read-only Special2788/#32 identity lane;
3. validate Hard Adult Challenge v1 design;
4. run the audited #39 R3 engine with frozen evidence + real bridge requirements;
5. apply the Issue #41 effective-risk overlay;
6. stop before blind30 if any required bridge is missing/blocked;
7. otherwise build the effective-risk blind30 package.

No production data is written by this module.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _fingerprint(paths: list[Path]) -> tuple[str, dict[str, str]]:
    identities = {path.name: _sha256(path) for path in paths if path and path.exists()}
    payload = json.dumps(
        identities, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest(), identities


def run_pipeline(
    root: Path,
    *,
    issue32_snapshot: Path | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    output = root / "translation_quarantine" / "r3"

    # Lazy imports keep this module easy to syntax-test in isolation while the
    # repository runtime supplies the audited #39 modules.
    from .r3_hard_adult_gate import validate_files
    from .r3_issue41_bridge_discovery import discover
    from .r3_issue41_build_blind import build as build_blind
    from .r3_issue41_effective_risk import apply_file
    from .r3_issue41_normalize_evidence import normalize
    from .r3_run import run as run_r3

    hard = validate_files(
        output / "hard_adult_challenge_v1.jsonl",
        output / "hard_adult_ambiguity_probes_v1.jsonl",
    )
    if not hard["ok"]:
        raise ValueError(f"Hard Adult Challenge v1 invalid: {hard['errors']}")

    normalized = normalize(root)
    overlap = discover(root)
    evidence_path = output / "issue41_frozen_evidence_manifest.jsonl"
    requirements_path = output / "issue41_issue32_overlap_requirements.jsonl"
    overrides_path = output / "issue41_effective_risk_overrides.jsonl"

    r3_result = run_r3(
        root,
        output,
        evidence_path=evidence_path,
        issue32_path=issue32_snapshot,
        issue32_requirements_path=requirements_path,
    )
    effective = apply_file(output, overrides_path)
    effective_rows = _read_jsonl(output / "pilot_rows_effective.jsonl")
    availability_counts: dict[str, int] = {}
    for row in effective_rows:
        value = str(row.get("bridge32_availability", ""))
        availability_counts[value] = availability_counts.get(value, 0) + 1

    blocked = sum(
        availability_counts.get(value, 0)
        for value in ("BRIDGE_MISSING", "BLOCKED_BRIDGE")
    )
    blind_state = "HOLD_BRIDGE" if blocked else "BUILT"
    blind_key: dict[str, Any] | None = None
    if not blocked:
        blind_key = build_blind(output)

    fingerprint_paths = [
        evidence_path,
        requirements_path,
        overrides_path,
        output / "hard_adult_challenge_v1.jsonl",
        output / "hard_adult_ambiguity_probes_v1.jsonl",
    ]
    if issue32_snapshot is not None:
        fingerprint_paths.append(issue32_snapshot)
    input_fingerprint, input_identities = _fingerprint(fingerprint_paths)

    summary = {
        "schema_version": "issue41-pipeline-1",
        "normalized_input": normalized,
        "bridge_discovery": overlap,
        "hard_adult_design": hard,
        "effective_risk": effective,
        "bridge_availability_counts": dict(sorted(availability_counts.items())),
        "blind30_state": blind_state,
        "blind30_selected": len(blind_key.get("selected", [])) if blind_key else 0,
        "input_fingerprint": input_fingerprint,
        "input_identities": input_identities,
        "issue32_snapshot_supplied": issue32_snapshot is not None,
        "production_modified": False,
        "remaining_925_processed": False,
        "stage10_production_ab_started": False,
        "r3_engine_result_state": (
            r3_result.get("state", r3_result.get("outcome", ""))
            if isinstance(r3_result, dict)
            else ""
        ),
    }
    (output / "issue41_pipeline_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--issue32-snapshot", type=Path)
    args = parser.parse_args()
    print(
        json.dumps(
            run_pipeline(args.root, issue32_snapshot=args.issue32_snapshot),
            ensure_ascii=False,
            indent=2,
        )
    )
