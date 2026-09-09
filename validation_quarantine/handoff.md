# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 2000
- Cumulative: PASS 1548 / FIX 174 / REVIEW 261 / IMAGE_TEST_REQUIRED 17
- Batch 1-20 R2 acceptance gates: PASS
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 2001
- Production/main modified: NO

## Batch 20 complete
1901-2000: PASS 100 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0. Five 20-row result blocks are durable.

A-risk IDs1912 `box tie`, 1914 `frogtie`, 1915 `hogtie`, 1919 `legs bound apart`, 1926 `reverse prayer`, 1932 `shrimp tie`, 1935 `stationary restraints`, 1937 `strappado`, 1938 `suspension`, and1940 `wrists bound apart` were deep-reviewed PASS. Pose/spatial/composition metadata remains structural only; no automatic support insertion was inferred. Stage10 evidence was treated as scoped evidence, not production truth.

Alias rows preserve exact Special identity with canonical linkage statistics-only. Semantic-role rows remain search/support-only and do not assert direct model recognition.

Deterministic R2 PASS re-audit checked20/100 including every A-risk PASS. New false-PASS:0. Batch20 acceptance gate: PASS.

`candidate_fixes.csv` and `revalidation_queue.csv` checked unchanged at checkpoints. Semantic support remains55/58; common/rare statistics were not conflated with semantic support.

## Exact restart
Resume first-pass at sequence 2001. Checkpoint every20. Do not modify production/main.
