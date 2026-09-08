"""Deterministic fresh-P0 selection for the R3 quarantine pilot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

try:
    from .r3_common import (
        BLIND_SEED,
        PILOT_QUOTAS,
        PILOT_SEED,
        RISK_ORDER,
        classify_risk,
        file_hash,
        json_hash,
        read_csv,
        read_json,
        stable_key,
        write_json,
    )
except ImportError:  # pragma: no cover - supports direct CLI execution
    from r3_common import (
    BLIND_SEED,
    PILOT_QUOTAS,
    PILOT_SEED,
    RISK_ORDER,
    classify_risk,
    file_hash,
    json_hash,
    read_csv,
    read_json,
    stable_key,
    write_json,
    )


def load_overlap(path: Path | None) -> set[str]:
    if path is None or not path.exists():
        return set()
    if path.suffix.lower() in {".json", ".jsonl"}:
        if path.suffix.lower() == ".json":
            value = read_json(path)
            rows = value if isinstance(value, list) else value.get("rows", [])
        else:
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    else:
        rows = read_csv(path)
    result: set[str] = set()
    for row in rows:
        if isinstance(row, str):
            result.add(row.strip())
            continue
        for field in ("canonical", "canonical_tag", "candidate_canonical", "tag", "name"):
            value = str(row.get(field, "")).strip()
            if value:
                result.add(value)
                break
    return result


def _row_risk(row: dict[str, str]) -> str:
    return classify_risk(row.get("canonical", ""), row.get("risk_class", ""))


def _ordered(rows: Iterable[dict[str, Any]], seed: str, overlap: set[str]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            0 if row["canonical"] in overlap else 1,
            row["selection_key"] if seed == PILOT_SEED else row["blind_key"],
            row["canonical"],
        ),
    )


def select_pilot(
    root: Path,
    *,
    missing_candidates: Path | None = None,
    regression_fixtures: Path | None = None,
    issue32_overlap: Path | None = None,
    overlap_canonicals: set[str] | None = None,
) -> dict[str, Any]:
    """Select exactly 100 fresh rows or fail closed when the pool is too small."""

    missing_candidates = missing_candidates or root / "translation_quarantine" / "missing_candidates.csv"
    regression_fixtures = regression_fixtures or root / "translation_quarantine" / "phase1a_review.csv"
    queue = read_csv(missing_candidates)
    regression = read_csv(regression_fixtures)
    excluded = {row.get("canonical", "").strip() for row in regression if row.get("canonical", "").strip()}
    overlap = set(overlap_canonicals or load_overlap(issue32_overlap))
    eligible: list[dict[str, Any]] = []
    seen: set[str] = set()
    for source_row in queue:
        canonical = source_row.get("canonical", "").strip()
        if not canonical or source_row.get("priority", "").strip() != "P0" or canonical in excluded:
            continue
        if canonical in seen:
            raise ValueError(f"duplicate eligible canonical: {canonical}")
        seen.add(canonical)
        risk = _row_risk(source_row)
        eligible.append({
            "canonical": canonical,
            "lanes": source_row.get("lanes", ""),
            "priority": source_row.get("priority", ""),
            "post_count_or_reference": source_row.get("post_count_or_reference", ""),
            "semantic_class": source_row.get("semantic_class", ""),
            "risk_class": risk,
            "issue32_overlap": "YES" if canonical in overlap else "NO",
            "selection_key": stable_key(PILOT_SEED, canonical),
        })
    if len(eligible) < sum(PILOT_QUOTAS.values()):
        raise ValueError(f"fresh eligible pool has {len(eligible)} rows; 100 required")

    by_risk = {risk: _ordered((row for row in eligible if row["risk_class"] == risk), PILOT_SEED, overlap)
               for risk in RISK_ORDER}
    selected: list[dict[str, Any]] = []
    selected_keys: set[str] = set()
    achieved = {risk: 0 for risk in RISK_ORDER}
    shortage = {risk: max(0, PILOT_QUOTAS[risk] - len(by_risk[risk])) for risk in RISK_ORDER}
    for risk in RISK_ORDER:
        for row in by_risk[risk][: PILOT_QUOTAS[risk]]:
            selected.append({**row, "selection_stratum": risk})
            selected_keys.add(row["canonical"])
            achieved[risk] += 1

    # A shortage may only be filled by the next higher-risk strata.  This is
    # deliberately one-way: a sparse high-risk class never pulls in a lower
    # risk row that was requested by an earlier quota.
    for index, risk in enumerate(RISK_ORDER):
        missing = PILOT_QUOTAS[risk] - achieved[risk]
        if missing <= 0:
            continue
        for donor_risk in RISK_ORDER[index + 1:]:
            donors = [row for row in by_risk[donor_risk] if row["canonical"] not in selected_keys]
            for row in donors[:missing]:
                selected.append({**row, "selection_stratum": risk})
                selected_keys.add(row["canonical"])
                achieved[risk] += 1
                missing -= 1
                if missing == 0:
                    break
            if missing == 0:
                break
        if missing:
            raise ValueError(f"cannot satisfy R3 quota for {risk}; shortage={missing}")

    if len(selected) != 100:
        raise AssertionError(f"selection produced {len(selected)} rows")
    selected.sort(key=lambda row: (RISK_ORDER.index(row["risk_class"]), row["selection_key"], row["canonical"]))
    for ordinal, row in enumerate(selected, 1):
        row["pilot_ordinal"] = ordinal
    return {
        "schema_version": "r3-1",
        "selection_seed": PILOT_SEED,
        "pilot_algorithm_version": "r3-selection-1",
        "eligible_pool": {
            "priority": "P0",
            "source": str(missing_candidates.relative_to(root)).replace("\\", "/"),
            "excluded_regression_source": str(regression_fixtures.relative_to(root)).replace("\\", "/"),
            "eligible_count": len(eligible),
            "excluded_count": len(excluded),
            "excluded_phase1a_canonicals_hash": json_hash(sorted(excluded)),
        },
        "requested_stratum_counts": dict(PILOT_QUOTAS),
        "achieved_stratum_counts": achieved,
        "shortage_by_stratum": shortage,
        "issue32_overlap_counts": {
            "pool": sum(row["canonical"] in overlap for row in eligible),
            "selected": sum(row["canonical"] in overlap for row in selected),
            "omitted": sum(row["canonical"] in overlap for row in eligible if row["canonical"] not in selected_keys),
        },
        "source_hashes": {
            "missing_candidates.csv": file_hash(missing_candidates),
            "phase1a_review.csv": file_hash(regression_fixtures),
            **({"issue32_overlap": file_hash(issue32_overlap)} if issue32_overlap and issue32_overlap.exists() else {}),
        },
        "selected": selected,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--issue32-overlap", type=Path)
    args = parser.parse_args()
    from r3_common import ensure_r3_output
    ensure_r3_output(args.root.resolve(), args.output.parent)
    result = select_pilot(args.root.resolve(), issue32_overlap=args.issue32_overlap)
    write_json(args.output, result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
