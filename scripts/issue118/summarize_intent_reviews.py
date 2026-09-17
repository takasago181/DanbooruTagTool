#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

SAMPLE = Path("docs/issue118/intent_pilot_sample_v1.csv")
REVIEW_DIR = Path("docs/issue118/reviews")
OUT = REVIEW_DIR / "semantic_pilot_summary_v1.json"
ALLOWED = {"SEXUAL", "NON_SEXUAL", "CONTEXTUAL"}


def main() -> int:
    with SAMPLE.open(encoding="utf-8-sig", newline="") as f:
        sample = list(csv.DictReader(f))
    if len(sample) != 700:
        raise SystemExit(f"expected 700 sample rows, got {len(sample)}")
    sample_by_key = {r["identity_key"]: r for r in sample}
    if len(sample_by_key) != 700:
        raise SystemExit("sample identity keys are not unique")

    review_files = sorted(REVIEW_DIR.glob("chunk_???_review_v1.csv"))
    if len(review_files) != 7:
        raise SystemExit(f"expected 7 review files, got {len(review_files)}")

    reviews: list[dict[str, str]] = []
    per_file: dict[str, dict[str, int]] = {}
    for path in review_files:
        with path.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        if len(rows) != 100:
            raise SystemExit(f"{path}: expected 100 rows, got {len(rows)}")
        counts = Counter()
        for row in rows:
            cls = row["reviewed_class"].strip()
            status = row["pilot_review_status"].strip()
            if status == "REVIEWED":
                if cls not in ALLOWED:
                    raise SystemExit(f"{path}: invalid reviewed class for {row['identity_key']}: {cls}")
                counts[cls] += 1
            elif status == "UNCLASSIFIED":
                if cls:
                    raise SystemExit(f"{path}: UNCLASSIFIED row must have blank class: {row['identity_key']}")
                counts["UNCLASSIFIED"] += 1
            else:
                raise SystemExit(f"{path}: invalid status {status}")
        per_file[path.name] = dict(sorted(counts.items()))
        reviews.extend(rows)

    review_keys = [r["identity_key"] for r in reviews]
    if len(set(review_keys)) != 700:
        raise SystemExit("review identity keys are not unique")
    if set(review_keys) != set(sample_by_key):
        missing = sorted(set(sample_by_key) - set(review_keys))[:10]
        extra = sorted(set(review_keys) - set(sample_by_key))[:10]
        raise SystemExit(f"review/sample identity mismatch missing={missing} extra={extra}")

    overall = Counter()
    strata: dict[str, Counter] = defaultdict(Counter)
    membership: dict[str, Counter] = defaultdict(Counter)
    joined = []
    for review in reviews:
        sample_row = sample_by_key[review["identity_key"]]
        cls = review["reviewed_class"].strip() or "UNCLASSIFIED"
        overall[cls] += 1
        strata[sample_row["sample_stratum"]][cls] += 1
        membership_key = (
            "OVERLAP" if sample_row["is_general"] == "YES" and sample_row["is_special"] == "YES"
            else "GENERAL_ONLY" if sample_row["is_general"] == "YES"
            else "SPECIAL_ONLY"
        )
        membership[membership_key][cls] += 1
        joined.append({**sample_row, **review})

    summary = {
        "issue": 118,
        "mode": "REVIEWED_700_IDENTITY_SEMANTIC_PILOT",
        "pilot_rows": len(reviews),
        "overall_counts": dict(sorted(overall.items())),
        "overall_rates": {k: round(v / len(reviews), 6) for k, v in sorted(overall.items())},
        "stratum_counts": {k: dict(sorted(v.items())) for k, v in sorted(strata.items())},
        "membership_counts": {k: dict(sorted(v.items())) for k, v in sorted(membership.items())},
        "per_chunk_counts": per_file,
        "validation": {
            "sample_rows": len(sample),
            "review_rows": len(reviews),
            "review_files": len(review_files),
            "unique_sample_identity_keys": len(sample_by_key),
            "unique_review_identity_keys": len(set(review_keys)),
            "exact_identity_coverage": "PASS",
            "allowed_classes_only": "PASS",
        },
        "boundaries": {
            "production_data_mutated": "NO",
            "main_mutated": "NO",
            "issue117_code_mutated": "NO",
            "catalog_mutated": "NO",
            "user_db_mutated": "NO",
            "pilot_results_are_population_prevalence_estimate": "NO",
        },
    }
    OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary["overall_counts"], sort_keys=True))
    print("ISSUE118_SEMANTIC_PILOT_SUMMARY=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
