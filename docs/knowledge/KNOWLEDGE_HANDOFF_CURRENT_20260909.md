# KNOWLEDGE Current Handoff

Owner: Issue #44 `KNOWLEDGE:#44`

Date: 2026-09-09

Status: `HANDOFF_READY_V3 / TOPIC_CATALOG_FINALIZED`

## Purpose

This is the compact restart point for the persistent DanbooruTagTool KNOWLEDGE lane. A future chat must recover current knowledge from GitHub without relying on conversational memory.

## Restore order

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #44 latest comments
4. `docs/knowledge/KNOWLEDGE_HANDOFF_CURRENT_20260909.md` (this file)
5. `docs/knowledge/KNOWLEDGE_CATALOG.md`
6. relevant `docs/knowledge/catalog/*.md`
7. detailed `docs/knowledge/research/*` only when evidence/provenance is needed
8. `docs/knowledge/GENERATION_KNOWLEDGE_CORPUS.md`
9. `docs/knowledge/GENERATION_KNOWLEDGE_SOURCES.md`
10. `docs/knowledge/GENERATION_KNOWLEDGE_INDEX.md` for broad historical coverage/backlog context

## Team identity / boundaries

- TEAM_ID: `KNOWLEDGE:#44`
- branch: `knowledge/generation-corpus`
- lane: ongoing persistent corpus
- current user instruction: remain independent from other active teams unless an explicit handoff is requested
- runtime product remains local and non-LLM
- KNOWLEDGE does not directly rewrite production dictionary data
- KNOWLEDGE does not own #32 validation verdicts
- KNOWLEDGE does not authorize Stage10 production A/B
- unresolved behavior stays `HOLD / TEST_REQUIRED / IMAGE_TEST_REQUIRED`

## Current product goal

The original Special-first purpose remains valid; success criteria expanded.

`short Japanese/English intent -> correct Special Core Dictionary candidate(s) -> minimum useful support/structure -> model-family-appropriate canonical-English Prompt -> safe failure diagnosis -> fewer unnecessary generation iterations`

Primary product value: reduce manual trial-and-error while preserving semantic correctness, model-family scope, traceability and uncertainty.

## Canonical topic catalog

The knowledge corpus now uses one canonical taxonomy only:

0. `catalog/00_FOUNDATIONS_AND_AUTHORITY.md`
   - product goal, evidence classes, authority boundaries
1. `catalog/01_MODEL_FAMILIES.md`
   - WAI17 / Illustrious / NoobAI / Anima
2. `catalog/02_PROMPT_SUPPORT_AND_COMPOSITION.md`
   - minimum-sufficient Prompt, support, anti-support, multi-Special composition
3. `catalog/03_FAILURE_TESTING_AND_EVALUATION.md`
   - failure diagnosis, paired A/B, E0-E3, WD/Kagami/CL and evaluator limits
4. `catalog/04_TOOLS_POSTPROCESS_AND_LORA.md`
   - Hires, ADetailer, img2img, ControlNet, regional prompting, LoRA confounds
5. `catalog/05_HARD_NICHE_ADULT_GENERATION.md`
   - insertion/body-site, BDSM topology, machine/device, tentacle, fluid, rare/extreme, hard composites
6. `catalog/06_SEMANTICS_ALIAS_TRIGGER.md`
   - Danbooru canonical, Alias, implication, e621/Gelbooru, model trigger drift
7. `catalog/07_WAI17_LOCAL_TEST_PROFILE.md`
   - current user's WAI17/Forge Neo baseline and first controlled-test lane
8. `catalog/08_SOURCE_AND_SITE_AUDITS.md`
   - source hierarchy, AIArtRecipe, Toshiaki Wiki, HF, Danbooru/e621
9. `catalog/09_OPEN_QUESTIONS_AND_HOLD.md`
   - unresolved claims and image-test backlog
10. `catalog/10_FILE_MAP.md`
   - complete mapping of current root/research knowledge files into the topics above

`docs/knowledge/KNOWLEDGE_CATALOG.md` is the master map and `catalog/README.md` mirrors this same numbering. Do not create a second overlapping taxonomy.

## Corpus layers

- **Handoff** — current lane state / restart route / immediate priority
- **Catalog** — current organized conclusions by topic; default reading layer
- **Corpus** — durable cross-topic synthesis
- **Sources** — source registry/provenance
- **Research** — detailed investigation, source audit, limitations, historical evidence

Research originals are preserved. Reorganization must not erase provenance.

## Core durable knowledge

- model family/version/profile is part of every generation claim
- canonical identity, Alias, implication, UI Japanese, model trigger and generation support are separate layers
- presence is not relation success; actor/target/owner/body-site/source/destination/topology/count can fail independently
- minimum sufficient does not mean shortest; preserve semantic nucleus and remove redundant/competitive pressure
- semantically compatible support can become generation-harmful anti-support
- Negative Prompt is an active semantic intervention
- one seed is case evidence, not reliability
- postprocess/control/LoRA-assisted success is separate from Prompt-only capability
- machine evaluator vocabulary/semantic capability/calibration/OOD must be checked before confidence is interpreted
- unsupported/uncertain cases route to REVIEW/HOLD rather than forced PASS/FAIL

## Major completed research blocks

### Goal / reassessment
- `CURRENT_PRODUCT_GOAL_20260909.md`
- `PRODUCT_GOAL_EVOLUTION_20260909.md`
- `KNOWLEDGE_REASSESSMENT_20260909.md`

### Methodology
- Batch A: false-assumption prevention / diagnosis
- Batch B: minimum-sufficient Prompt / pruning
- Batch C: evidence reliability / evaluator boundaries

### Hard / niche adult generation
Focused research exists for:
- insertion/body-site/count
- BDSM/restraint topology
- machine/device functional relation
- tentacle/nonhuman ownership
- fluid/source-destination
- rare/anatomy-changing/extreme targets
- model-family differences
- composite-hard failure matrix

### Source/site audits
Completed:
- AIArtRecipe
- としあきdiffusion Wiki
- Danbooru Wiki semantic authority
- e621 alternate-vocabulary/NoobAI relevance
- Hugging Face model cards/discussions
- durable source-authority matrix

## Current first test target — WAI Illustrious v17

Read first:
`catalog/07_WAI17_LOCAL_TEST_PROFILE.md`

Current exact-author knowledge:
- Forge Neo recommended
- Euler a
- Steps 15–30
- CFG 5–7
- integrated VAE
- original area larger than 1024×1024 recommended; author examples 1024×1344
- short quality / Negative baseline
- too many quality/aesthetic tags and overly long Negative can reduce quality/blur
- Hires may repair limbs; base vs Hires must be separate evidence

Current local test baseline:
- Forge Neo
- WAI Illustrious v17
- Euler a
- Steps 25
- CFG 5
- portrait 1024×1344 first candidate when appropriate
- fixed paired seeds
- Hires OFF
- ADetailer OFF
- LoRA OFF
- regional/ControlNet OFF

Current WAI17 HOLD/test backlog:
- canonical vs Alias activation
- rare Special exposure
- broad+specific
- actor-target/body-site relation ceiling
- restraint topology
- machine/device functional relation
- tentacle source/ownership
- simultaneous Special/count breakpoints
- visibility-support effect
- unusual anatomy/count Negative ON/OFF
- LoRA × Special/support
- Prompt-only -> assisted-control threshold

## Evaluator state

- WD EVA02: common/unary baseline; rare Special absence is not image failure
- Kagami-24k: wider-vocabulary candidate; rare-tail reliability still separate
- CL Tagger v2: wide vocabulary + per-tag calibration/threshold/OOD information; not relation ground truth
- full WD/Kagami/CL Special2788 coverage comparison remains queued after dictionary finalization
- no global threshold across semantic classes/model families

## Maintenance rule

For substantial new research:
1. preserve the detailed research original
2. update the relevant canonical catalog topic
3. register the research file in `catalog/10_FILE_MAP.md`
4. update this handoff only when current priorities/state changed
5. leave a #44 checkpoint

## Handoff readiness

The KNOWLEDGE lane is **HANDOFF_READY_V3** when the next chat follows the restore order above.

Exact image-test outcomes that have not yet been performed are intentionally not invented; they remain explicit HOLD entries.