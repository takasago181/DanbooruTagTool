# Batch 21 R2 integrity / false-PASS audit

Range: 2001-2100
Rule: R2

## Reconciliation
- Expected rows: 100
- Durable result blocks: 5 x 20
- Missing sequences: 0
- Duplicate sequences: 0
- PASS: 98
- FIX: 0
- REVIEW: 2
- IMAGE_TEST_REQUIRED: 0
- Non-PASS rows: 2029 `grabbing another's breast`, 2031 `guided breast grab`

## High-risk deep review
- 2003 `cross-section`: A-risk PASS; camera/internal-view metadata remains structural only.
- 2004 `x-ray`: A-risk PASS; camera/internal-view metadata remains structural only.
- 2005 `anal cross-section`: A-risk PASS; camera/internal-view metadata remains structural only.
- 2028 `cooperative breast smother`: A-risk PASS; explicit actor/spatial/separation structure is internally consistent.
- 2029 `grabbing another's breast`: A-risk REVIEW; actor requirement is plausibly missing, but exact independent evidence was not attached, so no guessed FIX.
- 2031 `guided breast grab`: A-risk REVIEW; analogous guided-grab precedent suggests actor requirement, but exact independent evidence was not attached.

## Deterministic PASS false-PASS sample
20 / 98 PASS rows sampled, preferentially including all A-risk PASS rows in the batch.

Sample: 2003, 2004, 2005, 2028, 2001, 2006, 2011, 2016, 2021, 2026, 2035, 2040, 2045, 2050, 2055, 2060, 2065, 2070, 2080, 2090.

Result: 0 new false-PASS.

The sample includes camera/internal-view, semantic/search-only, alias/body-attribute, interaction, and clothing-exposure families. Semantic support/search rows were not treated as model-recognition truth. Statistical canonical/alias linkage was not promoted to semantic generation equivalence. Blank requirement fields were not auto-errors.

## Gate
Batch 21 R2 acceptance gate: PASS.

No production/main changes. Stage10 knowledge was used only as scoped evidence where required and was not promoted to production truth.
