#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

SRC = Path("docs/issue118/remaining_cluster_inventory_v7/cluster_inventory_v7.csv")
OUT = Path("docs/issue118/remaining_cluster_triage_v8")

# These roots are NOT declared NON_SEXUAL.
# They are only low-risk candidates for the next adversarial validation stage.
# PERSON_COUNT is intentionally excluded after v8's first materialization showed
# mixed concepts such as bisexual_male / blacked_male / male_harem in one cluster.
LOW_RISK_BULK_ROOTS = {
    "STYLE_QUALITY_META",
    "COLOR_APPEARANCE",
    "EXPRESSION_EMOTION",
    "GAZE_ORIENTATION",
    "COMPOSITION_CAMERA",
    "PLACE_BACKGROUND",
    "LIVING_NATURE",
    "TEXT_SYMBOL",
    "HAIR_FACE",
}

VALID_TRIAGE = {"BULK_CANDIDATE", "SPLIT_REQUIRED", "BOUNDARY_REVIEW"}


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def triage(row: dict[str, str]) -> tuple[str, str, str]:
    membership = row["membership"]
    path = row["general_path"]
    root = row["general_root"]
    family = row["generation_family"]
    lex = row["lex_flags"]

    if membership != "GENERAL_ONLY":
        return (
            "BOUNDARY_REVIEW",
            "special_or_overlap_membership",
            "mine exact SEXUAL/CONTEXTUAL/NON_SEXUAL concept rules or review queue; do not bulk-promote",
        )
    if lex != "NONE":
        return (
            "BOUNDARY_REVIEW",
            "explicit_risk_flag",
            "keep out of NON_SEXUAL bulk; review/derive exact-concept boundary rules",
        )
    if path == "(none)":
        return (
            "BOUNDARY_REVIEW",
            "no_accepted_general_path",
            "resolve semantic cluster first; do not infer intent from missing taxonomy",
        )

    if root in LOW_RISK_BULK_ROOTS and family == "(none)":
        return (
            "BULK_CANDIDATE",
            "ordinary_general_root_no_risk_signal",
            "run full adversarial scan, independent fixed review artifact, then fresh holdout before any promotion",
        )

    return (
        "SPLIT_REQUIRED",
        "mixed_semantic_cluster",
        "derive smaller subclusters/negative controls, then adversarial-scan each subcluster",
    )


def main() -> int:
    rows = read_csv(SRC)
    if len(rows) != 323:
        raise SystemExit(f"expected 323 v7 clusters, got {len(rows)}")

    out_rows = []
    cluster_counts = Counter()
    identity_counts = Counter()
    reason_counts = Counter()
    top_by_bucket: dict[str, list[dict[str, object]]] = defaultdict(list)

    total_identities = 0
    for row in rows:
        n = int(row["rows"])
        total_identities += n
        bucket, reason, next_gate = triage(row)
        if bucket not in VALID_TRIAGE:
            raise SystemExit(f"invalid triage bucket: {bucket}")

        out = dict(row)
        out["triage_bucket"] = bucket
        out["triage_reason"] = reason
        out["next_gate"] = next_gate
        out_rows.append(out)

        cluster_counts[bucket] += 1
        identity_counts[bucket] += n
        reason_counts[reason] += n
        top_by_bucket[bucket].append(
            {
                "cluster_key": row["cluster_key"],
                "rows": n,
                "examples": row["examples"],
                "reason": reason,
            }
        )

    if total_identities != 15880:
        raise SystemExit(f"expected 15880 remaining identities, got {total_identities}")

    for bucket in top_by_bucket:
        top_by_bucket[bucket].sort(key=lambda x: (-int(x["rows"]), str(x["cluster_key"])))

    OUT.mkdir(parents=True, exist_ok=True)
    fields = [
        "cluster_key",
        "rows",
        "membership",
        "general_path",
        "general_root",
        "generation_family",
        "lex_flags",
        "examples",
        "triage_bucket",
        "triage_reason",
        "next_gate",
    ]
    with (OUT / "cluster_triage_v8.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(out_rows)

    summary = {
        "issue": 118,
        "mode": "REMAINING_CLUSTER_TRIAGE_V8",
        "source": str(SRC),
        "source_cluster_count": len(rows),
        "source_remaining_unclassified_rows": total_identities,
        "triage_cluster_counts": dict(sorted(cluster_counts.items())),
        "triage_identity_counts": dict(sorted(identity_counts.items())),
        "triage_identity_share": {
            k: round(identity_counts[k] / total_identities, 6)
            for k in sorted(identity_counts)
        },
        "triage_reason_identity_counts": dict(sorted(reason_counts.items())),
        "bulk_candidate_roots": sorted(LOW_RISK_BULK_ROOTS),
        "top_clusters_by_bucket": {
            k: v[:20] for k, v in sorted(top_by_bucket.items())
        },
        "semantic_authority": "NO",
        "auto_promotion_performed": "NO",
        "review_verdicts_generated": "NO",
        "production_authority": "NO",
        "main_mutated": "NO",
        "issue117_code_mutated": "NO",
        "catalog_mutated": "NO",
        "user_db_mutated": "NO",
        "next_recommended_step": (
            "validate BULK_CANDIDATE with adversarial scan + independent fixed review artifact + fresh holdout; "
            "subcluster SPLIT_REQUIRED; keep BOUNDARY_REVIEW out of General bulk promotion"
        ),
    }
    (OUT / "summary_v8.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "clusters": len(rows),
        "identities": total_identities,
        "cluster_counts": dict(sorted(cluster_counts.items())),
        "identity_counts": dict(sorted(identity_counts.items())),
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
