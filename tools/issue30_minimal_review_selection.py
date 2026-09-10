#!/usr/bin/env python3
"""Select the smallest informative human-review set from the Issue #30 pilot.

This reads the existing local pilot artifacts only.  It never generates images,
calls evaluators, or writes data/**.  Raw evaluator files are addressed by
image_id instead of trusting the per-row artifact pointer in the pilot JSON.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw


THRESHOLDS = {"wd14": 0.50, "kagami": 0.37, "cl_v2_00": 0.50}
EVALUATORS = ("wd14", "kagami", "cl_v2_00")

JA_GLOSS = {
    "anus": "肛門",
    "anus peek": "肛門ちら見せ",
    "spread anus": "開いた肛門",
    "exposed genitals": "露出した性器",
    "genital closeup": "性器のクローズアップ",
    "armpit sex": "脇を使った性行為",
    "grabbing another's ass": "他人の尻をつかむ",
    "anal object insertion": "肛門への物体挿入",
    "double handjob": "二人がかりの手による性行為",
    "cooperative fellatio": "協力して行うフェラチオ",
    "after footjob": "足を使った性行為の後の状態",
    "hug and suck": "抱擁と吸う行為の複合",
    "bound penis": "拘束された陰茎",
    "cuddling handjob": "寄り添いながらの手による性行為",
}


def norm(value: Any) -> str:
    value = str(value or "").strip().casefold().replace("_", " ")
    value = re.sub(r"[()\[\]{}]", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def canonical_parts(canonical: str) -> list[str]:
    return [x.strip() for x in re.split(r"\s*\+\s*|\s*,\s*", canonical) if x.strip()]


def normalized_pairs(value: Any) -> list[tuple[str, float]]:
    pairs: list[tuple[str, float]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(item, (float, int)) and 0 <= float(item) <= 1:
                pairs.append((str(key), float(item)))
            elif isinstance(item, (dict, list)):
                pairs.extend(normalized_pairs(item))
    elif isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                tag = item.get("tag") or item.get("label") or item.get("name")
                score = item.get("score") or item.get("confidence") or item.get("probability")
                if tag is not None and isinstance(score, (int, float)):
                    pairs.append((str(tag), float(score)))
                else:
                    pairs.extend(normalized_pairs(item))
            elif isinstance(item, (list, tuple)) and len(item) == 2:
                pairs.append((str(item[0]), float(item[1])))
    return sorted(pairs, key=lambda item: item[1], reverse=True)


def target_score(pairs: list[tuple[str, float]], canonical: str) -> tuple[float | None, bool, str]:
    targets = {norm(x) for x in canonical_parts(canonical)}
    direct = [(score, tag) for tag, score in pairs if norm(tag) in targets]
    if direct:
        score, _ = max(direct)
        return score, True, "DIRECT"
    components = []
    for tag, score in pairs:
        nt = norm(tag)
        if any(piece in nt or nt in piece for piece in targets for piece in piece.split() if len(piece) > 2):
            components.append(score)
    if components:
        return max(components), True, "COMPONENT_PROXY"
    return None, False, "NONE"


def read_gzip_json(path: Path) -> Any:
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def evaluator_from_raw(run_root: Path, image_id: str, canonical: str, name: str) -> dict[str, Any]:
    if name == "wd14":
        path = run_root / "raw" / "wd14" / f"{image_id}.json"
        obj = json.loads(path.read_text(encoding="utf-8"))
        version = "wd14-eva02.v3.large"
    elif name == "kagami":
        path = run_root / "raw" / "kagami" / f"{image_id}.json.gz"
        obj = read_gzip_json(path)
        version = "Kagami-24k"
    else:
        path = run_root / "raw" / "cl v2.00" / f"{image_id}.json.gz"
        obj = read_gzip_json(path)
        version = "CL v2.00"
    if "error" in obj:
        return {"name": name, "version": version, "state": "ERROR", "raw_score": None, "observed": None, "basis": "UNVERIFIED", "threshold": THRESHOLDS[name], "artifact": str(path)}
    pairs = normalized_pairs(obj.get("caption", obj) if name == "wd14" else obj.get("top_tags", []))
    score, observed, basis = target_score(pairs, canonical)
    return {"name": name, "version": version, "state": "OK", "raw_score": score, "observed": observed, "basis": basis, "threshold": THRESHOLDS[name], "artifact": str(path)}


def derive_row(run_root: Path, row: dict[str, Any]) -> dict[str, Any]:
    evaluators = {name: evaluator_from_raw(run_root, row["image_id"], row["canonical"], name) for name in EVALUATORS}
    votes = [evaluators[name]["observed"] for name in EVALUATORS]
    states = [evaluators[name]["state"] for name in EVALUATORS]
    relation = row["screening"]["desk_relation_sensitive"]
    classes: list[str] = []
    if relation:
        classes.append("RELATION_OR_BINDING")
    if row["screening"]["desk_classification"] == "BLOCKED" or any(state != "OK" for state in states):
        classes.append("BLOCKED")
    bases = [evaluators[name]["basis"] for name in EVALUATORS]
    if "COMPONENT_PROXY" in bases and not all(basis == "DIRECT" for basis in bases):
        classes.append("COMPONENT_ONLY")
    if len(set(v for v in votes if v is not None)) > 1:
        classes.append("DISAGREEMENT")
    low_flags = [
        evaluators[name]["raw_score"] is None or evaluators[name]["raw_score"] < evaluators[name]["threshold"]
        for name in EVALUATORS
    ]
    if any(low_flags):
        classes.append("LOW_CONFIDENCE")
    scores = [evaluators[name]["raw_score"] for name in EVALUATORS]
    if all(score is not None for score in scores):
        minimum = min(scores)
        band = "HIGH" if minimum >= 0.75 else ("MEDIUM" if minimum >= 0.50 else "LOW")
    else:
        band = "UNAVAILABLE"
    all_direct = all(evaluators[name]["basis"] == "DIRECT" and evaluators[name]["state"] == "OK" for name in EVALUATORS)
    unanimous_positive = votes == [True, True, True]
    high = all_direct and unanimous_positive and not relation and row["screening"]["desk_classification"] == "AUTO_CANDIDATE" and band == "HIGH"
    if high:
        classes.append("HIGH_CONFIDENCE_AUTO_LIKELY")
    if not classes:
        classes.append("LOW_CONFIDENCE")
    low_names = [name for name, low in zip(EVALUATORS, low_flags) if low]
    if len(set(votes)) == 2:
        if sum(v is True for v in votes) == 1:
            pattern = "ONE_POSITIVE_TWO_NEGATIVE"
        else:
            pattern = "TWO_POSITIVE_ONE_NEGATIVE"
    elif any(v is None for v in votes):
        pattern = "ABSTAINED"
    elif all(v is True for v in votes):
        pattern = "UNANIMOUS_POSITIVE"
    else:
        pattern = "UNANIMOUS_NEGATIVE"
    distances = [
        abs(evaluators[name]["raw_score"] - evaluators[name]["threshold"])
        for name in EVALUATORS
        if evaluators[name]["raw_score"] is not None
    ]
    distance = min(distances) if distances else None
    return {
        "image_id": row["image_id"],
        "case_id": row["case_id"],
        "canonical": row["canonical"],
        "canonical_ja": JA_GLOSS.get(row["canonical"], "日本語説明未登録"),
        "cell_type": row["cell_type"],
        "capability_class": row["human_review_selection"]["capability_class"],
        "desk_classification": row["screening"]["desk_classification"],
        "question": row["experiment_question"],
        "screening_classes": classes,
        "relation": relation,
        "agreement_pattern": pattern,
        "score_band": band,
        "minimum_threshold_distance": distance,
        "low_evaluators": low_names,
        "evaluators": evaluators,
        "originally_selected": row["human_review_selection"]["selected_for_human_review"],
        "original_pilot_classes": row["screening"]["screening_classes"],
        "image_path": row["image_artifact"]["path"],
        "sha256": row["image_artifact"]["sha256"],
    }


def select_minimal(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    selected: list[dict[str, Any]] = []
    reasons: dict[str, str] = {}

    def add(row: dict[str, Any], reason: str, impact: str) -> None:
        if row["image_id"] not in {r["image_id"] for r in selected} and len(selected) < 20:
            row = dict(row)
            row["selection_reason"] = reason
            row["decision_impact"] = impact
            selected.append(row)
            reasons[row["image_id"]] = reason

    # The current pilot's one HIGH record is outside the 58-row queue and is mandatory.
    high = [r for r in rows if "HIGH_CONFIDENCE_AUTO_LIKELY" in r["original_pilot_classes"]]
    for row in high[:1]:
        add(row, "唯一のHIGH_CONFIDENCE_AUTO_LIKELY。まずmachine-positiveの実画像妥当性を確認する", "AUTO viability")

    queue = [r for r in rows if r["originally_selected"]]
    nonrelation = [r for r in queue if not r["relation"]]

    # AUTO-nearest: direct, unanimous, non-relation, then strongest minimum score.
    auto_candidates = [r for r in nonrelation if r["desk_classification"] == "AUTO_CANDIDATE"]
    auto_candidates.sort(key=lambda r: (all(e["basis"] == "DIRECT" for e in r["evaluators"].values()), r["agreement_pattern"] == "UNANIMOUS_POSITIVE", r["score_band"] == "HIGH", -min(e["raw_score"] or 0 for e in r["evaluators"].values())), reverse=True)
    for row in auto_candidates:
        add(row, "AUTO候補に最も近い非relation例。direct/unanimous/score帯を代表", "AUTO viability")
        if sum("AUTO viability" == r["decision_impact"] for r in selected) >= 4:
            break

    # One row for each observed disagreement pattern, avoiding same-case duplicates.
    used_patterns: set[str] = set()
    for row in sorted(nonrelation, key=lambda r: (r["agreement_pattern"] in used_patterns, r["minimum_threshold_distance"] if r["minimum_threshold_distance"] is not None else 999.0)):
        pattern = row["agreement_pattern"]
        if "DISAGREEMENT" in row["screening_classes"] and pattern not in used_patterns:
            add(row, f"evaluator disagreement代表: {pattern} / low={','.join(row['low_evaluators']) or 'none'}", "disagreement behavior")
            used_patterns.add(pattern)
        if len(used_patterns) >= 3:
            break

    # Threshold boundary: closest to any declared threshold, with one positive and one negative/abstain when possible.
    boundary = sorted([r for r in nonrelation if "LOW_CONFIDENCE" in r["screening_classes"]], key=lambda r: r["minimum_threshold_distance"] if r["minimum_threshold_distance"] is not None else 999.0)
    for row in boundary:
        add(row, "threshold直上/直下に近い境界例。固定thresholdの感度を確認", "threshold boundary")
        if sum("threshold boundary" == r["decision_impact"] for r in selected) >= 2:
            break

    # Two blocked/rare-tail controls; do not spend the whole blocked pool.
    blocked = [r for r in queue if "BLOCKED" in r["screening_classes"]]
    blocked.sort(key=lambda r: (r["capability_class"] != "rare_or_no_vocab", r["agreement_pattern"] != "UNANIMOUS_NEGATIVE"))
    for row in blocked[:2]:
        add(row, "BLOCKED/rare-tailの失敗対照。人間reviewが必要な境界を確認", "blocked confirmation")

    # One non-relation component proxy control if available.
    component = [r for r in nonrelation if "COMPONENT_ONLY" in r["screening_classes"]]
    if component:
        add(component[0], "非relationのcomponent-only proxy。component検出だけで成立と誤るか確認", "component-proxy safety")

    # Relation/binding: one high-information anchor per distinct safety dimension.
    relation_priority = [
        "relation", "actor_subject_object", "bodypart", "count_or_multi", "spatial", "compound", "restraint_bodypart_binding", "components_only"
    ]
    for capability in relation_priority:
        candidates = [r for r in queue if r["relation"] and r["capability_class"] == capability]
        if candidates:
            row = sorted(candidates, key=lambda r: ("COMPONENT_ONLY" not in r["screening_classes"], r["score_band"] == "HIGH"), reverse=True)[0]
            add(row, f"relation/binding保護アンカー: {capability}。Tagger通過が関係性正解を意味しないことを確認", "relation safety")

    # A final compound/insertion representative if the first relation selection did not cover it.
    if not any(r["capability_class"] == "compound" for r in selected):
        candidates = [r for r in queue if r["relation"] and r["capability_class"] == "compound"]
        if candidates:
            add(candidates[0], "compound retention / insertion-contactのrelation安全性代表", "relation safety")

    return selected[:20], reasons


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def create_blinded_contact_sheet(run_root: Path, selected: list[dict[str, Any]]) -> Path:
    """Create an ordered, score-free sheet for the user's visual review."""
    thumb_w, thumb_h, label_h = 320, 320, 44
    cols = 4
    rows = (len(selected) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), "white")
    draw = ImageDraw.Draw(sheet)
    for index, row in enumerate(selected):
        with Image.open(row["image_path"]) as image:
            image = image.convert("RGB")
            image.thumbnail((thumb_w - 8, thumb_h - 8), Image.Resampling.LANCZOS)
            x = (index % cols) * thumb_w + (thumb_w - image.width) // 2
            y = (index // cols) * (thumb_h + label_h) + (thumb_h - image.height) // 2
            sheet.paste(image, (x, y))
        label = f"{row['review_order']:02d}  [{row['target_or_contrast']}] {row['canonical_ja']}"
        draw.text(((index % cols) * thumb_w + 4, (index // cols) * (thumb_h + label_h) + thumb_h + 4), label, fill="black")
    output = run_root / "review_queue" / "minimal_review_contact_sheet.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, format="PNG")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", required=True, type=Path)
    parser.add_argument("--repo-root", default=Path(__file__).resolve().parents[1], type=Path)
    args = parser.parse_args()
    run_root = args.run_root
    source = json.loads((run_root / "calibration_results.json").read_text(encoding="utf-8"))
    rows = [derive_row(run_root, row) for row in source]
    selected, _ = select_minimal(rows)
    for index, row in enumerate(selected, start=1):
        row["review_order"] = index
        row["target_or_contrast"] = "target" if row["cell_type"].startswith("target_present") else "contrast"
        row["wd14_score"] = row["evaluators"]["wd14"]["raw_score"]
        row["wd14_vote"] = row["evaluators"]["wd14"]["observed"]
        row["kagami_score"] = row["evaluators"]["kagami"]["raw_score"]
        row["kagami_vote"] = row["evaluators"]["kagami"]["observed"]
        row["cl_score"] = row["evaluators"]["cl_v2_00"]["raw_score"]
        row["cl_vote"] = row["evaluators"]["cl_v2_00"]["observed"]
        row["what_human_decides"] = row["question"]
    contact_sheet = create_blinded_contact_sheet(run_root, selected)
    minimal_fields = [
        "review_order", "image_id", "case_id", "canonical", "target_or_contrast", "cell_type", "capability_class",
        "canonical_ja",
        "screening_classes", "agreement_pattern", "score_band", "wd14_score", "wd14_vote", "kagami_score", "kagami_vote",
        "cl_score", "cl_vote", "selection_reason", "what_human_decides", "decision_impact", "image_path", "sha256"
    ]
    minimal_rows = []
    for row in selected:
        out = dict(row)
        out["screening_classes"] = ";".join(row["screening_classes"])
        minimal_rows.append(out)
    out_root = args.repo_root / "docs" / "testing"
    write_csv(out_root / "ISSUE30_MINIMAL_REVIEW_MANIFEST_20260910.csv", minimal_rows, minimal_fields)

    selected_ids = {row["image_id"] for row in selected}
    mapping_rows = []
    queue_rows = [r for r in rows if r["originally_selected"]]
    for row in queue_rows:
        chosen = next((x for x in selected if x["image_id"] == row["image_id"]), None)
        mapping_rows.append({
            "image_id": row["image_id"], "case_id": row["case_id"], "canonical": row["canonical"], "canonical_ja": row["canonical_ja"], "cell_type": row["cell_type"],
            "capability_class": row["capability_class"], "pilot_screening_classes": ";".join(row["original_pilot_classes"]),
            "raw_audit_screening_classes": ";".join(row["screening_classes"]), "selected_minimal": row["image_id"] in selected_ids,
            "review_order": chosen["review_order"] if chosen else "", "defer_reason": chosen["selection_reason"] if chosen else "redundant within covered pattern or outside current decision need"
        })
    write_csv(out_root / "ISSUE30_REVIEW_QUEUE_MAPPING_20260910.csv", mapping_rows, ["image_id", "case_id", "canonical", "canonical_ja", "cell_type", "capability_class", "pilot_screening_classes", "raw_audit_screening_classes", "selected_minimal", "review_order", "defer_reason"])

    label_schema = {
        "schema_version": "issue30.minimal_review_input.v1",
        "per_image": {
            "review_order": "integer",
            "image_id": "string",
            "human_target_concept_present": "yes|no|unclear",
            "human_actor_subject_correct": "yes|no|unclear|not_applicable",
            "human_target_object_correct": "yes|no|unclear|not_applicable",
            "human_body_part_ownership_site_correct": "yes|no|unclear|not_applicable",
            "human_count_correct": "yes|no|unclear|not_applicable",
            "human_spatial_relation_correct": "yes|no|unclear|not_applicable",
            "human_compound_all_elements_retained": "yes|no|unclear|not_applicable",
            "human_unwanted_extra_interpretation": "yes|no|unclear",
            "usable_for_stage10_preference_judgment": "yes|no|unclear",
            "human_final_route": "AUTO_SUPPORT|HUMAN_REVIEW_ONLY|BLOCKED|UNRESOLVED",
            "reviewer_note": "string"
        },
        "rules": [
            "Do not reveal evaluator votes, scores, screening class, or route while making the human judgment.",
            "Use UNRESOLVED for unclear or unresolved judgments; exclude it from threshold fitting and AUTO promotion.",
            "A relation/binding failure is HUMAN_REVIEW_ONLY even when all evaluators vote positive."
        ]
    }
    (out_root / "ISSUE30_MINIMAL_REVIEW_INPUT_SCHEMA_20260910.json").write_text(json.dumps(label_schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary = {
        "source_run": str(run_root), "pilot_images": len(rows), "current_review_queue": len(queue_rows), "minimal_review_count": len(selected),
        "selected_from_current_queue": sum(row["originally_selected"] for row in selected), "high_candidate_outside_queue": sum(not row["originally_selected"] for row in selected),
        "selected_by_impact": dict(Counter(row["decision_impact"] for row in selected)),
        "excluded_current_queue": len(queue_rows) - sum(row["originally_selected"] for row in selected),
        "raw_pointer_mismatch_count": sum(any(str(row["evaluators"][name]["artifact"]) != str(next(x for x in source if x["image_id"] == row["image_id"])["evaluators"][name]["raw_output_artifact"]) for name in EVALUATORS) for row in rows),
        "raw_audit_note": "The pilot result artifact pointers are inconsistent for 127/128 rows; this selection re-addresses existing raw files by image_id and does not rerun evaluators.",
        "ordered_contact_sheet": str(contact_sheet),
        "early_stop": {
            "stop_auto_validation_if": [
                "the mandatory HIGH candidate is a clear human false positive",
                "two false positives occur among review orders 1-4",
                "a non-relation simple class has two clear human-negative examples despite unanimous positive machine votes"
            ],
            "on_stop": "mark AUTO_CALIBRATION_HOLD; do not review deferred redundant cases; keep relation/binding HUMAN_REVIEW_ONLY"
        },
        "no_generation_or_evaluator_calls": True,
        "production_auto_promotion": False
    }
    (out_root / "ISSUE30_MINIMAL_REVIEW_SELECTION_SUMMARY_20260910.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("selected:", ", ".join(f"{r['review_order']}:{r['image_id']}" for r in selected))


if __name__ == "__main__":
    main()
