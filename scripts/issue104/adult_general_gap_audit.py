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

# Canonical-tag review prioritization only. These patterns NEVER exclude rows from
# the complete uncovered inventory. Patterns are intentionally boundary-aware to
# avoid substring failures such as collarbone->collar, grape->rape, title->tit,
# baseball->ball, or birthday->birth.
DOMAIN_PATTERNS: dict[str, tuple[str, ...]] = {
    "SEX_ACT_RELATION": (
        r"\bsex\b", r"\bsexual\b", r"\bintercourse\b", r"\bfuck(?:ing|ed)?\b",
        r"\bmasturb\w*\b", r"\borgasm\w*\b", r"\bfellatio\b", r"\bblowjob\b",
        r"\bhandjob\b", r"\bfootjob\b", r"\bpaizuri\b", r"\bfrottage\b",
        r"\btribad\w*\b", r"\bcunnilingus\b", r"\banilingus\b", r"\bfacesitting\b",
        r"\bgangbang\b", r"\bthreesome\b", r"\bfoursome\b", r"\brape\b",
        r"\bmolest\w*\b", r"\bgrop\w*\b", r"\bteabagging\b", r"\bcumswap\b",
        r"\bpecfuck\b", r"\bbuttjob\b", r"\bglansjob\b", r"\bhairjob\b",
        r"\bthigh sex\b", r"\barmpit sex\b", r"\bear sex\b", r"\bkneepit sex\b",
    ),
    "BREAST_NIPPLE_AREOLA": (
        r"\bbreasts?\b", r"\bboobs?\b", r"\btits?\b", r"\bnipples?\b",
        r"\bareolae?\b", r"\bcleavage\b", r"\bsideboob\b", r"\bunderboob\b",
        r"\boppai\b", r"\bpaizuri\b", r"\blactat\w*\b", r"\bbreast milk\b",
    ),
    "FEMALE_GENITAL": (
        r"\bvagina\b", r"\bvaginal\b", r"\bvulva\b", r"\bpussy\b", r"\bcunt\b",
        r"\blabia\b", r"\bclitoris\b", r"\bclit\b", r"\bcervix\b", r"\bhymen\b",
        r"\bcameltoe\b", r"\bfemale genitals?\b", r"\bcospussy\b",
    ),
    "MALE_GENITAL": (
        r"\bpenis\b", r"\bcock\b", r"\bdick\b", r"\bglans\b", r"\btesticles?\b",
        r"\bscrotum\b", r"\bprostate\b", r"\berection\b", r"\bforeskin\b",
        r"\bmale genitals?\b",
    ),
    "ANAL_RECTAL": (
        r"\banal\b", r"\banus\b", r"\brectal\b", r"\brectum\b", r"\basshole\b",
        r"\bprolapse\b", r"\bgaping\b", r"\benema\b", r"\bbutt plug\b",
        r"\banal beads\b", r"\banal hook\b", r"\banal tail\b",
    ),
    "INSERTION_BODY_SITE": (
        r"\binsertion\b", r"\binserting\b", r"\bpenetrat\w*\b", r"\burethr\w*\b",
        r"\bcatheter\b", r"\bfingering\b", r"\bfisting\b", r"\bfisted\b",
        r"\bin anus\b", r"\bin vagina\b", r"\bin pussy\b", r"\bin urethra\b",
    ),
    "SEX_DEVICE_IMPLEMENT": (
        r"\bdildo\b", r"\bvibrator\b", r"\bsex toy\b", r"\bonahole\b",
        r"\bbutt plug\b", r"\banal beads\b", r"\banal hook\b", r"\bchastity cage\b",
        r"\bnipple clamps?\b", r"\bcock ring\b", r"\bpenis ring\b",
        r"\bmilking machine\b", r"\bsex machine\b", r"\bwooden horse\b",
        r"\belectrostim\w*\b", r"\belectro stim\w*\b",
    ),
    "BDSM_RESTRAINT": (
        r"\bbondage\b", r"\bbdsm\b", r"\brestrain\w*\b", r"\bbound\b", r"\bshibari\b",
        r"\brope bondage\b", r"\bball gag\b", r"\bgagged\b", r"\bblindfold\w*\b",
        r"\bhandcuffs?\b", r"\bshackles?\b", r"\bleash\b", r"\bstraitjacket\b",
        r"\bslave\b", r"\bdominatrix\b", r"\bfemdom\b", r"\bsadism\b", r"\bmasoch\w*\b",
        r"\bspanking\b", r"\bwhipping\b", r"\bcaning\b", r"\bpetplay\b",
        r"\bchastity\b", r"\bnipple clamps?\b", r"\bwooden horse\b",
    ),
    "FLUID_EXCRETION": (
        r"\bcum\b", r"\bsemen\b", r"\bsperm\b", r"\bejaculat\w*\b", r"\bbukkake\b",
        r"\bcreampie\b", r"\bprecum\b", r"\burine\b", r"\bpiss\b", r"\bpee\b",
        r"\bfeces\b", r"\bfaeces\b", r"\bscat\b", r"\bdefecat\w*\b", r"\bvomit\w*\b",
        r"\bsaliva\b", r"\bdrool\w*\b", r"\blactat\w*\b", r"\bbreast milk\b",
    ),
    "REPRODUCTION_PREGNANCY": (
        r"\bpregnan\w*\b", r"\bimpregnat\w*\b", r"\binseminat\w*\b",
        r"\bgiving birth\b", r"\bchildbirth\b", r"\bcervix\b", r"\buterus\b",
        r"\bovary\b", r"\bbreeding\b", r"\bfertiliz\w*\b", r"\blactat\w*\b",
    ),
    "NONHUMAN_TENTACLE": (
        r"\btentacles?\b", r"\bslime sex\b", r"\bmonster sex\b", r"\bbestial\w*\b",
        r"\bzooph\w*\b", r"\boviposition\b", r"\begg laying\b", r"\bvore\b",
        r"\bliving sex toy\b",
    ),
    "EXPOSURE_FETISH_CLOTHING": (
        r"\bnude\b", r"\bnaked\b", r"\btopless\b", r"\bbottomless\b", r"\bno panties\b",
        r"\bpanties aside\b", r"\bpanty pull\b", r"\bupskirt\b", r"\bdownblouse\b",
        r"\bsee through\b", r"\btransparent clothes\b", r"\bcrotchless\b",
        r"\bmicro bikini\b", r"\bmicro panties\b", r"\bbreasts out\b", r"\bnipple slip\b",
        r"\bareola slip\b", r"\bgenitals?\b", r"\bopen chest\b",
        r"\bunzipping another(?:'s|s)? clothes\b",
    ),
    "R18G_INJURY": (
        r"\bgore\b", r"\bguro\b", r"\bryona\b", r"\bblood from\b", r"\bbleeding\b",
        r"\bwounds?\b", r"\bamput\w*\b", r"\bdismember\w*\b", r"\bdecapitat\w*\b",
        r"\bintestines?\b", r"\btorture\b", r"\bmutilat\w*\b", r"\bcastrat\w*\b",
        r"\bnecroph\w*\b",
    ),
}

OPAQUE_CANONICAL_PATTERNS = (
    r"\bfutanari\b", r"\bfuta\b", r"\bnewhalf\b", r"\bjosou\b", r"\byaoi\b", r"\byuri\b",
    r"\bzenra\b", r"\bnakadashi\b", r"\bpaizuri\b", r"\bashikoki\b", r"\bsumata\b",
    r"\bteabagging\b", r"\bcumswap\b", r"\bpecfuck\b", r"\boppai\b", r"\bcospussy\b",
    r"\binseki\b", r"\bfutasub\b", r"\bpower bottom\b",
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


def scan_text(text: str) -> tuple[list[str], list[str]]:
    hay = norm(text)
    domains: list[str] = []
    matched: list[str] = []
    for domain, patterns in DOMAIN_PATTERNS.items():
        local = [p for p in patterns if re.search(p, hay, flags=re.IGNORECASE)]
        if local:
            domains.append(domain)
            matched.extend(f"{domain}:{p}" for p in local)
    opaque = [p for p in OPAQUE_CANONICAL_PATTERNS if re.search(p, hay, flags=re.IGNORECASE)]
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
        canonical = str(row["canonical_tag"])
        aliases = str(row["aliases"])
        n = norm(canonical)
        if n in covered_canonical:
            covered_count += 1
            covered_by_identity += 1
            continue
        if n in all_surfaces:
            covered_count += 1
            covered_by_surface += 1
            continue

        canonical_domains, canonical_hits = scan_text(canonical)
        alias_domains, alias_hits = scan_text(aliases)
        uncovered.append({
            "canonical_tag": canonical,
            "post_count": row["post_count"],
            "aliases": aliases,
            "canonical_adult_domain_count": len(canonical_domains),
            "canonical_adult_domains": ";".join(canonical_domains),
            "canonical_adult_signal_count": len(canonical_hits),
            "canonical_adult_signals": ";".join(canonical_hits),
            "alias_only_adult_domain_count": len(set(alias_domains) - set(canonical_domains)),
            "alias_adult_domains": ";".join(alias_domains),
            "alias_adult_signals": ";".join(alias_hits),
            "review_priority": "CANONICAL_ADULT_FETISH_PRIORITY" if canonical_domains else (
                "ALIAS_ADULT_SIGNAL_ONLY" if alias_domains else "UNFLAGGED"
            ),
            "coverage_status": "GENERAL_CANONICAL_NOT_IN_SPECIAL",
        })

    uncovered.sort(key=lambda r: (-int(r["post_count"]), str(r["canonical_tag"])))
    canonical_adult = [r for r in uncovered if r["review_priority"] == "CANONICAL_ADULT_FETISH_PRIORITY"]
    canonical_adult.sort(key=lambda r: (-int(r["canonical_adult_domain_count"]), -int(r["post_count"]), str(r["canonical_tag"])))
    alias_signal = [r for r in uncovered if r["review_priority"] == "ALIAS_ADULT_SIGNAL_ONLY"]
    alias_signal.sort(key=lambda r: (-int(r["post_count"]), str(r["canonical_tag"])))
    top = uncovered[: max(0, args.top_uncovered)]

    fields = [
        "canonical_tag", "post_count", "aliases",
        "canonical_adult_domain_count", "canonical_adult_domains",
        "canonical_adult_signal_count", "canonical_adult_signals",
        "alias_only_adult_domain_count", "alias_adult_domains", "alias_adult_signals",
        "review_priority", "coverage_status",
    ]
    out = Path(args.out_dir)
    write_csv(out / "general_not_in_special_v2.csv", uncovered, fields)
    write_csv(out / "adult_fetish_canonical_priority_v2.csv", canonical_adult, fields)
    write_csv(out / "adult_alias_signal_only_v2.csv", alias_signal, fields)
    write_csv(out / "top_uncovered_by_post_count_v2.csv", top, fields)

    domain_counts = Counter()
    for row in canonical_adult:
        for domain in str(row["canonical_adult_domains"]).split(";"):
            if domain:
                domain_counts[domain] += 1

    summary = {
        "mode": "ISSUE104_ADULT_GENERAL_GAP_AUDIT_V2",
        "source_rows": len(source),
        "danbooru_general_rows": len(danbooru_general),
        "special": special_stats,
        "general_canonical_covered_by_special": covered_count,
        "covered_by_special_identity_closure": covered_by_identity,
        "covered_by_literal_special_surface": covered_by_surface,
        "general_not_in_special_count": len(uncovered),
        "canonical_adult_fetish_priority_count": len(canonical_adult),
        "alias_adult_signal_only_count": len(alias_signal),
        "top_uncovered_review_count": len(top),
        "canonical_adult_domain_counts": dict(sorted(domain_counts.items())),
        "highest_post_count_canonical_adult_priority": [
            {
                "tag": r["canonical_tag"],
                "post_count": r["post_count"],
                "adult_domains": r["canonical_adult_domains"],
            }
            for r in sorted(canonical_adult, key=lambda x: (-int(x["post_count"]), str(x["canonical_tag"])))[:150]
        ],
        "adult_heuristic_is_exclusion_filter": "NO",
        "canonical_and_alias_adult_signals_separated": "YES",
        "post_count_is_accept_reject_threshold": "NO",
        "product_general_membership_used_to_exclude": "NO",
        "production_mutation": "NO",
        "issue70_mutated": "NO",
        "userdata_mutated": "NO",
        "pseudo_canonical_created": "NO",
        "content_filter_used": "NO",
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary_v2.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
