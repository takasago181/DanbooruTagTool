#!/usr/bin/env python3
"""Resolve one HOME per Character from validated, traceable v3 evidence paths."""
from __future__ import annotations
import json
import sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _issue180_v3_common import *

MASTER = OUT / "character_home_master_v3.csv"
MIGRATION = OUT / "migration_comparison_v3.csv"
GAP_RECONCILIATION = DOCS_OUT / "MIGRATION_GAP_RECONCILIATION_V3.csv"
FIELDS = ["canonical_tag", "final_state", "home_copyright", "origin_class", "reason_code", "resolver_path", "conflict_homes"]
MIGRATION_FIELDS = ["canonical_tag", "v2_home", "v2_resolution_route", "authority_scope", "authority_type", "source_provenance", "evidence_url", "evidence_claim", "family", "base_character", "v3_state", "v3_home", "current_v3_rejection_reason", "migration_state", "primary_migration_loss_reason", "difference_class", "difference_detail", "evidence_path"]

def main() -> None:
    characters, copyrights, char_by = load_catalog()
    root_set = {r["canonical_tag"] for r in copyrights}
    ledger = read_csv(OUT / "evidence_ledger_v3.csv")
    graph = read_csv(OUT / "structure_graph_v3.csv")
    origin_rows = read_csv(ORIGIN)
    origin_by = {r.get("canonical_tag", ""): r.get("origin_class", "") for r in origin_rows}
    direct: dict[str, list[dict[str, str]]] = defaultdict(list)
    family_home: dict[str, list[dict[str, str]]] = defaultdict(list)
    membership: dict[str, list[dict[str, str]]] = defaultdict(list)
    variant_of: dict[str, list[dict[str, str]]] = defaultdict(list)
    for e in ledger:
        if e.get("review_state") != "VALIDATED":
            continue
        rel = e["relation_type"]
        if rel == "DIRECT_HOME": direct[e["subject_key"]].append(e)
        elif rel == "FAMILY_HOME": family_home[e["subject_key"]].append(e)
        elif rel == "MEMBER_OF": membership[e["subject_key"]].append(e)
        elif rel == "VARIANT_OF": variant_of[e["subject_key"]].append(e)

    family_candidates: dict[str, list[str]] = defaultdict(list)
    variant_candidates: dict[str, list[str]] = defaultdict(list)
    invalid_home_candidates: set[str] = set()
    invalid_family_homes: set[str] = set()
    for e in graph:
        if e["relation_type"] == "MEMBER_OF": family_candidates[e["subject_key"]].append(e["object_key"])
        elif e["relation_type"] == "VARIANT_OF": variant_candidates[e["subject_key"]].append(e["object_key"])
        elif e["relation_type"] == "DIRECT_HOME" and e.get("review_state") == "CANDIDATE" and e["object_key"] not in root_set:
            invalid_home_candidates.add(e["subject_key"])
        elif e["relation_type"] == "FAMILY_HOME" and e.get("review_state") == "CANDIDATE" and e["object_key"] not in root_set:
            invalid_family_homes.add(e["subject_key"])

    paths: dict[str, list[dict[str, object]]] = defaultdict(list)
    for tag, evidence in direct.items():
        for e in evidence:
            if e["object_key"] in root_set:
                paths[tag].append({"home": e["object_key"], "kind": "DIRECT_HOME", "evidence_ids": [e["evidence_id"]],
                                   "path_edges": [{"relation_type": "DIRECT_HOME", "subject_key": tag, "object_key": e["object_key"], "evidence_id": e["evidence_id"]}]})
    for tag, memberships in membership.items():
        for m in memberships:
            for f in family_home.get(m["object_key"], []):
                if f["object_key"] in root_set:
                    paths[tag].append({"home": f["object_key"], "kind": "FAMILY_HOME", "evidence_ids": [m["evidence_id"], f["evidence_id"]],
                                       "path_edges": [{"relation_type": "MEMBER_OF", "subject_key": tag, "object_key": m["object_key"], "evidence_id": m["evidence_id"]},
                                                      {"relation_type": "FAMILY_HOME", "subject_key": m["object_key"], "object_key": f["object_key"], "evidence_id": f["evidence_id"]}]})

    visiting: set[str] = set()
    resolved_variant_paths: dict[str, list[dict[str, object]]] = {}
    def variant_paths(tag: str) -> list[dict[str, object]]:
        if tag in resolved_variant_paths:
            return resolved_variant_paths[tag]
        if tag in visiting:
            return []
        visiting.add(tag)
        found: list[dict[str, object]] = []
        for relation in variant_of.get(tag, []):
            base = relation["object_key"]
            base_paths = list(paths.get(base, [])) + variant_paths(base)
            for bp in base_paths:
                found.append({"home": bp["home"], "kind": "VARIANT_INHERITANCE",
                              "evidence_ids": [relation["evidence_id"], *bp["evidence_ids"]],
                              "path_edges": [{"relation_type": "VARIANT_OF", "subject_key": tag, "object_key": base, "evidence_id": relation["evidence_id"]}, *bp["path_edges"]]})
        visiting.remove(tag)
        resolved_variant_paths[tag] = found
        return found
    for tag in sorted(char_by):
        paths[tag].extend(variant_paths(tag))

    master: list[dict[str, str]] = []
    for tag in sorted(char_by):
        candidates = paths.get(tag, [])
        selected_home, homes, corroborating = select_home(candidates)
        origin = origin_by.get(tag, "")
        if origin == "UNKNOWN":
            state, home, reason = "HOME_UNRESOLVED", "", "IDENTITY_REVIEW_REQUIRED"
        elif len(homes) > 1:
            state, home, reason = "HOME_UNRESOLVED", "", "EVIDENCE_CONFLICT"
        elif len(homes) == 1:
            state, home, reason = "HOME_CONFIRMED", selected_home, ""
        else:
            state, home = "HOME_UNRESOLVED", ""
            family_cands = sorted(set(family_candidates.get(tag, [])))
            variant_cands = sorted(set(variant_candidates.get(tag, [])))
            if tag in invalid_home_candidates or set(family_cands) & invalid_family_homes:
                reason = "COPYRIGHT_ROOT_MISSING"
            elif variant_cands:
                validated_bases = [e["object_key"] for e in variant_of.get(tag, [])]
                if not validated_bases:
                    reason = "VARIANT_OFFICIALITY_MISSING"
                elif not any(paths.get(base) for base in validated_bases):
                    reason = "BASE_IDENTITY_MISSING"
                else:
                    reason = "NO_SAFE_PATH"
            elif family_cands:
                validated_families = [e["object_key"] for e in membership.get(tag, [])]
                if any(f in family_home for f in family_cands) and not validated_families:
                    reason = "FAMILY_MEMBERSHIP_MISSING"
                else:
                    reason = "FAMILY_HOME_MISSING"
            elif any(not e.get("evidence_url") for e in direct.get(tag, [])):
                reason = "DIRECT_AUTHORITY_MISSING"
            else:
                reason = "DIRECT_AUTHORITY_MISSING"
        chosen = corroborating if state == "HOME_CONFIRMED" else []
        ids = sorted({eid for p in chosen for eid in p["evidence_ids"]})
        conflict = ";".join(homes) if len(homes) > 1 else ""
        master.append({"canonical_tag": tag, "final_state": state, "home_copyright": home,
                       "origin_class": origin, "reason_code": reason,
                       "resolver_path": json.dumps(chosen, ensure_ascii=False, separators=(",", ":")) if chosen else "",
                       "conflict_homes": conflict})
    write_csv(MASTER, master, FIELDS)

    if not V3_BASELINE.exists():
        raise FileNotFoundError(f"tracked v2 comparison baseline missing: {V3_BASELINE}")
    v2_rows = read_csv(V3_BASELINE)
    v2_by = {r["canonical_tag"]: r for r in v2_rows}
    v3_by = {r["canonical_tag"]: r for r in master}
    decision_by_key: dict[str, list[dict[str, str]]] = defaultdict(list)
    for d in load_decisions():
        if d.get("validation_state") == "PASS":
            decision_by_key[d.get("key", "")].append(d)
    applied_by_tag: dict[str, dict[str, str]] = v2_by
    direct_authority_homes: dict[str, set[str]] = defaultdict(set)
    for evidence in ledger:
        if evidence.get("relation_type") == "DIRECT_HOME" and evidence.get("review_state") == "VALIDATED":
            direct_authority_homes[evidence.get("subject_key", "")].add(evidence.get("object_key", ""))

    def has_old_family_base_conflict(tag: str, old_home: str) -> bool:
        if "_(" not in tag:
            return False
        base = tag.rsplit("_(", 1)[0]
        roots = direct_authority_homes.get(base, set())
        return base in char_by and bool(roots) and roots != {old_home}

    migration: list[dict[str, str]] = []
    for tag, old in sorted(v2_by.items()):
        new = v3_by.get(tag)
        detail = ""
        primary_loss = ""
        if new is None:
            state, home, result, cls, path = "MISSING", "", "V3_UNRESOLVED", "SOURCE_DRIFT", ""
            detail = "Character key exists in the v2 baseline but not the current Issue #70 source."
        elif new["final_state"] == "HOME_CONFIRMED" and new["home_copyright"] == old.get("home_copyright", ""):
            state, home, result, cls, path = new["final_state"], new["home_copyright"], "SAME_HOME", "", new["resolver_path"]
            detail = "Same HOME recovered through a validated v3 evidence path."
        elif new["final_state"] == "HOME_CONFIRMED":
            state, home, result, cls, path = new["final_state"], new["home_copyright"], "DIFFERENT_HOME", "OLD_DECISION_DEFECT", new["resolver_path"]
            detail = "Validated v3 path resolves to a different HOME than v2; no automatic overwrite performed."
        else:
            state, home, result = new["final_state"], new["home_copyright"], "V3_UNRESOLVED"
            drows = decision_by_key.get(tag, [])
            if new.get("reason_code") == "EVIDENCE_CONFLICT": cls = "OLD_DECISION_DEFECT"
            elif has_old_family_base_conflict(tag, old.get("home_copyright", "")):
                cls = "OLD_DECISION_DEFECT"
                base = tag.rsplit("_(", 1)[0]
                detail = (f"v2 family HOME {old.get('home_copyright')!r} conflicts with independently validated direct HOME(s) "
                          f"{sorted(direct_authority_homes[base])!r} for exact existing base Character {base!r}; "
                          "the v3 family/variant path is withheld and no alternate HOME is inferred.")
            elif old.get("source_provenance") == "SPLATOON_OFFICIAL_HOME_V1.csv" and new.get("reason_code") == "VARIANT_OFFICIALITY_MISSING": cls = "OLD_DECISION_DEFECT"
            elif drows and not any(e.get("subject_key") == tag for e in ledger if e.get("relation_type") in {"DIRECT_HOME", "VARIANT_OF"}): cls = "EVIDENCE_MIGRATION_ERROR"
            elif (new.get("reason_code") in {"FAMILY_HOME_MISSING", "FAMILY_MEMBERSHIP_MISSING"} and tag.endswith(")")
                  and tag.rsplit("_(", 1)[-1][:-1].lower() in STRUCTURAL_FAMILY_BLOCKS):
                cls = "RESOLVER_BEHAVIOR_CHANGE"
                detail = (f"HOME_UNRESOLVED / {new.get('reason_code')}; the exact terminal family qualifier is explicitly blocked from bulk structural expansion "
                          f"as a company/platform/event/crossover/costume/generic class ({tag.rsplit('_(', 1)[-1][:-1]}). Prior v2 mapping is retained in the comparison baseline only.")
            elif new.get("reason_code") in {"FAMILY_HOME_MISSING", "FAMILY_MEMBERSHIP_MISSING"}: cls = "EVIDENCE_MIGRATION_ERROR"
            elif new.get("reason_code") == "IDENTITY_REVIEW_REQUIRED": cls = "SOURCE_DRIFT"
            else: cls = "RESOLVER_BEHAVIOR_CHANGE" if drows else "EVIDENCE_MIGRATION_ERROR"
            path = ""
            old_prov = applied_by_tag.get(tag, {})
            source_prov = old.get("source_provenance", "")
            scope = old.get("authority_scope", "")
            authority = old.get("authority_type", "")
            if scope == "VARIANT_CHARACTER": primary_loss = "VARIANT_CHAIN_NOT_MIGRATED"
            elif scope == "FAMILY_QUALIFIER" and authority == "POLICY_ROOT_NORMALIZATION": primary_loss = "ROOT_POLICY_NOT_MIGRATED"
            elif scope == "FAMILY_QUALIFIER" and authority in {"EXACT_COPYRIGHT_REVIEWED", "FIRST_PARTY_REVIEWED", "FIRST_PARTY_CANONICAL_ROOT"}: primary_loss = "FAMILY_FASTPATH_NOT_MIGRATED"
            elif source_prov.startswith("docs/issue180/autonomous/decisions/"): primary_loss = "APPROVED_REPO_EVIDENCE_NOT_MIGRATED"
            elif scope == "DIRECT_CHARACTER" and source_prov.startswith("DIRECT_OFFICIAL_CHARACTER_ROSTER"): primary_loss = "APPROVED_REPO_EVIDENCE_NOT_MIGRATED"
            elif scope == "DIRECT_CHARACTER": primary_loss = "FOUNDATION_DIRECT_NOT_MIGRATED"
            else: primary_loss = "OTHER"
            if cls != "OLD_DECISION_DEFECT" or not has_old_family_base_conflict(tag, old.get("home_copyright", "")):
                detail = f"{new.get('reason_code','NO_SAFE_PATH')}; v2_scope={old_prov.get('authority_scope','')}; v2_authority={old_prov.get('authority_type','')}; v2_provenance={old_prov.get('source_provenance','')}; no validated v3 path to old HOME."
            if cls == "RESOLVER_BEHAVIOR_CHANGE" and tag.endswith(")") and tag.rsplit("_(", 1)[-1][:-1].lower() in STRUCTURAL_FAMILY_BLOCKS:
                detail = (f"HOME_UNRESOLVED / {new.get('reason_code')}; exact terminal qualifier {tag.rsplit('_(', 1)[-1][:-1]!r} is explicitly blocked from bulk structural expansion "
                          "as a company/platform/event/crossover/costume/generic class. The v2 mapping is retained in the comparison baseline only.")
        source_prov = old.get("source_provenance", "")
        family = old.get("family", "")
        base_character = next((d.get("base_character", "") for d in decision_by_key.get(tag, []) if d.get("scope") == "VARIANT_CHARACTER"), "")
        migration.append({"canonical_tag": tag, "v2_home": old.get("home_copyright", ""), "v2_resolution_route": old.get("v2_resolution_route", old.get("authority_scope", "")),
                          "authority_scope": old.get("authority_scope", ""), "authority_type": old.get("authority_type", ""), "source_provenance": source_prov,
                          "evidence_url": old.get("evidence_url", ""), "evidence_claim": old.get("evidence_claim", ""), "family": family,
                          "base_character": base_character, "v3_state": state, "v3_home": home,
                          "current_v3_rejection_reason": new.get("reason_code", ""), "migration_state": result,
                          "primary_migration_loss_reason": primary_loss, "difference_class": cls, "difference_detail": detail, "evidence_path": path})
    write_csv(MIGRATION, migration, MIGRATION_FIELDS)
    from collections import Counter
    pre_gap = read_csv(V3_PRE_REPAIR_GAP) if V3_PRE_REPAIR_GAP.exists() else []
    gap_rows: list[dict[str, str]] = []
    gap_fields = ["canonical_tag", "v2_home", "v2_resolution_route", "authority_scope", "authority_type", "source_provenance", "evidence_url", "evidence_claim", "family", "base_character", "pre_repair_rejection_reason", "primary_migration_loss_reason", "repair_status", "current_v3_rejection_reason", "difference_class", "v3_home", "evidence_path"]
    for previous in pre_gap:
        tag = previous["canonical_tag"]
        old = v2_by.get(tag, {})
        new = v3_by.get(tag, {})
        scope, authority, source_prov = old.get("authority_scope", ""), old.get("authority_type", ""), old.get("source_provenance", "")
        if scope == "FAMILY_QUALIFIER" and authority == "POLICY_ROOT_NORMALIZATION": primary = "ROOT_POLICY_NOT_MIGRATED"
        elif scope == "FAMILY_QUALIFIER": primary = "FAMILY_FASTPATH_NOT_MIGRATED"
        elif scope == "VARIANT_CHARACTER": primary = "VARIANT_CHAIN_NOT_MIGRATED"
        elif scope == "DIRECT_CHARACTER" and (source_prov.startswith("docs/issue180/") or "ROSTER" in authority or "ROSTER" in source_prov or source_prov.endswith("OFFICIAL_HOME_V1.csv")): primary = "APPROVED_REPO_EVIDENCE_NOT_MIGRATED"
        elif scope == "DIRECT_CHARACTER" and source_prov: primary = "FOUNDATION_DIRECT_NOT_MIGRATED"
        elif not source_prov: primary = "PROVENANCE_PARSE_FAILURE"
        else: primary = "OTHER"
        decisions_for_tag = decision_by_key.get(tag, [])
        base = next((d.get("base_character", "") for d in decisions_for_tag if d.get("scope") == "VARIANT_CHARACTER"), "")
        confirmed_same = new.get("final_state") == "HOME_CONFIRMED" and new.get("home_copyright") == old.get("home_copyright", "")
        if source_prov == "SPLATOON_OFFICIAL_HOME_V1.csv" and new.get("reason_code") == "VARIANT_OFFICIALITY_MISSING": primary = "UNSUPPORTED_LEGACY_DIRECT_VARIANT"
        gap_rows.append({"canonical_tag": tag, "v2_home": old.get("home_copyright", ""),
            "v2_resolution_route": old.get("v2_resolution_route", scope), "authority_scope": scope,
            "authority_type": authority, "source_provenance": source_prov, "evidence_url": old.get("evidence_url", ""),
            "evidence_claim": old.get("evidence_claim", ""), "family": old.get("family", ""), "base_character": base,
            "pre_repair_rejection_reason": previous.get("difference_detail", previous.get("difference_class", "")),
            "primary_migration_loss_reason": primary,
            "repair_status": "RECOVERED_SAME_HOME" if confirmed_same else ("DIFFERENT_HOME_REQUIRES_REVIEW" if new.get("final_state") == "HOME_CONFIRMED" else "UNRESOLVED_AFTER_REPAIR"),
            "current_v3_rejection_reason": new.get("reason_code", ""),
            "difference_class": "" if confirmed_same else ("OLD_DECISION_DEFECT" if (source_prov == "SPLATOON_OFFICIAL_HOME_V1.csv" and new.get("reason_code") == "VARIANT_OFFICIALITY_MISSING") or has_old_family_base_conflict(tag, old.get("home_copyright", "")) else ("RESOLVER_BEHAVIOR_CHANGE" if new.get("reason_code") in {"FAMILY_HOME_MISSING", "FAMILY_MEMBERSHIP_MISSING"} and tag.endswith(")") and tag.rsplit("_(", 1)[-1][:-1].lower() in STRUCTURAL_FAMILY_BLOCKS else previous.get("difference_class", "OTHER"))),
            "v3_home": new.get("home_copyright", ""), "evidence_path": new.get("resolver_path", "")})
    write_csv(GAP_RECONCILIATION, gap_rows, gap_fields)
    counts = Counter(r["migration_state"] for r in migration)
    classes = Counter(r["difference_class"] for r in migration if r["difference_class"])
    summary = {"v2_confirmed": len(v2_by), "migration_counts": dict(counts), "difference_classes": dict(classes),
               "v3_states": dict(Counter(r["final_state"] for r in master)),
               "v3_reason_counts": dict(Counter(r["reason_code"] for r in master if r["reason_code"])),
               "multi_home_conflicts": sum(r["reason_code"] == "EVIDENCE_CONFLICT" for r in master),
               "copyright_roots_missing": sum(r["final_state"] == "HOME_CONFIRMED" and r["home_copyright"] not in root_set for r in master),
               "master_sha256": sha256_file(MASTER), "migration_sha256": sha256_file(MIGRATION)}
    summary["pre_repair_gap_rows"] = len(gap_rows)
    summary["pre_repair_gap_primary_reasons"] = dict(sorted(Counter(r["primary_migration_loss_reason"] for r in gap_rows).items()))
    summary["pre_repair_gap_repair_status"] = dict(sorted(Counter(r["repair_status"] for r in gap_rows).items()))
    summary["pre_repair_gap_unique_keys"] = len({r["canonical_tag"] for r in gap_rows}) == len(gap_rows)
    write_json(OUT / "resolver_summary_v3.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
