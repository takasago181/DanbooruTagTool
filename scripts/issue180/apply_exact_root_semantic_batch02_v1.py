#!/usr/bin/env python3
"""Issue #180 exact-root semantic authority batch 02.

Resolves the 12 exact Copyright-root families intentionally left for semantic review.
Research-only and fail-closed:
- only exact qualifier families already present in GLOBAL_EXACT_COPYRIGHT_SECOND_REVIEW_V1;
- official root authority is required;
- nested Character variants/costumes do not inherit automatically;
- umbrella roots may remain unresolved;
- never modifies accepted source or production.
"""
import csv
import json
import re
from pathlib import Path

R = Path(__file__).resolve().parents[2]
A = R / "artifacts/issue180-full-preflight"
D = A / "POST_NORMALIZED_REVIEW"
EXACT = A / "GLOBAL_EXACT_COPYRIGHT_SECOND_REVIEW_V1.csv"
IP = D / "IP_REMAINING.csv"
EV = R / "docs/issue180/evidence/exact_root_semantic_authority_batch02.csv"
OUT = D / "EXACT_ROOT_SEMANTIC_BATCH02_V1.csv"
SUMMARY = D / "exact_root_semantic_batch02_v1_summary.json"

EXPECTED_FAMILIES = 12
EXPECTED_ROWS = 375
EXPECTED_PASS = 315
EXPECTED_VARIANTS = 30
EXPECTED_UMBRELLA = 30

def nested_variant(tag: str, family: str) -> bool:
    suffix = f"_({family})"
    if not tag.endswith(suffix):
        return False
    base = tag[:-len(suffix)]
    return re.search(r"_\([^()]+\)$", base) is not None

def read_csv(path):
    return list(csv.DictReader(path.open(encoding="utf-8-sig", newline="")))

def main():
    evidence_rows = read_csv(EV)
    evidence = {r["family"]: r for r in evidence_rows}
    if len(evidence) != len(evidence_rows):
        raise SystemExit("duplicate family in authority evidence")

    exact_rows = [r for r in read_csv(EXACT) if r.get("second_review") == "UNRESOLVED"]
    exact = {r["family"]: r for r in exact_rows}

    if len(exact) != EXPECTED_FAMILIES or set(exact) != set(evidence):
        raise SystemExit(f"family population mismatch exact={len(exact)} evidence={len(evidence)}")
    if sum(int(r["character_rows"]) for r in exact_rows) != EXPECTED_ROWS:
        raise SystemExit("exact semantic review population drift")

    for family, r in exact.items():
        e = evidence[family]
        if r.get("hint_state") != "EXACT_CATALOG_HINT":
            raise SystemExit(f"root is not exact catalog hint: {family}")
        if r.get("candidate_root_hint") != e["home_copyright"]:
            raise SystemExit(f"root mismatch: {family}")
        if e["root_review"] not in {"PASS", "UNRESOLVED_UMBRELLA"}:
            raise SystemExit(f"unsupported root review state: {family}")

    ip_rows = [r for r in read_csv(IP) if r.get("final_qualifier") in evidence]
    if len(ip_rows) != EXPECTED_ROWS:
        raise SystemExit(f"IP row population drift: {len(ip_rows)}")

    per_family = {}
    out = []
    for r in ip_rows:
        family = r["final_qualifier"]
        e = evidence[family]
        is_variant = nested_variant(r["canonical_tag"], family)

        if e["root_review"] != "PASS":
            decision = "HOME_UNRESOLVED_UMBRELLA"
            review = "UNRESOLVED"
        elif is_variant:
            decision = "VARIANT_OFFICIALITY_PENDING"
            review = "UNRESOLVED"
        else:
            decision = "EXACT_QUALIFIER_ACCEPTED_ROOT_AUTHORITY"
            review = "PASS"

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
        per_family.setdefault(family, {"rows": 0, "pass": 0, "unresolved": 0})
        per_family[family]["rows"] += 1
        per_family[family]["pass" if review == "PASS" else "unresolved"] += 1

    for family, erow in exact.items():
        if per_family.get(family, {}).get("rows", 0) != int(erow["character_rows"]):
            raise SystemExit(f"family row count drift: {family}")

    pass_rows = sum(r["second_review"] == "PASS" for r in out)
    variant_rows = sum(r["authority_decision"] == "VARIANT_OFFICIALITY_PENDING" for r in out)
    umbrella_rows = sum(r["authority_decision"] == "HOME_UNRESOLVED_UMBRELLA" for r in out)

    if (pass_rows, variant_rows, umbrella_rows) != (EXPECTED_PASS, EXPECTED_VARIANTS, EXPECTED_UMBRELLA):
        raise SystemExit(
            f"expected pass/variant/umbrella {(EXPECTED_PASS, EXPECTED_VARIANTS, EXPECTED_UMBRELLA)} "
            f"got {(pass_rows, variant_rows, umbrella_rows)}"
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out[0].keys(), lineterminator="\n")
        w.writeheader()
        w.writerows(out)

    summary = {
        "families": len(evidence),
        "family_rows": len(out),
        "pass_roots": sum(r["root_review"] == "PASS" for r in evidence_rows),
        "unresolved_roots": sum(r["root_review"] != "PASS" for r in evidence_rows),
        "second_review_pass": pass_rows,
        "variant_officiality_pending": variant_rows,
        "umbrella_unresolved": umbrella_rows,
        "missing_roots": 0,
        "multi_home_conflicts": 0,
        "auto_inferred": 0,
        "accepted_source_modified": False,
        "production_modified": False,
        "per_family": per_family,
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
