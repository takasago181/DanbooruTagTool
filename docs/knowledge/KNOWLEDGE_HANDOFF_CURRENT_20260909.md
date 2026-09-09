# KNOWLEDGE Current Handoff

Owner: Issue #44 `KNOWLEDGE:#44`

Date: 2026-09-09

Status: `HANDOFF_READY_V1`

## Purpose

This is the compact restart point for the persistent DanbooruTagTool KNOWLEDGE lane. A future chat should be able to recover the current state without relying on conversational memory.

This file does not replace `CURRENT_STATE.md`, `PERMANENT_RULES.md`, Issue #44 or the detailed corpus. It tells the next KNOWLEDGE chat what to read and what the current research emphasis is.

## Restore order

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #44 latest comments
4. `docs/knowledge/KNOWLEDGE_HANDOFF_CURRENT_20260909.md` (this file)
5. `docs/knowledge/GENERATION_KNOWLEDGE_INDEX.md`
6. `docs/knowledge/CURRENT_PRODUCT_GOAL_20260909.md`
7. `docs/knowledge/PRODUCT_GOAL_EVOLUTION_20260909.md`
8. `docs/knowledge/KNOWLEDGE_REASSESSMENT_20260909.md`
9. relevant focused research files
10. `docs/knowledge/GENERATION_KNOWLEDGE_CORPUS.md`
11. `docs/knowledge/GENERATION_KNOWLEDGE_SOURCES.md`

## Team identity / boundaries

- TEAM_ID: `KNOWLEDGE:#44`
- branch: `knowledge/generation-corpus`
- lane status: ongoing persistent corpus
- current user instruction: keep independence from other active teams unless an explicit handoff is requested
- runtime product remains non-LLM
- KNOWLEDGE does not directly rewrite production dictionary data
- KNOWLEDGE does not own #32 validation verdicts
- KNOWLEDGE does not authorize Stage10 production A/B
- unresolved behavior stays `HOLD / TEST_REQUIRED / IMAGE_TEST_REQUIRED`.

## Current product-goal baseline

The original Special-first purpose remains valid but the success criterion has expanded.

Current target:
`short Japanese/English intent -> correct Special Core Dictionary candidate(s) -> minimum useful support/structure -> model-family-appropriate canonical-English Prompt -> safe failure diagnosis -> fewer unnecessary generation iterations`

Primary goal: reduce manual trial-and-error without sacrificing semantic correctness, model-family scope, traceability or uncertainty handling.

## Evidence discipline

Use:
- `FACT_EXACT_MODEL`
- `FACT_GENERAL`
- `CONTROLLED_PRACTICAL`
- `PRACTICAL`
- `COMMUNITY`
- `HOLD`
- `REJECT`.

Language does not determine evidence rank. Japanese/English/Chinese/Korean and other useful sources are allowed; authority and experimental control determine rank.

Canonical meaning, Alias identity, model trigger surface, generation support and UI Japanese are separate layers.

## Major completed research blocks

### Core reassessment
- `CURRENT_PRODUCT_GOAL_20260909.md`
- `PRODUCT_GOAL_EVOLUTION_20260909.md`
- `KNOWLEDGE_REASSESSMENT_20260909.md`

### Generation methodology
- `research/BATCH_A_FALSE_ASSUMPTION_PREVENTION_20260909.md`
- `research/BATCH_A_SOURCES_20260909.md`
- `research/BATCH_B_MINIMUM_SUFFICIENT_PROMPT_20260909.md`
- `research/BATCH_B_SOURCES_20260909.md`
- `research/BATCH_C_EVIDENCE_RELIABILITY_20260909.md`
- `research/BATCH_C_SOURCES_20260909.md`

Key durable ideas:
- relation/ownership/body-site != component presence
- semantic support can become anti-support generation-wise
- unary success does not guarantee composite success
- Negative is an active semantic intervention
- minimum sufficient != shortest Prompt
- use one-variable changes and predetermined paired seeds
- one seed is case evidence, not reliability
- preserve `TIE / UNCLEAR / BOTH_FAIL / BLOCKED`
- postprocess/control/LoRA must be separated from base Prompt success.

### Hard / niche adult generation
- `research/HARD_FETISH_GENERATION_INDEX_20260909.md`
- `research/HARD_FETISH_ANAL_INSERTION_20260909.md`
- `research/HARD_FETISH_BDSM_RESTRAINT_20260909.md`
- `research/HARD_FETISH_MACHINE_DEVICE_20260909.md`
- `research/HARD_FETISH_TENTACLE_FANTASY_20260909.md`
- `research/HARD_FETISH_FLUID_EXCRETION_20260909.md`
- `research/HARD_FETISH_RARE_EXTREME_20260909.md`
- `research/HARD_FETISH_MODEL_FAMILY_MATRIX_20260909.md`
- `research/HARD_FETISH_COMPOSITE_FAILURE_MATRIX_20260909.md`
- `research/HARD_FETISH_SOURCES_20260909.md`

Structural classes include body-site, binding relation, restraint topology, device relation, exact count, nonhuman appendage relation, anatomy-changing and composite-hard cases.

### Japanese practical-source audits
- `research/AIARTRECIPE_SITE_AUDIT_20260909.md`
- `research/AIARTRECIPE_PRACTICAL_FINDINGS_20260909.md`
- `research/TOSHIAKI_WIKI_SITE_AUDIT_20260909.md`
- `research/TOSHIAKI_WIKI_PRACTICAL_FINDINGS_20260909.md`
- `research/TOSHIAKI_WIKI_COVERAGE_MAP_20260909.md`

AIArtRecipe is useful as a practical failure-observation corpus, not canonical authority.
Toshiaki Wiki is useful as Japanese operations/practical knowledge, with legacy and exact-model claims explicitly separated.

### Semantic / source-authority audits
- `research/DANBOORU_WIKI_SEMANTIC_AUDIT_20260909.md`
- `research/E621_WIKI_SEMANTIC_TRIGGER_AUDIT_20260909.md`
- `research/HF_MODEL_DISCUSSIONS_AUDIT_20260909.md`
- `research/SOURCE_AUTHORITY_MATRIX_20260909.md`

Authority summary:
- Danbooru current Wiki / active Alias / implication = primary Danbooru semantic identity sources
- e621 = secondary nonhuman/anatomy/fetish vocabulary and NoobAI alternate-trigger/exposure source, never silent Danbooru canonical replacement
- exact model author card = highest exact-model generation authority
- author discussion reply > general community discussion
- GitHub official docs = highest tool-behavior authority
- papers = strongest general-mechanism evidence
- practical sites = hypothesis/failure evidence, not canonical truth.

## Model-family state

### WAI Illustrious v17
Current first test target and local priority.

Read first:
`research/WAI17_LOCAL_ENV_TEST_BASELINE_20260909.md`

Strong exact knowledge:
- Forge Neo recommended by author
- Euler a
- Steps 15–30
- CFG 5–7
- VAE integrated
- source examples 1024×1344 / author asks for original area larger than 1024×1024
- minimal quality and Negative baselines
- too many quality/aesthetic tags and overly long Negative can hurt quality
- Hires may repair limbs; therefore base vs Hires evidence must be separated.

Local immediate baseline:
- Euler a / 25 steps / CFG 5
- 1024-class generation, 1024×1344 preferred first portrait test when appropriate
- fixed paired seed
- Hires OFF
- ADetailer OFF
- LoRA OFF
- regional/ControlNet OFF until they are the tested variable.

WAI17 HOLD/test backlog:
- canonical vs Alias activation
- rare Special exposure
- broad+specific
- actor-target/body-site relation ceiling
- restraint topology
- device functional relation
- tentacle ownership
- simultaneous Special/count breakpoints
- visibility support effect
- unusual anatomy/count Negative ON/OFF
- LoRA x Special/support
- Prompt-only -> assisted-control threshold.

### Illustrious XL baseline
Strong general family context; do not flatten exact derivative behavior into family truth.

### NoobAI XL 1.1 EPS
Strong exact settings/caption-order knowledge; Danbooru+e621 exposure. Exact rare/current trigger and hard relation behavior remain test-required.

### NoobAI V-Pred 1.0
Prediction regime and settings must remain separate from EPS.

### Anima
Strong official formatting/tag/NL/tag-dropout knowledge; relation-heavy tag-only vs concise-hybrid remains an important controlled-test lane. Community reports support binding/identity-bleed risk but are not exact success rates.

## Evaluator state

Current principle:
- WD EVA02 = common/unary baseline only
- rare Special absence from WD output is not image failure
- Kagami-24k and CL Tagger v2 are stronger wide-vocabulary candidates
- full WD/Kagami/CL Special2788 coverage comparison is queued only after dictionary finalization
- no global threshold across semantic classes or model families
- relation/topology/body-site/source-destination often requires decomposed or human/specialized review.

## Current knowledge-source hierarchy

For a claim, prefer:
1. exact author/model/tool primary source
2. current Danbooru semantic authority when claim is about Danbooru identity
3. primary research for general mechanism
4. controlled exact-model practical evidence
5. versioned practical evidence
6. community observation
7. unresolved = HOLD.

## Current highest-value next work

Immediate focus is WAI17 because the user plans to test with that environment first.

Priority order:
1. preserve the local WAI17 baseline exactly
2. choose representative Special classes including rare and relation-heavy cases
3. test base Prompt-only behavior before postprocess/control
4. run controlled support ablations
5. test Negative collisions for unusual anatomy/count cases
6. learn canonical/Alias/alternate-trigger behavior under exact WAI17
7. record all local controlled outcomes back into #44 under pinned context
8. only later generalize to NoobAI/Anima after WAI17 evidence is stable.

## Handoff readiness

At this checkpoint, the KNOWLEDGE lane is considered **HANDOFF_READY** if the next chat reads this file plus the files above.

What is intentionally not 'known': exact image-test outcomes not yet performed. Those gaps are explicitly preserved instead of being reconstructed from memory or guessed.