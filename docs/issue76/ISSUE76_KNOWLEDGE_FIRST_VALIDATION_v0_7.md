# Issue #76 Knowledge-first practical validation v0.7

Status: **KNOWLEDGE-FIRST REVALIDATION PASS / v0.6 STRUCTURE RETAINED / REAL-IMAGE WAVE DOWNGRADED TO SUPPORTING EVIDENCE**

Date: 2026-09-15 JST

## 1. Why this pass exists

The previous v0.6 practical-generation pass used the historical Issue #30 WAI17 image wave as one important cross-check. That evidence is useful but too small and model-mismatched to be the primary basis for a 2,788-row browse taxonomy.

Per user direction, this pass changes the evidence order:

1. **KNOWLEDGE #44 current claim-scoped corpus / current practical NoobAI-Anima guide**
2. **exact/current model-author and upstream sources on the web**
3. **current Japanese practical sources with version preserved**
4. **project full-data semantics / 2,788-row mapping evidence**
5. **historical Issue #30 real-image Wave 1** as a supporting structural cross-check only
6. isolated community anecdotes only as failure-pattern discovery

The taxonomy is still a discovery index, not generation truth.

## 2. Knowledge sources consumed

Project knowledge authority:
- Issue #44 `[KNOWLEDGE][ONGOING][PROMPT-MERGED]`
- `docs/knowledge/current/PRACTICAL_GENERATION_NOOB_ANIMA.md`
- `docs/knowledge/research/BATCH_L_NOOB_ANIMA_PRACTICAL_GENERATION_DEEP_DIVE_20260913.md`
- `docs/knowledge/research/BATCH_M_JAPANESE_PRACTICAL_SOURCE_AUDIT_NOOB_ANIMA_20260913.md`

Primary/current upstream rechecked:
- NoobAI XL 1.1 official model card:
  - https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
- Illustrious paper:
  - https://arxiv.org/abs/2409.19946
- Anima official model card:
  - https://huggingface.co/circlestone-labs/Anima/blob/main/README.md

Current Japanese practical evidence rechecked as supporting operational knowledge:
- recent Anima multi-character practical tests on note.com
- recent Forge Couple / Illustrious practical writeups
- current NoobAI / Illustrious prompt-organization writeups

These do not override exact model-author facts and are not treated as universal success-rate evidence.

## 3. What the higher-priority knowledge says

### 3.1 NoobAI is explicitly tag-native

NoobAI XL 1.1 author guidance says its training uses current Danbooru/e621 native tag captions and recommends the caption organization:

`count -> character -> series -> artists -> special tags -> general tags -> other tags`

This strongly supports keeping Special browse as a concept-discovery layer rather than trying to encode every generation-support detail into a deep semantic tree.

### 3.2 Complex composition/binding is still a separate problem

Illustrious is SDXL/CLIP-based. Its own paper notes that CLIP-based architectures can have limits on complex composition and compositional understanding, and the Illustrious architecture may share those limits.

KNOWLEDGE #44 independently retains actor/target/body-site/count/relation as separate failure dimensions rather than treating unary tag presence as proof of structural correctness.

Therefore a useful browse taxonomy should expose the **structural discriminators users need to find the right Special**, but must not pretend that the browse route itself solves binding.

### 3.3 Anima reinforces explicit actor/relation structure

Current Anima author guidance supports tag + natural-language mixing and explicitly recommends identifying characters and their visible appearance, especially for multiple-character prompts.

Japanese practical sources repeatedly report attribute mixing / role confusion as a real multi-character problem and use explicit actor descriptions or regional tools when needed.

This reinforces the project distinction:
- discovery taxonomy: what concept / body-site / theme is intended;
- generation structure: who acts on whom, ownership, count, visibility, topology;
- assisted control: regional/control/inpaint when Prompt-only is insufficient.

Do not collapse all three into one browse hierarchy.

## 4. Taxonomy decision after knowledge-first revalidation

### KEEP — three independent discovery axes

1. `種類から探す`
2. `部位から探す`
3. `テーマから探す`

This remains the best practical structure.

Reason:
- `種類` answers *what kind of concept is this?* (action, object, body state, fluid, scene, etc.)
- `部位` answers *which intrinsic/discriminative body-site matters?*
- `テーマ` answers *which cross-cutting semantic context is this part of?*

Those are useful discovery questions and map cleanly to generation troubleshooting without pretending to solve actor/target binding.

### KEEP — no return to the old 38 permanent visible subgenres

Knowledge-first review does not produce evidence that the old deep shelves are necessary.

The practical sources instead favor:
- correct tag surface;
- explicit count/actor/relation wording when needed;
- body-site/visibility awareness;
- composition/camera controls;
- regional/control escalation for hard multi-actor cases.

None of those require restoring a `自慰 / 口淫 / 手足刺激 / 局所刺激 / ...` navigation tree.

### KEEP — `kind` optional

Theme-native umbrella concepts should not receive a fake kind solely to satisfy a schema.

Examples:
- `bdsm` -> テーマ:拘束・BDSM
- `guro` / `ryona` -> テーマ:損傷・R18G
- `breeding kink` -> テーマ:生殖・妊娠・授乳

A row is usable if it has at least one practical discovery route.

### KEEP — body-site only when intrinsic/discriminative

The v0.6 correction remains justified by knowledge, independent of the 16-case image wave.

Examples:
- `handjob` -> 男性器
- `fellatio` -> 口・口内 + 男性器
- `cunnilingus` -> 口・口内 + 女性器
- `anilingus` -> 口・口内 + 尻・肛門
- `paizuri` -> 乳房・乳首 + 男性器
- `anal beads` -> 尻・肛門
- `urethral beads` -> 尿道

Do not attach every body part that can appear incidentally. The facet is for a site whose presence distinguishes the concept during discovery/generation diagnosis.

## 5. What should NOT become a visible browse axis

### Count / actor / ownership

These are critical generation predicates, but poor permanent browse categories.

Reasons:
- count is highly compositional and often encoded inside the Special itself (`double`, `multiple`, `cooperative`, etc.);
- actor/target ownership depends on the current scene and cannot be represented reliably as a small fixed shelf;
- current model knowledge says these are failure-diagnosis/control dimensions, not stable ontology nodes.

Keep them in:
- tag identity / search text;
- Prompt construction guidance;
- future result metadata where useful;
- Stage10 diagnosis.

Do not add `人数から探す` or `役割から探す` to the v2 left tree now.

### Camera / visibility / pose support

These are often General/support controls rather than the identity of the Special.

Keep them in General search, Prompt editing, and generation guidance. Do not duplicate them as Special taxonomy facets unless a future concrete discovery failure proves a need.

## 6. The 907-row `行為・接触` shelf

The shelf is large, but raw count alone is not a reason to restore subgenres.

The preferred product behavior remains:
- shallow left tree;
- result-pane filter chips for independent axes;
- same-axis multi-select where meaningful (for example `口・口内` AND `男性器`);
- Japanese/English text search inside the selected set;
- post-count/usage ordering.

The user should not have to decide whether a concept is semantically `口淫`, `局所刺激`, `擦り`, `協力行為`, etc. before seeing candidates.

The system should let the user ask practical questions like:
- `尻・肛門 × 道具`
- `口・口内 × 男性器 × 行為`
- `BDSM × 道具`
- `R18G × 行為`

without creating another nested taxonomy.

## 7. Role of historical real-image evidence after this pass

Issue #30 Wave 1 remains useful as **supporting structural evidence only**.

It may demonstrate concrete examples such as:
- a body-site relation can fail even when component concepts are present;
- a restraint topology can fail;
- scene/context can remain ambiguous;
- seed can change success.

It must NOT be used to claim:
- v0.6 taxonomy is correct because 16 experiments matched it;
- NoobAI success rates;
- model-wide effectiveness of any Special;
- exhaustive coverage of the 2,788 entries.

The knowledge-first structure should survive even if that small WAI17 image set is removed from the evidence stack.

## 8. v0.7 verdict

**PASS_WITH_IMPLEMENTATION_GATES**

Retain the v0.6 semantic patch and three-axis model.
No new semantic mapping delta is required from the knowledge-first revalidation itself.

Before production replacement:
1. materialize the v0.6 patch into a deterministic 2,788-row complete candidate;
2. validate coverage/uniqueness/product-fit invariants;
3. prototype the actual WPF intersection/filter-chip behavior;
4. run realistic browse tasks in the product using knowledge-led task definitions;
5. only add a visible subcategory if those tasks show a concrete discovery failure.

No production WPF taxonomy or protected/canonical data is changed by this document.
