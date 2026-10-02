# BATCH_T — Lexical ambiguity / tag coverage community map — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Branch: `knowledge/generation-corpus`  
Mode: public-user tag-behavior harvest  
Focus: colors, garments, body tags, aesthetic tags, cross-model character/tag response

## 1. Color words are not necessarily pure color controls

Source:
- みし, 2026-06-07  
  https://note.com/mith_mmk/n/ndcd5709f47ff

Profile:
- Anima Base v1.0.

Method:
- automated basic + CSS named-color sweep;
- fixed base character/clothing colors;
- target surface inserted as `<colorname> color background`;
- machine-assisted checking plus manual correction.

Reported:
- broad color vocabulary coverage;
- `navy` and `indigo` yielded distinguishable colors;
- lexical collisions:
  - `snow` pulled snow-related content;
  - `seashell` pulled shell-related content;
  - `orchid` pulled orchid/flower concepts;
  - `tomato` strongly injected tomato-related meaning;
- some light-* CSS names were not reliably recognized;
- spacing/plural differences changed behavior in some cases.

Limitations:
- author explicitly says color-variance testing was rough;
- machine checker reliability was low and manually corrected;
- no claim about complete CSS-color support.

Promoted:
- K-COMM-TAG-003.

Practical implication:
- a UI label like “background color = snow” cannot assume the English token behaves as a namespace-qualified color;
- generation behavior may need a role-qualified surface such as “snow color background”, and even that can retain lexical bleed.

## 2. Body-tag coverage — preview-era large tag sweep

Source:
- みし, 2026-03-28  
  https://note.com/mith_mmk/n/n8f06ec51fba5

Environment:
- Anima preview2
- Qwen3-0.6B
- ComfyUI
- automated/machine-assisted tag testing with manual correction.

Value:
- broad discovery list for body/anatomy tag behavior;
- useful for selecting modern v1.0 retest candidates.

Limitation:
- preview2 is stale relative to Base/Aesthetic/Turbo v1;
- author reports many automated-analysis false positives;
- no current Claim promotion.

## 3. Preview3 broad tag-test notes

Source:
- みし, 2026-05-02  
  https://note.com/mith_mmk/n/n912541215f09

Reported high-level observations:
- tag combinations changed the effect/meaning of individual tags;
- object/food behavior differed from Illustrious in the author's testing;
- some rare tags appeared represented;
- safety behavior was not perfectly stable.

Treatment:
- discovery/backlog only;
- too broad and preview-era for durable v1 Claim;
- useful for building a modern retest sample.

## 4. Real-world garment names vs learned visual vocabulary

Source:
- ノラ, 2026-08-21  
  https://note.com/stray_dog0012/n/n9ece9bc66aef

Design:
- real 2026 fashion/swimwear taxonomy chosen externally to reduce cherry-picking;
- fixed pose/background/lighting/camera;
- only garment wording changed;
- roughly a dozen generated examples.

Research value:
- excellent candidate set for testing the difference between:
  - real-world fashion product vocabulary;
  - Danbooru canonical garment tags;
  - structural descriptive language.

Treatment:
- source-map only until detailed per-item pass/fail is re-extracted.

## 5. Auto-tag vs manual-adjustment LoRA experiment

Source:
- azrakuC, 2026-08-21  
  https://note.com/azrakuc/n/n3d6d5eaa850e

Topic:
- Anima LoRA training;
- mostly auto-tagged dataset vs manual tag adjustment;
- whether detailed tag curation remains necessary.

Treatment:
- paid/partial public article in current retrieval;
- retain as research lead;
- no directional Claim without complete methods/results.

## 6. Illustrious aesthetic-tag pressure vs checkpoint prior

Source:
- alaya, 2026-08-19  
  https://note.com/alayaproject/n/ned0a95fb3c86

Reported run:
- semi-real Illustrious derivative;
- custom style LoRA 0.85;
- repeated `kawaii/cute/adorable` plus a large quality/style block;
- 100 generated images across scene motifs;
- author reports the semi-real rendering prior remained despite repeated “cute/kawaii” pressure.

Interpretation:
- useful illustration that a checkpoint/LoRA prior can dominate an aesthetic adjective;
- highly confounded by style LoRA and many simultaneous style terms;
- no Claim promotion.

## 7. Cross-model character-tag comparison

Source:
- TNSOR_WORKS, 2026-06-26  
  https://note.com/tnsor_works/n/n0d9ab70999f2

Design:
- same tag prompt and seed across Krea2 / NoobAI / Anima / Illustrious / another model;
- no LoRA;
- character features held as prompt target.

Value:
- discovery of differences in feature retention and model-native interpretation;
- useful for selecting exact-model follow-up tests.

Limitation:
- same seed across different model architectures/checkpoints is not equivalent controlled latent identity;
- few images per model;
- no comparative superiority Claim.

## 8. Prompt relation wording: latest same-seed Anima practice

Source:
- あおくま, 2026-09-05  
  https://note.com/ai_on_desk/n/n553eac75840d

Reported:
- tags plus one relation/action sentence improved “who does what to whom” in the tested Aesthetic setup;
- referring to actors only as right/left could lose previously tagged appearance;
- referring by visible attributes such as hair/clothing retained identity better in those comparisons.

Treatment:
- strengthens existing K-COMM-ANIMA-001/002/014;
- no duplicate Claim.

## 9. Why this matters for tag-tool data design

A tag-generation behavior table should eventually permit:
- `lexical_ambiguity`: color/object/name collisions;
- `learned_broader_prior`: narrow surface evokes a broad concept;
- `weak_trigger`;
- `misdirected_trigger`;
- `context_suppressed`;
- `combination_sensitive`;
- `profile_specific`;
- `needs_structural_description`.

This is evidence metadata, not canonical Danbooru identity.

## Promotion result

New CANDIDATE:
- K-COMM-TAG-003

No HOLD closed.
