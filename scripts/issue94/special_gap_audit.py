#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import unicodedata
from collections import Counter
from pathlib import Path


CATEGORY_NAMES = {
    "0": "General",
    "1": "Artist",
    "3": "Copyright",
    "4": "Character",
    "5": "Meta",
}


def norm(value: object) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKC", text).strip().casefold().replace("_", " ")
    return " ".join(text.split())


def split_aliases(value: str) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def require_columns(rows: list[dict[str, str]], required: set[str], label: str) -> None:
    if not rows:
        raise ValueError(f"{label}: no rows")
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"{label}: missing columns {sorted(missing)}")


def as_int(value: str) -> int:
    text = (value or "").strip().replace(",", "")
    if not text:
        return 0
    return int(float(text))


def read_canonical_source(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for line_no, raw in enumerate(csv.reader(handle), start=1):
            if len(raw) != 4:
                raise ValueError(
                    f"canonical-source: expected headerless four-column rows; "
                    f"line {line_no} has {len(raw)} columns"
                )
            tag, category_id, post_count, raw_aliases = raw
            category_id = category_id.strip()
            rows.append(
                {
                    "Tag": tag,
                    "DanbooruCategory": CATEGORY_NAMES.get(category_id, category_id),
                    "post_count": post_count,
                    "Aliases": "",
                    "RawAliases": raw_aliases,
                    "Special2788": "",
                }
            )
    if not rows:
        raise ValueError("canonical-source: no rows")
    return rows


def attach_unique_aliases(
    canonical_rows: list[dict[str, str]], alias_index_path: Path
) -> tuple[list[dict[str, str]], dict[str, int]]:
    alias_rows = read_csv(alias_index_path)
    require_columns(
        alias_rows,
        {"NormalizedAlias", "TargetCount", "CanonicalTargets"},
        "alias-index",
    )
    canonical_by_norm = {norm(row["Tag"]): row for row in canonical_rows}
    aliases_by_canonical: dict[str, list[str]] = {}
    unique_rows = 0
    ambiguous_rows = 0
    canonical_precedence_rows = 0
    unresolved_targets = 0

    for row in alias_rows:
        target_count = as_int(row.get("TargetCount", ""))
        status = (row.get("ResolutionStatus") or "").strip().upper()
        if status == "CANONICAL_PRECEDENCE":
            canonical_precedence_rows += 1
            continue
        if target_count != 1:
            ambiguous_rows += 1
            continue
        target = (row.get("CanonicalTargets") or "").strip()
        target_row = canonical_by_norm.get(norm(target))
        if target_row is None:
            unresolved_targets += 1
            continue
        alias = (row.get("NormalizedAlias") or "").strip()
        if not alias:
            continue
        aliases_by_canonical.setdefault(norm(target_row["Tag"]), []).append(alias)
        unique_rows += 1

    for canonical_norm, aliases in aliases_by_canonical.items():
        canonical_by_norm[canonical_norm]["Aliases"] = ",".join(dict.fromkeys(aliases))

    if unresolved_targets:
        raise ValueError(
            f"alias-index: {unresolved_targets} unique alias targets are absent from canonical source"
        )

    stats = {
        "alias_index_rows": len(alias_rows),
        "unique_alias_rows_used": unique_rows,
        "ambiguous_alias_rows_skipped": ambiguous_rows,
        "canonical_precedence_rows_skipped": canonical_precedence_rows,
    }
    return canonical_rows, stats


def attach_embedded_unique_aliases(
    canonical_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], dict[str, int]]:
    canonical_by_norm = {norm(row["Tag"]): row for row in canonical_rows}
    alias_targets: dict[str, set[str]] = {}
    alias_surfaces: dict[tuple[str, str], str] = {}
    raw_alias_entries = 0
    canonical_precedence_rows = 0

    for row in canonical_rows:
        canonical_norm = norm(row["Tag"])
        for alias in split_aliases(row.get("RawAliases", "")):
            alias_norm = norm(alias)
            if not alias_norm:
                continue
            raw_alias_entries += 1
            if alias_norm in canonical_by_norm:
                canonical_precedence_rows += 1
                continue
            alias_targets.setdefault(alias_norm, set()).add(canonical_norm)
            alias_surfaces.setdefault((alias_norm, canonical_norm), alias)

    aliases_by_canonical: dict[str, list[str]] = {}
    unique_rows = 0
    ambiguous_rows = 0
    for alias_norm, targets in alias_targets.items():
        if len(targets) != 1:
            ambiguous_rows += 1
            continue
        canonical_norm = next(iter(targets))
        surface = alias_surfaces[(alias_norm, canonical_norm)]
        aliases_by_canonical.setdefault(canonical_norm, []).append(surface)
        unique_rows += 1

    for canonical_norm, aliases in aliases_by_canonical.items():
        canonical_by_norm[canonical_norm]["Aliases"] = ",".join(dict.fromkeys(aliases))

    return canonical_rows, {
        "embedded_alias_entries_seen": raw_alias_entries,
        "unique_alias_rows_used": unique_rows,
        "ambiguous_alias_rows_skipped": ambiguous_rows,
        "canonical_precedence_rows_skipped": canonical_precedence_rows,
    }


def load_full_input(args: argparse.Namespace) -> tuple[list[dict[str, str]], dict[str, object]]:
    if args.full_kb:
        if args.canonical_source or args.alias_index:
            raise ValueError(
                "choose one source mode: --full-kb OR --canonical-source [--alias-index]"
            )
        full = read_csv(args.full_kb)
        require_columns(
            full,
            {"Tag", "DanbooruCategory", "post_count", "Aliases", "Special2788"},
            "full-kb",
        )
        return full, {
            "source_mode": "FULL_KB",
            "full_kb": str(args.full_kb),
            "canonical_source": None,
            "alias_index": None,
            "legacy_marker_available": True,
        }

    if not args.canonical_source:
        raise ValueError(
            "source input required: --full-kb OR --canonical-source [--alias-index]"
        )
    full = read_canonical_source(args.canonical_source)
    if args.alias_index:
        full, alias_stats = attach_unique_aliases(full, args.alias_index)
        source_mode = "CANONICAL_SOURCE_PLUS_VERIFIED_ALIAS_INDEX"
        alias_index = str(args.alias_index)
    else:
        full, alias_stats = attach_embedded_unique_aliases(full)
        source_mode = "CANONICAL_SOURCE_PLUS_EMBEDDED_UNIQUE_ALIAS_CLOSURE"
        alias_index = None
    return full, {
        "source_mode": source_mode,
        "full_kb": None,
        "canonical_source": str(args.canonical_source),
        "alias_index": alias_index,
        "legacy_marker_available": False,
        **alias_stats,
    }


def profile_row_is_semantic(row: dict[str, str]) -> bool:
    promotion = (row.get("PromotionStatus") or "").strip().upper()
    meaning = (row.get("MeaningStatus") or "").strip().upper()
    flags = (row.get("SpecialFlags") or "").strip().upper()
    return (
        promotion == "APPROVED_SEMANTIC_ROLE"
        or meaning == "SEMANTIC_SUPPORT"
        or "SEMANTIC_NOT_DIRECT_CANONICAL" in flags
    )


def load_special_input(
    args: argparse.Namespace,
) -> tuple[list[dict[str, str]], dict[str, object]]:
    if args.special:
        special = read_csv(args.special)
        require_columns(
            special,
            {"ID", "Tag", "Danbooru種別", "canonical_target"},
            "special",
        )
        return special, {
            "special_source_mode": "PROTECTED_SPECIAL_SOURCE",
            "special": str(args.special),
            "special_profile": None,
            "special_profile_semantic_rows": None,
        }

    profile = read_csv(args.special_profile)
    require_columns(
        profile,
        {"SpecialID", "Tag", "PromotionStatus", "MeaningStatus", "SpecialFlags"},
        "special-profile",
    )
    special: list[dict[str, str]] = []
    semantic_count = 0
    for row in profile:
        semantic = profile_row_is_semantic(row)
        if semantic:
            semantic_count += 1
        special.append(
            {
                "ID": row["SpecialID"],
                "Tag": row["Tag"],
                "Danbooru種別": "Semantic/General" if semantic else "Derived/Identity",
                "canonical_target": "",
            }
        )
    if semantic_count != args.expected_profile_semantic:
        raise ValueError(
            "special-profile semantic row count mismatch: "
            f"expected {args.expected_profile_semantic}, got {semantic_count}"
        )
    return special, {
        "special_source_mode": "TRACKED_GENERATION_PROFILE_DERIVED_IDENTITY",
        "special": None,
        "special_profile": str(args.special_profile),
        "special_profile_semantic_rows": semantic_count,
    }


def derive_profile_canonical_targets(
    special: list[dict[str, str]],
    full: list[dict[str, str]],
    expected_alias_count: int,
) -> tuple[dict[str, list[str]], dict[str, object]]:
    canonical_norms = {norm(row["Tag"]) for row in full}
    alias_to_canonicals: dict[str, set[str]] = {}
    for row in full:
        canonical_norm = norm(row["Tag"])
        for alias in split_aliases(row.get("Aliases", "")):
            alias_to_canonicals.setdefault(norm(alias), set()).add(canonical_norm)

    raw_alias_targets: dict[str, set[str]] = {}
    for row in full:
        canonical_norm = norm(row["Tag"])
        for alias in split_aliases(row.get("RawAliases", "")):
            alias_norm = norm(alias)
            if alias_norm:
                raw_alias_targets.setdefault(alias_norm, set()).add(canonical_norm)

    canonical_targets: dict[str, list[str]] = {}
    exact_count = 0
    alias_count = 0
    unresolved: list[str] = []
    ambiguous: list[dict[str, object]] = []

    for row in special:
        if (row["Danbooru種別"] or "").strip().casefold() == "semantic/general":
            continue
        tag_norm = norm(row["Tag"])
        evidence = f"{row['ID']}:{row['Tag']}"
        if tag_norm in canonical_norms:
            exact_count += 1
            continue
        targets = alias_to_canonicals.get(tag_norm, set())
        if len(targets) == 1:
            target_norm = next(iter(targets))
            canonical_targets.setdefault(target_norm, []).append(evidence)
            alias_count += 1
            continue

        raw_targets = raw_alias_targets.get(tag_norm, set())
        if len(raw_targets) > 1:
            ambiguous.append(
                {
                    "special": evidence,
                    "targets": sorted(raw_targets),
                }
            )
        elif len(raw_targets) == 1:
            # A raw alias that has one target should have survived unique alias closure.
            # Treat divergence as a data-integrity failure instead of guessing.
            unresolved.append(f"{evidence}: unique raw alias missing from closure")
        else:
            unresolved.append(evidence)

    if unresolved:
        raise ValueError(
            "special-profile identity closure has unresolved non-semantic rows; "
            f"protected canonical_target fallback is required: {unresolved}"
        )

    alias_layer_count = alias_count + len(ambiguous)
    if alias_layer_count != expected_alias_count:
        raise ValueError(
            "special-profile Alias layer count mismatch: "
            f"expected {expected_alias_count}, got {alias_layer_count} "
            f"(unique={alias_count}, ambiguous={len(ambiguous)})"
        )

    return canonical_targets, {
        "special_profile_exact_canonical_rows": exact_count,
        "special_profile_unique_alias_target_rows": alias_count,
        "special_profile_ambiguous_alias_rows": len(ambiguous),
        "special_profile_alias_layer_rows": alias_layer_count,
        "special_profile_unresolved_identity_rows": 0,
        "special_profile_ambiguous_aliases": ambiguous,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Issue #94 read-only Danbooru General -> Special identity gap scanner"
    )
    source = parser.add_mutually_exclusive_group(required=False)
    source.add_argument("--full-kb", type=Path)
    source.add_argument("--canonical-source", type=Path)
    parser.add_argument(
        "--alias-index",
        type=Path,
        help=(
            "Optional verified normalized alias index used with --canonical-source. "
            "When omitted, the scanner derives a unique alias closure from the fourth "
            "column embedded in the historical canonical source."
        ),
    )
    special_source = parser.add_mutually_exclusive_group(required=True)
    special_source.add_argument("--special", type=Path)
    special_source.add_argument(
        "--special-profile",
        type=Path,
        help=(
            "Tracked data/generation/special2788_generation_profile.csv fallback. "
            "Semantic rows are identified from approved semantic markers; non-semantic "
            "alias targets are reconstructed from the selected Danbooru alias closure. "
            "Known multi-target aliases remain ambiguous and do not cover any one canonical."
        ),
    )
    parser.add_argument("--alias-map", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--expected-general", type=int, default=30743)
    parser.add_argument("--expected-special", type=int, default=2788)
    parser.add_argument("--expected-profile-semantic", type=int, default=336)
    parser.add_argument("--expected-profile-alias", type=int, default=778)
    args = parser.parse_args()

    full, source_meta = load_full_input(args)
    special, special_meta = load_special_input(args)

    if len(special) != args.expected_special:
        raise ValueError(
            f"special row count mismatch: expected {args.expected_special}, got {len(special)}"
        )
    ids = [row["ID"] for row in special]
    if len(ids) != len(set(ids)):
        raise ValueError("special contains duplicate IDs")

    special_identity_terms: dict[str, list[str]] = {}
    semantic_terms: dict[str, list[str]] = {}
    canonical_targets: dict[str, list[str]] = {}

    for row in special:
        tag_norm = norm(row["Tag"])
        source_type = (row["Danbooru種別"] or "").strip().casefold()
        sid = row["ID"]
        evidence = f"{sid}:{row['Tag']}"
        if source_type == "semantic/general":
            semantic_terms.setdefault(tag_norm, []).append(evidence)
        else:
            special_identity_terms.setdefault(tag_norm, []).append(evidence)
        target_norm = norm(row.get("canonical_target", ""))
        if target_norm:
            canonical_targets.setdefault(target_norm, []).append(evidence)

    if args.special_profile:
        canonical_targets, derived_meta = derive_profile_canonical_targets(
            special, full, args.expected_profile_alias
        )
        special_meta.update(derived_meta)

    alias_special_by_canonical: dict[str, list[str]] = {}
    if args.alias_map:
        alias_rows = read_csv(args.alias_map)
        require_columns(
            alias_rows,
            {"Alias", "CanonicalTag", "Special2788Alias"},
            "alias-map",
        )
        for row in alias_rows:
            if (row.get("Special2788Alias") or "").strip().upper() != "YES":
                continue
            canonical_norm = norm(row["CanonicalTag"])
            alias_special_by_canonical.setdefault(canonical_norm, []).append(row["Alias"])

    general = [
        row for row in full
        if (row.get("DanbooruCategory") or "").strip().casefold() == "general"
    ]
    if len(general) != args.expected_general:
        raise ValueError(
            f"General row count mismatch: expected {args.expected_general}, got {len(general)}"
        )

    inventory: list[dict[str, object]] = []
    status_counts: Counter[str] = Counter()
    legacy_false_gap_count = 0

    for row in general:
        canonical = row["Tag"]
        canonical_norm = norm(canonical)
        aliases = split_aliases(row.get("Aliases", ""))
        aliases_norm = {norm(alias): alias for alias in aliases}

        exact = special_identity_terms.get(canonical_norm, [])
        target = canonical_targets.get(canonical_norm, [])
        alias_hits: list[str] = []
        for alias_norm, original_alias in aliases_norm.items():
            if alias_norm in special_identity_terms:
                for hit in special_identity_terms[alias_norm]:
                    alias_hits.append(f"{original_alias}->{hit}")
        map_hits = alias_special_by_canonical.get(canonical_norm, [])

        semantic_hits: list[str] = []
        if canonical_norm in semantic_terms:
            semantic_hits.extend(semantic_terms[canonical_norm])
        for alias_norm, original_alias in aliases_norm.items():
            for hit in semantic_terms.get(alias_norm, []):
                semantic_hits.append(f"{original_alias}->{hit}")

        if exact:
            identity_status = "PRESENT_EXACT"
            identity_evidence = exact
        elif target:
            identity_status = "PRESENT_CANONICAL_TARGET"
            identity_evidence = target
        elif alias_hits or map_hits:
            identity_status = "PRESENT_ALIAS_CLOSURE"
            identity_evidence = alias_hits + [f"alias-map:{x}" for x in map_hits]
        elif semantic_hits:
            identity_status = "SEMANTIC_EXACT_OVERLAP_ONLY"
            identity_evidence = []
        else:
            identity_status = "GENERAL_ONLY_GAP"
            identity_evidence = []

        status_counts[identity_status] += 1
        legacy_marker = (row.get("Special2788") or "").strip().upper()
        if (
            source_meta["legacy_marker_available"]
            and legacy_marker != "YES"
            and identity_status.startswith("PRESENT_")
        ):
            legacy_false_gap_count += 1

        inventory.append(
            {
                "canonical": canonical,
                "post_count": as_int(row.get("post_count", "")),
                "aliases": "|".join(aliases),
                "legacy_special2788": legacy_marker,
                "identity_status": identity_status,
                "identity_evidence": "|".join(identity_evidence),
                "semantic_exact_overlap": "|".join(semantic_hits),
            }
        )

    order = {
        "GENERAL_ONLY_GAP": 0,
        "SEMANTIC_EXACT_OVERLAP_ONLY": 1,
        "PRESENT_ALIAS_CLOSURE": 2,
        "PRESENT_CANONICAL_TARGET": 3,
        "PRESENT_EXACT": 4,
    }
    inventory.sort(
        key=lambda row: (
            order[str(row["identity_status"])],
            -int(row["post_count"]),
            str(row["canonical"]),
        )
    )

    args.out_dir.mkdir(parents=True, exist_ok=True)
    inventory_path = args.out_dir / "general_special_identity_inventory.csv"
    with inventory_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(inventory[0]))
        writer.writeheader()
        writer.writerows(inventory)

    summary = {
        "mode": "ISSUE94_READ_ONLY_IDENTITY_AUDIT",
        **source_meta,
        **special_meta,
        "alias_map": str(args.alias_map) if args.alias_map else None,
        "total_general_scanned": len(general),
        "special_rows": len(special),
        "identity_status_counts": dict(sorted(status_counts.items())),
        "legacy_blank_but_identity_covered": (
            legacy_false_gap_count if source_meta["legacy_marker_available"] else None
        ),
        "content_filter_used": "NO",
        "production_files_changed": "NO",
        "issue70_mutated": "NO",
        "important_note": (
            "SEMANTIC_EXACT_OVERLAP_ONLY means exact normalized term overlap only; "
            "broader semantic similarity still requires human review. GENERAL_ONLY_GAP "
            "is an identity gap inventory, not automatic product-fit approval. "
            "Canonical-source modes admit only aliases with one normalized canonical target; "
            "canonical-name collisions and ambiguous aliases are never silently resolved. "
            "Special-profile mode preserves known multi-target Alias rows as ambiguous and "
            "does not use them to claim coverage of any one canonical. Unresolved non-semantic "
            "Special rows still abort the scan."
        ),
    }
    with (args.out_dir / "coverage_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
