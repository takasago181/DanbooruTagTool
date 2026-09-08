"""Deterministic unseen-P0 selection for the Issue #36 canary."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import subprocess
from pathlib import Path
from typing import Any

try:
    from .r3_common import classify_risk, file_hash, json_hash, read_csv, read_json, stable_key, write_json
except ImportError:  # pragma: no cover
    from r3_common import classify_risk, file_hash, json_hash, read_csv, read_json, stable_key, write_json


CANARY_SEED = "UIJA-R3-BULK-CANARY-20260909-V1"
CANARY_SIZE = 200
VALIDATED_R3_BASE = "53f02d9b3419db8fd9099b38204c29eed289ee8e"


def portable_rows_hash(rows: list[dict[str, Any]]) -> str:
    """Hash parsed CSV content, independent of raw newline encoding."""

    normalized = [
        {str(key): "" if value is None else str(value) for key, value in row.items()}
        for row in rows
    ]
    return json_hash(normalized)


def portable_csv_text_hash(text: str) -> str:
    """Expose the newline-independent identity for focused portability tests."""

    reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff"), newline=""))
    return portable_rows_hash([dict(row) for row in reader])


def _git_command(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    safe_directory = str(root).replace("\\", "/")
    return subprocess.run(
        ["git", "-c", f"safe.directory={safe_directory}", *args],
        cwd=root,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def _git_blob_hash(root: Path, ref: str, relative_path: str) -> str:
    result = _git_command(root, "rev-parse", f"{ref}:{relative_path}")
    if result.returncode != 0:
        raise ValueError(
            f"cannot resolve Git blob for {ref}:{relative_path}: "
            f"{result.stderr.decode('utf-8', errors='replace').strip()}"
        )
    return result.stdout.decode("ascii").strip()


def _git_rows(root: Path, ref: str, relative_path: str) -> tuple[list[dict[str, str]], str]:
    result = _git_command(root, "show", f"{ref}:{relative_path}")
    if result.returncode != 0:
        raise ValueError(
            f"cannot read Git source for {ref}:{relative_path}: "
            f"{result.stderr.decode('utf-8', errors='replace').strip()}"
        )
    raw = result.stdout
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    return [dict(row) for row in reader], hashlib.sha256(raw).hexdigest()


def _canonicals(rows: list[dict[str, Any]]) -> set[str]:
    return {str(row.get("canonical", "")).strip() for row in rows if str(row.get("canonical", "")).strip()}


def _load_issue41_exclusions(path: Path) -> set[str]:
    value = read_json(path)
    rows = value.get("selected", []) if isinstance(value, dict) else value
    return _canonicals(rows)


def select_records(queue: list[dict[str, Any]], excluded: set[str], size: int = CANARY_SIZE) -> list[dict[str, Any]]:
    """Select from already-frozen records; filesystem/hash gates live in select_canary."""

    eligible: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source in queue:
        canonical = str(source.get("canonical", "")).strip()
        if not canonical or source.get("priority", "").strip() != "P0" or canonical in excluded:
            continue
        if canonical in seen:
            raise ValueError(f"duplicate unseen P0 canonical: {canonical}")
        seen.add(canonical)
        eligible.append({
            "canonical": canonical,
            "lanes": source.get("lanes", ""),
            "priority": source.get("priority", ""),
            "post_count_or_reference": source.get("post_count_or_reference", ""),
            "semantic_class": source.get("semantic_class", ""),
            "risk_class": classify_risk(canonical, source.get("risk_class", "")),
            "selection_key": stable_key(CANARY_SEED, canonical),
        })
    if len(eligible) < size:
        raise ValueError(f"unseen eligible P0 pool has {len(eligible)} rows; {size} required")
    eligible.sort(key=lambda row: (row["selection_key"], row["canonical"]))
    return [
        dict(row, canary_ordinal=index, pilot_ordinal=index)
        for index, row in enumerate(eligible[:size], 1)
    ]


def select_canary(
    root: Path,
    *,
    queue_path: Path | None = None,
    phase1a_path: Path | None = None,
    issue41_selection_path: Path | None = None,
    size: int = CANARY_SIZE,
) -> dict[str, Any]:
    root = root.resolve()
    queue_path = queue_path or root / "translation_quarantine" / "missing_candidates.csv"
    phase1a_path = phase1a_path or root / "translation_quarantine" / "phase1a_review.csv"
    issue41_selection_path = issue41_selection_path or root / "translation_quarantine" / "r3" / "pilot_selection.json"
    if size <= 0:
        raise ValueError("canary size must be positive")
    if not queue_path.exists() or not phase1a_path.exists() or not issue41_selection_path.exists():
        raise FileNotFoundError("frozen #36/#41 selection inputs are missing")

    issue41_selection = read_json(issue41_selection_path)
    expected_queue_hash = str(issue41_selection.get("source_hashes", {}).get("missing_candidates.csv", ""))
    expected_phase1a_hash = str(issue41_selection.get("source_hashes", {}).get("phase1a_review.csv", ""))
    queue = read_csv(queue_path)
    phase1a = read_csv(phase1a_path)
    queue_hash = file_hash(queue_path)
    phase1a_hash = file_hash(phase1a_path)
    source_specs = (
        ("missing_candidates.csv", queue_path, queue),
        ("phase1a_review.csv", phase1a_path, phase1a),
    )
    source_identity: dict[str, dict[str, str]] = {}
    for relative_name, current_path, current_rows in source_specs:
        current_blob = _git_blob_hash(root, "HEAD", f"translation_quarantine/{relative_name}")
        validated_blob = _git_blob_hash(root, VALIDATED_R3_BASE, f"translation_quarantine/{relative_name}")
        if current_blob != validated_blob:
            raise ValueError(
                f"Git blob differs from validated R3 base for {relative_name}; "
                "refusing to switch sources"
            )
        validated_rows, validated_raw_hash = _git_rows(
            root, VALIDATED_R3_BASE, f"translation_quarantine/{relative_name}"
        )
        current_portable = portable_rows_hash(current_rows)
        validated_portable = portable_rows_hash(validated_rows)
        if current_portable != validated_portable:
            raise ValueError(
                f"parsed source content differs from validated R3 source for {relative_name}; "
                "refusing to switch sources"
            )
        source_identity[relative_name] = {
            "current_git_blob": current_blob,
            "validated_git_blob": validated_blob,
            "current_raw_hash": file_hash(current_path),
            "validated_raw_hash": validated_raw_hash,
            "historical_raw_hash": expected_queue_hash if relative_name == "missing_candidates.csv" else expected_phase1a_hash,
            "current_portable_content_identity": current_portable,
            "validated_portable_content_identity": validated_portable,
        }

    excluded_phase1a = _canonicals(phase1a)
    excluded_issue41 = _load_issue41_exclusions(issue41_selection_path)
    excluded = excluded_phase1a | excluded_issue41
    eligible_count = sum(
        1
        for row in queue
        if str(row.get("canonical", "")).strip()
        and row.get("priority", "").strip() == "P0"
        and str(row.get("canonical", "")).strip() not in excluded
    )
    eligible_rows = select_records(queue, excluded, eligible_count)
    selected = eligible_rows[:size]
    selection_hash = json_hash([row["canonical"] for row in selected])
    excluded_hash = json_hash(sorted(excluded))
    return {
        "schema_version": "issue36-bulk-selection-1",
        "campaign_id": "issue36-r3-bulk-canary-20260909-v1",
        "selection_seed": CANARY_SEED,
        "canary_size": size,
        "source_queue": "translation_quarantine/missing_candidates.csv",
        "source_queue_hash": queue_hash,
        "validated_r3_source_hash": expected_queue_hash,
        "source_queue_portable_content_identity": source_identity["missing_candidates.csv"]["current_portable_content_identity"],
        "phase1a_exclusion_source_hash": phase1a_hash,
        "validated_phase1a_exclusion_hash": expected_phase1a_hash,
        "phase1a_exclusion_portable_content_identity": source_identity["phase1a_review.csv"]["current_portable_content_identity"],
        "validated_r3_base": VALIDATED_R3_BASE,
        "source_identity": source_identity,
        "exclusion_set": {
            "hash": excluded_hash,
            "count": len(excluded),
            "phase1a_count": len(excluded_phase1a),
            "issue41_fresh100_count": len(excluded_issue41),
            "union_count": len(excluded),
            "sources": [
                "translation_quarantine/phase1a_review.csv",
                "translation_quarantine/r3/pilot_selection.json",
            ],
        },
        "eligible_unseen_p0_count": eligible_count,
        "eligible_pool_effective_risk_distribution": {
            risk: sum(row["risk_class"] == risk for row in eligible_rows)
            for risk in ("LOW", "MEDIUM", "HIGH_POSE_ACTION", "HIGH_ANATOMY_ADULT", "CRITICAL")
        },
        "canary_membership_hash": selection_hash,
        "effective_risk_distribution": {
            risk: sum(row["risk_class"] == risk for row in selected)
            for risk in ("LOW", "MEDIUM", "HIGH_POSE_ACTION", "HIGH_ANATOMY_ADULT", "CRITICAL")
        },
        "selected": selected,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write_json(args.output, select_canary(args.root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
