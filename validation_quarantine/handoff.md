# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Completed Special-level first pass: 240
- Effective counts: PASS 210 / FIX 18 / REVIEW 4 / IMAGE_TEST_REQUIRED 8
- Batch 1 R2 acceptance gate: PASS
- Batch 2 (101-200) acceptance gate: PASS
- Batch 3 checkpoints: 201-220 and 221-240 complete
- Revalidation queue pending: 0
- Semantic-support frozen target: 58 rows; covered: 24
- Next first-pass Special sequence: 241
- Current external batch: 3 (201-300)
- Production modified: NO

## Batch 3 findings so far
201-240 delta: PASS 36 / FIX 4 / REVIEW 0 / IMAGE_TEST_REQUIRED 0.

### New FIX candidates
- ID209 `urethral beads`: `ImplementRequirementOverride=true`.
- ID211 `urethral insertion`: `ImplementRequirementOverride=true`.
- ID233 `love train`: `PoseRequirementOverride=true`; the repeated formation is intrinsic, but this does not auto-insert a generic pose tag.
- ID240 `reverse spitroast`: `PoseRequirementOverride=true`; specific multi-actor positional structure is intrinsic.

No semantic-support sidecar input rows map to Specials 201-240, so global semantic coverage remains 24/58.

## Active rules
- Blank/None is not automatically an error.
- Requirement metadata is structural; it does not itself auto-inject support tags.
- Alias/Semantic model-response equivalence remains Stage10 HOLD unless controlled evidence exists.
- Geometry/kinematic need is distinct from support-tag auto-addition.
- S/A findings receive deep review and Stage10 knowledge cross-check.
- main/production is read-only.

## Exact restart
Resume first-pass at sequence 241 under R2. Continue 20-row append-only checkpoints. At sequence 300 run Batch3 consistency and deterministic false-PASS sampling before accepting the batch.
