#!/usr/bin/env python3
"""Validate Issue #180 authority policy against reviewed pilot ledgers."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REVIEWS = ROOT / "docs/issue180/reviews"
B001 = REVIEWS / "I180-B001_FIRST_PASS.csv"
B002 = REVIEWS / "I180-B002_HARD_CASE_FIRST_PASS.csv"

AUTO_ACCEPT = {
    "QUALIFIER_COPYRIGHT",
    "CURATED_COPYRIGHT_LIST",
    "CURATED_COPYRIGHT_LIST+ROOT_NORMALIZATION",
    "CHARACTER_IMPLICATION_INHERITANCE",
}
MUST_UNRESOLVE = {
    "NO_ACCEPTED_HOME_AUTHORITY",
    "QUALIFIER_ALIAS_UNVERIFIED",
    "CATALOG_ROOT_FALLBACK",
}
VALID_STATES = {"HOME_CONFIRMED", "HOME_UNRESOLVED"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def validate_rows(rows: list[dict[str, str]], name: str) -> None:
    seen: set[str] = set()
    for row in rows:
        rid = row["row_id"].strip()
        state = row["home_state"].strip()
        home = row["home_copyright"].strip()
        authority = row["authority_type"].strip()

        if not rid or rid in seen:
            raise SystemExit(f"{name}: duplicate/blank row_id {rid!r}")
        seen.add(rid)

        if state not in VALID_STATES:
            raise SystemExit(f"{name}: invalid state {state!r} for {rid}")

        if state == "HOME_CONFIRMED":
            if not home:
                raise SystemExit(f"{name}: confirmed row missing HOME for {rid}")
            if authority not in AUTO_ACCEPT:
                raise SystemExit(
                    f"{name}: confirmed row uses non-auto authority "
                    f"{authority!r} for {rid}"
                )
        else:
            if home:
                raise SystemExit(f"{name}: unresolved row carries HOME {home!r} for {rid}")
            if authority in AUTO_ACCEPT:
                raise SystemExit(
                    f"{name}: unresolved row unexpectedly uses auto authority "
                    f"{authority!r} for {rid}"
                )

        if authority in MUST_UNRESOLVE and state != "HOME_UNRESOLVED":
            raise SystemExit(
                f"{name}: {authority} must remain unresolved for {rid}"
            )


def main() -> int:
    b001 = read(B001)
    b002 = read(B002)

    if len(b001) != 50:
        raise SystemExit(f"B001 expected 50 rows, got {len(b001)}")
    if len(b002) != 50:
        raise SystemExit(f"B002 expected 50 rows, got {len(b002)}")

    validate_rows(b001, "B001")
    validate_rows(b002, "B002")

    b002_states = Counter(r["home_state"].strip() for r in b002)
    if b002_states != Counter({"HOME_CONFIRMED": 39, "HOME_UNRESOLVED": 11}):
        raise SystemExit(f"B002 calibration drift: {dict(b002_states)}")

    authorities = Counter(r["authority_type"].strip() for r in b002)
    print("Issue180 authority policy validation PASS")
    print(f"B001 rows={len(b001)}")
    print(f"B002 rows={len(b002)} states={dict(b002_states)}")
    print(f"B002 authority_types={dict(authorities)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
