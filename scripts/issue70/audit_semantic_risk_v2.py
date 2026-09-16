#!/usr/bin/env python3
"""Issue #70 semantic risk census v2.

This wrapper keeps the v1 I/O/ledger machinery but replaces the deliberately
broad first-pass screening with category-aware rules learned from the first
real 92,739-row census. In particular, blank search_ja and normal Artist
romanization are not treated as defects.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

# Running this file directly makes scripts/issue70 the initial sys.path entry.
# Add repository root explicitly so the shared Issue70 module is importable in
# GitHub Actions and local direct execution alike.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.issue70 import audit_semantic_risk as base


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
    # Blank search_ja is valid in the current overlay. Only a populated search
    # field that omits display is a search-quality signal.
    if search_terms and display and base.norm(display) not in search_norm:
        base.add_flag(record, "DISPLAY_MISSING_FROM_SEARCH", 2)
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

    # The source 'rejected' bucket can contain legitimate official English
    # titles/handles, so it is a review clue rather than proof of wrongness.
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
    if impact == "TOP_1_PERCENT" or flags & structural:
        return True
    if "DUPLICATE_DISPLAY_WITHIN_CATEGORY" in flags:
        return True
    if flags & {"DISPLAY_MATCHES_REJECTED_JA", "SEARCH_CONTAINS_REJECTED_JA"}:
        return True
    if "DISPLAY_MISSING_FROM_SEARCH" in flags:
        return True

    if category == "Artist":
        if "ARTIST_JA_DISPLAY_UNSUPPORTED_BY_SOURCE" in flags:
            return True
        if impact == "TOP_10_PERCENT" and "NO_SOURCE_JA_EVIDENCE_OVERLAP" in flags:
            return True
        return False

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
    data["mode"] = "read_only_semantic_risk_census_v2_category_aware"
    data["selection_policy"]["accepted_risk"] = (
        "category-aware: all top-1%-impact + structural/conflict/collision signals; "
        "blank search_ja and normal Artist romanization are not defects; top-10% "
        "evidence gaps are prioritized"
    )
    data["selection_policy"]["v1_disposition"] = (
        "superseded: v1 over-selected Artist because blank search and canonical-like "
        "romanization were incorrectly treated as risk"
    )
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def output_path_from_argv() -> Path:
    if "--out" in sys.argv:
        i = sys.argv.index("--out")
        if i + 1 < len(sys.argv):
            return Path(sys.argv[i + 1])
    return base.DEFAULT_OUT


def main() -> int:
    base.score_row = score_row
    base.add_duplicate_display_flags = add_duplicate_display_flags
    base.is_accepted_risk = is_accepted_risk
    rc = base.main()
    rewrite_summary(output_path_from_argv())
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
