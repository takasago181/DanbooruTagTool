# KNOWLEDGE Research Backlog — 2026-09-13

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `P0_P1_COMPLETE / PRACTICAL_GENERATION_ENRICHMENT_NEXT / P2_ON_DEMAND`

This file is a planning/backlog layer only. It does **not** override `CLAIM_REGISTRY.csv`, create product requirements, or promote HOLD/CANDIDATE claims.

## Current conclusion

The major post-2026-09-12 beginner-facing knowledge imbalance has been addressed by P0 + P1.

A fresh practical-generation audit found a different imbalance:

- controlled generation / failure diagnosis = strong
- ordinary creative production from first draft to finished image = only partially consolidated

Durable audit:
`PRACTICAL_GENERATION_READINESS_AUDIT_20260913.md`

Therefore the next useful KNOWLEDGE work is **not broad P2 image testing**. First consolidate practical operation knowledge for the user's local generation workflow.

## P0 — COMPLETE / consolidated

### K-RB-01 Existing-Prompt surface/type interpretation
Research:
`../research/BATCH_E_EXISTING_PROMPT_SURFACE_CLASSIFICATION_20260913.md`

### K-RB-02 Prompt semantic-role decomposition
Research:
`../research/BATCH_F_PROMPT_SEMANTIC_ROLE_DECOMPOSITION_20260913.md`

### K-RB-03 Beginner-safe Japanese explanation rules
Research:
`../research/BATCH_G_BEGINNER_SAFE_JAPANESE_EXPLANATION_20260913.md`

### K-RB-04 / 05 / 06 Danbooru category / relation / unknown handling
Research:
`../research/BATCH_H_DANBOORU_CATEGORY_RELATION_UNKNOWN_HANDLING_20260913.md`

Key durable outcomes promoted to Claim Registry:
- classify surface type before assigning tag meaning
- comma-separated Prompt text is not automatically Danbooru identity
- interpretation is exact-first/conservative even when search is permissive
- tag category / explanation role / generation effect are separate
- conflict handling for beginner flow is `detect -> explain -> preserve -> user decides`

## P1 — COMPLETE / consolidated

### K-RB-07 Quality / rating / aesthetic / score-like surfaces
### K-RB-08 Artist identity / style / artist-trigger boundary
### K-RB-10 Prompt ordering/grouping by exact model family
### K-RB-11 Negative semantics vs exact-model recipes
### K-RB-12 source/model/evaluator freshness

Research:
`../research/BATCH_I_MODEL_PROMPT_CONVENTIONS_QUALITY_ARTIST_ORDER_NEGATIVE_FRESHNESS_20260913.md`

Durable conclusions:
- Danbooru `score:` / `rating:` metadata != model `score_*` / safety Prompt surfaces
- quality/rating/safety conventions are exact-model/profile scoped
- NoobAI and Anima have documented grouping/order; do not export their grammar universally
- Danbooru Artist identity != model artist/style trigger
- Anima `@artist` is model trigger syntax, not Danbooru canonical syntax
- Anima-Aesthetic is a distinct quality/score profile
- exact-model Negative recipes are guidance, not universal defaults

### K-RB-09 Existing Prompt conflict/explanation
Research:
`../research/BATCH_J_EXISTING_PROMPT_CONFLICT_EXPLANATION_20260913.md`

Covered:
- same-role composition tension
- count contradiction
- canonical/Alias duplicate identity
- implication/broad+specific overlap
- Positive/Negative semantic overlap
- actor/target/ownership ambiguity
- runtime/wrapper ambiguity
- fuzzy lexical collision

### Evaluator freshness completion
Research:
`../research/BATCH_K_EVALUATOR_FRESHNESS_RECHECK_20260913.md`

Important freshness finding:
- CL Tagger latest current `v2_01a` is provisional and may be updated in place under the same version label
- promotion-critical evidence must pin exact evaluator sub-version/retrieval identity

`VERSION_FRESHNESS_LEDGER.csv` was refreshed on 2026-09-13 for current model/evaluator/Danbooru/runtime public sources.

## PRACTICAL_GENERATION — NEXT

Audit verdict:
Current knowledge answers **"why did this fail?"** better than **"what should I do next to finish the picture?"**.

### PG-01 Daily generation loop
Build a durable first-draft -> finished-image workflow:
- choose exact model/profile
- author baseline
- exploratory seeds
- lock seed only for diagnosis
- fix composition/visibility before prompt piles
- LoRA one at a time
- Hires only after base structure is acceptable
- local repair with ADetailer/inpaint
- regional/control escalation only when needed
- preserve final infotext/preset

### PG-02 Exact-model quick-start cards
Create short practical cards for:
- WAI17
- NoobAI XL 1.1 EPS / V-Pred
- Anima Base / Aesthetic / Turbo

Each card should separate:
- author baseline
- Prompt convention
- resolution
- sampler/scheduler
- known practical cautions
- what remains unproven

### PG-03 Resolution + sampler/scheduler + seed workflow
Consolidate practical choices without inventing universal winners.

Needed:
- portrait / landscape / group / close-up aspect-ratio choices
- when crop/visibility means change resolution rather than Prompt
- sampler/scheduler exact-model defaults and safe variations
- random seed discovery -> fixed-seed diagnosis -> random exploration return
- batch/X-Y-Z use for bounded search

### PG-04 LoRA practical operations
Consolidate daily-use guidance:
- character/style/concept role
- trigger placement
- starting weight
- one-LoRA-first isolation
- stacking
- context leakage / overpowering diagnosis
- lower weight vs adding Negative
- interaction with Hires/ADetailer/regional

### PG-05 Hires + ADetailer finishing workflow
WAI17 author Hires recipe already exists and should be surfaced operationally.

Add:
- when to enable Hires
- denoise interpretation
- preserve vs redraw expectations
- Hires ordering with ADetailer
- ADetailer face/hand/person detector selection
- separate ADetailer Prompt/Negative boundaries
- damage/regression checks

### PG-06 img2img / inpaint repair ladder
Consolidate:
- whole-image revision vs local repair
- mask scope
- denoise bands as operational concepts
- when repeated inpaint should stop
- metadata preservation

### PG-07 Forge Couple / current ControlNet escalation
Current Forge Couple supports Basic / Advanced / Mask / Global Effect / Common Prompts and Anima.
Current Forge Neo documents LLLite / Union / Region ControlNet support.

Need:
- plain Prompt -> Basic Couple -> Advanced/Mask -> Control escalation
- total-subject-count handling
- global/background prompts
- Hires compatibility
- limitation: regional conditioning cannot create composition knowledge the checkpoint lacks

### PG-08 Forge Neo presets / X-Y-Z / infotext workflow
Current maintained Forge Neo includes current Preset, X/Y/Z Plot, updated infotext and related workflow features.

Need a repeatable daily iteration pattern instead of treating all batching as formal Stage10 evidence.

### PG-09 Local-runtime identity / performance
Only after exact local Forge Neo remote/commit is captured.

Scope may include:
- attention backend choices
- tiled VAE
- mixed precision
- torch.compile
- memory behavior
- current GPU-generation compatibility notes

Do not generalize runtime-performance advice without exact build/hardware scope.

## P2 — advanced generation research / pull only when needed

### K-RB-13 WAI17 canonical vs Alias/historical trigger response
Maps to `H-K-001`.
Requires pinned local checkpoint/runtime.

### K-RB-14 WAI17 relation/body-site/topology/device/tentacle/count ceiling
Maps to `H-K-003` through `H-K-007`.
Already well-defined as HOLD; next value comes from controlled image evidence, not more generic prose.

### K-RB-15 Broad + specific / support-interference tests
Maps to `H-K-002` / `K-SUPPORT-004`.
Use selected representative cases only.

### K-RB-16 LoRA x Special/support interaction
Maps to `H-K-009`.
Pin adapter/checkpoint/runtime identity before testing.

### K-RB-17 Prompt-only -> regional/control/inpaint escalation threshold
Maps to `H-K-016`.
Practical guidance can be documented first; promotion of exact effectiveness thresholds still requires controlled evidence.

### K-RB-18 Evaluator coverage/calibration
Maps to `H-K-014` / `H-K-015`.
Source freshness is complete; project-specific calibration/coverage remains future evidence work.

## Important source correction from practical audit

The freshness ledger previously treated `gi0baro/forge-neo` as current Forge Neo upstream.

Current maintained upstream is:
`Haoming02/sd-webui-forge-classic` branch `neo`.

The ledger has been corrected. The user's exact local remote/commit is still unpinned.

## Explicitly deprioritized

Do not create another broad pass on:
- WAI/Illustrious/NoobAI/Anima overview
- generic minimum-sufficient Prompt theory
- generic niche/hard taxonomy
- generic evidence methodology
- broad Stage10 A/B without a concrete question
- full 100k+ Danbooru ontology
- General 30,629 taxonomy (#64 owns it)

## Recommended next behavior

While core DEV continues #64, proceed with:

`PG-01 -> PG-02 -> PG-03 -> PG-04 -> PG-05 -> PG-06 -> PG-07 -> PG-08`

PG-09 only after exact local runtime identity is available.
P2 remains on-demand.

For each future substantial batch:
1. preserve source/evidence with version/date
2. separate semantic authority / author guidance / runtime fact / community practice
3. update Claim IDs only for durable statements
4. keep unresolved items HOLD/CANDIDATE
5. update Catalog only when needed
6. update freshness ledger for versioned sources
7. register research/audit in `catalog/10_FILE_MAP.md`
8. add #44 checkpoint

No new knowledge automatically changes DEV/product behavior.
