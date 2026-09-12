# Special2788 Product-Fit Full Audit — 2026-09-12

Status: IN PROGRESS
Scope: Special Core Dictionary IDs 1–2788
Audit purpose: product-purpose fit for the local DanbooruTagTool prompt workflow.
Production data/code modifications: NONE. This file is an audit log only.

## Fixed audit rules

- GitHub source-of-truth files remain authoritative; this log records product-fit audit verdicts only.
- Allowed verdicts: `KEEP`, `KEEP_REFERENCE_ONLY`, `OUT_OF_SCOPE_PRODUCT`, `REVIEW`.
- Do not remove or weaken a concept merely because it is age-related, sexually strong, non-consensual, R18G, niche, or extreme.
- Stage10 generation eligibility is a separate layer from dictionary product-fit.
- Alias/search/reference surfaces may remain `KEEP_REFERENCE_ONLY` when the underlying identity is preserved.
- If canonicalization/aliasing would lose intensity, consent condition, specificity, or identity, stop at `REVIEW` rather than silently normalizing.
- General-English ambiguity belongs primarily to search relevance (#34) unless the Special identity itself is ambiguous.
- Proper nouns/brands are not automatically out-of-scope: retain them when they are direct adult implements/concepts; reject work-specific names/characters/mecha/abilities when they are foreign to the product nucleus.
- During this audit, production Special IDs, canonical identity, alias relations, provenance, and layers are not modified.

## Batch summaries (corrected)

### Batch 1 — IDs 1–200
- KEEP 167
- KEEP_REFERENCE_ONLY 32
- OUT_OF_SCOPE_PRODUCT 0
- REVIEW 1
- REVIEW: #70 `automatic sex`

### Batch 2 — IDs 201–400
- KEEP 162
- KEEP_REFERENCE_ONLY 37
- OUT_OF_SCOPE_PRODUCT 0
- REVIEW 1
- REVIEW: #309 `mecha on girl`

### Batch 3 — IDs 401–600
Corrected after the strong-condition audit.
- KEEP 127
- KEEP_REFERENCE_ONLY 70
- OUT_OF_SCOPE_PRODUCT 0
- REVIEW 3
- REVIEW additions: #438 `attempted rape`, #444 `dubcon`, #445 `dubious consent`

### Batch 4 — IDs 601–800
Corrected after the age-policy audit.
- KEEP 164
- KEEP_REFERENCE_ONLY 36
- OUT_OF_SCOPE_PRODUCT 0
- REVIEW 0
- Age-related concepts are not demoted merely because Stage10 generation is adult-only.

### Batch 5 — IDs 801–1000
- KEEP 191
- KEEP_REFERENCE_ONLY 5
- OUT_OF_SCOPE_PRODUCT 4
- REVIEW 0
- OUT: #876 `slave gear (tsmg nao!)`, #939 `bad vulva`, #950 `slave crest (shield hero)`, #953 `paizuri day`

### Batch 6 — IDs 1001–1200
- KEEP 176
- KEEP_REFERENCE_ONLY 10
- OUT_OF_SCOPE_PRODUCT 6
- REVIEW 8
- OUT: #1012 `poke ball insertion`, #1040 `masturbation day`, #1055 `slave visor (tsmg nao!)`, #1084 `arm slave`, #1166 `exs-slave`, #1171 `instance domination`

### Batch 7 — IDs 1201–1400
Corrected after age-policy and strong-condition audits.
- KEEP 37
- KEEP_REFERENCE_ONLY 157
- OUT_OF_SCOPE_PRODUCT 0
- REVIEW 6
- #1237 `sexualized chibi`, #1238 `lolidom`, #1239 `shotadom` are KEEP.
- #1308 `gang rape` moved from reference-only to REVIEW because non-consent may be lost by normalization to `gangbang`.

### Batch 8 — IDs 1401–1600
- KEEP 0
- KEEP_REFERENCE_ONLY 199
- OUT_OF_SCOPE_PRODUCT 0
- REVIEW 1
- This range is effectively an alias-preservation block.
- REVIEW: #1577 `erect nipplees` due surface/canonical conflict with `covered_nipples`.

### Batch 9 — IDs 1601–1800
- KEEP 52
- KEEP_REFERENCE_ONLY 145
- OUT_OF_SCOPE_PRODUCT 0
- REVIEW 3
- REVIEW: #1616 `gangrape`, #1635 `forced blowjob`, #1792 `penectomy`
- `gagging` and `gaping` remain KEEP; lexical ambiguity is not itself a product-fit failure.

### Batch 10 — IDs 1801–2000
- KEEP 163
- KEEP_REFERENCE_ONLY 36
- OUT_OF_SCOPE_PRODUCT 0
- REVIEW 1
- REVIEW: #1864 `convenient tentacle`
- Strong BDSM/R18G conditions are retained when they represent useful distinct concepts.

### Batch 11 — IDs 2001–2200
- KEEP 129
- KEEP_REFERENCE_ONLY 71
- OUT_OF_SCOPE_PRODUCT 0
- REVIEW 0
- General fashion/support items were commonly demoted to reference-only; niche exposure/fetish clothing and concrete sexual/reproductive conditions remain KEEP.

## Cumulative through ID 2200

- KEEP: 1368
- KEEP_REFERENCE_ONLY: 798
- OUT_OF_SCOPE_PRODUCT: 10
- REVIEW: 24
- Total audited: 2200
- Remaining: 588

## Current REVIEW set notes

Known long-lived REVIEW examples include #70 `automatic sex` and #309 `mecha on girl`.
Additional REVIEW items were added where identity is insufficiently evidenced or normalization could erase material meaning/conditions.

## Persistence policy from this point

- Update this audit log after every completed ~200-ID batch.
- Do not write verdict changes into production dictionary data during the audit.
- Final audit output should distinguish: product removal candidates, reference/search-only assets, true unresolved semantic identity, and ordinary KEEP concepts.
