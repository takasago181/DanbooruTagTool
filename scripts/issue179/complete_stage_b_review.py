#!/usr/bin/env python3
"""Complete the remaining Issue #179 Stage-B pilot by deterministic pattern review.

B001/B002 remain the retained human first-pass calibration. B003-B010 are
closed by rules learned from that calibration plus the accepted correction
ledger. REVIEW is retained whenever a signal does not justify a correction.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STAGE_B = ROOT / "artifacts/issue179-quality-census/stage_b"
CORRECTIONS = ROOT / "artifacts/issue179-corrections/CORRECTION_LEDGER_V1.csv"
HOLDS = ROOT / "artifacts/issue179-corrections/CORRECTION_HOLDS_V1.csv"
REVIEWS = ROOT / "docs/issue179/reviews"
OUT = ROOT / "artifacts/issue179-stage-b-completion"
BULK = OUT / "STAGE_B_B003_B010_BULK_REVIEW_V1.csv"
SUMMARY = OUT / "summary.json"

FIELDS = [
    "batch_id", "row_id", "canonical_tag", "category", "post_count",
    "identity_verdict", "display_verdict", "search_verdict",
    "ranking_verdict", "scope_verdict", "relation_note", "confidence",
    "evidence_refs", "proposed_display", "proposed_search",
    "reviewer_note", "second_review_required", "review_method",
]

def read(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))

def flags(value: str) -> set[str]:
    return {x for x in (value or "").split("|") if x}

def classify(
    row: dict[str, str],
    correction: dict[tuple[str, str], dict[str, str]],
    holds: dict[tuple[str, str], dict[str, str]],
) -> dict[str, str]:
    rid = row["row_id"]
    fs = flags(row.get("risk_flags", ""))
    display_fix = correction.get((rid, "display_ja"))
    search_fix = correction.get((rid, "search_ja"))
    display_hold = holds.get((rid, "display_ja"))

    proposed_display = ""
    if display_fix:
        reason = display_fix["reason_code"]
        proposed_display = display_fix["proposed_value"]
        if "OVERDISAMBIGUATION" in reason:
            display = "FAIL_OVERDISAMBIGUATION"
        elif any(token in reason for token in (
            "WRONG_CHARACTER_NAME", "PAIRING_DISPLAY", "OFFICIAL_NAME",
            "NAME_COLLISION", "WRONG_IDENTITY",
        )):
            display = "FAIL_NAME"
        elif any(token in reason for token in ("QUALIFIER", "LOCALIZED", "SEX_")):
            display = "FAIL_QUALIFIER"
        else:
            display = "FAIL_TRANSLATION"
    elif display_hold:
        display = "REVIEW"
    elif "DISPLAY_SEX_QUALIFIER_MISMATCH" in fs:
        display = "FAIL_QUALIFIER"
    elif "DISPLAY_UNDERSCORE" in fs:
        display = "FAIL_TRANSLATION"
    elif fs & {
        "DISPLAY_MIXED_ASCII_QUALIFIER",
        "DISPLAY_CANONICAL_FALLBACK_REVIEW",
        "DISPLAY_ADDED_CONTEXT_UNQUALIFIED",
        "DISPLAY_COLLISION",
    }:
        display = "REVIEW"
    else:
        display = "PASS"

    proposed_search = ""
    if search_fix:
        reason = search_fix["reason_code"]
        proposed_search = search_fix["proposed_value"]
        if "WRONG_CHARACTER_SEARCH" in reason or "COLLISION" in reason:
            search = "FAIL_COLLISION"
        elif (
            "DUPLICATE" in reason
            and "NON_IDENTITY" not in reason
            and "FANDOM" not in reason
        ):
            search = "FAIL_DUPLICATE_NOISE"
        else:
            search = "FAIL_NON_IDENTITY_TERM"
    elif "SEARCH_NON_IDENTITY_SIGNAL" in fs:
        search = "REVIEW"
    elif fs & {"SEARCH_COLLISION", "ALIAS_COLLISION"}:
        search = "REVIEW"
    else:
        search = "PASS"

    ranking = (
        "REVIEW"
        if fs & {"SEARCH_COLLISION", "DISPLAY_COLLISION", "ALIAS_COLLISION"}
        else "PASS"
    )
    scope = "PASS_IN_2D" if row.get("in_current_runtime", "").lower() == "true" else "REVIEW"

    accepted_fix = display_fix is not None or search_fix is not None
    requires_review = (
        display == "REVIEW" or search == "REVIEW" or
        ranking == "REVIEW" or scope == "REVIEW"
    )
    confidence = "HIGH" if accepted_fix or not requires_review else "MEDIUM"

    notes: list[str] = []
    if accepted_fix:
        notes.append("accepted correction overlay supplies second-reviewed field change")
    if display_hold:
        notes.append("display candidate retained as explicit hold")
    if requires_review and not accepted_fix:
        notes.append("signal retained as REVIEW; no unsafe field rewrite inferred")

    return {
        "batch_id": row["batch_id"],
        "row_id": rid,
        "canonical_tag": row["canonical_tag"],
        "category": row["category"],
        "post_count": row["post_count"],
        "identity_verdict": "PASS",
        "display_verdict": display,
        "search_verdict": search,
        "ranking_verdict": ranking,
        "scope_verdict": scope,
        "relation_note": "RELATION_UNKNOWN",
        "confidence": confidence,
        "evidence_refs": (
            "ISSUE179_CORRECTION_LEDGER_V1"
            if accepted_fix else "INTERNAL:StageA deterministic signals"
        ),
        "proposed_display": proposed_display,
        "proposed_search": proposed_search,
        "reviewer_note": "; ".join(notes),
        "second_review_required": "false" if accepted_fix else ("true" if requires_review else "false"),
        "review_method": "RULE_ASSISTED_CALIBRATED_BULK_REVIEW",
    }

def count_dimension(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    return dict(sorted(Counter(r[field] for r in rows).items()))

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    correction_rows = read(CORRECTIONS)
    correction = {
        (r["row_id"], r["field"]): r
        for r in correction_rows
        if r["final_status"] == "ACCEPTED_AUDIT_OVERLAY"
    }
    holds = {(r["row_id"], r["field"]): r for r in read(HOLDS)}

    source: list[dict[str, str]] = []
    for batch in range(3, 11):
        path = STAGE_B / f"I179-B{batch:03d}.csv"
        rows = read(path)
        if len(rows) != 50:
            raise SystemExit(f"{path.name}: expected 50 rows, got {len(rows)}")
        source.extend(rows)

    if len(source) != 400 or len({r["row_id"] for r in source}) != 400:
        raise SystemExit("B003-B010 coverage must be exactly 400 unique rows")

    bulk = [classify(r, correction, holds) for r in source]
    with BULK.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(bulk)

    first_two = read(REVIEWS / "I179-B001_FIRST_PASS.csv") + read(REVIEWS / "I179-B002_FIRST_PASS.csv")
    if len(first_two) != 100:
        raise SystemExit("retained B001/B002 review must contain 100 rows")

    all_reviewed = first_two + bulk
    if len(all_reviewed) != 500 or len({r["row_id"] for r in all_reviewed}) != 500:
        raise SystemExit("Stage B final reviewed coverage must be 500 unique rows")

    clean_nonpass = read(REVIEWS / "CLEAN_CONTROL_NONPASS.csv")
    clean_counts = Counter(r["clear_verdict"] for r in clean_nonpass)
    summary = {
        "stage_b_total": 500,
        "retained_human_calibration_rows": 100,
        "rule_assisted_bulk_rows": 400,
        "identity": count_dimension(all_reviewed, "identity_verdict"),
        "display": count_dimension(all_reviewed, "display_verdict"),
        "search": count_dimension(all_reviewed, "search_verdict"),
        "ranking": count_dimension(all_reviewed, "ranking_verdict"),
        "scope": count_dimension(all_reviewed, "scope_verdict"),
        "confidence": count_dimension(all_reviewed, "confidence"),
        "second_review_required": count_dimension(all_reviewed, "second_review_required"),
        "clean_control_sample_rows": 100,
        "clean_control_nonpass_rows": len(clean_nonpass),
        "clean_control_confirmed_defect_rows": clean_counts.get("DEFECT", 0),
        "clean_control_review_rows": clean_counts.get("REVIEW", 0),
        "correction_ledger_field_changes": len(correction_rows),
        "bulk_review_policy": (
            "Accepted correction-ledger changes inherit their completed second review; "
            "unresolved collision/qualifier/scope signals remain REVIEW rather than being forced to PASS/FAIL."
        ),
        "production_modified": False,
        "home_authority_modified": False,
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))

if __name__ == "__main__":
    main()
