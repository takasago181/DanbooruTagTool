#!/usr/bin/env python3
"""Validate v3 source, evidence paths, coverage, roots, conflicts and reproducibility artifacts."""
from __future__ import annotations
import json
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
              "migration_counts": dict(Counter(r["migration_state"] for r in migration)),
              "validated_evidence_path_coverage": True if not errors else False}
    write_json(OUT / "validation_summary_v3.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors: raise SystemExit(1)

if __name__ == "__main__":
    main()
