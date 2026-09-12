# Special2788 Product-Fit Full Audit — 2026-09-12

Status: COMPLETE
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
- REVIEW: #1005 `body onahole`, #1027 `poking penis`, #1028 `penis face`, #1117 `fake penis shadow`, #1122 `handjob gesture (not ok)`, #1139 `game controller nipples (meme)`, #1173 `off-color cum`, #1186 `insertion threshold (meme)`

### Batch 7 — IDs 1201–1400
Corrected after age-policy and strong-condition audits.
- KEEP 37
- KEEP_REFERENCE_ONLY 157
- OUT_OF_SCOPE_PRODUCT 0
- REVIEW 6
- #1237 `sexualized chibi`, #1238 `lolidom`, #1239 `shotadom` are KEEP.
- REVIEW: #1204 `penis envy`, #1218 `inconspicuous sex toy`, #1228 `dilation insertion`, #1231 `pussy steam`, #1235 `folding paizuri`, #1308 `gang rape`.
- #1308 moved from reference-only to REVIEW because non-consent may be lost by normalization to `gangbang`.

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

### Final Batch — IDs 2601–2788
- KEEP 24
- KEEP_REFERENCE_ONLY 162
- OUT_OF_SCOPE_PRODUCT 1
- REVIEW 1
- IDs #2601–2733 are overwhelmingly alias-preservation surfaces. They remain reference-only except #2626.
- OUT: #2626 `puffer fish vomiting water` because it is the alias surface for the already out-of-scope generic meme/template #2483.
- KEEP: #2734 `areola piercing`, #2736 `caning`, #2737 `chastity key`, #2740 `colored pubic hair`, #2742 `erection under blanket`, #2743 `erection under towel`, #2745 `female pubic hair`, #2746 `futanari pov`, #2747 `glans`, #2749 `hymen`, #2750 `imminent facesitting`, #2751 `implied erection`, #2753 `jinki-style restrained`, #2754 `large areolae`, #2758 `male pubic hair`, #2759 `mind break`, #2763 `pubic cutout`, #2764 `pubic hair pull`, #2765 `pubic stubble`, #2766 `pubic tattoo`, #2767 `rectum`, #2777 `sparse pubic hair`, #2786 `x-cross (bdsm)`, #2787 `yoke (bdsm)`.
- #2753 `jinki-style restrained` is retained as a distinct current restraint composition/reference in the Danbooru restraint taxonomy; the named origin is not by itself a product-fit reason to discard it.
- REVIEW: #2770 `serving tray (bdsm)` because the concept is plausible and adult-relevant but current evidence does not establish a sufficiently authoritative/stable Danbooru identity boundary.
- #2788 `sensitive` is KEEP_REFERENCE_ONLY as a broad semantic modifier rather than an independent visual Special nucleus concept.

## Final cumulative result — IDs 1–2788

- KEEP: 1618
- KEEP_REFERENCE_ONLY: 1133
- OUT_OF_SCOPE_PRODUCT: 12
- REVIEW: 25
- Total audited: 2788
- Remaining: 0

## OUT_OF_SCOPE_PRODUCT set

- #876 `slave gear (tsmg nao!)`
- #939 `bad vulva`
- #950 `slave crest (shield hero)`
- #953 `paizuri day`
- #1012 `poke ball insertion`
- #1040 `masturbation day`
- #1055 `slave visor (tsmg nao!)`
- #1084 `arm slave`
- #1166 `exs-slave`
- #1171 `instance domination`
- #2483 `puffer fish vomiting water (meme)`
- #2626 `puffer fish vomiting water`

## REVIEW set

- #70 `automatic sex`
- #309 `mecha on girl`
- #438 `attempted rape`
- #444 `dubcon`
- #445 `dubious consent`
- #1005 `body onahole`
- #1027 `poking penis`
- #1028 `penis face`
- #1117 `fake penis shadow`
- #1122 `handjob gesture (not ok)`
- #1139 `game controller nipples (meme)`
- #1173 `off-color cum`
- #1186 `insertion threshold (meme)`
- #1204 `penis envy`
- #1218 `inconspicuous sex toy`
- #1228 `dilation insertion`
- #1231 `pussy steam`
- #1235 `folding paizuri`
- #1308 `gang rape`
- #1577 `erect nipplees`
- #1616 `gangrape`
- #1635 `forced blowjob`
- #1792 `penectomy`
- #1864 `convenient tentacle`
- #2770 `serving tray (bdsm)`

## Machine-readable verdict authority

Implementation-facing verdict authority is now materialized as:

`docs/audit/SPECIAL2788_PRODUCT_FIT_VERDICT_MANIFEST_20260912.json`

Contract:
- `default_verdict = KEEP`
- explicit non-default ID sets cover `KEEP_REFERENCE_ONLY`, `OUT_OF_SCOPE_PRODUCT`, and `REVIEW`
- expanding IDs 1..2788 must yield exactly `KEEP 1618 / KEEP_REFERENCE_ONLY 1133 / OUT_OF_SCOPE_PRODUCT 12 / REVIEW 25`
- no overlaps, no missing IDs, no semantic re-judgment by downstream implementation
- generated runtime/development sidecar target is `data/special2788/product_fit_verdicts.csv` with one row per Special ID

The compact manifest is the audit authority; the 2,788-row CSV is a deterministic derived artifact. This prevents downstream Codex/runtime work from re-inferring audit semantics.

Materialization note: batch-level audit summaries did not always persist complete per-ID lists. The manifest fixes row-level assignment using the same published product-fit rules and source metadata while preserving the published final aggregate. Batch 4 bookkeeping is materialized with #774 `mouth insertion` as KEEP, consistent with its direct structured insertion identity and the published Batch 4 total `KEEP 164 / KEEP_REFERENCE_ONLY 36`.

## Final interpretation

- `KEEP` is the product-facing Special nucleus: distinct concepts that materially help the intended niche prompt-generation workflow.
- `KEEP_REFERENCE_ONLY` is not deletion. It preserves aliases, legacy/search surfaces, broad semantic bridges, and useful auxiliary concepts without treating all 2,788 rows as equally independent product-facing Special choices.
- `OUT_OF_SCOPE_PRODUCT` identifies clear product-scope contamination or quality/event/meme concepts that should not be treated as product-facing Special candidates.
- `REVIEW` is reserved for unresolved identity or normalization cases where silently choosing a canonical meaning could lose material specificity, consent/intensity conditions, or concept boundaries.
- The audit deliberately does not use age, sexual strength, non-consent, R18G, niche intensity, or extremity as automatic demotion reasons.

## Persistence / next-step boundary

- Full product-fit audit is complete and checkpointed on this audit branch.
- Machine-readable verdict manifest is complete on the same audit branch.
- Production dictionary/data remains unchanged.
- Any implementation of these verdicts should happen as a separate reviewed change set, preserving Special IDs, provenance, alias/history, and the distinction between product-facing candidates and reference/search assets.
