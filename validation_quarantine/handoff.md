# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 2340
- Cumulative: PASS 1883 / FIX 174 / REVIEW 266 / IMAGE_TEST_REQUIRED 17
- Batch 1-23 R2 acceptance gates: PASS
- Batch 24: partial; 2301-2340 durably checkpointed
- Active revalidation pending pointer: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 2341
- Production/main modified: NO

## Batch 24 partial summary
Range 2301-2340: PASS 37 / FIX 0 / REVIEW 3 / IMAGE_TEST_REQUIRED 0.

Durable result blocks:
- `results_blocks/2301_2320.csv`
- `results_blocks/2321_2340.csv`

A-risk REVIEW remains 2301 `collar grab`, 2308 `grabbing another's skirt`, and 2309 `necktie grab` because independent Danbooru semantics indicate another-person ownership while ActorRequirementOverride is blank; no guessed spatial/actor-separation fix was promoted. A-risk IDs2332-2336 (smelling family) were deep-reviewed PASS as explicit structured actions with existing ActorRequirementOverride=true and no unsupported target/spatial support insertion.

Alias IDs2327-2328 preserve exact Special prompt identity with canonical linkage statistics-only. Context/semantic support remains support-only and is not treated as direct model recognition. Blank/None fields were not auto-errors. `candidate_fixes.csv` and `revalidation_queue.csv` were inspected at each 20-row checkpoint with no delta. No Stage10 HOLD knowledge was promoted to production truth.

## Exact restart
Resume first-pass at sequence 2341 (Batch 24). Checkpoint every 20. Do not modify production/main.
