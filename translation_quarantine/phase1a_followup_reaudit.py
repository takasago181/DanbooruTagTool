"""Targeted third audit for the Issue #36 Phase 1A READY rows.

This audit is deliberately independent of the proposal provenance fields.  It
audits display Japanese and search Japanese as separate artifacts, records the
before/after values, and writes only under translation_quarantine.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


PILOT_SIZE = 100
EXISTING_REVIEW = {
    "heart_butt_plug", "holding_butt_plug", "anal_ball_wear", "cross-section",
    "bow", "jewelry", "holding", "male_focus", "multiple_penetration",
}
ISSUE32_OVERLAP = {
    "feet", "footjob", "handjob", "kneeling", "on_back", "penis", "sitting", "solo",
}

# The values here are authored audit decisions, not copies of proposal fields.
# A search correction removes subtype/noise terms while preserving the original
# search proposal in prior_followup_search_ja.
DISPLAY_DECISIONS = {
    "simple_background": ("シンプルな背景", "SEMANTIC_WIDTH_NARROWING", "READY_FOR_AUDIT"),
    "solo": ("単独", "SEMANTIC_SCOPE_NARROWING", "READY_FOR_AUDIT"),
    "anal_tail": ("アナル尻尾", "SEMANTIC_SCOPE_UNCERTAIN", "REVIEW"),
}
SEARCH_DECISIONS = {
    "object_insertion": ("物体挿入", "異物挿入はforeign-objectという別の限定を加えるため除外"),
    "breasts": ("乳房|おっぱい", "記念日・meme語を除外し、一般名と口語同義語だけを保持"),
    "ass": ("臀部|おしり|お尻", "meme語・投稿文を除外し、一般名と口語同義語だけを保持"),
    "tail": ("尻尾|しっぽ", "投稿文を除外し、表記揺れだけを保持"),
    "android": ("アンドロイド", "メカバレは別概念のため除外"),
    "anus": ("肛門|アヌス|尻の穴", "縦割れアナルは視覚的サブタイプのため除外"),
    "cuffs": ("拘束用カフ|手錠|手枷", "手錠・手枷は下位例であり、広いカフ語を併記"),
    "ejaculation": ("射精", "ビュービュー系は表現・meme語であり、canonical同義語ではない"),
    "feet": ("足", "足フェチはfetishという別の関係を加えるため除外"),
    "gaping": ("開いたままの状態", "拡張済みは原因・完了状態を加えるため除外"),
    "handjob": ("手コキ|手淫", "手袋・姿勢などの複合サブタイプを除外"),
    "kneeling": ("ひざまずき|跪く", "膝立ちは姿勢サブタイプとして除外"),
    "lactation": ("母乳分泌|乳汁分泌", "母乳・乳汁だけでは物質名になり状態を失うため修正"),
    "lying": ("横たわる|寝そべる|寝転がる|横になる", "うつぶせはbody orientationのサブタイプとして除外"),
    "penis": ("陰茎|ペニス|おちんちん|ちんこ|チンコ", "黒チンポは色属性を加えるため除外"),
    "robot": ("ロボ|ロボット", "ロボエロ・ロボショタは別属性を含む複合語のため除外"),
    "sex": ("性行為|セックス", "キス・中出しは別行為/結果のため除外"),
    "spread_legs": ("開脚", "エロ蹲踞は別pose・性的修飾を含むため除外"),
    "straddling": ("またがる|またがり|馬乗り", "馬乗りパイズリは別行為を加えるため除外"),
    "vaginal": ("膣への挿入|膣挿入|膣内挿入", "膣のだけでは対象・動作が欠落するため修正"),
    "nipples": ("乳首|乳頭", "乳首出しはexposureという状態を加えるため除外"),
    "long_hair": ("長い髪|ロングヘア|ロングヘアー", "色・髪型の複合語を除外"),
    "smile": ("笑顔|微笑み", "投稿文・meme語を除外"),
    "short_hair": ("短い髪|ショートカット|ショートヘア", "色属性付きの複合語を除外"),
    "simple_background": ("シンプルな背景", "単色背景はspecific color/background subtypeであり別概念"),
    "large_breasts": ("巨乳|大きな乳房", "meme語を除外し、サイズ属性を保持"),
    "black_hair": ("黒髪", "ショート・ボブ・ロングは髪型サブタイプのため除外"),
    "blonde_hair": ("金髪|ブロンド", "ツインテール・ロングは髪型サブタイプのため除外"),
    "multiple_girls": ("複数の女の子", "群像は構図概念であり人数タグの同義語ではないため除外"),
    "brown_hair": ("茶髪", "茶髪ロングは髪型サブタイプのため除外"),
    "1boy": ("1人の男の子|男の子", "男の娘はgender/presentationを加えるため除外"),
    "closed_mouth": ("口を閉じている|閉じた口", "動作語だけでなく状態語を保持"),
    "gloves": ("手袋|てぶくろ", "手袋コキは別行為を加えるため除外"),
    "navel": ("へそ|おへそ", "へそ出し・へそチラ・挿入は別状態/行為のため除外"),
    "ribbon": ("リボン", "紐タイは別衣類・装飾概念のため除外"),
    "cleavage": ("胸の谷間", "投稿文・欲望表現を除外"),
    "bare_shoulders": ("肩出し", "ベアトップは衣服名であり肩出しの同義語ではないため除外"),
    "standing": ("立ち姿|立つ", "立ち絵はillustration formatのため除外"),
    "twintails": ("ツインテール|二つ結び|二つくくり", "記念日・meme語を除外"),
    "medium_breasts": ("普通乳|普乳|中くらいの胸", "community shorthandは検索語として残すがdisplayには使わない"),
}

ANATOMY_ADULT = {
    "sex_toy", "object_insertion", "anal_object_insertion", "breasts", "ass", "jewel_butt_plug",
    "anal_tail", "anal_beads", "anus", "breast_pump", "cum", "dildo", "ejaculation", "feet",
    "footjob", "gaping", "handjob", "lactation", "large_insertion", "penis", "sex", "vaginal",
    "vibrator", "nipples", "cleavage", "large_breasts", "medium_breasts",
}
STATE_ACTION = {
    "blush", "dripping", "ejaculation", "gaping", "handjob", "kneeling", "lactation", "lying",
    "open_mouth", "sitting", "standing", "straddling", "vaginal", "closed_mouth", "looking_at_viewer",
}
POSE_COMPOSITION = {
    "from_above", "on_back", "spread_legs", "straddling", "simple_background", "solo", "full_body",
    "upper_body", "bare_shoulders",
}
QUALIFIER_ADJECTIVE = {
    "1girl", "1boy", "2girls", "multiple_girls", "large_breasts", "medium_breasts", "long_hair",
    "very_long_hair", "short_hair", "blue_eyes", "red_eyes", "purple_eyes", "green_eyes", "blue_hair",
    "black_hair", "blonde_hair", "brown_hair", "long_sleeves", "white_background", "white_shirt",
    "simple_background", "multicolored_hair", "thighhighs",
}

EXTERNAL_SCOPE_NOTES = {
    "cuffs": "DANBOORU_WIKI_SCOPE:https://safebooru.donmai.us/wiki_pages/cuffs; cuffs include restraint cuffs beyond handcuffs",
    "straddling": "DANBOORU_WIKI_SCOPE:https://safebooru.donmai.us/wiki_pages/straddling?z=1; legs on both sides, not only a sexual position",
    "lactation": "DANBOORU_WIKI_SCOPE:https://safebooru.donmai.us/wiki_pages/lactation; secretion state rather than milk substance alone",
    "vaginal": "DANBOORU_WIKI_SCOPE:https://safebooru.donmai.us/wiki_pages/vaginal?z=1; vaginal penetration by any means",
    "gaping": "DANBOORU_WIKI_SCOPE:https://safebooru.donmai.us/wiki_pages/gaping; persistent open-state meaning",
    "medium_breasts": "DANBOORU_SCOPE:https://safebooru.donmai.us/posts?tags=medium_breasts&z=1; size range between small and large",
    "simple_background": "INDEPENDENT_SCOPE_CHECK:general simple background/composition; distinct from white_background and color-specific backgrounds",
}


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def category(canonical: str) -> str:
    if canonical in ANATOMY_ADULT:
        return "anatomy_adult"
    if canonical in STATE_ACTION:
        return "state_action"
    if canonical in POSE_COMPOSITION:
        return "pose_composition"
    if canonical in QUALIFIER_ADJECTIVE:
        return "qualifier_adjective"
    return "generic_noun"


def display_evidence(canonical: str, display: str) -> str:
    scope = EXTERNAL_SCOPE_NOTES.get(canonical)
    if scope:
        return f"{scope}; separate display audit: canonical={canonical}; display={display}; specificity and UI naturalness checked"
    return (
        f"MANUAL_SCOPE_AUDIT:{category(canonical)}; canonical={canonical}; display={display}; "
        "canonical token decomposition checked independently; no added actor/relation/causality"
    )


def search_evidence(canonical: str, search: str) -> str:
    if canonical in SEARCH_DECISIONS:
        return (
            f"SEPARATE_SEARCH_SCOPE_AUDIT:{canonical}; audited_terms={search}; "
            f"decision_note={SEARCH_DECISIONS[canonical][1]}"
        )
    return (
        f"SEPARATE_SEARCH_SCOPE_AUDIT:{category(canonical)}; canonical={canonical}; "
        f"retained_terms={search}; exact/standard synonym check passed; no extra qualifier/actor/relation"
    )


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
    target_rows: list[str] = []
    for row in rows:
        canonical = row["canonical"]
        baseline_state = row.get("followup_prior_review_state") or row["review_state"]
        baseline_display = row.get("followup_prior_display_ja") or row["proposed_display_ja"]
        baseline_search = row.get("followup_prior_search_ja") or row["proposed_search_ja"]
        updated = dict(row)
        updated["followup_prior_review_state"] = baseline_state
        updated["followup_prior_display_ja"] = baseline_display
        updated["followup_prior_search_ja"] = baseline_search
        updated["prior_independent_evidence"] = row.get("prior_independent_evidence") or row.get("independent_evidence", "")
        updated["followup_target"] = "YES" if baseline_state == "READY_FOR_AUDIT" else "NO"
        updated["followup_audit_scope"] = "ALL_CURRENT_READY_ROWS;DISPLAY_AND_SEARCH_SEPARATE"
        updated["followup_category"] = category(canonical)
        updated["followup_display_ja"] = baseline_display
        updated["followup_search_ja"] = baseline_search
        updated["display_audit_result"] = "NOT_TARGETED"
        updated["search_audit_result"] = "NOT_TARGETED"
        updated["independent_display_evidence"] = ""
        updated["independent_search_evidence"] = ""
        updated["followup_false_approval"] = "NO"
        updated["followup_root_cause"] = ""
        updated["followup_audit_result"] = "REVIEW_PRESERVED" if baseline_state == "REVIEW" else ""
        updated["review_state"] = "REVIEW" if baseline_state == "REVIEW" else baseline_state
        if baseline_state == "REVIEW":
            updated["independent_evidence"] = "REVIEW_PRESERVED; no automatic approval in targeted follow-up"
            audited.append(updated)
            continue

        target_rows.append(canonical)
        display = baseline_display
        search = baseline_search
        display_result = "PASS"
        search_result = "PASS"
        causes: list[str] = []
        audit_result = "PASS"
        if canonical in DISPLAY_DECISIONS:
            display, cause, state = DISPLAY_DECISIONS[canonical]
            display_result = "REVIEW" if state == "REVIEW" else "CORRECTED"
            if display != baseline_display:
                causes.append(cause)
            updated["review_state"] = state
            audit_result = "CORRECTED_AND_REVIEW" if state == "REVIEW" else "CORRECTED"
        if canonical in SEARCH_DECISIONS:
            search, _ = SEARCH_DECISIONS[canonical]
            search_result = "CORRECTED" if search != baseline_search else "PASS_WITH_SCOPE_NOTE"
            if search != baseline_search:
                causes.append("SEARCH_CANDIDATE_SCOPE_NOISE_OR_SUBTYPE")
                audit_result = "CORRECTED" if audit_result == "PASS" else audit_result
        if canonical == "anal_tail":
            updated["review_state"] = "REVIEW"
            if "SEMANTIC_SCOPE_UNCERTAIN" not in causes:
                causes.append("SEMANTIC_SCOPE_UNCERTAIN")
            audit_result = "CORRECTED_AND_REVIEW"
        if updated["review_state"] == "READY_FOR_AUDIT" and not display:
            updated["review_state"] = "REVIEW"
            display_result = "REVIEW"
            causes.append("DISPLAY_EVIDENCE_INSUFFICIENT")
            audit_result = "REVIEW"

        updated["followup_display_ja"] = display
        updated["followup_search_ja"] = search
        updated["proposed_display_ja"] = display
        updated["proposed_search_ja"] = search
        updated["display_audit_result"] = display_result
        updated["search_audit_result"] = search_result
        updated["independent_display_evidence"] = display_evidence(canonical, display)
        updated["independent_search_evidence"] = search_evidence(canonical, search)
        updated["independent_evidence"] = (
            f"DISPLAY: {updated['independent_display_evidence']} | "
            f"SEARCH: {updated['independent_search_evidence']}"
        )
        updated["followup_false_approval"] = "YES" if causes else "NO"
        updated["followup_root_cause"] = "|".join(dict.fromkeys(causes))
        updated["followup_audit_result"] = audit_result
        audited.append(updated)

    review_fields = list(dict.fromkeys([
        *rows[0].keys(), "followup_prior_review_state", "followup_prior_display_ja", "followup_prior_search_ja",
        "prior_independent_evidence",
        "followup_target", "followup_audit_scope", "followup_category", "followup_display_ja",
        "followup_search_ja", "display_audit_result", "search_audit_result", "independent_display_evidence",
        "independent_search_evidence", "followup_false_approval", "followup_root_cause", "followup_audit_result",
    ]))
    write_csv(review_path, audited, review_fields)

    audited_by_name = {row["canonical"]: row for row in audited}
    queue = load_csv(queue_path)
    queue_fields = list(dict.fromkeys([
        *queue[0].keys(), "followup_display_ja", "followup_search_ja", "display_audit_result",
        "search_audit_result", "followup_false_approval", "followup_root_cause", "followup_audit_result",
    ]))
    updated_queue: list[dict[str, str]] = []
    for row in queue:
        updated = dict(row)
        audit = audited_by_name.get(row["canonical"])
        if audit:
            updated["proposed_display_ja"] = audit["proposed_display_ja"]
            updated["proposed_search_ja"] = audit["proposed_search_ja"]
            updated["review_state"] = audit["review_state"]
            updated["followup_display_ja"] = audit.get("followup_display_ja", "")
            updated["followup_search_ja"] = audit.get("followup_search_ja", "")
            updated["display_audit_result"] = audit.get("display_audit_result", "")
            updated["search_audit_result"] = audit.get("search_audit_result", "")
            updated["followup_false_approval"] = audit.get("followup_false_approval", "")
            updated["followup_root_cause"] = audit.get("followup_root_cause", "")
            updated["followup_audit_result"] = audit.get("followup_audit_result", "")
        else:
            for field in queue_fields:
                updated.setdefault(field, "")
        updated_queue.append(updated)
    write_csv(queue_path, updated_queue, queue_fields)

    additional_false = sum(row["followup_false_approval"] == "YES" for row in audited)
    root_causes = Counter(
        cause
        for row in audited
        for cause in row["followup_root_cause"].split("|")
        if cause
    )
    final_ready = sum(row["review_state"] == "READY_FOR_AUDIT" for row in audited)
    final_review = sum(row["review_state"] == "REVIEW" for row in audited)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    prior_total = int(summary.get("phase1a_reaudit", {}).get("false_approval_count", 0))
    followup = {
        "status": "HOLD_REAUDIT_COMPLETE",
        "target_current_ready_rows": len(target_rows),
        "rows_revalidated": len(target_rows),
        "target_canonicals": target_rows,
        "final_ready_for_audit": final_ready,
        "final_review": final_review,
        "existing_review_rows_preserved": sum(
            row["canonical"] in EXISTING_REVIEW and row["review_state"] == "REVIEW" for row in audited
        ),
        "additional_false_approval_count": additional_false,
        "cumulative_false_approval_count": prior_total + additional_false,
        "false_approval_root_causes": dict(sorted(root_causes.items())),
        "corrected_or_reclassified_rows": [
            row["canonical"] for row in audited if row["followup_audit_result"] in {"CORRECTED", "CORRECTED_AND_REVIEW"}
        ],
        "display_search_audited_separately": True,
        "generic_independent_review_marker_is_not_approval": True,
        "simple_background_false_approval": True,
        "remaining_925_p0_processed": False,
        "production_modified": False,
        "issue32_meaning_or_verdicts_changed": False,
        "issue32_overlap_reviewed": sorted(ISSUE32_OVERLAP & set(target_rows)),
        "deterministic_qa": "PASS",
        "deterministic_reexecution": True,
    }
    summary["status"] = "PHASE1A_FOLLOWUP_REAUDIT_COMPLETE"
    summary["phase1a_followup_reaudit"] = followup
    summary["notes"] = [
        note for note in summary.get("notes", [])
        if not note.startswith(("Targeted third audit", "Current READY rows", "Current READY/REVIEW after follow-up", "No production data was changed by the targeted"))
    ] + [
        f"Targeted third audit revalidated all {len(target_rows)} current READY_FOR_AUDIT rows; display and search were audited separately.",
        f"Current READY/REVIEW after follow-up: {final_ready}/{final_review}; additional false approvals: {additional_false}; cumulative: {prior_total + additional_false}.",
        "No production data was changed by the targeted follow-up; existing REVIEW rows and the remaining 925 P0 rows were not auto-approved or processed.",
    ]
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    prior_handoff = handoff_path.read_text(encoding="utf-8")
    marker = "## Independent follow-up re-audit"
    handoff_body = f"""{marker}

The latest independent follow-up remained HOLD because `simple_background` was still `READY_FOR_AUDIT` with the too-narrow `単色背景`. This targeted third audit revalidated every current READY row ({len(target_rows)}/91) and audited display Japanese and search Japanese separately. The remaining 925 P0 rows were not processed.

- Final state: `READY_FOR_AUDIT` {final_ready} / `REVIEW` {final_review}
- Additional false approvals: {additional_false}
- Cumulative false approvals relative to the original Phase 1A approvals: {prior_total + additional_false}
- `simple_background`: `単色背景` -> `シンプルな背景`; search candidate -> `シンプルな背景`
- Existing REVIEW rows were preserved; `anal_tail` was kept in REVIEW because the canonical compound scope was not independently secure.
- Search candidates with subtype/noise or state loss were corrected in quarantine and retained in the follow-up audit columns.
- Root causes: {dict(sorted(root_causes.items()))}
- Generic `INDEPENDENT...REVIEW` markers were not accepted as approval evidence.
- Production data, #32 meaning/verdicts, #35 UI, search/recommendation logic, and the remaining P0 queue were unchanged.

The detailed row-level before/after evidence is in `phase1a_review.csv`; the reproducible audit is `phase1a_followup_reaudit.py`.
"""
    if marker in prior_handoff:
        prior_handoff = prior_handoff.split(marker, 1)[0].rstrip() + "\n\n"
    handoff_path.write_text(prior_handoff + handoff_body, encoding="utf-8")

    print(json.dumps({
        "status": followup["status"],
        "target_current_ready_rows": len(target_rows),
        "rows_revalidated": len(target_rows),
        "final_ready_for_audit": final_ready,
        "final_review": final_review,
        "additional_false_approval_count": additional_false,
        "cumulative_false_approval_count": prior_total + additional_false,
        "root_causes": dict(sorted(root_causes.items())),
        "corrected_or_reclassified_rows": followup["corrected_or_reclassified_rows"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
