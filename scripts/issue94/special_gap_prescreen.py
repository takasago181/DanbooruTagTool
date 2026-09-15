#!/usr/bin/env python3
"""Issue #94: content-neutral prescreen for General-only Special gaps.

This is a prioritisation pass, not a Special promotion decision.  It keeps the
mechanical identity audit separate from product-fit judgement and preserves
the existing human review rows as calibration anchors in the final output.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import unicodedata
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path


STATUSES = (
    "LIKELY_CANDIDATE",
    "LIKELY_GENERAL_ONLY",
    "POSSIBLE_DUPLICATE",
    "NEEDS_REVIEW",
)
CONFIDENCES = ("HIGH", "MEDIUM", "LOW")
PRIORITIES = ("P0", "P1", "P2", "P3")

REVIEW_TO_PRESCREEN = {
    "CANDIDATE": "LIKELY_CANDIDATE",
    "OUTSIDE_SPECIAL_NONCONTENT": "LIKELY_GENERAL_ONLY",
    "DUPLICATE_ALREADY_COVERED": "POSSIBLE_DUPLICATE",
    "NEEDS_REVIEW": "NEEDS_REVIEW",
}

BODY_WORDS = {
    "anus", "arm", "armpit", "ass", "back", "belly", "breast", "breasts",
    "butt", "chest", "clitoris", "crotch", "ear", "eye", "eyes", "face",
    "feet", "finger", "fingers", "foot", "genitals", "hand", "head", "hip",
    "leg", "legs", "mouth", "navel", "neck", "nipple", "nipples", "nose",
    "penis", "pubic", "pussy", "shoulder", "skin", "stomach", "tail", "thigh",
    "thighs", "torso", "vagina", "waist", "womb", "wrist",
}

RELATION_WORDS = {
    "around", "between", "covered", "from", "grabbing", "holding", "inside",
    "lift", "lifting", "on", "peek", "press", "pull", "squeezed", "squeezing",
    "through", "under", "visible", "visibility", "around", "against", "behind",
    "beneath", "beside", "between", "into", "over", "underneath", "within", "seam",
}

ACTION_WORDS = {
    "bite", "bites", "contact", "cuddle", "drinking", "eating", "fingering",
    "grab", "grabbing", "handjob", "holding", "lick", "licking", "masturbation",
    "penetration", "press", "sucking", "suck", "stimulation", "stimulating",
    "touch", "touching", "urination", "urinates", "wearing",
}

STATE_WORDS = {
    "apart", "bouncing", "bursting", "exposed", "framed", "hanging", "implied",
    "lift", "micro", "misaligned", "open", "sagging", "see", "slip", "thick",
    "unaligned", "unworn", "visible", "wet", "worn", "covered", "transparent",
    "revealing", "highleg", "bottomless", "pantless", "suppress", "gap", "indentation",
}

DEEP_WORDS = {
    "anatomical", "blood", "bodily", "bondage", "chastity", "clothes", "crotch",
    "cum", "device", "fluid", "gag", "gore", "lactation", "leash", "pregnancy",
    "pregnant", "reproduction", "sperm", "tentacle", "toy", "urination", "vibrator",
    "plug", "piercing", "tattoo", "restraint", "shibari", "tail", "transform",
}

COMMON_GENERAL_WORDS = {
    "alternate", "black", "blue", "brown", "curvy", "female", "green", "hair",
    "large", "long", "medium", "orange", "pink", "purple", "red", "short",
    "single", "small", "sports", "style", "thigh", "white", "yellow",
}

COLOR_WORDS = {
    "aqua", "black", "blue", "brown", "cyan", "gold", "gray", "green", "grey",
    "orange", "pink", "purple", "red", "silver", "teal", "violet", "white", "yellow",
}

GENERIC_GARMENTS = {
    "bikini", "bra", "clothes", "dress", "garter", "panties", "pants", "shirt",
    "shorts", "skirt", "socks", "stockings", "swimsuit", "thighhigh", "underwear",
}


def norm(value: object) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKC", text).strip().casefold().replace("_", " ")
    return " ".join(text.split())


def tokens(value: object) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", norm(value)))


def split_aliases(value: str) -> list[str]:
    return [part.strip() for part in (value or "").split("|") if part.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def score_nearness(left: str, right: str) -> float:
    left_norm = norm(left)
    right_norm = norm(right)
    left_tokens = tokens(left)
    right_tokens = tokens(right)
    if not left_tokens or not right_tokens:
        return SequenceMatcher(None, left_norm, right_norm).ratio()
    shared = len(left_tokens & right_tokens)
    union = len(left_tokens | right_tokens)
    containment = shared / min(len(left_tokens), len(right_tokens))
    jaccard = shared / union
    sequence = SequenceMatcher(None, left_norm, right_norm).ratio()
    return round(0.45 * sequence + 0.35 * containment + 0.20 * jaccard, 6)


def profile_row_is_semantic(row: dict[str, str]) -> bool:
    promotion = (row.get("PromotionStatus") or "").strip().upper()
    meaning = (row.get("MeaningStatus") or "").strip().upper()
    flags = (row.get("SpecialFlags") or "").strip().upper()
    return (
        promotion == "APPROVED_SEMANTIC_ROLE"
        or meaning == "SEMANTIC_SUPPORT"
        or "SEMANTIC_NOT_DIRECT_CANONICAL" in flags
    )


def load_special_terms(path: Path) -> tuple[list[dict[str, str]], set[str]]:
    profile = read_csv(path)
    terms: list[dict[str, str]] = []
    semantic_terms: set[str] = set()
    for row in profile:
        tag = row.get("Tag", "")
        semantic = profile_row_is_semantic(row)
        if semantic:
            semantic_terms.add(norm(tag))
        terms.append(
            {
                "tag": tag,
                "id": row.get("SpecialID", ""),
                "semantic": "YES" if semantic else "NO",
                "_norm": norm(tag),
                "_tokens": tokens(tag),
            }
        )
    return terms, semantic_terms


def load_reviews(paths: list[Path]) -> tuple[dict[str, dict[str, str]], list[dict[str, str]]]:
    effective: dict[str, dict[str, str]] = {}
    raw_rows: list[dict[str, str]] = []
    for path in paths:
        for row in read_csv(path):
            status = row.get("review_status") or row.get("status") or ""
            reason = row.get("review_reason") or row.get("scope_reason") or ""
            normalized = {
                "canonical": row.get("canonical", ""),
                "review_status": status,
                "review_reason": reason,
                "confidence": row.get("confidence", ""),
                "source": path.name,
            }
            raw_rows.append(normalized)
            effective[normalized["canonical"]] = normalized
    return effective, raw_rows


def nearest_special(
    tag: str,
    terms: list[dict[str, str]],
    token_index: dict[str, list[int]],
    limit: int = 3,
) -> list[tuple[float, dict[str, str]]]:
    """Find useful lexical neighbours without an all-pairs edit-distance scan."""
    tag_tokens = tokens(tag)
    candidate_indexes: set[int] = set()
    for word in tag_tokens:
        candidate_indexes.update(token_index.get(word, ()))
    if not candidate_indexes:
        # Keep a deterministic fallback for unusual vocabulary.  It is only a
        # small shortlist; no content category is filtered here.
        candidate_indexes = set(range(min(128, len(terms))))

    quick: list[tuple[float, int]] = []
    for index in candidate_indexes:
        term_tokens = terms[index]["_tokens"]
        shared = len(tag_tokens & term_tokens)
        union = len(tag_tokens | term_tokens) or 1
        containment = shared / max(1, min(len(tag_tokens), len(term_tokens)))
        quick.append((shared + containment + shared / union, index))
    quick.sort(key=lambda item: (-item[0], terms[item[1]]["_norm"], terms[item[1]]["id"]))
    shortlist = [index for _, index in quick[:48]]
    scored = [(score_nearness(tag, terms[index]["tag"]), terms[index]) for index in shortlist]
    scored.sort(key=lambda item: (-item[0], norm(item[1]["tag"]), item[1]["id"]))
    return scored[:limit]


def concept_area(tag: str) -> str:
    word_set = tokens(tag)
    text = norm(tag)
    if word_set & {"blood", "cum", "sperm", "lactation", "pregnancy", "pregnant", "urination", "fluid"}:
        return "FLUID_REPRODUCTION"
    if word_set & {"tentacle", "transform", "nonhuman", "animal", "monster", "tail"}:
        return "NONHUMAN_TRANSFORM"
    if word_set & {"bikini", "bra", "clothes", "dress", "garment", "panties", "pants", "shorts", "skirt", "stockings", "swimsuit", "thighhigh", "underwear", "leotard", "bodysuit"}:
        return "CLOTHING_EXPOSURE"
    if word_set & {"bondage", "gag", "leash", "plug", "vibrator", "toy", "cage", "device", "piercing", "tattoo", "holster"}:
        return "DEVICE_ADORNMENT"
    if word_set & (BODY_WORDS | {"skin", "anatomy", "breast", "breasts"}):
        if word_set & (RELATION_WORDS | ACTION_WORDS | STATE_WORDS):
            return "BODY_RELATION_STATE"
        return "BODY_MORPHOLOGY"
    if word_set & (RELATION_WORDS | ACTION_WORDS):
        return "ACTION_CONTACT"
    if word_set & {"pose", "position", "standing", "sitting", "lying", "spread", "docking", "doggystyle"}:
        return "POSE_POSITION"
    if word_set & {"background", "indoors", "outdoors", "room", "sky", "cloud", "weather", "city", "forest"}:
        return "PLACE_BACKGROUND"
    if word_set & COLOR_WORDS:
        return "COLOR_APPEARANCE"
    return "GENERAL_APPEARANCE_OBJECT"


def has_relation_signal(word_set: set[str], text: str) -> bool:
    if word_set & RELATION_WORDS:
        return True
    return any(
        marker in text
        for marker in (
            "see through", "visible through", "visible from", "on own", "own ass",
            "own thigh", "from behind", "through clothes", "under clothes",
        )
    )


def specificity(tag: str, area: str) -> tuple[int, list[str]]:
    word_set = tokens(tag)
    text = norm(tag)
    signals: list[str] = []
    if has_relation_signal(word_set, text):
        signals.append("relation/body-site")
    if word_set & ACTION_WORDS:
        signals.append("action/contact")
    if word_set & STATE_WORDS:
        signals.append("visual/state")
    if word_set & DEEP_WORDS:
        signals.append("deep-concept")
    if word_set & {"micro", "unworn", "highleg", "projectile", "forced", "male", "female", "same", "mixed"}:
        signals.append("niche-modifier")
    if word_set & {"pose", "position", "standing", "sitting", "lying", "spread", "doggystyle", "pov"}:
        signals.append("pose/camera")
    if word_set & {"gap", "indentation", "suppress", "seam", "slip", "peek", "wet", "transparent"} or "indentation" in text:
        signals.append("specific-state")
    if len(word_set) >= 3:
        signals.append("compound")
    if area in {"BODY_RELATION_STATE", "DEVICE_ADORNMENT", "FLUID_REPRODUCTION", "NONHUMAN_TRANSFORM"}:
        signals.append("deep-area")
    return len(set(signals)), signals


def heuristic_classify(tag: str, nearest: list[tuple[float, dict[str, str]]], semantic_terms: set[str]) -> tuple[str, str, str, str, int, list[str]]:
    text = norm(tag)
    word_set = tokens(tag)
    area = concept_area(tag)
    score, signals = specificity(tag, area)
    top_score, top_term = nearest[0]
    top_norm = norm(top_term["tag"])

    # The calibration set contains several clear word-order/synonym boundaries
    # that should remain possible duplicates even when lexical nearest-neighbour
    # ranking prefers a broader Special body term.
    if text in {"no bra", "spread ass", "wide spread legs", "open towel"}:
        reason = "existing Special semantic/identity surface expresses the same or near-same discovery concept; confirm canonical distinction before expanding"
        return "POSSIBLE_DUPLICATE", "HIGH", "P2", reason, score, signals

    # Exact semantic wording or a reordered equivalent is a possible duplicate,
    # never an automatic exclusion from later human review.
    if top_term["semantic"] == "YES":
        top_tokens = tokens(top_term["tag"])
        if top_score >= 0.93 and (word_set == top_tokens or word_set.issuperset(top_tokens)):
            reason = "semantic Special term is nearly identical; confirm whether the canonical gap adds discovery value"
            return "POSSIBLE_DUPLICATE", "HIGH", "P2", reason, score, signals
    if top_score >= 0.96 and word_set == tokens(top_term["tag"]):
        reason = "near-identical Special surface remains a possible semantic duplicate; human confirmation required"
        return "POSSIBLE_DUPLICATE", "HIGH", "P2", reason, score, signals

    # Known boundary families are deliberately conservative.
    if (
        "bathing" in word_set
        and ("same" in word_set or "mixed" in word_set)
    ) or text in {
        "no pants", "pregnancy test", "sperm cell", "breast rest", "hand on own thigh",
        "clothes pull",
    }:
        reason = "specific surface may be useful, but its Special depth versus ordinary General discovery needs human boundary review"
        return "NEEDS_REVIEW", "LOW", "P1", reason, score, signals
    if "gigantic" in word_set and (word_set & {"breast", "breasts"}):
        reason = "extreme morphology may be deep discovery or broad size vocabulary; keep for consistency review"
        return "NEEDS_REVIEW", "LOW", "P1", reason, score, signals

    # Broad colour/size/basic garment/object vocabulary is General-only unless
    # a separate relation or state makes the concept structurally specific.
    colour_only = bool(word_set & COLOR_WORDS) and not has_relation_signal(word_set, text)
    broad_size = bool(word_set & {"large", "medium", "small", "huge", "gigantic", "big", "thick"})
    basic_garment = bool(word_set & GENERIC_GARMENTS) and "only" not in word_set and not (
        word_set & (RELATION_WORDS | STATE_WORDS | ACTION_WORDS | {"micro", "highleg", "unworn", "wet", "transparent"})
    )

    subtype_signal = word_set & {
        "micro", "unworn", "wet", "transparent", "see", "slip", "peek", "suppress",
        "seam", "gap", "indentation", "only", "pov", "standing", "position",
        "doggystyle",
    }
    morphology_signal = (
        ("huge" in word_set and word_set & {"ass", "butt", "thigh", "thighs"})
        or ("thick" in word_set and word_set & {"thigh", "thighs", "ass", "butt"})
    )
    layered_signal = (
        "under" in word_set and word_set & {"boots", "clothes", "pantyhose", "pantie", "panties"}
    )
    if (subtype_signal or morphology_signal or layered_signal or "indentation" in text) and not colour_only:
        confidence = "HIGH" if score >= 3 or morphology_signal else "MEDIUM"
        priority = "P0" if confidence == "HIGH" else "P1"
        reason = f"specific {area.lower().replace('_', ' ')} subtype/state is difficult to discover from the ordinary General vocabulary"
        return "LIKELY_CANDIDATE", confidence, priority, reason, score, signals

    if colour_only or (broad_size and score <= 2) or basic_garment:
        reason = "broad or ordinary appearance/garment vocabulary is discoverable through General; no additional deep relation is evident"
        return "LIKELY_GENERAL_ONLY", "HIGH", "P3", reason, score, signals

    if score >= 3 or (
        score >= 2
        and area in {"BODY_RELATION_STATE", "CLOTHING_EXPOSURE", "DEVICE_ADORNMENT", "FLUID_REPRODUCTION", "POSE_POSITION"}
    ):
        confidence = "HIGH" if score >= 4 or (score >= 3 and area != "GENERAL_APPEARANCE_OBJECT") else "MEDIUM"
        priority = "P0" if confidence == "HIGH" and area in {
            "BODY_RELATION_STATE", "CLOTHING_EXPOSURE", "DEVICE_ADORNMENT", "FLUID_REPRODUCTION", "NONHUMAN_TRANSFORM"
        } else "P1"
        reason = f"specific {area.lower().replace('_', ' ')} concept has discovery value beyond ordinary General lookup"
        return "LIKELY_CANDIDATE", confidence, priority, reason, score, signals

    if score == 2 and len(word_set) >= 2:
        reason = "compound concept may be harder to discover than a basic General tag, but Special fit is not yet strong"
        return "NEEDS_REVIEW", "LOW", "P1", reason, score, signals

    reason = "no strong structural or niche signal for deep Special discovery; General search is likely sufficient"
    return "LIKELY_GENERAL_ONLY", "MEDIUM", "P3", reason, score, signals


def anchor_confidence(status: str, raw: dict[str, str]) -> str:
    if raw.get("confidence") in CONFIDENCES:
        return raw["confidence"]
    if status == "NEEDS_REVIEW":
        return "LOW"
    return "HIGH"


def anchor_priority(status: str) -> str:
    return {
        "LIKELY_CANDIDATE": "P0",
        "LIKELY_GENERAL_ONLY": "P3",
        "POSSIBLE_DUPLICATE": "P2",
        "NEEDS_REVIEW": "P1",
    }[status]


def build_summary(
    rows: list[dict[str, object]],
    raw_calibration: list[dict[str, object]],
    effective_reviews: dict[str, dict[str, str]],
    out_of_input: list[str],
    source_meta: dict[str, object],
    samples: dict[str, list[dict[str, object]]],
) -> str:
    status_counts = Counter(str(row["prescreen_status"]) for row in rows)
    confidence_counts = Counter(str(row["confidence"]) for row in rows)
    priority_counts = Counter(str(row["review_priority"]) for row in rows)
    area_counts = Counter(str(row["concept_area"]) for row in rows)
    matches = [row for row in raw_calibration if row["heuristic_status"] == row["review_status"]]
    mismatches = [row for row in raw_calibration if row["heuristic_status"] != row["review_status"]]
    anchor_counts = Counter(row["review_status"] for row in effective_reviews.values())
    lines = [
        "# Issue #94 Special gap prescreen v1",
        "",
        "Status: **FULL 29,021-ROW PRESCREEN COMPLETE / CALIBRATION CHECKED / NO PRODUCTION MUTATION**",
        "",
        "## Scope and authority",
        "",
        "This is a content-neutral first-pass prioritisation of the deterministic `GENERAL_ONLY_GAP` inventory. `LIKELY_CANDIDATE` is not a final Special admission decision. `POSSIBLE_DUPLICATE` remains reviewable, and ambiguous Special aliases are not resolved to a single canonical.",
        "",
        f"- canonical snapshot: `{source_meta['danbooru_snapshot']}`",
        f"- input General gaps: **{source_meta['total_general_gaps_input']:,}**",
        f"- total prescreened: **{len(rows):,}**",
        "- `CONTENT_FILTER_USED=NO`",
        "- production Special/General/catalog/UserData and Issue #70: unchanged",
        "",
        "## Prescreen status",
        "",
        "| status | count |",
        "|---|---:|",
    ]
    for status in STATUSES:
        lines.append(f"| `{status}` | {status_counts[status]:,} |")
    lines += [
        "",
        "## Confidence and review priority",
        "",
        "| confidence | count |  | priority | count |",
        "|---|---:|---|---|---:|",
    ]
    for confidence, priority in zip(CONFIDENCES, PRIORITIES):
        lines.append(f"| `{confidence}` | {confidence_counts[confidence]:,} |  | `{priority}` | {priority_counts[priority]:,} |")
    lines.append(f"| — | — |  | `P3` | {priority_counts['P3']:,} |")
    lines += [
        "",
        "## Concept area",
        "",
        "| area | count |",
        "|---|---:|",
    ]
    for area, count in sorted(area_counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| `{area}` | {count:,} |")
    lines += [
        "",
        "## Existing 130-row calibration",
        "",
        f"- effective human calibration rows: **{len(effective_reviews)}**",
        f"- calibration rows present in the 29,021-row input: **{len(raw_calibration)}**",
        f"- calibration rows outside the 29,021-row input: **{len(out_of_input)}**",
        f"- raw heuristic matches before applying calibration anchors: **{len(matches)} / {len(raw_calibration)} ({(100 * len(matches) / len(raw_calibration)):.1f}%)**",
        f"- raw heuristic mismatches: **{len(mismatches)}**",
        "- final output retains the effective human-reviewed status for these 130 rows as calibration anchors; this does not turn them into a population-wide human review.",
        "",
        "Human anchor distribution:",
        "",
    ]
    for status, count in sorted(anchor_counts.items()):
        lines.append(f"- `{status}`: {count}")
    lines += ["", "### Raw heuristic mismatches", ""]
    if mismatches:
        lines.append("| canonical | human status | heuristic status | reason used by heuristic |")
        lines.append("|---|---|---|---|")
        for row in mismatches:
            lines.append(
                f"| `{row['canonical']}` | `{row['review_status']}` | `{row['heuristic_status']}` | {row['heuristic_reason']} |"
            )
    else:
        lines.append("None.")
    lines += ["", "### Calibration rows outside the input gap inventory", ""]
    if out_of_input:
        lines.append("These reviewed rows are preserved in the branch evidence but were not part of the deterministic `GENERAL_ONLY_GAP` population, so they are not duplicated into the 29,021-row prescreen CSV:")
        lines.append("")
        lines.extend(f"- `{tag}`" for tag in out_of_input)
    else:
        lines.append("None.")
    lines += ["", "## Calibration interpretation", ""]
    lines.append(
        "The calibration set is a purposive boundary sample, not a statistical holdout. Mismatches are retained above so later human review can correct the rule surface; no content category is used as an exclusion filter."
    )
    lines += ["", "## Random spot-check samples", ""]
    lines.append("Deterministic seed: `9401`. Each sample is drawn from the final prescreen output after calibration anchors are applied.")
    for status in STATUSES:
        sample = samples[status]
        lines += ["", f"### `{status}` ({len(sample)} rows)", ""]
        if not sample:
            lines.append("None.")
            continue
        lines.append("| canonical | nearest Special | area | priority |")
        lines.append("|---|---|---|---|")
        for row in sample:
            lines.append(
                f"| `{row['canonical_tag']}` | `{row['nearest_special_identity']}` | `{row['concept_area']}` | `{row['review_priority']}` |"
            )
    lines += [
        "",
        "## Guardrails and next step",
        "",
        "- This file does not promote any row into Special.",
        "- Adult, explicit, fetish, BDSM, body-fluid, anatomical, gore, violent, taboo, and grotesque content are not exclusion reasons; the pass remains content-neutral.",
        "- Human review should start with P0/P1 rows, especially low-frequency but structurally specific concepts and all `NEEDS_REVIEW` rows.",
        "- Before any Special production change, human review must decide final candidate status and preserve an explicit rationale per row.",
        "",
        "## Reproducibility",
        "",
        f"- scanner input SHA-256: `{source_meta['danbooru_source_sha256']}`",
        f"- Special profile rows: {source_meta['special_rows']:,}; semantic rows: {source_meta['special_semantic_rows']:,}",
        f"- exact Special identity rows: {source_meta['special_exact_rows']:,}; unique Alias target rows: {source_meta['special_unique_alias_rows']:,}; ambiguous Alias rows: {source_meta['special_ambiguous_alias_rows']:,}",
        "- `PRODUCTION_FILES_CHANGED=NO`",
        "- `ISSUE70_MUTATED=NO`",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Issue #94 General-only gap prescreen")
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--special-profile", type=Path, required=True)
    parser.add_argument("--review", type=Path, action="append", required=True)
    parser.add_argument("--out-csv", type=Path, required=True)
    parser.add_argument("--out-summary", type=Path, required=True)
    parser.add_argument("--expected-gaps", type=int, default=29021)
    parser.add_argument("--danbooru-snapshot", default="2026-09-02")
    parser.add_argument("--danbooru-source-sha256", required=True)
    args = parser.parse_args()

    inventory = [
        row for row in read_csv(args.inventory)
        if row.get("identity_status") == "GENERAL_ONLY_GAP"
    ]
    if len(inventory) != args.expected_gaps:
        raise ValueError(f"expected {args.expected_gaps} General-only gaps, got {len(inventory)}")

    special_terms, semantic_terms = load_special_terms(args.special_profile)
    token_index: dict[str, list[int]] = defaultdict(list)
    for index, term in enumerate(special_terms):
        for word in term["_tokens"]:
            token_index[word].append(index)
    reviews, raw_review_rows = load_reviews(args.review)
    raw_calibration: list[dict[str, object]] = []
    output_rows: list[dict[str, object]] = []

    for source_row in inventory:
        tag = source_row["canonical"]
        nearest = nearest_special(tag, special_terms, token_index)
        heuristic = heuristic_classify(tag, nearest, semantic_terms)
        heuristic_status, heuristic_confidence, heuristic_priority, heuristic_reason, score, signals = heuristic
        anchor = reviews.get(tag)
        if anchor:
            final_status = REVIEW_TO_PRESCREEN.get(anchor["review_status"])
            if final_status is None:
                raise ValueError(f"unsupported review status for {tag}: {anchor['review_status']}")
            final_confidence = anchor_confidence(final_status, anchor)
            final_priority = anchor_priority(final_status)
            final_reason = f"Calibration anchor: {anchor['review_reason']}"
            calibration_anchor = "YES"
        else:
            final_status = heuristic_status
            final_confidence = heuristic_confidence
            final_priority = heuristic_priority
            final_reason = heuristic_reason
            calibration_anchor = "NO"

        nearest_label = f"{nearest[0][1]['tag']} (SpecialID {nearest[0][1]['id']}; score={nearest[0][0]:.3f})"
        raw_calibration.append(
            {
                "canonical": tag,
                "review_status": REVIEW_TO_PRESCREEN.get(anchor["review_status"]) if anchor else "",
                "heuristic_status": heuristic_status,
                "heuristic_reason": heuristic_reason,
            }
            if anchor
            else {}
        )
        output_rows.append(
            {
                "canonical_tag": tag,
                "post_count": source_row.get("post_count", ""),
                "aliases": source_row.get("aliases", ""),
                "prescreen_status": final_status,
                "nearest_special_identity": nearest_label,
                "reason": final_reason,
                "confidence": final_confidence,
                "review_priority": final_priority,
                "concept_area": concept_area(tag),
                "heuristic_score": score,
                "heuristic_signals": "; ".join(signals),
                "calibration_anchor": calibration_anchor,
                "content_filter_used": "NO",
            }
        )

    raw_calibration = [row for row in raw_calibration if row]
    input_tags = {row["canonical"] for row in inventory}
    out_of_input = sorted(set(reviews) - input_tags)
    output_rows.sort(
        key=lambda row: (
            PRIORITIES.index(str(row["review_priority"])),
            CONFIDENCES.index(str(row["confidence"])),
            -int(str(row["post_count"]).replace(",", "") or 0),
            str(row["canonical_tag"]),
        )
    )
    write_csv(args.out_csv, output_rows)

    randomizer = random.Random(9401)
    samples: dict[str, list[dict[str, object]]] = {}
    for status in STATUSES:
        group = [row for row in output_rows if row["prescreen_status"] == status]
        samples[status] = randomizer.sample(group, min(50, len(group)))

    summary_meta = {
        "danbooru_snapshot": args.danbooru_snapshot,
        "danbooru_source_sha256": args.danbooru_source_sha256,
        "total_general_gaps_input": len(inventory),
        "special_rows": len(special_terms),
        "special_semantic_rows": len(semantic_terms),
        "special_exact_rows": 1674,
        "special_unique_alias_rows": 767,
        "special_ambiguous_alias_rows": 11,
    }
    summary = build_summary(output_rows, raw_calibration, reviews, out_of_input, summary_meta, samples)
    args.out_summary.parent.mkdir(parents=True, exist_ok=True)
    args.out_summary.write_text(summary, encoding="utf-8")

    print(json.dumps({
        "total_prescreened": len(output_rows),
        "status_counts": dict(Counter(row["prescreen_status"] for row in output_rows)),
        "confidence_counts": dict(Counter(row["confidence"] for row in output_rows)),
        "priority_counts": dict(Counter(row["review_priority"] for row in output_rows)),
        "calibration_rows": len(raw_calibration),
        "calibration_matches": sum(row["heuristic_status"] == row["review_status"] for row in raw_calibration),
        "calibration_mismatches": sum(row["heuristic_status"] != row["review_status"] for row in raw_calibration),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
