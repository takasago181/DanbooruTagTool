#!/usr/bin/env python3
"""Materialize an audit-only Special-vs-General reverse-audit ledger.

This script is intentionally conservative. It never mutates production assets and
never treats General overlap as an automatic demotion. Exact overlap is only a
review signal; deep Special generation families remain KEEP_SPECIAL by default.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

DEEP_FAMILIES = {
    "ACTION_INTERACTION",
    "INSERTION_STRUCTURED",
    "MULTI_ACTOR_INTERACTION",
    "SELF_ACTION",
    "RESTRAINT_ACTION",
    "RESTRAINT_IMPLEMENT",
    "FLUID_STATE_ACTION",
    "NONHUMAN_INTERACTION",
    "MACHINE_STRUCTURED",
    "DAMAGE_STATE_ACTION",
}

GENERALISH_REVIEW_FAMILIES = {
    "BODY_ATTRIBUTE",
    "BODY_STATE",
    "CLOTHING_EXPOSURE",
    "POSE_COMPOSITION",
    "REACTION_STATE",
    "SCENE_CONTEXT",
    "RELATION_ROLE_CONTEXT",
    "CONTEXT_MODIFIER",
    "DIRECT_COMPOSITE",
    "IMPLEMENT_OBJECT",
}

# Human-seeded obvious/plain concepts from the first direct review tranche.
# These are audit candidates only. They are NOT deletion authority.
B1_HUMAN_SEEDS = {
    1: "plain anatomy/body-site concept; verify General Japanese discovery",
    213: "plain anatomy/body-site concept; verify whether Special depth adds value",
    509: "plain anatomy label/slang; verify General Japanese discovery",
    578: "plain anatomy concept; verify General Japanese discovery",
    636: "broad ordinary exposure state; verify General Japanese discovery",
    638: "broad ordinary exposure state/intensity; verify General Japanese discovery",
    665: "plain anatomy concept; verify General Japanese discovery",
    666: "common exposure state; verify General Japanese discovery",
    722: "general character-type concept; verify whether adult deep-discovery value is distinct",
    724: "general character-type concept; verify whether adult deep-discovery value is distinct",
}

B1_HUMAN_NEEDS_REVIEW = {
    54: "very broad adult umbrella; broadness alone is not a demotion reason",
    416: "broad BDSM umbrella; may still be valuable as a deep-discovery entry/theme anchor",
    421: "broad torture concept; may still be valuable for BDSM/R18G discovery",
    712: "broad adult/body category; verify General sufficiency without losing niche discovery",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def normalize_tag(value: str) -> str:
    return "_".join(value.strip().lower().replace("_", " ").split())


def choose_field(fields: list[str], candidates: list[str], *, required: bool = False) -> str | None:
    lowered = {f.lower(): f for f in fields}
    for c in candidates:
        if c.lower() in lowered:
            return lowered[c.lower()]
    if required:
        raise SystemExit(f"required field not found; candidates={candidates}; actual={fields}")
    return None


def val(row: dict[str, str], field: str | None) -> str:
    return (row.get(field, "") if field else "").strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="data/generation/special2788_generation_profile.csv")
    ap.add_argument("--fit", default="data/special2788/product_fit_verdicts.csv")
    ap.add_argument("--general", default="docs/issue64/production_candidate/effective_sidecar.csv")
    ap.add_argument("--out-dir", default="docs/issue109")
    args = ap.parse_args()

    profile_path = Path(args.profile)
    fit_path = Path(args.fit)
    general_path = Path(args.general)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with profile_path.open(encoding="utf-8-sig", newline="") as f:
        profile = list(csv.DictReader(f))
    with fit_path.open(encoding="utf-8-sig", newline="") as f:
        fit_rows = list(csv.DictReader(f))
    with general_path.open(encoding="utf-8-sig", newline="") as f:
        gr = csv.DictReader(f)
        general_fields = list(gr.fieldnames or [])
        general_rows = list(gr)

    if len(profile) != 3088:
        raise SystemExit(f"expected 3088 Special rows, got {len(profile)}")
    ids = [int(r["SpecialID"]) for r in profile]
    if ids != list(range(1, 3089)):
        raise SystemExit("Special IDs are not exactly contiguous 1..3088")
    if len(fit_rows) != 3088:
        raise SystemExit(f"expected 3088 product-fit rows, got {len(fit_rows)}")
    if len(general_rows) != 30629:
        raise SystemExit(f"expected 30629 General rows, got {len(general_rows)}")

    general_canonical = choose_field(general_fields, ["canonical", "canonical_tag", "tag", "Tag"], required=True)
    general_display = choose_field(general_fields, ["display_ja", "japanese_display", "display_japanese"])
    general_search = choose_field(general_fields, ["search_ja", "japanese_search", "search_japanese"])
    general_post = choose_field(general_fields, ["post_count", "posts", "count"])
    general_status = choose_field(general_fields, ["status", "classification_status", "taxonomy_status"])
    general_confidence = choose_field(general_fields, ["confidence", "classification_confidence"])
    general_primary = choose_field(general_fields, ["primary_path", "primary_genre_id", "genre_id", "category_path"])
    general_secondary = choose_field(general_fields, ["secondary_paths", "secondary_path"])

    gindex: dict[str, dict[str, str]] = {}
    collisions: dict[str, int] = Counter()
    for row in general_rows:
        key = normalize_tag(val(row, general_canonical))
        if not key:
            continue
        if key in gindex:
            collisions[key] += 1
        else:
            gindex[key] = row
    if collisions:
        raise SystemExit(f"normalized General canonical collisions: {len(collisions)}")

    fit_by_id = {int(r["special_id"]): r.get("product_fit_verdict", "") for r in fit_rows}
    ledger: list[dict[str, str]] = []
    counts = Counter()
    overlap_count = 0

    for row in profile:
        sid = int(row["SpecialID"])
        tag = row["Tag"].strip()
        key = normalize_tag(tag)
        grow = gindex.get(key)
        exact_general = grow is not None
        if exact_general:
            overlap_count += 1

        family = row.get("GenerationFamily", "").strip()
        promotion = row.get("PromotionStatus", "").strip()
        meaning = row.get("MeaningStatus", "").strip()
        mode = row.get("PromptUseMode", "").strip()
        flags = row.get("SpecialFlags", "").strip()
        fit = fit_by_id.get(sid, "")

        # Conservative machine triage. General overlap never directly proves General sufficiency.
        if sid in B1_HUMAN_SEEDS:
            triage = "GENERAL_SUFFICIENT_CANDIDATE" if exact_general else "NEEDS_REVIEW"
            reason = "B1_HUMAN_SEED; " + B1_HUMAN_SEEDS[sid]
        elif sid in B1_HUMAN_NEEDS_REVIEW:
            triage = "NEEDS_REVIEW"
            reason = "B1_HUMAN_REVIEW; " + B1_HUMAN_NEEDS_REVIEW[sid]
        elif family in DEEP_FAMILIES:
            triage = "KEEP_SPECIAL"
            reason = f"DEEP_FAMILY:{family}"
        elif exact_general and family in GENERALISH_REVIEW_FAMILIES:
            triage = "NEEDS_REVIEW"
            reason = f"EXACT_GENERAL_OVERLAP+GENERALISH_FAMILY:{family}"
        elif exact_general and (promotion in {"APPROVED_IDENTITY_ONLY", "APPROVED_SEMANTIC_ROLE"} or mode in {"ALIAS_PRESERVE", "SUPPORT", "REFERENCE_ONLY"}):
            triage = "NEEDS_REVIEW"
            reason = "EXACT_GENERAL_OVERLAP+IDENTITY_OR_SEARCH_SUPPORT"
        else:
            triage = "KEEP_SPECIAL"
            reason = "NO_STRONG_GENERAL_SUFFICIENCY_SIGNAL"

        counts[triage] += 1
        ledger.append({
            "special_id": str(sid),
            "tag": tag,
            "mechanical_triage": triage,
            "triage_reason": reason,
            "exact_general_overlap": "YES" if exact_general else "NO",
            "product_fit_verdict": fit,
            "promotion_status": promotion,
            "meaning_status": meaning,
            "generation_family": family,
            "generation_role": row.get("GenerationRole", "").strip(),
            "prompt_use_mode": mode,
            "special_flags": flags,
            "general_canonical": val(grow or {}, general_canonical),
            "general_display_ja": val(grow or {}, general_display),
            "general_search_ja": val(grow or {}, general_search),
            "general_post_count": val(grow or {}, general_post),
            "general_status": val(grow or {}, general_status),
            "general_confidence": val(grow or {}, general_confidence),
            "general_primary_path": val(grow or {}, general_primary),
            "general_secondary_paths": val(grow or {}, general_secondary),
            "human_final": "",
            "human_reason": "",
        })

    fields = list(ledger[0])
    ledger_path = out_dir / "mechanical_triage_v1.csv"
    with ledger_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(ledger)

    review = [r for r in ledger if r["mechanical_triage"] != "KEEP_SPECIAL"]
    review_path = out_dir / "review_queue_v1.csv"
    with review_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(review)

    summary = {
        "issue": 109,
        "source_special_rows": len(profile),
        "source_general_rows": len(general_rows),
        "special_ids": [1, 3088],
        "general_exact_overlap": overlap_count,
        "triage_counts": dict(sorted(counts.items())),
        "review_queue_rows": len(review),
        "general_fields": general_fields,
        "resolved_general_fields": {
            "canonical": general_canonical,
            "display_ja": general_display,
            "search_ja": general_search,
            "post_count": general_post,
            "status": general_status,
            "confidence": general_confidence,
            "primary_path": general_primary,
            "secondary_paths": general_secondary,
        },
        "input_sha256": {
            str(profile_path): sha256(profile_path),
            str(fit_path): sha256(fit_path),
            str(general_path): sha256(general_path),
        },
        "output_sha256": {
            str(ledger_path): sha256(ledger_path),
            str(review_path): sha256(review_path),
        },
        "boundaries": {
            "production_special_mutated": "NO",
            "local_catalog_mutated": "NO",
            "issue70_mutated": "NO",
            "userdata_mutated": "NO",
            "ids_deleted_or_renumbered": "NO",
            "automatic_demotion_authority": "NO",
        },
        "note": "Mechanical triage is review prioritization only; human review decides any General-sufficient candidate.",
    }
    summary_path = out_dir / "mechanical_triage_summary_v1.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
