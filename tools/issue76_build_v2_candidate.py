#!/usr/bin/env python3
"""Build Issue #76 v2 browse candidate from the accepted Issue #56 mapping.

This is analysis-only. It does not mutate canonical Special data or production taxonomy.
It projects the accepted v1 primary/secondary browse paths into three shallow axes:
- kind/home
- body-site facets
- theme facets

The projection is intentionally conservative and preserves explicit review queues.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.issue56_ui_genre_pilot_selector import load_prompt_reference
from tools.issue56_ui_genre_rollout import (
    SOURCE_DIR,
    load_taxonomy,
    merge_mapping_sources,
    validate_mapping,
)

VERSION = "issue76-v2-candidate-v0.2"
DEFAULT_OUTPUT_DIR = ROOT / "docs" / "issue76" / "generated"

TYPE_MAP = {
    "BODY_ANATOMY": "BODY_STATE",
    "NUDITY_CLOTHING_EXPOSURE": "CLOTHING_EXPOSURE",
    "POSE_POSITION_COMPOSITION": "POSE_SCENE",
    "SEXUAL_ACTIVITY_STIMULATION": "ACTION_CONTACT",
    "CONTACT_INSERTION_BODY_SITE": "ACTION_CONTACT",
    "TOOLS_TOYS_MACHINES": "TOOL_OBJECT",
    "FLUID_EXCRETION_SOILING": "FLUID_EXCRETION",
    "NONHUMAN_TENTACLE_TRANSFORMATION": "NONHUMAN_TRANSFORMATION",
    "PERSON_RELATION_ROLE": "PERSON_RELATION",
    "SITUATION_SCENE": "POSE_SCENE",
    "META_RATING": "META_EXPRESSION",
}

TYPE_LABELS = {
    "BODY_STATE": "身体・状態",
    "CLOTHING_EXPOSURE": "衣服・露出",
    "ACTION_CONTACT": "行為・接触",
    "TOOL_OBJECT": "道具・物",
    "FLUID_EXCRETION": "体液・排泄",
    "POSE_SCENE": "ポーズ・構図・場面",
    "PERSON_RELATION": "人物・関係",
    "NONHUMAN_TRANSFORMATION": "異形・変形",
    "META_EXPRESSION": "表現・メタ",
}

BODY_FACET_MAP = {
    ("BODY_ANATOMY", "BREAST_NIPPLE"): "BREAST_NIPPLE",
    ("BODY_ANATOMY", "FEMALE_GENITAL"): "FEMALE_GENITAL",
    ("BODY_ANATOMY", "MALE_GENITAL"): "MALE_GENITAL",
    ("BODY_ANATOMY", "BUTTOCK_ANUS"): "BUTTOCK_ANUS",
    ("CONTACT_INSERTION_BODY_SITE", "ANAL_SITE"): "BUTTOCK_ANUS",
    ("CONTACT_INSERTION_BODY_SITE", "FEMALE_GENITAL_SITE"): "FEMALE_GENITAL",
    ("CONTACT_INSERTION_BODY_SITE", "URETHRAL_SITE"): "URETHRA",
    ("SEXUAL_ACTIVITY_STIMULATION", "ORAL_ACTIVITY"): "MOUTH_ORAL",
    ("BONDAGE_BDSM_DOMINATION", "GAG_MOUTH_RESTRAINT"): "MOUTH_ORAL",
}

BODY_LABELS = {
    "BREAST_NIPPLE": "乳房・乳首",
    "FEMALE_GENITAL": "女性器",
    "MALE_GENITAL": "男性器",
    "BUTTOCK_ANUS": "臀部・肛門（暫定）",
    "MOUTH_ORAL": "口・口内",
    "URETHRA": "尿道",
}

THEME_MAP = {
    "BONDAGE_BDSM_DOMINATION": "BDSM_RESTRAINT",
    "INJURY_R18G": "INJURY_R18G",
    "REPRODUCTION_PREGNANCY_LACTATION": "REPRO_PREGNANCY_LACTATION",
}

THEME_LABELS = {
    "BDSM_RESTRAINT": "拘束・BDSM",
    "INJURY_R18G": "損傷・R18G",
    "REPRO_PREGNANCY_LACTATION": "生殖・妊娠・授乳",
}

BDSM_FALLBACK = {
    "": "ACTION_CONTACT",
    "BONDAGE_STATE": "ACTION_CONTACT",
    "BONDAGE_POSITION": "POSE_SCENE",
    "RESTRAINT_DEVICE": "TOOL_OBJECT",
    "GAG_MOUTH_RESTRAINT": "TOOL_OBJECT",
    "CHASTITY_CONTROL": "TOOL_OBJECT",
    "PAIN_TORTURE": "ACTION_CONTACT",
    "DOMINATION_SUBMISSION": "PERSON_RELATION",
    "FORCE_NONCONSENT": "ACTION_CONTACT",
}

MAPPING_FIELDS = [
    "special_id",
    "primary_genre_id",
    "primary_subgenre_id",
    "secondary_paths",
    "classification_status",
    "ambiguity_note",
    "v2_kind_id",
    "v2_kind_ja",
    "v2_body_sites",
    "v2_body_sites_ja",
    "v2_themes",
    "v2_themes_ja",
    "v2_status",
    "v2_reason",
    "v2_review_note",
]

REVIEW_FIELDS = [
    "special_id",
    "v1_primary",
    "v1_secondary",
    "candidate_kind",
    "candidate_body_sites",
    "candidate_themes",
    "review_class",
    "severity",
    "review_note",
]


def _parse_path(value: str) -> tuple[str, str]:
    if not value:
        return "", ""
    parts = value.split(">", 1)
    return parts[0].strip(), parts[1].strip() if len(parts) == 2 else ""


def _all_paths(mapping: dict[str, str]) -> list[tuple[str, str]]:
    paths: list[tuple[str, str]] = []
    if mapping["primary_genre_id"]:
        paths.append((mapping["primary_genre_id"], mapping["primary_subgenre_id"]))
    for raw in mapping["secondary_paths"].split("|"):
        raw = raw.strip()
        if raw:
            paths.append(_parse_path(raw))
    return paths


def _derive_kind(mapping: dict[str, str]) -> tuple[str, str]:
    genre = mapping["primary_genre_id"]
    subgenre = mapping["primary_subgenre_id"]
    if not genre:
        return "", "v1_unresolved"
    if genre in TYPE_MAP:
        return TYPE_MAP[genre], "direct_primary_genre"
    if genre == "BONDAGE_BDSM_DOMINATION":
        return BDSM_FALLBACK.get(subgenre, "ACTION_CONTACT"), "bdsm_subgenre_projection"
    if genre == "REPRODUCTION_PREGNANCY_LACTATION":
        secondary_types = []
        for raw in mapping["secondary_paths"].split("|"):
            raw = raw.strip()
            if not raw:
                continue
            secondary_genre, _ = _parse_path(raw)
            if secondary_genre in TYPE_MAP:
                secondary_types.append(TYPE_MAP[secondary_genre])
        for preferred in ("CLOTHING_EXPOSURE", "ACTION_CONTACT", "BODY_STATE"):
            if preferred in secondary_types:
                return preferred, "repro_secondary_projection"
        return "BODY_STATE", "repro_default_body_state"
    if genre == "INJURY_R18G":
        secondary_types = []
        for raw in mapping["secondary_paths"].split("|"):
            raw = raw.strip()
            if not raw:
                continue
            secondary_genre, _ = _parse_path(raw)
            if secondary_genre in TYPE_MAP:
                secondary_types.append(TYPE_MAP[secondary_genre])
        for preferred in ("ACTION_CONTACT", "FLUID_EXCRETION", "PERSON_RELATION", "BODY_STATE"):
            if preferred in secondary_types:
                return preferred, "injury_secondary_projection"
        return "BODY_STATE", "injury_default_body_state"
    return "", "unhandled_primary_genre"


def _derive_body_sites(mapping: dict[str, str]) -> list[str]:
    result: list[str] = []
    for path in _all_paths(mapping):
        facet = BODY_FACET_MAP.get(path)
        if facet and facet not in result:
            result.append(facet)
    return result


def _derive_themes(mapping: dict[str, str]) -> list[str]:
    result: list[str] = []
    for genre, _ in _all_paths(mapping):
        theme = THEME_MAP.get(genre)
        if theme and theme not in result:
            result.append(theme)
    return result


def _write_csv(path: Path, fields: Sequence[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build_candidate(output_dir: Path) -> dict[str, object]:
    source_rows, source_hashes = load_prompt_reference(SOURCE_DIR)
    _, genres, subgenres = load_taxonomy()
    mappings, _ = merge_mapping_sources()
    validate_mapping(source_rows, mappings, genres, subgenres, require_complete=True)

    if len(source_rows) != 2788 or set(mappings) != set(range(1, 2789)):
        raise ValueError("Issue #76 requires exact frozen Special ID coverage 1..2788")

    candidate_rows: list[dict[str, str]] = []
    review_rows: list[dict[str, str]] = []

    for special_id in sorted(mappings):
        mapping = mappings[special_id]
        kind, reason = _derive_kind(mapping)
        body_sites = _derive_body_sites(mapping)
        themes = _derive_themes(mapping)
        status = "AUTO_CANDIDATE"
        review_note = ""

        if mapping["classification_status"] == "REVIEW_REQUIRED":
            status = "REVIEW_V1_UNRESOLVED"
            review_note = mapping["ambiguity_note"] or "v1 unresolved"
            kind = ""
            body_sites = []
            themes = []
        elif not kind:
            status = "REVIEW_NO_KIND"
            review_note = reason
        elif (
            mapping["primary_genre_id"] == "BONDAGE_BDSM_DOMINATION"
            and mapping["primary_subgenre_id"] == "CHASTITY_CONTROL"
        ):
            status = "REVIEW_MIXED_FAMILY"
            review_note = "CHASTITY_CONTROL mixes device/state/control concepts"

        has_ambiguous_buttock_route = any(
            genre == "BODY_ANATOMY" and subgenre == "BUTTOCK_ANUS"
            for genre, subgenre in _all_paths(mapping)
        )
        if has_ambiguous_buttock_route:
            review_note = (
                review_note + "; " if review_note else ""
            ) + "BUTTOCK_ANUS v1 route conflates buttock and anus"

        row = {
            "special_id": str(special_id),
            "primary_genre_id": mapping["primary_genre_id"],
            "primary_subgenre_id": mapping["primary_subgenre_id"],
            "secondary_paths": mapping["secondary_paths"],
            "classification_status": mapping["classification_status"],
            "ambiguity_note": mapping["ambiguity_note"],
            "v2_kind_id": kind,
            "v2_kind_ja": TYPE_LABELS.get(kind, ""),
            "v2_body_sites": " | ".join(body_sites),
            "v2_body_sites_ja": " | ".join(BODY_LABELS[item] for item in body_sites),
            "v2_themes": " | ".join(themes),
            "v2_themes_ja": " | ".join(THEME_LABELS[item] for item in themes),
            "v2_status": status,
            "v2_reason": reason,
            "v2_review_note": review_note,
        }
        candidate_rows.append(row)

        review_classes: list[str] = []
        severity = ""
        if status != "AUTO_CANDIDATE":
            review_classes.append(status)
            severity = "BLOCKING" if status == "REVIEW_V1_UNRESOLVED" else "FAMILY_REVIEW"
        if has_ambiguous_buttock_route:
            review_classes.append("SITE_FACET_AUDIT")
            severity = severity or "FACET_AUDIT"
        if review_classes:
            review_rows.append(
                {
                    "special_id": str(special_id),
                    "v1_primary": mapping["primary_genre_id"]
                    + (f">{mapping['primary_subgenre_id']}" if mapping["primary_subgenre_id"] else ""),
                    "v1_secondary": mapping["secondary_paths"],
                    "candidate_kind": row["v2_kind_ja"],
                    "candidate_body_sites": row["v2_body_sites_ja"],
                    "candidate_themes": row["v2_themes_ja"],
                    "review_class": " | ".join(review_classes),
                    "severity": severity,
                    "review_note": review_note or mapping["ambiguity_note"],
                }
            )

    _write_csv(output_dir / "issue76_v2_candidate_mapping_v0_2.csv", MAPPING_FIELDS, candidate_rows)
    _write_csv(output_dir / "issue76_v2_review_queue_v0_2.csv", REVIEW_FIELDS, review_rows)

    kind_counts = Counter(row["v2_kind_ja"] or "REVIEW_REQUIRED" for row in candidate_rows)
    body_counts = Counter(
        item
        for row in candidate_rows
        for item in row["v2_body_sites_ja"].split(" | ")
        if item
    )
    theme_counts = Counter(
        item
        for row in candidate_rows
        for item in row["v2_themes_ja"].split(" | ")
        if item
    )
    body_multiplicity = Counter(
        len([item for item in row["v2_body_sites"].split(" | ") if item])
        for row in candidate_rows
    )
    theme_multiplicity = Counter(
        len([item for item in row["v2_themes"].split(" | ") if item])
        for row in candidate_rows
    )
    combined_multiplicity = Counter(
        len([item for item in row["v2_body_sites"].split(" | ") if item])
        + len([item for item in row["v2_themes"].split(" | ") if item])
        for row in candidate_rows
    )
    status_counts = Counter(row["v2_status"] for row in candidate_rows)
    review_class_counts: Counter[str] = Counter()
    for row in review_rows:
        for item in row["review_class"].split(" | "):
            review_class_counts[item] += 1

    meta = {
        "version": VERSION,
        "source": "Issue #56 accepted full browse mapping",
        "source_total": len(candidate_rows),
        "source_hashes": source_hashes,
        "kind_counts": dict(kind_counts),
        "body_site_counts": dict(body_counts),
        "theme_counts": dict(theme_counts),
        "body_site_multiplicity": {str(k): v for k, v in sorted(body_multiplicity.items())},
        "theme_multiplicity": {str(k): v for k, v in sorted(theme_multiplicity.items())},
        "combined_facet_multiplicity": {str(k): v for k, v in sorted(combined_multiplicity.items())},
        "candidate_status_counts": dict(status_counts),
        "review_queue_rows": len(review_rows),
        "review_class_counts": dict(review_class_counts),
        "notes": [
            "Facet counts are route-derived from accepted v1 primary/secondary paths and therefore conservative.",
            "No canonical Special identity is changed.",
            "BUTTOCK_ANUS-derived rows are flagged for dedicated site naming/split audit.",
            "CHASTITY_CONTROL is kept provisional because it mixes device/state/control concepts.",
            "43 v1 REVIEW_REQUIRED rows remain fail-closed.",
        ],
    }
    (output_dir / "issue76_v2_candidate_meta_v0_2.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return meta


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    meta = build_candidate(args.output_dir)
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
