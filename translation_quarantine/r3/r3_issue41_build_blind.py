"""Build Issue #41 blind30 from effective-risk pilot rows.

The audited #39 blind builder remains untouched. This Issue-41 layer reads
``pilot_rows_effective.jsonl`` and stratifies only on ``effective_risk_class``.
Reviewer input stays masked from all risk/state/reason fields.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

BLIND_SEED = "UIJA-R3-BLIND30-20260908-V1"
RISK_ORDER = (
    "LOW",
    "MEDIUM",
    "HIGH_POSE_ACTION",
    "HIGH_ANATOMY_ADULT",
    "CRITICAL",
)
BLIND_QUOTAS = {
    "LOW": 4,
    "MEDIUM": 5,
    "HIGH_POSE_ACTION": 6,
    "HIGH_ANATOMY_ADULT": 7,
    "CRITICAL": 8,
}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
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
    path.write_text(
        "".join(
            json.dumps(
                dict(row), ensure_ascii=False, sort_keys=True, separators=(",", ":")
            )
            + "\n"
            for row in rows
        ),
        encoding="utf-8",
        newline="\n",
    )


def _stable_key(seed: str, canonical: str) -> str:
    return hashlib.sha256((seed + "\0" + canonical).encode("utf-8")).hexdigest()


def select_effective(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {risk: [] for risk in RISK_ORDER}
    overlap = {
        str(row["canonical"]) for row in rows if row.get("issue32_overlap") == "YES"
    }
    for raw in rows:
        row = dict(raw)
        canonical = str(row.get("canonical", "")).strip()
        risk = str(row.get("effective_risk_class", ""))
        selection = str(row.get("selection_risk_class", row.get("risk_class", "")))
        if not canonical:
            raise ValueError("effective pilot row canonical is blank")
        if risk not in grouped:
            raise ValueError(f"unknown effective risk for {canonical}: {risk}")
        if selection not in grouped:
            raise ValueError(f"unknown selection risk for {canonical}: {selection}")
        row["blind_key"] = _stable_key(BLIND_SEED, canonical)
        grouped[risk].append(row)
    for risk in grouped:
        grouped[risk].sort(
            key=lambda row: (
                0 if str(row["canonical"]) in overlap else 1,
                row["blind_key"],
                str(row["canonical"]),
            )
        )

    selected: list[dict[str, Any]] = []
    selected_canonicals: set[str] = set()
    achieved = {risk: 0 for risk in RISK_ORDER}
    source_counts = {risk: len(grouped[risk]) for risk in RISK_ORDER}
    for risk in RISK_ORDER:
        for row in grouped[risk][: BLIND_QUOTAS[risk]]:
            selected.append(row)
            selected_canonicals.add(str(row["canonical"]))
            achieved[risk] += 1

    # Preserve #39's one-way conservative backfill rule, but use effective-risk groups.
    for index, risk in enumerate(RISK_ORDER):
        missing = BLIND_QUOTAS[risk] - achieved[risk]
        if missing <= 0:
            continue
        for donor_risk in RISK_ORDER[index + 1 :]:
            donors = [
                row
                for row in grouped[donor_risk]
                if str(row["canonical"]) not in selected_canonicals
            ]
            for row in donors[:missing]:
                selected.append(row)
                selected_canonicals.add(str(row["canonical"]))
                achieved[risk] += 1
                missing -= 1
                if missing == 0:
                    break
            if missing == 0:
                break
        if missing:
            raise ValueError(f"cannot satisfy blind quota for {risk}; shortage={missing}")

    if len(selected) != 30:
        raise AssertionError(f"blind selection produced {len(selected)} rows")
    selected.sort(key=lambda row: (row["blind_key"], str(row["canonical"])))
    key = {
        "schema_version": "issue41-blind30-1",
        "blind_seed": BLIND_SEED,
        "requested_stratum_counts": dict(BLIND_QUOTAS),
        "achieved_stratum_counts": achieved,
        "source_effective_risk_counts": source_counts,
        "selected": [
            {
                "canonical": str(row["canonical"]),
                "selection_risk_class": str(
                    row.get("selection_risk_class", row.get("risk_class", ""))
                ),
                "effective_risk_class": str(row["effective_risk_class"]),
                "blind_key": row["blind_key"],
                "issue32_overlap": row.get("issue32_overlap", "NO"),
            }
            for row in selected
        ],
        "omitted_overlap": sorted(overlap - selected_canonicals),
    }
    return selected, key


def build(output_dir: Path) -> dict[str, Any]:
    rows = _read_jsonl(output_dir / "pilot_rows_effective.jsonl")
    if not rows:
        raise ValueError("pilot_rows_effective.jsonl is empty or missing")
    search_rows = _read_jsonl(output_dir / "search_terms.jsonl")
    evidence = _read_jsonl(output_dir / "evidence_manifest.jsonl")

    by_search: dict[str, list[dict[str, Any]]] = {}
    for row in search_rows:
        if row.get("term_state") in {"ACCEPTED", "REVIEW"}:
            by_search.setdefault(str(row.get("canonical", "")), []).append(
                {
                    "term": row.get("term", ""),
                    "term_class": row.get("term_class", ""),
                }
            )
    by_evidence: dict[str, list[dict[str, Any]]] = {}
    for row in evidence:
        by_evidence.setdefault(str(row.get("canonical", "")), []).append(row)

    selected, key = select_effective(rows)
    blind_input: list[dict[str, Any]] = []
    for row in selected:
        canonical = str(row["canonical"])
        semantic = [
            {
                "evidence_id": item.get("evidence_id", ""),
                "scope_note": item.get("scope_note", ""),
                "source_ref": item.get("source_ref", ""),
            }
            for item in by_evidence.get(canonical, [])
            if item.get("evidence_role") == "SEMANTIC_SCOPE"
        ]
        bridge = [
            {
                "evidence_id": item.get("evidence_id", ""),
                "scope_note": item.get("scope_note", ""),
                "source_ref": item.get("source_ref", ""),
            }
            for item in by_evidence.get(canonical, [])
            if item.get("evidence_role") == "BRIDGE32"
        ]
        blind_input.append(
            {
                "canonical": canonical,
                "candidate_display": row.get("display_candidate", ""),
                "search_terms": by_search.get(canonical, []),
                "semantic_evidence": semantic,
                "issue32_snapshot_evidence": bridge,
            }
        )

    _write_jsonl(output_dir / "blind30_input_issue41.jsonl", blind_input)
    (output_dir / "blind30_key_issue41.json").write_text(
        json.dumps(key, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return key


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.output_dir), ensure_ascii=False, indent=2))
