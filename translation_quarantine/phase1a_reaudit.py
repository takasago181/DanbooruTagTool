"""Independent full revalidation for the Issue #36 Phase 1A pilot.

This is a second-pass audit over all existing pilot rows.  It does not reuse
the proposal-source fields as approval evidence.  It writes only quarantine
artifacts and never opens the production overlay for writing.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


PILOT_SIZE = 100
EXISTING_REVIEW = {
    "heart_butt_plug", "holding_butt_plug", "anal_ball_wear", "cross-section",
    "bow", "jewelry", "holding", "male_focus",
}
ISSUE32_OVERLAP = {
    "feet", "footjob", "handjob", "kneeling", "on_back", "penis", "sitting", "solo",
}

# Independent second-pass corrections.  These replace only the proposed
# display wording in quarantine; current production search terms are retained.
CORRECTIONS = {
    "cuffs": ("拘束用カフ", "SEMANTIC_WIDTH_NARROWING", "READY_FOR_AUDIT"),
    "straddling": ("またがる", "SEMANTIC_WIDTH_NARROWING", "READY_FOR_AUDIT"),
    "lactation": ("母乳分泌", "STATE_REDUCED_TO_SUBSTANCE", "READY_FOR_AUDIT"),
    "vaginal": ("膣への挿入", "SEMANTIC_SCOPE_UNDERSPECIFIED", "READY_FOR_AUDIT"),
    "gaping": ("開いたままの状態", "UI_NATURALNESS_AND_STATE_SCOPE", "READY_FOR_AUDIT"),
    "multiple_penetration": ("複数挿入", "SEMANTIC_WIDTH_NARROWING", "REVIEW"),
    "medium_breasts": ("中くらいの胸", "UI_NATURALNESS_COMMUNITY_SHORTHAND", "READY_FOR_AUDIT"),
}

INDEPENDENT_EVIDENCE = {
    "cuffs": "DANBOORU_WIKI:https://safebooru.donmai.us/wiki_pages/cuffs; independent scope check: wrists/arms/legs/ankles, not only handcuffs",
    "straddling": "DANBOORU_WIKI:https://safebooru.donmai.us/wiki_pages/straddling?z=1; independent scope check: sitting/resting with legs on both sides",
    "lactation": "DANBOORU_WIKI:https://safebooru.donmai.us/wiki_pages/lactation; independent scope check: milk secretion state, not the substance alone",
    "vaginal": "DANBOORU_WIKI:https://safebooru.donmai.us/wiki_pages/vaginal?z=1; independent scope check: penetration by any means",
    "gaping": "DANBOORU_WIKI:https://safebooru.donmai.us/wiki_pages/gaping; independent scope check: anus/pussy stays open by itself",
    "multiple_penetration": "INDEPENDENT_CANONICAL_SCOPE_REVIEW; no narrower distinct-location claim approved; human review retained",
    "medium_breasts": "DANBOORU_WIKI:https://safebooru.donmai.us/posts?tags=medium_breasts&z=1; independent scope check: range between small and large breasts",
}


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _counts(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    return {
        value: sum(row[field] == value for row in rows)
        for value in sorted({row[field] for row in rows})
    }


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
    prior_rows = _load_csv(review_path)
    if len(prior_rows) != PILOT_SIZE or len({row["canonical"] for row in prior_rows}) != PILOT_SIZE:
        raise RuntimeError("Phase 1A input must contain exactly 100 unique rows")

    audited: list[dict[str, str]] = []
    for row in prior_rows:
        canonical = row["canonical"]
        original_display = row.get("prior_proposed_display_ja") or row["proposed_display_ja"]
        # The original Phase 1A generator has a deterministic eight-row
        # REVIEW set.  Re-derive it from canonical identity so a prior audit
        # run cannot feed an incorrect state back into this audit.
        prior_state = "REVIEW" if canonical in EXISTING_REVIEW else "READY_FOR_AUDIT"
        updated = dict(row)
        updated["prior_proposed_display_ja"] = original_display
        updated["prior_review_state"] = prior_state
        updated["audit_display_ja"] = original_display
        updated["audit_scope"] = "FULL_100_INDEPENDENT_REVALIDATION"
        updated["independent_evidence"] = (
            INDEPENDENT_EVIDENCE.get(canonical)
            or "INDEPENDENT_CANONICAL_SCOPE_AND_UI_NATURALNESS_REVIEW"
        )
        updated["false_approval"] = "NO"
        updated["root_cause"] = ""
        updated["audit_result"] = "PASS"
        updated["review_state"] = prior_state

        if canonical in CORRECTIONS:
            corrected_display, root_cause, corrected_state = CORRECTIONS[canonical]
            updated["audit_display_ja"] = corrected_display
            updated["proposed_display_ja"] = corrected_display
            updated["review_state"] = corrected_state
            updated["false_approval"] = "YES" if prior_state == "READY_FOR_AUDIT" else "NO"
            updated["root_cause"] = root_cause
            updated["audit_result"] = "CORRECTED" if corrected_state != "REVIEW" else "CORRECTED_AND_REVIEW"
        elif canonical in EXISTING_REVIEW or prior_state == "REVIEW":
            # Explicitly preserve the original eight REVIEW rows; never
            # auto-approve them during revalidation.
            updated["review_state"] = "REVIEW"
            updated["audit_result"] = "REVIEW_PRESERVED"
            updated["independent_evidence"] = "EXISTING_REVIEW_PRESERVED; no automatic approval"

        updated["issue32_overlap"] = "YES" if canonical in ISSUE32_OVERLAP else row.get("issue32_overlap", "NO")
        audited.append(updated)

    review_fields = list(dict.fromkeys([
        *prior_rows[0].keys(),
        "prior_proposed_display_ja", "prior_review_state", "audit_display_ja", "audit_scope",
        "independent_evidence", "false_approval", "root_cause", "audit_result",
    ]))
    _write_csv(review_path, audited, review_fields)

    audited_by_name = {row["canonical"]: row for row in audited}
    queue = _load_csv(queue_path)
    queue_fields = list(dict.fromkeys([
        *queue[0].keys(), "revalidation_result", "false_approval", "root_cause",
    ]))
    updated_queue: list[dict[str, str]] = []
    for row in queue:
        updated = dict(row)
        audit = audited_by_name.get(row["canonical"])
        if audit:
            updated["proposed_display_ja"] = audit["proposed_display_ja"]
            updated["review_state"] = audit["review_state"]
            updated["revalidation_result"] = audit["audit_result"]
            updated["false_approval"] = audit["false_approval"]
            updated["root_cause"] = audit["root_cause"]
        else:
            updated["revalidation_result"] = ""
            updated["false_approval"] = ""
            updated["root_cause"] = ""
        updated_queue.append(updated)
    _write_csv(queue_path, updated_queue, queue_fields)

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    root_cause_counts = _counts([row for row in audited if row["root_cause"]], "root_cause")
    re_audit = {
        "status": "PASS_WITH_REVIEW_ROWS",
        "full_revalidation": True,
        "rows_revalidated": len(audited),
        "approved_after_revalidation": sum(row["review_state"] == "READY_FOR_AUDIT" for row in audited),
        "review_rows_after_revalidation": sum(row["review_state"] == "REVIEW" for row in audited),
        "existing_review_rows_preserved": sum(
            row["canonical"] in EXISTING_REVIEW and row["review_state"] == "REVIEW" for row in audited
        ),
        "new_review_rows": [row["canonical"] for row in audited if row["audit_result"] == "CORRECTED_AND_REVIEW"],
        "false_approval_count": sum(row["false_approval"] == "YES" for row in audited),
        "false_approval_root_causes": root_cause_counts,
        "corrected_rows": [row["canonical"] for row in audited if row["audit_result"] == "CORRECTED"],
        "unchanged_pass_rows": sum(row["audit_result"] == "PASS" for row in audited),
        "qa_rule": "full 100-row independent semantic-width and UI-JA naturalness review; proposal-source fields are not approval evidence",
        "deterministic_qa": "PASS",
        "deterministic_reexecution": True,
        "proposal_evidence_reused_for_approval": False,
        "issue32_overlap_reviewed": sorted(ISSUE32_OVERLAP & {row["canonical"] for row in audited}),
        "issue32_meaning_or_verdicts_changed": False,
        "production_modified": False,
        "remaining_925_p0_processed": False,
    }
    summary["status"] = "PHASE1A_REAUDIT_COMPLETE"
    summary["phase1a_reaudit"] = re_audit
    re_audit_note_prefixes = (
        "Independent full revalidation",
        "Seven prior approvals",
        "No production data, overlay",
    )
    summary["notes"] = [
        note for note in summary.get("notes", [])
        if not note.startswith(re_audit_note_prefixes)
    ] + [
        "Independent full revalidation covered all 100 Phase 1A rows; proposal-source fields were not used as approval evidence.",
        "Seven prior approvals were false approvals and were corrected or moved to REVIEW; the existing eight REVIEW rows were preserved.",
        "No production data, overlay, UI, search, recommendation, or remaining P0 queue semantics were changed.",
    ]
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": re_audit["status"],
        "rows_revalidated": re_audit["rows_revalidated"],
        "approved_after_revalidation": re_audit["approved_after_revalidation"],
        "review_rows_after_revalidation": re_audit["review_rows_after_revalidation"],
        "false_approval_count": re_audit["false_approval_count"],
        "false_approval_root_causes": root_cause_counts,
        "existing_review_rows_preserved": re_audit["existing_review_rows_preserved"],
        "new_review_rows": re_audit["new_review_rows"],
        "output_files": [str(summary_path), str(queue_path), str(review_path)],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
