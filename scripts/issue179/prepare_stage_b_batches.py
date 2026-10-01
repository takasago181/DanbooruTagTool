#!/usr/bin/env python3
"""Prepare reproducible Stage B review batches for Issue #179.

Consumes Stage A pilot_manifest.csv and creates ten 50-row review batches.
Review fields are blank by design; heuristics never become semantic verdicts.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IN = ROOT / "artifacts/issue179-quality-census/pilot_manifest.csv"
DEFAULT_OUT = ROOT / "artifacts/issue179-quality-census/stage_b"

REVIEW_FIELDS = [
    "batch_id",
    "row_id",
    "canonical_tag",
    "category",
    "post_count",
    "display_ja",
    "search_ja",
    "aliases",
    "translation_status",
    "quality_band",
    "risk_flags",
    "pilot_reasons",
    "scope_authority",
    "scope_recheck",
    "old_media_scope",
    "in_current_runtime",
    "identity_verdict",
    "display_verdict",
    "search_verdict",
    "ranking_verdict",
    "scope_verdict",
    "relation_note",
    "confidence",
    "evidence_refs",
    "proposed_display",
    "proposed_search",
    "reviewer_note",
    "second_review_required",
]

VALID_IDENTITY = {"", "PASS", "REVIEW", "FAIL_IDENTITY", "OUT_OF_PRODUCT_SCOPE"}
VALID_DISPLAY = {
    "", "PASS", "REVIEW", "FAIL_NAME", "FAIL_TRANSLATION",
    "FAIL_QUALIFIER", "FAIL_OVERDISAMBIGUATION",
}
VALID_SEARCH = {
    "", "PASS", "REVIEW", "FAIL_MISSING_ALIAS",
    "FAIL_NON_IDENTITY_TERM", "FAIL_COLLISION", "FAIL_DUPLICATE_NOISE",
}
VALID_RANKING = {"", "PASS", "REVIEW", "FAIL_RELEVANCE", "FAIL_AMBIGUITY"}
VALID_SCOPE = {"", "PASS_IN_2D", "REVIEW", "OUT_OF_PRODUCT_SCOPE"}
VALID_RELATION = {"", "RELATION_OK_KNOWN", "RELATION_BAD_OLD_COOCCURRENCE", "RELATION_UNKNOWN"}
VALID_CONFIDENCE = {"", "HIGH", "MEDIUM", "LOW"}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=REVIEW_FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in REVIEW_FIELDS})


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_IN)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    rows = read_rows(args.input)
    if len(rows) != 500:
        raise SystemExit(f"pilot row drift: {len(rows)} != 500")
    ids = [row["row_id"] for row in rows]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate row_id in pilot")

    # Preserve Stage A priority while spreading clean controls and known regression
    # rows across batches. Each batch gets 10 clean controls when possible.
    clean = [r for r in rows if "CLEAN_CONTROL" in (r.get("pilot_reasons") or "").split("|")]
    nonclean = [r for r in rows if r not in clean]
    if len(clean) != 100:
        raise SystemExit(f"clean control drift: {len(clean)} != 100")

    # Known regressions first among semantic candidates, then HIGH_RISK, then CHECK/CLEAR.
    def priority(row: dict[str, str]) -> tuple[int, int, int, str]:
        reasons = set((row.get("pilot_reasons") or "").split("|"))
        known = 0 if "KNOWN_REGRESSION" in reasons else 1
        band = {"HIGH_RISK": 0, "CHECK": 1, "CLEAR": 2}.get(row.get("quality_band") or "", 3)
        post = -int(row.get("post_count") or 0)
        return (known, band, post, row.get("canonical_tag") or "")

    clean.sort(key=priority)
    nonclean.sort(key=priority)

    batches: list[list[dict[str, str]]] = [[] for _ in range(10)]

    # 10 controls per batch.
    for i, row in enumerate(clean):
        batches[i % 10].append(row)

    # Fill each batch to 50 in round-robin order so early semantic priorities are
    # distributed rather than concentrated in a single batch.
    b = 0
    for row in nonclean:
        while len(batches[b]) >= 50:
            b = (b + 1) % 10
        batches[b].append(row)
        b = (b + 1) % 10

    if any(len(batch) != 50 for batch in batches):
        raise SystemExit(f"batch size drift: {[len(x) for x in batches]}")

    args.out.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, str]] = []
    for idx, batch in enumerate(batches, 1):
        batch_id = f"I179-B{idx:03d}"
        prepared: list[dict[str, str]] = []
        for src in batch:
            row = {field: src.get(field, "") for field in REVIEW_FIELDS}
            row["batch_id"] = batch_id
            row["second_review_required"] = ""
            prepared.append(row)
            manifest.append(row)
        write_rows(args.out / f"{batch_id}.csv", prepared)

    write_rows(args.out / "STAGE_B_REVIEW_MANIFEST.csv", manifest)

    counts = Counter(r.get("quality_band") or "" for r in manifest)
    categories = Counter(r.get("category") or "" for r in manifest)
    known = sum("KNOWN_REGRESSION" in (r.get("pilot_reasons") or "").split("|") for r in manifest)
    controls = sum("CLEAN_CONTROL" in (r.get("pilot_reasons") or "").split("|") for r in manifest)

    print({
        "rows": len(manifest),
        "batches": 10,
        "batch_size": 50,
        "quality_bands": dict(counts),
        "categories": dict(categories),
        "known_regressions": known,
        "clean_controls": controls,
    })
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
