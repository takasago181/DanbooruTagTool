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

## Final read-only census baseline

The first broad census was intentionally treated as exploratory and was rejected because it over-selected Artist rows and search-field rows. The accepted census is the category-aware, runtime-aware v2 pass on audit branch commit `610701266693600abbc56983eb6f453a2aa064dd`.

The runtime search contract was checked in `RuntimeCatalogIndex.SearchDocument.Create()`: `entry.Japanese` is indexed separately from `entry.JapaneseSearch`. Therefore a blank `search_ja`, or a `search_ja` that does not repeat `display_ja`, is not itself an error.

Accepted census outcome:

- rows scanned: 92,739
- REVIEW_REQUIRED: 13,221
- ACCEPTED_AI risk: 4,186
- clean ACCEPTED_AI deterministic sample: 900
- unique initial audit ledger: 18,307

Ledger by category:

- Character: 14,869
- Copyright: 2,412
- Artist: 1,026

The 4,186 ACCEPTED_AI risk rows comprise:

- Character: 2,410
- Copyright: 1,050
- Artist: 726

Risk selection is a screening signal, not a verdict. A flagged row may still be `KEEP`.

## Audit population

The initial ledger is the union of:

- every `REVIEW_REQUIRED` row,
- `ACCEPTED_AI` rows selected by deterministic semantic-risk rules,
- every `ACCEPTED_AI` row in the top 1% post-count impact tier,
- deterministic clean ACCEPTED_AI sampling (300 per category, split between top-10%-excluding-top-1% and the remaining population).

The ACCEPTED_AI screening deliberately does **not** treat normal Artist romanization as an error and does **not** require `search_ja` to duplicate `display_ja`.

## Semantic audit order

Do not review the 18,307 rows as one arbitrary row-order stream. Review by repeatable problem family so one confirmed error pattern can be expanded across all 92,739 rows:

1. structural corruption / malformed display (`_`, broken brackets, replacement characters),
2. strong Japanese source evidence but current Latin/canonical fallback,
3. duplicate/colliding display names and lost disambiguation,
4. source-evidence conflicts and suspicious search-only terms,
5. Character variant/identity/name-order issues using related Copyright context,
6. Copyright official-title / franchise / installment naming issues,
7. Artist Japanese readings not supported by preserved evidence,
8. remaining REVIEW_REQUIRED ambiguity groups,
9. clean ACCEPTED_AI stratified sample.

Whenever a semantic error pattern is confirmed, run a full-dataset pattern expansion before considering that pattern closed.

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

`post_count` changes audit priority, not correctness. Low-post-count rows may still require correction. High-impact rows are deliberately covered because mistakes there affect more practical searches.

## External verification policy

Do not research all rows externally. Use external verification when the preserved evidence cannot safely resolve identity or official Japanese naming, especially for high-impact rows. Danbooru aliases/wiki/identity evidence and official sources take priority over generic web results.

## Output

`python scripts/issue70/audit_semantic_risk_v2.py` emits read-only files under `artifacts/issue70-semantic-audit-v2/`:

- `risk_summary.json`
- `review_required.csv`
- `accepted_risk.csv`
- `accepted_clean_sample.csv`
- `audit_ledger_template.csv`

These are audit artifacts, not production overlay files.
