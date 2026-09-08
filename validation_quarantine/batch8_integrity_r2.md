# Batch 8 R2 integrity audit

Issue: #32
Range: Special 701-800
Rule: R2

## Ledger reconciliation
- Expected sequences: 701-800 inclusive = 100
- Result blocks: 0701_0720 / 0721_0740 / 0741_0760 / 0761_0780 / 0781_0800
- Rows: 20 + 20 + 20 + 20 + 20 = 100
- Gaps: 0
- Duplicates: 0
- Sequence/order mismatch: 0
- Companion candidate-fix checkpoint blocks: 5 / 5
- Companion revalidation-queue checkpoint blocks: 5 / 5
- New revalidation queue items: 0

## Effective Batch 8 distribution
- PASS: 58
- FIX: 28
- REVIEW: 14
- IMAGE_TEST_REQUIRED: 0
- Total: 100

## Cross-consistency checks
- Explicit bodypart target corrections follow the Batch7 narrowed precedent; contact alone does not create spatial assignment.
- Existing DIRECT_COMPOSITE spatial=true is retained rather than duplicated.
- `another's` / explicit participant-role rows receive actor structure only where ownership/role is intrinsic.
- Self-action corrections use the established SELF_ACTION / SELF_ACTOR_ROLE sibling pattern.
- PROVISIONAL rows without exact independent evidence remain REVIEW; blanks are not auto-errors.
- Animal-species penis correction follows approved horse/dog body-attribute siblings and is static only.
- Statistical common/rare evidence was not used as semantic-support evidence.
- No Stage10 unresolved generation claim was promoted to production truth.
- Semantic-support frozen coverage remains 53/58; no support source row belongs to this Batch8 range.

## Deterministic PASS sampling
`pass_sampling_batch8_r2.csv` re-audits 12 / 58 PASS rows (20.69%). All surviving A-risk PASS rows identified for this batch are included before spread controls.

Result:
- sampled PASS: 12
- false-PASS: 0
- expanded sample required: NO
- full-batch revalidation required: NO

## Acceptance
Batch 8 R2 acceptance gate: **PASS**

Sequence 801 may resume after progress/handoff are synchronized. Production/main remains unchanged.
