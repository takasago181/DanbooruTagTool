# KNOWLEDGE Research Backlog — 2026-09-13

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `P0_P1_COMPLETE / P2_ON_DEMAND`

This file is a planning/backlog layer only. It does **not** override `CLAIM_REGISTRY.csv`, create product requirements, or promote HOLD/CANDIDATE claims.

## Current conclusion

The major post-2026-09-12 knowledge imbalance has now been addressed.

Previously, generation/evaluation research was much deeper than knowledge for:

`理解 -> 発見 -> 選択 -> 出力`

The completed P0 + P1 work now covers both:

1. **beginner-facing Prompt understanding knowledge**
2. **model-specific Prompt-convention boundaries needed to explain what the user pasted**

without turning KNOWLEDGE into an automatic Prompt optimizer or a second UI-taxonomy owner.

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

`VERSION_FRESHNESS_LEDGER.csv` was refreshed on 2026-09-13 for current model/evaluator/Danbooru/Forge-Neo public sources.

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
Use only when a concrete advanced-assistance feature needs an escalation policy.

### K-RB-18 Evaluator coverage/calibration
Maps to `H-K-014` / `H-K-015`.
Source freshness is complete; project-specific calibration/coverage remains future evidence work.

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

There is no need to start P2 automatically.

While core DEV continues #64, useful KNOWLEDGE work can now be one of:

1. **current-product support:** inspect #42/#34 future needs against the new Prompt-understanding Claims and prepare evidence only where a concrete gap exists;
2. **knowledge maintenance:** source freshness / new model-version changes / new high-quality practical evidence;
3. **advanced pull:** take one P2 HOLD only when the user or an adopted feature specifically needs it.

For each future substantial batch:
1. preserve source/evidence with version/date
2. separate semantic authority / author guidance / runtime fact / community practice
3. update Claim IDs only for durable statements
4. keep unresolved items HOLD/CANDIDATE
5. update Catalog only when needed
6. update freshness ledger for versioned sources
7. register research in `catalog/10_FILE_MAP.md`
8. add #44 checkpoint

No new knowledge automatically changes DEV/product behavior.
