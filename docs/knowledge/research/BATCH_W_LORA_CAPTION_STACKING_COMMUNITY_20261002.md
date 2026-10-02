# BATCH_W — LoRA caption / stacking / synthetic-data community experiments — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`
Branch: `knowledge/generation-corpus`
Mode: controlled public-user LoRA experiment harvest
Focus: caption allocation, trigger absorption, synthetic self-training, adapter stacking, weight sweeps

## 1. Character-LoRA caption density — 2026-09-30

Source:
- 久遠ノイズ  
  https://note.com/kuon_noise/n/n5bd44f5bb1fb

Compared caption strategies:
- A: trigger only;
- B: trigger + reduced/switchable tag set;
- C: trigger + full tagger output.

Inference also compared:
- simple prompt;
- detailed prompt;
- changed outfit;
- changed camera/pose;
- later one-character / multi-outfit datasets.

Reported behavior:
- full-tagger-caption variant could fail to reproduce omitted attributes under a simple inference prompt because those traits had been learned as explicitly conditioned features;
- the reduced-caption variant reproduced the character well under simpler prompting;
- all variants could work when inference prompts explicitly supplied needed attributes;
- changed clothes and dynamic pose tests did not reveal a clear winner in the shown one-character case;
- for several outfits, the author found minimal switch tags sufficient in that dataset.

Interpretation:
Captioning decides **what belongs to the trigger prior** versus **what must be independently named at inference**.

Do not generalize:
- “minimal captions are universally best”;
- the article uses the author's current timestep/training setup;
- multi-character behavior was still open.

Promoted:
- K-COMM-LORA-004.

## 2. Synthetic Anima-only dataset / rapid identity convergence

Source:
- lilting channel, 2026-05-27 / updated 2026-06-03  
  https://lilting.ch/articles/wai-anima-keichan-lora-training

Experiment:
- character LoRA dataset made entirely from Anima-generated images;
- tested epochs 5 / 10 / 20 / 50 / 125;
- three inference formats:
  - K: trigger only;
  - N: trigger + natural-language description;
  - KT: trigger + explicit `hair intakes` tag;
- 3 seeds × 5 epochs × 3 formats = 45 images;
- Turbo LoRA used for 8-step evaluation.

Reported:
- core identity locked relatively early in that synthetic dataset;
- trigger-only captured broad identity but the distinctive intake feature was weaker;
- explicit `hair intakes` strengthened the intake but also produced unwanted ahoge in the shown test;
- concise NL description produced a cleaner intake without that side effect;
- author interprets the unwanted association as inherited from the base model's concept coupling;
- clothing was deliberately left variable rather than baked into identity.

High-value lesson:
A LoRA trained on model-generated data can strongly learn identity while also inheriting the generator's own correlations/biases. Stronger explicit tags at inference can reawaken those correlations.

Promoted:
- K-COMM-LORA-005.

## 3. LoRA stacking — same-seed 0 / 1 / 3 adapters

Source:
- bububu, 2026-09-13  
  https://note.com/fresh_macaw9581/n/n7a3a7f6ed1e7

Shared setup:
- Anima 1.0;
- 1024×1280;
- steps 20;
- CFG 4;
- seed 314159265 reset before each run;
- workflow wiring unchanged.

Conditions:
1. no LoRA;
2. one style LoRA;
3. three LoRAs (character/style/detailer-like mix).

Reported:
- no LoRA: simpler/cleaner composition;
- one style LoRA: more hair/clothing/light/background detail while remaining relatively stable;
- three: strongest volume/shading/detail, but also unrequested clothing/props and reduced prompt/composition consistency.

Methodological note:
The author initially caught automatic seed changes and regenerated the comparison with the seed manually reset. That makes this more useful than an ordinary showcase.

Promoted:
- K-COMM-LORA-006.

## 4. Single style-LoRA weight sweep 0 / 0.4 / 0.7 / 1.0

Source:
- bububu, 2026-09-13  
  https://note.com/fresh_macaw9581/n/nc7bf40b8429c

Shared setup:
- Anima Base v1.0;
- qwen_3_06b_base;
- qwen_image_vae;
- 1024×1280;
- steps 20;
- CFG4;
- er_sde/simple;
- seed 314159265;
- CLIP strength fixed 1.0;
- only Model strength changed.

Reported:
- increasing weight changed face, line, hair, clothing, light and background density;
- author preferred 0.7 for this particular LoRA;
- at 1.0 the LoRA's own style was more dominant and prompt-defined elements became easier to shift.

Treatment:
- the preferred 0.7 is **not** promoted;
- the durable lesson is that weight changes are not a pure one-dimensional style-strength knob.

Promoted:
- K-COMM-LORA-007.

## 5. Training-data ontology implication

Across BATCH_Q/R/W:
- trigger token = features intentionally bundled as identity/prior;
- captions = features kept independently controllable;
- dataset variation = evidence that a feature is mutable;
- missing variation = risk that context becomes welded into the trigger;
- inference support can expose or suppress model-native concept correlations.

A future LoRA knowledge schema should retain:
- target_type: character / style / concept / pose / speed / control;
- training_base;
- trigger(s);
- caption policy;
- mutable attributes;
- intentionally absorbed attributes;
- dataset-source type: real / curated illustration / model-generated / mixed;
- adapter weight;
- text-encoder/CLIP weight where relevant;
- known spillover;
- compatibility evidence.

## Promotion result

New CANDIDATE:
- K-COMM-LORA-004
- K-COMM-LORA-005
- K-COMM-LORA-006
- K-COMM-LORA-007

No universal numeric weight/epoch/caption recommendation accepted.
No HOLD closed.
