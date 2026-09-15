#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

META_CANDIDATES = {
    "traditional_media",
    "photo_(medium)",
    "collage_(medium)",
    "painting_(medium)",
    "watercolor_(medium)",
    "marker_(medium)",
    "visual_novel_cg",
    "jpeg_artifacts",
    "anime_screenshot",
    "tall_image",
    "colorized",
    "novel_illustration",
    "concept_art",
    "screenshot",
    "mixed_media",
    "stitched",
    "key_visual",
    "acrylic_paint_(medium)",
    "production_art",
    "wide_image",
    "unconventional_media",
    "alpha_transparency",
    "crease",
    "oil_painting_(medium)",
    "art_study",
    "self-portrait",
    "game_screenshot",
    "aliasing",
    "graphite_(medium)",
    "colored_pencil_(medium)",
    "pen_(medium)",
    "nib_pen_(medium)",
    "millipen_(medium)",
    "ballpoint_pen_(medium)",
    "calligraphy_brush_(medium)",
    "watercolor_pencil_(medium)",
    "pastel_(medium)",
    "eyecatch",
    "papercraft_(medium)",
    "rotated",
    "color_ink_(medium)",
    "gouache_(medium)",
    "color_halftone",
    "blueprint_(medium)",
    "color_study",
    "bleed_through",
    "color_banding",
    "food_art_(medium)",
    "paper_cutout_(medium)",
    "crayon_(medium)",
    "lighting_study",
    "rotoscoping",
    "print_(medium)",
    "airbrush_(medium)",
    "charcoal_(medium)",
    "anatomy_study",
    "environment_study",
    "acrylic_gouache_(medium)",
    "clay_(medium)",
    "latte_art_(medium)",
    "coupy_pencil_(medium)",
    "vector_art",
    "wigglypaint_(medium)",
    "engraving_(medium)",
    "postcard_(medium)",
    "brush_(medium)",
    "vector_trace",
    "nude_filter",
}

ALIAS_TYPO_NOISE = {
    "breats",
    "thighhgihs",
    "thighhigs",
    "thighighs",
    "thighthick",
    "zettai_ryouki",
    "crossection",
}

ALIAS_OVERBROAD = {
    "assertive",
    "covering",
    "internal",
    "presenting",
    "public",
    "shaved",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def alias_decision(alias: str) -> tuple[str, str]:
    if alias.startswith("/"):
        return "REJECT_SHORTCUT", "Danbooru command-style shortcut is not a useful product search surface"
    if alias in ALIAS_TYPO_NOISE:
        return "REJECT_TYPO_NOISE", "misspelling-only redirect adds search noise without meaningful alternate vocabulary"
    if alias in ALIAS_OVERBROAD:
        return "REJECT_OVERBROAD_ALIAS", "surface is too broad to map safely to this narrower Special identity"
    return (
        "CANDIDATE_SEARCH_ALIAS",
        "verified one-target Danbooru alias for an already accepted Special-covered canonical; keep canonical output unchanged",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize Issue #97 Phase B bounded human review v1")
    parser.add_argument("--audit-dir", type=Path, required=True)
    args = parser.parse_args()

    alias_rows = read_csv(args.audit_dir / "alias_surface_inventory.csv")
    meta_rows = read_csv(args.audit_dir / "meta_prescreen_inventory.csv")

    candidates: list[dict[str, object]] = []
    rejected: list[dict[str, object]] = []
    review: list[dict[str, object]] = []

    for row in alias_rows:
        if row["status"] == "ALREADY_SPECIAL_SURFACE":
            decision = "NO_GAP_ALREADY_COVERED"
            reason = "alias surface is already represented by an accepted Special surface"
        else:
            decision, reason = alias_decision(row["alias"])

        record = {
            "lane": "ALIAS_SURFACE",
            "surface_or_canonical": row["alias"],
            "canonical_target": row["canonical_target"],
            "category": row["target_category"],
            "post_count": row["target_post_count"],
            "decision": decision,
            "reason": reason,
        }
        review.append(record)
        if decision == "CANDIDATE_SEARCH_ALIAS":
            candidates.append(record)
        else:
            rejected.append(record)

    meta_seen = {row["canonical"] for row in meta_rows}
    missing_meta = META_CANDIDATES - meta_seen
    if missing_meta:
        raise ValueError(f"pinned source missing reviewed Meta identities: {sorted(missing_meta)}")

    for row in meta_rows:
        canonical = row["canonical"]
        if row["status"] == "ALREADY_SPECIAL_COVERED":
            decision = "NO_GAP_ALREADY_COVERED"
            reason = "Meta canonical is already covered by accepted Special identity closure"
        elif canonical in META_CANDIDATES:
            decision = "CANDIDATE_META_CANONICAL"
            reason = (
                "human-screened as materially visible or generation-relevant medium, image type, "
                "layout/state, or rendering artifact; requires later product-fit/promotion review"
            )
        else:
            decision = "REJECT_META_NONPRODUCT"
            reason = (
                "human-screened out: administrative/provenance/source/tool/audio-video metadata or "
                "insufficient deep-discovery value for Special"
            )

        record = {
            "lane": "META_CANONICAL",
            "surface_or_canonical": canonical,
            "canonical_target": canonical,
            "category": "Meta",
            "post_count": row["post_count"],
            "decision": decision,
            "reason": reason,
        }
        review.append(record)
        if decision == "CANDIDATE_META_CANONICAL":
            candidates.append(record)
        else:
            rejected.append(record)

    candidates.sort(key=lambda r: (r["lane"], -int(r["post_count"]), r["surface_or_canonical"]))
    rejected.sort(key=lambda r: (r["lane"], r["decision"], -int(r["post_count"]), r["surface_or_canonical"]))
    review.sort(key=lambda r: (r["lane"], -int(r["post_count"]), r["surface_or_canonical"]))

    fields = [
        "lane", "surface_or_canonical", "canonical_target", "category", "post_count", "decision", "reason"
    ]
    write_csv(args.audit_dir / "phase_b_human_review_v1.csv", review, fields)
    write_csv(args.audit_dir / "phase_b_candidate_subset_v1.csv", candidates, fields)
    write_csv(args.audit_dir / "phase_b_rejected_ledger_v1.csv", rejected, fields)

    counts = Counter(row["decision"] for row in review)
    summary = {
        "mode": "ISSUE97_PHASE_B_HUMAN_REVIEW_V1",
        "reviewed_alias_inventory_rows": len(alias_rows),
        "reviewed_meta_rows": len(meta_rows),
        "reviewed_total": len(review),
        "decision_counts": dict(sorted(counts.items())),
        "candidate_aliases": sum(1 for r in candidates if r["decision"] == "CANDIDATE_SEARCH_ALIAS"),
        "candidate_meta_canonicals": sum(1 for r in candidates if r["decision"] == "CANDIDATE_META_CANONICAL"),
        "candidate_total": len(candidates),
        "rejected_or_already_covered_total": len(rejected),
        "production_mutation": "NO",
        "candidate_is_automatic_promotion": "NO",
        "phase_c_mixed_in": "NO",
        "issue70_mutated": "NO",
        "userdata_mutated": "NO",
        "content_filter_used": "NO",
        "note": (
            "Alias candidates are search-only surfaces and must continue to resolve to the current canonical target. "
            "Meta candidates are canonical identities only because they exist as current Danbooru Meta canonicals; "
            "this review does not approve promotion. Artist/Character/Copyright catalogs remain excluded by Phase B policy."
        ),
    }
    (args.audit_dir / "phase_b_human_review_summary_v1.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
