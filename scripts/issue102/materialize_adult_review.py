#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

# This is a human/product review over the complete bounded omission set.
# Any row not explicitly routed below was still reviewed for this audit question and is
# retained in the ledger as NO_SPECIAL_ADULT_ACTION; that is NOT a verdict that the row
# must never enter product General in a future freshness/update pass.

SPECIAL = {
    "speckled_areolae": (
        "DIRECT_ADULT_ANATOMY",
        "Deep breast/areola morphology is directly aligned with Special discovery; current Danbooru breast taxonomy lists it as a distinct areola description.",
        "current Danbooru breast tag-group evidence + pinned canonical snapshot",
    ),
    "unzipping_another's_clothes": (
        "ADULT_ADJACENT_RELATION",
        "Specific actor-target clothing-state action is harder to discover than generic unzipping/open-clothes and fits Special relation/exposure discovery.",
        "pinned canonical snapshot + product-fit structural review",
    ),
    "cospussy": (
        "DIRECT_EXPLICIT_GENITAL",
        "Explicit niche genital/cosplay concept; current Danbooru new-tag reporting confirms it as a General canonical surface and it is absent from both product dictionaries.",
        "current Danbooru new-tag report + pinned canonical snapshot",
    ),
    "open-chest_straitjacket": (
        "DIRECT_BDSM_RESTRAINT_EXPOSURE",
        "Combines restraint equipment with explicit chest-access/exposure geometry and is a strong deep-fetish discovery concept rather than ordinary clothing.",
        "pinned canonical snapshot + external semantic corroboration for open-chest straitjacket restraint/fetish use",
    ),
}

NEEDS = {
    "offering_collar": (
        "BDSM_ADJACENT_AMBIGUOUS",
        "Potential petplay/BDSM relation concept, but the canonical surface alone does not prove fetish semantics; verify Danbooru definition/examples before Special admission.",
    ),
    "tied_from_afar": (
        "RESTRAINT_ADJACENT_AMBIGUOUS",
        "Likely a remote/off-frame restraint topology concept and appears with ribbon-around-body material, but exact current semantics/status need direct verification before admission.",
    ),
    "outstretched_stomach": (
        "BODY_STATE_AMBIGUOUS",
        "Body-state wording can look fetish-relevant, but current indexed Danbooru context also places it in nonsexual taser/electrocution material; do not classify as adult without definition-level evidence.",
    ),
}

GENERAL = {
    "multiple_cutouts": "Reusable clothing cutout descriptor with exposure relevance, but broad enough for General rather than deep Special.",
    "gender_transitioning_(ftm)": "Current Danbooru body/identity state is useful discovery vocabulary, but it is not an adult/fetish concept by itself; route to General freshness rather than sexual Special.",
    "gender_transitioning_(mtf)": "Current Danbooru body/identity state is useful discovery vocabulary, but it is not an adult/fetish concept by itself; route to General freshness rather than sexual Special.",
    "long_unitard": "Ordinary garment subtype; useful General freshness item, not deep adult Special.",
    "strawberry_print_bra": "Underwear pattern is adult-adjacent but structurally ordinary clothing; General is the appropriate layer.",
    "short_unitard": "Ordinary garment subtype; useful General freshness item, not deep adult Special.",
    "cropped_wetsuit": "Clothing/exposure-adjacent garment variant, but still broad clothing vocabulary suited to General.",
    "sock_tan": "Specific tan-line/body-appearance surface with fetish relevance, but existing Special already has broad tanlines; exact canonical belongs in General unless later evidence supports deep promotion.",
    "black_bike_shorts": "Ordinary clothing/color subtype; General freshness only.",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--omissions", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    rows = read_rows(Path(args.omissions))
    if len(rows) != 108:
        raise SystemExit(f"expected strict omission set of 108 rows, got {len(rows)}")
    tags = [r["canonical_tag"] for r in rows]
    if len(set(tags)) != len(tags):
        raise SystemExit("duplicate canonical tag in omission input")

    routed = set(SPECIAL) | set(NEEDS) | set(GENERAL)
    unknown = routed - set(tags)
    if unknown:
        raise SystemExit(f"review mapping refers to absent omission tags: {sorted(unknown)}")

    reviewed: list[dict[str, object]] = []
    for r in rows:
        tag = r["canonical_tag"]
        if tag in SPECIAL:
            relevance, reason, evidence = SPECIAL[tag]
            decision = "SPECIAL_CANDIDATE"
            confidence = "HIGH"
        elif tag in NEEDS:
            relevance, reason = NEEDS[tag]
            evidence = "pinned canonical snapshot + bounded web/context review; definition-level confirmation still required"
            decision = "NEEDS_SEMANTIC_REVIEW"
            confidence = "MEDIUM"
        elif tag in GENERAL:
            relevance = "ADULT_ADJACENT_OR_NONADULT_GENERAL"
            reason = GENERAL[tag]
            evidence = "pinned canonical snapshot + product-layer review"
            decision = "GENERAL_GAP_CANDIDATE"
            confidence = "HIGH"
        else:
            relevance = "NO_DIRECT_ADULT_FETISH_R18G_SIGNAL"
            reason = (
                "Reviewed in the complete 108-row omission set; no direct adult/fetish/BDSM/body-site/fluid/nonhuman/R18G "
                "Special fit was identified in this pass. Preserve for ordinary General/freshness review; do not treat this as permanent product exclusion."
            )
            evidence = "complete bounded omission human/product review"
            decision = "NO_SPECIAL_ADULT_ACTION"
            confidence = "HIGH"
        reviewed.append({
            "canonical_tag": tag,
            "post_count": int(r["post_count"]),
            "aliases": r.get("aliases", ""),
            "adult_focused_relevance": relevance,
            "decision": decision,
            "confidence": confidence,
            "reason": reason,
            "evidence": evidence,
        })

    counts = Counter(x["decision"] for x in reviewed)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    fields = ["canonical_tag","post_count","aliases","adult_focused_relevance","decision","confidence","reason","evidence"]
    with (out / "adult_focused_review_v1.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(reviewed)
    candidates = [x for x in reviewed if x["decision"] == "SPECIAL_CANDIDATE"]
    with (out / "special_candidate_subset_v1.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(candidates)
    unresolved = [x for x in reviewed if x["decision"] == "NEEDS_SEMANTIC_REVIEW"]
    with (out / "semantic_review_queue_v1.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(unresolved)

    summary = {
        "mode": "ISSUE102_ADULT_FOCUSED_FULL_REVIEW_V1",
        "reviewed_total": len(reviewed),
        "decision_counts": dict(sorted(counts.items())),
        "special_candidate_count": len(candidates),
        "special_candidates": [{"tag": x["canonical_tag"], "post_count": x["post_count"]} for x in candidates],
        "semantic_review_count": len(unresolved),
        "semantic_review_tags": [x["canonical_tag"] for x in unresolved],
        "all_omissions_reviewed_for_adult_fit": "YES",
        "nonadult_no_action_is_permanent_product_exclusion": "NO",
        "automatic_production_promotion": "NO",
        "issue70_mutated": "NO",
        "userdata_mutated": "NO",
        "content_filter_used": "NO",
    }
    (out / "adult_focused_review_summary_v1.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
