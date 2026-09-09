# 01 — Product Goal and Scope

## Current goal

`short Japanese/English intent -> correct Special Core Dictionary candidate(s) -> minimum useful support/structure -> model-family-appropriate canonical-English Prompt -> safe failure diagnosis -> fewer unnecessary generation iterations`

The project is not primarily a generic Danbooru browser, translation dictionary, maximal-tag generator, generic Stable Diffusion handbook, benchmark suite, or runtime LLM assistant.

## Stable invariants

- **Special-first:** one or more Specials form the Core Tag Set.
- Full Danbooru, co-occurrence, Semantic, Japanese search/display, LoRA, and control tools are supporting layers.
- Runtime is local and non-LLM.
- Final model-facing Prompt is English/canonical or justified model-trigger surface; Japanese UI wording is not semantic authority.
- Multiple Specials are first-class, including relation-heavy and conflict-prone combinations.
- More tags are not automatically better; target is a **minimum sufficient Prompt**.
- Model family/version/profile is part of every generation claim.
- `REVIEW / UNKNOWN / IMAGE_TEST_REQUIRED / assisted-control` are valid outcomes.

## Success criterion

The strongest product-level measure is reduction of manual trial-and-error **without sacrificing semantic correctness, traceability, model scope, or uncertainty handling**.

For any recommendation, ask:
1. Did we select the right Special meaning?
2. What is the smallest support set that actually helps this model?
3. Which plausible support is redundant or harmful?
4. What failure class explains the miss?
5. When should Prompt escalation stop?

## Knowledge priority

### P0
- semantic false-assumption prevention
- canonical vs model trigger
- actor-target/body-site/ownership binding
- rare/composite targets
- Negative collisions
- support-class confusion
- postprocess confounds

### P1
- minimum-sufficient support/pruning
- support conflict / anti-support
- prompt/concept density
- broad+specific
- family-specific ordering/weighting where evidence exists
- assisted-control escalation

### P2
- seed/sample reliability
- evaluator routing
- LoRA interaction
- local empirical-history rules

### Lower priority
Generic sampler micro-tuning and aesthetic polish unless they materially change Special success.

## Knowledge-team boundaries

KNOWLEDGE does not:
- decide Japanese display wording;
- redefine canonical meaning from model response;
- change #32 verdicts;
- write production data;
- choose production implementation architecture;
- introduce runtime LLM dependence;
- turn community practice into universal truth.

## Source files

Primary detailed anchors:
- `docs/knowledge/CURRENT_PRODUCT_GOAL_20260909.md`
- `docs/knowledge/PRODUCT_GOAL_EVOLUTION_20260909.md`
- `docs/knowledge/KNOWLEDGE_REASSESSMENT_20260909.md`
- Issue #44 body and latest checkpoints.