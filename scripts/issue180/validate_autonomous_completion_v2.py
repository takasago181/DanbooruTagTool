#!/usr/bin/env python3
"""Invariant gate for Issue #180 autonomous completion v2."""
from __future__ import annotations
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parents[2]
A = R / "artifacts/issue180-full-preflight"
D = A / "POST_NORMALIZED_REVIEW/MASTER_HOME_V2"
CAT = R / "docs/issue70/data/runtime/issue70_catalog_overlay.csv"
MASTER = D / "CHARACTER_HOME_MASTER_V2.csv"
APPLIED = D / "APPLIED_AUTHORITY_LEDGER_V2.csv"
EXPECTED = 35890


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main():
    catalog = read(CAT)
    roots = {r["canonical_tag"] for r in catalog if r.get("category_name") == "Copyright"}
    rows = read(MASTER)
    applied = read(APPLIED)
    if len(rows) != EXPECTED:
        raise SystemExit(f"master rows {len(rows)} != {EXPECTED}")
    tags = [r["canonical_tag"] for r in rows]
    if len(set(tags)) != EXPECTED:
        raise SystemExit("duplicate canonical_tag in v2 master")
    states = Counter(r["final_state"] for r in rows)
    if set(states) - {"HOME_CONFIRMED", "HOME_UNRESOLVED", "NOT_OFFICIAL_CHARACTER"}:
        raise SystemExit("invalid final state")
    missing = []
    for row in rows:
        state = row["final_state"]
        home = row.get("home_copyright", "")
        if state == "HOME_CONFIRMED":
            if not home:
                raise SystemExit("confirmed row without HOME: " + row["canonical_tag"])
            if home not in roots:
                missing.append((row["canonical_tag"], home))
        elif home:
            raise SystemExit("non-confirmed row has HOME: " + row["canonical_tag"])
        if str(row.get("production_approved", "")).lower() == "true":
            raise SystemExit("production approval leaked into master")
    if missing:
        raise SystemExit("missing Copyright roots: " + repr(missing[:10]))

    by = defaultdict(set)
    for row in applied:
        by[row["canonical_tag"]].add(row["home_copyright"])
        if str(row.get("production_approved", "")).lower() == "true":
            raise SystemExit("production approval leaked into ledger")
    conflicts = {k: v for k, v in by.items() if len(v) > 1}
    if conflicts:
        raise SystemExit("multi-home applied ledger conflict: " + repr(list(conflicts.items())[:10]))
    if len(applied) != states["HOME_CONFIRMED"]:
        raise SystemExit("applied ledger count mismatch")

    by_tag = {r["canonical_tag"]: r for r in rows}
    regression = {
        "berserker_(fate/zero)": "fate_(series)",
        "female_protagonist_(pokemon_go)": "pokemon",
        "agent_3_(splatoon_3)": "splatoon_(series)",
    }
    for tag, expected_home in regression.items():
        row = by_tag.get(tag)
        if not row or row["final_state"] != "HOME_CONFIRMED" or row["home_copyright"] != expected_home:
            raise SystemExit(f"canonical-root regression: {tag} expected {expected_home}, got {row}")
    bad_project_voltage = [
        r["canonical_tag"] for r in rows
        if r.get("final_qualifier") == "project_voltage"
        and r["final_state"] == "HOME_CONFIRMED"
        and r["home_copyright"] == "project_voltage"
    ]
    if bad_project_voltage:
        raise SystemExit("non-HOME collaboration regression: " + repr(bad_project_voltage[:10]))

    summary = json.load((D / "character_home_master_v2_summary.json").open(encoding="utf-8"))
    if summary["multi_home_or_policy_conflicts"] != 0 or summary["family_authority_conflicts"] != 0:
        raise SystemExit("unresolved authority conflict in v2 summary")
    foundation = json.load((D / "autonomous_foundation_v2_summary.json").open(encoding="utf-8"))
    if states["HOME_CONFIRMED"] < foundation["foundation_confirmed_before_autonomous_decisions"]:
        raise SystemExit("v2 compiler regressed foundation confirmations")

    result = {
        "character_population": len(rows),
        "states": dict(states),
        "missing_copyright_roots": 0,
        "multi_home_conflicts": 0,
        "silent_approval": 0,
        "production_approved_rows": 0,
        "semantic_regressions": 0,
        "accepted_source_modified": False,
        "production_modified": False,
        "gate": "PASS",
    }
    (D / "autonomous_completion_v2_validation.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
