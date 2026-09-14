#!/usr/bin/env python3
"""Build the explicit, provenance-preserving Issue #64 effective sidecar."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:  # Supports both `python tools/script.py` and pytest namespace imports.
    from issue64_full_rollout_validate import (
        FULL_ROOT,
        MANIFEST_PATH,
        POPULATION_PATH,
        TAXONOMY_PATH,
        _ledger_bytes,
        _read_json,
        _taxonomy_path_error,
        canonicalize_path,
        normalize_row,
        sha256,
    )
except ModuleNotFoundError:  # pragma: no cover - exercised by pytest import mode
    from tools.issue64_full_rollout_validate import (
        FULL_ROOT,
        MANIFEST_PATH,
        POPULATION_PATH,
        TAXONOMY_PATH,
        _ledger_bytes,
        _read_json,
        _taxonomy_path_error,
        canonicalize_path,
        normalize_row,
        sha256,
    )


REWORK_ROOT = FULL_ROOT / "corrections"
RECOVERY_PATH = REWORK_ROOT / "recovery_batch009_17.csv"
EFFECTIVE_PATH = FULL_ROOT / "effective_sidecar.csv"
CORRECTION_MANIFEST_PATH = REWORK_ROOT / "CORRECTION_MANIFEST.json"
EFFECTIVE_SUMMARIES_PATH = REWORK_ROOT / "effective_batch_summaries.json"
PATH_CORRECTIONS_PATH = REWORK_ROOT / "batch034_path_corrections.csv"
SEMANTIC_CORRECTIONS_PATH = REWORK_ROOT / "semantic_corrections.csv"
HASH_PROVENANCE_PATH = REWORK_ROOT / "hash_provenance.json"
RESIDUAL_REVIEW_PATH = REWORK_ROOT / "residual_candidate_review.csv"


# Only direct semantic equivalents enter a pilot-v2 subgenre. Other rejected
# subgenres fall back to their already accepted parent genre, preserving the
# broad browse route without inventing a taxonomy node.
SUBGENRE_ALIASES = {
    ("LIVING_NATURE", "ANIMAL"): "CREATURE",
    ("CLOTHING", "ACCESSORIES"): "ACCESSORY",
    ("CLOTHING", "HAIR_ORNAMENT"): "ACCESSORY",
    ("CLOTHING", "UNDERWEAR"): "EVERYDAY",
    ("CLOTHING", "OUTERWEAR"): "EVERYDAY",
    ("CLOTHING", "TOPS"): "EVERYDAY",
    ("CLOTHING", "BOTTOMS"): "EVERYDAY",
    ("CLOTHING", "FOOTWEAR"): "EVERYDAY",
    ("CLOTHING", "HEADWEAR"): "EVERYDAY",
    ("CLOTHING", "LEGWEAR"): "EVERYDAY",
    ("OBJECT_PROP", "FURNITURE_OBJECT"): "DAILY",
    ("ACTION_CONTACT", "HOLDING_CARRYING"): "OBJECT_USE",
    ("ACTION_CONTACT", "CONTACT"): "INTERACTION",
}


SEMANTIC_CORRECTIONS: dict[str, dict[str, Any]] = {
    "smoking_pipe_in_mouth": {
        "path": ("ACTION_CONTACT", "OBJECT_USE"),
        "confidence": "MEDIUM",
        "reason": "口にくわえたパイプを使う行為・物との関係を主経路にする。",
        "evidence_url": "",
        "review_note": "Luna risk audit: object/contact boundary; BODY_PART is incidental.",
    },
    "pink_nails": {
        "path": ("BODY_PART", None),
        "confidence": "HIGH",
        "reason": "爪という身体部位の色を表すため身体・部位から探す。",
        "evidence_url": "https://safebooru.donmai.us/wiki_pages/pink_nails",
        "review_note": "Wiki defines colored fingernails/toenails; HAIR_FACE is outside the tag identity.",
    },
    "cropped_head": {
        "path": ("COMPOSITION_CAMERA", None),
        "confidence": "HIGH",
        "reason": "頭部が画面内で切られる構図・フレーミングを表すため構図から探す。",
        "evidence_url": "https://safebooru.donmai.us/posts?page=12&tags=cropped_torso",
        "review_note": "Danbooru cropped-torso wiki defines an in-image crop and links cropped_head under Image composition.",
    },
    "cropped_arm": {
        "path": ("COMPOSITION_CAMERA", None),
        "confidence": "MEDIUM",
        "reason": "腕が画面内で切られる構図を表すため構図から探す。",
        "evidence_url": "https://safebooru.donmai.us/posts?page=12&tags=cropped_torso",
        "review_note": "Singular variant of the cropped-body-part framing family; corroborated by the official cropped-torso tag family.",
    },
    "cropped_arms": {
        "path": ("COMPOSITION_CAMERA", None),
        "confidence": "HIGH",
        "reason": "腕が画面内で切られる構図・フレーミングを表すため構図から探す。",
        "evidence_url": "https://safebooru.donmai.us/posts?page=12&tags=cropped_torso",
        "review_note": "Danbooru cropped-torso wiki lists cropped_arms and links the family to Image composition.",
    },
    "cropped_legs": {
        "path": ("COMPOSITION_CAMERA", None),
        "confidence": "HIGH",
        "reason": "脚が画面内で切られる構図・フレーミングを表すため構図から探す。",
        "evidence_url": "https://safebooru.donmai.us/posts?page=12&tags=cropped_torso",
        "review_note": "Danbooru cropped-torso wiki lists cropped_legs and links the family to Image composition.",
    },
    "cropped_shoulders": {
        "path": ("COMPOSITION_CAMERA", None),
        "confidence": "HIGH",
        "reason": "肩から上で切り取る構図・フレーミングを表すため構図から探す。",
        "evidence_url": "https://safebooru.donmai.us/posts?page=12&tags=cropped_torso",
        "review_note": "Danbooru cropped-torso wiki distinguishes cropped_shoulders as an image crop and links the family to Image composition.",
    },
    "cropped_torso": {
        "path": ("COMPOSITION_CAMERA", None),
        "confidence": "HIGH",
        "reason": "胴体を画像内で切り取る構図・フレーミングを表すため構図から探す。",
        "evidence_url": "https://safebooru.donmai.us/posts?page=12&tags=cropped_torso",
        "review_note": "Danbooru wiki defines this as a character cropped within the image and links it to Image composition.",
    },
    "orange_nails": {
        "path": ("BODY_PART", None),
        "confidence": "HIGH",
        "reason": "爪という身体部位の色を表すため身体・部位から探す。",
        "evidence_url": "https://safebooru.donmai.us/wiki_pages/pink_nails",
        "review_note": "Analogous nail-color tag; same body-part identity as pink_nails.",
    },
    "red_nails": {
        "path": ("BODY_PART", None),
        "confidence": "HIGH",
        "reason": "爪という身体部位の色を表すため身体・部位から探す。",
        "evidence_url": "https://safebooru.donmai.us/wiki_pages/pink_nails",
        "review_note": "Analogous nail-color tag; same body-part identity as pink_nails.",
    },
    "standing_on_chair": {
        "path": ("ACTION_CONTACT", "INTERACTION"),
        "confidence": "MEDIUM",
        "reason": "椅子との接触関係を含むため、姿勢単独でなく行為・接触から探す。",
        "evidence_url": "",
        "review_note": "Pilot boundary sends posture involving contact with an object to ACTION_CONTACT.",
    },
    "sitting_on_creature": {
        "path": ("ACTION_CONTACT", "INTERACTION"),
        "confidence": "MEDIUM",
        "reason": "生き物の上に座る対象間の関係を主経路にする。",
        "evidence_url": "",
        "review_note": "Pilot boundary: contact with another entity takes precedence over pose-only routing.",
    },
    "sarcophagus": {
        "path": ("OBJECT_PROP", None),
        "confidence": "HIGH",
        "reason": "石棺という具体的な物品identityを主経路にする。",
        "evidence_url": "",
        "review_note": "Object identity is clearer than a place/background route; no new related graph added.",
    },
    "beer_can": {
        "path": ("OBJECT_PROP", "DAILY"),
        "confidence": "MEDIUM",
        "reason": "ビール入り飲料缶という容器・小物identityを主経路にする。",
        "evidence_url": "https://safebooru.donmai.us/wiki_pages/beer_can",
        "review_note": "Tag wiki defines an aluminum drink can containing beer and implicates drink_can.",
    },
    "studio_microphone": {
        "path": ("OBJECT_PROP", "DAILY"),
        "confidence": "HIGH",
        "reason": "録音ブースで使うマイク機材という具体的な物品から探す。",
        "evidence_url": "https://shima.donmai.us/wiki_pages/studio_microphone?z=1",
        "review_note": "Danbooru wiki defines studio microphones as recording equipment and the technology group lists them under microphones.",
    },
    "vocaloid_boxart_pose": {
        "path": ("POSE_MOVEMENT", None),
        "confidence": "HIGH",
        "reason": "Vocaloidなどの箱絵に使われるポーズを表すためポーズから探す。",
        "evidence_url": "https://safebooru.donmai.us/posts?page=14&tags=vocaloid_boxart_pose",
        "review_note": "Danbooru wiki defines the tag by the character pose used for Vocaloid or vocal-synth box art.",
    },
    "optical_camouflage": {
        "path": ("STYLE_QUALITY_META", None),
        "confidence": "MEDIUM",
        "reason": "背景投影による不可視化という視覚効果を画面表現から探す。",
        "evidence_url": "https://safebooru.donmai.us/wiki_pages/optical_camouflage",
        "review_note": "Tag wiki describes a visual concealment effect, not text or a symbol.",
    },
    "waiter": {
        "path": ("PERSON_COUNT", None),
        "confidence": "HIGH",
        "reason": "飲食店の職業・役柄を人物の種類から探す。",
        "evidence_url": "https://safebooru.donmai.us/wiki_pages/waiter",
        "review_note": "Luna risk audit: clear role/person candidate.",
    },
    "umpire": {
        "path": ("PERSON_COUNT", None),
        "confidence": "MEDIUM",
        "reason": "審判という人物の役割を人物の種類から探す。",
        "evidence_url": "",
        "review_note": "Occupation/role tag; accepted PERSON_COUNT route includes roles.",
    },
    "veterinarian": {
        "path": ("PERSON_COUNT", None),
        "confidence": "MEDIUM",
        "reason": "獣医師という人物の職業を人物の種類から探す。",
        "evidence_url": "",
        "review_note": "Occupation/role tag; accepted PERSON_COUNT route includes roles.",
    },
    "warrior": {
        "path": ("PERSON_COUNT", None),
        "confidence": "MEDIUM",
        "reason": "戦士という人物の役柄を人物の種類から探す。",
        "evidence_url": "",
        "review_note": "Role tag; accepted PERSON_COUNT route includes roles.",
    },
    "witch": {
        "path": ("PERSON_COUNT", None),
        "confidence": "MEDIUM",
        "reason": "魔女という人物の役柄を人物の種類から探す。",
        "evidence_url": "",
        "review_note": "Role tag; kept at top level because taxonomy has no role subgenre.",
    },
    "wizard": {
        "path": ("PERSON_COUNT", None),
        "confidence": "MEDIUM",
        "reason": "魔法使いという人物の役柄を人物の種類から探す。",
        "evidence_url": "",
        "review_note": "Role tag; kept at top level because taxonomy has no role subgenre.",
    },
    "seiza": {
        "path": ("POSE_MOVEMENT", None),
        "confidence": "MEDIUM",
        "reason": "正座という座り方・姿勢をポーズから探す。",
        "evidence_url": "",
        "review_note": "Luna risk audit: common sitting posture candidate.",
    },
}


def _path_text(path: tuple[str, str | None] | None) -> str:
    if not path:
        return ""
    return f"{path[0]}/{path[1]}" if path[1] else path[0]


def _correct_path(path: tuple[str, str | None] | None, taxonomy: dict[str, Any]) -> tuple[tuple[str, str | None] | None, str]:
    if path is None:
        return None, ""
    normalized = canonicalize_path(path, taxonomy)
    if _taxonomy_path_error(normalized, taxonomy) is None:
        if normalized != path:
            return normalized, "canonical_id_case"
        return normalized, ""
    genre, subgenre = normalized
    if genre not in taxonomy.get("genres", {}):
        raise ValueError(f"cannot correct unknown genre {genre!r} without a reviewed mapping")
    alias = SUBGENRE_ALIASES.get((genre, subgenre or ""))
    if alias:
        candidate = (genre, alias)
        if _taxonomy_path_error(candidate, taxonomy):
            raise ValueError(f"invalid explicit alias mapping {normalized!r} -> {candidate!r}")
        return candidate, f"explicit_alias:{subgenre}->{alias}"
    # The source subgenre is not in accepted pilot-v2. Retain its valid parent
    # route rather than inventing a node or forcing it into a nearby bucket.
    return (genre, None), f"top_level_fallback:{subgenre}"


def _load_source_rows(root: Path, manifest: dict[str, Any], population: list[str], taxonomy: dict[str, Any]):
    records: dict[str, list[dict[str, Any]]] = defaultdict(list)
    population_set = set(population)
    unreadable: list[dict[str, Any]] = []
    path_corrections: list[dict[str, str]] = []
    batch_errors: dict[int, str] = {}
    for batch in manifest["batches"]:
        number = int(batch["batch"])
        start, end = map(int, batch["range"])
        try:
            _, raw, decode_issues = _ledger_bytes(root, batch)
            rows = list(csv.DictReader(raw.decode("utf-8-sig").splitlines()))
            if decode_issues:
                batch_errors[number] = "; ".join(decode_issues)
            for offset, raw_row in enumerate(rows):
                record = normalize_row(raw_row, start + offset, taxonomy)
                source_global = record["global_row"]
                canonical = record["canonical"]
                if not canonical:
                    raise ValueError(f"batch {number} row {offset + 1}: empty canonical")
                if canonical not in population_set:
                    raise ValueError(f"batch {number}: canonical outside target population: {canonical}")
                record.update({
                    "source_batch": number,
                    "source_global_row": source_global,
                    "source_correction_ids": [],
                    "reason": raw_row.get("reason_ja") or raw_row.get("classification_reason") or "",
                })

                original_primary = record["primary_path"]
                fixed_primary, primary_rule = _correct_path(original_primary, taxonomy)
                original_secondary = list(record["secondary_paths"])
                fixed_secondary: list[tuple[str, str | None]] = []
                secondary_rules = []
                for secondary_path in original_secondary:
                    fixed_path, rule = _correct_path(secondary_path, taxonomy)
                    if fixed_path:
                        fixed_secondary.append(fixed_path)
                    if rule:
                        secondary_rules.append(rule)
                if fixed_primary != original_primary or fixed_secondary != original_secondary:
                    record["primary_path"] = fixed_primary
                    record["secondary_paths"] = fixed_secondary
                    record["source_correction_ids"].append("BATCH034_PATH_REMAP" if number == 34 else "ACCEPTED_PATH_NORMALIZATION")
                    path_corrections.append({
                        "canonical": canonical,
                        "source_batch": str(number),
                        "source_global_row": str(source_global),
                        "old_primary_path": _path_text(original_primary),
                        "new_primary_path": _path_text(fixed_primary),
                        "old_secondary_paths": json.dumps([_path_text(x) for x in original_secondary], ensure_ascii=False),
                        "new_secondary_paths": json.dumps([_path_text(x) for x in fixed_secondary], ensure_ascii=False),
                        "rule": ";".join(([primary_rule] if primary_rule else []) + secondary_rules),
                    })
                records[canonical].append(record)
        except Exception as exc:
            unreadable.append({"batch": number, "range": [start, end], "error": f"{type(exc).__name__}: {exc}"})
    return records, unreadable, path_corrections, batch_errors


def _load_recovery_rows(root: Path, taxonomy: dict[str, Any]) -> dict[int, dict[str, Any]]:
    path = root / RECOVERY_PATH
    if not path.is_file():
        raise FileNotFoundError(f"bounded recovery review is required: {path}")
    recovered: dict[int, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        for raw in csv.DictReader(stream):
            row = normalize_row(raw, int(raw["global_row"]), taxonomy)
            global_row = row["global_row"]
            if global_row in recovered:
                raise ValueError(f"duplicate recovery global_row {global_row}")
            row.update({
                "source_batch": 9 if 5701 <= global_row <= 5900 else 17,
                "source_global_row": global_row,
                "source_correction_ids": ["BATCH009_017_CORRUPTION_REVIEW"],
                "reason": raw.get("reason_ja") or "",
            })
            recovered[global_row] = row
    expected_rows = set(range(5701, 5901)) | set(range(12151, 13151))
    if set(recovered) != expected_rows:
        raise ValueError(
            f"recovery rows do not cover the exact 1,200-row scope: "
            f"missing={sorted(expected_rows - set(recovered))[:20]}, extra={sorted(set(recovered) - expected_rows)[:20]}"
        )
    return recovered


def _recovery_edge_rows(population: list[str]) -> dict[int, dict[str, Any]]:
    # Batch 8's two-row offset leaves these two population entries uncovered.
    edge = {
        5699: ("OBJECT_PROP", None, "MEDIUM", "コンピューター本体という物品identityを道具・小物から探す。"),
        5700: ("OBJECT_PROP", None, "MEDIUM", "コンピューター部品という物品identityを道具・小物から探す。"),
    }
    expected = {5699: "computer", 5700: "computer_chip"}
    result = {}
    for row_id, (genre, subgenre, confidence, reason) in edge.items():
        canonical = population[row_id - 1]
        if canonical != expected[row_id]:
            raise ValueError(f"population edge changed: row {row_id} is {canonical!r}")
        result[row_id] = {
            "global_row": row_id,
            "canonical": canonical,
            "status": "PROPOSED",
            "primary_path": (genre, subgenre),
            "secondary_paths": [],
            "confidence": confidence,
            "source_batch": 8,
            "source_global_row": None,
            "source_correction_ids": ["BATCH008_EDGE_RECOVERY"],
            "reason": reason,
        }
    return result


def _apply_semantic_corrections(rows: dict[str, dict[str, Any]], taxonomy: dict[str, Any]) -> list[dict[str, str]]:
    changes: list[dict[str, str]] = []
    for canonical, change in SEMANTIC_CORRECTIONS.items():
        if canonical not in rows:
            continue
        row = rows[canonical]
        new_path = change["path"]
        if _taxonomy_path_error(new_path, taxonomy):
            raise ValueError(f"semantic correction path is invalid for {canonical}: {new_path}")
        old_status = row["status"]
        old_path = row["primary_path"]
        old_confidence = row["confidence"]
        row.update({
            "status": "PROPOSED",
            "primary_path": new_path,
            "secondary_paths": [],
            "confidence": change["confidence"],
            "reason": change["reason"],
            "evidence_url": change["evidence_url"],
        })
        row["source_correction_ids"].append(f"SEMANTIC_{canonical.upper()}")
        changes.append({
            "canonical": canonical,
            "old_status": old_status,
            "old_path": _path_text(old_path),
            "old_confidence": old_confidence,
            "new_status": "PROPOSED",
            "new_path": _path_text(new_path),
            "new_confidence": change["confidence"],
            "reason_ja": change["reason"],
            "evidence_url": change["evidence_url"],
            "review_note": change["review_note"],
        })

    # The targeted boundary scan found a consistent pattern family: *_on_*
    # relation tags routed to posture/appearance even though pilot-v2 assigns
    # object/other-entity contact to ACTION_CONTACT. Keep pure body-posture
    # forms such as standing_on_one_leg in POSE_MOVEMENT.
    pure_posture_suffixes = {"one_leg", "three_legs", "tiptoes", "toes", "heels"}
    relation_pattern = re.compile(r"^(?:standing|sitting|kneeling|lying|crouching)_on_(.+)$")
    already_changed = {item["canonical"] for item in changes}
    for canonical, row in sorted(rows.items()):
        if canonical in already_changed or row["status"] != "PROPOSED":
            continue
        match = relation_pattern.match(canonical)
        if not match or match.group(1) in pure_posture_suffixes:
            continue
        path = row["primary_path"]
        if not path or path[0] not in {"POSE_MOVEMENT", "HAIR_FACE"}:
            continue
        new_path = ("ACTION_CONTACT", "INTERACTION")
        if _taxonomy_path_error(new_path, taxonomy):
            raise ValueError(f"relation-family correction path is invalid for {canonical}")
        old_path, old_confidence = path, row["confidence"]
        row.update({
            "primary_path": new_path,
            "secondary_paths": [],
            "confidence": "MEDIUM",
            "reason": "対象となる人・生き物・物との接触関係を行為・接触から探す。",
        })
        row["source_correction_ids"].append("SEMANTIC_RELATIONAL_ON_CONTACT")
        changes.append({
            "canonical": canonical,
            "old_status": "PROPOSED",
            "old_path": _path_text(old_path),
            "old_confidence": old_confidence,
            "new_status": "PROPOSED",
            "new_path": _path_text(new_path),
            "new_confidence": "MEDIUM",
            "reason_ja": row["reason"],
            "evidence_url": "",
            "review_note": "Deterministic analogue rule: relational contact with another entity/object; pure body-posture suffixes are excluded.",
        })
    return changes


def _apply_residual_candidate_review(
    rows: dict[str, dict[str, Any]], taxonomy: dict[str, Any], root: Path
) -> dict[str, Any]:
    """Apply only the explicit residual review list, failing closed on drift."""
    path = root / RESIDUAL_REVIEW_PATH
    if not path.is_file():
        raise FileNotFoundError(f"bounded residual candidate review is required: {path}")

    reviewed: set[str] = set()
    families: Counter[str] = Counter()
    dispositions: Counter[str] = Counter()
    changed: list[dict[str, str]] = []

    def parse_review_path(value: str) -> tuple[str, str | None] | None:
        if not value:
            return None
        parts = value.split("/")
        if len(parts) == 1:
            return parts[0], None
        if len(parts) == 2:
            return parts[0], parts[1]
        raise ValueError(f"residual review path has invalid depth: {value!r}")

    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        for review in csv.DictReader(stream):
            canonical = review["canonical"]
            if canonical in reviewed:
                raise ValueError(f"duplicate residual candidate: {canonical}")
            if canonical not in rows:
                raise ValueError(f"residual candidate is outside effective population: {canonical}")
            reviewed.add(canonical)
            families[review["candidate_family"]] += 1

            row = rows[canonical]
            expected = (
                review["expected_status"],
                review["expected_path"],
                review["expected_confidence"],
            )
            actual = (row["status"], _path_text(row["primary_path"]), row["confidence"])
            if actual != expected:
                raise ValueError(f"residual candidate baseline drift for {canonical}: {actual!r} != {expected!r}")

            disposition = review["disposition"]
            dispositions[disposition] += 1
            new_status = review["new_status"]
            new_path = parse_review_path(review["new_path"])
            new_confidence = review["new_confidence"]
            if disposition == "KEEP":
                if (new_status, _path_text(new_path), new_confidence) != actual:
                    raise ValueError(f"KEEP candidate attempts to change output: {canonical}")
                continue

            if disposition == "UNRESOLVED":
                if new_status != "UNRESOLVED" or new_path is not None or new_confidence != "LOW":
                    raise ValueError(f"invalid UNRESOLVED residual decision for {canonical}")
            elif disposition == "RECLASSIFY":
                if new_status != "PROPOSED" or new_path is None or new_confidence not in {"HIGH", "MEDIUM"}:
                    raise ValueError(f"invalid RECLASSIFY residual decision for {canonical}")
                error = _taxonomy_path_error(new_path, taxonomy)
                if error:
                    raise ValueError(f"residual review path for {canonical} is invalid: {error}")
            else:
                raise ValueError(f"unknown residual review disposition {disposition!r}")

            old_status, old_path, old_confidence = actual
            row.update({
                "status": new_status,
                "primary_path": new_path,
                "secondary_paths": [],
                "confidence": new_confidence,
                "reason": review["reason_ja"],
                "evidence_url": review["evidence_url"],
            })
            row["source_correction_ids"].append("SEMANTIC_RESIDUAL_REVIEW")
            changed.append({
                "canonical": canonical,
                "old_status": old_status,
                "old_path": old_path,
                "old_confidence": old_confidence,
                "new_status": new_status,
                "new_path": _path_text(new_path),
                "new_confidence": new_confidence,
                "reason_ja": review["reason_ja"],
                "evidence_url": review["evidence_url"],
                "review_note": review["review_note"],
            })

    if len(reviewed) != 76:
        raise ValueError(f"residual review must contain the fixed 76-row bounded set, got {len(reviewed)}")
    return {
        "path": str(RESIDUAL_REVIEW_PATH).replace("\\", "/"),
        "rows": len(reviewed),
        "sha256": sha256(path.read_bytes()),
        "families": dict(sorted(families.items())),
        "dispositions": dict(sorted(dispositions.items())),
        "changed_rows": changed,
        "scope_note": "Exact residual families from the fresh Luna review notes, materialized by canonical identity: reviewed relation/contact correction rows, Batch 34 water-prefixed rows, two named time/event candidates, and the named modifier+object candidate. No population-wide semantic rescan.",
    }


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build(root: Path) -> dict[str, Any]:
    manifest = _read_json(root / MANIFEST_PATH)
    taxonomy = _read_json(root / TAXONOMY_PATH)
    population_bytes = (root / POPULATION_PATH).read_bytes()
    population = population_bytes.decode("utf-8-sig").splitlines()
    if len(population) != int(manifest["population_count"]) or len(set(population)) != len(population):
        raise ValueError("fixed population is not exactly the declared unique target population")

    source_records, unreadable, path_corrections, source_batch_errors = _load_source_rows(
        root, manifest, population, taxonomy
    )
    recovery = _load_recovery_rows(root, taxonomy)
    edge_recovery = _recovery_edge_rows(population)

    effective_by_canonical: dict[str, dict[str, Any]] = {}
    dropped_duplicates: list[dict[str, Any]] = []
    index_remaps: list[dict[str, Any]] = []
    for global_row, canonical in enumerate(population, start=1):
        candidate_records = source_records.get(canonical, [])
        if candidate_records:
            candidate_records = sorted(
                candidate_records,
                key=lambda item: (abs(int(item["source_global_row"]) - global_row), int(item["source_batch"])),
            )
            selected = dict(candidate_records[0])
            if len(candidate_records) > 1:
                for discarded in candidate_records[1:]:
                    if (
                        discarded["status"], discarded["primary_path"], discarded["secondary_paths"], discarded["confidence"]
                    ) != (
                        selected["status"], selected["primary_path"], selected["secondary_paths"], selected["confidence"]
                    ):
                        raise ValueError(f"duplicate ledger decision conflicts for {canonical}: {candidate_records}")
                    dropped_duplicates.append({
                        "canonical": canonical,
                        "selected_batch": selected["source_batch"],
                        "selected_global_row": selected["source_global_row"],
                        "discarded_batch": discarded["source_batch"],
                        "discarded_global_row": discarded["source_global_row"],
                        "reason": "duplicate canonical row; selected source row nearest to the fixed population index",
                    })
            selected["global_row"] = global_row
            if int(selected["source_global_row"]) != global_row:
                selected["source_correction_ids"].append("BATCH008_CANONICAL_REINDEX")
                index_remaps.append({
                    "canonical": canonical,
                    "source_batch": selected["source_batch"],
                    "source_global_row": selected["source_global_row"],
                    "effective_global_row": global_row,
                })
            effective_by_canonical[canonical] = selected
        elif global_row in recovery:
            row = dict(recovery[global_row])
            if row["canonical"] != canonical:
                raise ValueError(f"recovery canonical at row {global_row} is {row['canonical']!r}, expected {canonical!r}")
            effective_by_canonical[canonical] = row
        elif global_row in edge_recovery:
            row = dict(edge_recovery[global_row])
            if row["canonical"] != canonical:
                raise ValueError(f"edge recovery canonical mismatch at row {global_row}")
            effective_by_canonical[canonical] = row
        else:
            raise ValueError(f"no source or bounded recovery row for global row {global_row}: {canonical}")

    if set(effective_by_canonical) != set(population):
        raise ValueError("effective row membership differs from the fixed population")
    semantic_corrections = _apply_semantic_corrections(effective_by_canonical, taxonomy)
    residual_review = _apply_residual_candidate_review(effective_by_canonical, taxonomy, root)
    semantic_corrections.extend(residual_review["changed_rows"])

    # Ensure every effective row is in the accepted schema and has no invalid
    # paths before writing any output.
    for global_row, canonical in enumerate(population, start=1):
        row = effective_by_canonical[canonical]
        if row["global_row"] != global_row:
            raise ValueError(f"effective global row mismatch for {canonical}")
        if row["status"] == "UNRESOLVED":
            if row["confidence"] != "LOW" or row["primary_path"] or row["secondary_paths"]:
                raise ValueError(f"unresolved row violates invariants: {canonical}")
        elif row["status"] == "PROPOSED":
            if row["confidence"] not in {"HIGH", "MEDIUM"} or not row["primary_path"]:
                raise ValueError(f"proposed row violates invariants: {canonical}")
        else:
            raise ValueError(f"invalid status for {canonical}: {row['status']}")
        for path in ([row["primary_path"]] if row["primary_path"] else []) + row["secondary_paths"]:
            error = _taxonomy_path_error(path, taxonomy)
            if error:
                raise ValueError(f"effective taxonomy path for {canonical} is invalid: {error}")

    effective_rows = []
    batch_ranges = [(int(x["batch"]), *map(int, x["range"])) for x in manifest["batches"]]
    batch_summaries: dict[str, Any] = {}
    summary_rows: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for global_row, canonical in enumerate(population, start=1):
        row = effective_by_canonical[canonical]
        target_batch = next(batch_no for batch_no, start, end in batch_ranges if start <= global_row <= end)
        summary_rows[target_batch].append(row)
        path = _path_text(row["primary_path"])
        secondary = json.dumps([_path_text(item) for item in row["secondary_paths"]], separators=(",", ":"))
        effective_rows.append({
            "global_row": global_row,
            "canonical": canonical,
            "classification_status": row["status"],
            "primary_path": path,
            "secondary_paths": secondary,
            "confidence": row["confidence"],
            "classification_reason": row.get("reason", ""),
            "source_batch": row["source_batch"],
            "source_global_row": row.get("source_global_row", ""),
            "correction_ids": json.dumps(row.get("source_correction_ids", []), separators=(",", ":")),
        })

    effective_fields = [
        "global_row", "canonical", "classification_status", "primary_path", "secondary_paths",
        "confidence", "classification_reason", "source_batch", "source_global_row", "correction_ids",
    ]
    _write_csv(root / EFFECTIVE_PATH, effective_fields, effective_rows)
    effective_hash = sha256((root / EFFECTIVE_PATH).read_bytes())

    for batch_no, rows in sorted(summary_rows.items()):
        statuses = Counter(row["status"] for row in rows)
        confidences = Counter(row["confidence"] for row in rows)
        genres = Counter(row["primary_path"][0] for row in rows if row["primary_path"])
        batch_summaries[str(batch_no)] = {
            "range": [int(manifest["batches"][batch_no - 1]["range"][0]), int(manifest["batches"][batch_no - 1]["range"][1])],
            "count": len(rows),
            "status_counts": {key: statuses.get(key, 0) for key in ("PROPOSED", "UNRESOLVED")},
            "confidence_counts": {key: confidences.get(key, 0) for key in ("HIGH", "MEDIUM", "LOW")},
            "primary_genre_counts": dict(sorted(genres.items())),
            "unresolved": [row["canonical"] for row in rows if row["status"] == "UNRESOLVED"],
        }

    totals = {
        "PROPOSED": sum(1 for row in effective_rows if row["classification_status"] == "PROPOSED"),
        "UNRESOLVED": sum(1 for row in effective_rows if row["classification_status"] == "UNRESOLVED"),
        "HIGH": sum(1 for row in effective_rows if row["confidence"] == "HIGH"),
        "MEDIUM": sum(1 for row in effective_rows if row["confidence"] == "MEDIUM"),
        "LOW": sum(1 for row in effective_rows if row["confidence"] == "LOW"),
    }

    # Audit/review source-hash semantics without changing the protected inputs.
    repo_root = root.parent.parent
    source_csv = repo_root / "issue64_general_30629.csv"
    expected_working_hash = manifest.get("working_source_sha256")
    source_hash_result: dict[str, Any] = {
        "manifest_working_source_sha256": expected_working_hash,
        "population_sha256_sorted_utf8_lf": sha256(population_bytes),
        "working_source_semantics": "UTF-8-SIG CSV, sorted canonical rows with canonical/display_ja/search_ja/post_count columns, materialized from the Japanese overlay and usage snapshot",
        "population_semantics": "UTF-8/LF canonical-only sorted list; derived from the same target population, not byte-identical to the richer source CSV",
        "verification": "NOT_AVAILABLE",
    }
    if source_csv.is_file():
        raw = source_csv.read_bytes()
        actual_hash = sha256(raw)
        with source_csv.open("r", encoding="utf-8-sig", newline="") as stream:
            source_rows = list(csv.DictReader(stream))
        source_canonicals = [row.get("canonical", "") for row in source_rows]
        source_hash_result.update({
            "local_materialized_source_path": "issue64_general_30629.csv",
            "local_materialized_source_note": "Untracked local extraction used only to verify source hash and canonical membership; not included in this change.",
            "local_materialized_source_sha256": actual_hash,
            "local_materialized_source_rows": len(source_rows),
            "verification": "PASS" if actual_hash == expected_working_hash and source_canonicals == population else "FAIL",
        })
        if source_hash_result["verification"] != "PASS":
            raise ValueError("local working-source CSV does not match manifest hash and exact target population")
    _write_json(root / HASH_PROVENANCE_PATH, source_hash_result)

    recovery_raw_hash = sha256((root / RECOVERY_PATH).read_bytes())
    changed_path_rows = len({row["canonical"] for row in path_corrections})
    original_artifact_integrity = []
    for batch_no in (9, 17):
        batch = manifest["batches"][batch_no - 1]
        if "parts" in batch:
            for part in batch["parts"]:
                actual = sha256((root / part["path"]).read_bytes())
                original_artifact_integrity.append({
                    "batch": batch_no,
                    "path": part["path"],
                    "expected_base64_text_sha256": part.get("base64_text_sha256"),
                    "actual_base64_text_sha256": actual,
                    "status": "PASS" if actual == part.get("base64_text_sha256") else "RECOVERED_BY_SUPERSEDING_REVIEW",
                })
        else:
            actual = sha256((root / batch["path"]).read_bytes())
            original_artifact_integrity.append({
                "batch": batch_no,
                "path": batch["path"],
                "expected_xz_sha256": batch.get("xz_sha256"),
                "actual_file_sha256": actual,
                "status": "PASS" if actual == batch.get("xz_sha256") else "RECOVERED_BY_SUPERSEDING_REVIEW",
            })
    rework_manifest = {
        "format_version": 1,
        "candidate_base_commit": "7d15f856cdf6b1dab509b2bcb6706623eba968b0",
        "effective_population_count": len(effective_rows),
        "population_sha256_sorted_utf8_lf": sha256(population_bytes),
        "accepted_taxonomy": {
            "path": str(TAXONOMY_PATH).replace("\\", "/"),
            "version": taxonomy.get("version"),
            "sha256": sha256((root / TAXONOMY_PATH).read_bytes()),
        },
        "immutable_history_policy": "Historical batch ledgers and summaries remain unchanged; all fixes are superseding artifacts in corrections/ plus effective_sidecar.csv.",
        "unreadable_original_batches": unreadable,
        "original_artifact_integrity": original_artifact_integrity,
        "recovery_review": {
            "path": str(RECOVERY_PATH).replace("\\", "/"),
            "rows": 1200,
            "sha256": recovery_raw_hash,
            "scope": [[5701, 5900], [12151, 13150]],
            "method": "bounded row-by-row recovery review of only the two unrecoverable historical ledgers; no full-population LLM reread",
        },
        "batch008_repair": {
            "method": "canonical-key remap to exact population position; choose the duplicate decision whose source row is nearest that position; preserve raw source ledgers",
            "reindexed_rows": index_remaps,
            "duplicate_decisions_dropped": dropped_duplicates,
            "missing_edge_rows_recovered": [5699, 5700],
        },
        "batch016_summary_replacement": "effective_batch_summaries.json#16",
        "batch034_path_correction": {
            "corrected_rows": changed_path_rows,
            "distinct_source_path_rules": len({row["rule"] for row in path_corrections}),
            "direct_aliases": {
                f"{genre}/{subgenre}": alias
                for (genre, subgenre), alias in sorted(SUBGENRE_ALIASES.items())
            },
            "fallback": "When a subgenre is not in accepted pilot-v2 and has no direct alias, keep its accepted top-level genre only.",
        },
        "semantic_corrections": semantic_corrections,
        "residual_candidate_review": residual_review,
        "effective_sidecar": {
            "path": str(EFFECTIVE_PATH).replace("\\", "/"),
            "sha256": effective_hash,
            "counts": totals,
        },
        "effective_batch_summaries_path": str(EFFECTIVE_SUMMARIES_PATH).replace("\\", "/"),
        "source_hash_provenance_path": str(HASH_PROVENANCE_PATH).replace("\\", "/"),
        "source_hash_provenance": source_hash_result,
        "protected_data": "Read-only inputs; no canonical, overlay, Special, #64 production, or #66 files changed.",
    }

    _write_csv(root / PATH_CORRECTIONS_PATH, [
        "canonical", "source_batch", "source_global_row", "old_primary_path", "new_primary_path",
        "old_secondary_paths", "new_secondary_paths", "rule",
    ], path_corrections)
    _write_csv(root / SEMANTIC_CORRECTIONS_PATH, [
        "canonical", "old_status", "old_path", "old_confidence", "new_status", "new_path",
        "new_confidence", "reason_ja", "evidence_url", "review_note",
    ], semantic_corrections)
    _write_json(root / EFFECTIVE_SUMMARIES_PATH, {
        "format_version": 1,
        "sidecar_sha256": effective_hash,
        "population_sha256_sorted_utf8_lf": sha256(population_bytes),
        "totals": totals,
        "batches": batch_summaries,
    })
    _write_json(root / CORRECTION_MANIFEST_PATH, rework_manifest)
    return rework_manifest


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    result = build(root)
    sys.stdout.write(json.dumps({
        "effective_sidecar": result["effective_sidecar"],
        "recovery": result["recovery_review"],
        "batch008": {
            "reindexed_rows": len(result["batch008_repair"]["reindexed_rows"]),
            "duplicate_decisions_dropped": len(result["batch008_repair"]["duplicate_decisions_dropped"]),
            "missing_edge_rows_recovered": result["batch008_repair"]["missing_edge_rows_recovered"],
        },
        "batch034": result["batch034_path_correction"],
        "semantic_correction_count": len(result["semantic_corrections"]),
        "residual_candidate_review": {
            "rows": result["residual_candidate_review"]["rows"],
            "dispositions": result["residual_candidate_review"]["dispositions"],
            "changed_rows": [item["canonical"] for item in result["residual_candidate_review"]["changed_rows"]],
        },
        "source_hash_verification": result["source_hash_provenance"],
    }, ensure_ascii=False, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
