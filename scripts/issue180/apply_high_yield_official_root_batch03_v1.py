#!/usr/bin/env python3
"""Issue #180 high-yield official root authority batch 03.

Research-only and fail-closed:
- consumes only the current IP_REMAINING population;
- every qualifier->HOME normalization is manually reviewed against an official series/franchise source;
- canonical Copyright root must exist in the accepted catalog;
- syntactically explicit nested variants are not auto-inherited;
- no legacy RelatedCopyright/co-occurrence authority is consumed;
- never modifies accepted source or production.
"""
import csv
import json
import re
from pathlib import Path

R = Path(__file__).resolve().parents[2]
A = R / "artifacts/issue180-full-preflight"
D = A / "POST_NORMALIZED_REVIEW"
IP = D / "IP_REMAINING.csv"
CAT = R / "docs/issue70/data/runtime/issue70_catalog_overlay.csv"
EV = R / "docs/issue180/evidence/high_yield_official_root_authority_batch03.csv"
OUT = D / "HIGH_YIELD_OFFICIAL_ROOT_BATCH03_V1.csv"
SUMMARY = D / "high_yield_official_root_batch03_v1_summary.json"

EXPECTED_FAMILIES = 14
EXPECTED_ROWS = 453
EXPECTED_VARIANTS = 15
EXPECTED_PASS = 438

def read_csv(path):
    return list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))

def nested_variant(tag: str, family: str) -> bool:
    suffix = f"_({family})"
    if not tag.endswith(suffix):
        return False
    base = tag[:-len(suffix)]
    return re.search(r"_\([^()]+\)$", base) is not None

def main():
    evidence_rows = read_csv(EV)
    evidence = {r["family"]: r for r in evidence_rows}
    if len(evidence_rows) != EXPECTED_FAMILIES or len(evidence) != EXPECTED_FAMILIES:
        raise SystemExit(f"evidence family count drift: {len(evidence_rows)}")
    if any(r.get("root_review") != "PASS" for r in evidence_rows):
        raise SystemExit("non-PASS root authority in batch03 evidence")

    catalog = read_csv(CAT)
    copyright_roots = {
        r["canonical_tag"]
        for r in catalog
        if r.get("category_name") == "Copyright"
    }
    missing_roots = sorted({
        r["home_copyright"] for r in evidence_rows
        if r["home_copyright"] not in copyright_roots
    })
    if missing_roots:
        raise SystemExit("missing Copyright roots: " + ",".join(missing_roots))

    ip_rows = [r for r in read_csv(IP) if r.get("final_qualifier") in evidence]
    if len(ip_rows) != EXPECTED_ROWS:
        raise SystemExit(f"batch03 population drift: expected {EXPECTED_ROWS}, got {len(ip_rows)}")

    actual_counts = {}
    for r in ip_rows:
        actual_counts[r["final_qualifier"]] = actual_counts.get(r["final_qualifier"], 0) + 1
    for family, e in evidence.items():
        expected = int(e["expected_rows"])
        actual = actual_counts.get(family, 0)
        if actual != expected:
            raise SystemExit(f"family row count drift {family}: expected {expected}, got {actual}")

    out = []
    per_family = {}
    for r in ip_rows:
        family = r["final_qualifier"]
        e = evidence[family]
        is_variant = nested_variant(r["canonical_tag"], family)
        review = "UNRESOLVED" if is_variant else "PASS"
        decision = (
            "VARIANT_OFFICIALITY_PENDING"
            if is_variant
            else "QUALIFIER_PLUS_OFFICIAL_ROOT_AUTHORITY"
        )

        row = dict(r)
        row.update({
            "candidate_root_hint": e["home_copyright"],
            "evidence_url": e["evidence_url"],
            "evidence_type": e["evidence_type"],
            "root_review": e["root_review"],
            "authority_decision": decision,
            "variant_gate": "NESTED_VARIANT_REQUIRES_OFFICIALITY" if is_variant else "DIRECT_TAG",
            "second_review": review,
            "production_approved": "false",
        })
        out.append(row)
        pf = per_family.setdefault(family, {"rows": 0, "pass": 0, "unresolved": 0})
        pf["rows"] += 1
        pf["pass" if review == "PASS" else "unresolved"] += 1

    variant_rows = sum(r["authority_decision"] == "VARIANT_OFFICIALITY_PENDING" for r in out)
    pass_rows = sum(r["second_review"] == "PASS" for r in out)
    if (variant_rows, pass_rows) != (EXPECTED_VARIANTS, EXPECTED_PASS):
        raise SystemExit(
            f"batch03 pass/variant drift expected {(EXPECTED_PASS, EXPECTED_VARIANTS)} "
            f"got {(pass_rows, variant_rows)}"
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out[0].keys(), lineterminator="\n")
        w.writeheader()
        w.writerows(out)

    summary = {
        "families": len(evidence),
        "family_rows": len(out),
        "second_review_pass": pass_rows,
        "variant_officiality_pending": variant_rows,
        "missing_roots": len(missing_roots),
        "multi_home_conflicts": 0,
        "auto_inferred": 0,
        "legacy_relation_used": False,
        "accepted_source_modified": False,
        "production_modified": False,
        "per_family": per_family,
    }
    SUMMARY.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
