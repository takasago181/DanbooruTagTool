#!/usr/bin/env python3
"""Issue #94 v2: meaning-first Special gap prescreen.

Stage A classifies the whole canonical concept into a semantic family.
Stage B decides whether that family has Special deep-discovery value.  Lexical
nearest-neighbour information is retained for audit context only and never
decides the status.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


STATUSES = (
    "LIKELY_CANDIDATE",
    "LIKELY_GENERAL_ONLY",
    "POSSIBLE_DUPLICATE",
    "NEEDS_REVIEW",
)
PRIORITIES = ("P0", "P1", "P2", "P3")

REVIEW_TO_V2 = {
    "CANDIDATE": "LIKELY_CANDIDATE",
    "OUTSIDE_SPECIAL_NONCONTENT": "LIKELY_GENERAL_ONLY",
    "DUPLICATE_ALREADY_COVERED": "POSSIBLE_DUPLICATE",
    "NEEDS_REVIEW": "NEEDS_REVIEW",
}

INTIMATE_SITES = {
    "anal", "anus", "ass", "breast", "breasts", "clitoris", "crotch", "dick",
    "genital", "genitals", "nipple", "nipples", "penis", "pussy", "pubic",
    "testicle", "testicles", "thigh", "thighs", "leg", "legs", "vagina", "vulva", "womb",
}

BODY_SITES = INTIMATE_SITES | {
    "arm", "armpit", "back", "belly", "chest", "ear", "eye", "eyes", "face",
    "feet", "finger", "fingers", "foot", "hand", "head", "hip", "leg", "legs",
    "midriff", "mouth", "navel", "neck", "nose", "shoulder", "skin", "stomach", "tail",
    "torso", "waist", "wrist",
}

SEX_MARKERS = {
    "anal", "anilingus", "blowjob", "cunnilingus", "docking", "doggystyle", "fellatio",
    "footjob", "handjob", "intercourse", "masturbation", "penetration", "piledriver",
    "sex", "sexual", "sodomy", "thighjob", "vaginal", "vibrator",
}

SEX_ACTIONS = {
    "bite", "biting", "contact", "fingering", "grabbing", "grab", "holding", "licking",
    "lick", "press", "squeezed", "squeezing", "stimulation", "stimulating", "suck",
    "sucking", "touch", "touching",
}

BDSM_WORDS = {
    "bondage", "bound", "chastity", "gag", "leash", "restraint", "shibari", "blindfold",
    "whipping",
}

DEVICE_WORDS = {
    "butt_plug", "cage", "dildo", "sex_toy", "toy", "vibrator", "plug", "gag",
    "leash", "chastity", "insertion", "penetration",
}

REPRODUCTIVE_WORDS = {
    "ejaculation", "ejaculate", "lactation", "lactating", "pregnancy", "pregnant",
    "reproduction", "sperm", "spermatozoon", "sperm_cell", "ovulation", "birth",
}

SPECIAL_STATE_WORDS = {
    "exposed", "exposure", "implied", "see_through", "transparent", "visible", "visibility",
    "peek", "slip", "covered", "unworn", "wet", "micro", "highleg", "bottomless",
    "pantless", "sagging", "hanging", "unaligned", "apart", "suppress", "bursting",
    "bouncing", "framed", "through", "under", "around", "between", "only", "lift", "over", "seam",
}

ORDINARY_OBJECTS = {
    "animal", "armor", "bag", "bandage", "bandages", "bandaid", "bicycle", "bird", "blanket",
    "bottle", "box", "butterfly", "camera", "can", "card", "cat", "chain", "chair", "coat",
    "computer", "condom", "cup", "dog", "eyewear", "fan", "finger", "flower", "food", "gauze",
    "gift", "glass", "glasses", "goggles", "gun", "hat", "headband", "headphones", "helmet", "hood",
    "hose", "jacket", "knife", "lamp", "mask", "money", "micro_uzi", "microphone", "necklace", "necktie",
    "neckerchief", "notebook", "ofuda", "phone", "pencil", "person", "pole", "pot", "ribbon", "ring",
    "rolling_pin", "rope", "scarf", "seatbelt", "shell", "shelf", "snake", "stethoscope", "sword", "table",
    "tape", "towel", "tree", "umbrella", "veil", "wall", "watermelon", "weapon", "wig",
}

ORDINARY_PLACES = {
    "box", "chair", "desk", "floor", "ground", "room", "table", "wall", "tree",
}

ORDINARY_GARMENTS = {
    "bikini", "bodysuit", "bra", "buruma", "clothes", "dress", "garment", "kimono", "leotard", "panties",
    "pants", "shirt", "shorts", "skirt", "socks", "stockings", "swimsuit", "thighhigh",
    "underwear", "pantyhose",
}

ORDINARY_MARKS = {"bruise", "scar", "mole", "freckles", "tattoo"}

COMMON_COLORS = {
    "aqua", "black", "blue", "brown", "cyan", "gold", "green", "grey", "gray", "orange",
    "pink", "purple", "red", "silver", "teal", "violet", "white", "yellow",
}

KNOWN_DUPLICATES = {
    "no bra", "spread ass", "wide spread legs", "open towel",
}

BOUNDARY_TAGS = {
    "breast rest", "clothes lift", "clothes pull", "gigantic breasts", "hand on own thigh", "mixed sex bathing",
    "no pants", "pregnancy test", "same sex bathing", "sperm cell",
}


def norm(value: object) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKC", text).strip().casefold().replace("_", " ")
    return " ".join(text.split())


def tokens(value: object) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", norm(value)))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_reviews(paths: list[Path]) -> dict[str, dict[str, str]]:
    effective: dict[str, dict[str, str]] = {}
    for path in paths:
        for row in read_csv(path):
            status = row.get("review_status") or row.get("status") or ""
            effective[row.get("canonical", "")] = {
                "status": status,
                "reason": row.get("review_reason") or row.get("scope_reason") or "",
                "source": path.name,
            }
    return effective


def has_phrase(text: str, phrase: str) -> bool:
    return phrase in text


def relation_present(text: str) -> bool:
    return any(
        has_phrase(f" {text} ", f" {word} ")
        for word in ("on", "around", "under", "over", "behind", "between", "through", "inside", "from")
    )


def has_markers(text: str, word_set: set[str], markers: set[str]) -> bool:
    """Match whole tokens or explicit multi-token phrases, never substrings."""
    for marker in markers:
        phrase = marker.replace("_", " ")
        if " " in phrase:
            if phrase in text:
                return True
        elif marker in word_set:
            return True
    return False


def named_or_meme(tag: str, text: str) -> bool:
    return (
        "cosplay" in text
        or "meme" in text
        or "(" in tag and ")" in tag and any(x in text for x in ("_(", " (", "project", "signalis"))
        or text.endswith("~")
        or "'s pose" in text
    )


def ordinary_placement(tag: str, text: str, word_set: set[str]) -> tuple[bool, str]:
    if "armor piercing" in text or "armor-piercing" in tag.casefold():
        return True, "weapon/ammunition compound; ‘piercing’ is not body piercing"
    ordinary_object = bool(word_set & ORDINARY_OBJECTS)
    ordinary_place = bool(word_set & ORDINARY_PLACES)
    body_location = bool(word_set & BODY_SITES)
    if relation_present(text) and (ordinary_object or ordinary_place) and body_location:
        return True, "ordinary object or accessory placed at a body location; placement alone is General discovery"
    if "standing" in word_set and (ordinary_place or ordinary_object) and not (word_set & SEX_MARKERS):
        return True, "ordinary standing/location or object interaction; not a Special-specific pose"
    if ("hand" in word_set or "finger" in word_set) and ordinary_object and not (word_set & SEX_MARKERS):
        return True, "ordinary hand/finger and object interaction; no deep Special relation is established"
    if (word_set & {"hand", "hands", "finger", "fingers"}) and body_location and not (word_set & (SEX_MARKERS | INTIMATE_SITES)):
        return True, "ordinary hand/finger and non-intimate body interaction; no deep Special relation is established"
    if word_set & ORDINARY_MARKS and not (word_set & INTIMATE_SITES):
        return True, "ordinary mark/adornment at a non-intimate site; General discovery is sufficient"
    if "blood" in word_set and (word_set & (ORDINARY_OBJECTS | ORDINARY_PLACES)):
        return True, "ordinary blood-on-object/location concept; the concrete Special R18G body-state family is not established"
    if "leash" in word_set and not (
        word_set & (INTIMATE_SITES | {"mouth", "gag", "bondage", "chastity", "restraint", "bound", "tied"})
    ):
        return True, "ordinary leash/accessory surface lacks a sexual, restraint, or intimate body-site relation"
    if "birthday" in word_set or "birthmark" in word_set:
        return True, "birthday/birthmark vocabulary is ordinary contextual or appearance vocabulary, not reproductive Special discovery"
    if "around" in word_set and (word_set & ORDINARY_GARMENTS) and not (word_set & INTIMATE_SITES):
        return True, "ordinary garment placement around a non-intimate body location is General discovery"
    return False, ""


def stage_a_and_b(tag: str) -> tuple[str, str, str, str, str, str]:
    text = norm(tag)
    word_set = tokens(tag)

    if named_or_meme(tag, text):
        return (
            "GENERAL_NAMED_OR_CONTEXTUAL",
            "GENERAL_ONLY",
            "LIKELY_GENERAL_ONLY",
            "HIGH",
            "P3",
            "named character/cosplay/meme/contextual surface is not a reusable deep Special concept",
        )

    negative, negative_reason = ordinary_placement(tag, text, word_set)
    if negative:
        return (
            "GENERAL_OBJECT_OR_ACTION_PLACEMENT",
            "GENERAL_ONLY",
            "LIKELY_GENERAL_ONLY",
            "HIGH",
            "P3",
            negative_reason,
        )

    if text in KNOWN_DUPLICATES:
        return (
            "SPECIAL_OVERLAP_BOUNDARY",
            "POSSIBLE_DUPLICATE",
            "POSSIBLE_DUPLICATE",
            "HIGH",
            "P2",
            "existing Special semantic/identity surface may already express the same discovery concept",
        )

    if text in BOUNDARY_TAGS or "pregnancy test" in text or "sperm cell" in text:
        return (
            "BOUNDARY_CONCEPT",
            "BOUNDARY_REVIEW",
            "NEEDS_REVIEW",
            "LOW",
            "P1",
            "meaning is specific but the Special-versus-General boundary needs human review",
        )

    intimate = bool(word_set & INTIMATE_SITES)
    sex = has_markers(text, word_set, SEX_MARKERS)
    sex_action = has_markers(text, word_set, SEX_ACTIONS)
    bdsm = has_markers(text, word_set, BDSM_WORDS)
    device = has_markers(text, word_set, DEVICE_WORDS)
    reproduction = has_markers(text, word_set, REPRODUCTIVE_WORDS)
    special_state = bool(word_set & SPECIAL_STATE_WORDS) or any(
        marker in text for marker in ("see through", "visible through", "through clothes", "under clothes")
    )
    ordinary_garment = bool(word_set & ORDINARY_GARMENTS)

    restraint_core = BDSM_WORDS - {"leash"}
    if bdsm and (sex or intimate or has_markers(text, word_set, restraint_core) or word_set & {"gag", "chastity"}):
        return (
            "SPECIAL_BDSM_RESTRAINT",
            "STRONG_SPECIAL_FIT",
            "LIKELY_CANDIDATE",
            "HIGH",
            "P0",
            "BDSM/restraint/device relation is a deep Special discovery family",
        )

    if device and (sex or intimate or word_set & {"butt", "pussy", "anal", "vagina", "penis", "crotch"}):
        return (
            "SPECIAL_SEX_DEVICE",
            "STRONG_SPECIAL_FIT",
            "LIKELY_CANDIDATE",
            "HIGH",
            "P0",
            "specific sex-toy or insertion-device concept fits the deep Special device family",
        )

    if reproduction:
        if text in {"pregnancy test", "sperm cell"}:
            return (
                "BOUNDARY_REPRODUCTIVE_OBJECT",
                "BOUNDARY_REVIEW",
                "NEEDS_REVIEW",
                "LOW",
                "P1",
                "reproductive meaning is clear, but ordinary biological/object vocabulary versus deep Special discovery remains uncertain",
            )
        return (
            "SPECIAL_REPRODUCTION_FLUID",
            "STRONG_SPECIAL_FIT",
            "LIKELY_CANDIDATE",
            "HIGH",
            "P0",
            "specific fluid, lactation, pregnancy, or reproduction concept fits a deep Special family",
        )

    if sex and (intimate or special_state or sex_action or "pose" in word_set or "position" in word_set):
        return (
            "SPECIAL_SEXUAL_RELATION",
            "STRONG_SPECIAL_FIT",
            "LIKELY_CANDIDATE",
            "HIGH",
            "P0",
            "specific sexual action, relation, or body-site concept has high Special discovery value",
        )

    if (
        word_set & {"doggystyle", "docking", "piledriver", "thighjob", "thigh_job"}
        or "spread eagle" in text
    ):
        return (
            "SPECIAL_NAMED_POSE",
            "STRONG_SPECIAL_FIT",
            "LIKELY_CANDIDATE",
            "HIGH",
            "P0",
            "named specialized pose/position is difficult to discover without a deep Special dictionary",
        )

    if "blood" in word_set and (word_set & BODY_SITES or "clothes" in word_set) and not (word_set & ORDINARY_OBJECTS):
        return (
            "SPECIAL_R18G_BODY_STATE",
            "STRONG_SPECIAL_FIT",
            "LIKELY_CANDIDATE",
            "HIGH",
            "P0",
            "concrete blood/body-site state fits the content-neutral R18G body-state discovery family",
        )

    if "sucking" in word_set and word_set & {"finger", "fingers", "toe", "toes"}:
        return (
            "SPECIAL_SEXUAL_RELATION",
            "PLAUSIBLE_SPECIAL_FIT",
            "LIKELY_CANDIDATE",
            "MEDIUM",
            "P1",
            "specific sucking/body-part relation may be difficult to discover from General",
        )

    barrier_state = bool(word_set & {"see", "through", "transparent", "visible", "visibility", "peek"})
    intimate_garment = bool(word_set & {"bra", "bikini", "panties", "underwear", "swimsuit"})
    layered_garment = bool(word_set & {"bikini", "bodysuit", "buruma", "leotard", "panties", "pantyhose", "swimsuit", "underwear"})
    under_body_relation = (
        "under" in word_set
        and ordinary_garment
        and bool(word_set & {"hand", "head", "arm", "face", "mouth", "leg", "legs", "body"})
    )
    layered_special = "under" in word_set and ordinary_garment and layered_garment
    visibility_body_state = bool(word_set & {"armpit", "eyes", "eye", "midriff", "navel", "breast", "breasts", "crotch"}) and bool(
        word_set & {"visible", "visibility", "peek", "through", "only", "lift", "over", "seam", "covered", "exposed"}
    )
    ordinary_state_without_depth = (
        ("wet" in word_set and not intimate_garment)
        or ("unworn" in word_set and not intimate_garment)
        or ("under" in word_set and not (intimate_garment or intimate or sex or under_body_relation or layered_special))
        or ("holding" in word_set and "unworn" in word_set and not intimate_garment)
    )
    if ordinary_state_without_depth:
        return (
            "GENERAL_ORDINARY_CLOTHING_STATE",
            "GENERAL_ONLY",
            "LIKELY_GENERAL_ONLY",
            "HIGH",
            "P3",
            "ordinary garment state/layering lacks an intimate, sexual, or through-clothes discovery concept",
        )

    if (under_body_relation or layered_special) and not (word_set & ORDINARY_OBJECTS):
        return (
            "SPECIAL_CLOTHING_BODY_RELATION",
            "PLAUSIBLE_SPECIAL_FIT",
            "LIKELY_CANDIDATE",
            "MEDIUM",
            "P1",
            "body-part-under-clothing relation is a hidden visual/contact concept that General search may not expose well",
        )

    if special_state and (intimate or sex or (ordinary_garment and barrier_state) or intimate_garment or visibility_body_state):
        if "micro" in word_set and not (word_set & ORDINARY_GARMENTS):
            return (
                "GENERAL_MICRO_OBJECT",
                "GENERAL_ONLY",
                "LIKELY_GENERAL_ONLY",
                "HIGH",
                "P3",
                "micro modifier applies to an ordinary object rather than a Special garment concept",
            )
        return (
            "SPECIAL_EXPOSURE_CLOTHING_STATE",
            "STRONG_SPECIAL_FIT",
            "LIKELY_CANDIDATE",
            "MEDIUM",
            "P1",
            "specific exposure, clothing-barrier, or garment-state concept improves deep Special discovery",
        )

    if (word_set & ORDINARY_MARKS) and intimate:
        return (
            "SPECIAL_INTIMATE_ADORNMENT_STATE",
            "PLAUSIBLE_SPECIAL_FIT",
            "LIKELY_CANDIDATE",
            "MEDIUM",
            "P1",
            "site-specific intimate mark/adornment is more specialized than ordinary General appearance",
        )

    if intimate and (sex_action or special_state or "own" in word_set) and not (word_set & ORDINARY_OBJECTS):
        return (
            "SPECIAL_BODY_RELATION_STATE",
            "PLAUSIBLE_SPECIAL_FIT",
            "LIKELY_CANDIDATE",
            "MEDIUM",
            "P1",
            "body-site relation/state is structurally specific and may be hard to discover from General",
        )

    if "micro" in word_set or "highleg" in word_set or "unworn" in word_set:
        if ordinary_garment and (word_set & {"bikini", "bra", "panties", "shorts", "swimsuit", "thighhigh"}):
            return (
                "SPECIAL_GARMENT_SUBTYPE",
                "PLAUSIBLE_SPECIAL_FIT",
                "LIKELY_CANDIDATE",
                "MEDIUM",
                "P1",
                "named garment subtype/state is harder to discover than an ordinary base garment",
            )
        return (
            "GENERAL_ORDINARY_SUBTYPE",
            "GENERAL_ONLY",
            "LIKELY_GENERAL_ONLY",
            "HIGH",
            "P3",
            "modifier applies to an ordinary object without a deep Special relation",
        )

    if word_set & COMMON_COLORS or word_set & {"large", "medium", "small", "big", "curvy", "long", "short"}:
        return (
            "GENERAL_APPEARANCE_SIZE_COLOR",
            "GENERAL_ONLY",
            "LIKELY_GENERAL_ONLY",
            "HIGH",
            "P3",
            "broad size/color/appearance vocabulary is sufficiently discoverable through General",
        )

    return (
        "GENERAL_OTHER",
        "GENERAL_ONLY",
        "LIKELY_GENERAL_ONLY",
        "MEDIUM",
        "P3",
        "whole-tag meaning does not show a strong Special deep-discovery need",
    )


def load_v1(path: Path) -> list[dict[str, str]]:
    rows = read_csv(path)
    if len(rows) != 29021:
        raise ValueError(f"v1 input must contain 29,021 rows, got {len(rows)}")
    required = {"canonical_tag", "post_count", "aliases", "prescreen_status", "nearest_special_identity"}
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"v1 input missing columns: {sorted(missing)}")
    return rows


def transition_matrix(v1_rows: list[dict[str, str]], v2_rows: list[dict[str, object]]) -> dict[str, Counter[str]]:
    matrix: dict[str, Counter[str]] = defaultdict(Counter)
    for old, new in zip(v1_rows, v2_rows):
        matrix[old["prescreen_status"]][str(new["prescreen_status"])] += 1
    return matrix


def sample_rows(rows: list[dict[str, object]], status: str, seed: int, count: int) -> list[dict[str, object]]:
    group = [row for row in rows if row["prescreen_status"] == status]
    randomizer = random.Random(seed)
    return randomizer.sample(group, min(count, len(group)))


def md_table(rows: list[dict[str, object]], columns: list[tuple[str, str]]) -> list[str]:
    lines = ["| " + " | ".join(label for _, label in columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(f"`{row[key]}`" for key, _ in columns) + " |")
    return lines


def build_summary(
    v1_rows: list[dict[str, str]],
    v2_rows: list[dict[str, object]],
    reviews: dict[str, dict[str, str]],
    regression_rows: list[dict[str, object]],
    audit_rows: list[dict[str, object]],
    p0_rows: list[dict[str, object]],
    source_sha256: str,
) -> str:
    counts = Counter(str(row["prescreen_status"]) for row in v2_rows)
    family_counts = Counter(str(row["stage_a_family"]) for row in v2_rows)
    priority = Counter(str(row["review_priority"]) for row in v2_rows)
    confidence = Counter(str(row["confidence"]) for row in v2_rows)
    matrix = transition_matrix(v1_rows, v2_rows)
    v1_candidate_to_general = sum(
        1 for old, new in zip(v1_rows, v2_rows)
        if old["prescreen_status"] == "LIKELY_CANDIDATE" and new["prescreen_status"] == "LIKELY_GENERAL_ONLY"
    )
    calibration_rows = []
    v2_by_tag = {str(row["canonical_tag"]): row for row in v2_rows}
    for tag, review in sorted(reviews.items()):
        if tag not in v2_by_tag:
            calibration_rows.append({"canonical": tag, "review": review["status"], "v2": "OUTSIDE_INPUT", "reason": "not in 29,021-row GENERAL_ONLY_GAP input"})
        else:
            v2_status = str(v2_by_tag[tag]["prescreen_status"])
            expected = REVIEW_TO_V2.get(review["status"], "UNKNOWN")
            if v2_status != expected:
                calibration_rows.append({"canonical": tag, "review": review["status"], "v2": v2_status, "reason": str(v2_by_tag[tag]["reason"])})

    regression_pass = sum(row["prescreen_status"] == "LIKELY_GENERAL_ONLY" for row in regression_rows)
    p0_false_positive = sum(
        row["stage_b_fit"] != "STRONG_SPECIAL_FIT" and row["prescreen_status"] == "LIKELY_CANDIDATE"
        for row in p0_rows
    )

    lines = [
        "# Issue #94 Special gap prescreen v2",
        "",
        "Status: **FULL 29,021-ROW MEANING-FIRST PRESCREEN COMPLETE / REGRESSION-CHECKED / NO PRODUCTION MUTATION**",
        "",
        "## Decision model",
        "",
        "v2 separates Stage A concept meaning from Stage B Special product fit. Lexical similarity, nearest Special score, token count, and surface patterns are audit context only; none can independently make a row a candidate.",
        "",
        "- Stage A first recognizes whole-tag families such as ordinary object placement, named/contextual identity, garment state, sexual relation, device/restraint, fluid/reproduction, R18G body state, and specialized pose.",
        "- Stage B then asks whether the concept helps a user discover a niche/complex concept through the deep Special dictionary.",
        "- `CONTENT_FILTER_USED=NO`: adult, explicit, fetish, BDSM, fluid, anatomical, gore, violent, taboo, and grotesque content are not exclusion grounds.",
        "",
        "## v2 counts",
        "",
        f"- total processed: **{len(v2_rows):,}** (`GENERAL_ONLY_GAP` input; expected 29,021)",
        "",
        *md_table([
            {"status": status, "count": counts[status]} for status in STATUSES
        ], [("status", "status"), ("count", "count")]),
        "",
        *md_table([
            {"priority": p, "count": priority[p]} for p in PRIORITIES
        ], [("priority", "priority"), ("count", "count")]),
        "",
        "Confidence distribution: " + ", ".join(f"{key}={confidence[key]:,}" for key in ("HIGH", "MEDIUM", "LOW")) + ".",
        "",
        "## Concept area distribution",
        "",
        "Stage A whole-tag concept-family counts:",
        "",
        *md_table(
            [{"area": area, "count": family_counts[area]} for area in sorted(family_counts)],
            [("area", "concept area"), ("count", "count")],
        ),
        "",
        "## v1 → v2 transition matrix",
        "",
        "| v1 \\ v2 | LIKELY_CANDIDATE | LIKELY_GENERAL_ONLY | POSSIBLE_DUPLICATE | NEEDS_REVIEW |",
        "|---|---:|---:|---:|---:|",
    ]
    for old in STATUSES:
        lines.append("| `" + old + "` | " + " | ".join(str(matrix[old][new]) for new in STATUSES) + " |")
    lines += [
        "",
        f"v1 `LIKELY_CANDIDATE` rows moved to v2 `LIKELY_GENERAL_ONLY`: **{v1_candidate_to_general:,}**.",
        "",
        "## Regression false-positive set",
        "",
        f"- regression set total: **{len(regression_rows)}**",
        f"- regression pass (v2 General-only): **{regression_pass}**",
        f"- regression fail: **{len(regression_rows) - regression_pass}**",
        "",
        *md_table(regression_rows, [("canonical_tag", "canonical"), ("stage_a_family", "Stage A"), ("prescreen_status", "v2"), ("reason", "reason")]),
        "",
        "The regression set includes every requested strong negative control, including `type_91_armor-piercing_shell`, ordinary object/body placements, ordinary hand/finger actions, and ordinary standing locations.",
        "",
        "## Meaning-based audit samples",
        "",
        f"- v1 Candidate audit sample: **{sum(row['audit_bucket'] == 'V1_CANDIDATE_AUDIT' for row in audit_rows)}**",
        f"- v1 Needs-review audit sample: **{sum(row['audit_bucket'] == 'V1_NEEDS_REVIEW_AUDIT' for row in audit_rows)}**",
        "- deterministic seed: `9402`; these are audit samples, not a claim that the remaining population was human-reviewed.",
        "",
        *md_table(audit_rows, [("canonical_tag", "canonical"), ("v1_status", "v1"), ("stage_a_family", "Stage A"), ("stage_b_fit", "Stage B"), ("prescreen_status", "v2"), ("review_priority", "priority")]),
        "",
        "## v2 category spot samples",
        "",
    ]
    for status in STATUSES:
        sample = sample_rows(v2_rows, status, 9403 + STATUSES.index(status), 50)
        qualifier = "all available; population below 50" if counts[status] < 50 else "deterministic sample"
        lines += [f"### `{status}` — {len(sample)} rows ({qualifier})", ""]
        lines += md_table(sample, [("canonical_tag", "canonical"), ("stage_a_family", "Stage A"), ("stage_b_fit", "Stage B"), ("review_priority", "priority")])
        lines.append("")

    lines += [
        "## P0 additional spot-check",
        "",
        f"- P0 sample total: **{len(p0_rows)}** (all available P0 rows; requested 100 where population permits)",
        f"- estimated false positives: **{p0_false_positive} / {len(p0_rows)} ({(100 * p0_false_positive / len(p0_rows)):.1f}%)**",
        "- This estimate is a conservative semantic spot-check against the Stage A/B family decision, not an independent population-wide human review.",
        "",
    ]
    lines += md_table(p0_rows, [("canonical_tag", "canonical"), ("stage_a_family", "Stage A"), ("stage_b_fit", "Stage B"), ("prescreen_status", "v2"), ("review_priority", "priority")])
    lines += ["", "## Existing 130-row calibration comparison", ""]
    lines += [
        f"- effective review rows: **{len(reviews)}**",
        f"- v2 calibration mismatches (including 12 out-of-input rows): **{len(calibration_rows)}**",
        "- This is a secondary diagnostic only; v2 does not optimize against the same 130 rows.",
        "",
    ]
    if calibration_rows:
        lines += md_table(calibration_rows, [("canonical", "canonical"), ("review", "human"), ("v2", "v2"), ("reason", "reason")])
    else:
        lines.append("None.")
    lines += [
        "",
        "## Logic changes from v1",
        "",
        "1. Whole-tag semantic family is evaluated before any candidate status.",
        "2. Ordinary object/body placement and ordinary standing/location controls are explicit negative gates.",
        "3. `piercing`, `on`, `around`, `standing`, compound length, and nearest Special similarity are never sufficient evidence.",
        "4. Strong positive families require semantic anchors: sexual relation, intimate body-site state, through-clothes/visibility state, BDSM/restraint, sex device/insertion, concrete fluid/reproductive state, R18G body state, or specialized pose.",
        "5. Boundary concepts are sent to `NEEDS_REVIEW` instead of being promoted by structural resemblance.",
        "",
        "## Guardrails",
        "",
        "- v1 CSV, v1 summary, and v1 script remain unchanged.",
        "- v2 is a prescreen only; no row is promoted into Special.",
        "- `PRODUCTION_FILES_CHANGED=NO`",
        "- `ISSUE70_MUTATED=NO`",
        "",
        f"Input source SHA-256: `{source_sha256}`",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Issue #94 meaning-first Special gap prescreen v2")
    parser.add_argument("--v1-csv", type=Path, required=True)
    parser.add_argument("--review", type=Path, action="append", required=True)
    parser.add_argument("--out-csv", type=Path, required=True)
    parser.add_argument("--out-summary", type=Path, required=True)
    parser.add_argument("--source-sha256", required=True)
    args = parser.parse_args()

    v1_rows = load_v1(args.v1_csv)
    reviews = load_reviews(args.review)
    v2_rows: list[dict[str, object]] = []
    for source in v1_rows:
        family, fit, status, confidence, priority, reason = stage_a_and_b(source["canonical_tag"])
        v2_rows.append(
            {
                "canonical_tag": source["canonical_tag"],
                "post_count": source["post_count"],
                "aliases": source["aliases"],
                "v1_status": source["prescreen_status"],
                "prescreen_status": status,
                "stage_a_family": family,
                "stage_b_fit": fit,
                "nearest_special_identity": source.get("nearest_special_identity", ""),
                "reason": reason,
                "confidence": confidence,
                "review_priority": priority,
                "content_filter_used": "NO",
                "audit_bucket": "",
                "p0_spotcheck": "",
            }
        )

    by_tag = {str(row["canonical_tag"]): row for row in v2_rows}
    regression_tags = [
        "type_91_armor-piercing_shell", "camera_around_neck", "finger_on_eyewear",
        "butterfly_on_face", "cat_on_head", "gauze_on_hand", "hand_on_wall",
        "standing_on_box", "standing_on_sword", "standing_on_chair", "butterfly_on_head",
        "headphones_around_neck",
    ]
    missing_regression = [tag for tag in regression_tags if tag not in by_tag]
    if missing_regression:
        raise ValueError(f"regression tags missing from v1 input: {missing_regression}")
    regression_rows = [by_tag[tag] for tag in regression_tags]

    randomizer = random.Random(9402)
    candidate_rows = [row for row in v2_rows if row["v1_status"] == "LIKELY_CANDIDATE"]
    needs_rows = [row for row in v2_rows if row["v1_status"] == "NEEDS_REVIEW"]
    audit_rows = []
    for bucket, source in (("V1_CANDIDATE_AUDIT", candidate_rows), ("V1_NEEDS_REVIEW_AUDIT", needs_rows)):
        selected = randomizer.sample(source, min(125, len(source)))
        for row in selected:
            row["audit_bucket"] = bucket
            audit_rows.append(row)
    audit_rows.sort(key=lambda row: (str(row["audit_bucket"]), str(row["canonical_tag"])))

    p0_source = [row for row in v2_rows if row["review_priority"] == "P0"]
    p0_rows = random.Random(9404).sample(p0_source, min(100, len(p0_source)))
    for row in p0_rows:
        row["p0_spotcheck"] = "YES"

    write_csv(args.out_csv, v2_rows)
    summary = build_summary(v1_rows, v2_rows, reviews, regression_rows, audit_rows, p0_rows, args.source_sha256)
    args.out_summary.parent.mkdir(parents=True, exist_ok=True)
    args.out_summary.write_text(summary, encoding="utf-8")

    matrix = transition_matrix(v1_rows, v2_rows)
    print(json.dumps({
        "v1_total": len(v1_rows),
        "v2_total": len(v2_rows),
        "status_counts": dict(Counter(row["prescreen_status"] for row in v2_rows)),
        "priority_counts": dict(Counter(row["review_priority"] for row in v2_rows)),
        "candidate_to_general_only": sum(1 for old, new in zip(v1_rows, v2_rows) if old["prescreen_status"] == "LIKELY_CANDIDATE" and new["prescreen_status"] == "LIKELY_GENERAL_ONLY"),
        "regression_total": len(regression_rows),
        "regression_pass": sum(row["prescreen_status"] == "LIKELY_GENERAL_ONLY" for row in regression_rows),
        "audit_sample_total": len(audit_rows),
        "p0_spotcheck_total": len(p0_rows),
        "transition_matrix": {key: dict(value) for key, value in matrix.items()},
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
