#!/usr/bin/env python3
"""Issue #70 semantic risk census v2.

Category-aware, runtime-aware, read-only semantic screening over all 92,739
Issue #70 rows. The scanner never rewrites production translation data.
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.issue70 import audit_semantic_risk as base

TRAILING_PAREN_RE = re.compile(r"(?:\([^()]*\)|（[^（）]*）)$")


def score_row(record: dict[str, Any]) -> None:
    display = record["display_ja"]
    search = record["search_ja"]
    canonical = record["canonical_tag"]
    category = record["category_name"]

    if record["translation_status"] == "REVIEW_REQUIRED":
        base.add_flag(record, "STATUS_REVIEW_REQUIRED", 0)
    if not display:
        base.add_flag(record, "EMPTY_DISPLAY", 20)
    if "\ufffd" in display or "\ufffd" in search:
        base.add_flag(record, "UNICODE_REPLACEMENT_CHAR", 20)
    if "_" in display or "|" in display:
        base.add_flag(record, "RAW_TAG_SYNTAX_IN_DISPLAY", 10)
    if not base.balanced_brackets(display) or not base.balanced_brackets(search):
        base.add_flag(record, "UNBALANCED_BRACKETS", 6)

    search_terms = base.split_pipe(search)
    search_norm = base.uniq_norm(search_terms)
    # RuntimeCatalogIndex.SearchDocument.Create() indexes entry.Japanese
    # separately from entry.JapaneseSearch. This is diagnostic only.
    if search_terms and display and base.norm(display) not in search_norm:
        base.add_flag(record, "DISPLAY_MISSING_FROM_SEARCH", 0)
    if len(search_terms) > 8:
        base.add_flag(record, "SEARCH_TOO_MANY_TERMS", 2)
    if len(search_norm) != len(search_terms):
        base.add_flag(record, "DUPLICATE_SEARCH_TERM", 1)

    display_norm = base.norm(display)
    canonical_plain = base.norm(base.PAREN_QUALIFIER_RE.sub("", canonical))
    if display_norm and display_norm in {base.norm(canonical), canonical_plain} and category != "Artist":
        base.add_flag(record, "DISPLAY_CANONICAL_LIKE", 1)
    if category in {"Character", "Copyright"} and base.is_ascii_alpha(display):
        base.add_flag(record, "ASCII_ONLY_DISPLAY_NON_ARTIST", 1)

    qualifier = base.PAREN_QUALIFIER_RE.search(canonical)
    if qualifier and category in {"Character", "Copyright"}:
        if not any(ch in display + search for ch in "()（）"):
            base.add_flag(record, "DISAMBIGUATOR_NOT_VISIBLE", 1)

    accepted_evidence = base.evidence_terms(record, rejected=False)
    rejected_evidence = base.evidence_terms(record, rejected=True)
    accepted_norm = base.uniq_norm(accepted_evidence)
    rejected_norm = base.uniq_norm(rejected_evidence)

    if display_norm and display_norm in rejected_norm:
        base.add_flag(record, "DISPLAY_MATCHES_REJECTED_JA", 4)
    if search_norm & rejected_norm:
        base.add_flag(record, "SEARCH_CONTAINS_REJECTED_JA", 4)

    current_all = {display_norm} | search_norm
    source_ja_norm = base.uniq_norm([x for x in accepted_evidence if base.contains_ja(x)])
    if source_ja_norm and not (current_all & source_ja_norm):
        base.add_flag(record, "NO_SOURCE_JA_EVIDENCE_OVERLAP", 2)

    if category == "Artist" and base.contains_ja(display) and display_norm not in accepted_norm:
        base.add_flag(record, "ARTIST_JA_DISPLAY_UNSUPPORTED_BY_SOURCE", 5)
    if category in {"Character", "Copyright"} and base.contains_ja(display) and display_norm not in accepted_norm:
        base.add_flag(record, "JA_DISPLAY_NOT_EXACT_SOURCE_EVIDENCE", 1)
    if category == "Character" and not record["related_copyright_top1"]:
        base.add_flag(record, "CHARACTER_NO_COPYRIGHT_CONTEXT", 1)
    if len(display) > 80:
        base.add_flag(record, "DISPLAY_UNUSUALLY_LONG", 2)
    if len(search) > 400:
        base.add_flag(record, "SEARCH_UNUSUALLY_LONG", 2)


def qualifier_count(tag: str) -> int:
    return tag.count("_(")


def canonical_stem(tag: str) -> str:
    return tag.split("_(", 1)[0]


def identity_display(value: str) -> str:
    value = (value or "").strip()
    while value:
        stripped = TRAILING_PAREN_RE.sub("", value).strip()
        if stripped == value:
            break
        value = stripped
    return value


def add_character_family_flags(records: list[dict[str, Any]]) -> None:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        row["family_base_canonical"] = ""
        row["family_base_display_ja"] = ""
        if row["category_name"] != "Character":
            continue
        stem = canonical_stem(row["canonical_tag"])
        if not stem:
            continue
        key = (stem, row.get("related_copyright_top1") or "")
        groups[key].append(row)

    for rows in groups.values():
        if len(rows) < 2:
            continue
        # The least-qualified, highest-usage row is the best available internal
        # identity anchor. This is evidence for audit, never an automatic fix.
        base_row = min(
            rows,
            key=lambda r: (qualifier_count(r["canonical_tag"]), -r["post_count"], len(r["canonical_tag"]), r["row_id"]),
        )
        base_q = qualifier_count(base_row["canonical_tag"])
        base_identity = identity_display(base_row["display_ja"])
        if not base_identity or len(base.norm(base_identity)) < 2:
            continue
        for row in rows:
            if row is base_row:
                continue
            if qualifier_count(row["canonical_tag"]) <= base_q:
                continue
            row["family_base_canonical"] = base_row["canonical_tag"]
            row["family_base_display_ja"] = base_row["display_ja"]
            current = base.norm(row["display_ja"])
            anchor = base.norm(base_identity)
            if anchor not in current:
                base.add_flag(row, "VARIANT_DISPLAY_MISSING_BASE_IDENTITY", 5)
            elif current in {anchor, base.norm(base_row["display_ja"])}:
                base.add_flag(row, "VARIANT_DISPLAY_LOST_QUALIFIER", 3)


def add_duplicate_display_flags(records: list[dict[str, Any]]) -> None:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        key = (row["category_name"], base.norm(row["display_ja"]))
        if key[1]:
            groups[key].append(row)
    for (category, _), rows in groups.items():
        if len({r["canonical_tag"] for r in rows}) < 2:
            continue
        weight = 3 if category in {"Character", "Copyright"} else 2
        for row in rows:
            base.add_flag(row, "DUPLICATE_DISPLAY_WITHIN_CATEGORY", weight)
    add_character_family_flags(records)


def is_accepted_risk(row: dict[str, Any]) -> bool:
    if row["translation_status"] != "ACCEPTED_AI":
        return False

    flags = set(row["risk_flags"])
    category = row["category_name"]
    impact = row["impact_tier"]

    structural = {
        "RAW_TAG_SYNTAX_IN_DISPLAY",
        "UNICODE_REPLACEMENT_CHAR",
        "UNBALANCED_BRACKETS",
    }
    family = {"VARIANT_DISPLAY_MISSING_BASE_IDENTITY", "VARIANT_DISPLAY_LOST_QUALIFIER"}
    if impact == "TOP_1_PERCENT" or flags & structural or flags & family:
        return True
    if "DUPLICATE_DISPLAY_WITHIN_CATEGORY" in flags:
        return True
    if flags & {"DISPLAY_MATCHES_REJECTED_JA", "SEARCH_CONTAINS_REJECTED_JA"}:
        return True

    if category == "Artist":
        return "ARTIST_JA_DISPLAY_UNSUPPORTED_BY_SOURCE" in flags

    if (
        "JA_DISPLAY_NOT_EXACT_SOURCE_EVIDENCE" in flags
        and "NO_SOURCE_JA_EVIDENCE_OVERLAP" in flags
    ):
        return True
    if (
        impact == "TOP_10_PERCENT"
        and "ASCII_ONLY_DISPLAY_NON_ARTIST" in flags
        and "NO_SOURCE_JA_EVIDENCE_OVERLAP" in flags
    ):
        return True
    return False


def rewrite_summary(out: Path) -> None:
    path = out / "risk_summary.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["format_version"] = 2
    data["mode"] = "read_only_semantic_risk_census_v2_category_runtime_family_aware"
    data["selection_policy"]["accepted_risk"] = (
        "runtime-aware category screening + Character family consistency: all top-1%-impact, "
        "structural/conflict/collision signals, variant rows missing the internal base identity "
        "or qualifier, unsupported Japanese Artist readings, and selected source-evidence gaps. "
        "Blank search_ja and display omission from search_ja are valid."
    )
    data["selection_policy"]["v1_disposition"] = (
        "superseded: v1 over-selected Artist and search fields; v2 is constrained by the actual "
        "RuntimeCatalogIndex search contract and internal Character family evidence"
    )
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def output_path_from_argv() -> Path:
    if "--out" in sys.argv:
        i = sys.argv.index("--out")
        if i + 1 < len(sys.argv):
            return Path(sys.argv[i + 1])
    return base.DEFAULT_OUT


def main() -> int:
    for field in ("family_base_canonical", "family_base_display_ja"):
        if field not in base.OUTPUT_FIELDS:
            base.OUTPUT_FIELDS.append(field)
        if field not in base.LEDGER_FIELDS:
            base.LEDGER_FIELDS.append(field)
    base.score_row = score_row
    base.add_duplicate_display_flags = add_duplicate_display_flags
    base.is_accepted_risk = is_accepted_risk
    rc = base.main()
    rewrite_summary(output_path_from_argv())
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
