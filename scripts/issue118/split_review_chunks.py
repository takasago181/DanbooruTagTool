#!/usr/bin/env python3
from __future__ import annotations

import csv
from pathlib import Path

SOURCE = Path("docs/issue118/intent_pilot_sample_v1.csv")
OUT = Path("docs/issue118/review_chunks")
CHUNK = 100
FIELDS = [
    "identity_key",
    "is_general",
    "is_special",
    "general_primary_path",
    "special_id",
    "generation_family",
    "issue104_reviewed",
    "issue104_product_fit_decision",
    "issue104_adult_domains",
    "sample_stratum",
]


def main() -> int:
    with SOURCE.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 700:
        raise SystemExit(f"expected 700 pilot rows, got {len(rows)}")
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("chunk_*.csv"):
        old.unlink()
    for i in range(0, len(rows), CHUNK):
        path = OUT / f"chunk_{i // CHUNK + 1:03d}.csv"
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
            w.writeheader()
            for row in rows[i:i + CHUNK]:
                w.writerow({field: row.get(field, "") for field in FIELDS})
    print(f"ISSUE118_REVIEW_CHUNKS={len(list(OUT.glob('chunk_*.csv')))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
