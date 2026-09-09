# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 1340
- Cumulative: PASS 890 / FIX 174 / REVIEW 259 / IMAGE_TEST_REQUIRED 17
- Batch 1-13 R2 acceptance gates: PASS
- Batch 14: 1301-1340 checkpoint durable; batch gate not yet run
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 1341
- Production/main modified: NO

## Batch 14 partial
1301-1340: PASS 40 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0. All frozen rows in this range are APPROVED_IDENTITY_ONLY / ALIAS_TARGET_RESOLVED / ALIAS_PRESERVE. Exact Special prompt identity is preserved; canonical_target remains statistics-only. No enabled semantic-support row is attached to these Specials.

Before restarting Batch14, RESULT_LEDGER_INDEX.csv was found stale at sequence940 while durable append-only blocks existed through1300. The durable block directory was reconciled and index restored through1300 before new validation resumed.

candidate_fixes.csv and revalidation_queue.csv were checked; no new finding or queue entry was required through1340.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 1341. Checkpoint every20. Do not modify production/main.
