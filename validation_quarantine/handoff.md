# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 2400
- Cumulative: PASS 1941 / FIX 174 / REVIEW 268 / IMAGE_TEST_REQUIRED 17
- Batch 1-23 R2 acceptance gates: PASS
- Batch 24: 2301-2400 durably checkpointed; R2 100-row gate pending
- Active revalidation pending pointer: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence after gate: 2401
- Production/main modified: NO

## Batch 24 pre-gate summary
Range 2301-2400: PASS 95 / FIX 0 / REVIEW 5 / IMAGE_TEST_REQUIRED 0.

Durable result blocks:
- `results_blocks/2301_2320.csv`
- `results_blocks/2321_2340.csv`
- `results_blocks/2341_2360.csv`
- `results_blocks/2361_2380.csv`
- `results_blocks/2381_2400.csv`

Deep-review non-PASS:
- A-risk REVIEW: 2301 `collar grab`, 2308 `grabbing another's skirt`, 2309 `necktie grab` due independent another-person semantics with blank ActorRequirementOverride; no guessed spatial/actor-separation fix.
- S-risk REVIEW: 2393 `blindfold mask`, 2394 `ribbon bondage`; both are PROVISIONAL/audit-only. Independent evidence confirms identity/usage but does not safely determine the project's exact generation family/role, so blanks are not auto-fixed.

Semantic-role rows remain search/support-only; alias rows preserve exact prompt identity with canonical linkage statistics-only. No Stage10 HOLD knowledge was promoted. `candidate_fixes.csv` and `revalidation_queue.csv` were inspected at every 20-row checkpoint with no delta.

## Exact restart
Do not process 2401 until Batch24 integrity and PASS re-sampling gate is persisted. If interrupted now, first-pass through 2400 is durable but Batch24 acceptance remains pending. Do not modify production/main.
