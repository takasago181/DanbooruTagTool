#!/usr/bin/env python3
"""Measure Issue #179 reviewed overlay impact on the current product runtime."""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CENSUS = ROOT / "artifacts/issue179-quality-census/quality_census.csv"
PROJECTION = ROOT / "artifacts/issue179-runtime/ISSUE179_RUNTIME_PROJECTION_V1.csv"
OUT = ROOT / "artifacts/issue179-post-overlay-audit"
SUMMARY = OUT / "summary.json"
RESIDUAL = OUT / "RESIDUAL_SEARCH_REGEX_SIGNALS_V1.csv"

PAREN_RE = re.compile(r"（([^）]*)）|\(([^()]*)\)")
ASCII_LOWER_RE = re.compile(r"[a-z]{3,}")
NON_IDENTITY_RE = re.compile(
    r"(?:イラスト|ファンアート|fanart|fan_art|の日(?:$|\s)|^絵[^\s]{2,})",
    re.IGNORECASE,
)
FANDOM_RE = re.compile(
    r"(?:腐|お絵描き|ドット絵部|コッショリ|夢絵|夢小説|夢アカ|fanart|fan_art)",
    re.IGNORECASE,
)
DESCRIPTIVE_RE = re.compile(r"(?:ための|するため)")

def read(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))

def split_pipe(value: str) -> list[str]:
    return [x.strip() for x in (value or "").split("|") if x.strip()]

def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").lower().replace("_", " ")
    return " ".join(value.split())

def has_ja(value: str) -> bool:
    return any("\u3040" <= c <= "\u30ff" or "\u3400" <= c <= "\u9fff" for c in value)

def mixed_ascii_qualifier(value: str) -> bool:
    if not has_ja(value):
        return False
    groups = [
        next(g for g in m.groups() if g is not None)
        for m in PAREN_RE.finditer(value or "")
    ]
    return any(ASCII_LOWER_RE.search(g) for g in groups)

def signals(rows: list[dict[str, str]]) -> dict[str, int]:
    display_index: dict[tuple[str, str], set[str]] = defaultdict(set)
    search_index: dict[tuple[str, str], set[str]] = defaultdict(set)
    duplicate = non_identity = fandom = descriptive = mixed = underscore = 0

    for row in rows:
        rid = row["row_id"]
        category = row["category"]
        display = row["display_ja"]
        search = row["search_ja"]

        if "_" in display:
            underscore += 1
        if mixed_ascii_qualifier(display):
            mixed += 1

        dn = norm(display)
        if dn:
            display_index[(category, dn)].add(rid)

        terms = split_pipe(search)
        normalized = [norm(t) for t in terms if norm(t)]
        if len(normalized) != len(set(normalized)):
            duplicate += 1
        if any(NON_IDENTITY_RE.search(t) for t in terms):
            non_identity += 1
        if any(FANDOM_RE.search(t) for t in terms):
            fandom += 1
        if any(len(t) >= 12 and DESCRIPTIVE_RE.search(t) for t in terms):
            descriptive += 1
        for term in terms:
            tn = norm(term)
            if tn:
                search_index[(category, tn)].add(rid)

    display_collision_ids: set[str] = set()
    for ids in display_index.values():
        if len(ids) > 1:
            display_collision_ids.update(ids)
    search_collision_ids: set[str] = set()
    for ids in search_index.values():
        if len(ids) > 1:
            search_collision_ids.update(ids)

    return {
        "display_underscore_rows": underscore,
        "display_mixed_ascii_qualifier_rows": mixed,
        "search_normalized_duplicate_rows": duplicate,
        "search_non_identity_regex_rows": non_identity,
        "search_fandom_community_regex_rows": fandom,
        "search_descriptive_phrase_rows": descriptive,
        "display_collision_rows": len(display_collision_ids),
        "search_collision_rows": len(search_collision_ids),
    }

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    census = [r for r in read(CENSUS) if r["in_current_runtime"].lower() == "true"]
    if len(census) != 42894:
        raise SystemExit(f"current runtime census drift: {len(census)}")

    projection = {r["row_id"]: r for r in read(PROJECTION)}
    after: list[dict[str, str]] = []
    for src in census:
        row = dict(src)
        change = projection.get(src["row_id"])
        if change:
            if change["has_display"] == "1":
                row["display_ja"] = change["display_ja"]
            if change["has_search"] == "1":
                row["search_ja"] = change["search_ja"]
        after.append(row)

    before = signals(census)
    current = signals(after)
    delta = {key: current[key] - before[key] for key in before}

    if current["search_normalized_duplicate_rows"] != 0:
        raise SystemExit("normalized duplicate search cleanup regressed")
    if current["search_descriptive_phrase_rows"] != 0:
        raise SystemExit("descriptive search cleanup regressed")

    residual_rows: list[dict[str, str]] = []
    for row in after:
        terms = split_pipe(row["search_ja"])
        hits = [
            term for term in terms
            if NON_IDENTITY_RE.search(term) or FANDOM_RE.search(term)
            or (len(term) >= 12 and DESCRIPTIVE_RE.search(term))
        ]
        if hits:
            residual_rows.append({
                "row_id": row["row_id"],
                "canonical_tag": row["canonical_tag"],
                "category": row["category"],
                "post_count": row["post_count"],
                "search_ja": row["search_ja"],
                "regex_hits": " | ".join(hits),
                "disposition": "REVIEW_OR_REGEX_FALSE_POSITIVE",
            })
    with RESIDUAL.open("w", encoding="utf-8-sig", newline="") as fh:
        fields = ["row_id", "canonical_tag", "category", "post_count", "search_ja", "regex_hits", "disposition"]
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(residual_rows)

    summary = {
        "runtime_rows": len(census),
        "character_rows": sum(r["category"] == "Character" for r in census),
        "copyright_rows": sum(r["category"] == "Copyright" for r in census),
        "projection_rows": len(projection),
        "before": before,
        "after": current,
        "delta": delta,
        "residual_regex_signal_rows": len(residual_rows),
        "interpretation": (
            "Collision and mixed-ASCII counts are triage signals, not defects. "
            "Residual regex rows require semantic interpretation because legitimate names "
            "such as Illustrious, Fukawa, Emori, Oekaki Musume and title words can match the regex."
        ),
        "source_data_mutated": False,
        "home_authority_modified": False,
        "production_modified": False,
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))

if __name__ == "__main__":
    main()
