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
FIELDS = ["canonical_tag", "final_state", "home_copyright", "origin_class", "reason_code", "resolver_path", "conflict_homes"]
MIGRATION_FIELDS = ["canonical_tag", "v2_home", "v3_state", "v3_home", "migration_state", "difference_class", "difference_detail", "evidence_path"]

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

    if not V2_MASTER.exists():
        raise FileNotFoundError(f"migration baseline missing: {V2_MASTER}")
    v2_rows = read_csv(V2_MASTER)
    v2_by = {r["canonical_tag"]: r for r in v2_rows if r.get("final_state") == "HOME_CONFIRMED"}
    v3_by = {r["canonical_tag"]: r for r in master}
    decision_by_key: dict[str, list[dict[str, str]]] = defaultdict(list)
    for d in load_decisions():
        if d.get("validation_state") == "PASS":
            decision_by_key[d.get("key", "")].append(d)
    applied_by_tag: dict[str, dict[str, str]] = {}
    if V2_APPLIED.exists():
        applied_by_tag = {r.get("canonical_tag", ""): r for r in read_csv(V2_APPLIED)}
    migration: list[dict[str, str]] = []
    for tag, old in sorted(v2_by.items()):
        new = v3_by.get(tag)
        detail = ""
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
            elif drows and not any(e.get("subject_key") == tag for e in ledger if e.get("relation_type") in {"DIRECT_HOME", "VARIANT_OF"}): cls = "EVIDENCE_MIGRATION_ERROR"
            elif new.get("reason_code") in {"FAMILY_HOME_MISSING", "FAMILY_MEMBERSHIP_MISSING"}: cls = "EVIDENCE_MIGRATION_ERROR"
            elif new.get("reason_code") == "IDENTITY_REVIEW_REQUIRED": cls = "SOURCE_DRIFT"
            else: cls = "RESOLVER_BEHAVIOR_CHANGE" if drows else "EVIDENCE_MIGRATION_ERROR"
            path = ""
            old_prov = applied_by_tag.get(tag, {})
            detail = f"{new.get('reason_code','NO_SAFE_PATH')}; v2_scope={old_prov.get('authority_scope','')}; v2_authority={old_prov.get('authority_type','')}; v2_provenance={old_prov.get('source_provenance','')}; no validated v3 path to old HOME."
        migration.append({"canonical_tag": tag, "v2_home": old.get("home_copyright", ""), "v3_state": state,
                          "v3_home": home, "migration_state": result, "difference_class": cls, "difference_detail": detail, "evidence_path": path})
    write_csv(MIGRATION, migration, MIGRATION_FIELDS)
    from collections import Counter
    counts = Counter(r["migration_state"] for r in migration)
    classes = Counter(r["difference_class"] for r in migration if r["difference_class"])
    summary = {"v2_confirmed": len(v2_by), "migration_counts": dict(counts), "difference_classes": dict(classes),
               "v3_states": dict(Counter(r["final_state"] for r in master)),
               "v3_reason_counts": dict(Counter(r["reason_code"] for r in master if r["reason_code"])),
               "multi_home_conflicts": sum(r["reason_code"] == "EVIDENCE_CONFLICT" for r in master),
               "copyright_roots_missing": sum(r["final_state"] == "HOME_CONFIRMED" and r["home_copyright"] not in root_set for r in master),
               "master_sha256": sha256_file(MASTER), "migration_sha256": sha256_file(MIGRATION)}
    write_json(OUT / "resolver_summary_v3.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
