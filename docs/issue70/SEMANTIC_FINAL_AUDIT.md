# Issue #70 Semantic Final Audit

## Scope

This lane performs the final semantic QA for the completed Character / Copyright / Artist Japanese overlay.

Baseline main at audit start: `07f6e05c7300831a9c4f52fe3857043594b8413b`.

Frozen runtime facts:

- total rows: 92,739
- Character: 35,890
- Copyright: 8,536
- Artist: 48,313
- ACCEPTED_AI: 79,518
- REVIEW_REQUIRED: 13,221
- runtime results SHA-256: `74d4f16b3b34c313aa94204a6ecfad014791d67d0869070f1455111b0254e622`

## Non-mutation rule

The risk census and semantic audit must not rewrite production translation data. Production corrections are applied only after:

1. risk census,
2. REVIEW_REQUIRED semantic audit,
3. ACCEPTED_AI risk audit,
4. clean ACCEPTED_AI stratified sampling,
5. discovered-pattern expansion across all 92,739 rows,
6. resolution of external-check/user-decision items,
7. final approved correction ledger.

Only then may approved corrections be batch-applied and the Issue #70 runtime overlay regenerated. The workstation catalog rebuild happens once after that final correction pass.

## Audit population

The initial ledger is the union of:

- every `REVIEW_REQUIRED` row,
- `ACCEPTED_AI` rows selected by deterministic semantic-risk rules,
- every `ACCEPTED_AI` row in the top 1% post-count impact tier,
- deterministic clean ACCEPTED_AI sampling (default 300 per category, split between top-10%-excluding-top-1% and the remaining population).

Risk selection is a screening signal, not a verdict. A flagged row may still be `KEEP`.

## Audit verdicts

- `KEEP`
- `FIX_DISPLAY`
- `FIX_SEARCH`
- `FIX_BOTH`
- `NEEDS_EXTERNAL_CHECK`
- `NEEDS_USER_DECISION`

The ledger preserves current values and source evidence next to any proposal. Never overwrite a current value merely because a heuristic fired.

## Category policy

### Copyright

Prefer official Japanese titles / Japanese release titles when established. Do not invent literal Japanese translations for titles normally known in English. Preserve series/installment/remake/sequel disambiguation where needed.

### Character

Prefer official Japanese character names and stable common Japanese forms. Check surname/given-name form, disambiguation, versions/variants, nicknames and alternate identities. Use preserved related-Copyright evidence as context, not as an automatic truth rule.

### Artist

Do not invent readings. Handles, circles, pseudonyms and established romanized forms may legitimately remain ASCII. External lookup is selective for ambiguous/high-impact rows rather than automatic for all 48,313 Artist rows.

## Impact policy

`post_count` changes audit priority, not correctness. Low-post-count rows may still require correction. High-impact rows are deliberately oversampled/audited because mistakes there affect more practical searches.

## Output

`python scripts/issue70/audit_semantic_risk.py` emits read-only files under `artifacts/issue70-semantic-audit/`:

- `risk_summary.json`
- `review_required.csv`
- `accepted_risk.csv`
- `accepted_clean_sample.csv`
- `audit_ledger_template.csv`

These are audit artifacts, not production overlay files.
