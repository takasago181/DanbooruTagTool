# Stage10 PROMPT semantic authority — Danbooru / e621

最終更新: 2026-09-09  
Owner: PROMPT / Issue #5  
Status: semantic evidence ledger. **Not production specification.**

## Purpose

hard-target Promptで使う概念について、
- canonical meaning
- alias / implication
- broad vs specific
- body-site / relation / object granularity
をmodel behaviorから分離して記録する。

## Danbooru role

Danbooru/Safebooru wiki is the primary semantic authority for DanbooruTagTool canonical concepts.

Useful official surfaces:
- Help:Tags — tag formatting and basic mechanics
- Howto:Get Started — synonyms/aliases and tag-group usage
- Tag Group:Groups — character count and sex/position groups
- Tag Group:Character Count — count semantics
- Howto:Tag Checklist — explicit image elements are separated into body parts / sexual actions / positions / themes
- individual wiki pages for exact meaning and see-also relationships

## Key semantic findings

### Broad theme != render-critical detail

Danbooru taxonomy naturally separates broad concepts from specific components.

Examples observed:
- `urethral insertion` is a broad insertion concept; `sounding`, `urethral fingering`, `urethral penetration` are more specific branches
- `bead sex machine` defines a specific machine subtype rather than generic machinery
- `liquid tentacles` defines an appendage material/type subtype
- character count, sex act and sexual position are separate tag-group dimensions

PROMPT implication:
- broad theme alone should not be assumed sufficient for hard-target realization
- `[ACT]`, `[SITE]`, `[OBJECT]`, `[POSE]`, `[RELATION]` should remain separable internal roles

### Alias / implication is semantic, not model-equivalence evidence

Example:
- `sounding` implicates `urethral_insertion`
- `urethral_object_push` is aliased to `urethral_insertion`

PROMPT implication:
- semantic hierarchy may guide candidate generation
- it does **not** prove the checkpoint responds equally to alias/canonical/broad/specific strings
- model response remains Stage10 test material

## e621 role

Use e621 only as `SUPPLEMENTAL_NONHUMAN_TAXONOMY`.

Reason:
- NoobAI XL 1.1 official model card states training on Danbooru + e621
- e621 has richer non-human / creature / transformation / appendage / niche relationship taxonomy in some areas

Useful surfaces:
- Tag Group Index
- BDSM / Bondage groups
- anatomy and non-human body/appendage groups
- concept-specific wiki pages

## e621 cautions

- e621 taxonomy is not Danbooru canonical authority
- tags can carry fandom/furry-specific semantics not suitable for direct Danbooru mapping
- forum discussion is not stable wiki authority
- active tag cleanup / umbrella-tag disputes exist (e.g. egg-laying/oviposition-related discussions)
- a concept being present in e621 training data does not prove NoobAI will realize it reliably

## Cross-booru mapping states

Use one of:
- `SAME_MEANING_HIGH_CONFIDENCE`
- `NEAR_MEANING_DIFFERENT_SCOPE`
- `E621_ONLY_SUPPLEMENT`
- `DANBOORU_CANONICAL_ONLY`
- `ACTIVE_TAXONOMY_CONFLICT`
- `MODEL_RESPONSE_UNKNOWN`

Never silently convert one booru's taxonomy into another.

## Semantic audit checklist for hard targets

For every target concept, ask:
1. What is the exact Danbooru canonical meaning?
2. Is it broad or specific?
3. Does it imply another act/site/object concept?
4. Is it an alias or a true separate concept?
5. Does the tag encode relation or only theme?
6. Is body-site encoded or must support carry it?
7. Is object identity encoded or separate?
8. Does e621 add useful non-human distinctions?
9. Is any e621 mapping scope-shifted?
10. Has actual model response been tested?

## Product consequence

The tool should preserve provenance:
`user intent -> Japanese search term -> canonical/alias/semantic candidate -> resolved model-facing Prompt`

Semantic correctness and generation effectiveness must stay separate fields.

## Boundary

- This document does not modify #32 dictionary verdicts.
- No e621 term is promoted into Danbooru canonical identity here.
- No explicit production hard-target Prompt is defined.