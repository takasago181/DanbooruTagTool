"""Build the deterministic, state-masked blind30 reviewer package."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    from .r3_common import (
        BLIND_QUOTAS,
        BLIND_SEED,
        RISK_ORDER,
        file_hash,
        read_json,
        read_jsonl,
        stable_key,
        ensure_r3_output,
        write_json,
        write_jsonl,
    )
except ImportError:  # pragma: no cover - supports direct CLI execution
    from r3_common import (
    BLIND_QUOTAS,
    BLIND_SEED,
    RISK_ORDER,
    file_hash,
    read_json,
    read_jsonl,
    stable_key,
    ensure_r3_output,
    write_json,
    write_jsonl,
    )


REVIEW_FIELDS = {
    "canonical", "display_judgement", "search_judgement", "bridge32_judgement", "review_note",
}


def _select(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    overlap = {row["canonical"] for row in rows if row.get("issue32_overlap") == "YES"}
    grouped: dict[str, list[dict[str, Any]]] = {risk: [] for risk in RISK_ORDER}
    for row in rows:
        item = dict(row)
        item["blind_key"] = stable_key(BLIND_SEED, str(row["canonical"]))
        grouped.setdefault(str(row["risk_class"]), []).append(item)
    for risk in grouped:
        grouped[risk].sort(key=lambda item: (0 if item["canonical"] in overlap else 1, item["blind_key"], item["canonical"]))

    selected: list[dict[str, Any]] = []
    selected_canonicals: set[str] = set()
    achieved = {risk: 0 for risk in RISK_ORDER}
    for risk in RISK_ORDER:
        for row in grouped.get(risk, [])[: BLIND_QUOTAS[risk]]:
            selected.append(row)
            selected_canonicals.add(row["canonical"])
            achieved[risk] += 1
    for index, risk in enumerate(RISK_ORDER):
        missing = BLIND_QUOTAS[risk] - achieved[risk]
        if missing <= 0:
            continue
        for donor_risk in RISK_ORDER[index + 1:]:
            donors = [row for row in grouped.get(donor_risk, []) if row["canonical"] not in selected_canonicals]
            for row in donors[:missing]:
                selected.append(row)
                selected_canonicals.add(row["canonical"])
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
    selected.sort(key=lambda row: (row["blind_key"], row["canonical"]))
    omitted_overlap = sorted(overlap - selected_canonicals)
    return selected, {
        "schema_version": "r3-1",
        "blind_seed": BLIND_SEED,
        "blind_algorithm_version": "r3-blind30-1",
        "requested_stratum_counts": dict(BLIND_QUOTAS),
        "achieved_stratum_counts": achieved,
        "selected": [
            {
                "canonical": row["canonical"],
                "risk_class": row["risk_class"],
                "blind_key": row["blind_key"],
                "issue32_overlap": row.get("issue32_overlap", "NO"),
            }
            for row in selected
        ],
        "omitted_overlap": omitted_overlap,
    }


def build(output_dir: Path, *, review_path: Path | None = None) -> dict[str, Any]:
    output_dir = output_dir.resolve()
    # ``.../translation_quarantine/r3`` is the output root in both the
    # repository and isolated test roots; parents[1] is that root's root.
    ensure_r3_output(output_dir.parents[1], output_dir)
    rows = read_jsonl(output_dir / "pilot_rows.jsonl")
    search_rows = read_jsonl(output_dir / "search_terms.jsonl")
    evidence = read_jsonl(output_dir / "evidence_manifest.jsonl")
    by_canonical_search: dict[str, list[dict[str, Any]]] = {}
    for row in search_rows:
        if row.get("term_state") in {"ACCEPTED", "REVIEW"}:
            by_canonical_search.setdefault(str(row["canonical"]), []).append({
                "term": row["term"],
                "term_class": row["term_class"],
            })
    by_canonical_evidence: dict[str, list[dict[str, Any]]] = {}
    for row in evidence:
        by_canonical_evidence.setdefault(str(row.get("canonical", "")), []).append(row)

    selected, key = _select(rows)
    blind_input = []
    for row in selected:
        canonical = str(row["canonical"])
        semantic_notes = [
            {
                "evidence_id": item["evidence_id"],
                "scope_note": item.get("scope_note", ""),
                "source_ref": item.get("source_ref", ""),
            }
            for item in by_canonical_evidence.get(canonical, [])
            if item.get("evidence_role") == "SEMANTIC_SCOPE"
        ]
        bridge_evidence = [
            {
                "evidence_id": item["evidence_id"],
                "scope_note": item.get("scope_note", ""),
                "source_ref": item.get("source_ref", ""),
            }
            for item in by_canonical_evidence.get(canonical, [])
            if item.get("evidence_role") == "BRIDGE32"
        ]
        blind_input.append({
            "canonical": canonical,
            "candidate_display": row.get("display_candidate", ""),
            "search_terms": by_canonical_search.get(canonical, []),
            "semantic_evidence": semantic_notes,
            "issue32_snapshot_evidence": bridge_evidence,
        })

    write_jsonl(output_dir / "blind30_input.jsonl", blind_input)
    write_json(output_dir / "blind30_key.json", key)
    if review_path and review_path.exists():
        review = read_jsonl(review_path)
        for row in review:
            if set(row) - REVIEW_FIELDS or not REVIEW_FIELDS <= set(row):
                raise ValueError(f"invalid blind review fields for {row.get('canonical')}")
            if row["display_judgement"] not in {"PASS", "FALSE_APPROVAL", "INSUFFICIENT_EVIDENCE"}:
                raise ValueError("invalid display judgement")
            if row["search_judgement"] not in {"PASS", "FALSE_APPROVAL", "INSUFFICIENT_EVIDENCE"}:
                raise ValueError("invalid search judgement")
            if row["bridge32_judgement"] not in {"PASS", "SILENT_CONTRADICTION", "NOT_APPLICABLE"}:
                raise ValueError("invalid bridge judgement")
    else:
        review = []
    write_jsonl(output_dir / "blind30_review.jsonl", review)

    metrics = {
        "selected": len(blind_input),
        "semantic_false_ready": sum(row.get("display_judgement") == "FALSE_APPROVAL" for row in review),
        "search_scope_false_ready": sum(row.get("search_judgement") == "FALSE_APPROVAL" for row in review),
        "silent_bridge_contradictions": sum(row.get("bridge32_judgement") == "SILENT_CONTRADICTION" for row in review),
        "review_rows": len(review),
        "state": "REVIEW_PENDING" if not review else "REVIEWED",
    }
    summary_path = output_dir / "run_summary.json"
    summary = read_json(summary_path)
    summary["blind30_gate_metrics"] = metrics
    write_json(summary_path, summary)

    manifest_path = output_dir / "run_manifest.json"
    if manifest_path.exists():
        manifest = read_json(manifest_path)
        manifest["generated_file_hashes"] = {
            name: file_hash(output_dir / name)
            for name in (
                "pilot_selection.json", "evidence_manifest.jsonl", "pilot_rows.jsonl",
                "search_terms.jsonl", "bridge32.jsonl", "blind30_input.jsonl",
                "blind30_key.json", "blind30_review.jsonl", "run_summary.json",
            )
        }
        write_json(manifest_path, manifest)
    return {"input": blind_input, "key": key, "review": review, "metrics": metrics}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--review", type=Path)
    args = parser.parse_args()
    build(args.output, review_path=args.review)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
