#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

CATEGORY_NAMES = {
    "0": "General",
    "1": "Artist",
    "3": "Copyright",
    "4": "Character",
    "5": "Meta",
}

META_CANDIDATE_PHRASES = (
    "4koma", "4 koma", "animated", "animation", "anaglyph", "bar censor",
    "caption", "censored", "censoring", "character sheet", "collage", "comic",
    "comparison", "diagram", "english text", "fisheye", "frame", "framed", "gif",
    "infographic", "japanese text", "letterbox", "manga", "mosaic censor",
    "multiple images", "onomatopoeia", "panel", "panorama", "photo", "photograph",
    "pillarbox", "pixel art", "reference sheet", "scan", "screencap", "signature",
    "speech bubble", "split image", "stereogram", "subtitle", "text", "thought bubble",
    "traditional media", "transparent background", "uncensored", "video", "watermark",
    "webtoon",
)

META_ADMIN_PHRASES = (
    "bad id", "bad pixiv id", "commentary", "commission", "deleted", "duplicate",
    "fanbox", "md5", "paid reward", "patreon", "pixiv", "request", "revision",
    "source request", "tagme", "translated", "translation request", "twitter",
    "unknown artist", "upload",
)

META_LOW_PRODUCT_VALUE_PHRASES = (
    "artist name", "copyright name", "official art", "sample", "source",
)

SEMANTIC_PROMOTION = "APPROVED_SEMANTIC_ROLE"
SEMANTIC_MEANING = "SEMANTIC_SUPPORT"
SEMANTIC_FLAG = "SEMANTIC_NOT_DIRECT_CANONICAL"


def norm(value: object) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKC", text).strip().casefold().replace("_", " ")
    return " ".join(text.split())


def as_int(value: str) -> int:
    text = (value or "").strip().replace(",", "")
    return int(float(text)) if text else 0


def split_aliases(value: str) -> list[str]:
    return [part.strip() for part in (value or "").split(",") if part.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_canonical_source(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for line_no, raw in enumerate(csv.reader(handle), start=1):
            if len(raw) != 4:
                raise ValueError(
                    f"canonical-source: expected headerless 4 columns; line {line_no} has {len(raw)}"
                )
            tag, category_id, post_count, raw_aliases = raw
            rows.append(
                {
                    "tag": tag.strip(),
                    "category_id": category_id.strip(),
                    "category": CATEGORY_NAMES.get(category_id.strip(), category_id.strip()),
                    "post_count": as_int(post_count),
                    "raw_aliases": raw_aliases.strip(),
                }
            )
    if not rows:
        raise ValueError("canonical-source: no rows")
    return rows


def profile_row_is_semantic(row: dict[str, str]) -> bool:
    return (
        (row.get("PromotionStatus") or "").strip().upper() == SEMANTIC_PROMOTION
        or (row.get("MeaningStatus") or "").strip().upper() == SEMANTIC_MEANING
        or SEMANTIC_FLAG in (row.get("SpecialFlags") or "").strip().upper()
    )


def build_alias_closure(
    canonical_rows: list[dict[str, object]],
) -> tuple[dict[str, list[tuple[str, str]]], dict[str, set[str]], dict[str, int]]:
    canonical_by_norm = {norm(row["tag"]): row for row in canonical_rows}
    alias_targets: dict[str, set[str]] = defaultdict(set)
    surfaces: dict[tuple[str, str], str] = {}
    raw_entries = 0
    canonical_precedence = 0

    for row in canonical_rows:
        target_norm = norm(row["tag"])
        for alias in split_aliases(str(row["raw_aliases"])):
            alias_norm = norm(alias)
            if not alias_norm:
                continue
            raw_entries += 1
            if alias_norm in canonical_by_norm:
                canonical_precedence += 1
                continue
            alias_targets[alias_norm].add(target_norm)
            surfaces.setdefault((alias_norm, target_norm), alias)

    unique_by_target: dict[str, list[tuple[str, str]]] = defaultdict(list)
    ambiguous = 0
    for alias_norm, targets in alias_targets.items():
        if len(targets) != 1:
            ambiguous += 1
            continue
        target_norm = next(iter(targets))
        unique_by_target[target_norm].append(
            (alias_norm, surfaces[(alias_norm, target_norm)])
        )

    for entries in unique_by_target.values():
        entries.sort(key=lambda pair: (pair[0], pair[1]))

    return unique_by_target, alias_targets, {
        "raw_alias_entries": raw_entries,
        "unique_alias_surfaces": sum(len(v) for v in unique_by_target.values()),
        "ambiguous_alias_surfaces": ambiguous,
        "canonical_precedence_aliases": canonical_precedence,
    }


def build_special_coverage(
    profile_path: Path,
    canonical_rows: list[dict[str, object]],
    unique_aliases_by_target: dict[str, list[tuple[str, str]]],
    alias_targets: dict[str, set[str]],
    expected_special: int,
) -> tuple[set[str], set[str], dict[str, object]]:
    rows = read_csv(profile_path)
    if not rows:
        raise ValueError("special-profile: no rows")
    required = {"SpecialID", "Tag", "PromotionStatus", "MeaningStatus", "SpecialFlags"}
    missing = required - set(rows[0])
    if missing:
        raise ValueError(f"special-profile missing columns: {sorted(missing)}")
    if len(rows) != expected_special:
        raise ValueError(
            f"special-profile row count mismatch: expected {expected_special}, got {len(rows)}"
        )

    ids = [int(row["SpecialID"]) for row in rows]
    if sorted(ids) != list(range(1, expected_special + 1)):
        raise ValueError("special-profile IDs are not exact contiguous 1..expected-special")

    canonical_norms = {norm(row["tag"]) for row in canonical_rows}
    unique_alias_target: dict[str, str] = {}
    for target_norm, pairs in unique_aliases_by_target.items():
        for alias_norm, _surface in pairs:
            unique_alias_target[alias_norm] = target_norm

    all_surfaces: set[str] = set()
    covered_canonical: set[str] = set()
    semantic_rows = 0
    exact_rows = 0
    unique_alias_rows = 0
    ambiguous_alias_rows = 0
    unresolved_rows: list[str] = []

    for row in rows:
        tag = row["Tag"]
        tag_norm = norm(tag)
        all_surfaces.add(tag_norm)
        if profile_row_is_semantic(row):
            semantic_rows += 1
            continue
        if tag_norm in canonical_norms:
            covered_canonical.add(tag_norm)
            exact_rows += 1
            continue
        target = unique_alias_target.get(tag_norm)
        if target:
            covered_canonical.add(target)
            unique_alias_rows += 1
            continue
        raw_targets = alias_targets.get(tag_norm, set())
        if len(raw_targets) > 1:
            ambiguous_alias_rows += 1
            continue
        unresolved_rows.append(f"{row['SpecialID']}:{tag}")

    return all_surfaces, covered_canonical, {
        "special_rows": len(rows),
        "semantic_rows": semantic_rows,
        "exact_canonical_rows": exact_rows,
        "unique_alias_identity_rows": unique_alias_rows,
        "ambiguous_alias_identity_rows": ambiguous_alias_rows,
        "unresolved_nonsemantic_rows": unresolved_rows,
    }


def contains_phrase(text: str, phrases: tuple[str, ...]) -> list[str]:
    hits: list[str] = []
    for phrase in phrases:
        p = norm(phrase)
        if p in text:
            hits.append(phrase)
    return hits


def classify_meta(tag: str) -> tuple[str, str, str]:
    text = norm(tag)
    admin_hits = contains_phrase(text, META_ADMIN_PHRASES)
    candidate_hits = contains_phrase(text, META_CANDIDATE_PHRASES)
    low_hits = contains_phrase(text, META_LOW_PRODUCT_VALUE_PHRASES)

    if admin_hits and not candidate_hits:
        return (
            "EXCLUDE_ADMIN_OR_PROVENANCE",
            ",".join(admin_hits),
            "administrative/provenance metadata rather than reusable visible generation intent",
        )
    if candidate_hits:
        return (
            "REVIEW_VISIBLE_OR_STRUCTURAL_META",
            ",".join(candidate_hits),
            "Meta identity has a visible, layout, text, censoring, medium, or image-structure signal",
        )
    if low_hits:
        return (
            "EXCLUDE_LOW_PRODUCT_VALUE_META",
            ",".join(low_hits),
            "Meta identity is mostly attribution/source labeling rather than deep discovery",
        )
    return (
        "EXCLUDE_NO_VISIBLE_SIGNAL",
        "",
        "no mechanical visible/image-structure signal; keep out of bounded human review",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Issue #97 Phase B read-only Danbooru non-General and alias coverage audit"
    )
    parser.add_argument("--canonical-source", type=Path, required=True)
    parser.add_argument("--special-profile", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--expected-special", type=int, default=2983)
    parser.add_argument("--alias-review-limit", type=int, default=600)
    parser.add_argument("--meta-review-limit", type=int, default=400)
    args = parser.parse_args()

    canonical_rows = read_canonical_source(args.canonical_source)
    unique_aliases_by_target, alias_targets, alias_stats = build_alias_closure(canonical_rows)
    special_surfaces, covered_canonical, special_stats = build_special_coverage(
        args.special_profile,
        canonical_rows,
        unique_aliases_by_target,
        alias_targets,
        args.expected_special,
    )

    canonical_by_norm = {norm(row["tag"]): row for row in canonical_rows}

    alias_inventory: list[dict[str, object]] = []
    for target_norm in sorted(covered_canonical):
        target = canonical_by_norm.get(target_norm)
        if target is None:
            continue
        for alias_norm, alias_surface in unique_aliases_by_target.get(target_norm, []):
            status = (
                "ALREADY_SPECIAL_SURFACE"
                if alias_norm in special_surfaces
                else "REVIEW_ALIAS_SURFACE"
            )
            alias_inventory.append(
                {
                    "lane": "ALIAS_SURFACE",
                    "status": status,
                    "alias": alias_surface,
                    "canonical_target": target["tag"],
                    "target_category": target["category"],
                    "target_post_count": target["post_count"],
                    "reason": (
                        "verified unique Danbooru alias to an existing Special-covered canonical"
                        if status == "REVIEW_ALIAS_SURFACE"
                        else "alias surface already resolves through an existing Special surface"
                    ),
                }
            )

    alias_inventory.sort(
        key=lambda row: (
            0 if row["status"] == "REVIEW_ALIAS_SURFACE" else 1,
            -int(row["target_post_count"]),
            norm(row["canonical_target"]),
            norm(row["alias"]),
        )
    )
    alias_review_all = [
        row for row in alias_inventory if row["status"] == "REVIEW_ALIAS_SURFACE"
    ]
    alias_review_batch = alias_review_all[: args.alias_review_limit]

    meta_inventory: list[dict[str, object]] = []
    for row in canonical_rows:
        if row["category"] != "Meta":
            continue
        tag_norm = norm(row["tag"])
        if tag_norm in covered_canonical:
            status = "ALREADY_SPECIAL_COVERED"
            signals = ""
            reason = "current canonical Meta identity is already covered by Special"
        else:
            status, signals, reason = classify_meta(str(row["tag"]))
        meta_inventory.append(
            {
                "lane": "META_CANONICAL",
                "status": status,
                "canonical": row["tag"],
                "post_count": row["post_count"],
                "signals": signals,
                "reason": reason,
            }
        )

    meta_inventory.sort(
        key=lambda row: (
            0 if row["status"] == "REVIEW_VISIBLE_OR_STRUCTURAL_META" else 1,
            -int(row["post_count"]),
            norm(row["canonical"]),
        )
    )
    meta_review_all = [
        row
        for row in meta_inventory
        if row["status"] == "REVIEW_VISIBLE_OR_STRUCTURAL_META"
    ]
    meta_review_batch = meta_review_all[: args.meta_review_limit]

    review_queue: list[dict[str, object]] = []
    for row in alias_review_batch:
        review_queue.append(
            {
                "lane": row["lane"],
                "surface_or_canonical": row["alias"],
                "canonical_target": row["canonical_target"],
                "category": row["target_category"],
                "post_count": row["target_post_count"],
                "signals": "verified_unique_alias",
                "machine_reason": row["reason"],
                "human_decision": "",
                "human_reason": "",
            }
        )
    for row in meta_review_batch:
        review_queue.append(
            {
                "lane": row["lane"],
                "surface_or_canonical": row["canonical"],
                "canonical_target": row["canonical"],
                "category": "Meta",
                "post_count": row["post_count"],
                "signals": row["signals"],
                "machine_reason": row["reason"],
                "human_decision": "",
                "human_reason": "",
            }
        )

    review_queue.sort(
        key=lambda row: (
            0 if row["lane"] == "ALIAS_SURFACE" else 1,
            -int(row["post_count"]),
            norm(row["surface_or_canonical"]),
        )
    )

    exclusion_ledger: list[dict[str, object]] = []
    for row in meta_inventory:
        if str(row["status"]).startswith("EXCLUDE_"):
            exclusion_ledger.append(
                {
                    "lane": row["lane"],
                    "surface_or_canonical": row["canonical"],
                    "category": "Meta",
                    "post_count": row["post_count"],
                    "exclusion": row["status"],
                    "reason": row["reason"],
                }
            )

    category_counts = Counter(str(row["category"]) for row in canonical_rows)
    category_policy = [
        {
            "category": category,
            "rows": category_counts.get(category, 0),
            "phase_b_policy": policy,
            "reason": reason,
        }
        for category, policy, reason in (
            ("General", "NOT_REOPENED", "Issue #94 canonical General audit is complete"),
            ("Artist", "CATALOG_EXCLUDED", "do not import Artist catalog into Special"),
            ("Copyright", "CATALOG_EXCLUDED", "do not import Copyright catalog into Special"),
            ("Character", "CATALOG_EXCLUDED", "do not import Character catalog into Special"),
            ("Meta", "BOUNDED_PRESCREEN", "review only visible/generation-relevant structural Meta identities"),
        )
    ]

    out = args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    write_csv(
        out / "alias_surface_inventory.csv",
        alias_inventory,
        ["lane", "status", "alias", "canonical_target", "target_category", "target_post_count", "reason"],
    )
    write_csv(
        out / "meta_prescreen_inventory.csv",
        meta_inventory,
        ["lane", "status", "canonical", "post_count", "signals", "reason"],
    )
    write_csv(
        out / "phase_b_review_queue.csv",
        review_queue,
        [
            "lane", "surface_or_canonical", "canonical_target", "category", "post_count",
            "signals", "machine_reason", "human_decision", "human_reason",
        ],
    )
    write_csv(
        out / "phase_b_exclusion_ledger.csv",
        exclusion_ledger,
        ["lane", "surface_or_canonical", "category", "post_count", "exclusion", "reason"],
    )
    write_csv(
        out / "category_policy_summary.csv",
        category_policy,
        ["category", "rows", "phase_b_policy", "reason"],
    )

    alias_status = Counter(str(row["status"]) for row in alias_inventory)
    meta_status = Counter(str(row["status"]) for row in meta_inventory)
    summary = {
        "mode": "ISSUE97_PHASE_B_NONGENERAL_READ_ONLY_AUDIT",
        "canonical_rows": len(canonical_rows),
        "category_counts": dict(sorted(category_counts.items())),
        **alias_stats,
        **special_stats,
        "special_covered_canonical_targets": len(covered_canonical),
        "alias_status_counts": dict(sorted(alias_status.items())),
        "alias_review_total": len(alias_review_all),
        "alias_review_batch": len(alias_review_batch),
        "alias_review_limit": args.alias_review_limit,
        "meta_status_counts": dict(sorted(meta_status.items())),
        "meta_review_total": len(meta_review_all),
        "meta_review_batch": len(meta_review_batch),
        "meta_review_limit": args.meta_review_limit,
        "review_queue_rows": len(review_queue),
        "meta_exclusion_ledger_rows": len(exclusion_ledger),
        "general_canonical_reopened": "NO",
        "artist_catalog_imported": "NO",
        "character_catalog_imported": "NO",
        "copyright_catalog_imported": "NO",
        "content_filter_used": "NO",
        "production_files_changed": "NO",
        "issue70_mutated": "NO",
        "userdata_mutated": "NO",
        "phase_c_recipes_mixed_in": "NO",
        "important_note": (
            "The review queue is a bounded first human-review batch, not an automatic promotion list. "
            "Alias rows are admitted only when the historical snapshot gives one canonical target and "
            "that target is already covered by Special. Meta rows are mechanically prescreened for "
            "visible/image-structure signals. Post count only orders review; it does not determine "
            "inclusion or exclusion. Artist/Character/Copyright catalogs are excluded at category-policy "
            "level rather than bulk-imported or row-by-row re-reviewed."
        ),
    }
    with (out / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)
        handle.write("\n")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
