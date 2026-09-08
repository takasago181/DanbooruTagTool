# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Completed Special-level first pass: 100
- Batch 1 first-pass: COMPLETE
- Batch 1 R2 acceptance gate: FAILED
- Batch 1 R2 revalidation checkpoint: 80 / 100
- Next Batch 1 revalidation position: 81
- Next new Special sequence position: 101 (BLOCKED)
- Revalidation queue remains pending until full Batch 1 gate acceptance: 100 entries
- Effective first-pass counts before gate acceptance: PASS 84 / FIX 9 / REVIEW 3 / IMAGE_TEST_REQUIRED 4
- Semantic-support frozen target: 58 rows; covered: 9
- False-PASS found: 1 (S risk; ID88)
- Production modified: NO

## Fail root cause
ID88 `masturbation` omitted enabled CORE_SUPPORT+ADDITIVE `solo` from its immutable 81-100 verdict. R2 requires deep review of default-on additive support; effective ID88 state is IMAGE_TEST_REQUIRED pending controlled A/B. Sequence101 stays blocked until the complete Batch1 gate passes.

## R2 revalidation checkpoints
### 1-20
No new false-PASS. IDs16/17/19 remain IMAGE_TEST_REQUIRED; ID20 A-priority PASS retained.

### 21-40
No new false-PASS. IDs22/40 remain REVIEW. IDs34/36 retain narrowed ActorRequirementOverride FIX. IDs21/25 remain conservative A-priority PASS.

### 41-60
No new false-PASS. ID55 remains REVIEW; IDs49/50/57/58/59 retain existing A-priority FIX candidates after schema/Stage10 cross-check. Stored in `revalidation_blocks/0041_0060.csv`.

### 61-80
No new false-PASS or FIX.
- ID65 `upright 69`: A-priority static pose/composition structure retained; no auto-support claim.
- IDs66/67 `fuck`/`fucking`: ALIAS_PRESERVE retained as identity policy; canonical/Alias image-response equivalence remains Stage10 HOLD.
- IDs68-80 semantic/search concepts remain conservative and do not claim direct model equivalence.
Stored in `revalidation_blocks/0061_0080.csv`.

## Semantic-support coverage
Frozen rows1-9 are explicitly audited: IDs16/17/19 default-on CORE_SUPPORT+ADDITIVE rows and ID88 `solo` are IMAGE_TEST_REQUIRED; ID88 optional pose alternatives are static PASS as optional choices only.

## Preserved unresolved/candidates
- IMAGE_TEST_REQUIRED: 16,17,19,88
- REVIEW: 22,40,55
- FIX candidates: 34,36,49,50,57,58,59,92,94

## Exact restart
Resume Batch1 R2 revalidation at sequence81. Keep all 100 queue entries pending until complete 1-100 revalidation and final Batch1 gate. Do not process sequence101 yet.

## Durable ledgers
`RESULT_LEDGER_INDEX.csv`, `results_blocks/`, `revalidation_results.csv`, `revalidation_blocks/`, `candidate_fixes.csv`, `revalidation_queue.csv`, `semantic_support_results.csv`, `progress.json`, `handoff.md`.
