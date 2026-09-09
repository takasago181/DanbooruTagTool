# Batch A Source Registry — False-Assumption Prevention — 2026-09-09

Owner: Issue #44

Research target:
- support conflict / anti-support
- actor-target / body-site / relation binding
- rare/composite trigger drift
- Negative semantic collision
- failure diagnosis
- seed/evaluation reliability
- LoRA/multi-concept confounding where it affects diagnosis

Evidence classes follow Issue #44:
- `FACT_EXACT_MODEL`
- `FACT_GENERAL`
- `CONTROLLED_PRACTICAL`
- `PRACTICAL`
- `COMMUNITY`
- `HOLD`

Language is metadata, not evidence rank.

---

## Primary / conference / model-author evidence

### A01 — CO3 / mode collisions

- Title: Steer Away from Mode Collisions: Improving Composition in Diffusion Models
- Venue: ICLR 2026
- URL: https://proceedings.iclr.cc/paper_files/paper/2026/hash/2952abee7fa3c062c7855c108ceb45e5-Abstract-Conference.html
- Language: English
- Class: `FACT_GENERAL`
- Scope: diffusion multi-concept composition, not exact project checkpoint
- Used for:
  - missing/faint/colliding concepts under joint prompts;
  - single-concept dominance inside multi-concept generation;
  - unstable guidance-weight regimes can worsen balance.
- Do not infer:
  - exact WAI/NoobAI/Anima weight values;
  - one universal correction rule.

### A02 — R-Bind

- Title: R-Bind: Unified Enhancement of Attribute and Relation Binding in Text-to-Image Diffusion Models
- Venue: EMNLP 2025
- URL: https://aclanthology.org/2025.emnlp-main.349/
- Language: English
- Class: `FACT_GENERAL`
- Scope: T2I semantic binding
- Used for:
  - entity-attribute binding and entity-relation-entity binding are distinct alignment problems;
  - relation correctness cannot be inferred from unary concept presence.
- Do not infer:
  - exact Danbooru Special support recipe.

### A03 — Negative Prompt mechanism

- Title: Understanding the Impact of Negative Prompts: When and How Do They Take Effect?
- URL: https://arxiv.org/abs/2406.02965
- Language: English
- Class: `FACT_GENERAL`
- Scope: negative prompting mechanisms in diffusion
- Used for:
  - delayed effect;
  - deletion through latent neutralization/cancellation with positive concept;
  - Negative is a semantic intervention, not neutral cleanup.
- Do not infer:
  - exact strength of `bad anatomy`/`extra limbs` on every project model.

### A04 — ConceptMix

- Title: ConceptMix: A Compositional Image Generation Benchmark with Controllable Difficulty
- URL: https://arxiv.org/abs/2408.14339
- Language: English
- Class: `FACT_GENERAL`
- Scope: compositional T2I benchmarks across models
- Used for:
  - generation performance drops as requested concept count/complexity increases, especially for open models;
  - concept count is meaningful but must be interpreted by concept type and relation structure.
- Do not infer:
  - a fixed maximum number of Specials for this product.

### A05 — Reliable Random Seeds

- Title: Enhancing Compositional Text-to-Image Generation with Reliable Random Seeds
- Venue: ICLR 2025
- URL: https://proceedings.iclr.cc/paper_files/paper/2025/hash/708e0d691a22212e1e373dc8779cbe53-Abstract-Conference.html
- Code: https://github.com/doub7e/Reliable-Random-Seeds
- Language: English
- Class: `FACT_GENERAL`
- Scope: compositional seed effects
- Used for:
  - initial noise/seed materially affects composition, object placement and prompt adherence;
  - a single lucky/unlucky seed is not a reliability estimate.
- Do not infer:
  - preselecting a global “good seed” for DanbooruTagTool production.

### A06 — Good Seed Makes a Good Crop

- Title: Good Seed Makes a Good Crop: Discovering Secret Seeds in Text-to-Image Diffusion Models
- Venue: WACV 2025
- URL: https://openaccess.thecvf.com/content/WACV2025/html/Xu_Good_Seed_Makes_a_Good_Crop_Discovering_Secret_Seeds_in_WACV_2025_paper.html
- Language: English
- Class: `FACT_GENERAL`
- Scope: diffusion seed effects
- Used for:
  - seeds affect object location, size, depth, borders, grayscale tendency and other visual dimensions;
  - seed is part of experiment identity rather than harmless randomness.

### A07 — GenEval

- Title: GenEval: An Object-Focused Framework for Evaluating Text-to-Image Alignment
- Repo: https://github.com/djghosh13/geneval
- Paper: https://arxiv.org/abs/2310.11513
- Language: English
- Class: `FACT_GENERAL`
- Scope: object/count/color/position/attribute-binding evaluation
- Used for:
  - benchmark generates 4 images per prompt rather than one;
  - composition/binding evaluation needs multiple samples;
  - object presence and relation/binding should be judged separately.
- Do not infer:
  - 4 samples is a universal minimum for every Stage10 question.

### A08 — T2I-CompBench

- Title: T2I-CompBench: A Comprehensive Benchmark for Open-world Compositional Text-to-image Generation
- Repo: https://github.com/Karine-Huang/T2I-CompBench
- Language: English
- Class: `FACT_GENERAL`
- Scope: color/shape/texture/spatial/non-spatial/complex compositional evaluation
- Used for:
  - benchmark generates 10 images per prompt for metric calculation;
  - separate evaluators are used for different semantic categories;
  - fixed comparison conditions do not eliminate the need for multiple outputs.
- Do not infer:
  - 10 images per project experiment is mandatory.

### A09 — LoRACLR

- Title: LoRACLR: Contrastive Adaptation for Customization of Diffusion Models
- Venue: CVPR 2025
- URL: https://openaccess.thecvf.com/content/CVPR2025/html/Simsar_LoRACLR_Contrastive_Adaptation_for_Customization_of_Diffusion_Models_CVPR_2025_paper.html
- Language: English
- Class: `FACT_GENERAL`
- Scope: multi-LoRA / multi-concept personalization
- Used for:
  - ordinary combination/merging of multiple personalized models can lead to attribute entanglement/feature interference;
  - LoRA composition is a confounder for Special evaluation.

### A10 — ConceptSplit

- Title: ConceptSplit: Decoupled Multi-Concept Personalization of Diffusion Models via Token-wise Adaptation and Attention Disentanglement
- Venue: ICCV 2025
- URL: https://openaccess.thecvf.com/content/ICCV2025/html/Lim_ConceptSplit_Decoupled_Multi-Concept_Personalization_of_Diffusion_Models_via_Token-wise_Adaptation_ICCV_2025_paper.html
- Chinese open-access mirror: https://openaccess.thecvf.com.cn/content/ICCV2025/html/Lim_ConceptSplit_Decoupled_Multi-Concept_Personalization_of_Diffusion_Models_via_Token-wise_Adaptation_ICCV_2025_paper.html
- Language: English + Chinese mirror
- Class: `FACT_GENERAL`
- Scope: multi-concept personalization
- Used for:
  - concept mixing/interference and attention entanglement are real multi-concept failure mechanisms.

### A11 — TARA

- Title: TARA: Token-Aware LoRA for Composable Personalization in Diffusion Models
- Venue: AAAI 2026
- URL: https://ojs.aaai.org/index.php/AAAI/article/view/37788
- Language: English
- Class: `FACT_GENERAL`
- Scope: multiple LoRA modules
- Used for:
  - multi-LoRA generation can cause identity missing and visual feature leakage;
  - token-wise interference and spatial misalignment are explicit failure modes.

### A12 — Personalized token context entanglement

- Title: Disentangling Subject-Irrelevant Elements in Personalized Text-to-Image Diffusion via Filtered Self-Distillation
- Venue: WACV 2025
- URL: https://openaccess.thecvf.com/content/WACV2025/html/Choi_Disentangling_Subject-Irrelevant_Elements_in_Personalized_Text-to-Image_Diffusion_via_Filtered_Self-Distillation_WACV_2025_paper.html
- Language: English
- Class: `FACT_GENERAL`
- Scope: personalization / subject-context conflicts
- Used for:
  - personalized concept tokens can bind irrelevant background/pose elements from training and conflict with prompt context.
- Product implication:
  - LoRA/trigger can carry hidden structural priors; apparent Prompt failure can originate from personalization entanglement.

---

## Exact model / official-hosted evidence

### A13 — Anima model card

- Model: `circlestone-labs/Anima`
- URL: https://huggingface.co/circlestone-labs/Anima
- Language: English
- Class: `FACT_EXACT_MODEL`
- Current documented facts used:
  - anime knowledge cutoff September 2025;
  - Base/Aesthetic/Turbo separated;
  - Base/Aesthetic standard 30–50 steps, CFG 4–5; Turbo CFG1, 8–12 steps;
  - trained with tags, natural language, and mixed captions;
  - tag order and spelling conventions;
  - prefer Gelbooru version when a Danbooru/Gelbooru tag differs;
  - tag dropout;
  - multiple characters: name character and describe basic appearance; names alone can confuse model;
  - provided comparison workflow varies seeds by rows.

### A14 — Anima discussion #93: multiple characters

- URL: https://huggingface.co/circlestone-labs/Anima/discussions/93
- Language: English
- Class: `PRACTICAL` / official-hosted community discussion, not author model-card FACT
- Scope: Anima preview/current family multi-character behavior
- Used for:
  - some pairs work across seeds while other pairs fail despite both individual characters working;
  - descriptions may rescue some pairs;
  - strong franchise/concept tokens can bleed into other actors;
  - lowering strong concept weight can reduce bleed but degrade identity, showing a trade-off;
  - underscore/alternate surface forms may affect response in particular pair formats.
- Do not infer:
  - universal weight value or guaranteed description recipe.

### A15 — Anima discussion #120: separate character tagging

- URL: https://huggingface.co/circlestone-labs/Anima/discussions/120
- Language: English
- Class: `PRACTICAL`
- Scope: Anima multi-character attribute binding
- Used for:
  - attribute swaps remain under richer prompts;
  - 3–4 characters with individual position/outfit/object bindings can exceed practical Prompt-only capacity;
  - less-popular characters may disappear in multi-character cases;
  - community conclusion points toward regional prompting for severe cases.

### A16 — Anima discussion #73 / #136: trigger drift

- URLs:
  - https://huggingface.co/circlestone-labs/Anima/discussions/73
  - https://huggingface.co/circlestone-labs/Anima/discussions/136
- Language: English
- Class: `PRACTICAL`, corroborated by exact model-card Gelbooru preference
- Used for:
  - an older/Gelbooru spelling can activate an artist concept where current Danbooru spelling does not;
  - current canonical correctness does not prove model trigger optimality.
- Do not infer:
  - all aliases are stronger than canonical;
  - dictionary canonical should be rewritten.

### A17 — NoobAI XL 1.1 model card

- Model: `Laxhar/noobai-XL-1.1`
- URL: https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
- Language: English
- Class: `FACT_EXACT_MODEL`
- Used for:
  - CFG 5–6 / Steps 25–30 / Euler a / ~1024² family;
  - native caption order places Special before General;
  - official negative list includes `bad hands`, `mutated hands` but does not establish broad anatomy/count negatives as mandatory.

---

## Japanese practical evidence

### A18 — Anima multiple-character natural-language test

- Title: `【Anima×ComfyUI】複数キャラクターを描き分けられる？自然言語で検証したら予想外の結果に！`
- URL: https://note.com/hkmclab/n/n7611426be16a
- Language: Japanese
- Class: `CONTROLLED_PRACTICAL` for the shown prompt progression; not a global benchmark
- Used for:
  - light tag-only two-character attributes can separate;
  - adding more/local attributes eventually mixes them;
  - character/position-scoped natural-language grouping can improve separation in the shown tests;
  - small ornament/local attributes remain more leak-prone;
  - later 3-person cases using Detailer are confounded and cannot certify Prompt-only scalability.

### A19 — Anima hand-role prompting test

- Title: `Anima系モデルで手を崩れにくくするプロンプトの書き方`
- URL: https://note.com/sepiablue/n/nc4944ea5fb53
- Language: Japanese
- Class: `PRACTICAL`
- Used for:
  - explicit hand visibility plus different concrete roles/contact for the two hands is a promising support bundle;
  - author still observes failure/seed dependence.
- Do not infer:
  - one phrase alone caused the improvement;
  - deterministic left/right hand binding.

### A20 — WAI v17 + Forge Couple practical guide

- Title: `【SDXL/Illustrious】Forge Coupleの使い方とプロンプト記法の基礎まとめ`
- URL: https://note.com/nonb0716/n/n02ce7117ac22
- Environment stated by author:
  - ForgeNeo
  - WAI-illustrious-SDXL v17
  - Forge Couple v7.0.7
- Language: Japanese; translated Korean/English views also available on Note
- Class: `PRACTICAL`
- Used for:
  - real failure classes: color bleed, missing second actor, mirrored output;
  - regional prompting effectiveness remains dependent on checkpoint raw composition ability;
  - region/global count and prompt partitioning can themselves introduce bleed/conflicts;
  - over-separating one character into too many disconnected prompt pieces can weaken coherence.
- Do not infer:
  - Forge Couple solves every relation/binding task;
  - exact weights/regions generalize to all checkpoints.

### A21 — Anima position test

- Title: `【検証】AIイラスト 複数キャラの位置指定｜Animaは拡張機能なしで左右に並べられる`
- URL: https://note.com/stray_dog0012/n/n6576baad72c1
- Language: Japanese
- Class: `PRACTICAL`
- Used only as additional evidence that explicit natural-language actor/position grouping can work in some Anima cases.
- Lower weight than official card + broader test set because it is a single practical workflow.

---

## Chinese / multilingual corroboration

### A22 — Chinese CVF mirror for ConceptSplit

- URL: https://openaccess.thecvf.com.cn/content/ICCV2025/html/Lim_ConceptSplit_Decoupled_Multi-Concept_Personalization_of_Diffusion_Models_via_Token-wise_Adaptation_ICCV_2025_paper.html
- Language: Chinese
- Class: `FACT_GENERAL` mirror of peer-reviewed ICCV paper
- Purpose:
  - multilingual accessibility/corroboration; not independent experimental evidence from the English original.

### A23 — Korean-rendered Note view of WAI v17 Forge Couple article

- URL: https://note.com/nonb0716/n/n02ce7117ac22?hl=ko
- Language: Korean rendering of Japanese source
- Class: same source as A20, not independent evidence
- Purpose:
  - do not double-count translated/mirrored pages as multiple confirmations.

---

## Source discipline decisions from Batch A

1. Mirrors/translations count as the same underlying evidence unless they contain independent experiments.
2. Official-hosted model discussions are useful practical evidence but do not become author FACT unless the model author/team explicitly states the claim.
3. General T2I papers establish failure mechanisms/risk plausibility, not exact WAI/NoobAI/Anima support recipes.
4. One-seed practical examples can prove a failure/counterexample exists, but cannot establish a success probability.
5. Postprocessed/regional/Detailer-assisted examples must be marked as assisted/confounded when interpreting Prompt-only ability.
6. Current Danbooru frequency is not a substitute for known model training exposure.
7. Lower-quality generic “best prompt”/giant Negative lists were deliberately excluded from durable conclusions.
