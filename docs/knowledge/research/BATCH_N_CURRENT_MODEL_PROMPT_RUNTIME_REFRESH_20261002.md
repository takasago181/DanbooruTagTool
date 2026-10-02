# BATCH_N — Current model / Prompt / runtime refresh — 2026-10-02

Owner: Issue #44 `KNOWLEDGE:#44`  
Branch: `knowledge/generation-corpus`  
Scope: NoobAI XL, Anima, WAI Illustrious v17, Forge Neo, Forge Couple  
Mode: source refresh + durable claim extraction; no production behavior change

## Why this batch

The 2026-10-01 textbook identified remaining gaps around model-specific weighting, Noob binding/count/alias response, Anima tag-vs-hybrid behavior, Negative ON/OFF effects, and LoRA interaction. This batch rechecks current upstream documentation and promotes only facts that upstream sources directly support. Image-dependent performance questions remain HOLD.

## Current primary sources rechecked

1. Anima official model card  
   https://huggingface.co/circlestone-labs/Anima
2. NoobAI XL 1.1 EPS author model card  
   https://huggingface.co/Laxhar/noobai-XL-1.1/blob/main/README.md
3. NoobAI XL V-Pred 1.0 author model card  
   https://huggingface.co/Laxhar/noobai-XL-Vpred-1.0/blob/main/README.md
4. WAI Illustrious SDXL v17 author mirror/model card  
   https://huggingface.co/LyliaEngine/waiIllustriousSDXL_v170
5. Forge Neo upstream  
   https://github.com/Haoming02/sd-webui-forge-classic/tree/neo
6. Forge Couple upstream  
   https://github.com/Haoming02/sd-forge-couple

Checked: 2026-10-02 JST.

## Durable findings promoted

### Anima Prompt weighting
The current author card says weighting works but requires higher weight than normally used for SDXL and gives `(chibi:2)` as an example.

Interpretation:
- ACCEPT as exact-family author guidance.
- DO NOT turn `2` into a universal optimum.
- Old SDXL weight heuristics remain only hypotheses when moved to Anima.

### Anima tag dropout
The author card states that random tag dropout was used during training and that not every relevant tag must be included.

Interpretation:
- ACCEPT that exhaustive visual-property enumeration is not required by the documented training regime.
- This does not prove that shorter is always better; semantic workload/conflict rules still apply.

### Anima natural language and multi-character prompting
The author recommends descriptive pure-natural-language Prompts of roughly two sentences or more, permits arbitrary tag/NL mixing, and explicitly recommends naming a character plus describing basic appearance. This is described as especially important for multiple characters.

Interpretation:
- ACCEPT as author guidance.
- This strengthens the practical rationale for explicit identity+appearance binding.
- It does NOT close K-MODEL-ANIMA-004; tag-only vs hybrid relation success remains an image-test question.

### Anima profile priors
Current author guidance characterizes:
- Base: maximum flexibility/diversity/style adherence; plain/neutral default without artist/quality guidance.
- Aesthetic: stronger consistency and higher-quality default style.
- Turbo: CFG 1, 8–12 steps, increased stability/strong default style, reduced diversity.

Interpretation:
- ACCEPT profile-level behavior as author guidance.
- Do not pool seeds/settings across profiles as if profile only changed speed.

### Anima LoRA training
Current author guidance says:
- train LoRAs on Anima Base;
- do not train the LLM adapter;
- rank-32 LoRA can start around LR 2e-5 and then be adjusted.

Reason given by the author: the LLM adapter processes text embeddings before the diffusion model, has outsized image influence, contains substantial knowledge, and is easy to degrade.

Interpretation:
- ACCEPT as Anima-specific training guidance.
- `2e-5` is a starting point, not an optimum.
- This does not close K-LORA-002, which concerns project-specific inference interaction.

### NoobAI XL V-Pred
Current author card still specifies:
- CFG 4–5;
- 28–35 steps;
- Euler sampling;
- around SDXL 1MP resolution.
It also states that training uses native tags plus natural-language captioning and that V-Pred is distinct from EPS.

Interpretation:
- ACCEPT exact V-Pred operational guidance.
- Do not infer Anima-like natural-language relation performance from caption presence alone.
- Noob binding/count/alias HOLDs stay open.

### Forge Couple
Current upstream says:
- Forge Neo and Anima are supported;
- total subject count should still be prompted inside every region;
- extension effectiveness depends on checkpoint composition understanding;
- Subject Replacement can replace total-count expressions with singular subject terms within tiles;
- Dynamic Prompts and other Prompt preprocessors may break the Couple separator/common Prompts;
- compatibility mode can disable Couple during Hires Fix.

Interpretation:
- ACCEPT runtime behavior.
- Evidence identity must record whether Couple was active on base and Hires passes.
- Assisted success still does not prove plain-checkpoint binding.

### Forge Neo
Current upstream documents:
- LLLite ControlNet for SDXL / Anima;
- Region ControlNet for Anima.

Interpretation:
- ACCEPT runtime availability.
- Keep these in assisted-control evidence lanes.

### WAI Illustrious v17 freshness
The current official Hugging Face file page exposes SHA256:
`f116b0c78ff441467b0cdc8f1936e1ed18ea31e9997c7b132b1b8db533f0bd04`.

This pins the current remote artifact but does not prove the user's local installed checkpoint is the same file. H-K-017 therefore remains open for local hash/runtime commit identity.

## Questions deliberately NOT promoted

The following still require controlled image evidence:
- exact Anima weight thresholds by concept/profile;
- Noob EPS canonical-vs-alias-vs-historical/e621 trigger response;
- Noob exact actor/body-site/count ceiling;
- Anima tag-only vs concise-hybrid relation success rate;
- Negative OFF/ON effect on unusual anatomy/count targets;
- LoRA × target/support interference;
- cross-family LoRA portability/reliability;
- whether Forge Couple materially improves a specific hard target relative to a carefully minimized plain Prompt.

## Registry changes

Added:
- K-MODEL-ANIMA-007 through K-MODEL-ANIMA-011
- K-LORA-003
- K-MODEL-NOOB-006
- K-TOOL-008 through K-TOOL-010

No existing HOLD was closed solely from documentation.

## Product boundary

This batch changes KNOWLEDGE only. It does not:
- modify production `data/**`;
- auto-insert support tags;
- rewrite user Prompts;
- change canonical Danbooru meaning;
- promote assisted-control capability into Prompt-only capability;
- authorize generation recipes as universal defaults.
