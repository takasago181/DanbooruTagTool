"""Extend the existing Issue #36 masked20 without rerunning the canary.

This module consumes only committed canary artifacts and the frozen queue.  It
does not call the canary selector or the R3 evaluator.  The extra challenge
rows are deliberately allowed to have empty candidate/evidence fields: the
review must see the absence rather than receive guessed semantic evidence.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .r3_bulk_run import MASKED_FIELDS, check_masked_rows
    from .r3_common import read_csv, read_json, read_jsonl, stable_key, write_json, write_jsonl
except ImportError:  # pragma: no cover
    from r3_bulk_run import MASKED_FIELDS, check_masked_rows
    from r3_common import read_csv, read_json, read_jsonl, stable_key, write_json, write_jsonl


AUDIT50_SEED = "UIJA-R3-BULK-CANARY-AUDIT50-20260909-V1"
HARD_ADULT_CHALLENGE = (
    "areola_slip",
    "bottomless",
    "cameltoe",
    "completely_nude",
    "oral",
    "licking",
    "testicles",
    "topless_female",
    "topless_male",
    "underboob",
)
SEXUAL_SEMANTIC_CHALLENGE = (
    "brown_pantyhose",
    "black_pantyhose",
    "white_pantyhose",
    "pantyhose",
    "panty_pull",
    "pantyshot",
    "nude",
    "male_pubic_hair",
    "female_pubic_hair",
    "pubic_hair",
    "sideboob",
    "kiss",
    "yuri",
    "yaoi",
    "finger_to_mouth",
    "girl_on_top",
    "hand_on_another's_head",
    "from_behind",
    "on_stomach",
    "looking_at_another",
)


def _output(root: Path, output: Path | None) -> Path:
    allowed = (root / "translation_quarantine" / "r3_bulk_canary").resolve()
    target = (output or allowed).resolve()
    target.relative_to(allowed)
    target.mkdir(parents=True, exist_ok=True)
    return target


def _eligible_p0(root: Path) -> set[str]:
    phase1a = {str(row.get("canonical", "")) for row in read_csv(root / "translation_quarantine" / "phase1a_review.csv")}
    issue41 = {str(row.get("canonical", "")) for row in read_json(root / "translation_quarantine" / "r3" / "pilot_selection.json").get("selected", [])}
    return {
        str(row.get("canonical", ""))
        for row in read_csv(root / "translation_quarantine" / "missing_candidates.csv")
        if row.get("priority") == "P0"
        and str(row.get("canonical", ""))
        and str(row.get("canonical", "")) not in phase1a | issue41
    }


def _masked_record(
    canonical: str,
    rows_by_canonical: dict[str, dict[str, Any]],
    search_by_canonical: dict[str, list[dict[str, Any]]],
    evidence_by_canonical: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    row = rows_by_canonical.get(canonical, {})
    evidence = evidence_by_canonical.get(canonical, [])
    return {
        "canonical": canonical,
        "candidate_display": row.get("display_candidate", ""),
        "search_terms": search_by_canonical.get(canonical, []),
        "semantic_evidence": [
            {
                "evidence_id": item["evidence_id"],
                "scope_note": item.get("scope_note", ""),
                "source_ref": item.get("source_ref", ""),
            }
            for item in evidence
            if item.get("evidence_role") == "SEMANTIC_SCOPE"
        ],
        "issue32_snapshot_evidence": [
            {
                "evidence_id": item["evidence_id"],
                "scope_note": item.get("scope_note", ""),
                "source_ref": item.get("source_ref", ""),
            }
            for item in evidence
            if item.get("evidence_role") == "BRIDGE32"
        ],
    }


def generate(root: Path, output: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    target = _output(root, output)
    current_input = read_jsonl(target / "masked_audit20_input.jsonl")
    if len(current_input) != 20:
        raise ValueError("existing masked audit20 must contain exactly 20 rows")
    current_canonicals = [str(row.get("canonical", "")) for row in current_input]
    if len(set(current_canonicals)) != 20:
        raise ValueError("existing masked audit20 contains duplicate canonicals")

    selection = read_json(target / "canary_selection.json")
    canary_rows = read_jsonl(target / "rows.jsonl")
    if selection.get("canary_size") != 200 or len(canary_rows) != 200:
        raise ValueError("current 200-row canary artifacts are missing or altered")
    canary_canonicals = {str(row.get("canonical", "")) for row in selection.get("selected", [])}
    canary_row_map = {str(row["canonical"]): row for row in canary_rows}
    if canary_canonicals != set(canary_row_map):
        raise ValueError("canary selection and rows do not have identical membership")

    hard = list(HARD_ADULT_CHALLENGE)
    sexual = list(SEXUAL_SEMANTIC_CHALLENGE)
    additional = hard + sexual
    if len(set(additional)) != 30:
        raise ValueError("challenge lists must contain 30 unique canonicals")
    existing = set(current_canonicals)
    if existing & set(additional):
        raise ValueError(f"challenge canonical already used by audit20: {sorted(existing & set(additional))}")
    allowed = canary_canonicals | _eligible_p0(root)
    if not set(additional) <= allowed:
        raise ValueError(f"challenge canonical is outside canary/eligible queue: {sorted(set(additional) - allowed)}")

    search_by_canonical: dict[str, list[dict[str, Any]]] = {}
    for row in read_jsonl(target / "search_terms.jsonl"):
        search_by_canonical.setdefault(str(row["canonical"]), []).append({
            "term": row["term"],
            "term_class": row["term_class"],
        })
    evidence_by_canonical: dict[str, list[dict[str, Any]]] = {}
    for row in read_jsonl(target / "evidence_manifest.jsonl"):
        evidence_by_canonical.setdefault(str(row["canonical"]), []).append(row)

    records_by_canonical = {
        canonical: _masked_record(canonical, canary_row_map, search_by_canonical, evidence_by_canonical)
        for canonical in set(current_canonicals) | set(additional)
    }
    selected = [records_by_canonical[canonical] for canonical in set(current_canonicals) | set(additional)]
    selected.sort(key=lambda row: (stable_key(AUDIT50_SEED, row["canonical"]), row["canonical"]))

    category = {
        **{canonical: "NORMAL_MASKED_AUDIT20" for canonical in current_canonicals},
        **{canonical: "HARD_ADULT_SEMANTIC_CHALLENGE" for canonical in hard},
        **{canonical: "ADDITIONAL_SEXUAL_SEMANTIC_CHALLENGE" for canonical in sexual},
    }
    key_rows = []
    for row in selected:
        canonical = row["canonical"]
        source = "CURRENT_CANARY" if canonical in canary_canonicals else "ELIGIBLE_QUEUE"
        canary_row = canary_row_map.get(canonical, {})
        key_rows.append({
            "canonical": canonical,
            "audit_key": stable_key(AUDIT50_SEED, canonical),
            "selection_group": category[canonical],
            "source_membership": source,
            "effective_risk_class": canary_row.get("risk_class", ""),
            "display_state": canary_row.get("display_state", ""),
            "search_state": canary_row.get("search_state", ""),
            "bridge32_state": canary_row.get("bridge32_state", ""),
            "row_state": canary_row.get("row_state", ""),
            "reason_codes": canary_row.get("reason_codes", []),
        })
    key = {
        "schema_version": "issue36-bulk-audit50-key-1",
        "audit_seed": AUDIT50_SEED,
        "selection_counts": {
            "NORMAL_MASKED_AUDIT20": 20,
            "HARD_ADULT_SEMANTIC_CHALLENGE": 10,
            "ADDITIONAL_SEXUAL_SEMANTIC_CHALLENGE": 20,
        },
        "canary_membership_hash": selection.get("canary_membership_hash", ""),
        "selected": key_rows,
    }
    input_path = target / "masked_audit50_input.jsonl"
    key_path = target / "masked_audit50_key.json"
    leakage_path = target / "masked_audit50_leakage_check.json"
    write_jsonl(input_path, selected)
    write_json(key_path, key)
    leakage = check_masked_rows(selected, key, input_path.read_text(encoding="utf-8"))
    forbidden_input_fields = {
        "state", "risk", "reason", "key", "prior_verdict", "prior_review_verdict",
        "selection_group", "source_membership", "effective_risk_class", "display_state",
        "search_state", "bridge32_state", "row_state", "reason_codes", "audit_key",
    }
    leaked_input_fields = sorted(
        forbidden_input_fields & set().union(*(set(row) for row in selected))
    )
    leakage["leaked_masked_fields"] = sorted(
        set(leakage.get("leaked_masked_fields", [])) | set(leaked_input_fields)
    )
    leakage["ok"] = not leakage["leaked_masked_fields"] and not leakage.get("leaked_key_values") and not leakage.get("forbidden_state_literals")
    leakage["schema_version"] = "issue36-bulk-audit50-leakage-1"
    leakage["masked_rows"] = len(selected)
    write_json(leakage_path, leakage)
    return {
        "input": str(input_path),
        "key": str(key_path),
        "leakage": str(leakage_path),
        "rows": len(selected),
        "selection_counts": dict(Counter(category.values())),
        "canary_rerun": False,
        "leakage_ok": leakage["ok"],
        "self_grade": "NOT_PERFORMED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "r3_bulk_canary")
    args = parser.parse_args()
    print(json.dumps(generate(args.root, args.output), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
