#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

SRC = Path("docs/issue118/bulk_candidate_adversarial_v9/bulk_candidate_inventory_v9.csv")
OUT = Path("docs/issue118/relationship_boundary_refinement_v10")

EXACT_BOUNDARY_TOKENS = {
    "brocon",
    "siscon",
    "lolicon",
    "shotacon",
    "incest",
    "virgin",
    "virginity",
    "seme",
    "uke",
    "femdom",
    "maledom",
    "ageplay",
    "cuckold",
    "cuckquean",
    "netorare",
    "netori",
    "ntr",
}

COMPOUND_PATTERNS = [
    re.compile(r"(?:^|[_/\-])brocon(?:$|[_/\-])"),
    re.compile(r"(?:^|[_/\-])siscon(?:$|[_/\-])"),
    re.compile(r"(?:^|[_/\-])top[/_-]bottom[_/-]dynamic(?:$|[_/\-])"),
    re.compile(r"(?:^|[_/\-])bottom[/_-]top[_/-]dynamic(?:$|[_/\-])"),
    re.compile(r"(?:^|[_/\-])seme[/_-]uke(?:$|[_/\-])"),
    re.compile(r"(?:^|[_/\-])uke[/_-]seme(?:$|[_/\-])"),
]


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def tokenize(key: str) -> set[str]:
    return {p for p in re.split(r"[^a-z0-9]+", key.lower()) if p}


def boundary_flags(key: str) -> list[str]:
    toks = tokenize(key)
    flags = []
    exact = sorted(toks & EXACT_BOUNDARY_TOKENS)
    if exact:
        flags.append("relationship_exact:" + ",".join(exact))
    for pat in COMPOUND_PATTERNS:
        if pat.search(key.lower()):
            flags.append("relationship_compound:" + pat.pattern)
    return flags


def holdout_rank(key: str) -> str:
    return hashlib.sha256(("issue118-v10-fresh-holdout:" + key).encode("utf-8")).hexdigest()


def main() -> int:
    rows = read_csv(SRC)
    clean_v9 = [r for r in rows if r["candidate_state"] == "CLEAN_FOR_FRESH_HOLDOUT"]
    if len(rows) != 1843:
        raise SystemExit(f"v9 inventory drift: {len(rows)}")
    if len(clean_v9) != 1711:
        raise SystemExit(f"v9 clean drift: {len(clean_v9)}")

    flagged = []
    clean = []
    for r in clean_v9:
        flags = boundary_flags(r["identity_key"])
        out = dict(r)
        out["v10_boundary_flags"] = "|".join(flags)
        out["v10_state"] = "RELATIONSHIP_BOUNDARY_REVIEW" if flags else "CLEAN_FOR_FRESH_HOLDOUT_V10"
        if flags:
            flagged.append(out)
        else:
            clean.append(out)

    flagged.sort(key=lambda r: r["identity_key"])
    clean.sort(key=lambda r: r["identity_key"])
    holdout = sorted(clean, key=lambda r: (holdout_rank(r["identity_key"]), r["identity_key"]))[:120]

    if "brocon" not in {r["identity_key"] for r in flagged}:
        raise SystemExit("expected brocon to be relationship-boundary flagged")
    if "top/bottom_dynamic_annotated" not in {r["identity_key"] for r in flagged}:
        raise SystemExit("expected top/bottom_dynamic_annotated to be relationship-boundary flagged")

    OUT.mkdir(parents=True, exist_ok=True)
    fields = list(clean_v9[0].keys()) + ["v10_boundary_flags", "v10_state"]

    with (OUT / "relationship_boundary_review_v10.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(flagged)

    with (OUT / "clean_candidate_inventory_v10.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(clean)

    holdout_fields = [
        "identity_key","general_path","cluster_key","v10_state",
        "human_intent","review_note",
    ]
    with (OUT / "fresh_holdout_template_v10.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=holdout_fields, lineterminator="\n")
        w.writeheader()
        for r in holdout:
            w.writerow({
                "identity_key": r["identity_key"],
                "general_path": r["general_path"],
                "cluster_key": r["cluster_key"],
                "v10_state": r["v10_state"],
                "human_intent": "",
                "review_note": "",
            })

    summary = {
        "issue": 118,
        "mode": "RELATIONSHIP_BOUNDARY_REFINEMENT_V10",
        "source_v9_clean_rows": len(clean_v9),
        "relationship_boundary_review_rows": len(flagged),
        "clean_candidate_rows_v10": len(clean),
        "fresh_holdout_template_rows": len(holdout),
        "required_counterexamples_captured": [
            "brocon",
            "top/bottom_dynamic_annotated",
        ],
        "boundary_rules_use": "DISCOVERY_ONLY_NOT_CLASSIFICATION_AUTHORITY",
        "holdout_verdicts_generated": "NO",
        "semantic_authority": "NO",
        "auto_promotion_performed": "NO",
        "production_authority": "NO",
        "main_mutated": "NO",
        "issue117_code_mutated": "NO",
        "catalog_mutated": "NO",
        "user_db_mutated": "NO",
        "next_gate": (
            "independently review relationship-boundary rows and the new fixed 120-row holdout; "
            "only then consider promotion of the remaining clean set"
        ),
    }
    (OUT / "summary_v10.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
