# Issue #180 — Evidence-driven HOME Resolver v3

Status: research/build-time implementation. This pipeline does not write the accepted Issue #70 source or production data.

Target invariant: `Character -> HOME_COPYRIGHT (0..1)`.

## Active pipeline

The six entry scripts are `build_structure_v3.py`, `migrate_evidence_v3.py`, `resolve_character_home_v3.py`, `build_residual_units_v3.py`, `validate_character_home_v3.py`, and `run_issue180_v3.py`. They use the standard-library support module `_issue180_v3_common.py`. No v1/v2 research script is executed or imported.

1. **Source** — accepted Issue #70 translation-result catalog (Character/Copyright categories), Issue #179 origin handoff, Issue #180 approved evidence/decisions, and the tracked v3 migration seed. The tracked v2 baseline is comparison/provenance only. The clean v3 pipeline does not read ignored v1/v2 artifacts or generated queues.
2. **Structure Builder** — emits identity/root candidates and candidate-only `MEMBER_OF` / `VARIANT_OF` edges. Parsed tag shapes are never promoted by themselves.
3. **Evidence Ledger** — represents `EXTERNAL_AUTHORITY`, `APPROVED_REPO_EVIDENCE`, `REVIEWED_QUALIFIER_COPYRIGHT`, `ROOT_POLICY_NORMALIZATION`, `REVIEWED_VARIANT_AUTHORITY`, and the constrained Tier-B `SAFE_STRUCTURAL_VARIANT` basis with deterministic evidence IDs and provenance. A safe exact terminal Copyright-family qualifier can establish membership even when inner qualifiers are present, provided no prior qualifier signals a different reviewed HOME or blocked broad/company/platform/event/crossover class. Structural variants require one exact outer Copyright root, one unique existing base with a matching validated HOME, and no known collision/crossover signal. They assert HOME inheritance only, not costume/event officiality. Decision CSVs alone are never evidence.
4. **Resolver** — considers DIRECT_HOME, FAMILY_HOME + validated MEMBER_OF, and VARIANT_OF + base HOME. A variant decision emits only `VARIANT_OF`; structurally validated variants use the same inheritance path. HOME conflicts yield `HOME_UNRESOLVED / EVIDENCE_CONFLICT`; route preference never suppresses a competing root. Unknown/broad/attribute/non-home families remain blocked by the Issue #180 policy.
5. **Residual Planner** — gives every unresolved Character a reason and groups it into deterministic research units.
6. **Validator** — checks population, exact coverage, state cardinality, source roots, evidence-path edges, conflicts, residual coverage and rerun determinism.

## Run

From repository root:

```powershell
python scripts/issue180/run_issue180_v3.py
```

Generated CSV/JSON artifacts are written under ignored `artifacts/issue180-v3/`. `docs/issue180/v3/reports/MIGRATION_GATE_SUMMARY_V3.json` records the migration stop gate when the run completes. This is build-time research data; none of the ledger, graph or research-unit artifacts are loaded by the WPF runtime.

## Migration reconciliation

`v2_confirmed_baseline_v3.csv` and `MIGRATION_PROVENANCE_V3.json` are comparison/lineage records, not HOME authority. The pre-repair mismatch population is preserved in `MIGRATION_GAP_BEFORE_REPAIR_V3.csv`; the active resolver emits row-level `reports/MIGRATION_GAP_RECONCILIATION_V3.csv` including the original rejection, primary migration-loss reason and repaired evidence path. Current migration comparison remains `SAME_HOME`, `V3_UNRESOLVED`, or `DIFFERENT_HOME`.

`V3_EXECUTION_BASE.json` fingerprints the active scripts/helper, catalog, #179 handoff, migrated seed and baseline. The unit-test/pipeline CI runs only this v3 flow; the old 95-step pipeline remains historical and is not a required gate. The migration gate is followed by the residual research-unit workflow; migration success does not mean residual research is complete.

`research_unit_terminal_reviews_v3.csv` records source-backed terminal outcomes for reviewed units. Each review is bound to the deterministic unit ID and SHA-256 of its exact member set; stale reviews fail closed. Units without a matching reviewed record remain `OPEN`. The current #179-UNKNOWN identity rows are terminalized as `IDENTITY_BLOCKED`, not excluded or assigned a HOME.

## Legacy migration manifest

See [MIGRATION_MANIFEST_V3.csv](MIGRATION_MANIFEST_V3.csv). v1/v2 code and evidence are retained; the classifications describe preservation and migration treatment, not deletion or blanket acceptance.
