# Dictionary Validation Handoff

Issue: #32
Branch: `dict-validation/quarantine`
Status: IN_PROGRESS
Rule version: R2

## Current position
- Target: 2,788 Specials
- Special-level first pass accepted through: 800
- Cumulative effective verdicts: PASS 677 / FIX 86 / REVIEW 21 / IMAGE_TEST_REQUIRED 16
- Batch 1-8 R2 acceptance gates: PASS
- Revalidation pending: 0
- Semantic-support frozen target: 58 rows; durable audited coverage: 53
- Next first-pass sequence: 801
- Production modified: NO

## Batch 8 acceptance
Range 701-800 is durably stored in five 20-row result blocks with matching candidate-fix and revalidation-queue checkpoint blocks.

Final Batch8 distribution:
- PASS 58
- FIX 28
- REVIEW 14
- IMAGE_TEST_REQUIRED 0

`pass_sampling_batch8_r2.csv` rechecked 12 / 58 PASS rows (20.69%) with A-risk preference and found 0 new false-PASS. `batch8_integrity_r2.md` records 100/100 reconciliation, no gaps/duplicates, and Batch8 R2 acceptance gate PASS.

Notable quarantine-only findings:
- explicit bodypart/implement/actor/self/spatial omissions were corrected narrowly under established sibling rules;
- ID738 `animal penis` -> static BODY_ATTRIBUTE/body_attribute/DIRECT correction aligned with approved horse/dog siblings;
- ID779 `tweaking own nipple` -> SELF_ACTION/action/STRUCTURED + actor/bodypart + SELF_ACTOR_ROLE candidate;
- PROVISIONAL or exact-meaning gaps (including 706/710/756/763/765/766/769/776/780/785/788/792/794/795) remain REVIEW rather than guessed promotion.

Semantic-support coverage remains 53/58; remaining frozen rows belong to later Special IDs 1159, 1823, and 1839.

## Critical interpretation rules
- Blank/None is not automatically missing data; UNKNOWN/not asserted remains valid.
- Requirement overrides are structural metadata, not support-insertion commands.
- Statistical common/rare/co-occurrence remains separate from semantic support.
- Stage10 HOLD evidence is not production truth.
- Direct structural profiles and semantic/search-only rows must not be conflated.
- Special2788 exact identity remains first-class.

## Exact restart
Resume first-pass at sequence 801. Process at most 100 Specials, checkpoint every 20, and run Batch9 integrity + deterministic PASS resampling before acceptance. Do not modify production/main.
