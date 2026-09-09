# 01 — Model-Family Knowledge

## WAI Illustrious v17 — current first priority

Exact author facts:
- recommended software: Forge Neo
- Sampler: Euler a
- Steps: 15–30
- CFG: 5–7
- integrated VAE
- original size larger than 1024×1024 area; author examples 1024×1344
- minimal quality example: `masterpiece, best quality, amazing quality`
- minimal Negative example: `bad quality, worst quality, worst detail, sketch, censor`
- author warns too many quality/aesthetic tags and overly long Negative can reduce quality / blur
- Hires example: 1.5 upscale, 20 Hires steps, Anime6B upscaler, denoise 0.35–0.5
- v17 Hires may repair limbs/hands/feet, so base and Hires results are separate evidence states.

Current WAI17 unknowns remain image-test questions: rare Special activation, canonical-vs-Alias, relation/body-site/topology ceiling, broad+specific, unusual-anatomy Negative effects, multi-Special/count breakpoints, LoRA interaction.

## Illustrious XL baseline

Useful family-level facts:
- Booru-oriented captioning with richer caption context than simple independent tags alone
- critical composition tags can conflict; mutually incompatible frame/viewpoint concepts are a Prompt contradiction before a Special failure
- derivative checkpoints must be revalidated; generic Illustrious advice is not exact WAI truth.

## NoobAI XL 1.1 EPS

Exact author facts:
- CFG 5–6
- Steps 25–30
- Euler a
- around SDXL 1MP sizes
- native caption organization: `count -> character -> series -> artists -> special -> general -> other`
- trained using Danbooru + e621 native tag captions

Implications:
- Special-before-General has exact-model structural support
- e621 is relevant to alternate trigger/exposure hypotheses
- current canonical spelling may differ from training-era surface
- rare/current Alias response and relation behavior remain test-required.

## NoobAI V-Pred 1.0

Keep separate from EPS for inference claims:
- CFG 4–5
- Steps 28–35
- Euler
- different prediction regime

Never pool EPS and V-Pred results as if they were one model profile.

## Anima

Exact family guidance:
- Base / Aesthetic / Turbo are meaningfully different
- tags, natural language, and mixed Prompt are supported
- lowercase and spaces generally preferred; Gelbooru form may be preferred when Danbooru/Gelbooru differ
- random tag dropout means every related tag need not be injected
- multiple characters benefit from explicit identity/basic appearance context
- Aesthetic does not require quality tags in the same way as older SDXL habits
- Turbo uses very different low-CFG/low-step inference and must be separated.

Practical risk:
- natural language does not eliminate binding/identity bleed
- left/right, multi-actor ownership, strong-concept bleed and long-prose concept pressure remain failure modes
- tag-only vs concise factual relation sentence is a controlled-test lane, not a universal rule.

## Cross-family rules safe to transfer

Safe as general warnings:
- presence != relation success
- negative conditioning is active
- composition load matters
- rare concepts are seed-sensitive
- LoRA/postprocess/control are confounders
- evaluator coverage must be checked.

Do not transfer without evidence:
- exact Prompt order
- exact quality/Negative lists
- camera tag placement
- weight values
- canonical/Alias preference
- natural-language superiority
- simultaneous-Special ceiling.

## Primary originals

- `../GENERATION_KNOWLEDGE_CORPUS.md`
- `../research/HARD_FETISH_MODEL_FAMILY_MATRIX_20260909.md`
- `../research/HF_MODEL_DISCUSSIONS_AUDIT_20260909.md`
- `../research/WAI17_LOCAL_ENV_TEST_BASELINE_20260909.md`