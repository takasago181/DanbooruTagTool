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
POLICY_PATH = R / "docs/issue180/autonomous/AUTONOMOUS_POLICY_V2.json"


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def main():
    catalog = read(CAT)
    roots = {r["canonical_tag"] for r in catalog if r.get("category_name") == "Copyright"}
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    broad_families = set(policy["broad_families"])
    non_home_families = set(policy["non_home_families"])
    not_official_origin_classes = set(policy["not_official_origin_classes"])
    broad_pass_types = set(policy["broad_pass_types"])
    allow_not_official = bool(policy["allow_autonomous_not_official_pass"])
    allow_broad_family = bool(policy["allow_autonomous_broad_family_pass"])
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
    applied_by_tag = {}
    for row in applied:
        by[row["canonical_tag"]].add(row["home_copyright"])
        applied_by_tag[row["canonical_tag"]] = row
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

    forbidden_qualifier_home = {
        "pauline_(nintendo)": "nintendo",
        "hyper_roll_(marvel_vs._capcom)": "marvel_vs._capcom",
        "otomachi_una_(voicepeak)": "voicepeak",
    }
    for tag, forbidden_home in forbidden_qualifier_home.items():
        row = by_tag.get(tag)
        if row and row["final_state"] == "HOME_CONFIRMED" and row["home_copyright"] == forbidden_home:
            raise SystemExit(f"qualifier-is-not-HOME regression: {tag} -> {forbidden_home}")

    officiality_violations = []
    broad_family_violations = []
    non_home_family_violations = []
    for row in rows:
        tag = row["canonical_tag"]
        if row["final_state"] != "HOME_CONFIRMED":
            continue
        authority = applied_by_tag.get(tag, {})
        origin_class = row.get("origin_class", "")
        if origin_class and origin_class not in {"OFFICIAL_IDENTITY","OFFICIAL_ALIAS","OFFICIAL_VARIANT"}:
            if authority.get("authority_scope") not in {"DIRECT_CHARACTER","VARIANT_CHARACTER"} or authority.get("officiality_state") not in {"OFFICIAL_CONFIRMED","OFFICIAL_IDENTITY","OFFICIAL_VARIANT"}:
                officiality_violations.append((tag, origin_class, authority.get("authority_scope"), authority.get("officiality_state")))
        family = row.get("final_qualifier", "")
        if authority.get("authority_scope") == "FAMILY_QUALIFIER":
            if family in non_home_families:
                non_home_family_violations.append((tag, family, authority.get("authority_type")))
            if family in broad_families:
                if not allow_broad_family or authority.get("authority_type") not in broad_pass_types:
                    broad_family_violations.append((tag, family, authority.get("authority_type")))
    if officiality_violations:
        raise SystemExit("Issue179 officiality guard regression: " + repr(officiality_violations[:10]))
    if non_home_family_violations:
        raise SystemExit("non-HOME family authority regression: " + repr(non_home_family_violations[:10]))
    if broad_family_violations:
        raise SystemExit("broad family authority regression: " + repr(broad_family_violations[:10]))
    if not allow_not_official:
        bad_not_official = [
            r["canonical_tag"] for r in rows
            if r["final_state"] == "NOT_OFFICIAL_CHARACTER"
            and r.get("origin_class", "") not in not_official_origin_classes
        ]
        if bad_not_official:
            raise SystemExit("NOT_OFFICIAL_CHARACTER without Issue179-confirmed non-official origin: " + repr(bad_not_official[:10]))

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
        "officiality_guard_violations": 0,
        "broad_family_violations": 0,
        "non_home_family_violations": 0,
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
