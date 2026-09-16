#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

SEMANTIC_PROMOTION = "APPROVED_SEMANTIC_ROLE"
SEMANTIC_MEANING = "SEMANTIC_SUPPORT"
SEMANTIC_FLAG = "SEMANTIC_NOT_DIRECT_CANONICAL"

# Review prioritization only. No row is excluded from the complete uncovered inventory
# because it does or does not match these patterns.
DOMAIN_PATTERNS: dict[str, tuple[str, ...]] = {
    "SEX_ACT_RELATION": (
        r"\bsex\b", r"sexual", r"fuck", r"intercourse", r"penetrat", r"masturb", r"orgasm",
        r"fellatio", r"blowjob", r"handjob", r"footjob", r"paizuri", r"frott", r"tribad",
        r"cunniling", r"aniling", r"facesitt", r"gangbang", r"threesome", r"foursome", r"rape",
        r"molest", r"grop", r"crotch grab", r"breast grab", r"nipple tweak", r"sex position",
    ),
    "BREAST_NIPPLE_AREOLA": (
        r"breast", r"boob", r"tit", r"nipple", r"areola", r"cleavage", r"sideboob", r"underboob",
        r"topless", r"oppai", r"paizuri", r"lactat", r"breast milk",
    ),
    "FEMALE_GENITAL": (
        r"vagina", r"vaginal", r"vulva", r"pussy", r"cunt", r"labia", r"clitoris", r"clit",
        r"cervix", r"hymen", r"cameltoe", r"female genital", r"gyaru-oh", r"cospussy",
    ),
    "MALE_GENITAL": (
        r"penis", r"cock", r"dick", r"glans", r"testicle", r"scrot", r"balls?\b", r"prostate",
        r"erection", r"foreskin", r"male genital", r"chastity cage",
    ),
    "ANAL_RECTAL": (
        r"\banal\b", r"anus", r"rectal", r"rectum", r"butt plug", r"asshole", r"prolapse",
        r"gaping", r"enema", r"anal beads", r"anal tail",
    ),
    "INSERTION_BODY_SITE": (
        r"insert", r"insertion", r"penetrat", r"urethr", r"catheter", r"fingering", r"fisted",
        r"fisting", r"object in", r"in anus", r"in vagina", r"in pussy", r"in urethra",
    ),
    "SEX_DEVICE_IMPLEMENT": (
        r"dildo", r"vibrator", r"sex toy", r"onahole", r"butt plug", r"anal beads", r"anal hook",
        r"chastity", r"nipple clamp", r"clamp", r"cock ring", r"penis ring", r"milking machine",
        r"sex machine", r"wooden horse", r"electrostim", r"electro-stim",
    ),
    "BDSM_RESTRAINT": (
        r"bondage", r"bdsm", r"restrain", r"bound", r"shibari", r"rope bondage", r"gag", r"blindfold",
        r"handcuff", r"shackle", r"collar", r"leash", r"straitjacket", r"slave", r"dominatrix",
        r"femdom", r"sadism", r"masoch", r"spanking", r"whipping", r"caning", r"petplay",
    ),
    "FLUID_EXCRETION": (
        r"\bcum\b", r"semen", r"sperm", r"ejaculat", r"bukkake", r"creampie", r"precum", r"urine",
        r"piss", r"pee\b", r"feces", r"faeces", r"scat", r"defecat", r"vomit", r"saliva", r"drool",
        r"lactat", r"breast milk", r"sweat fetish",
    ),
    "REPRODUCTION_PREGNANCY": (
        r"pregnan", r"impregnat", r"insemin", r"birth", r"giving birth", r"cervix", r"uterus",
        r"ovary", r"breeding", r"fertiliz", r"lactat", r"nursing",
    ),
    "NONHUMAN_TENTACLE": (
        r"tentacle", r"slime sex", r"monster sex", r"bestial", r"zooph", r"egg laying", r"oviposition",
        r"parasite", r"vore", r"inflation", r"transformation", r"living clothes", r"living sex toy",
    ),
    "EXPOSURE_FETISH_CLOTHING": (
        r"nude", r"naked", r"topless", r"bottomless", r"no panties", r"panties aside", r"panty pull",
        r"upskirt", r"downblouse", r"see-through", r"transparent clothes", r"crotchless", r"micro bikini",
        r"micro panties", r"breasts out", r"nipple slip", r"areola slip", r"genital", r"exposed",
        r"open-chest", r"unzipping another", r"clothes lift", r"clothing aside",
    ),
    "R18G_INJURY": (
        r"gore", r"guro", r"ryona", r"blood from", r"bleeding", r"wound", r"amput", r"dismember",
        r"decapitat", r"organ", r"guts", r"intestine", r"torture", r"mutilat", r"castrat", r"necroph",
    ),
}

# Opaque/slang/non-English surfaces that are easy to miss with ordinary anatomical words.
OPAQUE_REVIEW_PATTERNS = (
    r"futanari", r"futa\b", r"newhalf", r"josou", r"yaoi", r"yuri", r"ero\b", r"ecchi",
    r"zenra", r"nakadashi", r"paizuri", r"ashikoki", r"sumata", r"teabagging", r"cumswap",
    r"pecfuck", r"oppai", r"cospussy", r"inseki", r"futasub", r"power bottom",
)


def norm(value: object) -> str:
    text = "" if value is None else str(value)
    text = unicodedata.normalize("NFKC", text).strip().casefold().replace("_", " ")
    return " ".join(text.split())


def as_int(value: object) -> int:
    text = "" if value is None else str(value).strip().replace(",", "")
    return int(float(text)) if text else 0


def split_aliases(value: object) -> list[str]:
    return [p.strip() for p in ("" if value is None else str(value)).split(",") if p.strip()]


def read_source(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for line_no, raw in enumerate(csv.reader(handle), start=1):
            if len(raw) != 4:
                raise ValueError(f"source line {line_no}: expected 4 columns, got {len(raw)}")
            tag, category_id, post_count, aliases = raw
            rows.append({
                "canonical_tag": tag.strip(),
                "category_id": category_id.strip(),
                "post_count": as_int(post_count),
                "aliases": aliases.strip(),
            })
    if not rows:
        raise ValueError("canonical source is empty")
    return rows


def profile_is_semantic(row: dict[str, str]) -> bool:
    return (
        (row.get("PromotionStatus") or "").strip().upper() == SEMANTIC_PROMOTION
        or (row.get("MeaningStatus") or "").strip().upper() == SEMANTIC_MEANING
        or SEMANTIC_FLAG in (row.get("SpecialFlags") or "").strip().upper()
    )


def build_alias_targets(source_rows: list[dict[str, object]]) -> dict[str, set[str]]:
    canonical_norms = {norm(r["canonical_tag"]) for r in source_rows}
    targets: dict[str, set[str]] = defaultdict(set)
    for row in source_rows:
        target = norm(row["canonical_tag"])
        for alias in split_aliases(row["aliases"]):
            alias_norm = norm(alias)
            if not alias_norm or alias_norm in canonical_norms:
                continue
            targets[alias_norm].add(target)
    return targets


def build_special_coverage(
    special_path: Path, source_rows: list[dict[str, object]], expected_special: int
) -> tuple[set[str], set[str], dict[str, object]]:
    with special_path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != expected_special:
        raise ValueError(f"Special row count mismatch: expected {expected_special}, got {len(rows)}")
    ids = [int(r["SpecialID"]) for r in rows]
    if sorted(ids) != list(range(1, expected_special + 1)):
        raise ValueError("Special IDs are not exact contiguous 1..expected")

    canonical_norms = {norm(r["canonical_tag"]) for r in source_rows}
    alias_targets = build_alias_targets(source_rows)
    all_surfaces: set[str] = set()
    covered_canonical: set[str] = set()
    stats = Counter()
    unresolved: list[str] = []

    for row in rows:
        surface = norm(row.get("Tag", ""))
        if not surface:
            raise ValueError(f"blank Special tag at ID {row.get('SpecialID')}")
        all_surfaces.add(surface)
        if profile_is_semantic(row):
            stats["semantic"] += 1
            continue
        if surface in canonical_norms:
            covered_canonical.add(surface)
            stats["exact"] += 1
            continue
        targets = alias_targets.get(surface, set())
        if len(targets) == 1:
            covered_canonical.add(next(iter(targets)))
            stats["unique_alias"] += 1
        elif len(targets) > 1:
            stats["ambiguous_alias"] += 1
        else:
            unresolved.append(f"{row.get('SpecialID')}:{row.get('Tag')}")

    return all_surfaces, covered_canonical, {
        "rows": len(rows),
        "exact_canonical_rows": stats["exact"],
        "unique_alias_identity_rows": stats["unique_alias"],
        "semantic_rows": stats["semantic"],
        "ambiguous_alias_rows": stats["ambiguous_alias"],
        "unresolved_nonsemantic_rows": unresolved,
    }


def domain_hits(tag: str, aliases: str) -> tuple[list[str], list[str]]:
    hay = norm(f"{tag} {aliases}")
    domains: list[str] = []
    matched: list[str] = []
    for domain, patterns in DOMAIN_PATTERNS.items():
        local = []
        for pattern in patterns:
            if re.search(pattern, hay, flags=re.IGNORECASE):
                local.append(pattern)
        if local:
            domains.append(domain)
            matched.extend(f"{domain}:{p}" for p in local)
    opaque = [p for p in OPAQUE_REVIEW_PATTERNS if re.search(p, hay, flags=re.IGNORECASE)]
    if opaque:
        domains.append("OPAQUE_ADULT_SURFACE")
        matched.extend(f"OPAQUE:{p}" for p in opaque)
    return sorted(set(domains)), sorted(set(matched))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--canonical-source", required=True)
    parser.add_argument("--special-profile", required=True)
    parser.add_argument("--expected-special", type=int, default=2983)
    parser.add_argument("--top-uncovered", type=int, default=5000)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    source = read_source(Path(args.canonical_source))
    all_surfaces, covered_canonical, special_stats = build_special_coverage(
        Path(args.special_profile), source, args.expected_special
    )
    if special_stats["unresolved_nonsemantic_rows"]:
        raise ValueError(f"unresolved Special identities: {special_stats['unresolved_nonsemantic_rows'][:20]}")

    danbooru_general = [r for r in source if r["category_id"] == "0"]
    uncovered: list[dict[str, object]] = []
    covered_count = 0
    covered_by_surface = 0
    covered_by_identity = 0

    for row in danbooru_general:
        n = norm(row["canonical_tag"])
        if n in covered_canonical:
            covered_count += 1
            covered_by_identity += 1
            continue
        if n in all_surfaces:
            covered_count += 1
            covered_by_surface += 1
            continue
        domains, hits = domain_hits(str(row["canonical_tag"]), str(row["aliases"]))
        uncovered.append({
            "canonical_tag": row["canonical_tag"],
            "post_count": row["post_count"],
            "aliases": row["aliases"],
            "adult_domain_count": len(domains),
            "adult_domains": ";".join(domains),
            "adult_signal_count": len(hits),
            "adult_signals": ";".join(hits),
            "review_priority": "ADULT_FETISH_PRIORITY" if domains else "UNFLAGGED",
            "coverage_status": "GENERAL_CANONICAL_NOT_IN_SPECIAL",
        })

    uncovered.sort(key=lambda r: (-int(r["post_count"]), str(r["canonical_tag"])))
    adult = [r for r in uncovered if r["review_priority"] == "ADULT_FETISH_PRIORITY"]
    adult.sort(key=lambda r: (-int(r["adult_domain_count"]), -int(r["post_count"]), str(r["canonical_tag"])))
    top = uncovered[: max(0, args.top_uncovered)]

    fields = [
        "canonical_tag", "post_count", "aliases", "adult_domain_count", "adult_domains",
        "adult_signal_count", "adult_signals", "review_priority", "coverage_status",
    ]
    out = Path(args.out_dir)
    write_csv(out / "general_not_in_special_v1.csv", uncovered, fields)
    write_csv(out / "adult_fetish_priority_v1.csv", adult, fields)
    write_csv(out / "top_uncovered_by_post_count_v1.csv", top, fields)

    domain_counts = Counter()
    for row in adult:
        for d in str(row["adult_domains"]).split(";"):
            if d:
                domain_counts[d] += 1

    summary = {
        "mode": "ISSUE104_ADULT_GENERAL_GAP_AUDIT_V1",
        "source_rows": len(source),
        "danbooru_general_rows": len(danbooru_general),
        "special": special_stats,
        "general_canonical_covered_by_special": covered_count,
        "covered_by_special_identity_closure": covered_by_identity,
        "covered_by_literal_special_surface": covered_by_surface,
        "general_not_in_special_count": len(uncovered),
        "adult_fetish_priority_count": len(adult),
        "top_uncovered_review_count": len(top),
        "adult_domain_counts": dict(sorted(domain_counts.items())),
        "highest_post_count_uncovered": [
            {"tag": r["canonical_tag"], "post_count": r["post_count"], "adult_domains": r["adult_domains"]}
            for r in uncovered[:50]
        ],
        "highest_post_count_adult_priority": [
            {"tag": r["canonical_tag"], "post_count": r["post_count"], "adult_domains": r["adult_domains"]}
            for r in sorted(adult, key=lambda x: (-int(x["post_count"]), str(x["canonical_tag"])))[:100]
        ],
        "adult_heuristic_is_exclusion_filter": "NO",
        "post_count_is_accept_reject_threshold": "NO",
        "product_general_membership_used_to_exclude": "NO",
        "production_mutation": "NO",
        "issue70_mutated": "NO",
        "userdata_mutated": "NO",
        "pseudo_canonical_created": "NO",
        "content_filter_used": "NO",
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary_v1.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
