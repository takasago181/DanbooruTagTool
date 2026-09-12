# KNOWLEDGE Research Backlog — 2026-09-13

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `P0_PROMPT_UNDERSTANDING_RESEARCH_COMPLETE / P1_NEXT`

This file is a planning/backlog layer only. It does **not** override `CLAIM_REGISTRY.csv`, create product requirements, or promote HOLD/CANDIDATE claims.

## Audit conclusion

Current KNOWLEDGE is already strong in:
- model-family separation for WAI17 / Illustrious / NoobAI / Anima
- Prompt support / anti-support / minimum-sufficient principles
- failure diagnosis and evidence discipline
- niche/hard structural decomposition (binding/body-site/count/topology/device/tentacle/fluid)
- Prompt-only vs assisted-control/postprocess separation
- evaluator limitations and compositional-evaluation methodology
- Danbooru/e621 semantic authority and Alias/trigger separation
- source/site authority rules

The largest imbalance after the 2026-09-12 beginner-first product reset was that generation/evaluation knowledge was much deeper than knowledge for understanding an existing Prompt and explaining tag roles to a beginner.

The first P0 enrichment pass now covers that gap at research level.

## P0 — research complete

### K-RB-01 Existing-Prompt surface/type interpretation — COMPLETE

Durable research:
`../research/BATCH_E_EXISTING_PROMPT_SURFACE_CLASSIFICATION_20260913.md`

Covered:
- canonical/Alias surfaces
- runtime syntax
- LoRA/hypernetwork
- textual inversion
- Dynamic Prompts/template syntax
- natural-language text
- unknown/ambiguous state
- wrapper vs inner semantic payload

### K-RB-02 Prompt semantic-role decomposition — COMPLETE

Durable research:
`../research/BATCH_F_PROMPT_SEMANTIC_ROLE_DECOMPOSITION_20260913.md`

Covered:
- subject/count
- character/source/artist identity
- appearance/body
- clothing/accessory
- expression/gaze
- pose/gesture
- action/relation
- object
- camera/frame/viewpoint
- environment/background
- time/weather
- light/color
- style/quality/model convention
- meta/technical
- unknown/multirole

### K-RB-03 Beginner-safe Japanese explanation rules — COMPLETE

Durable research:
`../research/BATCH_G_BEGINNER_SAFE_JAPANESE_EXPLANATION_20260913.md`

Covered:
- display label vs explanation vs search synonym
- canonical English traceability
- actor/target/body-site/count preservation
- state/object/action distinctions
- ambiguity/unknown wording
- proper noun handling
- runtime syntax explanation
- repair threshold reusing #36 policy

### K-RB-04 / 05 / 06 — COMPLETE

Durable research:
`../research/BATCH_H_DANBOORU_CATEGORY_RELATION_UNKNOWN_HANDLING_20260913.md`

Covered:
- General / Character / Copyright / Artist / Meta meaning
- category vs semantic role vs generation effect separation
- Alias / implication / related / co-occurrence / Japanese synonym / model trigger distinction
- exact-first interpretation
- unknown/ambiguous preservation
- search permissive vs interpretation conservative

## P0 consolidation state

Research package is complete and registered in `catalog/10_FILE_MAP.md`.

The combined durable principles are ready for a future Claim Registry / Catalog consolidation pass, but **no Claim Registry row is silently promoted by this backlog file**.

Reason for consolidating together:
E/F/G/H deliberately separate surface type, semantic role, Japanese explanation, and authority/uncertainty. Adding fragmented Claims before the set was complete would create duplication and overloaded labels.

## Priority P1 — next knowledge enrichment

### K-RB-07 Quality / rating / aesthetic / score-like token families across model families

Goal:
Separate semantic tags from quality/meta conventions and document family/version-specific behavior.

Cover where evidence exists:
- WAI17
- Illustrious derivatives
- NoobAI EPS/V-Pred
- Anima profiles

Questions:
- official recommended quality surfaces
- deprecated/legacy habits
- excessive quality-token competition
- rating/score surfaces: semantic category vs training/prompt convention

Image testing only if a specific effectiveness claim is promoted.

### K-RB-08 Artist/style tag and style-trigger semantics

Goal:
Clarify the boundary among Danbooru Artist identity, model-learned artist/style trigger, style LoRA, generic style adjectives, and visual-style descriptions.

Guardrail:
Artist identity and model style effect are separate claims.

### K-RB-09 Existing Prompt conflict/explanation knowledge

Goal:
Describe conceptual tensions without auto-removing them.

Examples:
- competing frame/viewpoint tags
- count contradictions
- duplicate Alias/canonical surfaces
- Positive/Negative overlap
- actor/target ambiguity
- broad+specific relation

Output should explain `可能性` rather than silently rewrite.

### K-RB-10 Prompt ordering / grouping evidence by exact model family

Goal:
Audit documented ordering/grouping for WAI17, Illustrious, NoobAI and Anima.

Known strong anchor:
NoobAI native caption order.

Do not turn community habits into universal grammar.

### K-RB-11 Negative Prompt knowledge split: semantics vs model convention

Separate:
- quality/artifact negatives
- anatomy negatives
- target-overlap semantic negatives
- count/anatomy-changing hazards
- model-family recommended baseline
- legacy long-negative recipes

First pass = source/author research.

### K-RB-12 Source freshness / model-card recheck pass

Refresh:
- WAI17 author card
- Forge Neo upstream/local identity
- NoobAI EPS/V-Pred
- Anima profiles
- Danbooru authority pages
- evaluator model cards

`VERSION_FRESHNESS_LEDGER.csv` remains the freshness authority.

## Priority P2 — advanced generation research; not current blocker

### K-RB-13 WAI17 canonical vs Alias/historical trigger response
Maps to `H-K-001`.

### K-RB-14 WAI17 relation/body-site/topology/device/tentacle/count ceiling
Maps to `H-K-003` through `H-K-007`.

### K-RB-15 Broad + specific and support-interference tests on WAI17
Maps to `H-K-002` / `K-SUPPORT-004`.

### K-RB-16 LoRA x Special/support interaction
Maps to `H-K-009`.

### K-RB-17 Prompt-only -> regional/control/inpaint escalation threshold
Maps to `H-K-016`.

### K-RB-18 Evaluator coverage/calibration refresh
Maps to `H-K-014` / `H-K-015`.

## Explicitly deprioritized

Do not spend the next pass on:
- another broad WAI/Illustrious/NoobAI/Anima overview
- another generic minimum-sufficient Prompt essay
- another broad niche/hard taxonomy
- more generic evidence-level methodology
- broad Stage10 A/B planning without a concrete question
- full 100k+ Danbooru ontology
- General 30,629 taxonomy ownership (#64 owns it)

## Recommended next execution order

P1:
`K-RB-07 -> 08 -> 09 -> 10 -> 11 -> 12`

P2 only when a concrete generation-effectiveness question needs it.

## Completion rule for each research theme

For each substantial batch:
1. preserve source/evidence with version/date
2. separate semantic authority / author guidance / runtime fact / community practice
3. add/update Claim IDs only for durable statements
4. keep unresolved items HOLD/CANDIDATE
5. update relevant Catalog explanation when promoted
6. update freshness ledger when versioned sources are involved
7. register new research file in `catalog/10_FILE_MAP.md`
8. add #44 checkpoint

No new knowledge automatically changes DEV/product behavior.
