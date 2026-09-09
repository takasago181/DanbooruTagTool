# Batch 18 R2 Integrity / Acceptance Audit

Range: sequences 1701-1800
Rule: R2

## Ledger reconciliation
- Authoritative result blocks: `1701_1720.csv`, `1721_1740.csv`, `1741_1760.csv`, `1761_1780.csv`, `1781_1800.csv`
- Expected rows: 100
- Observed rows: 100
- Contiguous sequence coverage: PASS (1701-1800)
- Duplicate sequence IDs: 0
- Missing sequence IDs: 0
- Batch delta: PASS 99 / FIX 0 / REVIEW 1 / IMAGE_TEST_REQUIRED 0

## High-risk deep review
- ID1739 `defloration`: A-risk ActorRequirementOverride=true retained as intrinsic structural metadata only.
- IDs1745-1756: A-risk POSE_COMPOSITION / PoseRequirementOverride=true retained as intrinsic pose structure. Stage10 pose/geometry/visibility guidance was used only as evidence-boundary cross-check; no experimental behavior was promoted to production truth.
- ID1787 `vaginal prolapse`: S-risk REVIEW. Cross-row inconsistency with ID1759 `prolapse` (BODY_ATTRIBUTE/body_target_or_attribute vs BODY_STATE/body_state). No independent frozen evidence was sufficient to select a concrete correction safely.

## PASS false-PASS audit
- PASS population: 99
- Deterministic re-audit sample: 20 (R2 maximum; includes all 13 A-risk PASS rows)
- Sample ledger: `pass_sampling_batch18_r2.csv`
- New false-PASS: 0
- Escalation triggered: NO

## Side ledgers / boundaries
- `candidate_fixes.csv`: checked; no Batch18 addition (ID1787 remains REVIEW, not guessed into a FIX).
- `revalidation_queue.csv`: checked; no new retroactive queue item required.
- semantic support coverage remains 55/58; no Batch18 Special row was used to conflate semantic support with common/rare statistics.
- Blank requirement fields were treated as UNKNOWN / NOT ASSERTED, not automatic errors.
- Stage10 HOLD/experimental knowledge was not promoted to production truth.
- production/main modified: NO.

## Acceptance
Batch18 R2 acceptance gate: **PASS**.
Next safe first-pass sequence: **1801**.
