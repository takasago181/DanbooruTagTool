# Candidate FIX cross-consistency — R2 post-first-pass

Issue: #32
Branch: `dict-validation/quarantine`
Date: 2026-09-10
Scope: quarantine only; production `data/**` unchanged

## Result

**PASS_WITH_STATUS_FILTER**

The Special-level audit contains 174 FIX verdicts. The FIX total is a Special-level verdict count, not a count of physical candidate-fix CSV rows: one Special may carry multiple field corrections, and historical candidate ledgers also retain withdrawn proposals for traceability.

No blocking contradiction was found in the active FIX rule families when the effective candidate set is interpreted with status filtering.

## Count / ledger reconciliation

The cumulative FIX count reached 174 by Batch 13 and did not increase after that point.

Evidence chain:
- through Batch 6: effective cumulative FIX = 34
- Batch 7: +24 -> 58
- Batch 8: +28 -> 86
- Batch 9: +27 -> 113
- Batch 10: +23 -> 136
- Batch 11: +18 -> 154
- Batch 12: +19 -> 173
- Batch 13: +1 -> 174
- Batch 14-28: no additional FIX verdicts

The early consolidated `candidate_fixes.csv` is layered with later append-only `candidate_fix_blocks/`. Historical rows with status such as `WITHDRAWN_AFTER_SIBLING_CHECK` remain evidence only and MUST NOT be promoted as active corrections.

## Cross-consistency rules checked

### Actor / ownership
- Actor structure is added only when distinct actor/ownership/role is intrinsic to the Special identity.
- `another's` / explicit participant-role cases follow this rule.
- Self-directed actions use the established `SELF_ACTION` / `SELF_ACTOR_ROLE` sibling convention where schema evidence supports it.
- Ambiguous insertion/self-action cases without sufficient schema authority remain REVIEW rather than guessed FIX.

### Target / body-site
- Bodypart requirements are corrected only when the target body site is explicit/intrinsic.
- A bodypart mention or contact alone does not create an independent spatial assignment.

### Spatial / relation
- `SpatialAssignmentOverride=true` is limited to intrinsic relation/placement semantics.
- Mere contact is insufficient.
- Existing `DIRECT_COMPOSITE` spatial=true is retained rather than duplicated.
- Relation-bearing Specials remain first-class identities; constituent/general tags do not replace the relation.

### Implement / object
- Implement requirements are corrected only for explicitly defining objects/devices.
- Generic parent/support tags are not treated as generation-equivalent to the exact Special.

### Pose / camera / family
- Static metadata corrections are separated from generation-effect claims.
- Camera/pose/visibility support that depends on model behavior is not promoted from a static candidate.
- PROVISIONAL / REVIEW_REQUIRED rows without exact independent evidence remain REVIEW.

## Knowledge evidence boundary

Issue #44 / current KNOWLEDGE material was consulted read-only. The following remain model/version scoped and were NOT used to self-certify FIX candidates:
- broad + specific generation effect
- actor/target/body-site/topology reliability
- device/relation binding ceilings
- canonical/Alias generation response
- NoobAI / Illustrious / WAI17 / Anima prompt behavior
- minimum-sufficient Prompt / anti-support behavior

Static semantic/structural correctness and generation reliability remain separate claims.

## Promotion normalization requirements

A final promotion implementation MUST:
1. select only effective active quarantined candidate rows;
2. exclude withdrawn/superseded historical proposals;
3. preserve provenance to the originating Special verdict/evidence;
4. not infer prompt-support/default-on behavior from structural FIX fields;
5. not flatten model-family scoped generation knowledge into production-global truth;
6. apply all approved field changes for a Special atomically where one FIX contains multiple fields.

## Verdict

Candidate FIX cross-consistency gate: **PASS_WITH_STATUS_FILTER**.

This gate does not authorize production writes. It only establishes that the 174 Special-level FIX verdicts can proceed to an independent final promotion audit once the remaining #32 gates are satisfied.
