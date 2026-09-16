# Issue #104 — Danbooru General adult/fetish gaps missing from Special

## Result

- Danbooru General canonical: **30,743**
- accepted Special baseline: **2,983**
- General canonical not identity-covered by Special: **28,826**
- strict canonical adult/fetish priority: **217**
- already reviewed/excluded by Issue #94: **11**
- missed by the old Issue #94 final-review prescreen and reviewed here: **206**
- additional opaque rescue rows reviewed: **30**
- total product-fit reviewed: **236**
- Special candidates after final product-fit review: **105**
- definition-level review remaining: **0**

## Interpretation

The old Issue #94 bounded prescreen did not expose most of the strict adult/fetish-named General gaps to final human review. This audit confirms a real Special deep-discovery coverage gap while rejecting broad General descriptors, ordinary variants, memes, UI/game concepts and lexical false positives instead of promoting every adult-looking tag.

All 206 strict prescreen-missed rows plus 30 independent opaque rescue rows have now received an explicit product-fit decision. The remaining definition-review queue is zero.

The 105-row candidate subset is **audit evidence only**. It does not certify model-generation effectiveness and does not mutate production Special.

## Important source checks

- Danbooru `Tag group:Breasts tags` explicitly lists deep breast morphology, actions, relations and transformation concepts used in the review.
- `breast_drop` is a distinct visual reveal/motion state rather than a generic breast descriptor.
- `groping_motion` is a defined two-hand gesture indicating intent to grope.
- leash documentation distinguishes holding/offering/viewer relations and ties them to pet-play usage.
- `cuffed` is not promoted separately because current Special already contains direct `cuffs`, `handcuffs`, `shackles` and structured `bound wrists` coverage.
- `edging_underwear` is routed to General because Danbooru places it with male-underwear color/trim variants, not sexual edging.
- `breast_slider` is rejected as a product-fit false positive because Danbooru places it under gameplay/UI attribute sliders.
- `saliva_pool` remains General: its definition is a broad saliva accumulation state and is not inherently an adult/fetish identity.

## Boundaries

- automatic production promotion: **NO**
- content filter: **NO**
- Issue #70 mutation: **NO**
- UserData mutation: **NO**
- pseudo-canonical tags: **NO**

## Next gate

Integrate this audit evidence, then handle promotion of the 105 candidates as a separate deterministic Special-expansion change with ID assignment, alias/metadata checks, browse/search routing and rollback validation. Do not silently add all General tags and do not use post count alone as a promotion rule.
