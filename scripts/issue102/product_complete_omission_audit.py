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

# Review aid only. These hits NEVER exclude rows from the complete omission set.
ADULT_REVIEW_TERMS = (
    "anal", "anus", "ass", "butt", "rectal", "vagina", "vaginal", "pussy", "vulva",
    "clitoris", "penis", "cock", "dick", "testicle", "balls", "scrot", "urethr", "nipple",
    "breast", "boob", "cleavage", "areola", "nude", "naked", "topless", "bottomless",
    "panties", "underwear", "bra", "sex", "sexual", "intercourse", "penetrat", "insert",
    "masturb", "orgasm", "ejaculat", "cum", "semen", "sperm", "bukkake", "fellatio",
    "blowjob", "handjob", "footjob", "paizuri", "frott", "tribad", "cunniling", "oral",
    "bondage", "bdsm", "bound", "restrain", "gag", "collar", "leash", "shibari", "rope",
    "cuff", "chastity", "dildo", "vibrator", "butt plug", "sex toy", "beads", "tentacle",
    "pregnan", "impregnat", "birth", "lactat", "milk", "urine", "pee", "piss", "feces",
    "scat", "vomit", "saliva", "drool", "blood", "gore", "guro", "wound", "amput",
    "prolapse", "inflation", "vore", "ryona", "molest", "rape", "crotch", "cameltoe",
    "moose knuckle", "upskirt", "downblouse", "see-through", "transparent clothes",
    "crotchless", "micro bikini", "micro panties", "exposed", "genitals", "genital",
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
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for line_no, raw in enumerate(csv.reader(f), start=1):
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
        raise ValueError("source is empty")
    return rows


def read_general(path: Path, expected: int) -> tuple[list[dict[str, str]], str]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != expected:
        raise ValueError(f"product General row count mismatch: expected {expected}, got {len(rows)}")
    if not rows:
        raise ValueError("product General is empty")
    keys = set(rows[0])
    candidates = ("canonical_tag", "CanonicalTag", "canonical", "tag", "Tag")
    field = next((x for x in candidates if x in keys), None)
    if not field:
        raise ValueError(f"cannot identify product General canonical field; fields={sorted(keys)}")
    values = [norm(r.get(field, "")) for r in rows]
    if any(not x for x in values):
        raise ValueError("product General contains blank canonical identity")
    if len(set(values)) != len(values):
        raise ValueError("product General canonical identities are not unique after normalization")
    return rows, field


def profile_is_semantic(row: dict[str, str]) -> bool:
    return (
        (row.get("PromotionStatus") or "").strip().upper() == SEMANTIC_PROMOTION
        or (row.get("MeaningStatus") or "").strip().upper() == SEMANTIC_MEANING
        or SEMANTIC_FLAG in (row.get("SpecialFlags") or "").strip().upper()
    )


def build_alias_map(source_rows: list[dict[str, object]]) -> tuple[dict[str, set[str]], dict[str, str]]:
    canonical_norms = {norm(r["canonical_tag"]) for r in source_rows}
    alias_targets: dict[str, set[str]] = defaultdict(set)
    alias_surface: dict[str, str] = {}
    for row in source_rows:
        target = norm(row["canonical_tag"])
        for alias in split_aliases(row["aliases"]):
            a = norm(alias)
            if not a or a in canonical_norms:
                continue
            alias_targets[a].add(target)
            alias_surface.setdefault(a, alias)
    return alias_targets, alias_surface


def build_special_coverage(
    special_path: Path,
    source_rows: list[dict[str, object]],
    expected: int,
) -> tuple[set[str], dict[str, object]]:
    with special_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != expected:
        raise ValueError(f"Special row count mismatch: expected {expected}, got {len(rows)}")
    ids = [int(r["SpecialID"]) for r in rows]
    if sorted(ids) != list(range(1, expected + 1)):
        raise ValueError("Special IDs are not contiguous 1..expected")

    canonical_norms = {norm(r["canonical_tag"]) for r in source_rows}
    alias_targets, _ = build_alias_map(source_rows)
    covered: set[str] = set()
    stats = Counter()
    unresolved: list[str] = []

    for row in rows:
        if profile_is_semantic(row):
            stats["semantic"] += 1
            continue
        surface = norm(row["Tag"])
        if surface in canonical_norms:
            covered.add(surface)
            stats["exact"] += 1
            continue
        targets = alias_targets.get(surface, set())
        if len(targets) == 1:
            covered.add(next(iter(targets)))
            stats["unique_alias"] += 1
        elif len(targets) > 1:
            stats["ambiguous_alias"] += 1
        else:
            unresolved.append(f"{row['SpecialID']}:{row['Tag']}")

    return covered, {
        "special_rows": len(rows),
        "exact_canonical_rows": stats["exact"],
        "unique_alias_identity_rows": stats["unique_alias"],
        "semantic_rows": stats["semantic"],
        "ambiguous_alias_rows": stats["ambiguous_alias"],
        "unresolved_nonsemantic_rows": unresolved,
    }


def adult_review_hits(tag: str, aliases: str) -> list[str]:
    hay = norm(tag + " " + aliases)
    hits = []
    for term in ADULT_REVIEW_TERMS:
        if norm(term) in hay:
            hits.append(term)
    return sorted(set(hits))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--canonical-source", required=True)
    ap.add_argument("--product-general", required=True)
    ap.add_argument("--special-profile", required=True)
    ap.add_argument("--expected-general", type=int, default=30629)
    ap.add_argument("--expected-special", type=int, default=2983)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    source = read_source(Path(args.canonical_source))
    general_rows, general_field = read_general(Path(args.product_general), args.expected_general)
    general_norms = {norm(r[general_field]) for r in general_rows}
    special_covered, special_stats = build_special_coverage(Path(args.special_profile), source, args.expected_special)

    danbooru_general = [r for r in source if r["category_id"] == "0"]
    omissions: list[dict[str, object]] = []
    for row in danbooru_general:
        n = norm(row["canonical_tag"])
        if n in general_norms or n in special_covered:
            continue
        hits = adult_review_hits(str(row["canonical_tag"]), str(row["aliases"]))
        omissions.append({
            "canonical_tag": row["canonical_tag"],
            "post_count": row["post_count"],
            "aliases": row["aliases"],
            "adult_review_priority": "HIGH" if hits else "UNFLAGGED_REVIEW_REQUIRED",
            "adult_review_hits": ";".join(hits),
            "coverage_status": "PRODUCT_COMPLETE_OMISSION",
            "human_review_status": "REVIEW_REQUIRED",
            "notes": "",
        })
    omissions.sort(key=lambda r: (-int(r["post_count"]), str(r["canonical_tag"])))

    fields = [
        "canonical_tag", "post_count", "aliases", "adult_review_priority", "adult_review_hits",
        "coverage_status", "human_review_status", "notes",
    ]
    out = Path(args.out_dir)
    write_csv(out / "complete_omissions_v1.csv", omissions, fields)
    write_csv(out / "adult_priority_v1.csv", [r for r in omissions if r["adult_review_priority"] == "HIGH"], fields)

    summary = {
        "mode": "ISSUE102_PRODUCT_COMPLETE_OMISSION_AUDIT_V1",
        "source_rows": len(source),
        "danbooru_general_rows": len(danbooru_general),
        "product_general_rows": len(general_rows),
        "product_general_canonical_field": general_field,
        "special": special_stats,
        "product_complete_omission_count": len(omissions),
        "adult_priority_count": sum(r["adult_review_priority"] == "HIGH" for r in omissions),
        "top_20_omissions": [
            {"tag": r["canonical_tag"], "post_count": r["post_count"], "priority": r["adult_review_priority"]}
            for r in omissions[:20]
        ],
        "adult_heuristic_is_exclusion_filter": "NO",
        "all_omissions_require_human_review": "YES",
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
