# Issue #180 — Evidence-driven HOME Resolver v3

Status: research/build-time implementation. This pipeline does not write the accepted Issue #70 source or production data.

Target invariant: `Character -> HOME_COPYRIGHT (0..1)`.

## Active pipeline

The six entry scripts are `build_structure_v3.py`, `migrate_evidence_v3.py`, `resolve_character_home_v3.py`, `build_residual_units_v3.py`, `validate_character_home_v3.py`, and `run_issue180_v3.py`. They use the standard-library support module `_issue180_v3_common.py`. No v1/v2 research script is executed or imported.

1. **Source** — accepted Issue #70 translation-result catalog (Character/Copyright categories), Issue #179 origin handoff, Issue #180 cited evidence and validated decision shards. The v2 applied ledger is retained only as provenance cross-reference; the v2 master is used only as the migration regression baseline. Generated queues never authorize HOME.
2. **Structure Builder** — emits identity/root candidates and candidate-only `MEMBER_OF` / `VARIANT_OF` edges. Parsed tag shapes are never promoted by themselves.
3. **Evidence Ledger** — converts a PASS decision into a validated relation only when it has a substantive claim, an external URL and an in-scope endpoint. Approved Issue #180 evidence files are also imported. Deterministic IDs hash the normalized source/relation tuple; decision files are provenance pointers, not proof.
4. **Resolver** — considers DIRECT_HOME, FAMILY_HOME + separately materialized membership, and VARIANT_OF + base HOME. Conflicting distinct roots yield `HOME_UNRESOLVED / EVIDENCE_CONFLICT`; route preference never suppresses a competing root.
5. **Residual Planner** — gives every unresolved Character a reason and groups it into deterministic research units.
6. **Validator** — checks population, exact coverage, state cardinality, source roots, evidence-path edges, conflicts, residual coverage and rerun determinism.

## Run

From repository root:

```powershell
python scripts/issue180/run_issue180_v3.py
```

Generated CSV/JSON artifacts are written under ignored `artifacts/issue180-v3/`. `docs/issue180/v3/reports/MIGRATION_GATE_SUMMARY_V3.json` records the migration stop gate when the run completes. This is build-time research data; none of the ledger, graph or research-unit artifacts are loaded by the WPF runtime.

## Migration stop gate

The comparison classifies each previously confirmed v2 Character as `SAME_HOME`, `V3_UNRESOLVED`, or `DIFFERENT_HOME`. A non-exact result is categorized as `EVIDENCE_MIGRATION_ERROR`, `RESOLVER_BEHAVIOR_CHANGE`, `OLD_DECISION_DEFECT`, `SOURCE_DRIFT`, or `OTHER`. No mismatch is silently repaired or overwritten. New residual web research is outside this v3 migration run.

## Legacy migration manifest

See [MIGRATION_MANIFEST_V3.csv](MIGRATION_MANIFEST_V3.csv). v1/v2 code and evidence are retained; the classifications describe preservation and migration treatment, not deletion or blanket acceptance.
