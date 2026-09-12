# KNOWLEDGE Research Backlog — 2026-09-13

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `POST_PROMPT_MERGE_GAP_AUDIT / PRIORITIZED`

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

The largest imbalance after the 2026-09-12 beginner-first product reset is that **generation/evaluation knowledge is much deeper than knowledge for understanding an existing Prompt and explaining tag roles to a beginner**.

Therefore the next enrichment pass should not simply create more WAI17 A/B hypotheses. First strengthen knowledge that supports:

`理解 -> 発見 -> 選択 -> 出力`

without turning KNOWLEDGE into a second UI-taxonomy owner or an automatic Prompt optimizer.

## Priority P0 — do next, no broad image testing required

### K-RB-01 Existing-Prompt surface/type interpretation

Goal:
Distinguish what a pasted Prompt contains before trying to explain it.

Research / document boundaries for:
- canonical Danbooru-like tags
- approved Alias/historical surfaces
- quality/style/artist/meta/rating-like tokens
- model-specific trigger tokens
- free natural-language fragments
- emphasis/weight syntax
- `BREAK` / runtime control syntax
- LoRA/embedding/control-like syntax where visible in Prompt text
- unknown/unclassified tokens

Why high priority:
This directly supports the current v1 entry point: understanding an existing Prompt. Current knowledge has runtime preprocessing facts, but not a beginner-facing interpretation model for mixed Prompt surfaces.

Guardrail:
Classification must not silently claim that every token is a Danbooru canonical tag.

### K-RB-02 Prompt semantic-role decomposition for explanation

Goal:
Create a non-destructive explanation vocabulary for existing Prompt components.

Candidate roles:
- subject/count/identity
- appearance/body
- clothing/accessory
- expression/gaze
- pose/action/contact/relation
- camera/frame/viewpoint/orientation/visibility
- environment/background/time/weather
- lighting/color/style
- quality/meta/model-trigger
- negative-conditioning role

Why high priority:
Lets the tool explain "what this part is doing" without automatically rewriting the Prompt.

Guardrail:
This is an explanation schema, not canonical semantic authority and not automatic optimization.

### K-RB-03 Beginner-safe Japanese explanation rules

Goal:
Define how technical/canonical tag meaning becomes short Japanese explanation/search assistance without semantic drift.

Research:
- literal meaning vs practical visual meaning
- ambiguous/polysemous tags
- body-site / actor-target / ownership wording
- count-sensitive wording
- implication vs synonym wording
- historical Alias/rename presentation
- when a one-line Japanese gloss is insufficient and detail should be shown

Why high priority:
Current knowledge strongly protects canonical authority, but has relatively little positive guidance for producing understandable Japanese explanations.

Guardrail:
Japanese wording never overwrites canonical identity.

### K-RB-04 Danbooru tag-type/category meaning for Prompt comprehension

Goal:
Document the practical difference between tag/category types a beginner may encounter in Prompt text, including at minimum general, character, copyright/series, artist/style-like surfaces, and meta/rating/quality-related concepts where applicable.

Questions:
- which are Danbooru semantic categories vs model-specific Prompt conventions?
- which should be explained as identity/context/style rather than ordinary visual attribute tags?
- which may be valid Prompt surfaces but are not normal General/Special dictionary entries?

Why high priority:
Prevents a pasted Prompt from being explained as if every comma-separated item were the same kind of tag.

### K-RB-05 Alias / implication / related / co-occurrence beginner distinction

Goal:
Turn the existing authority separation into a concrete beginner explanation model.

Need concise rules/examples for:
- Alias = same identity mapping
- implication = hierarchy/entailment, not synonym
- related/co-occurrence = association, not identity
- Japanese search synonym = UX aid, not canonical Alias
- model trigger alternative = generation surface, not semantic rewrite

Why high priority:
Directly supports discovery and prevents misleading candidate explanations.

### K-RB-06 Unknown / unsupported Prompt token handling

Goal:
Define what KNOWLEDGE can safely say when a pasted token cannot be matched confidently.

Possible states:
- exact canonical
- exact approved Alias
- known model/runtime syntax
- plausible free phrase
- ambiguous collision
- unknown

Need rules for not hallucinating a meaning, not fuzzy-matching too aggressively, and preserving raw text for user control.

Why high priority:
Essential for trust in the "understand existing Prompt" flow.

## Priority P1 — high value after P0

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
- whether rating tokens are training/prompt surfaces or semantic content

Image testing only if a specific effectiveness claim is promoted.

### K-RB-08 Artist/style tag and style-trigger semantics

Goal:
Clarify the boundary among Danbooru artist identity, model-learned artist/style trigger, style LoRA, generic style adjectives, and visual-style descriptions.

Why useful:
Artist/style surfaces frequently occur in anime-generation Prompts but current corpus treats them only indirectly.

Guardrail:
Artist identity and model style effect are separate claims.

### K-RB-09 Existing Prompt conflict/explanation knowledge

Goal:
Describe detectable conceptual tensions to the user without auto-removing them.

Examples:
- mutually competing frame/viewpoint tags
- count contradictions
- duplicate Alias/canonical surfaces
- positive/Negative overlap
- actor/target ambiguity
- broad+specific relation

This should support "可能性を説明する" rather than "勝手に修正する".

### K-RB-10 Prompt ordering / grouping evidence by exact model family

Goal:
Audit what is actually documented about ordering/grouping for WAI17, Illustrious, NoobAI and Anima.

Known strong anchor:
NoobAI native caption order.

Need to avoid turning community habits into universal grammar.

Image testing is optional and only for unresolved effectiveness claims.

### K-RB-11 Negative Prompt knowledge split: semantics vs model convention

Goal:
Expand beyond the general "Negative is active" principle.

Separate:
- quality/artifact negatives
- anatomy negatives
- target-overlap semantic negatives
- count/anatomy-changing hazards
- model-family recommended baseline
- legacy long-negative recipes

First pass should be source/author research; WAI17 ON/OFF tests remain HOLD until explicitly chosen.

### K-RB-12 Source freshness / model-card recheck pass

Goal:
Refresh authoritative source status after the current organization pass.

Targets:
- WAI17 author card
- Forge Neo upstream/local identity
- NoobAI EPS/V-Pred cards
- Anima card/profile guidance
- Danbooru Alias/Implication authority pages
- evaluator model cards

Why:
`VERSION_FRESHNESS_LEDGER.csv` currently marks most external/versioned sources as recheck-required.

## Priority P2 — advanced generation research; useful but not current blocker

### K-RB-13 WAI17 canonical vs Alias/historical trigger response

Maps to current HOLD `H-K-001`.
Requires pinned local checkpoint/runtime before promotion-critical tests.

### K-RB-14 WAI17 relation/body-site/topology/device/tentacle/count ceiling

Maps to `H-K-003` through `H-K-007`.
High future value for niche generation, but already well-defined as HOLD; do not duplicate prose research before controlled tests are justified.

### K-RB-15 Broad + specific and support-interference tests on WAI17

Maps to `H-K-002` / `K-SUPPORT-004`.
Use only selected representative cases, not a full corpus sweep.

### K-RB-16 LoRA x Special/support interaction

Maps to `H-K-009`.
First pin LoRA identity/base/weight and local runtime state. Keep base capability separate from adapter-assisted capability.

### K-RB-17 Prompt-only -> regional/control/inpaint escalation threshold

Maps to `H-K-016`.
Research should define a bounded stopping/escalation policy rather than proving that every target must work Prompt-only.

### K-RB-18 Evaluator coverage/calibration refresh

Maps to `H-K-014` / `H-K-015`.
Useful when a concrete image-evaluation task returns. Vocabulary breadth alone is not enough; relation/topology judgement remains human or specialized-evaluator territory unless validated.

## Explicitly deprioritized for now

Do **not** spend the next research pass on:
- another broad "what is WAI/Illustrious/NoobAI/Anima" overview — already covered
- another generic minimum-sufficient Prompt essay — already covered
- another broad niche/hard taxonomy — already deep
- more generic evidence-level methodology — already covered
- broad Stage10 A/B planning without a concrete question
- full 100k+ Danbooru ontology/taxonomy work
- General 30,629 taxonomy ownership — Issue #64 owns the actual browse taxonomy

## Recommended execution order

First enrichment sequence:

1. K-RB-01 Existing-Prompt surface/type interpretation
2. K-RB-02 Prompt semantic-role decomposition
3. K-RB-03 Beginner-safe Japanese explanation rules
4. K-RB-04 Danbooru tag-type/category meaning
5. K-RB-05 Alias/implication/related distinction
6. K-RB-06 Unknown token handling

Then consolidate those into current Claims/Catalog only after evidence review.

Second sequence:
K-RB-07 -> 08 -> 09 -> 10 -> 11 -> 12.

P2 should be pulled only when a concrete generation-effectiveness question needs it.

## Completion rule for each research theme

A theme is not complete merely because prose was collected.

For each substantial batch:
1. preserve source/evidence with version/date
2. separate semantic authority / author guidance / runtime fact / community practice
3. add/update Claim IDs only for durable statements
4. keep unresolved items HOLD/CANDIDATE
5. update relevant Catalog explanation
6. update freshness ledger when versioned sources are involved
7. register new research file in `catalog/10_FILE_MAP.md`
8. add #44 checkpoint

No new knowledge automatically changes DEV/product behavior.
