#!/usr/bin/env python3
"""Issue #179 full Character/Copyright quality census.

Read-only audit over the original 44,426 Character/Copyright rows.  Historical
Issue #70 scope/relation data is treated as provenance/evidence only.

Outputs are triage artifacts.  No source/runtime/production file is modified.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / "docs/issue70/data/runtime/issue70_catalog_overlay.csv"
FINAL = ROOT / "docs/issue70/data/runtime/issue70_catalog_overlay_2d_final.csv"
SCOPE = ROOT / "docs/issue70/scope/full_scope_ledger.csv"
FIXES = ROOT / "docs/issue70/finalization/FINAL_SEMANTIC_FIXES.csv"
DEFAULT_OUT = ROOT / "artifacts/issue179-quality-census"

EXPECTED = {"Character": 35890, "Copyright": 8536}
EXPECTED_TOTAL = sum(EXPECTED.values())
FINAL_EXPECTED = {"Character": 35278, "Copyright": 7616}

KNOWN_REGRESSIONS = {
    "hatsune_miku",
    "gotoh_hitori",
    "dawn_(pokemon)",
    "pikachu",
    "ikazuchi_(kancolle)",
    "inazuma_(kancolle)",
    "shirakami_fubuki",
    "kirby",
    "cyrene_(demiurge)_(honkai:_star_rail)",
    "cyrene_(philia093)_(honkai:_star_rail)",
    "aria_(human)_(zenless_zone_zero)",
    "perlica_(arknights)",
    "spider-man_(original_suit)",
    "luciana_de_montefio",
    "sameko_saba",
    "kaito_(vocaloid)",
    "irys_(hololive)",
    "pokemon",
    "vocaloid",
    "kantai_collection",
    "bocchi_the_rock!",
    "hololive",
}

NON_IDENTITY_SEARCH_RE = re.compile(
    r"(?:イラスト|ファンアート|fanart|fan_art|の日(?:$|\s)|^絵[^\s]{2,})",
    re.IGNORECASE,
)
PAREN_GROUP_RE = re.compile(r"（([^）]*)）|\(([^()]*)\)")
ASCII_LOWER_WORD_RE = re.compile(r"[a-z]{3,}")


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames:
            raise SystemExit(f"missing header: {path}")
        return list(reader.fieldnames), list(reader)


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").lower().replace("_", " ")
    return " ".join(value.split())


def split_pipe(value: str) -> list[str]:
    return [x.strip() for x in (value or "").split("|") if x.strip()]


def unique_norm_terms(value: str) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for term in split_pipe(value):
        n = norm(term)
        if n and n not in seen:
            seen.add(n)
            out.append(term)
    return out


def contains_ja(value: str) -> bool:
    for ch in value:
        if "\u3040" <= ch <= "\u30ff" or "\u3400" <= ch <= "\u9fff":
            return True
    return False


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def percentile_threshold(values: list[int], pct: float) -> int:
    if not values:
        return 0
    xs = sorted(values)
    idx = min(len(xs) - 1, max(0, math.ceil((len(xs) - 1) * pct)))
    return xs[idx]


def bracket_mismatch(value: str) -> bool:
    return value.count("(") != value.count(")") or value.count("（") != value.count("）")


def qualifier_count(value: str) -> int:
    return len(PAREN_GROUP_RE.findall(value or ""))


def mixed_ascii_qualifier(value: str) -> bool:
    if not contains_ja(value):
        return False
    for match in PAREN_GROUP_RE.finditer(value):
        q = next((g for g in match.groups() if g is not None), "")
        if q and not contains_ja(q) and ASCII_LOWER_WORD_RE.search(q):
            return True
    return False


def load_population() -> tuple[list[dict[str, str]], dict[str, dict[str, str]], dict[str, dict[str, str]], set[str]]:
    _, original_all = read_csv(ORIGINAL)
    rows = [r for r in original_all if (r.get("category_name") or "").strip() in EXPECTED]
    counts = Counter((r.get("category_name") or "").strip() for r in rows)
    if len(rows) != EXPECTED_TOTAL or dict(counts) != EXPECTED:
        raise SystemExit(f"population drift: total={len(rows)} counts={dict(counts)}")
    ids = [r["row_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate row_id in audit population")

    _, final_all = read_csv(FINAL)
    final_rows = [r for r in final_all if (r.get("category_name") or "").strip() in EXPECTED]
    final_counts = Counter((r.get("category_name") or "").strip() for r in final_rows)
    if dict(final_counts) != FINAL_EXPECTED:
        raise SystemExit(f"final runtime population drift: {dict(final_counts)}")
    final_by_id = {r["row_id"]: r for r in final_rows}

    _, scope_rows = read_csv(SCOPE)
    scope_by_id = {r["row_id"]: r for r in scope_rows}
    if len(scope_by_id) != EXPECTED_TOTAL:
        raise SystemExit(f"scope ledger drift: {len(scope_by_id)} != {EXPECTED_TOTAL}")

    _, fix_rows = read_csv(FIXES)
    fix_ids = {(r.get("row_id") or "").strip() for r in fix_rows if (r.get("row_id") or "").strip()}
    return rows, final_by_id, scope_by_id, fix_ids


def build_collision_indexes(records: list[dict[str, object]]) -> tuple[dict[tuple[str, str], set[str]], dict[tuple[str, str], set[str]], dict[tuple[str, str], set[str]]]:
    display_index: dict[tuple[str, str], set[str]] = defaultdict(set)
    search_index: dict[tuple[str, str], set[str]] = defaultdict(set)
    alias_index: dict[tuple[str, str], set[str]] = defaultdict(set)

    for r in records:
        category = str(r["category"])
        rid = str(r["row_id"])
        dn = norm(str(r["display_ja"]))
        if dn:
            display_index[(category, dn)].add(rid)
        for term in unique_norm_terms(str(r["search_ja"])):
            search_index[(category, norm(term))].add(rid)
        for term in unique_norm_terms(str(r["aliases"])):
            alias_index[(category, norm(term))].add(rid)
    return display_index, search_index, alias_index


def max_collision(index: dict[tuple[str, str], set[str]], category: str, values: list[str], rid: str) -> int:
    best = 0
    for value in values:
        n = norm(value)
        if not n:
            continue
        others = index.get((category, n), set()) - {rid}
        best = max(best, len(others))
    return best


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    source_rows, final_by_id, scope_by_id, fix_ids = load_population()

    thresholds: dict[str, dict[str, int]] = {}
    for category in EXPECTED:
        values = [int(r.get("post_count") or 0) for r in source_rows if r["category_name"] == category]
        thresholds[category] = {
            "p50": percentile_threshold(values, 0.50),
            "p90": percentile_threshold(values, 0.90),
            "p99": percentile_threshold(values, 0.99),
        }

    records: list[dict[str, object]] = []
    for src in source_rows:
        rid = src["row_id"]
        category = src["category_name"]
        current = final_by_id.get(rid)
        surface = current if current is not None else src
        scope = scope_by_id.get(rid, {})
        scope_source = (scope.get("decision_source") or "").strip()
        relation_derived_scope = scope_source.startswith("DOMINANT_COPYRIGHT_")
        records.append({
            "row_id": rid,
            "canonical_tag": src["canonical_tag"],
            "category": category,
            "post_count": int(src.get("post_count") or 0),
            "in_current_runtime": current is not None,
            "translation_status": (src.get("translation_status") or "").strip(),
            "display_ja": (surface.get("display_ja") or "").strip(),
            "search_ja": (surface.get("search_ja") or "").strip(),
            "aliases": (src.get("aliases") or "").strip(),
            "old_related_copyright": (src.get("related_copyright") or "").strip(),
            "old_media_scope": (scope.get("media_scope") or "").strip(),
            "old_scope_source": scope_source,
            "old_scope_relation_derived": relation_derived_scope,
            "touched_by_semantic_fix": rid in fix_ids,
        })

    display_index, search_index, alias_index = build_collision_indexes(records)

    flag_counts: Counter[str] = Counter()
    band_counts: Counter[str] = Counter()
    by_category_band: dict[str, Counter[str]] = {c: Counter() for c in EXPECTED}
    scope_authority_counts: Counter[str] = Counter()

    for r in records:
        flags: list[str] = []
        score = 0
        display = str(r["display_ja"])
        search = str(r["search_ja"])
        aliases = str(r["aliases"])
        category = str(r["category"])
        rid = str(r["row_id"])
        canonical = str(r["canonical_tag"])
        translation_status = str(r["translation_status"])

        def add(flag: str, weight: int) -> None:
            nonlocal score
            if flag not in flags:
                flags.append(flag)
                score += weight

        if not display:
            add("DISPLAY_EMPTY", 10)
        if "_" in display:
            add("DISPLAY_UNDERSCORE", 5)
        if bracket_mismatch(display):
            add("DISPLAY_BRACKET_MISMATCH", 8)
        qcount = qualifier_count(display)
        if qcount >= 2:
            add("DISPLAY_MULTI_QUALIFIER", 2)
        if mixed_ascii_qualifier(display):
            add("DISPLAY_MIXED_ASCII_QUALIFIER", 5)

        display_groups = [
            next((g for g in m.groups() if g is not None), "")
            for m in PAREN_GROUP_RE.finditer(display)
        ]
        if "_(female)" in canonical.lower() and any("男性" in g for g in display_groups):
            add("DISPLAY_SEX_QUALIFIER_MISMATCH", 10)
        if "_(male)" in canonical.lower() and any("女性" in g for g in display_groups):
            add("DISPLAY_SEX_QUALIFIER_MISMATCH", 10)

        # #177 invalidated old co-occurrence as ownership authority.  An
        # unqualified Character canonical that gained a work/context suffix in
        # the historical semantic-fix pass therefore needs independent review.
        if (
            category == "Character"
            and not re.search(r"_\([^()]+\)$", canonical)
            and qcount > 0
            and bool(r["touched_by_semantic_fix"])
        ):
            add("DISPLAY_ADDED_CONTEXT_UNQUALIFIED", 3)

        if (
            translation_status == "REVIEW_REQUIRED"
            and norm(display) == norm(canonical)
            and ("_" in canonical or "(" in canonical)
        ):
            add("DISPLAY_CANONICAL_FALLBACK_REVIEW", 3)

        display_collision = max_collision(display_index, category, [display], rid)
        if display_collision:
            add("DISPLAY_COLLISION", 3)

        raw_search_terms = split_pipe(search)
        normalized_search = [norm(x) for x in raw_search_terms if norm(x)]
        if len(normalized_search) != len(set(normalized_search)):
            add("SEARCH_DUPLICATE_TERM", 1)
        search_collision = max_collision(search_index, category, raw_search_terms, rid)
        if search_collision:
            add("SEARCH_COLLISION", 3)
        if any(
            NON_IDENTITY_SEARCH_RE.search(term)
            for term in raw_search_terms
            if norm(term) != norm(display)
        ):
            add("SEARCH_NON_IDENTITY_SIGNAL", 4)

        raw_aliases = split_pipe(aliases)
        alias_collision = max_collision(alias_index, category, raw_aliases, rid)
        if alias_collision:
            add("ALIAS_COLLISION", 2)

        band = "HIGH_RISK" if score >= 8 else "CHECK" if score >= 3 else "CLEAR"
        t = thresholds[category]
        post_count = int(r["post_count"])
        if post_count >= t["p99"]:
            impact = "TOP_1_PERCENT"
        elif post_count >= t["p90"]:
            impact = "TOP_10_PERCENT"
        elif post_count >= t["p50"]:
            impact = "UPPER_HALF"
        else:
            impact = "LOWER_HALF"

        if bool(r["old_scope_relation_derived"]):
            scope_authority = "LEGACY_RELATION_DERIVED"
        elif str(r["old_scope_source"]):
            scope_authority = "DIRECT_OR_MANUAL"
        else:
            scope_authority = "UNKNOWN"

        scope_recheck = ""
        if scope_authority == "LEGACY_RELATION_DERIVED":
            scope_recheck = "HIGH" if not bool(r["in_current_runtime"]) else "CHECK"

        r.update({
            "qualifier_count": qcount,
            "display_collision_other_rows": display_collision,
            "search_collision_other_rows": search_collision,
            "alias_collision_other_rows": alias_collision,
            "risk_flags": "|".join(flags),
            "risk_score": score,
            "quality_band": band,
            "impact_band": impact,
            "scope_authority": scope_authority,
            "scope_recheck": scope_recheck,
            "priority_score": score * 1_000_000 + min(post_count, 999_999),
        })
        for f in flags:
            flag_counts[f] += 1
        band_counts[band] += 1
        by_category_band[category][band] += 1
        scope_authority_counts[scope_authority] += 1

    census_fields = [
        "row_id", "canonical_tag", "category", "post_count", "in_current_runtime",
        "translation_status", "display_ja", "search_ja", "aliases",
        "old_media_scope", "old_scope_source", "old_scope_relation_derived",
        "scope_authority", "scope_recheck", "touched_by_semantic_fix",
        "qualifier_count", "display_collision_other_rows",
        "search_collision_other_rows", "alias_collision_other_rows",
        "risk_flags", "risk_score", "quality_band", "impact_band", "priority_score",
    ]

    def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
        with path.open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            for row in rows:
                writer.writerow({f: row.get(f, "") for f in fields})

    write_csv(out / "quality_census.csv", census_fields, records)

    # Clean controls: CLEAR rows sampled reproducibly across category + impact band.
    clean_candidates = [r for r in records if r["quality_band"] == "CLEAR"]
    clean_selected: list[dict[str, object]] = []
    for category in EXPECTED:
        for impact in ("TOP_1_PERCENT", "TOP_10_PERCENT", "UPPER_HALF", "LOWER_HALF"):
            bucket = [r for r in clean_candidates if r["category"] == category and r["impact_band"] == impact]
            bucket.sort(key=lambda r: stable_hash(f'clean|{r["row_id"]}|{r["canonical_tag"]}'))
            clean_selected.extend(bucket[:13])
    # Dedupe and cap exactly 100 when possible.
    clean_map: dict[str, dict[str, object]] = {}
    for r in clean_selected:
        clean_map[str(r["row_id"])] = r
    if len(clean_map) < 100:
        rest = [r for r in clean_candidates if str(r["row_id"]) not in clean_map]
        rest.sort(key=lambda r: stable_hash(f'clean-fill|{r["row_id"]}|{r["canonical_tag"]}'))
        for r in rest:
            clean_map[str(r["row_id"])] = r
            if len(clean_map) >= 100:
                break
    clean_sample = list(clean_map.values())[:100]
    write_csv(out / "clean_control_sample.csv", census_fields, clean_sample)

    # Deterministic 500-row pilot. Reserve clean controls explicitly so
    # heuristic false-positive rate can be measured instead of letting risk
    # candidates consume the full pilot.
    selected: dict[str, dict[str, object]] = {}
    reasons: dict[str, list[str]] = defaultdict(list)
    PILOT_TARGET = 500

    def select(
        candidates: list[dict[str, object]],
        reason: str,
        new_limit: int | None = None,
    ) -> None:
        added = 0
        for r in candidates:
            if len(selected) >= PILOT_TARGET:
                break
            rid = str(r["row_id"])
            if reason not in reasons[rid]:
                reasons[rid].append(reason)
            if rid not in selected:
                selected[rid] = r
                added += 1
                if new_limit is not None and added >= new_limit:
                    break

    known = [r for r in records if str(r["canonical_tag"]) in KNOWN_REGRESSIONS]
    known.sort(key=lambda r: (-int(r["post_count"]), str(r["canonical_tag"])))
    select(known, "KNOWN_REGRESSION")

    # Clean controls are deliberately inserted before heuristic queues.
    # They remain in the final 500-row pilot even when risk queues are large.
    select(clean_sample, "CLEAN_CONTROL", 100)

    risk_sorted = sorted(
        [r for r in records if r["quality_band"] != "CLEAR"],
        key=lambda r: (-int(r["risk_score"]), -int(r["post_count"]), str(r["canonical_tag"])),
    )
    select(risk_sorted, "TOP_RISK", 150)

    collision = [
        r for r in records
        if int(r["display_collision_other_rows"]) or int(r["search_collision_other_rows"]) or int(r["alias_collision_other_rows"])
    ]
    collision.sort(key=lambda r: (-int(r["post_count"]), -int(r["risk_score"]), str(r["canonical_tag"])))
    select(collision, "COLLISION", 80)

    qualifier = [
        r for r in records
        if int(r["qualifier_count"]) >= 2 or "DISPLAY_MIXED_ASCII_QUALIFIER" in str(r["risk_flags"])
    ]
    qualifier.sort(key=lambda r: (-int(r["post_count"]), -int(r["risk_score"]), str(r["canonical_tag"])))
    select(qualifier, "QUALIFIER_COMPLEXITY", 60)

    unqualified_context = [
        r for r in records
        if "DISPLAY_ADDED_CONTEXT_UNQUALIFIED" in str(r["risk_flags"])
    ]
    unqualified_context.sort(key=lambda r: (-int(r["post_count"]), str(r["canonical_tag"])))
    select(unqualified_context, "UNQUALIFIED_CONTEXT_RECHECK", 50)

    copyright_rows = [r for r in records if r["category"] == "Copyright"]
    copyright_rows.sort(key=lambda r: (-int(r["risk_score"]), -int(r["post_count"]), str(r["canonical_tag"])))
    select(copyright_rows, "COPYRIGHT_HIGH_IMPACT", 50)

    touched = [r for r in records if bool(r["touched_by_semantic_fix"])]
    touched.sort(key=lambda r: (-int(r["risk_score"]), -int(r["post_count"]), str(r["canonical_tag"])))
    select(touched, "HISTORICAL_FIX_RECHECK", 60)

    if len(selected) < PILOT_TARGET:
        fill = [r for r in records if str(r["row_id"]) not in selected]
        fill.sort(key=lambda r: stable_hash(f'pilot-fill|{r["row_id"]}|{r["canonical_tag"]}'))
        select(fill, "DETERMINISTIC_FILL", PILOT_TARGET - len(selected))

    pilot = list(selected.values())
    pilot_fields = ["pilot_reasons"] + census_fields
    pilot_rows = []
    for r in pilot:
        row = dict(r)
        row["pilot_reasons"] = "|".join(reasons[str(r["row_id"])])
        pilot_rows.append(row)
    write_csv(out / "pilot_manifest.csv", pilot_fields, pilot_rows)

    summary = {
        "format_version": 1,
        "issue": 179,
        "baseline_main": "bea08712eb691ca867e218d211023d7206b6b7dc",
        "production_modified": False,
        "artist_audit_rows": 0,
        "population": {
            "total": len(records),
            "by_category": dict(Counter(str(r["category"]) for r in records)),
            "current_runtime": dict(Counter(str(r["category"]) for r in records if bool(r["in_current_runtime"]))),
            "excluded_from_current_runtime": dict(Counter(str(r["category"]) for r in records if not bool(r["in_current_runtime"]))),
        },
        "quality_bands": dict(band_counts),
        "quality_bands_by_category": {k: dict(v) for k, v in by_category_band.items()},
        "risk_flag_counts": dict(flag_counts.most_common()),
        "scope_authority_counts": dict(scope_authority_counts),
        "legacy_relation_scope_rows": sum(bool(r["old_scope_relation_derived"]) for r in records),
        "legacy_relation_scope_excluded_rows": sum(bool(r["old_scope_relation_derived"]) and not bool(r["in_current_runtime"]) for r in records),
        "touched_by_historical_semantic_fix": sum(bool(r["touched_by_semantic_fix"]) for r in records),
        "post_count_thresholds": thresholds,
        "pilot_rows": len(pilot_rows),
        "pilot_clean_control_rows": sum("CLEAN_CONTROL" in reasons[str(r["row_id"])] for r in pilot),
        "pilot_known_regression_rows": sum("KNOWN_REGRESSION" in reasons[str(r["row_id"])] for r in pilot),
        "clean_control_rows": len(clean_sample),
        "policy": {
            "heuristic_flags_are_verdicts": False,
            "old_related_copyright_is_authority": False,
            "scope_relation_derived_is_separate_axis": True,
            "artist_excluded": True,
        },
    }
    (out / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
