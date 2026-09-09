# Batch 24 R2 Integrity / Acceptance Gate

Issue: #32
Branch: `dict-validation/quarantine`
Range: 2301-2400
Rule: R2

## Static integrity
- Durable blocks: 5 x 20 rows
- Sequence coverage: 2301-2400 contiguous
- Unique sequences: 100 / 100
- Missing: 0
- Duplicate: 0
- Final-state counts: PASS 95 / FIX 0 / REVIEW 5 / IMAGE_TEST_REQUIRED 0

Blocks:
- `results_blocks/2301_2320.csv`
- `results_blocks/2321_2340.csv`
- `results_blocks/2341_2360.csv`
- `results_blocks/2361_2380.csv`
- `results_blocks/2381_2400.csv`

## Deep-review non-PASS
- 2301 `collar grab` — A-risk REVIEW: independent Danbooru semantics require another person's collar, while ActorRequirementOverride is blank. Do not guess a FIX or spatial/separation flags before the project clothing-grab convention is resolved.
- 2308 `grabbing another's skirt` — A-risk REVIEW for the same actor-ownership gap; no spatial/separation inference solely from contact.
- 2309 `necktie grab` — A-risk REVIEW: neckwear-grab semantics implicate another person's neckwear; blank ActorRequirementOverride remains unresolved.
- 2393 `blindfold mask` — S-risk REVIEW: PROVISIONAL/audit-only row. Independent identity evidence is insufficient to choose the project's exact GenerationFamily/GenerationRole/ImplDependency.
- 2394 `ribbon bondage` — S-risk REVIEW: PROVISIONAL/audit-only row. Usage evidence is insufficient for exact project generation structure; blank fields are not auto-errors.

## PASS re-extraction audit
Deterministic/coverage-oriented re-audit: 20 / 95 PASS rows.

Sample file: `pass_sampling_batch24_r2.csv`

- Sampled PASS: 20
- Re-audit PASS: 20
- New false-PASS: 0
- All A-risk PASS rows included: 2332, 2333, 2334, 2335, 2336, 2360
- Additional +10 sample required: NO (clean sample)

Semantic-role and alias boundaries were explicitly represented in the sample: semantic/search support was not promoted to direct model recognition, and alias canonical linkage remained statistics-only.

## Side ledgers / scope
- `candidate_fixes.csv`: inspected at each checkpoint; Batch24 delta 0.
- `revalidation_queue.csv`: inspected at each checkpoint; active pending pointer remains 0; Batch24 delta 0.
- Semantic support snapshot remains 55 / 58 covered.
- Stage10 HOLD/Unknown knowledge was not promoted to production truth.
- main / production modified: NO.

## Gate
**Batch 24 R2 acceptance gate: PASS**

Safe next first-pass sequence: 2401.
