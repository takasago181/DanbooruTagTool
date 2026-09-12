#!/usr/bin/env python3
"""Validate and materialize Issue #56 full UI-taxonomy rollout state.

This tool never classifies a Special by keyword/category heuristic. It only:
- loads the frozen 2,788-row prompt-reference source;
- loads the frozen audited UI taxonomy;
- seeds the rollout with the audited 150-row Pilot map;
- merges explicitly reviewed rollout mapping fragments;
- validates browsing paths and safe Alias inheritance;
- materializes review queues and distribution metadata.

Canonical Special data is read-only.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

from tools.issue56_ui_genre_pilot_selector import (
    OTHER_PREFIX,
    PromptRow,
    build_tag_lookup,
    load_prompt_reference,
    resolve_alias_target,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "special2788" / "prompt_reference"
TAXONOMY_PATH = ROOT / "docs" / "issue56" / "rollout" / "issue56_ui_genre_taxonomy_v1.json"
PILOT_MAP_PATH = ROOT / "docs" / "issue56" / "pilot" / "issue56_ui_genre_pilot_v1_classification_map.csv"
REVIEWED_DIR = ROOT / "docs" / "issue56" / "rollout" / "reviewed"
DEFAULT_OUTPUT_DIR = ROOT / "docs" / "issue56" / "rollout" / "generated"

ALLOWED_STATUSES = {
    "HUMAN_REVIEWED",
    "AUTO_INHERITED_ALIAS",
    "REVIEW_REQUIRED",
    "AMBIGUOUS",
}

MAPPING_FIELDS = [
    "special_id",
    "primary_genre_id",
    "primary_subgenre_id",
    "secondary_paths",
    "classification_status",
    "classification_reason",
    "ambiguity_note",
]

QUEUE_FIELDS = [
    "source_file",
    "old_reference_row",
    "old_reference_category",
    "special_id",
    "japanese_display",
    "english_tag",
    "layer",
    "post_count",
    "canonical_target",
    "is_alias",
]


class RolloutError(ValueError):
    pass


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise RolloutError(f"{path}: missing header")
        missing = [field for field in MAPPING_FIELDS if field not in reader.fieldnames]
        if missing:
            raise RolloutError(f"{path}: missing mapping columns {missing}")
        return [{key: (value or "").strip() for key, value in row.items()} for row in reader]


def _write_csv(path: Path, fieldnames: Sequence[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _parse_path(path: str) -> tuple[str, str]:
    parts = path.split(">", 1)
    return parts[0].strip(), parts[1].strip() if len(parts) == 2 else ""


def _secondary_paths(value: str) -> list[str]:
    return [part.strip() for part in value.split("|") if part.strip()]


def _normalized_secondary(value: str) -> tuple[str, ...]:
    return tuple(_secondary_paths(value))


def load_taxonomy(path: Path = TAXONOMY_PATH) -> tuple[dict[str, object], dict[str, dict[str, object]], dict[str, set[str]]]:
    taxonomy = json.loads(path.read_text(encoding="utf-8"))
    genres_list = taxonomy.get("genres")
    if not isinstance(genres_list, list):
        raise RolloutError("taxonomy genres must be a list")

    genres: dict[str, dict[str, object]] = {}
    subgenres: dict[str, set[str]] = {}
    all_subgenre_ids: set[str] = set()
    for raw_genre in genres_list:
        if not isinstance(raw_genre, dict):
            raise RolloutError("taxonomy genre must be an object")
        genre_id = str(raw_genre.get("id", "")).strip()
        label_ja = str(raw_genre.get("label_ja", "")).strip()
        if not genre_id or genre_id in genres:
            raise RolloutError(f"invalid/duplicate genre id {genre_id!r}")
        if not label_ja:
            raise RolloutError(f"genre {genre_id} missing Japanese label")
        if genre_id.startswith("OTHER") or "その他" in label_ja:
            raise RolloutError(f"visible fallback genre is forbidden: {genre_id} / {label_ja}")
        genres[genre_id] = raw_genre

        children: set[str] = set()
        for raw_subgenre in raw_genre.get("subgenres", []):
            subgenre_id = str(raw_subgenre.get("id", "")).strip()
            subgenre_label = str(raw_subgenre.get("label_ja", "")).strip()
            if not subgenre_id or subgenre_id in children or subgenre_id in all_subgenre_ids:
                raise RolloutError(f"invalid/duplicate subgenre id {subgenre_id!r}")
            if not subgenre_label:
                raise RolloutError(f"subgenre {subgenre_id} missing Japanese label")
            if subgenre_id.startswith("OTHER") or "その他" in subgenre_label:
                raise RolloutError(
                    f"visible fallback subgenre is forbidden: {subgenre_id} / {subgenre_label}"
                )
            children.add(subgenre_id)
            all_subgenre_ids.add(subgenre_id)
        subgenres[genre_id] = children

    if len(genres) != 14:
        raise RolloutError(f"frozen taxonomy must contain 14 top-level genres, got {len(genres)}")
    if len(all_subgenre_ids) != 38:
        raise RolloutError(f"frozen taxonomy must contain 38 subgenres, got {len(all_subgenre_ids)}")
    return taxonomy, genres, subgenres


def validate_browse_path(path: str, genres: dict[str, dict[str, object]], subgenres: dict[str, set[str]]) -> None:
    genre_id, subgenre_id = _parse_path(path)
    if genre_id not in genres:
        raise RolloutError(f"unknown genre id {genre_id!r}")
    if subgenre_id and subgenre_id not in subgenres[genre_id]:
        raise RolloutError(f"unknown subgenre path {genre_id}>{subgenre_id}")


def load_mapping_fragments(reviewed_dir: Path = REVIEWED_DIR) -> list[tuple[Path, dict[str, str]]]:
    fragments: list[tuple[Path, dict[str, str]]] = []
    if not reviewed_dir.exists():
        return fragments
    for path in sorted(reviewed_dir.glob("*.csv")):
        for row in _read_csv(path):
            fragments.append((path, row))
    return fragments


def merge_mapping_sources(
    pilot_path: Path = PILOT_MAP_PATH,
    reviewed_dir: Path = REVIEWED_DIR,
) -> tuple[dict[int, dict[str, str]], dict[int, str]]:
    merged: dict[int, dict[str, str]] = {}
    origins: dict[int, str] = {}

    sources: list[tuple[Path, dict[str, str]]] = [(pilot_path, row) for row in _read_csv(pilot_path)]
    sources.extend(load_mapping_fragments(reviewed_dir))

    for path, row in sources:
        try:
            special_id = int(row["special_id"])
        except (TypeError, ValueError) as exc:
            raise RolloutError(f"{path}: invalid special_id {row.get('special_id')!r}") from exc
        if special_id in merged:
            raise RolloutError(
                f"duplicate reviewed mapping for Special ID {special_id}: {origins[special_id]} and {path}"
            )
        merged[special_id] = {field: row.get(field, "").strip() for field in MAPPING_FIELDS}
        origins[special_id] = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    return merged, origins


def validate_mapping(
    rows: Sequence[PromptRow],
    mappings: dict[int, dict[str, str]],
    genres: dict[str, dict[str, object]],
    subgenres: dict[str, set[str]],
    *,
    require_complete: bool = False,
) -> dict[str, object]:
    source_by_id = {row.special_id: row for row in rows}
    lookup = build_tag_lookup(rows)
    source_ids = set(source_by_id)
    mapping_ids = set(mappings)

    unknown_ids = sorted(mapping_ids - source_ids)
    if unknown_ids:
        raise RolloutError(f"reviewed mapping contains unknown Special IDs: {unknown_ids[:20]}")

    missing_ids = sorted(source_ids - mapping_ids)
    if require_complete and missing_ids:
        raise RolloutError(f"complete rollout required but {len(missing_ids)} Special IDs are unmapped")

    alias_pending: list[int] = []
    status_counts: Counter[str] = Counter()
    genre_counts: Counter[str] = Counter()
    subgenre_counts: Counter[str] = Counter()
    secondary_count_distribution: Counter[int] = Counter()

    for special_id, mapping in mappings.items():
        status = mapping["classification_status"]
        if status not in ALLOWED_STATUSES:
            raise RolloutError(f"Special ID {special_id}: invalid classification_status {status!r}")
        status_counts[status] += 1

        primary_genre = mapping["primary_genre_id"]
        primary_subgenre = mapping["primary_subgenre_id"]
        ambiguity_note = mapping["ambiguity_note"]
        unresolved = status in {"REVIEW_REQUIRED", "AMBIGUOUS"} and not primary_genre

        if unresolved:
            if primary_subgenre:
                raise RolloutError(f"Special ID {special_id}: unresolved row cannot have a subgenre")
            if not ambiguity_note:
                raise RolloutError(f"Special ID {special_id}: unresolved row requires ambiguity_note")
        else:
            if primary_genre not in genres:
                raise RolloutError(f"Special ID {special_id}: unknown primary genre {primary_genre!r}")
            if primary_subgenre and primary_subgenre not in subgenres[primary_genre]:
                raise RolloutError(
                    f"Special ID {special_id}: invalid primary subgenre {primary_genre}>{primary_subgenre}"
                )
            genre_counts[primary_genre] += 1
            if primary_subgenre:
                subgenre_counts[f"{primary_genre}>{primary_subgenre}"] += 1

        secondaries = _secondary_paths(mapping["secondary_paths"])
        if len(secondaries) != len(set(secondaries)):
            raise RolloutError(f"Special ID {special_id}: duplicate secondary path")
        primary_path = primary_genre + (f">{primary_subgenre}" if primary_subgenre else "")
        for secondary in secondaries:
            validate_browse_path(secondary, genres, subgenres)
            if primary_genre and secondary == primary_path:
                raise RolloutError(f"Special ID {special_id}: primary path duplicated as secondary")
        secondary_count_distribution[len(secondaries)] += 1

        if status == "AUTO_INHERITED_ALIAS":
            source = source_by_id[special_id]
            if not source.is_alias:
                raise RolloutError(f"Special ID {special_id}: AUTO_INHERITED_ALIAS but source layer is {source.layer}")
            target = resolve_alias_target(source, lookup)
            if target is None:
                raise RolloutError(f"Special ID {special_id}: Alias target does not resolve uniquely")
            target_mapping = mappings.get(target.special_id)
            if target_mapping is None:
                alias_pending.append(special_id)
            else:
                comparable = (
                    "primary_genre_id",
                    "primary_subgenre_id",
                )
                for field in comparable:
                    if mapping[field] != target_mapping[field]:
                        raise RolloutError(
                            f"Special ID {special_id}: Alias path differs from canonical ID {target.special_id} ({field})"
                        )
                if _normalized_secondary(mapping["secondary_paths"]) != _normalized_secondary(
                    target_mapping["secondary_paths"]
                ):
                    raise RolloutError(
                        f"Special ID {special_id}: Alias secondary paths differ from canonical ID {target.special_id}"
                    )

    if require_complete and alias_pending:
        raise RolloutError(
            f"complete rollout required but {len(alias_pending)} inherited Alias rows lack mapped canonical targets"
        )

    old_other_ids = {row.special_id for row in rows if row.source_file.startswith(OTHER_PREFIX)}
    old_other_mapped = old_other_ids & mapping_ids

    return {
        "source_total": len(rows),
        "mapped_total": len(mapping_ids),
        "unmapped_total": len(missing_ids),
        "old_other_total": len(old_other_ids),
        "old_other_mapped": len(old_other_mapped),
        "old_other_unmapped": len(old_other_ids - mapping_ids),
        "status_counts": dict(sorted(status_counts.items())),
        "genre_counts": dict(sorted(genre_counts.items())),
        "subgenre_counts": dict(sorted(subgenre_counts.items())),
        "secondary_path_count_distribution": {
            str(key): value for key, value in sorted(secondary_count_distribution.items())
        },
        "alias_inheritance_pending_canonical_mapping": sorted(alias_pending),
        "unmapped_ids": missing_ids,
    }


def queue_record(row: PromptRow) -> dict[str, object]:
    return {
        "source_file": row.source_file,
        "old_reference_row": row.old_reference_row,
        "old_reference_category": row.old_reference_category,
        "special_id": row.special_id,
        "japanese_display": row.japanese_display,
        "english_tag": row.english_tag,
        "layer": row.layer,
        "post_count": "" if row.post_count is None else row.post_count,
        "canonical_target": row.canonical_target,
        "is_alias": "true" if row.is_alias else "false",
    }


def build_outputs(output_dir: Path, *, require_complete: bool = False) -> dict[str, object]:
    rows, source_hashes = load_prompt_reference(SOURCE_DIR)
    if len(rows) != 2788 or {row.special_id for row in rows} != set(range(1, 2789)):
        raise RolloutError("prompt-reference source is not exact frozen 1..2788 coverage")

    taxonomy, genres, subgenres = load_taxonomy()
    mappings, origins = merge_mapping_sources()
    meta = validate_mapping(rows, mappings, genres, subgenres, require_complete=require_complete)

    source_by_id = {row.special_id: row for row in rows}
    old_other_unmapped = [
        row
        for row in rows
        if row.source_file.startswith(OTHER_PREFIX) and row.special_id not in mappings
    ]
    old_other_unmapped.sort(key=lambda row: (row.source_file, row.special_id))

    combined_rows = []
    for special_id in sorted(mappings):
        mapping = mappings[special_id]
        combined_rows.append({**mapping, "mapping_origin": origins[special_id]})

    combined_fields = MAPPING_FIELDS + ["mapping_origin"]
    _write_csv(output_dir / "issue56_ui_genre_mapping_partial_v1.csv", combined_fields, combined_rows)
    _write_csv(
        output_dir / "issue56_old_other_unmapped_v1.csv",
        QUEUE_FIELDS,
        (queue_record(row) for row in old_other_unmapped),
    )

    meta = {
        "version": "issue56-ui-rollout-v1",
        "taxonomy_version": taxonomy.get("version", ""),
        "source_hashes": source_hashes,
        **meta,
        "old_other_unmapped_ids": [row.special_id for row in old_other_unmapped],
        "pilot_seed_count": len(_read_csv(PILOT_MAP_PATH)),
        "review_fragment_files": [
            str(path.relative_to(ROOT)) for path in sorted(REVIEWED_DIR.glob("*.csv"))
        ] if REVIEWED_DIR.exists() else [],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "issue56_ui_genre_rollout_meta_v1.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return meta


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--require-complete", action="store_true")
    args = parser.parse_args()
    meta = build_outputs(args.output_dir, require_complete=args.require_complete)
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
