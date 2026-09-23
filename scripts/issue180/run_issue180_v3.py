#!/usr/bin/env python3
"""Run the small research-only Issue #180 v3 pipeline and reproducibility check."""
from __future__ import annotations
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "artifacts/issue180-v3"
STEPS = ["build_structure_v3.py", "migrate_evidence_v3.py", "resolve_character_home_v3.py", "build_residual_units_v3.py", "validate_character_home_v3.py"]

def run(script: str) -> None:
    subprocess.run([sys.executable, str(HERE / script)], cwd=ROOT, check=True)

def main() -> None:
    for s in STEPS: run(s)
    master = OUT / "character_home_master_v3.csv"
    first = hashlib.sha256(master.read_bytes()).hexdigest()
    run("resolve_character_home_v3.py")
    second = hashlib.sha256(master.read_bytes()).hexdigest()
    summary_path = OUT / "resolver_summary_v3.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    reproducibility = {"first_master_sha256": first, "second_master_sha256": second, "same": first == second}
    (OUT / "reproducibility_v3.json").write_text(json.dumps(reproducibility, indent=2) + "\n", encoding="utf-8")
    if first != second: raise SystemExit("REPRODUCIBILITY: resolver output changed on identical inputs")
    run("validate_character_home_v3.py")
    from _issue180_v3_common import (CATALOG, ORIGIN, V3_BASELINE, V3_SEED,
        V3_MIGRATION_MANIFEST, DOCS_OUT, sha256_file, write_json)
    unit_reviews = ROOT / "docs/issue180/v3/research_unit_terminal_reviews_v3.csv"
    active = ["build_structure_v3.py", "migrate_evidence_v3.py", "resolve_character_home_v3.py",
              "build_residual_units_v3.py", "validate_character_home_v3.py", "run_issue180_v3.py"]
    execution_base = {
        "schema_version": 3,
        "active_pipeline": {name: sha256_file(HERE / name) for name in active},
        "helper_sha256": sha256_file(HERE / "_issue180_v3_common.py"),
        "evidence_schema_version": 2,
        "migrated_evidence_seed_sha256": sha256_file(V3_SEED),
        "catalog_sha256": sha256_file(CATALOG),
        "issue179_handoff_sha256": sha256_file(ORIGIN),
        "issue180_policy_sha256": sha256_file(ROOT / "docs/issue180/autonomous/AUTONOMOUS_POLICY_V2.json"),
        "migration_baseline_sha256": sha256_file(V3_BASELINE),
        "migration_provenance_manifest_sha256": sha256_file(V3_MIGRATION_MANIFEST),
        "research_unit_terminal_reviews_sha256": sha256_file(unit_reviews),
        "resolver_semantics_version": "direct-family-membership-safe-structural-variant-v2",
        "validator_version": sha256_file(HERE / "validate_character_home_v3.py"),
        "runtime_research_dependency": False,
        "legacy_v1_v2_pipeline_dependency": False,
    }
    write_json(ROOT / "docs/issue180/v3/V3_EXECUTION_BASE.json", execution_base)
    source = json.loads((OUT / "source_manifest_v3.json").read_text(encoding="utf-8"))
    evidence = json.loads((OUT / "evidence_ledger_summary_v3.json").read_text(encoding="utf-8"))
    units = json.loads((OUT / "research_units_summary_v3.json").read_text(encoding="utf-8"))
    validation = json.loads((OUT / "validation_summary_v3.json").read_text(encoding="utf-8"))
    resolver = json.loads((OUT / "resolver_summary_v3.json").read_text(encoding="utf-8"))
    mig = resolver["migration_counts"]
    migration_exact = (mig.get("SAME_HOME", 0) == resolver["v2_confirmed"]
                       and mig.get("V3_UNRESOLVED", 0) == 0 and mig.get("DIFFERENT_HOME", 0) == 0)
    report = {"schema_version": 3, "source_manifest_sha256": hashlib.sha256((OUT / "source_manifest_v3.json").read_bytes()).hexdigest(),
              "pipeline_validation": validation["gate"], "reproducibility": reproducibility,
              "migration_gate": "PASS_EXACT" if migration_exact else "STOP_CLASSIFIED_DIFFERENCES",
              "character_population": validation["character_population"], "states": validation["states"],
              "residual_reason_counts": validation["reason_counts"], "research_unit_count": units["research_unit_count"],
              "research_unit_type_counts": units["unit_type_counts"], "evidence_rows": evidence["ledger_rows"],
              "research_unit_status_counts": units["unit_status_counts"], "open_research_units": units["open_unit_count"],
              "evidence_basis_counts": evidence["evidence_basis_counts"],
              "external_source_url_count": evidence["external_source_url_count"],
              "migration_counts": resolver["migration_counts"], "migration_difference_classes": resolver["difference_classes"],
              "migration_comparison_path": "docs/issue180/v3/reports/MIGRATION_COMPARISON_V3.csv",
              "multi_home_conflicts": validation["multi_home_conflicts"], "missing_roots": validation["missing_roots"],
              "active_pipeline_scripts": STEPS + ["run_issue180_v3.py"], "active_pipeline_script_count": 6,
              "legacy_v1_v2_scripts_executed": False, "production_runtime_dependency": False,
              "generated_output_directory": "artifacts/issue180-v3"}
    from _issue180_v3_common import DOCS_OUT, write_json
    write_json(DOCS_OUT / "MIGRATION_GATE_SUMMARY_V3.json", report)
    DOCS_OUT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(OUT / "migration_comparison_v3.csv", DOCS_OUT / "MIGRATION_COMPARISON_V3.csv")
    print(json.dumps({"pipeline": validation["gate"], "reproducibility": reproducibility, "report": str(DOCS_OUT / "MIGRATION_GATE_SUMMARY_V3.json"), "outputs": str(OUT)}, indent=2))

if __name__ == "__main__":
    main()
