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

### Batch 12 — IDs 2201–2400
- KEEP 112
- KEEP_REFERENCE_ONLY 88
- OUT_OF_SCOPE_PRODUCT 0
- REVIEW 0
- General clothing/fashion/body-part/search surfaces were kept as reference-only when they do not form the Special adult-generation nucleus.
- #2317 `wringing clothes` is reference-only: it is a general wet-clothes action, not an adult-specific Special concept.
- Age-related semantic descriptors (#2351–2357, #2375, #2379–2380) are reference-only because they are semantic/search descriptors, not because of age policy.
- #2373 `reverse trap` and #2374 `trap` are reference-only as legacy terminology/search assets.
- #2393 `blindfold mask` is reference-only as a general accessory concept; #2394 `ribbon bondage` remains KEEP as a concrete bondage concept.

### Batch 13 — IDs 2401–2600
- KEEP 114
- KEEP_REFERENCE_ONLY 85
- OUT_OF_SCOPE_PRODUCT 1
- REVIEW 0
- OUT: #2483 `puffer fish vomiting water (meme)` — named generic meme/template unrelated to the adult-generation nucleus.
- KEEP_REFERENCE_ONLY (non-alias): #2405 `colored blindfold`, #2419 `topless other`, #2424 `rear naked choke`, #2425 `vomiting rainbows`, #2431 `unworn blindfold`, #2443 `pee pad`, #2471 `holding blindfold`, #2487 `piss bottle`, #2498 `nude guy wrapped in ribbons standing (meme)`, #2501 `whipping hair`, #2505 `thong panties`, #2519 `sexually suggestive`.
- IDs #2528–2600 are alias-preservation surfaces and remain KEEP_REFERENCE_ONLY.
- #2501 `whipping hair` is a verified general hair action, not an adult-specific Special nucleus concept; retain for reference/search only.
- #2424 `rear naked choke` is a martial-arts chokehold; current clothing/exposure-style metadata is not a reason to treat it as an adult core concept.
- #2442 `negative space oral (meme)` remains KEEP because it represents a distinct niche sexual composition/template with practical generation value; meme origin alone is not a demotion reason.
- #2526 `virgin killer sweater` and #2527 `virgin destroyer sweater` remain KEEP as distinct sexualized clothing designs with useful visual identity.

## Cumulative through ID 2600

- KEEP: 1594
- KEEP_REFERENCE_ONLY: 971
- OUT_OF_SCOPE_PRODUCT: 11
- REVIEW: 24
- Total audited: 2600
- Remaining: 188

## Current REVIEW set notes

Known long-lived REVIEW examples include #70 `automatic sex` and #309 `mecha on girl`.
Additional REVIEW items were added where identity is insufficiently evidenced or normalization could erase material meaning/conditions.

## Persistence policy from this point

- Update this audit log after every completed ~200-ID batch.
- Do not write verdict changes into production dictionary data during the audit.
- Final audit output should distinguish: product removal candidates, reference/search-only assets, true unresolved semantic identity, and ordinary KEEP concepts.
