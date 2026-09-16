#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "docs/issue70/data/source/issue70_translation_source_with_relations.csv"
RESULTS = ROOT / "docs/issue70/data/runtime/issue70_translation_results.csv"
AUDIT_DIR = ROOT / "docs/issue70/audit/semantic_review"
OUT = ROOT / "artifacts/issue70-semantic-risk-scan/p0_copyright_validation.json"


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

source = {r["row_id"]: r for r in read_csv(SOURCE)}
results = {r["row_id"]: r for r in read_csv(RESULTS)}

p0 = {
    rid for rid, s in source.items()
    if s["category_name"] == "Copyright"
    and int(s.get("post_count") or 0) >= 10000
    and results[rid]["translation_status"] == "REVIEW_REQUIRED"
}

base_files = [
    "p0_copyright_phase1.csv",
    "p0_copyright_phase2.csv",
    "p0_copyright_phase3.csv",
    "p0_copyright_phase4.csv",
    "p0_copyright_phase5.csv",
    "p0_copyright_remaining_triage.csv",
]

verdicts = {}
seen = set()
for name in base_files:
    path = AUDIT_DIR / name
    for row in read_csv(path):
        rid = row["row_id"]
        if rid in seen:
            raise SystemExit(f"duplicate base ledger row: {rid}")
        seen.add(rid)
        verdicts[rid] = row["audit_verdict"]

# External resolution is an intentional override of NEEDS_EXTERNAL_CHECK triage rows.
for row in read_csv(AUDIT_DIR / "p0_copyright_external_resolution.csv"):
    rid = row["row_id"]
    if rid not in verdicts:
        raise SystemExit(f"resolution without base triage row: {rid}")
    if verdicts[rid] != row["prior_verdict"]:
        raise SystemExit(
            f"prior verdict mismatch for {rid}: ledger={verdicts[rid]} resolution={row['prior_verdict']}"
        )
    verdicts[rid] = row["final_verdict"]

ledger_ids = set(verdicts)
missing = sorted(p0 - ledger_ids)
extra = sorted(ledger_ids - p0)
unresolved = sorted(rid for rid in p0 if verdicts.get(rid) == "NEEDS_EXTERNAL_CHECK")

counts = {}
for rid in sorted(p0):
    v = verdicts.get(rid, "MISSING")
    counts[v] = counts.get(v, 0) + 1

summary = {
    "p0_definition": "Copyright + REVIEW_REQUIRED + post_count >= 10000",
    "expected_rows": len(p0),
    "ledger_rows": len(ledger_ids),
    "missing": missing,
    "extra": extra,
    "unresolved": unresolved,
    "final_verdict_counts": counts,
    "production_mutation": False,
}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))

if len(p0) != 71 or missing or extra or unresolved:
    raise SystemExit(1)
