# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: READY_TO_START
Rule version: R1

## Current position
- Target: 2,788 Specials
- Completed: 0
- Last completed Special: none
- Last completed batch: 0
- Next batch: 1
- Next sequence position: 1
- Revalidation pending: 0
- Production modified: NO

## Fixed audit input
See `AUDIT_INPUT_SNAPSHOT.md`.
The first pass uses the frozen production revision captured at setup. Do not silently switch to a later main revision.

## Active method
- 100 Specials per external batch
- 20 x 5 internal blocks
- static integrity pass + fast semantic screening
- mandatory deep review for S/A risk and all non-PASS findings
- mandatory deep review for `CORE_SUPPORT + ADDITIVE`
- PASS sampling every 100 to detect false-PASS drift
- rule changes are versioned and create revalidation work

## Critical interpretation rules
- Blank/None is not automatically missing data.
- UNKNOWN / NOT ASSERTED may be the correct state.
- Generation requirements are structural metadata, not automatic support insertion commands.
- common/rare/co-occurrence statistics are separate from semantic support.
- Stage10 HOLD knowledge is not production truth.
- model-family-specific knowledge must remain scoped.
- Special2788 identity remains first-class and is never replaced by support.

## Durable files
- `README.md`
- `VALIDATION_RULES.md`
- `AUDIT_INPUT_SNAPSHOT.md`
- `progress.json`
- `results.csv`
- `candidate_fixes.csv`
- `revalidation_queue.csv`
- this `handoff.md`

## Exact restart
Read Issue #32 and all files above. Confirm active rule version is R1 and `progress.json` still shows sequence position 1 unless another chat has advanced it. Then begin Batch 1 from the frozen Generation Profile row order.

## Chat migration rule
Before leaving any future validation chat, update at minimum:
1. `progress.json`
2. `handoff.md`
3. `results.csv`
4. `candidate_fixes.csv` if FIX exists
5. `revalidation_queue.csv` if rule/evidence changes require revisit

Never rely on conversational memory alone for restart.
