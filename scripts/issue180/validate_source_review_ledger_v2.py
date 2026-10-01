#!/usr/bin/env python3
"""Validate Issue #180 source-level QA reuse ledger."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "docs/issue180/parallel/SOURCE_REVIEW_LEDGER_V2.csv"
STATUSES = {"ACCEPTED", "NEEDS_REVIEW", "REVOKED"}


def main() -> None:
    with LEDGER.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    required = {
        "source_review_id", "source_url", "authority_type", "proved_scope", "home_root",
        "campaign_keys", "mapping_rule", "review_status", "reviewed_on",
        "last_verified_commit", "notes",
    }
    if not rows:
        raise SystemExit("SOURCE_REVIEW_LEDGER_V2.csv must contain at least one reviewed source")
    if set(rows[0]) != required:
        raise SystemExit(f"source review ledger columns mismatch: {set(rows[0]) ^ required}")

    seen_ids: set[str] = set()
    for row in rows:
        rid = row["source_review_id"].strip()
        if not rid or rid in seen_ids:
            raise SystemExit(f"duplicate/blank source_review_id: {rid!r}")
        seen_ids.add(rid)
        if not row["source_url"].startswith(("https://", "http://")):
            raise SystemExit(f"{rid}: source_url must be http(s)")
        if row["review_status"] not in STATUSES:
            raise SystemExit(f"{rid}: invalid review_status {row['review_status']!r}")
        try:
            keys = json.loads(row["campaign_keys"] or "[]")
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{rid}: invalid campaign_keys JSON") from exc
        if not isinstance(keys, list) or not all(isinstance(x, str) and x for x in keys):
            raise SystemExit(f"{rid}: campaign_keys must be a JSON string list")
        if row["review_status"] == "ACCEPTED":
            for field in ("authority_type", "proved_scope", "mapping_rule", "reviewed_on", "last_verified_commit"):
                if not row[field].strip():
                    raise SystemExit(f"{rid}: ACCEPTED row missing {field}")
    print(f"Issue180 source review ledger PASS: rows={len(rows)}")


if __name__ == "__main__":
    main()
