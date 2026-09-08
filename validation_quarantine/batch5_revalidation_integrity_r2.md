# Batch 5 R2 Revalidation Integrity Gate

Issue: #32
Scope: Special sequence 401-500
Rule version: R2
Production/main modified: NO

## Checkpoint integrity

The authoritative revalidation ledger consists of five append-only 20-row blocks:

- `revalidation_blocks/0401_0420.csv`
- `revalidation_blocks/0421_0440.csv`
- `revalidation_blocks/0441_0460.csv`
- `revalidation_blocks/0461_0480.csv`
- `revalidation_blocks/0481_0500.csv`

Each block contains its exact contiguous 20-Special interval. Together they cover 401-500 exactly once. Matching append-only queue-resolution overlays exist under `revalidation_queue_blocks/` for the same five intervals, so effective Batch5 revalidation pending count is 0.

## Effective Batch 5 verdict distribution after full revalidation

- PASS: 93
- FIX: 6
- REVIEW: 0
- IMAGE_TEST_REQUIRED: 1
- Total: 100

FIX Specials:
- ID420 `nipple torture` -> `BodypartRequirementOverride=true`
- ID422 `torture instruments` -> `ImplementRequirementOverride=true`
- ID469 `peeing on penis` -> `BodypartRequirementOverride=true` + `SpatialAssignmentOverride=true`
- ID479 `skull fucking` -> `BodypartRequirementOverride=true` + `SpatialAssignmentOverride=true`
- ID490 `bestiality` -> `ActorRequirementOverride=true`
- ID493 `mating (animal)` -> `ActorRequirementOverride=true`

IMAGE_TEST_REQUIRED:
- ID488 `xray sex` -> controlled generation remains required for model-dependent internal/x-ray visibility behavior. No Stage10 HOLD knowledge is promoted to production truth.

All six FIX items have corresponding quarantined candidate rows in `candidate_fixes.csv`. Requirement overrides remain structural metadata only and do not authorize automatic support-tag insertion.

## Semantic/statistical separation

Semantic/search-only rows were not converted into direct structural profiles by phrase decomposition. Statistical common/rare/co-occurrence evidence was not used as semantic-support truth. Frozen semantic-support coverage remains 53/58 and is not inflated by Batch5 completion.

## Post-revalidation PASS sampling

`pass_sampling_batch5_r2_revalidation.csv` rechecks 19 of the 93 effective PASS rows using deterministic spread and includes every surviving A-risk PASS in this batch. New false-PASS found: 0.

## Gate decision

PASS.

Batch5 may be accepted under R2. Sequence501 may be unblocked for the next first-pass batch. Quarantined findings remain candidates only; production/main remains unchanged.
