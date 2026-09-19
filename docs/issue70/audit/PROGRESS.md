# Issue #70 Final Semantic Audit Progress

Authority baseline at audit start: `main` `07f6e05c7300831a9c4f52fe3857043594b8413b`.

Audit branch: `audit/issue70-semantic-final`.

Production translation data remains unchanged. The audit lane is proposal-only until the full semantic ledger, pattern expansion, unresolved checks, and final approval are complete.

## Current census authority

The current screening authority is `scripts/issue70/audit_semantic_risk_v3.py` plus `.github/workflows/issue70_semantic_risk_census_v3.yml`.

v3 completed successfully over all 92,739 Issue #70 rows and produced:

- `REVIEW_REQUIRED`: 13,221
- `ACCEPTED_AI` risk hits: 4,149
- clean ACCEPTED_AI stratified sample: 900
- unique initial audit population: 18,270
- Character: 14,928
- Copyright: 2,316
- Artist: 1,026

v1/v2 are superseded screening iterations. v3 specifically removes false conflict signals caused by Latin/official spellings stored in `existing_rejected_ja` and by Chinese-only raw candidate evidence.

## Audited batches

### Copyright high-impact batch 001

File: `docs/issue70/audit/copyright_high_impact_batch001.csv`

- audited: 72
- correction proposals: 55
- KEEP: 17
- external check: 0

### Structural display batch 002

File: `docs/issue70/audit/structural_display_batch002.csv`

- audited: 43
- correction proposals: 17
- KEEP: 2
- external check: 24

### Variant lost-qualifier batch 003

Files:

- `variant_lost_qualifier_batch003_01.csv`
- `variant_lost_qualifier_batch003_02.csv`
- `variant_lost_qualifier_batch003_03.csv`
- `variant_lost_qualifier_batch003_04.csv`

All 83 `VARIANT_DISPLAY_LOST_QUALIFIER` rows were reviewed.

- audited: 83
- correction proposals: 58
- KEEP: 0
- external check: 25

The broader `VARIANT_DISPLAY_MISSING_BASE_IDENTITY` flag is not auto-fixable: many alternate forms legitimately have independent established names. Only the stronger lost-qualifier subset was batch-reviewed here.

### Copyright batch 004

Files:

- `copyright_batch004_01.csv`
- `copyright_batch004_02.csv`
- `copyright_batch004_03.csv`
- `copyright_batch004_04.csv`

- audited: 70
- correction proposals: 45
- KEEP: 22
- external check: 3

This batch specifically caught franchise/series rows whose display had been replaced by abbreviations, derivative works, fan subtags, Chinese candidates, or one installment of a broader series.

## Cumulative semantic audit

- audited: **268**
- correction proposals: **175**
- KEEP: **41**
- NEEDS_EXTERNAL_CHECK: **52**
- production rows changed: **0**

## Confirmed recurring error patterns

1. abbreviation selected as display instead of the full work/franchise title;
2. derivative/spinoff/movie subtitle selected as the parent copyright display;
3. Chinese/non-Japanese candidate selected as Japanese display;
4. Danbooru/raw underscore syntax leaked into display text;
5. series tag represented by one installment instead of the franchise;
6. variant Character row lost the qualifier and became visually identical to the base Character;
7. Japanese search evidence existed but was dropped while display also remained non-Japanese.

These patterns must be expanded across the full 92,739 rows before production correction is approved.

## Next audit route

1. continue Copyright REVIEW_REQUIRED in descending practical impact until the category is semantically stable;
2. resolve high-value `NEEDS_EXTERNAL_CHECK` items selectively with official/primary evidence;
3. process Character by strong recurring patterns rather than raw row order;
4. perform Artist risk audit conservatively without inventing readings;
5. audit the clean stratified sample and expand any newly discovered pattern across all 92,739 rows;
6. consolidate one approved corrections ledger;
7. only then apply corrections, regenerate the runtime overlay, validate, and perform one final workstation catalog rebuild/smoke.
