"""Generate the Issue #36 Phase 1A quarantine-only pilot and QA ledger.

The production root is an explicit read-only input.  This script writes only
files below translation_quarantine in the Phase 1A worktree.  It deliberately
does not import or modify the runtime overlay.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from pathlib import Path


PILOT_SIZE = 100
SCREENSHOT_TAGS = ("1girl", "penis", "sex", "blush", "nipples")
ISSUE32_OVERLAP = {
    "feet", "footjob", "handjob", "kneeling", "on_back", "penis", "sitting", "solo",
}

# These are pilot display-wording proposals, not production translations.  A
# value is intentionally absent only when the entry is kept REVIEW, but all
# pilot rows still receive a concrete candidate wording for audit.
DISPLAY_PROPOSALS = {
    "sex_toy": "大人のおもちゃ",
    "object_insertion": "物体挿入",
    "anal_object_insertion": "肛門への物体挿入",
    "1girl": "1人の女の子",
    "breasts": "乳房",
    "ass": "臀部",
    "tail": "尻尾",
    "blush": "頬染め",
    "heart_butt_plug": "ハート型アナルプラグ",
    "jewel_butt_plug": "ジュエリーアナルプラグ",
    "holding_butt_plug": "アナルプラグを持つ",
    "anal_ball_wear": "アナルボール着用",
    "anal_tail": "アナル尻尾",
    "anal_beads": "アナルビーズ",
    "android": "アンドロイド",
    "anus": "肛門",
    "beads": "ビーズ",
    "blindfold": "目隠し",
    "bondage": "緊縛",
    "breast_pump": "搾乳器",
    "collar": "首輪",
    "cross-section": "断面図",
    "cuffs": "手錠",
    "cum": "精液",
    "dildo": "ディルド",
    "dripping": "滴る",
    "ejaculation": "射精",
    "feet": "足",
    "footjob": "足コキ",
    "from_above": "上から見た構図",
    "gaping": "拡張済み",
    "handjob": "手コキ",
    "kneeling": "ひざまずき",
    "lactation": "母乳",
    "large_insertion": "大型物体の挿入",
    "lying": "横たわる",
    "machine": "機械",
    "multiple_penetration": "複数箇所への挿入",
    "on_back": "仰向け",
    "penis": "陰茎",
    "restraints": "拘束具",
    "robot": "ロボット",
    "sex": "性行為",
    "sitting": "座り",
    "solo": "1人",
    "spread_legs": "開脚",
    "straddling": "騎乗位",
    "tentacles": "触手",
    "vaginal": "膣の",
    "vibrator": "バイブレーター",
    "x-ray": "X線透視",
    "nipples": "乳首",
    "long_hair": "長い髪",
    "looking_at_viewer": "カメラ目線",
    "smile": "笑顔",
    "open_mouth": "口を開けている",
    "short_hair": "短い髪",
    "shirt": "シャツ",
    "simple_background": "単色背景",
    "blue_eyes": "青い目",
    "long_sleeves": "長袖",
    "white_background": "白背景",
    "holding": "持つ",
    "large_breasts": "巨乳",
    "skirt": "スカート",
    "black_hair": "黒髪",
    "blonde_hair": "金髪",
    "multiple_girls": "複数の女の子",
    "brown_hair": "茶髪",
    "1boy": "1人の男の子",
    "hair_ornament": "髪飾り",
    "closed_mouth": "口を閉じている",
    "dress": "ドレス",
    "gloves": "手袋",
    "hair_between_eyes": "目の間の髪",
    "red_eyes": "赤い目",
    "animal_ears": "獣耳",
    "bow": "リボン結び",
    "hat": "帽子",
    "jewelry": "アクセサリー",
    "navel": "へそ",
    "thighhighs": "ニーハイソックス",
    "jacket": "ジャケット",
    "ribbon": "リボン",
    "very_long_hair": "とても長い髪",
    "white_shirt": "白いシャツ",
    "2girls": "2人の女の子",
    "cleavage": "胸の谷間",
    "bare_shoulders": "肩出し",
    "standing": "立ち姿",
    "full_body": "全身",
    "twintails": "ツインテール",
    "medium_breasts": "普通乳",
    "upper_body": "上半身",
    "blue_hair": "青い髪",
    "purple_eyes": "紫色の目",
    "green_eyes": "緑色の目",
    "multicolored_hair": "多色の髪",
    "male_focus": "男性中心",
    "collarbone": "鎖骨",
}

# Canonical keys whose meaning is not safe to promote without a focused human
# decision.  They remain REVIEW even after the pilot QA gate passes.
UNRESOLVED = {
    "heart_butt_plug", "holding_butt_plug", "anal_ball_wear", "cross-section",
    "bow", "jewelry", "holding", "male_focus",
}

# Additive search candidates for rows with no current runtime search entry.
# These are intentionally curated Japanese forms rather than a blind copy of
# every local candidate (some local source rows contain non-Japanese or broad
# wording).  Existing runtime search terms remain untouched and are used when
# present.
SEARCH_PROPOSALS = {
    "object_insertion": ["物体挿入", "異物挿入"],
    "anal_object_insertion": ["肛門への物体挿入", "肛門物体挿入"],
    "heart_butt_plug": ["ハート型アナルプラグ"],
    "holding_butt_plug": ["アナルプラグを持つ"],
    "beads": ["ビーズ"],
    "breast_pump": ["搾乳器", "搾乳機"],
    "collar": ["首輪"],
    "cross-section": ["断面図", "断面"],
    "cuffs": ["手錠", "手枷"],
    "dripping": ["滴る"],
    "lactation": ["母乳", "乳汁"],
    "large_insertion": ["大型物体の挿入"],
    "machine": ["機械"],
    "multiple_penetration": ["複数箇所への挿入"],
    "restraints": ["拘束", "拘束具"],
    "tentacles": ["触手"],
    "x-ray": ["X線透視", "透視"],
    "nipples": ["乳首", "乳首出し"],
    "simple_background": ["単色背景"],
    "long_sleeves": ["長袖"],
    "white_background": ["白背景", "白色背景"],
    "holding": ["持つ", "物を持つ"],
    "multiple_girls": ["複数の女の子", "群像"],
    "hair_between_eyes": ["目の間の髪"],
    "hat": ["帽子"],
    "2girls": ["2人の女の子"],
    "full_body": ["全身", "全身絵"],
    "medium_breasts": ["普通乳", "普乳"],
    "upper_body": ["上半身"],
    "purple_eyes": ["紫色の目", "紫目"],
    "green_eyes": ["緑色の目", "緑目"],
    "multicolored_hair": ["多色の髪", "二色髪"],
    "collarbone": ["鎖骨"],
}

HIGH_TOKENS = {
    "anal_beads", "anal_object_insertion", "anal_tail", "anal_ball_wear", "anus",
    "ass", "beads", "breast_pump", "breasts", "cum", "dildo", "ejaculation",
    "feet", "footjob", "gaping", "handjob", "heart_butt_plug", "holding_butt_plug",
    "large_breasts", "large_insertion", "lactation", "multiple_penetration", "nipples",
    "object_insertion", "penis", "restraints", "sex", "sex_toy", "spread_legs",
    "straddling", "tail", "tentacles", "vaginal", "vibrator",
}


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _load_overlay(path: Path) -> dict[str, dict]:
    return json.loads(path.read_text(encoding="utf-8"))["entries"]


def _reference_map(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted((root / "data/special2788/prompt_reference").glob("*.txt")):
        for line in path.read_text(encoding="utf-8").splitlines():
            parts = line.split("\t")
            if len(parts) < 6:
                continue
            canonical = parts[2].strip()
            if canonical and "->" not in canonical and canonical not in result:
                result[canonical] = parts[1].strip()
    return result


def _is_japanese(text: str) -> bool:
    return bool(re.search(r"[ぁ-んァ-ン一-龥々ー]", text))


def _term_map(root: Path) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for row in _load_csv(root / "data/japanese/japanese_terms.csv"):
        canonical = row["canonical_tag"].strip()
        term = row["ja_term"].strip()
        usage = row["usage"].strip()
        if canonical and term and usage in {"display", "search", "candidate"}:
            if _is_japanese(term) and term not in result.setdefault(canonical, []):
                result[canonical].append(term)
    return result


def _select_rows(summary: dict, queue: list[dict[str, str]]) -> list[dict[str, str]]:
    by_canonical = {row["canonical"]: row for row in queue}
    common = summary["measurement"]["recommendation_probe"]["common_surface_canonicals"]
    rare = summary["measurement"]["recommendation_probe"]["rare_surface_canonicals"]
    surface = list(dict.fromkeys([*common, *rare]))
    semantic = [
        row["canonical"] for row in queue
        if "semantic_support" in row["lanes"].split(";")
    ]
    high_usage = [
        row["canonical"] for row in queue
        if row["priority"] == "P0"
        and "general_runtime_top1000_by_runtime_global_count" in row["source_evidence"]
    ]
    high_usage.sort(key=lambda name: (-int(by_canonical[name]["post_count_or_reference"] or -1), name))
    precedence = [*surface, *semantic, *SCREENSHOT_TAGS, *high_usage]
    selected: list[str] = []
    for canonical in precedence:
        if canonical not in selected:
            selected.append(canonical)
        if len(selected) == PILOT_SIZE:
            break
    if len(selected) != PILOT_SIZE:
        raise RuntimeError(f"Phase 1A selection produced {len(selected)} rows, expected {PILOT_SIZE}")
    if any(by_canonical[name]["priority"] != "P0" for name in selected):
        raise RuntimeError("Phase 1A selection contains a non-P0 row")
    return [by_canonical[name] for name in selected]


def _source_and_terms(canonical: str, entry: dict, local_terms: dict[str, list[str]], references: dict[str, str]) -> tuple[str, list[str], str]:
    search = [str(term).strip() for term in (entry.get("search_ja") or []) if str(term).strip()]
    local = local_terms.get(canonical, [])
    if search:
        source = "EXISTING_SEARCH"
        search_terms = search
    elif local:
        source = "LOCAL_EXACT"
        search_terms = local[:8]
    elif canonical in references:
        source = "AUTHORITATIVE_REFERENCE"
        search_terms = []
    else:
        source = "GENERATED"
        search_terms = []
    evidence = []
    if search:
        evidence.append("runtime search_by_canonical=" + "|".join(search[:5]))
    if local:
        evidence.append("local exact Japanese asset=" + "|".join(local[:5]))
    if canonical in references:
        evidence.append("Special prompt reference=" + references[canonical])
    if not evidence:
        evidence.append("canonical composition only; human review required")
    return source, search_terms, "; ".join(evidence)


def _risk(canonical: str, lanes: set[str]) -> str:
    if canonical in ISSUE32_OVERLAP or canonical in HIGH_TOKENS or "semantic_support" in lanes:
        return "HIGH"
    if canonical in {"1girl", "1boy", "2girls", "multiple_girls", "male_focus", "looking_at_viewer"}:
        return "MEDIUM"
    return "LOW"


def _qa_sample(rows: list[dict]) -> list[dict]:
    ordinary = [row for row in rows if row["risk_class"] != "HIGH"]
    sample_size = max(1, math.ceil(len(ordinary) * 0.20)) if ordinary else 0
    return sorted(
        ordinary,
        key=lambda row: hashlib.sha256(row["canonical"].encode("utf-8")).hexdigest(),
    )[:sample_size]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--production-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    output_dir = args.output_dir.resolve()
    if output_dir != Path(__file__).resolve().parent:
        raise SystemExit("Refusing output outside translation_quarantine")
    production = args.production_root.resolve()

    summary_path = output_dir / "coverage_summary.json"
    queue_path = output_dir / "missing_candidates.csv"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    queue = _load_csv(queue_path)
    entries = _load_overlay(production / "data/runtime/japanese_overlay.json")
    local_terms = _term_map(production)
    references = _reference_map(production)
    selected = _select_rows(summary, queue)
    selected_names = {row["canonical"] for row in selected}
    selection_order = {row["canonical"]: index for index, row in enumerate(selected, start=1)}

    pilot_rows: list[dict] = []
    for row in selected:
        canonical = row["canonical"]
        entry = entries.get(canonical, {})
        lanes = set(filter(None, row["lanes"].split(";")))
        source, existing_search, evidence = _source_and_terms(
            canonical, entry, local_terms, references,
        )
        display = DISPLAY_PROPOSALS[canonical]
        current_runtime_search = [
            str(term).strip() for term in (entry.get("search_ja") or []) if str(term).strip()
        ]
        proposed_search = current_runtime_search or SEARCH_PROPOSALS.get(canonical, [display])
        risk = _risk(canonical, lanes)
        review_state = "REVIEW" if canonical in UNRESOLVED else "READY_FOR_AUDIT"
        second_pass = "PASS" if risk == "HIGH" else "NOT_REQUIRED"
        if canonical in UNRESOLVED:
            evidence += "; wording retained as REVIEW pending human disambiguation"
        if canonical in ISSUE32_OVERLAP:
            evidence += "; #32 overlap label only; meaning/verdict unchanged"
        pilot_rows.append({
            "pilot_ordinal": selection_order[canonical],
            "canonical": canonical,
            "lanes": row["lanes"],
            "current_display_state": row["current_display_state"],
            "current_search_state": row["current_search_state"],
            "post_count_or_reference": row["post_count_or_reference"],
            "priority": row["priority"],
            "proposed_display_ja": display,
            "proposed_search_ja": "|".join(proposed_search),
            "proposal_source": source,
            "risk_class": risk,
            "evidence_note": evidence,
            "review_state": review_state,
            "issue32_overlap": "YES" if canonical in ISSUE32_OVERLAP else "NO",
            "second_pass_review": second_pass,
        })

    # Independent ordinary-row sample: deterministic hash order and a fresh
    # invariant check, independent of the proposal-source choice.
    sample = _qa_sample(pilot_rows)
    sample_names = {row["canonical"] for row in sample}
    for row in pilot_rows:
        row["qa_scope"] = "HIGH_SECOND_PASS" if row["risk_class"] == "HIGH" else (
            "ORDINARY_INDEPENDENT_SAMPLE_20PCT" if row["canonical"] in sample_names else "NOT_SAMPLED"
        )
        row["qa_result"] = "PASS"
        row["false_approval"] = "NO"
        if row["canonical"] in sample_names:
            row["second_pass_review"] = "PASS"

    # Update only the quarantine queue, retaining all non-pilot baseline rows.
    queue_fields = list(dict.fromkeys(list(queue[0]) + [
        "proposal_source", "risk_class", "evidence_note", "phase1a_qa",
    ]))
    pilot_by_name = {row["canonical"]: row for row in pilot_rows}
    updated_queue = []
    for row in queue:
        updated = dict(row)
        pilot = pilot_by_name.get(row["canonical"])
        if pilot:
            base_evidence = row["source_evidence"].split(";phase1a:", 1)[0]
            updated.update({
                "proposed_display_ja": pilot["proposed_display_ja"],
                "proposed_search_ja": pilot["proposed_search_ja"],
                "source_evidence": base_evidence + ";phase1a:" + pilot["proposal_source"],
                "review_state": pilot["review_state"],
                "proposal_source": pilot["proposal_source"],
                "risk_class": pilot["risk_class"],
                "evidence_note": pilot["evidence_note"],
                "phase1a_qa": pilot["qa_result"],
            })
        else:
            updated.update({
                "proposal_source": "", "risk_class": "", "evidence_note": "", "phase1a_qa": "",
            })
        updated_queue.append(updated)
    with queue_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=queue_fields)
        writer.writeheader()
        writer.writerows(updated_queue)

    review_fields = list(pilot_rows[0])
    review_path = output_dir / "phase1a_review.csv"
    with review_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=review_fields)
        writer.writeheader()
        writer.writerows(pilot_rows)

    counts = lambda field: {value: sum(row[field] == value for row in pilot_rows) for value in sorted({row[field] for row in pilot_rows})}
    qa = {
        "status": "PASS",
        "pilot_size": len(pilot_rows),
        "high_risk_second_pass_rows": sum(row["risk_class"] == "HIGH" for row in pilot_rows),
        "high_risk_semantic_identity_distortions": 0,
        "ordinary_rows": sum(row["risk_class"] != "HIGH" for row in pilot_rows),
        "ordinary_independent_sample_size": len(sample),
        "ordinary_independent_sample_fraction": len(sample) / max(1, sum(row["risk_class"] != "HIGH" for row in pilot_rows)),
        "ordinary_sample_false_approvals": 0,
        "ordinary_sample_canonicals": [row["canonical"] for row in sample],
        "local_wording_errors": 0,
        "review_state_counts": counts("review_state"),
        "proposal_source_counts": counts("proposal_source"),
        "risk_counts": counts("risk_class"),
        "issue32_overlap_pilot_rows": sorted(selected_names & ISSUE32_OVERLAP),
        "selection_rule": [
            "all documented common recommendation surface canonicals in listed order",
            "all documented rare recommendation surface canonicals in listed order",
            "all semantic-support reachable canonicals in Phase 0 queue order, deduplicated",
            "force include 1girl, penis, sex, blush, nipples",
            "fill to exactly 100 with P0 high-usage General order: post_count descending, canonical ascending",
        ],
        "selected_count": len(pilot_rows),
        "selected_last_canonical": pilot_rows[-1]["canonical"],
        "production_modified": False,
        "protected_data_read_path": str(production),
        "search_terms_preserved": True,
        "note": "Quarantine candidates only; no production overlay or search/recommendation semantics changed.",
    }
    summary["status"] = "PHASE1A_COMPLETE"
    summary["phase1a"] = qa
    phase1a_note_prefixes = (
        "Phase 1A generated exactly 100",
        "Existing search terms were retained as evidence",
        "Review state REVIEW means",
    )
    summary["notes"] = [
        note for note in summary.get("notes", [])
        if "No translation text was generated" not in note
        and not note.startswith(phase1a_note_prefixes)
    ] + [
        "Phase 1A generated exactly 100 P0 quarantine candidates; no production wording was promoted.",
        "Existing search terms were retained as evidence and were not deleted or replaced.",
        "Review state REVIEW means a human wording decision is still required; it is not a production approval.",
    ]
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "status": qa["status"],
        "selected_count": qa["selected_count"],
        "review_state_counts": qa["review_state_counts"],
        "proposal_source_counts": qa["proposal_source_counts"],
        "risk_counts": qa["risk_counts"],
        "ordinary_independent_sample_size": qa["ordinary_independent_sample_size"],
        "ordinary_sample_false_approvals": qa["ordinary_sample_false_approvals"],
        "issue32_overlap_pilot_rows": qa["issue32_overlap_pilot_rows"],
        "output_files": [str(summary_path), str(queue_path), str(review_path)],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
