#!/usr/bin/env python3
import argparse
import csv
from collections import Counter
from pathlib import Path

EXPECTED_TOTAL = 195
EXPECTED_REVIEW = 58
VALID_KINDS = {
    "ACTION_CONTACT", "CLOTHING_EXPOSURE", "TOOL_OBJECT", "BODY_STATE",
    "FLUID_EXCRETION", "POSE_SCENE", "PERSON_RELATION",
    "NONHUMAN_TRANSFORMATION", "META_EXPRESSION",
}

# tag -> (kind, optional replacement body facets, extra themes)
# None body means preserve prescreen body facets; [] deliberately clears them.
RESOLUTIONS = {
    "clothes_lift": ("CLOTHING_EXPOSURE", None, []),
    "skindentation": ("BODY_STATE", None, []),
    "thick_thighs": ("BODY_STATE", None, []),
    "clothes_pull": ("CLOTHING_EXPOSURE", None, []),
    "thigh_gap": ("BODY_STATE", None, []),
    "lifting_own_clothes": ("CLOTHING_EXPOSURE", None, []),
    "breast_press": ("ACTION_CONTACT", None, []),
    "breasts_squeezed_together": ("BODY_STATE", None, []),
    "huge_ass": ("BODY_STATE", None, []),
    "pov_crotch": ("POSE_SCENE", None, []),
    "blood_on_hand": ("FLUID_EXCRETION", None, ["INJURY_R18G"]),
    "gigantic_breasts": ("BODY_STATE", None, []),
    "breast_rest": ("ACTION_CONTACT", None, []),
    "hand_on_own_ass": ("ACTION_CONTACT", None, []),
    "grabbing_own_ass": ("ACTION_CONTACT", None, []),
    "grabbing_another's_thighs": ("ACTION_CONTACT", None, []),
    "hand_under_clothes": ("ACTION_CONTACT", None, []),
    "cloth_gag": ("TOOL_OBJECT", None, []),
    "presenting_own_ass": ("POSE_SCENE", None, []),
    "hands_on_own_ass": ("ACTION_CONTACT", None, []),
    "presenting_own_breasts": ("POSE_SCENE", None, []),
    "holding_own_legs_back": ("POSE_SCENE", None, []),
    "hand_on_own_crotch": ("ACTION_CONTACT", None, []),
    "bite_mark_on_breast": ("BODY_STATE", None, []),
    "ass_press": ("ACTION_CONTACT", None, []),
    "licking_breast": ("ACTION_CONTACT", None, []),
    "holding_pregnancy_test": ("ACTION_CONTACT", None, ["REPRO_PREGNANCY_LACTATION"]),
    "spreading_own_ass": ("ACTION_CONTACT", None, []),
    "sucking_own_breasts": ("ACTION_CONTACT", None, []),
    "gag_around_neck": ("TOOL_OBJECT", [], []),
    "stuffed_gag": ("TOOL_OBJECT", None, []),
    "grabbing_multiple_others'_breasts": ("ACTION_CONTACT", None, []),
    "cooperative_breast_sucking": ("ACTION_CONTACT", None, []),
    "explosion_gag": ("META_EXPRESSION", [], []),
    "bite_mark_on_ass": ("BODY_STATE", None, []),
    "applying_gag": ("ACTION_CONTACT", None, []),
    "public_urination": ("FLUID_EXCRETION", None, []),
    "hands_on_own_crotch": ("ACTION_CONTACT", None, []),
    "biting_breast": ("ACTION_CONTACT", None, []),
    "imminent_breast_grab": ("ACTION_CONTACT", None, []),
    "licking_leg": ("ACTION_CONTACT", None, []),
    "holding_gag": ("ACTION_CONTACT", [], []),
    "leash_in_mouth": ("TOOL_OBJECT", None, ["BDSM_RESTRAINT"]),
    "wraparound_tape_gag": ("TOOL_OBJECT", None, []),
    "poking_own_breast": ("ACTION_CONTACT", None, []),
    "licking_thigh": ("ACTION_CONTACT", None, []),
    "licking_ass": ("ACTION_CONTACT", None, []),
    "gag_chinstrap": ("TOOL_OBJECT", None, []),
    "sucking_on_multiple_breasts": ("ACTION_CONTACT", None, []),
    "mutual_breast_sucking": ("ACTION_CONTACT", None, []),
    "ovulation": ("BODY_STATE", None, []),
    "leash_between_breasts": ("TOOL_OBJECT", None, []),
    "biting_ass": ("ACTION_CONTACT", None, []),
    "holding_own_leg_back": ("POSE_SCENE", None, []),
    "holding_another's_legs_back": ("POSE_SCENE", None, []),
    "touching_another's_crotch": ("ACTION_CONTACT", None, []),
    "hand_grabbing_both_breasts": ("ACTION_CONTACT", None, []),
    "muzzle_gag": ("TOOL_OBJECT", None, []),
}


def split(value: str) -> list[str]:
    return [x for x in value.split("|") if x]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--review", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--summary", required=True)
    a = p.parse_args()

    with Path(a.input).open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    with Path(a.review).open("r", encoding="utf-8-sig", newline="") as f:
        review = list(csv.DictReader(f))
    if len(rows) != EXPECTED_TOTAL or len(review) != EXPECTED_REVIEW:
        raise SystemExit(f"input drift total={len(rows)} review={len(review)}")

    review_tags = {r["canonical_tag"] for r in review}
    if review_tags != set(RESOLUTIONS):
        missing = sorted(review_tags - set(RESOLUTIONS))
        extra = sorted(set(RESOLUTIONS) - review_tags)
        raise SystemExit(f"resolution coverage mismatch missing={missing} extra={extra}")

    human_resolved = 0
    for row in rows:
        tag = row["canonical_tag"]
        if tag not in RESOLUTIONS:
            if row["browse_status"] != "AUTO_CANDIDATE" or not row["kind_id"]:
                raise SystemExit(f"non-review row not mechanically resolved: {tag}")
            row["browse_status"] = "AUTO_CANDIDATE"
            row["validation_status"] = "TAXONOMY_RESOLVED"
            if tag == "breast_suppress":
                # Danbooru usage is a hands-on-breast action/contact concept, not an exposure state.
                row["kind_id"] = "ACTION_CONTACT"
                row["notes"] = "Issue96 semantic correction: breast_suppress is an action/contact concept, not clothing/exposure"
            continue

        kind, body_override, extra_themes = RESOLUTIONS[tag]
        if kind not in VALID_KINDS:
            raise SystemExit(f"invalid resolved kind at {tag}: {kind}")
        row["kind_id"] = kind
        if body_override is not None:
            row["body_site_ids"] = "|".join(body_override)
        themes = set(split(row["theme_ids"]))
        if tag == "explosion_gag":
            # Danbooru `gag` here means a visual/comedic explosion gag, not a mouth gag.
            themes.clear()
        themes.update(extra_themes)
        row["theme_ids"] = "|".join(sorted(themes))
        row["browse_status"] = "HUMAN_RESOLVED"
        row["validation_status"] = "TAXONOMY_RESOLVED"
        if tag == "explosion_gag":
            row["notes"] = "Issue96 semantic correction: visual/comedic explosion gag; META_EXPRESSION, no MOUTH_ORAL or BDSM facet"
        else:
            row["notes"] = "Issue96 bounded human taxonomy resolution; semantic home chosen independently from body/theme facets"
        human_resolved += 1

    if human_resolved != EXPECTED_REVIEW:
        raise SystemExit(f"human resolution count drift: {human_resolved}")
    if any(not r["kind_id"] or r["browse_status"] == "REVIEW_REQUIRED" for r in rows):
        raise SystemExit("taxonomy remains unresolved")

    out = Path(a.output); out.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0])
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader(); w.writerows(rows)

    kind_counts = Counter(r["kind_id"] for r in rows)
    body_counts = Counter(x for r in rows for x in split(r["body_site_ids"]))
    theme_counts = Counter(x for r in rows for x in split(r["theme_ids"]))
    auto = sum(r["browse_status"] == "AUTO_CANDIDATE" for r in rows)

    lines = [
        "# Issue #96 taxonomy final summary v1", "",
        "Status: **195/195 TAXONOMY RESOLVED / JA + DUPLICATE VALIDATION PENDING / NO PRODUCTION MUTATION**", "",
        f"- total: **{len(rows)}**",
        f"- conservative auto-resolved: **{auto}**",
        f"- bounded human-resolved: **{human_resolved}**",
        "- unresolved: **0**", "",
        "## Kind counts", "",
    ]
    lines += [f"- `{k}`: **{v}**" for k, v in sorted(kind_counts.items())]
    lines += ["", "## Body-site facet counts", ""]
    lines += [f"- `{k}`: **{v}**" for k, v in sorted(body_counts.items())]
    lines += ["", "## Theme counts", ""]
    lines += [f"- `{k}`: **{v}**" for k, v in sorted(theme_counts.items())]
    lines += [
        "", "## Resolution notes", "",
        "The 58 mixed/boundary rows were reviewed as a bounded set. Semantic home is independent from body-site/theme facets: gag objects stay TOOL_OBJECT, applying_gag stays ACTION_CONTACT, presenting/legs-back relations use POSE_SCENE, and morphology/mark states use BODY_STATE.",
        "`gag_around_neck` and `holding_gag` explicitly clear the lexical MOUTH_ORAL prescreen hint because the gag is not located in the mouth in those identities.",
        "`explosion_gag` is explicitly corrected to META_EXPRESSION with no MOUTH_ORAL/BDSM facet: Danbooru `gag` here means a visual/comedic explosion gag, not a restraint device.",
        "`breast_suppress` is explicitly corrected to ACTION_CONTACT: its Danbooru concept is a hands-on-breast suppressing action, not a clothing/exposure state.",
        "`blood_on_hand`, `holding_pregnancy_test`, and `leash_in_mouth` receive their relevant cross-cutting theme even though their #94 concept-area family did not mechanically supply it.",
        "", "`CONTENT_FILTER_USED=NO`  ", "`PRODUCTION_FILES_CHANGED=NO`  ", "`ISSUE70_MUTATED=NO`", "",
    ]
    Path(a.summary).write_text("\n".join(lines), encoding="utf-8")
    print(f"ISSUE96_TAXONOMY_FINAL_PASS total={len(rows)} auto={auto} human={human_resolved} unresolved=0")


if __name__ == "__main__":
    main()
