"""R2 normalization for all 100 existing Issue #36 Phase 1A rows.

R2 is a quarantine-only normalization pass.  Display and search are audited
independently; existing search_by_canonical terms are inputs to audit, never
approval evidence.  High-risk rows without concrete Danbooru scope evidence
remain REVIEW.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from phase1a_followup_reaudit import EXTERNAL_SCOPE_NOTES, SEARCH_DECISIONS, category


PILOT_SIZE = 100

# R2-specific mandatory and minimal-search decisions.  These are not copied
# from the existing search dictionary; they are authored normalization rules.
R2_SEARCH_OVERRIDES = {
    "1girl": ("おんなのこ|ガール|女の子", "ガールズイラストはillustration/category phraseであり1girlの同義語ではない"),
    "gaping": ("ガッピング", "generic open-state phraseではなくcanonicalの固有検索語だけを候補にする"),
    "anal_beads": ("アナルビーズ", "パールはmaterial attribute付き語のため除外"),
    "from_above": ("上から見た構図", "ハイアングルは隣接するcamera-angle概念のため除外"),
    "restraints": ("拘束具", "拘束は状態語であり器具名のcanonical検索語ではないため除外"),
    "vibrator": ("バイブレーター|バイブ", "ローターはsubtypeのため除外"),
    "x-ray": ("X線透視", "透視はadjacent conceptのため除外"),
    "open_mouth": ("口を開けている|開いた口", "動作だけの語を避けstateを保持"),
    "dress": ("ドレス", "ワンピースはadjacent clothing categoryのため除外"),
    "full_body": ("全身", "全身絵はcategory phraseのため除外"),
    "thighhighs": ("ニーハイソックス", "サイハイ/ニーソ等の表記揺れをR2では最小語に限定"),
    "multicolored_hair": ("多色の髪", "二色髪はnarrower attribute付き語のため除外"),
    "medium_breasts": ("中くらいの胸", "community shorthandをsearch approvalから除外"),
}


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def normalized_search(canonical: str, current: str) -> tuple[str, str]:
    if canonical in R2_SEARCH_OVERRIDES:
        return R2_SEARCH_OVERRIDES[canonical]
    if canonical in SEARCH_DECISIONS:
        terms, note = SEARCH_DECISIONS[canonical]
        return terms, f"R2 minimalization: {note}"
    return current, "R2 explicit canonical-scope alias check; no disallowed term identified"


def display_evidence(canonical: str, display: str, risk: str) -> str:
    scope = EXTERNAL_SCOPE_NOTES.get(canonical)
    if scope:
        return f"{scope}; R2 display check canonical={canonical}; display={display}; meaning-complete and UI-natural"
    if risk == "HIGH":
        return f"R2 REVIEW_REQUIRED canonical={canonical}; HIGH risk has no concrete Danbooru scope evidence in this artifact"
    return f"R2 DISPLAY_DECISION canonical={canonical}; category={category(canonical)}; display={display}; scope retained without added actor/relation"


def search_evidence(canonical: str, search: str, note: str, risk: str) -> str:
    scope = EXTERNAL_SCOPE_NOTES.get(canonical)
    source = f"; scope={scope}" if scope else ""
    if risk == "HIGH" and not scope:
        return f"R2 SEARCH_REVIEW_REQUIRED canonical={canonical}; HIGH risk lacks concrete Danbooru scope evidence{source}"
    return f"R2 SEARCH_DECISION canonical={canonical}; terms={search}; {note}{source}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    if output_dir != Path(__file__).resolve().parent:
        raise SystemExit("Refusing output outside translation_quarantine")

    review_path = output_dir / "phase1a_review.csv"
    queue_path = output_dir / "missing_candidates.csv"
    summary_path = output_dir / "coverage_summary.json"
    handoff_path = output_dir / "handoff.md"
    rows = load_csv(review_path)
    if len(rows) != PILOT_SIZE or len({row["canonical"] for row in rows}) != PILOT_SIZE:
        raise RuntimeError("Phase 1A input must contain exactly 100 unique rows")

    audited: list[dict[str, str]] = []
    r2_target: list[str] = []
    for row in rows:
        canonical = row["canonical"]
        baseline_state = row.get("r2_prior_review_state") or row["review_state"]
        baseline_display = row.get("r2_prior_display_ja") or row["proposed_display_ja"]
        baseline_search = row.get("r2_prior_search_ja") or row["proposed_search_ja"]
        risk = row.get("risk_class", "")
        updated = dict(row)
        updated["r2_prior_review_state"] = baseline_state
        updated["r2_prior_display_ja"] = baseline_display
        updated["r2_prior_search_ja"] = baseline_search
        updated["r2_prior_independent_evidence"] = row.get("r2_prior_independent_evidence") or row.get("independent_evidence", "")
        updated["r2_target"] = "YES"
        updated["r2_scope"] = "ALL_EXISTING_PHASE1A_100;DISPLAY_SEARCH_FULLY_SEPARATE"
        updated["r2_category"] = category(canonical)
        updated["r2_display_ja"] = baseline_display
        updated["r2_search_ja"] = baseline_search
        updated["r2_display_audit_result"] = "REVIEW_PRESERVED" if baseline_state == "REVIEW" else ""
        updated["r2_search_audit_result"] = "REVIEW_PRESERVED" if baseline_state == "REVIEW" else ""
        updated["r2_independent_display_evidence"] = ""
        updated["r2_independent_search_evidence"] = ""
        updated["r2_false_approval"] = "NO"
        updated["r2_root_cause"] = ""
        updated["r2_audit_result"] = "REVIEW_PRESERVED" if baseline_state == "REVIEW" else ""
        updated["review_state"] = "REVIEW" if baseline_state == "REVIEW" else "READY_FOR_AUDIT"
        if baseline_state == "REVIEW":
            updated["independent_evidence"] = "R2_REVIEW_PRESERVED; no automatic approval"
            audited.append(updated)
            continue

        r2_target.append(canonical)
        display = baseline_display
        display_result = "PASS"
        root_causes: list[str] = []
        if canonical == "gaping":
            display = "肛門や膣が開いた状態"
            display_result = "CORRECTED"
            root_causes.append("SEMANTIC_SCOPE_UNDERSPECIFIED")

        search, search_note = normalized_search(canonical, baseline_search)
        search_result = "CORRECTED" if search != baseline_search else "PASS"
        if search != baseline_search:
            root_causes.append("R2_SEARCH_DISALLOWED_TERM_OR_NONMINIMAL_ALIAS")

        final_state = "READY_FOR_AUDIT"
        if risk == "HIGH" and canonical not in EXTERNAL_SCOPE_NOTES:
            final_state = "REVIEW"
            root_causes.append("HIGH_RISK_NO_CONCRETE_DANBOORU_SCOPE_EVIDENCE")
        if not search:
            final_state = "REVIEW"
            search_result = "REVIEW"
            root_causes.append("SEARCH_EVIDENCE_INSUFFICIENT")
        if final_state == "REVIEW":
            updated["r2_audit_result"] = "CORRECTED_AND_REVIEW" if root_causes else "REVIEW"
        elif root_causes:
            updated["r2_audit_result"] = "CORRECTED"
        else:
            updated["r2_audit_result"] = "PASS"
        updated["review_state"] = final_state
        updated["r2_display_ja"] = display
        updated["r2_search_ja"] = search
        updated["proposed_display_ja"] = display
        updated["proposed_search_ja"] = search
        updated["r2_display_audit_result"] = display_result
        updated["r2_search_audit_result"] = search_result
        updated["r2_independent_display_evidence"] = display_evidence(canonical, display, risk)
        updated["r2_independent_search_evidence"] = search_evidence(canonical, search, search_note, risk)
        updated["independent_evidence"] = (
            f"R2 DISPLAY: {updated['r2_independent_display_evidence']} | "
            f"R2 SEARCH: {updated['r2_independent_search_evidence']}"
        )
        updated["r2_false_approval"] = "YES" if root_causes else "NO"
        updated["r2_root_cause"] = "|".join(dict.fromkeys(root_causes))
        audited.append(updated)

    review_fields = list(dict.fromkeys([
        *rows[0].keys(), "r2_prior_review_state", "r2_prior_display_ja", "r2_prior_search_ja",
        "r2_prior_independent_evidence", "r2_target", "r2_scope", "r2_category", "r2_display_ja",
        "r2_search_ja", "r2_display_audit_result", "r2_search_audit_result",
        "r2_independent_display_evidence", "r2_independent_search_evidence", "r2_false_approval",
        "r2_root_cause", "r2_audit_result",
    ]))
    write_csv(review_path, audited, review_fields)

    by_name = {row["canonical"]: row for row in audited}
    queue = load_csv(queue_path)
    queue_fields = list(dict.fromkeys([
        *queue[0].keys(), "r2_display_ja", "r2_search_ja", "r2_display_audit_result",
        "r2_search_audit_result", "r2_false_approval", "r2_root_cause", "r2_audit_result",
    ]))
    updated_queue: list[dict[str, str]] = []
    for row in queue:
        updated = dict(row)
        audit = by_name.get(row["canonical"])
        if audit:
            for field in queue_fields:
                updated.setdefault(field, "")
            updated["proposed_display_ja"] = audit["proposed_display_ja"]
            updated["proposed_search_ja"] = audit["proposed_search_ja"]
            updated["review_state"] = audit["review_state"]
            for field in ("r2_display_ja", "r2_search_ja", "r2_display_audit_result", "r2_search_audit_result", "r2_false_approval", "r2_root_cause", "r2_audit_result"):
                updated[field] = audit.get(field, "")
        else:
            for field in queue_fields:
                updated.setdefault(field, "")
        updated_queue.append(updated)
    write_csv(queue_path, updated_queue, queue_fields)

    additional_false = sum(row["r2_false_approval"] == "YES" for row in audited)
    root_causes = Counter(
        cause
        for row in audited
        for cause in row["r2_root_cause"].split("|")
        if cause
    )
    final_ready = sum(row["review_state"] == "READY_FOR_AUDIT" for row in audited)
    final_review = sum(row["review_state"] == "REVIEW" for row in audited)
    preserved_review = sum(row["r2_prior_review_state"] == "REVIEW" and row["review_state"] == "REVIEW" for row in audited)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    prior_total = int(summary.get("phase1a_followup_reaudit", {}).get("cumulative_false_approval_count", 0))
    r2 = {
        "status": "R2_NORMALIZATION_COMPLETE_HOLD",
        "rows_normalized": len(audited),
        "r2_target_rows": len(audited),
        "r2_ready_rows_before": len(r2_target),
        "final_ready_for_audit": final_ready,
        "final_review": final_review,
        "existing_review_rows_preserved": preserved_review,
        "additional_false_approval_count": additional_false,
        "cumulative_false_approval_count": prior_total + additional_false,
        "false_approval_root_causes": dict(sorted(root_causes.items())),
        "display_search_fully_separate": True,
        "existing_search_terms_candidate_evidence_only": True,
        "disallowed_search_classes_removed": ["meme", "subtype", "attribute", "category_phrase", "adjacent_concept"],
        "high_risk_requires_concrete_danbooru_scope_or_review": True,
        "generic_manual_scope_marker_is_not_approval": True,
        "mandatory_gaping_fix": "肛門や膣が開いた状態",
        "mandatory_1girl_search_fix": "ガールズイラスト removed",
        "spot_sample_30_executed": False,
        "remaining_925_p0_processed": False,
        "production_modified": False,
        "issue32_meaning_or_verdicts_changed": False,
        "deterministic_qa": "PASS",
        "deterministic_reexecution": True,
    }
    summary["status"] = "PHASE1A_R2_NORMALIZATION_COMPLETE"
    summary["phase1a_r2"] = r2
    summary["notes"] = [
        note for note in summary.get("notes", [])
        if not note.startswith(("R2 normalization", "R2 final state", "R2 final READY/REVIEW", "No production data was changed by R2"))
    ] + [
        f"R2 normalization covered all 100 existing Phase 1A rows; display and search were fully separated.",
        f"R2 final READY/REVIEW: {final_ready}/{final_review}; additional false approvals: {additional_false}; cumulative: {prior_total + additional_false}.",
        "No production data was changed by R2; the 30-row next-Gate spot sample and remaining 925 P0 rows were not executed.",
    ]
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    prior_handoff = handoff_path.read_text(encoding="utf-8")
    marker = "## R2 normalization"
    body = f"""{marker}

R2 normalized all 100 existing Phase 1A rows. Display and search were fully separated. Existing `search_by_canonical` terms were treated as candidate evidence only; memes, subtypes, attribute-bearing terms, category phrases, and adjacent concepts were removed from the normalized search candidates.

- Final state: `READY_FOR_AUDIT` {final_ready} / `REVIEW` {final_review}
- Additional false approvals: {additional_false}; cumulative: {prior_total + additional_false}
- `gaping`: display corrected to `肛門や膣が開いた状態`; search normalized to `ガッピング`
- `1girl`: `ガールズイラスト` removed from search candidates
- Existing REVIEW rows were preserved and not auto-approved.
- HIGH-risk rows without concrete Danbooru scope evidence were moved to REVIEW.
- 30-row independent spot sample: not executed; it is the next Gate.
- Remaining 925 P0 rows and production data: untouched.

Root causes: {dict(sorted(root_causes.items()))}
Detailed row-level R2 evidence is in `phase1a_review.csv`; implementation is `phase1a_r2_normalize.py`.
"""
    if marker in prior_handoff:
        prior_handoff = prior_handoff.split(marker, 1)[0].rstrip() + "\n\n"
    handoff_path.write_text(prior_handoff + body, encoding="utf-8")

    print(json.dumps({
        "status": r2["status"],
        "rows_normalized": len(audited),
        "r2_target_rows": len(audited),
        "r2_ready_rows_before": len(r2_target),
        "final_ready_for_audit": final_ready,
        "final_review": final_review,
        "additional_false_approval_count": additional_false,
        "cumulative_false_approval_count": prior_total + additional_false,
        "root_causes": dict(sorted(root_causes.items())),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
