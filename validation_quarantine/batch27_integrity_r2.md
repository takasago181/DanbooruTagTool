# Batch 27 R2 Integrity / False-PASS Gate

Issue: #32
Range: 2601-2700
Rule: R2

## Static integrity
- Durable result blocks: 5
- Expected rows: 100
- Observed rows: 100
- Sequence coverage: 2601-2700 contiguous
- Missing sequences: 0
- Duplicate sequences: 0
- Verdict totals: PASS 100 / FIX 0 / REVIEW 0 / IMAGE_TEST_REQUIRED 0
- candidate_fixes delta: 0
- revalidation_queue delta: 0
- semantic-support coverage: unchanged 55/58

## R2 boundary review
All 100 production rows are `APPROVED_IDENTITY_ONLY / ALIAS_TARGET_RESOLVED / ALIAS_PRESERVE` with blank structural-generation fields and `PRESERVE_PROMPT_IDENTITY` handling. Blank/None structural fields were treated as NOT ASSERTED, not automatic errors.

The audit did not infer canonical/model response equivalence from alias linkage. Exact alias Prompt identity remains first-class; canonical linkage remains statistics-only. Stage10 `canonical / Alias / Semantic response` remains HOLD. Wording that implies restraint, actor interaction, spatial relation, camera/POV, visibility, unusual anatomy, or implement use was not promoted into unasserted automatic support or structural metadata.

## PASS re-audit
- PASS population: 100
- Required sample: 20% = 20
- Sampled: 20
- Selection: deterministic interval sample across the fixed order, with concept-type spread (restraint, clothing/exposure, interaction, anatomy, spatial/body-location, implement, alternate-language alias)
- Sample ledger: `pass_sampling_batch27_r2.csv`
- New false-PASS: 0
- S/A false-PASS: 0

## Gate verdict
**PASS**

Batch27 may advance to sequence 2701. No production/main data was modified.

## Known storage note
`RESULT_LEDGER_INDEX.csv` is a secondary navigation index and remains behind durable result blocks from a pre-existing lag. This does not invalidate the append-only result blocks. The authoritative restart state is the durable block set plus `progress.json` and `handoff.md`; index reconciliation remains housekeeping and must not be mistaken for missing validation work.
