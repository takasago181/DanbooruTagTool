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


ORIGIN_CLASSES = {
    "OFFICIAL_IDENTITY",
    "OFFICIAL_ALIAS",
    "OFFICIAL_VARIANT",
    "FANWORK_PAIRING",
    "FANWORK_HASHTAG",
    "FANWORK_EVENT",
    "FANWORK_MEME",
    "FANWORK_COMMUNITY",
    "FANWORK_CROSSOVER",
    "FANWORK_DERIVATIVE",
    "NON_IDENTITY_DESCRIPTION",
    "UNKNOWN",
}
ORIGIN_REVIEW = REVIEWS / "I179-B001-B002_ORIGIN_REVIEW.csv"
ORIGIN_REQUIRED = {
    "row_id", "canonical_tag", "origin_class", "origin_excluded_terms",
    "origin_review_terms", "origin_evidence", "origin_note",
    "origin_second_review_required",
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

    # B001+B002 origin review is a separate overlay so the original semantic
    # verdict ledgers remain immutable.  It must cover exactly those first
    # two 50-row batches and may remove terms without suppressing official rows.
    if ORIGIN_REVIEW.exists():
        origin_rows = read(ORIGIN_REVIEW)
        if len(origin_rows) != 100:
            raise SystemExit(
                f"{ORIGIN_REVIEW.name}: expected 100 rows, got {len(origin_rows)}"
            )
        origin_fields = set(origin_rows[0]) if origin_rows else set()
        missing = ORIGIN_REQUIRED - origin_fields
        if missing:
            raise SystemExit(
                f"{ORIGIN_REVIEW.name}: missing fields {sorted(missing)}"
            )

        first_two_files = [
            REVIEWS / "I179-B001_FIRST_PASS.csv",
            REVIEWS / "I179-B002_FIRST_PASS.csv",
        ]
        first_two_rows = [row for path in first_two_files for row in read(path)]
        first_two = {row["row_id"]: row["canonical_tag"] for row in first_two_rows}
        origin_ids: set[str] = set()

        for row in origin_rows:
            rid = row["row_id"].strip()
            if not rid or rid in origin_ids:
                raise SystemExit(f"{ORIGIN_REVIEW.name}: duplicate/blank row_id: {rid}")
            origin_ids.add(rid)
            if rid not in first_two:
                raise SystemExit(f"{ORIGIN_REVIEW.name}: row outside B001/B002: {rid}")
            if row["canonical_tag"].strip() != first_two[rid].strip():
                raise SystemExit(f"{ORIGIN_REVIEW.name}: canonical drift: {rid}")

            origin_class = row["origin_class"].strip()
            if origin_class not in ORIGIN_CLASSES:
                raise SystemExit(
                    f"{ORIGIN_REVIEW.name}: invalid origin_class={origin_class!r} for {rid}"
                )
            if row["origin_second_review_required"].strip() not in {"true", "false"}:
                raise SystemExit(
                    f"{ORIGIN_REVIEW.name}: invalid origin_second_review_required for {rid}"
                )

            for field in ("origin_excluded_terms", "origin_review_terms"):
                value = row[field].strip()
                if not value:
                    continue
                for item in (x.strip() for x in value.split("|")):
                    if "::" not in item:
                        raise SystemExit(
                            f"{ORIGIN_REVIEW.name}: malformed {field} item {item!r} for {rid}"
                        )
                    _, cls = (x.strip() for x in item.rsplit("::", 1))
                    if cls not in ORIGIN_CLASSES:
                        raise SystemExit(
                            f"{ORIGIN_REVIEW.name}: invalid term origin class {cls!r} for {rid}"
                        )

        if origin_ids != set(first_two):
            missing_ids = sorted(set(first_two) - origin_ids)
            extra_ids = sorted(origin_ids - set(first_two))
            raise SystemExit(
                f"{ORIGIN_REVIEW.name}: coverage drift missing={missing_ids[:5]} extra={extra_ids[:5]}"
            )

    print(
        f"Issue179 review validation PASS: files={len(files)} rows={len(seen)} "
        f"origin_review={'100' if ORIGIN_REVIEW.exists() else 'absent'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
