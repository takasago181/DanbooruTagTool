#!/usr/bin/env python3
"""Compile Issue #180 Character HOME v2 deterministically.

The compiler consumes the v2 foundation plus an optional persistent autonomous
review ledger. Review rows can add family/direct/variant authority, blocks, or
confirmed non-official identities without editing generated master CSVs.
"""
from __future__ import annotations

import csv
import json
import re
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
DECISIONS_COMPAT = R / "docs/issue180/autonomous/AUTHORITY_DECISIONS_V2.csv"
DECISIONS_DIR = R / "docs/issue180/autonomous/decisions"
OUT = O / "CHARACTER_HOME_MASTER_V2.csv"
APPLIED = O / "APPLIED_AUTHORITY_LEDGER_V2.csv"
FAMILY_WORK = O / "FAMILY_WORK_QUEUE_V2.csv"
OFFICIALITY_WORK = O / "OFFICIALITY_WORK_QUEUE_V2.csv"
VARIANT_WORK = O / "VARIANT_WORK_QUEUE_V2.csv"
UNQUALIFIED_WORK = O / "UNQUALIFIED_WORK_QUEUE_V2.csv"
ORIGIN_HANDOFF = R / "docs/issue180/evidence/ISSUE179_ORIGIN_HANDOFF_V1.csv"
EXPECTED = 35890
POLICY_PATH = R / "docs/issue180/autonomous/AUTONOMOUS_POLICY_V2.json"
POLICY = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
if POLICY.get("version") != 2:
    raise SystemExit("unsupported autonomous policy version")
ATTR = set(POLICY["attribute_families"])
VARIANT_QUALIFIER_FAMILIES = set(POLICY["variant_qualifier_families"])
ORDINAL_COSTUME = re.compile(POLICY["ordinal_costume_regex"])
OFFICIAL_ORIGIN_CLASSES = set(POLICY["official_origin_classes"])
NOT_OFFICIAL_ORIGIN_CLASSES = set(POLICY["not_official_origin_classes"])
ALLOW_AUTONOMOUS_NOT_OFFICIAL = bool(POLICY["allow_autonomous_not_official_pass"])
VALID_SCOPES = {"FAMILY_QUALIFIER", "DISCOVERY_GROUP", "DIRECT_CHARACTER", "VARIANT_CHARACTER", "NOT_OFFICIAL_CHARACTER", "BLOCK_CHARACTER"}


def read(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"missing required input: {path}")
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def read_decisions() -> list[dict[str, str]]:
    paths = [DECISIONS_COMPAT] if DECISIONS_COMPAT.exists() else []
    if DECISIONS_DIR.exists():
        paths.extend(sorted(DECISIONS_DIR.glob("*.csv")))
    rows: list[dict[str, str]] = []
    for path in paths:
        for row in read(path):
            if not any((v or "").strip() for v in row.values()):
                continue
            rows.append({**row, "__source_file": str(path.relative_to(R))})
    return rows


def is_attribute_family(family: str) -> bool:
    return family in ATTR or family in VARIANT_QUALIFIER_FAMILIES or bool(ORDINAL_COSTUME.match(family or ""))


def nested(tag: str, family: str) -> bool:
    if not family:
        return False
    suffix = f"_({family})"
    return tag.lower().endswith(suffix.lower()) and tag[:-len(suffix)].endswith(")")


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str] | None = None) -> None:
    fields = fields or (list(rows[0].keys()) if rows else [])
    if not fields:
        raise SystemExit(f"cannot write schema-less CSV: {path}")
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    catalog = read(CAT)
    chars = [r for r in catalog if r.get("category_name") == "Character"]
    copyright_rows = [r for r in catalog if r.get("category_name") == "Copyright"]
    copyrights = {r["canonical_tag"] for r in copyright_rows}
    copyright_alias_index: dict[str, set[str]] = defaultdict(set)
    for row in copyright_rows:
        copyright_alias_index[row["canonical_tag"].lower()].add(row["canonical_tag"])
        for alias in (row.get("aliases", "") or "").split("|"):
            alias = alias.strip().lower()
            if alias:
                copyright_alias_index[alias].add(row["canonical_tag"])

    def canonical_root(value: str) -> str:
        value = (value or "").strip()
        if value in copyrights:
            return value
        hits = copyright_alias_index.get(value.lower(), set())
        if len(hits) == 1:
            return next(iter(hits))
        if not hits:
            raise SystemExit(f"authority HOME absent from Copyright catalog and aliases: {value}")
        raise SystemExit(f"ambiguous authority HOME alias: {value} -> {sorted(hits)}")

    if len(chars) != EXPECTED:
        raise SystemExit("Character population drift")
    char_tags = {r["canonical_tag"] for r in chars}
    census = {r["canonical_tag"]: r for r in read(CENSUS)}
    if len(census) != EXPECTED:
        raise SystemExit("census drift")
    origin_rows = read(ORIGIN_HANDOFF)
    origin_by = {
        r["canonical_tag"]: r["origin_class"].strip()
        for r in origin_rows
        if r.get("canonical_tag") in char_tags
    }
    origin_not_official = {
        tag: cls for tag, cls in origin_by.items()
        if cls in NOT_OFFICIAL_ORIGIN_CLASSES
    }
    origin_guarded = {
        tag: cls for tag, cls in origin_by.items()
        if cls not in OFFICIAL_ORIGIN_CLASSES and cls not in NOT_OFFICIAL_ORIGIN_CLASSES
    }

    direct: dict[str, list[dict[str, str]]] = defaultdict(list)
    family: dict[str, list[dict[str, str]]] = defaultdict(list)
    variant: dict[str, list[dict[str, str]]] = defaultdict(list)
    blocks: set[str] = set()
    # #179 is the authoritative source for confirmed non-official identity.
    # Autonomous #180 decisions cannot add to this set while policy disables it.
    not_official: set[str] = set(origin_not_official)
    foundation_family_rows = read(FAMILY_WORK)
    foundation_officiality_rows = read(OFFICIALITY_WORK)
    foundation_variant_rows = read(VARIANT_WORK)
    foundation_unqualified_rows = read(UNQUALIFIED_WORK)
    family_reason = {r["family"]: r.get("work_lane", "FAMILY_AUTHORITY_PENDING") for r in foundation_family_rows}
    officiality_reason = {r["canonical_tag"]: r.get("work_state", "OFFICIALITY_REVIEW_REQUIRED") for r in foundation_officiality_rows}
    variant_reason = {r["canonical_tag"]: r.get("work_state", "VARIANT_REVIEW_PENDING") for r in foundation_variant_rows}
    unqualified_reason = {r["canonical_tag"]: r.get("work_state", "ROSTER_DISCOVERY") for r in foundation_unqualified_rows}
    deferred_character_reason: dict[str, str] = {}
    deferred_family_reason: dict[str, str] = {}
    reviewed_discovery_groups: dict[str, dict[str, str]] = {}

    def add_record(store: dict[str, list[dict[str, str]]], key: str, home: str, rec: dict[str, str]) -> None:
        if not key or not home:
            raise SystemExit("authority row missing key/home")
        home = canonical_root(home)
        store[key].append({**rec, "home_copyright": home})

    for row in read(BASE_DIRECT):
        if row["canonical_tag"] in origin_guarded:
            raise SystemExit(f"origin-guarded Character leaked into BASE_DIRECT: {row['canonical_tag']} -> {origin_guarded[row['canonical_tag']]}")
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

    decisions = read_decisions()
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
        if state == "UNRESOLVED":
            decision_unresolved += 1
            key = (row.get("key") or "").strip()
            scope = (row.get("scope") or "").strip()
            reason = (row.get("notes") or row.get("evidence_claim") or "AUTONOMOUS_REVIEW_UNRESOLVED").strip()
            if scope == "FAMILY_QUALIFIER":
                deferred_family_reason[key.lower()] = reason
            elif scope == "DISCOVERY_GROUP":
                reviewed_discovery_groups[key.lower()] = {
                    "discovery_group": key.lower(),
                    "review_state": "UNRESOLVED",
                    "reason": reason,
                    "source_file": row.get("__source_file", ""),
                }
            elif key:
                deferred_character_reason[key] = reason
            continue
        if state == "PENDING":
            continue
        if state == "NEEDS_HIGHER_REASONING":
            decision_higher += 1
            key = (row.get("key") or "").strip()
            scope = (row.get("scope") or "").strip()
            reason = (row.get("notes") or row.get("evidence_claim") or "NEEDS_HIGHER_REASONING").strip()
            if scope == "FAMILY_QUALIFIER":
                deferred_family_reason[key.lower()] = "NEEDS_HIGHER_REASONING: " + reason
            elif scope == "DISCOVERY_GROUP":
                reviewed_discovery_groups[key.lower()] = {
                    "discovery_group": key.lower(),
                    "review_state": "NEEDS_HIGHER_REASONING",
                    "reason": reason,
                    "source_file": row.get("__source_file", ""),
                }
            elif key:
                deferred_character_reason[key] = "NEEDS_HIGHER_REASONING: " + reason
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
            "source_provenance": row.get("__source_file", "docs/issue180/autonomous/AUTHORITY_DECISIONS_V2.csv"),
            "validation_state": "PASS",
            "base_character": row.get("base_character", ""),
            "officiality_state": row.get("officiality_state", ""),
        }
        if scope == "DISCOVERY_GROUP":
            raise SystemExit("DISCOVERY_GROUP cannot produce PASS authority; use DIRECT_CHARACTER decisions")
        if scope == "BLOCK_CHARACTER":
            if key not in char_tags:
                raise SystemExit(f"block references unknown Character: {key}")
            blocks.add(key)
        elif scope == "NOT_OFFICIAL_CHARACTER":
            if not ALLOW_AUTONOMOUS_NOT_OFFICIAL:
                raise SystemExit("autonomous NOT_OFFICIAL_CHARACTER PASS is disabled; require a second-reviewed handoff")
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
        if tag in origin_guarded and direct_choice:
            if direct_choice[1].get("officiality_state", "") not in {"OFFICIAL_CONFIRMED", "OFFICIAL_IDENTITY", "OFFICIAL_VARIANT"}:
                direct_choice = None
        fam = (census[tag].get("final_qualifier") or "").strip().lower()
        family_choice = None
        if tag not in origin_guarded and fam and not is_attribute_family(fam) and not nested(tag, fam) and fam not in family_conflicts:
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
            if tag in home_by:
                if home_by[tag] != inherited:
                    conflicts.add(tag)
                # Same-HOME direct authority is corroboration; preserve the
                # already-selected direct authority rather than silently
                # replacing its provenance with variant inheritance.
                pending.remove(tag)
                changed = True
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
                "officiality_state": rec.get("officiality_state", origin_by.get(tag, "")),
                "origin_class": origin_by.get(tag, ""),
                "decision_reason": reason,
                "production_approved": "false",
            })
        else:
            state = "HOME_UNRESOLVED"
            home = ""
            if tag in officiality_reason:
                reason = officiality_reason[tag]
            elif tag in origin_guarded:
                reason = f"OFFICIALITY_REVIEW_REQUIRED_ISSUE179:{origin_guarded[tag]}"
            elif tag in deferred_character_reason:
                reason = deferred_character_reason[tag]
            elif tag in pending:
                reason = "VARIANT_BASE_HOME_NOT_CONFIRMED"
            elif tag in variant_reason:
                reason = variant_reason[tag]
            elif fam in deferred_family_reason:
                reason = deferred_family_reason[fam]
            elif fam in family_reason:
                reason = family_reason[fam]
            elif tag in unqualified_reason:
                reason = unqualified_reason[tag]
            else:
                reason = "NO_ACCEPTED_HOME_AUTHORITY"
        counts[state] += 1
        rows_out.append({
            "canonical_tag": tag,
            "final_qualifier": fam,
            "final_state": state,
            "home_copyright": home,
            "origin_class": origin_by.get(tag, ""),
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

    unresolved_set = {r["canonical_tag"] for r in rows_out if r["final_state"] == "HOME_UNRESOLVED"}
    deferred_character_tags = (set(deferred_character_reason) | blocks) & unresolved_set
    deferred_family_keys = set(deferred_family_reason)

    remaining_officiality = [
        dict(r) for r in foundation_officiality_rows
        if r["canonical_tag"] in unresolved_set and r["canonical_tag"] not in deferred_character_tags
    ]
    remaining_officiality.sort(key=lambda r: (-int(r.get("post_count", "0") or 0), r["canonical_tag"]))

    officiality_tags = {r["canonical_tag"] for r in remaining_officiality}
    remaining_family_counts = Counter()
    deferred_family_counts = Counter()
    for tag in unresolved_set:
        if tag in deferred_character_tags or tag in officiality_tags:
            continue
        fam = (census[tag].get("final_qualifier") or "").strip().lower()
        if fam and not is_attribute_family(fam) and not nested(tag, fam):
            if fam in deferred_family_keys:
                deferred_family_counts[fam] += 1
            else:
                remaining_family_counts[fam] += 1

    remaining_family = []
    for row in foundation_family_rows:
        count = remaining_family_counts.get(row["family"], 0)
        if not count:
            continue
        x = dict(row)
        x["character_rows"] = str(count)
        remaining_family.append(x)
    remaining_family.sort(key=lambda r: (-int(r["character_rows"]), r["family"]))

    deferred_family = []
    for row in foundation_family_rows:
        count = deferred_family_counts.get(row["family"], 0)
        if not count:
            continue
        x = dict(row)
        x["character_rows"] = str(count)
        x["deferred_reason"] = deferred_family_reason.get(row["family"], "AUTONOMOUS_REVIEW_UNRESOLVED")
        deferred_family.append(x)
    deferred_family.sort(key=lambda r: (-int(r["character_rows"]), r["family"]))

    remaining_variant = []
    for row in foundation_variant_rows:
        tag = row["canonical_tag"]
        if tag not in unresolved_set or tag in deferred_character_tags:
            continue
        x = dict(row)
        base = x.get("base_character", "")
        base_home = home_by.get(base, "")
        x["base_home_candidate"] = base_home
        if tag in origin_guarded:
            x["work_state"] = "OFFICIALITY_REVIEW_REQUIRED_ISSUE179"
        elif base_home:
            x["work_state"] = "BASE_HOME_READY_OFFICIALITY_REVIEW"
        elif base and base in char_tags:
            x["work_state"] = "BASE_EXISTS_HOME_PENDING"
        else:
            x["work_state"] = "BASE_NOT_FOUND_OR_NONTRIVIAL"
        remaining_variant.append(x)
    remaining_variant.sort(key=lambda r: (-int(r.get("post_count", "0") or 0), r["canonical_tag"]))

    remaining_unqualified = [
        dict(r) for r in foundation_unqualified_rows
        if r["canonical_tag"] in unresolved_set and r["canonical_tag"] not in deferred_character_tags
    ]
    remaining_unqualified.sort(key=lambda r: (-int(r.get("post_count", "0") or 0), r["canonical_tag"]))

    deferred_character = []
    row_by_tag = {r["canonical_tag"]: r for r in rows_out}
    for tag in sorted(deferred_character_tags):
        row = row_by_tag[tag]
        deferred_character.append({
            "canonical_tag": tag,
            "final_qualifier": row.get("final_qualifier", ""),
            "origin_class": row.get("origin_class", ""),
            "deferred_reason": deferred_character_reason.get(tag, "EXPLICIT_CHARACTER_BLOCK"),
            "production_approved": "false",
        })

    reviewed_group_rows = [reviewed_discovery_groups[k] for k in sorted(reviewed_discovery_groups)]
    write_csv(
        O / "REVIEWED_DISCOVERY_GROUPS_V2.csv",
        reviewed_group_rows,
        ["discovery_group","review_state","reason","source_file"],
    )
    write_csv(O / "REMAINING_OFFICIALITY_WORK_V2.csv", remaining_officiality, list(foundation_officiality_rows[0].keys()) if foundation_officiality_rows else None)
    write_csv(O / "REMAINING_FAMILY_WORK_V2.csv", remaining_family, list(foundation_family_rows[0].keys()) if foundation_family_rows else None)
    write_csv(O / "REMAINING_VARIANT_WORK_V2.csv", remaining_variant, list(foundation_variant_rows[0].keys()) if foundation_variant_rows else None)
    write_csv(O / "REMAINING_UNQUALIFIED_WORK_V2.csv", remaining_unqualified, list(foundation_unqualified_rows[0].keys()) if foundation_unqualified_rows else None)
    write_csv(
        O / "DEFERRED_FAMILY_REVIEW_V2.csv",
        deferred_family,
        (list(foundation_family_rows[0].keys()) + ["deferred_reason"]) if foundation_family_rows else None,
    )
    write_csv(
        O / "DEFERRED_CHARACTER_REVIEW_V2.csv",
        deferred_character,
        ["canonical_tag","final_qualifier","origin_class","deferred_reason","production_approved"],
    )
    remaining_summary = {
        "officiality_rows": len(remaining_officiality),
        "family_rows": sum(int(r["character_rows"]) for r in remaining_family),
        "family_families": len(remaining_family),
        "variant_rows": len(remaining_variant),
        "variant_base_home_ready": sum(r.get("work_state") == "BASE_HOME_READY_OFFICIALITY_REVIEW" for r in remaining_variant),
        "unqualified_rows": len(remaining_unqualified),
        "deferred_character_rows": len(deferred_character),
        "deferred_family_rows": sum(int(r["character_rows"]) for r in deferred_family),
        "deferred_family_families": len(deferred_family),
        "reviewed_discovery_groups": len(reviewed_discovery_groups),
        "total_unresolved": len(unresolved_set),
    }
    active = remaining_summary["officiality_rows"] + remaining_summary["family_rows"] + remaining_summary["variant_rows"] + remaining_summary["unqualified_rows"]
    deferred = remaining_summary["deferred_character_rows"] + remaining_summary["deferred_family_rows"]
    if active + deferred != len(unresolved_set):
        raise SystemExit(f"dynamic remaining/deferred partition mismatch active={active} deferred={deferred} unresolved={len(unresolved_set)}")
    (O / "remaining_work_v2_summary.json").write_text(
        json.dumps(remaining_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    state_counts = {
        "HOME_CONFIRMED": counts["HOME_CONFIRMED"],
        "HOME_UNRESOLVED": counts["HOME_UNRESOLVED"],
        "NOT_OFFICIAL_CHARACTER": counts["NOT_OFFICIAL_CHARACTER"],
    }
    unresolved_reason_counts = Counter(r["decision_reason"] for r in rows_out if r["final_state"] == "HOME_UNRESOLVED")
    authority_scope_counts = Counter(r["authority_scope"] for r in applied)
    authority_type_counts = Counter(r["authority_type"] for r in applied)
    summary = {
        "character_population": EXPECTED,
        "states": state_counts,
        "applied_authority_rows": len(applied),
        "authority_scope_counts": dict(authority_scope_counts),
        "authority_type_counts": dict(authority_type_counts),
        "unresolved_reason_counts": dict(unresolved_reason_counts),
        "autonomous_decision_rows": len(decisions),
        "autonomous_pass_rows": decision_pass,
        "autonomous_unresolved_rows": decision_unresolved,
        "autonomous_pending_rows": sum((r.get("validation_state") or "").strip() == "PENDING" for r in decisions),
        "autonomous_higher_reasoning_rows": decision_higher,
        "pending_reviewed_variants_without_confirmed_base": len(pending),
        "multi_home_or_policy_conflicts": len(conflicts),
        "family_authority_conflicts": len(family_conflicts),
        "remaining_work": remaining_summary,
        "accepted_source_modified": False,
        "production_modified": False,
    }
    (O / "character_home_master_v2_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
