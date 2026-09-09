# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 2020
- Cumulative: PASS 1568 / FIX 174 / REVIEW 261 / IMAGE_TEST_REQUIRED 17
- Batch 1-20 R2 acceptance gates: PASS
- Batch 21: partial checkpoint through 2020; 100-Special gate not yet run
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 2021
- Production/main modified: NO

## Batch 21 partial checkpoint
2001-2020: PASS 20 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0. Result block `results_blocks/2001_2020.csv` is durable.

IDs 2003 `cross-section`, 2004 `x-ray`, and 2005 `anal cross-section` were treated as A-risk because the profiles assert camera/internal-view structure. Deep review accepted the structural classification and camera requirement while preserving the Stage10 boundary: camera/visibility support is not automatically inserted, exact family camera tuning remains HOLD, and Stage10 knowledge is scoped evidence rather than production truth.

Semantic-role rows remain search/support-only; alias rows preserve exact Special identity with canonical linkage statistics-only. `candidate_fixes.csv` and `revalidation_queue.csv` were checked and require no new entries at this checkpoint. Semantic support remains 55/58.

Before this block, `RESULT_LEDGER_INDEX.csv` was found to stop at 1920 while durable result blocks/progress existed through 2000. The index was reconciled through 2000 from the existing immutable blocks before validation resumed.

## Exact restart
Resume first-pass at sequence 2021. Checkpoint every 20. Do not modify production/main.
