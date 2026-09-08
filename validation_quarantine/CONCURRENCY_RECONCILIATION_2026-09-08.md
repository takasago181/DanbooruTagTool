# Dictionary Validation Concurrency Reconciliation — 2026-09-08

Issue: #32
Branch: `dict-validation/quarantine`

## What happened
The scheduled continuation task and the active chat overlapped after Special sequence 40.

The scheduled task strengthened the audit from R1 to R2 and updated rule/progress/handoff state while the active chat was independently validating sequences 41-60 under the R1 rules it had already loaded.

A subsequent `progress.json` write correctly failed with HTTP 409 because the scheduled task had changed that file. No stale overwrite was forced.

## Reconciliation decision
- Preserve Special-level results 1-60 exactly as historical R1 evaluations.
- Do not relabel 41-60 as R2 after the fact.
- R2 remains the active rule.
- Direct R2 first-pass processing starts at sequence 61.
- Sequences 1-60 are queued for R2-only backfill obligations: generation-evidence cross-check where required and row-complete semantic-support coverage where applicable.
- Candidate fixes created during 41-60 remain quarantined R1 candidates and must survive R2 backfill before any promotion consideration.
- Production/main remains unchanged.

## Semantic support frozen count
The frozen `semantic_support_profiles.csv` has 59 physical lines: one header plus 58 data rows. R2 semantic-support completion target is therefore exactly 58 rows.

## Automation safety
During an active manual validation run, the hourly scheduled task must be disabled before writes begin. Re-enable it only after the current checkpoint is fully persisted. Each future run must read the latest GitHub checkpoint before work and must not force-update stale files.

This is an execution-history reconciliation, not a semantic rule change; no R3 is created.
