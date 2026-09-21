#!/usr/bin/env python3
"""Compile Issue #180 Character HOME v2 deterministically.

The compiler consumes the v2 foundation plus an optional persistent autonomous
review ledger. Review rows can add family/direct/variant authority, blocks, or
confirmed non-official identities without editing generated master CSVs.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).resolve().parents[2]
A = R / "artifacts/issue180-full-preflight"
D = A / "POST_NORMALIZED_REVIEW"
O = D / "MASTER_HOME_V2"
CAT = R / "docs/issue70/data/runtime/issue70_catalog_overlay.csv"
CENSUS = A / "CHARACTER_QUALIFIER_CENSUS.csv"
BASE_DIRECT = O / "BASE_DIRECT_AUTHORITY_V2.csv"
FAMILY_PROV = O / "FAMILY_AUTHORITY_PROVENANCE_V2.csv"
DECISIONS = R / "docs/issue180/autonomous/AUTHORITY_DECISIONS_V2.csv"
OUT = O / "CHARACTER_HOME_MASTER_V2.csv"
APPLIED = O / "APPLIED_AUTHORITY_LEDGER_V2.csv"
EXPECTED = 35890
ATTR = {
    "1st_costume", "2nd_costume", "3rd_costume", "4th_costume", "5th_costume",
    "new_year", "summer", "casual", "school_uniform", "female", "male", "young",
    "timeskip", "stand", "racehorse", "human", "character", "cat",
}
VALID_SCOPES = {"FAMILY_QUALIFIER", "DIRECT_CHARACTER", "VARIANT_CHARACTER", "NOT_OFFICIAL_CHARACTER", "BLOCK_CHARACTER"}


def read(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"missing required input: {path}")
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def nested(tag: str, family: str) -> bool:
    if not family:
        return False
    suffix = f"_({family})"
    return tag.lower().endswith(suffix.lower()) and tag[:-len(suffix)].endswith(")")


def main() -> None:
    catalog = read(CAT)
    chars = [r for r in catalog if r.get("category_name") == "Character"]
    copyrights = {r["canonical_tag"] for r in catalog if r.get("category_name") == "Copyright"}
    if len(chars) != EXPECTED:
        raise SystemExit("Character population drift")
    char_tags = {r["canonical_tag"] for r in chars}
    census = {r["canonical_tag"]: r for r in read(CENSUS)}
    if len(census) != EXPECTED:
        raise SystemExit("census drift")

    direct: dict[str, list[dict[str, str]]] = defaultdict(list)
    family: dict[str, list[dict[str, str]]] = defaultdict(list)
    variant: dict[str, list[dict[str, str]]] = defaultdict(list)
    blocks: set[str] = set()
    not_official: set[str] = set()

    def add_record(store: dict[str, list[dict[str, str]]], key: str, home: str, rec: dict[str, str]) -> None:
        if not key or not home:
            raise SystemExit("authority row missing key/home")
        if home not in copyrights:
            raise SystemExit(f"authority HOME absent from Copyright catalog: {key} -> {home}")
        store[key].append({**rec, "home_copyright": home})

    for row in read(BASE_DIRECT):
        add_record(direct, row["canonical_tag"], row["home_copyright"], {
            "authority_scope": "DIRECT_CHARACTER",
            "authority_type": row.get("authority_type", "V2_BASE_DIRECT"),
            "evidence_url": row.get("evidence_url", ""),
            "evidence_claim": row.get("evidence_claim", ""),
            "source_provenance": row.get("source_provenance", "BASE_DIRECT_AUTHORITY_V2.csv"),
            "validation_state": "PASS",
        })

    for row in read(FAMILY_PROV):
        if row.get("foundation_state") != "PASS_FASTPATH":
            continue
        add_record(family, row["family"], row["candidate_home"], {
            "authority_scope": "FAMILY_QUALIFIER",
            "authority_type": row.get("authority_basis", "V2_FAMILY_FASTPATH"),
            "evidence_url": row.get("evidence_url", ""),
            "evidence_claim": "Reviewed reusable qualifier-family authority",
            "source_provenance": row.get("source_file", "FAMILY_AUTHORITY_PROVENANCE_V2.csv"),
            "validation_state": "PASS",
        })

    decisions = read(DECISIONS)
    decision_pass = 0
    decision_unresolved = 0
    decision_higher = 0
    for row in decisions:
        scope = (row.get("scope") or "").strip()
        if not scope:
            continue
        if scope not in VALID_SCOPES:
            raise SystemExit(f"invalid autonomous authority scope: {scope}")
        state = (row.get("validation_state") or "").strip()
        if state in {"UNRESOLVED", "PENDING"}:
            decision_unresolved += 1
            continue
        if state == "NEEDS_HIGHER_REASONING":
            decision_higher += 1
            continue
        if state != "PASS":
            raise SystemExit(f"invalid autonomous validation_state: {state}")
        decision_pass += 1
        key = (row.get("key") or "").strip()
        home = (row.get("home_copyright") or "").strip()
        common = {
            "authority_scope": scope,
            "authority_type": row.get("authority_type", "AUTONOMOUS_REVIEW"),
            "evidence_url": row.get("evidence_url", ""),
            "evidence_claim": row.get("evidence_claim", ""),
            "source_provenance": "docs/issue180/autonomous/AUTHORITY_DECISIONS_V2.csv",
            "validation_state": "PASS",
            "base_character": row.get("base_character", ""),
            "officiality_state": row.get("officiality_state", ""),
        }
        if scope == "BLOCK_CHARACTER":
            if key not in char_tags:
                raise SystemExit(f"block references unknown Character: {key}")
            blocks.add(key)
        elif scope == "NOT_OFFICIAL_CHARACTER":
            if key not in char_tags:
                raise SystemExit(f"not-official references unknown Character: {key}")
            if home:
                raise SystemExit(f"NOT_OFFICIAL row must not have HOME: {key}")
            not_official.add(key)
        elif scope == "DIRECT_CHARACTER":
            if key not in char_tags:
                raise SystemExit(f"direct authority references unknown Character: {key}")
            add_record(direct, key, home, common)
        elif scope == "FAMILY_QUALIFIER":
            add_record(family, key.lower(), home, common)
        elif scope == "VARIANT_CHARACTER":
            if key not in char_tags:
                raise SystemExit(f"variant authority references unknown Character: {key}")
            variant[key].append({**common, "home_copyright": home})

    conflicts: set[str] = set()
    chosen_direct: dict[str, tuple[str, dict[str, str]]] = {}
    for tag, records in direct.items():
        homes = {r["home_copyright"] for r in records}
        if len(homes) != 1:
            conflicts.add(tag)
        else:
            home = next(iter(homes))
            chosen_direct[tag] = (home, records[0])

    chosen_family: dict[str, tuple[str, dict[str, str]]] = {}
    family_conflicts: set[str] = set()
    for fam, records in family.items():
        homes = {r["home_copyright"] for r in records}
        if len(homes) != 1:
            family_conflicts.add(fam)
        else:
            home = next(iter(homes))
            chosen_family[fam] = (home, records[0])

    home_by: dict[str, str] = {}
    rec_by: dict[str, dict[str, str]] = {}
    reason_by: dict[str, str] = {}
    for tag in char_tags:
        if tag in not_official or tag in blocks:
            continue
        direct_choice = chosen_direct.get(tag)
        fam = (census[tag].get("final_qualifier") or "").strip().lower()
        family_choice = None
        if fam and fam not in ATTR and not nested(tag, fam) and fam not in family_conflicts:
            family_choice = chosen_family.get(fam)
        homes = {x[0] for x in (direct_choice, family_choice) if x}
        if len(homes) > 1:
            conflicts.add(tag)
            continue
        if direct_choice:
            home_by[tag] = direct_choice[0]
            rec_by[tag] = direct_choice[1]
            reason_by[tag] = "DIRECT_CHARACTER_AUTHORITY"
        elif family_choice:
            home_by[tag] = family_choice[0]
            rec_by[tag] = family_choice[1]
            reason_by[tag] = "REUSABLE_FAMILY_QUALIFIER_AUTHORITY"

    pending = set(variant)
    changed = True
    while changed and pending:
        changed = False
        for tag in list(pending):
            records = variant[tag]
            bases = {r.get("base_character", "") for r in records if r.get("base_character")}
            if len(bases) != 1:
                conflicts.add(tag)
                pending.remove(tag)
                continue
            base = next(iter(bases))
            if base not in home_by:
                continue
            inherited = home_by[base]
            stated = {r.get("home_copyright", "") for r in records if r.get("home_copyright")}
            if stated and stated != {inherited}:
                conflicts.add(tag)
                pending.remove(tag)
                continue
            if tag in not_official or tag in blocks:
                conflicts.add(tag)
                pending.remove(tag)
                continue
            home_by[tag] = inherited
            rec_by[tag] = records[0]
            reason_by[tag] = "REVIEWED_VARIANT_INHERITANCE"
            pending.remove(tag)
            changed = True

    for tag in not_official:
        if tag in home_by or tag in direct:
            conflicts.add(tag)
    for tag in blocks:
        if tag in direct:
            conflicts.add(tag)

    if family_conflicts:
        conflicts.update({f"FAMILY::{x}" for x in family_conflicts})

    rows_out: list[dict[str, str]] = []
    applied: list[dict[str, str]] = []
    counts = Counter()
    for cr in chars:
        tag = cr["canonical_tag"]
        fam = (census[tag].get("final_qualifier") or "").strip().lower()
        if tag in conflicts:
            state = "HOME_UNRESOLVED"
            home = ""
            reason = "CONFLICTING_AUTHORITY"
        elif tag in not_official:
            state = "NOT_OFFICIAL_CHARACTER"
            home = ""
            reason = "SECOND_REVIEWED_NOT_OFFICIAL"
        elif tag in blocks:
            state = "HOME_UNRESOLVED"
            home = ""
            reason = "EXPLICIT_CHARACTER_BLOCK"
        elif tag in home_by:
            state = "HOME_CONFIRMED"
            home = home_by[tag]
            reason = reason_by[tag]
            rec = rec_by[tag]
            applied.append({
                "canonical_tag": tag,
                "family": fam,
                "home_copyright": home,
                "authority_scope": rec.get("authority_scope", ""),
                "authority_type": rec.get("authority_type", ""),
                "evidence_url": rec.get("evidence_url", ""),
                "evidence_claim": rec.get("evidence_claim", ""),
                "source_provenance": rec.get("source_provenance", ""),
                "decision_reason": reason,
                "production_approved": "false",
            })
        else:
            state = "HOME_UNRESOLVED"
            home = ""
            reason = "NO_ACCEPTED_HOME_AUTHORITY"
        counts[state] += 1
        rows_out.append({
            "canonical_tag": tag,
            "final_qualifier": fam,
            "final_state": state,
            "home_copyright": home,
            "decision_reason": reason,
            "production_approved": "false",
        })

    if len(rows_out) != EXPECTED or sum(counts.values()) != EXPECTED:
        raise SystemExit("v2 master accounting failure")
    if len(applied) != counts["HOME_CONFIRMED"]:
        raise SystemExit("applied authority/master confirmation mismatch")

    with OUT.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=rows_out[0].keys(), lineterminator="\n")
        w.writeheader()
        w.writerows(rows_out)
    with APPLIED.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=applied[0].keys(), lineterminator="\n")
        w.writeheader()
        w.writerows(applied)

    summary = {
        "character_population": EXPECTED,
        "states": dict(counts),
        "applied_authority_rows": len(applied),
        "autonomous_decision_rows": len(decisions),
        "autonomous_pass_rows": decision_pass,
        "autonomous_unresolved_rows": decision_unresolved,
        "autonomous_higher_reasoning_rows": decision_higher,
        "pending_reviewed_variants_without_confirmed_base": len(pending),
        "multi_home_or_policy_conflicts": len(conflicts),
        "family_authority_conflicts": len(family_conflicts),
        "accepted_source_modified": False,
        "production_modified": False,
    }
    (O / "character_home_master_v2_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
