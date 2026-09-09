# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- First pass checkpointed through: 1820
- Cumulative: PASS 1369 / FIX 174 / REVIEW 260 / IMAGE_TEST_REQUIRED 17
- Batch 1-18 R2 acceptance gates: PASS
- Batch 19: partial (1801-1820 checkpointed)
- Revalidation pending: 0
- Semantic support: 55 / 58; IMAGE_TEST_REQUIRED rows 30
- Next first-pass sequence: 1821
- Production/main modified: NO

## Batch 19 partial
1801-1820: PASS 20 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0. The 20-row append-only block is durable and indexed.

Semantic/search-only rows remain search/support-only and do not assert direct model recognition. Static BODY_STATE / CONTEXT_MODIFIER and RESTRAINT_IMPLEMENT rows are accepted as structural/reference metadata only; blank requirement fields remain unasserted rather than automatically erroneous. Candidate fixes and revalidation queue were checked and remain unchanged.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 1821. Checkpoint every20. Do not modify production/main.