"""Issue #41 effective-risk overlay for the quarantined R3 pilot.

This module deliberately does not modify the audited #39 selector or its fixed
fresh100 membership. It consumes generated ``pilot_rows.jsonl`` plus the
frozen override manifest and writes an Issue-41-specific effective-risk view.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

RISK_CLASSES = {
    "LOW",
    "MEDIUM",
    "HIGH_POSE_ACTION",
    "HIGH_ANATOMY_ADULT",
    "CRITICAL",
}
HIGH_OR_CRITICAL = {"HIGH_POSE_ACTION", "HIGH_ANATOMY_ADULT", "CRITICAL"}
_ALLOWED_TRANSITIONS = {
    "LOW": RISK_CLASSES,
    "MEDIUM": {"MEDIUM", "HIGH_POSE_ACTION", "HIGH_ANATOMY_ADULT", "CRITICAL"},
    "HIGH_POSE_ACTION": {"HIGH_POSE_ACTION", "CRITICAL"},
    "HIGH_ANATOMY_ADULT": {"HIGH_ANATOMY_ADULT", "CRITICAL"},
    "CRITICAL": {"CRITICAL"},
}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: JSONL record must be an object")
        rows.append(value)
    return rows


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    payload = "".join(
        json.dumps(dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        for row in rows
    )
    path.write_text(payload, encoding="utf-8", newline="\n")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _row_state(display: str, search: str, bridge: str) -> str:
    states = {display, search, bridge}
    if "CONTRADICTION" in states:
        return "CONTRADICTION"
    if "STALE_REVIEW" in states:
        return "STALE_REVIEW"
    if "REVIEW" in states:
        return "REVIEW"
    return "READY"


def load_overrides(path: Path) -> dict[str, dict[str, Any]]:
    required = {
        "canonical",
        "pilot_ordinal",
        "selection_risk_class",
        "effective_risk_class",
        "frozen",
    }
    result: dict[str, dict[str, Any]] = {}
    for row in _read_jsonl(path):
        missing = required - set(row)
        if missing:
            raise ValueError(f"effective-risk override missing fields: {sorted(missing)}")
        canonical = str(row["canonical"]).strip()
        if not canonical:
            raise ValueError("effective-risk override canonical is blank")
        if canonical in result:
            raise ValueError(f"duplicate effective-risk override: {canonical}")
        if row.get("frozen") is not True:
            raise ValueError(f"effective-risk override is not frozen: {canonical}")
        selection = str(row["selection_risk_class"])
        effective = str(row["effective_risk_class"])
        if selection not in RISK_CLASSES:
            raise ValueError(f"unknown selection risk for {canonical}: {selection}")
        if effective not in RISK_CLASSES:
            raise ValueError(f"unknown effective risk for {canonical}: {effective}")
        if effective not in _ALLOWED_TRANSITIONS[selection]:
            raise ValueError(
                f"risk downgrade/cross-lane conversion forbidden for {canonical}: "
                f"{selection} -> {effective}"
            )
        try:
            ordinal = int(row["pilot_ordinal"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid pilot ordinal for {canonical}") from exc
        if ordinal < 1:
            raise ValueError(f"invalid pilot ordinal for {canonical}: {ordinal}")
        normalized = dict(row)
        normalized["pilot_ordinal"] = ordinal
        result[canonical] = normalized
    return result


def apply_effective_risk(
    pilot_rows: list[Mapping[str, Any]],
    overrides: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    seen_canonicals: set[str] = set()
    seen_ordinals: set[int] = set()
    output: list[dict[str, Any]] = []
    row_by_canonical: dict[str, Mapping[str, Any]] = {}

    for raw in pilot_rows:
        canonical = str(raw.get("canonical", "")).strip()
        if not canonical:
            raise ValueError("pilot row canonical is blank")
        if canonical in seen_canonicals:
            raise ValueError(f"duplicate pilot canonical: {canonical}")
        try:
            ordinal = int(raw.get("pilot_ordinal"))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid pilot ordinal for {canonical}") from exc
        if ordinal in seen_ordinals:
            raise ValueError(f"duplicate pilot ordinal: {ordinal}")
        selection = str(raw.get("selection_risk_class") or raw.get("risk_class") or "")
        if selection not in RISK_CLASSES:
            raise ValueError(f"unknown pilot risk for {canonical}: {selection}")
        seen_canonicals.add(canonical)
        seen_ordinals.add(ordinal)
        row_by_canonical[canonical] = raw

    unknown = sorted(set(overrides) - set(row_by_canonical))
    if unknown:
        raise ValueError(f"override canonical not present in fixed pilot: {unknown}")

    for canonical, raw in sorted(
        row_by_canonical.items(), key=lambda item: int(item[1]["pilot_ordinal"])
    ):
        row = dict(raw)
        ordinal = int(row["pilot_ordinal"])
        selection = str(row.get("selection_risk_class") or row.get("risk_class"))
        override = overrides.get(canonical)
        effective = selection
        source = "SELECTION"
        if override is not None:
            if int(override["pilot_ordinal"]) != ordinal:
                raise ValueError(
                    f"override ordinal mismatch for {canonical}: "
                    f"{override['pilot_ordinal']} != {ordinal}"
                )
            if str(override["selection_risk_class"]) != selection:
                raise ValueError(
                    f"override selection risk mismatch for {canonical}: "
                    f"{override['selection_risk_class']} != {selection}"
                )
            effective = str(override["effective_risk_class"])
            source = "FROZEN_OVERRIDE"

        row["selection_risk_class"] = selection
        row["effective_risk_class"] = effective
        row["effective_risk_source"] = source

        semantic_ids = row.get("semantic_evidence_ids") or []
        if effective in HIGH_OR_CRITICAL and not semantic_ids:
            row["display_state"] = "REVIEW"
            reasons = set(row.get("reason_codes") or [])
            reasons.add("EFFECTIVE_HIGH_OR_CRITICAL_MISSING_EXACT_CANONICAL_SCOPE")
            row["reason_codes"] = sorted(reasons)
            row["row_state"] = _row_state(
                str(row.get("display_state", "REVIEW")),
                str(row.get("search_state", "REVIEW")),
                str(row.get("bridge32_state", "REVIEW")),
            )
        output.append(row)
    return output


def apply_file(
    output_dir: Path,
    overrides_path: Path,
    *,
    pilot_filename: str = "pilot_rows.jsonl",
    effective_filename: str = "pilot_rows_effective.jsonl",
    manifest_filename: str = "effective_risk_manifest.json",
) -> dict[str, Any]:
    pilot_path = output_dir / pilot_filename
    if not pilot_path.exists():
        raise FileNotFoundError(pilot_path)
    overrides = load_overrides(overrides_path)
    original = _read_jsonl(pilot_path)
    effective = apply_effective_risk(original, overrides)
    _write_jsonl(output_dir / effective_filename, effective)

    original_membership = [
        (int(row["pilot_ordinal"]), str(row["canonical"])) for row in original
    ]
    effective_membership = [
        (int(row["pilot_ordinal"]), str(row["canonical"])) for row in effective
    ]
    if original_membership != effective_membership:
        raise AssertionError("effective-risk overlay changed fixed pilot membership or ordinals")

    counts: dict[str, int] = {risk: 0 for risk in RISK_CLASSES}
    for row in effective:
        counts[str(row["effective_risk_class"])] += 1
    manifest = {
        "schema_version": "issue41-effective-risk-1",
        "pilot_rows": len(effective),
        "override_rows": len(overrides),
        "override_manifest_sha256": _sha256(overrides_path),
        "effective_risk_counts": dict(sorted(counts.items())),
        "membership_unchanged": True,
        "output_file": effective_filename,
    }
    (output_dir / manifest_filename).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return manifest


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("overrides", type=Path)
    args = parser.parse_args()
    print(json.dumps(apply_file(args.output_dir, args.overrides), ensure_ascii=False, indent=2))
