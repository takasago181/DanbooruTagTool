#!/usr/bin/env python3
"""Read-only semantic risk census for Issue #70.

This script never rewrites production translation data. It joins the frozen
Issue #70 runtime results with preserved source evidence, assigns review-risk
signals, and emits audit queues + a ledger template.
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
from typing import Any

DEFAULT_RESULTS = Path("docs/issue70/data/runtime/issue70_translation_results.csv")
DEFAULT_SOURCE = Path("docs/issue70/data/source/issue70_translation_source_with_relations.csv")
DEFAULT_OUT = Path("artifacts/issue70-semantic-audit")
EXPECTED_ROWS = 92739
CATEGORY_BY_ID = {"1": "Artist", "3": "Copyright", "4": "Character"}
CATEGORY_ORDER = {"Copyright": 0, "Character": 1, "Artist": 2}

REQUIRED_RESULT_FIELDS = {
    "row_id", "canonical_tag", "category", "display_ja", "search_ja",
    "translation_status", "translation_note",
}
REQUIRED_SOURCE_FIELDS = {
    "row_id", "canonical_tag", "category", "category_name", "post_count",
    "source_aliases", "verified_aliases", "existing_display_ja",
    "existing_search_ja", "existing_candidate_ja", "existing_rejected_ja",
    "related_copyright_candidates",
}
VALID_STATUS = {"ACCEPTED_AI", "REVIEW_REQUIRED"}
JA_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff々〆ヶ]")
ASCII_ALPHA_RE = re.compile(r"[A-Za-z]")
PAREN_QUALIFIER_RE = re.compile(r"_\(([^()]*)\)$")
WS_RE = re.compile(r"\s+")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            raise SystemExit(f"CSV has no header: {path}")
        return [dict(row) for row in reader]


def require_fields(rows: list[dict[str, str]], fields: set[str], path: Path) -> None:
    actual = set(rows[0]) if rows else set()
    missing = sorted(fields - actual)
    if missing:
        raise SystemExit(f"{path}: missing fields: {missing}")


def norm(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").strip().lower()
    value = value.replace("・", " ").replace("_", " ")
    value = value.replace("（", "(").replace("）", ")")
    return WS_RE.sub(" ", value)


def split_pipe(value: str) -> list[str]:
    return [part.strip() for part in (value or "").split("|") if part.strip()]


def uniq_norm(values: list[str]) -> set[str]:
    return {norm(x) for x in values if norm(x)}


def contains_ja(value: str) -> bool:
    return bool(JA_RE.search(value or ""))


def is_ascii_alpha(value: str) -> bool:
    return bool(value) and value.isascii() and bool(ASCII_ALPHA_RE.search(value))


def balanced_brackets(value: str) -> bool:
    pairs = [("(", ")"), ("（", "）"), ("[", "]"), ("【", "】")]
    return all((value or "").count(a) == (value or "").count(b) for a, b in pairs)


def sha_rank(seed: str, row_id: str) -> str:
    return hashlib.sha256(f"{seed}|{row_id}".encode("utf-8")).hexdigest()


def add_flag(record: dict[str, Any], flag: str, weight: int) -> None:
    if flag not in record["risk_flags"]:
        record["risk_flags"].append(flag)
        record["risk_score"] += weight


def top_related(value: str) -> tuple[str, str, str]:
    if not value:
        return "", "", ""
    try:
        items = json.loads(value)
    except json.JSONDecodeError:
        return "", "", ""
    if not isinstance(items, list) or not items:
        return "", "", ""
    first = items[0] if isinstance(items[0], dict) else {}
    return (
        str(first.get("copyright") or ""),
        str(first.get("co_posts") or ""),
        str(first.get("character_coverage") or ""),
    )


def evidence_terms(source: dict[str, str], rejected: bool = False) -> list[str]:
    fields = ("existing_rejected_ja",) if rejected else (
        "existing_display_ja", "existing_search_ja", "existing_candidate_ja"
    )
    terms: list[str] = []
    for field in fields:
        terms.extend(split_pipe(source.get(field, "")))
    return terms


def base_record(result: dict[str, str], source: dict[str, str]) -> dict[str, Any]:
    category_name = source.get("category_name") or CATEGORY_BY_ID.get(result["category"], result["category"])
    top_cp, top_cp_posts, top_cp_coverage = top_related(source.get("related_copyright_candidates", ""))
    try:
        post_count = int(source.get("post_count") or 0)
    except ValueError:
        post_count = 0
    return {
        "row_id": result["row_id"],
        "canonical_tag": result["canonical_tag"],
        "category": result["category"],
        "category_name": category_name,
        "post_count": post_count,
        "display_ja": result.get("display_ja", "").strip(),
        "search_ja": result.get("search_ja", "").strip(),
        "translation_status": result.get("translation_status", "").strip(),
        "translation_note": result.get("translation_note", "").strip(),
        "source_aliases": source.get("source_aliases", ""),
        "verified_aliases": source.get("verified_aliases", ""),
        "existing_display_ja": source.get("existing_display_ja", ""),
        "existing_search_ja": source.get("existing_search_ja", ""),
        "existing_candidate_ja": source.get("existing_candidate_ja", ""),
        "existing_rejected_ja": source.get("existing_rejected_ja", ""),
        "related_copyright_top1": top_cp,
        "related_copyright_top1_posts": top_cp_posts,
        "related_copyright_top1_coverage": top_cp_coverage,
        "risk_flags": [],
        "risk_score": 0,
        "impact_tier": "",
        "audit_bucket": "",
    }


def score_row(record: dict[str, Any]) -> None:
    display = record["display_ja"]
    search = record["search_ja"]
    canonical = record["canonical_tag"]
    category = record["category_name"]

    if record["translation_status"] == "REVIEW_REQUIRED":
        add_flag(record, "STATUS_REVIEW_REQUIRED", 0)
    if not display:
        add_flag(record, "EMPTY_DISPLAY", 20)
    if "\ufffd" in display or "\ufffd" in search:
        add_flag(record, "UNICODE_REPLACEMENT_CHAR", 20)
    if "_" in display or "|" in display:
        add_flag(record, "RAW_TAG_SYNTAX_IN_DISPLAY", 10)
    if not balanced_brackets(display) or not balanced_brackets(search):
        add_flag(record, "UNBALANCED_BRACKETS", 6)

    search_terms = split_pipe(search)
    search_norm = uniq_norm(search_terms)
    if display and norm(display) not in search_norm:
        add_flag(record, "DISPLAY_MISSING_FROM_SEARCH", 3)
    if len(search_terms) > 8:
        add_flag(record, "SEARCH_TOO_MANY_TERMS", 2)
    if len(search_norm) != len(search_terms):
        add_flag(record, "DUPLICATE_SEARCH_TERM", 1)

    display_norm = norm(display)
    canonical_plain = norm(PAREN_QUALIFIER_RE.sub("", canonical))
    if display_norm and display_norm in {norm(canonical), canonical_plain}:
        add_flag(record, "DISPLAY_CANONICAL_LIKE", 3 if category != "Artist" else 1)
    if category in {"Character", "Copyright"} and is_ascii_alpha(display):
        add_flag(record, "ASCII_ONLY_DISPLAY_NON_ARTIST", 2)

    qualifier = PAREN_QUALIFIER_RE.search(canonical)
    if qualifier and category in {"Character", "Copyright"}:
        if not any(ch in display + search for ch in "()（）"):
            add_flag(record, "DISAMBIGUATOR_NOT_VISIBLE", 1)

    accepted_evidence = evidence_terms(record, rejected=False)
    rejected_evidence = evidence_terms(record, rejected=True)
    accepted_norm = uniq_norm(accepted_evidence)
    rejected_norm = uniq_norm(rejected_evidence)

    if display_norm and display_norm in rejected_norm:
        add_flag(record, "DISPLAY_MATCHES_REJECTED_JA", 12)
    if search_norm & rejected_norm:
        add_flag(record, "SEARCH_CONTAINS_REJECTED_JA", 8)

    current_all = {display_norm} | search_norm
    source_ja_norm = uniq_norm([x for x in accepted_evidence if contains_ja(x)])
    if source_ja_norm and not (current_all & source_ja_norm):
        add_flag(record, "NO_SOURCE_JA_EVIDENCE_OVERLAP", 3)

    if category == "Artist" and contains_ja(display) and display_norm not in accepted_norm:
        add_flag(record, "ARTIST_JA_DISPLAY_UNSUPPORTED_BY_SOURCE", 3)
    if category in {"Character", "Copyright"} and contains_ja(display) and display_norm not in accepted_norm:
        add_flag(record, "JA_DISPLAY_NOT_EXACT_SOURCE_EVIDENCE", 1)
    if category == "Character" and not record["related_copyright_top1"]:
        add_flag(record, "CHARACTER_NO_COPYRIGHT_CONTEXT", 1)
    if len(display) > 80:
        add_flag(record, "DISPLAY_UNUSUALLY_LONG", 2)
    if len(search) > 400:
        add_flag(record, "SEARCH_UNUSUALLY_LONG", 2)


def assign_impact(records: list[dict[str, Any]]) -> None:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        groups[row["category_name"]].append(row)
    for rows in groups.values():
        rows.sort(key=lambda r: (-r["post_count"], r["row_id"]))
        total = len(rows)
        top1 = max(1, math.ceil(total * 0.01))
        top10 = max(top1, math.ceil(total * 0.10))
        for index, row in enumerate(rows):
            if index < top1:
                row["impact_tier"] = "TOP_1_PERCENT"
            elif index < top10:
                row["impact_tier"] = "TOP_10_PERCENT"
            else:
                row["impact_tier"] = "REST"


def add_duplicate_display_flags(records: list[dict[str, Any]]) -> None:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        key = (row["category_name"], norm(row["display_ja"]))
        if key[1]:
            groups[key].append(row)
    for (category, _), rows in groups.items():
        if len({r["canonical_tag"] for r in rows}) < 2:
            continue
        weight = 4 if category in {"Character", "Copyright"} else 2
        for row in rows:
            add_flag(row, "DUPLICATE_DISPLAY_WITHIN_CATEGORY", weight)


def is_accepted_risk(row: dict[str, Any]) -> bool:
    if row["translation_status"] != "ACCEPTED_AI":
        return False
    critical = {
        "DISPLAY_MATCHES_REJECTED_JA", "SEARCH_CONTAINS_REJECTED_JA",
        "RAW_TAG_SYNTAX_IN_DISPLAY", "UNICODE_REPLACEMENT_CHAR",
        "UNBALANCED_BRACKETS", "DUPLICATE_DISPLAY_WITHIN_CATEGORY",
    }
    flags = set(row["risk_flags"])
    return (
        row["impact_tier"] == "TOP_1_PERCENT"
        or bool(flags & critical)
        or row["risk_score"] >= 4
    )


def choose_sample(records: list[dict[str, Any]], accepted_risk_ids: set[str], per_category: int, seed: str) -> list[dict[str, Any]]:
    chosen: list[dict[str, Any]] = []
    for category in ("Copyright", "Character", "Artist"):
        pool = [
            r for r in records
            if r["category_name"] == category
            and r["translation_status"] == "ACCEPTED_AI"
            and r["row_id"] not in accepted_risk_ids
        ]
        top10 = [r for r in pool if r["impact_tier"] == "TOP_10_PERCENT"]
        rest = [r for r in pool if r["impact_tier"] == "REST"]
        n_top10 = min(len(top10), max(1, per_category // 3))
        n_rest = min(len(rest), per_category - n_top10)
        top10.sort(key=lambda r: sha_rank(seed + "|top10", r["row_id"]))
        rest.sort(key=lambda r: sha_rank(seed + "|rest", r["row_id"]))
        chosen.extend(top10[:n_top10])
        chosen.extend(rest[:n_rest])
    return chosen


OUTPUT_FIELDS = [
    "row_id", "canonical_tag", "category", "category_name", "post_count",
    "display_ja", "search_ja", "translation_status", "translation_note",
    "risk_score", "risk_flags", "impact_tier", "audit_bucket",
    "source_aliases", "verified_aliases", "existing_display_ja",
    "existing_search_ja", "existing_candidate_ja", "existing_rejected_ja",
    "related_copyright_top1", "related_copyright_top1_posts",
    "related_copyright_top1_coverage",
]
LEDGER_FIELDS = OUTPUT_FIELDS + [
    "audit_verdict", "proposed_display_ja", "proposed_search_ja",
    "reason_code", "confidence", "evidence_refs", "pattern_id",
    "audit_note", "approval_status",
]


def serializable(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    out["risk_flags"] = " | ".join(out.get("risk_flags", []))
    return out


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(serializable(row))


def audit_sort(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        CATEGORY_ORDER.get(row["category_name"], 99),
        0 if row["translation_status"] == "REVIEW_REQUIRED" else 1,
        0 if row["impact_tier"] == "TOP_1_PERCENT" else 1,
        -row["risk_score"], -row["post_count"], row["row_id"],
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--sample-per-category", type=int, default=300)
    parser.add_argument("--seed", default="issue70-semantic-final-v1")
    args = parser.parse_args()

    results = read_csv(args.results)
    source_rows = read_csv(args.source)
    require_fields(results, REQUIRED_RESULT_FIELDS, args.results)
    require_fields(source_rows, REQUIRED_SOURCE_FIELDS, args.source)
    if len(results) != EXPECTED_ROWS or len(source_rows) != EXPECTED_ROWS:
        raise SystemExit(f"row count mismatch: results={len(results)} source={len(source_rows)} expected={EXPECTED_ROWS}")

    source_by_id = {r["row_id"]: r for r in source_rows}
    if len(source_by_id) != EXPECTED_ROWS:
        raise SystemExit("source row_id is not unique")

    records: list[dict[str, Any]] = []
    for result in results:
        if result["translation_status"] not in VALID_STATUS:
            raise SystemExit(f"invalid status {result['translation_status']}: {result['row_id']}")
        source = source_by_id.get(result["row_id"])
        if source is None:
            raise SystemExit(f"source row missing: {result['row_id']}")
        if source["canonical_tag"] != result["canonical_tag"] or source["category"] != result["category"]:
            raise SystemExit(f"identity mismatch: {result['row_id']}")
        record = base_record(result, source)
        score_row(record)
        records.append(record)

    assign_impact(records)
    add_duplicate_display_flags(records)
    review = [r for r in records if r["translation_status"] == "REVIEW_REQUIRED"]
    accepted_risk = [r for r in records if is_accepted_risk(r)]
    accepted_risk_ids = {r["row_id"] for r in accepted_risk}
    sample = choose_sample(records, accepted_risk_ids, args.sample_per_category, args.seed)
    sample_ids = {r["row_id"] for r in sample}

    for row in records:
        if row["translation_status"] == "REVIEW_REQUIRED":
            row["audit_bucket"] = "REVIEW_REQUIRED"
        elif row["row_id"] in accepted_risk_ids:
            row["audit_bucket"] = "ACCEPTED_RISK"
        elif row["row_id"] in sample_ids:
            row["audit_bucket"] = "ACCEPTED_CLEAN_SAMPLE"
        else:
            row["audit_bucket"] = "NOT_QUEUED"

    review.sort(key=audit_sort)
    accepted_risk.sort(key=audit_sort)
    sample.sort(key=audit_sort)
    ledger_map: dict[str, dict[str, Any]] = {}
    for row in review + accepted_risk + sample:
        ledger_map[row["row_id"]] = row
    ledger = sorted(ledger_map.values(), key=audit_sort)

    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / "review_required.csv", review, OUTPUT_FIELDS)
    write_csv(out / "accepted_risk.csv", accepted_risk, OUTPUT_FIELDS)
    write_csv(out / "accepted_clean_sample.csv", sample, OUTPUT_FIELDS)
    write_csv(out / "audit_ledger_template.csv", ledger, LEDGER_FIELDS)

    flag_counts = Counter()
    for row in records:
        flag_counts.update(row["risk_flags"])

    def cat_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
        counter = Counter(r["category_name"] for r in rows)
        return {name: counter.get(name, 0) for name in ("Character", "Copyright", "Artist")}

    summary = {
        "format_version": 1,
        "issue": 70,
        "mode": "read_only_semantic_risk_census",
        "production_modified": False,
        "baseline": {
            "expected_rows": EXPECTED_ROWS,
            "results_path": str(args.results),
            "source_path": str(args.source),
        },
        "totals": {
            "rows_scanned": len(records),
            "review_required": len(review),
            "accepted_ai": sum(r["translation_status"] == "ACCEPTED_AI" for r in records),
            "accepted_risk": len(accepted_risk),
            "accepted_clean_sample": len(sample),
            "unique_audit_ledger_rows": len(ledger),
        },
        "category_counts": {
            "review_required": cat_counts(review),
            "accepted_risk": cat_counts(accepted_risk),
            "accepted_clean_sample": cat_counts(sample),
            "ledger": cat_counts(ledger),
        },
        "risk_flag_counts": dict(sorted(flag_counts.items(), key=lambda x: (-x[1], x[0]))),
        "selection_policy": {
            "review_required": "all rows",
            "accepted_risk": "TOP_1_PERCENT impact OR critical flag OR risk_score >= 4",
            "accepted_clean_sample": f"deterministic {args.sample_per_category}/category target outside accepted-risk; 1/3 TOP_10_PERCENT and 2/3 REST",
            "seed": args.seed,
        },
        "next_step": "semantic audit the ledger; do not apply production corrections until the ledger and pattern expansion are complete",
    }
    (out / "risk_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
