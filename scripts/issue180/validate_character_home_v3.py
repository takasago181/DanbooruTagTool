#!/usr/bin/env python3
"""Validate v3 source, evidence paths, coverage, roots, conflicts and reproducibility artifacts."""
from __future__ import annotations
import json
import re
import sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _issue180_v3_common import *

def main() -> None:
    characters, copyrights, char_by = load_catalog()
    master = read_csv(OUT / "character_home_master_v3.csv")
    ledger = read_csv(OUT / "evidence_ledger_v3.csv")
    units = read_csv(OUT / "research_units_v3.csv")
    roots = {r["canonical_tag"] for r in copyrights}
    errors: list[str] = []
    source_tags = [r["canonical_tag"] for r in characters]
    output_tags = [r["canonical_tag"] for r in master]
    if len(source_tags) != 35890:
        errors.append(f"INPUT_INTEGRITY: expected 35890 Character source rows, got {len(source_tags)}")
    if len(set(source_tags)) != len(source_tags): errors.append("INPUT_INTEGRITY: duplicate source Character key")
    if len(master) != len(source_tags) or len(set(output_tags)) != len(output_tags) or set(source_tags) != set(output_tags):
        errors.append("LOSS_INTEGRITY: master keys are not an exact one-to-one copy of the source Character population")
    if any(r.get("final_state") not in FINAL_STATES for r in master): errors.append("COVERAGE_INTEGRITY: invalid or missing final state")
    if any((r["final_state"] == "HOME_CONFIRMED") != bool(r["home_copyright"]) for r in master): errors.append("SINGLE_HOME: state/home cardinality mismatch")
    if any(r["final_state"] == "HOME_UNRESOLVED" and not r["reason_code"] for r in master): errors.append("COVERAGE_INTEGRITY: unresolved Character missing concrete reason")
    if any(r["home_copyright"] and r["home_copyright"] not in roots for r in master): errors.append("ROOT_INTEGRITY: confirmed HOME not in current Copyright catalog")
    ledger_by_id = {e["evidence_id"]: e for e in ledger}
    policy = json.loads((ROOT / "docs/issue180/autonomous/AUTONOMOUS_POLICY_V2.json").read_text(encoding="utf-8"))
    root_map = {str(k).lower(): str(v) for k, v in policy.get("root_policy_normalization", {}).items()}
    allowed_bases = {"EXTERNAL_AUTHORITY", "APPROVED_REPO_EVIDENCE", "REVIEWED_QUALIFIER_COPYRIGHT", "ROOT_POLICY_NORMALIZATION", "REVIEWED_VARIANT_AUTHORITY", "SAFE_STRUCTURAL_VARIANT"}
    character_keys = set(source_tags)
    master_by_tag = {r["canonical_tag"]: r for r in master}
    family_homes = {}
    for e in ledger:
        if e.get("relation_type") == "FAMILY_HOME" and e.get("review_state") == "VALIDATED":
            family_homes.setdefault(e["subject_key"].lower(), set()).add(e["object_key"])
    copyright_aliases = {}
    for root_row in copyrights:
        for alias in [root_row.get("canonical_tag", ""), *(root_row.get("aliases", "") or "").split("|")]:
            if alias.strip(): copyright_aliases.setdefault(alias.strip().lower(), set()).add(root_row["canonical_tag"])
    for e in ledger:
        if e.get("evidence_basis") not in allowed_bases:
            errors.append(f"EVIDENCE_INTEGRITY: unsupported/empty evidence basis for {e['evidence_id']}")
        expected_id = evidence_id(e["subject_type"], e["subject_key"], e["relation_type"], e["object_key"],
                                  e["authority_type"] + ":" + e["evidence_basis"], e["source_url"], e["source_claim"])
        if expected_id != e["evidence_id"]:
            errors.append(f"EVIDENCE_INTEGRITY: evidence ID/provenance tuple mismatch for {e['evidence_id']}")
        if e["evidence_basis"] == "ROOT_POLICY_NORMALIZATION" and root_map.get(e["subject_key"].lower()) != e["object_key"]:
            errors.append(f"EVIDENCE_INTEGRITY: root normalization is not an exact policy pair for {e['subject_key']}")
        if e["relation_type"] == "VARIANT_OF" and e["evidence_basis"] == "REVIEWED_VARIANT_AUTHORITY" and e.get("object_key") not in character_keys:
            errors.append(f"INHERITANCE_INTEGRITY: reviewed VARIANT_OF base is missing for {e['subject_key']}")
        if e["relation_type"] == "VARIANT_OF" and e["evidence_basis"] == "SAFE_STRUCTURAL_VARIANT":
            valid_options = safe_structural_variant_bases(e["subject_key"], character_keys, family_homes, policy, copyright_aliases)
            base_row = master_by_tag.get(e.get("object_key", ""), {})
            matching = [x for x in valid_options if x[0] == e.get("object_key")]
            expected_roots = (family_homes.get(matching[0][2].lower(), set()) | copyright_aliases.get(matching[0][2].lower(), set())) if matching else set()
            if (not matching or e.get("object_key") not in character_keys or e.get("source_url")
                    or base_row.get("final_state") != "HOME_CONFIRMED" or {base_row.get("home_copyright", "")} != expected_roots):
                errors.append(f"INHERITANCE_INTEGRITY: unsafe structural VARIANT_OF for {e['subject_key']}")
        if e["evidence_basis"] == "SAFE_STRUCTURAL_VARIANT" and e["relation_type"] != "VARIANT_OF":
            errors.append(f"INHERITANCE_INTEGRITY: structural variant basis used for non-variant relation {e['subject_key']}")
        if e["relation_type"] == "MEMBER_OF":
            if e["evidence_basis"] != "APPROVED_REPO_EVIDENCE":
                errors.append(f"INHERITANCE_INTEGRITY: MEMBER_OF lacks validated catalog/repository basis for {e['subject_key']}")
            upstream = re.search(r"membership derived from (ev3-[0-9a-f]+)", e.get("source_provenance", ""))
            parent = ledger_by_id.get(upstream.group(1), {}) if upstream else {}
            if (e.get("subject_key") not in character_keys or parent.get("relation_type") != "FAMILY_HOME"
                    or parent.get("subject_key") != e.get("object_key") or parent.get("review_state") != "VALIDATED"
                    or not safe_terminal_family_membership(e["subject_key"], e["object_key"], family_homes, policy, copyright_aliases)):
                errors.append(f"INHERITANCE_INTEGRITY: unsafe/untraceable exact-family membership for {e['subject_key']}")
    structure = read_csv(OUT / "structure_graph_v3.csv")
    if any(e.get("relation_type") == "DISCOVERY_HINT" and (e.get("review_state") != "CANDIDATE" or e.get("evidence_id")) for e in structure):
        errors.append("EVIDENCE_INTEGRITY: discovery hints must remain candidate-only without evidence IDs")
    for r in master:
        if r["final_state"] != "HOME_CONFIRMED": continue
        try: paths = json.loads(r["resolver_path"])
        except json.JSONDecodeError: paths = []
        valid = False
        path_homes = set()
        for p in paths:
            edges = p.get("path_edges", [])
            if not edges or any(ledger_by_id.get(edge.get("evidence_id", ""), {}).get("review_state") != "VALIDATED" for edge in edges): continue
            cursor = r["canonical_tag"]
            terminal = False
            chain_ok = True
            for edge in edges:
                ev = ledger_by_id.get(edge.get("evidence_id", ""), {})
                if (edge.get("subject_key") != cursor or ev.get("relation_type") != edge.get("relation_type")
                        or ev.get("subject_key") != edge.get("subject_key") or ev.get("object_key") != edge.get("object_key")):
                    chain_ok = False
                    break
                relation = edge.get("relation_type")
                if relation in {"VARIANT_OF", "MEMBER_OF"}:
                    cursor = edge["object_key"]
                elif relation in {"DIRECT_HOME", "FAMILY_HOME"}:
                    terminal = edge["object_key"] == r["home_copyright"]
                    cursor = ""
                else:
                    chain_ok = False
                    break
            valid |= chain_ok and terminal
            path_homes.add(p.get("home"))
        if not valid: errors.append(f"EVIDENCE_INTEGRITY/PROVENANCE_INTEGRITY: {r['canonical_tag']} has no validated derivation path")
        if path_homes - {r["home_copyright"]}: errors.append(f"CONFLICT_INTEGRITY: confirmed {r['canonical_tag']} silently omitted a competing HOME path")
    for e in ledger:
        if e["relation_type"] in {"DIRECT_HOME", "FAMILY_HOME"} and e["object_key"] not in roots:
            errors.append(f"ROOT_INTEGRITY: evidence {e['evidence_id']} names nonexistent root")
    unresolved = [r for r in master if r["final_state"] == "HOME_UNRESOLVED"]
    unit_tags = [tag for u in units for tag in json.loads(u["member_ids/tags"])]
    if len(unit_tags) != len(set(unit_tags)) or set(unit_tags) != {r["canonical_tag"] for r in unresolved}:
        errors.append("COVERAGE_INTEGRITY: residual units do not cover exactly all unresolved Characters")
    allowed_unit_states = {"OPEN", "RESOLVED", "PARTIALLY_RESOLVED", "NO_SAFE_EVIDENCE", "POLICY_BLOCKED", "IDENTITY_BLOCKED", "SUPERSEDED_BY_NEW_UNIT"}
    if any(u.get("status") not in allowed_unit_states for u in units):
        errors.append("RESEARCH_UNIT_INTEGRITY: unknown or nonterminalized unit status value")
    summary = json.loads((OUT / "resolver_summary_v3.json").read_text(encoding="utf-8"))
    migration = read_csv(OUT / "migration_comparison_v3.csv")
    state_counts = Counter(r["final_state"] for r in master)
    for state in FINAL_STATES: state_counts.setdefault(state, 0)
    result = {"gate": "PASS" if not errors else "FAIL", "errors": errors,
              "character_population": len(master), "copyright_roots": len(roots),
              "states": dict(sorted(state_counts.items())),
              "reason_counts": dict(Counter(r["reason_code"] for r in master if r["reason_code"])),
              "multi_home_conflicts": summary["multi_home_conflicts"],
              "missing_roots": summary["copyright_roots_missing"],
              "evidence_rows": len(ledger), "research_units": len(units),
              "research_unit_status_counts": dict(Counter(u["status"] for u in units)),
              "open_research_units": sum(u["status"] == "OPEN" for u in units),
              "migration_counts": dict(Counter(r["migration_state"] for r in migration)),
              "validated_evidence_path_coverage": True if not errors else False}
    write_json(OUT / "validation_summary_v3.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors: raise SystemExit(1)

if __name__ == "__main__":
    main()
