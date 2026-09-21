#!/usr/bin/env python3
"""Validate Issue #179 semantic review ledgers against generated Stage B pilot."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REVIEWS = ROOT / "docs/issue179/reviews"
STAGE_B = ROOT / "artifacts/issue179-quality-census/stage_b"

VALID = {
    "identity_verdict": {"PASS", "REVIEW", "FAIL_IDENTITY", "OUT_OF_PRODUCT_SCOPE"},
    "display_verdict": {
        "PASS", "REVIEW", "FAIL_NAME", "FAIL_TRANSLATION",
        "FAIL_QUALIFIER", "FAIL_OVERDISAMBIGUATION",
    },
    "search_verdict": {
        "PASS", "REVIEW", "FAIL_MISSING_ALIAS", "FAIL_NON_IDENTITY_TERM",
        "FAIL_COLLISION", "FAIL_DUPLICATE_NOISE",
    },
    "ranking_verdict": {"PASS", "REVIEW", "FAIL_RELEVANCE", "FAIL_AMBIGUITY"},
    "scope_verdict": {"PASS_IN_2D", "REVIEW", "OUT_OF_PRODUCT_SCOPE"},
    "relation_note": {
        "RELATION_OK_KNOWN", "RELATION_BAD_OLD_COOCCURRENCE", "RELATION_UNKNOWN",
    },
    "confidence": {"HIGH", "MEDIUM", "LOW"},
    "second_review_required": {"true", "false"},
}

REQUIRED = {
    "row_id", "canonical_tag", *VALID.keys(), "evidence_refs",
    "proposed_display", "proposed_search", "reviewer_note",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    files = sorted(REVIEWS.glob("I179-B*_FIRST_PASS.csv"))
    if not files:
        raise SystemExit("no Stage B first-pass review files")

    manifest = read(STAGE_B / "STAGE_B_REVIEW_MANIFEST.csv")
    pilot = {row["row_id"]: row for row in manifest}
    seen: set[str] = set()

    for path in files:
        rows = read(path)
        if len(rows) != 50:
            raise SystemExit(f"{path.name}: expected 50 rows, got {len(rows)}")
        fields = set(rows[0]) if rows else set()
        missing = REQUIRED - fields
        if missing:
            raise SystemExit(f"{path.name}: missing fields {sorted(missing)}")

        for row in rows:
            rid = row["row_id"].strip()
            if not rid or rid in seen:
                raise SystemExit(f"duplicate/blank reviewed row_id: {rid}")
            seen.add(rid)
            if rid not in pilot:
                raise SystemExit(f"{path.name}: row not in Stage B pilot: {rid}")
            if row["canonical_tag"].strip() != pilot[rid]["canonical_tag"].strip():
                raise SystemExit(f"{path.name}: canonical drift: {rid}")

            for field, allowed in VALID.items():
                value = row[field].strip()
                if value not in allowed:
                    raise SystemExit(
                        f"{path.name}: invalid {field}={value!r} for {rid}"
                    )

            if (
                row["display_verdict"].startswith("FAIL_")
                and not row["reviewer_note"].strip()
            ):
                raise SystemExit(f"{path.name}: display failure missing note: {rid}")
            if (
                row["search_verdict"].startswith("FAIL_")
                and not row["reviewer_note"].strip()
            ):
                raise SystemExit(f"{path.name}: search failure missing note: {rid}")

    print(f"Issue179 review validation PASS: files={len(files)} rows={len(seen)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
