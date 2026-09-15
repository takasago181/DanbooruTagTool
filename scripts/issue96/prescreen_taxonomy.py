#!/usr/bin/env python3
import argparse
import csv
from collections import Counter
from pathlib import Path

EXPECTED_ROWS = 195
VALID_KINDS = {
    "ACTION_CONTACT", "CLOTHING_EXPOSURE", "TOOL_OBJECT", "BODY_STATE",
    "FLUID_EXCRETION", "POSE_SCENE", "PERSON_RELATION",
    "NONHUMAN_TRANSFORMATION", "META_EXPRESSION",
}
VALID_BODY = {"MALE_GENITAL", "BREAST_NIPPLE", "FEMALE_GENITAL", "MOUTH_ORAL", "BUTTOCK_ANAL", "URETHRA"}
VALID_THEMES = {"BDSM_RESTRAINT", "INJURY_R18G", "REPRO_PREGNANCY_LACTATION"}

DIRECT_KIND = {
    "SPECIAL_EXPOSURE_CLOTHING_STATE": "CLOTHING_EXPOSURE",
    "SPECIAL_CLOTHING_BODY_RELATION": "CLOTHING_EXPOSURE",
    "SPECIAL_GARMENT_SUBTYPE": "CLOTHING_EXPOSURE",
    "SPECIAL_R18G_BODY_STATE": "FLUID_EXCRETION",
    "SPECIAL_INTIMATE_ADORNMENT_STATE": "BODY_STATE",
    "SPECIAL_SEX_DEVICE": "TOOL_OBJECT",
    "SPECIAL_NAMED_POSE": "POSE_SCENE",
    "SPECIAL_SEXUAL_RELATION": "ACTION_CONTACT",
}

BODY_WORDS = {
    "BREAST_NIPPLE": {"breast", "breasts", "nipple", "nipples", "areola", "areolae"},
    "FEMALE_GENITAL": {"clit", "clitoris", "clitoral", "vagina", "vaginal", "vulva", "vulval", "labia", "labial", "pussy", "cervix", "cervical"},
    "MALE_GENITAL": {"penis", "penile", "cock", "glans", "testicle", "testicles", "testicular", "scrotum", "scrotal"},
    "BUTTOCK_ANAL": {"anus", "anal", "ass", "butt", "butts", "buttock", "buttocks", "rectum", "rectal"},
    "MOUTH_ORAL": {"mouth", "oral", "tongue", "lip", "lips", "teeth", "tooth", "gag"},
    "URETHRA": {"urethra", "urethral"},
}


def body_facets(tag: str) -> list[str]:
    words = set(tag.lower().replace("-", "_").split("_"))
    found = []
    for facet, keys in BODY_WORDS.items():
        if words & keys:
            found.append(facet)
    return sorted(found)


def classify_kind(tag: str, area: str) -> tuple[str, str, str]:
    if area in DIRECT_KIND:
        return DIRECT_KIND[area], "AUTO_CANDIDATE", f"direct concept-area mapping: {area}"
    if area == "SPECIAL_REPRODUCTION_FLUID":
        t = tag.lower()
        if any(x in t for x in ("lactat", "breast_milk", "milk_")):
            return "FLUID_EXCRETION", "AUTO_CANDIDATE", "reproduction family with lactation/fluid surface"
        if any(x in t for x in ("pregnan", "pregnancy", "gravid", "birth")):
            return "BODY_STATE", "AUTO_CANDIDATE", "reproduction family with pregnancy/body-state surface"
        return "", "REVIEW_REQUIRED", "reproduction family kind is not mechanically unambiguous"
    if area == "SPECIAL_BDSM_RESTRAINT":
        return "", "REVIEW_REQUIRED", "BDSM is a theme, not a forced semantic home; inspect whether action/tool/pose/relation"
    if area == "SPECIAL_BODY_RELATION_STATE":
        return "", "REVIEW_REQUIRED", "body-relation family spans action/contact, pose and body-state homes"
    if area in {"GENERAL_OTHER", "BOUNDARY_CONCEPT", "GENERAL_OBJECT_OR_ACTION_PLACEMENT"}:
        return "", "REVIEW_REQUIRED", "human-override/boundary family requires explicit semantic-home review"
    return "", "REVIEW_REQUIRED", f"no approved conservative mapping rule for concept area {area}"


def themes(area: str) -> list[str]:
    if area == "SPECIAL_R18G_BODY_STATE":
        return ["INJURY_R18G"]
    if area == "SPECIAL_REPRODUCTION_FLUID":
        return ["REPRO_PREGNANCY_LACTATION"]
    if area == "SPECIAL_BDSM_RESTRAINT":
        return ["BDSM_RESTRAINT"]
    return []


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--review", required=True)
    p.add_argument("--summary", required=True)
    a = p.parse_args()

    with Path(a.input).open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != EXPECTED_ROWS:
        raise SystemExit(f"row drift: {len(rows)} != {EXPECTED_ROWS}")

    mapped = []
    review = []
    for row in rows:
        kind, status, why = classify_kind(row["canonical_tag"], row["concept_area"])
        body = body_facets(row["canonical_tag"])
        theme = themes(row["concept_area"])
        if kind and kind not in VALID_KINDS:
            raise SystemExit(f"invalid kind: {kind}")
        if not set(body) <= VALID_BODY or not set(theme) <= VALID_THEMES:
            raise SystemExit(f"invalid facet at {row['canonical_tag']}")
        next_row = dict(row)
        next_row["kind_id"] = kind
        next_row["body_site_ids"] = "|".join(body)
        next_row["theme_ids"] = "|".join(theme)
        next_row["browse_status"] = status
        next_row["validation_status"] = "TAXONOMY_PRESCREEN_READY" if status == "AUTO_CANDIDATE" else "TAXONOMY_REVIEW_REQUIRED"
        next_row["notes"] = why
        mapped.append(next_row)
        if status == "REVIEW_REQUIRED":
            review.append(next_row)

    out = Path(a.output); out.parent.mkdir(parents=True, exist_ok=True)
    fields = list(mapped[0])
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader(); w.writerows(mapped)
    with Path(a.review).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader(); w.writerows(review)

    kinds = Counter(r["kind_id"] or "REVIEW_REQUIRED" for r in mapped)
    bodies = Counter(x for r in mapped for x in r["body_site_ids"].split("|") if x)
    theme_counts = Counter(x for r in mapped for x in r["theme_ids"].split("|") if x)
    auto = EXPECTED_ROWS - len(review)

    lines = [
        "# Issue #96 taxonomy prescreen summary v1", "",
        "Status: **CONSERVATIVE PRESCREEN / HUMAN REVIEW QUEUE PRESERVED / NO PRODUCTION MUTATION**", "",
        f"- total: **{EXPECTED_ROWS}**",
        f"- mechanically clear taxonomy candidates: **{auto}**",
        f"- explicit taxonomy review queue: **{len(review)}**", "",
        "## Kind counts", "",
    ]
    lines += [f"- `{k}`: **{v}**" for k, v in sorted(kinds.items())]
    lines += ["", "## Body-site facet counts", ""]
    lines += [f"- `{k}`: **{v}**" for k, v in sorted(bodies.items())]
    lines += ["", "## Theme counts", ""]
    lines += [f"- `{k}`: **{v}**" for k, v in sorted(theme_counts.items())]
    lines += [
        "", "## Rule", "",
        "Only concept families with an unambiguous mapping to the already accepted Issue #76 9-kind model are auto-proposed. Mixed relation/BDSM/boundary families remain in the review queue rather than being force-fit.",
        "Body-site facets are lexical prescreen hints and remain reviewable metadata; they do not change canonical identity.",
        "", "`CONTENT_FILTER_USED=NO`  ", "`PRODUCTION_FILES_CHANGED=NO`  ", "`ISSUE70_MUTATED=NO`", "",
    ]
    Path(a.summary).write_text("\n".join(lines), encoding="utf-8")
    print(f"ISSUE96_TAXONOMY_PRESCREEN_PASS total={EXPECTED_ROWS} auto={auto} review={len(review)}")


if __name__ == "__main__":
    main()
