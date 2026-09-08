"""Deterministic schema and ambiguity gate for Hard Adult Challenge v1.

This is quarantine-only. It validates the frozen 64 canonical rows plus the 16
Japanese ambiguity probes and can score future resolver output without changing
production search ranking.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping

EXPECTED_STRATA = {
    "ANATOMY_BOUNDARY": 6,
    "SEXUAL_ACTION": 10,
    "INSERTION_TOY_MACHINE": 12,
    "BDSM_RESTRAINT_DOMINATION": 12,
    "FLUID_EXCRETION_CONTAMINATION": 12,
    "TENTACLE_NONHUMAN": 8,
    "REPRODUCTION_LACTATION": 4,
}
EXPECTED_PROBE_BEHAVIORS = {"RESOLVE_ONE", "RETURN_SET", "REVIEW_DECOMPOSE"}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{line_number}: row must be an object")
        rows.append(row)
    return rows


def validate_design(
    challenge_rows: list[Mapping[str, Any]],
    probes: list[Mapping[str, Any]],
) -> dict[str, Any]:
    errors: list[str] = []
    if len(challenge_rows) != 64:
        errors.append(f"challenge row count must be 64, got {len(challenge_rows)}")
    if len(probes) != 16:
        errors.append(f"ambiguity probe count must be 16, got {len(probes)}")

    ids = [str(row.get("challenge_id", "")) for row in challenge_rows]
    canonicals = [str(row.get("canonical", "")).strip() for row in challenge_rows]
    special_ids = [row.get("special_id") for row in challenge_rows]
    if len(set(ids)) != len(ids):
        errors.append("duplicate challenge_id")
    if len(set(canonicals)) != len(canonicals):
        errors.append("duplicate canonical in challenge set")
    if len(set(special_ids)) != len(special_ids):
        errors.append("duplicate Special ID in challenge set")
    if any(not value for value in canonicals):
        errors.append("blank canonical in challenge set")

    strata = Counter(str(row.get("stratum", "")) for row in challenge_rows)
    if dict(strata) != EXPECTED_STRATA:
        errors.append(f"stratum quotas mismatch: {dict(strata)}")

    probe_ids = [str(row.get("probe_id", "")) for row in probes]
    if len(set(probe_ids)) != len(probe_ids):
        errors.append("duplicate probe_id")

    canonical_set = set(canonicals)
    for probe in probes:
        probe_id = str(probe.get("probe_id", ""))
        behavior = str(probe.get("expected_behavior", ""))
        if behavior not in EXPECTED_PROBE_BEHAVIORS:
            errors.append(f"{probe_id}: unknown expected behavior {behavior}")
            continue
        if behavior == "RESOLVE_ONE":
            expected = [str(x) for x in probe.get("expected_canonicals", [])]
            if len(expected) != 1:
                errors.append(
                    f"{probe_id}: RESOLVE_ONE must have exactly one expected canonical"
                )
            elif expected[0] not in canonical_set:
                errors.append(
                    f"{probe_id}: expected canonical not in challenge set: {expected[0]}"
                )
            if probe.get("forbid_singleton_auto_ready") is not False:
                errors.append(f"{probe_id}: RESOLVE_ONE must allow exact singleton READY")
        elif behavior == "RETURN_SET":
            expected = {str(x) for x in probe.get("minimum_expected_candidates", [])}
            if len(expected) < 2:
                errors.append(
                    f"{probe_id}: RETURN_SET needs at least two expected candidates"
                )
            missing = sorted(expected - canonical_set)
            if missing:
                errors.append(
                    f"{probe_id}: expected candidates absent from challenge: {missing}"
                )
            if probe.get("forbid_singleton_auto_ready") is not True:
                errors.append(
                    f"{probe_id}: RETURN_SET must forbid singleton auto READY"
                )
        else:
            if probe.get("forbid_singleton_auto_ready") is not True:
                errors.append(
                    f"{probe_id}: REVIEW_DECOMPOSE must forbid singleton auto READY"
                )

    return {
        "ok": not errors,
        "errors": errors,
        "challenge_rows": len(challenge_rows),
        "ambiguity_probes": len(probes),
        "stratum_counts": dict(strata),
    }


def score_ambiguity_results(
    probes: list[Mapping[str, Any]],
    result_rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    by_probe: dict[str, Mapping[str, Any]] = {}
    for row in result_rows:
        probe_id = str(row.get("probe_id", ""))
        if not probe_id:
            raise ValueError("result probe_id is blank")
        if probe_id in by_probe:
            raise ValueError(f"duplicate result probe_id: {probe_id}")
        by_probe[probe_id] = row

    details: list[dict[str, Any]] = []
    false_singleton_ready = 0
    missing_expected = 0
    wrong_exact_resolution = 0
    missing_result = 0

    for probe in probes:
        probe_id = str(probe["probe_id"])
        result = by_probe.get(probe_id)
        if result is None:
            missing_result += 1
            details.append(
                {"probe_id": probe_id, "pass": False, "reason": "MISSING_RESULT"}
            )
            continue
        behavior = str(probe["expected_behavior"])
        resolved = {str(x) for x in result.get("resolved_canonicals", [])}
        auto_ready = str(result.get("auto_ready_canonical", "")).strip()
        decision = str(result.get("decision", ""))
        passed = True
        reasons: list[str] = []

        if probe.get("forbid_singleton_auto_ready") is True and auto_ready:
            false_singleton_ready += 1
            passed = False
            reasons.append("FORBIDDEN_SINGLETON_AUTO_READY")

        if behavior == "RESOLVE_ONE":
            expected = {str(x) for x in probe.get("expected_canonicals", [])}
            if resolved != expected:
                wrong_exact_resolution += 1
                passed = False
                reasons.append("WRONG_EXACT_RESOLUTION")
            if auto_ready and auto_ready not in expected:
                wrong_exact_resolution += 1
                passed = False
                reasons.append("WRONG_AUTO_READY_CANONICAL")
        elif behavior == "RETURN_SET":
            expected = {
                str(x) for x in probe.get("minimum_expected_candidates", [])
            }
            if not expected.issubset(resolved):
                missing_expected += 1
                passed = False
                reasons.append("MISSING_EXPECTED_CANDIDATES")
            if len(resolved) < 2:
                false_singleton_ready += 1
                passed = False
                reasons.append("RETURN_SET_COLLAPSED_TO_SINGLETON")
        else:
            if decision != "REVIEW_DECOMPOSE":
                passed = False
                reasons.append("DID_NOT_REVIEW_DECOMPOSE")

        details.append(
            {
                "probe_id": probe_id,
                "pass": passed,
                "reason": "PASS" if passed else "+".join(sorted(set(reasons))),
            }
        )

    metrics = {
        "false_singleton_ready": false_singleton_ready,
        "missing_expected_candidates": missing_expected,
        "wrong_exact_resolution": wrong_exact_resolution,
        "missing_result": missing_result,
    }
    return {
        "ok": all(value == 0 for value in metrics.values())
        and all(row["pass"] for row in details),
        "metrics": metrics,
        "details": details,
    }


def validate_files(challenge_path: Path, probes_path: Path) -> dict[str, Any]:
    return validate_design(read_jsonl(challenge_path), read_jsonl(probes_path))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("challenge", type=Path)
    parser.add_argument("probes", type=Path)
    args = parser.parse_args()
    print(json.dumps(validate_files(args.challenge, args.probes), ensure_ascii=False, indent=2))
