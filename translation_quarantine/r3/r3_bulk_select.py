"""Deterministic unseen-P0 selection for the Issue #36 canary."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    from .r3_common import classify_risk, file_hash, json_hash, read_csv, read_json, stable_key, write_json
except ImportError:  # pragma: no cover
    from r3_common import classify_risk, file_hash, json_hash, read_csv, read_json, stable_key, write_json


CANARY_SEED = "UIJA-R3-BULK-CANARY-20260909-V1"
CANARY_SIZE = 200


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
    return [dict(row, canary_ordinal=index) for index, row in enumerate(eligible[:size], 1)]


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

    queue_hash = file_hash(queue_path)
    phase1a_hash = file_hash(phase1a_path)
    issue41_selection = read_json(issue41_selection_path)
    expected_queue_hash = str(issue41_selection.get("source_hashes", {}).get("missing_candidates.csv", ""))
    expected_phase1a_hash = str(issue41_selection.get("source_hashes", {}).get("phase1a_review.csv", ""))
    if expected_queue_hash and expected_queue_hash != queue_hash:
        raise ValueError("P0 queue hash differs from the validated R3 source; refusing to switch queues")
    if expected_phase1a_hash and expected_phase1a_hash != phase1a_hash:
        raise ValueError("Phase1A exclusion hash differs from the validated R3 source; refusing to switch exclusions")

    queue = read_csv(queue_path)
    phase1a = read_csv(phase1a_path)
    excluded_phase1a = _canonicals(phase1a)
    excluded_issue41 = _load_issue41_exclusions(issue41_selection_path)
    excluded = excluded_phase1a | excluded_issue41
    selected = select_records(queue, excluded, size)
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
        "phase1a_exclusion_source_hash": phase1a_hash,
        "validated_phase1a_exclusion_hash": expected_phase1a_hash,
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
        "eligible_unseen_p0_count": sum(
            1 for row in queue
            if str(row.get("canonical", "")).strip()
            and row.get("priority", "").strip() == "P0"
            and str(row.get("canonical", "")).strip() not in excluded
        ),
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
