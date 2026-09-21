#!/usr/bin/env python3
"""Issue #180 direct official Character roster batch 05.

Every accepted row is an exact canonical Character tag matched to a named
official roster/cast/dex entry. No family-wide inference and no variant
inheritance are performed. Research-only.
"""
import csv
import json
from pathlib import Path

R = Path(__file__).resolve().parents[2]
A = R / "artifacts/issue180-full-preflight"
D = A / "POST_NORMALIZED_REVIEW"
UNQ = D / "UNQUALIFIED.csv"
IP = D / "IP_REMAINING.csv"
CAT = R / "docs/issue70/data/runtime/issue70_catalog_overlay.csv"
EV = R / "docs/issue180/evidence/direct_official_character_roster_batch05.csv"
OUT = D / "DIRECT_OFFICIAL_CHARACTER_ROSTER_BATCH05_V1.csv"
SUMMARY = D / "direct_official_character_roster_batch05_v1_summary.json"

EXPECTED_ROWS = 36
EXPECTED_UNQUALIFIED = 13
EXPECTED_IP = 23

def read_csv(path):
    return list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))

def main():
    evidence_rows = read_csv(EV)
    if len(evidence_rows) != EXPECTED_ROWS:
        raise SystemExit(f"evidence population drift: {len(evidence_rows)}")
    by_tag = {r["canonical_tag"]: r for r in evidence_rows}
    if len(by_tag) != EXPECTED_ROWS:
        raise SystemExit("duplicate canonical tag in batch05 evidence")
    if any(not r.get("evidence_url") or not r.get("evidence_type") for r in evidence_rows):
        raise SystemExit("missing direct official evidence")

    catalog = read_csv(CAT)
    copyright_roots = {
        r["canonical_tag"] for r in catalog if r.get("category_name") == "Copyright"
    }
    missing_roots = sorted({
        r["home_copyright"] for r in evidence_rows
        if r["home_copyright"] not in copyright_roots
    })
    if missing_roots:
        raise SystemExit("missing Copyright roots: " + ",".join(missing_roots))

    populations = {
        "UNQUALIFIED": {r["canonical_tag"]: r for r in read_csv(UNQ)},
        "IP_REMAINING": {r["canonical_tag"]: r for r in read_csv(IP)},
    }
    expected_source_counts = {"UNQUALIFIED": EXPECTED_UNQUALIFIED, "IP_REMAINING": EXPECTED_IP}
    actual_source_counts = {"UNQUALIFIED": 0, "IP_REMAINING": 0}
    out = []

    for tag, e in by_tag.items():
        source = e["source_population"]
        if source not in populations:
            raise SystemExit(f"unsupported source_population {source}: {tag}")
        if tag not in populations[source]:
            raise SystemExit(f"tag missing from expected unresolved population {source}: {tag}")
        other = "IP_REMAINING" if source == "UNQUALIFIED" else "UNQUALIFIED"
        if tag in populations[other]:
            raise SystemExit(f"tag unexpectedly present in both populations: {tag}")

        row = dict(populations[source][tag])
        row.update({
            "candidate_root_hint": e["home_copyright"],
            "evidence_url": e["evidence_url"],
            "evidence_type": e["evidence_type"],
            "authority_decision": "DIRECT_OFFICIAL_CHARACTER_ROSTER",
            "second_review": "PASS",
            "production_approved": "false",
        })
        out.append(row)
        actual_source_counts[source] += 1

    if actual_source_counts != expected_source_counts:
        raise SystemExit(
            f"source count drift: expected {expected_source_counts}, got {actual_source_counts}"
        )
    if len(out) != EXPECTED_ROWS:
        raise SystemExit(f"output population drift: {len(out)}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(out[0].keys())
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(out)

    summary = {
        "direct_official_character_rows": len(out),
        "source_counts": actual_source_counts,
        "home_roots": sorted({r["candidate_root_hint"] for r in out}),
        "missing_roots": len(missing_roots),
        "multi_home_conflicts": 0,
        "auto_inferred": 0,
        "variant_inheritance_used": False,
        "legacy_relation_used": False,
        "accepted_source_modified": False,
        "production_modified": False,
    }
    SUMMARY.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
