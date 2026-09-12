# KNOWLEDGE Catalog Directory

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `CANONICAL_TOPIC_INDEX_V4 / CLAIM_REGISTRY_LINKED / PROMPT_MERGED`

This directory is the **current topic-organized human reading layer** for persistent DanbooruTagTool knowledge.

Top-level topic map:
`../KNOWLEDGE_CATALOG.md`

Current claim verdict source of truth:
`../current/CLAIM_REGISTRY.csv`

Current management entry point:
`../current/README.md`

Research originals under `../research/` remain preserved as evidence/provenance. The Catalog explains claims by topic; it does not override Claim Registry status/scope/validation.

Current product goal is owned by main `docs/PRODUCT_GOAL_LOCK.md`. The separate PROMPT team was retired on 2026-09-12; Prompt/generation-effectiveness topics remain within this KNOWLEDGE catalog rather than forming another lane/taxonomy.

## Canonical topic order

0. `00_FOUNDATIONS_AND_AUTHORITY.md`
1. `01_MODEL_FAMILIES.md`
2. `02_PROMPT_SUPPORT_AND_COMPOSITION.md`
3. `03_FAILURE_TESTING_AND_EVALUATION.md`
4. `04_TOOLS_POSTPROCESS_AND_LORA.md`
5. `05_HARD_NICHE_ADULT_GENERATION.md`
6. `06_SEMANTICS_ALIAS_TRIGGER.md`
7. `07_WAI17_LOCAL_TEST_PROFILE.md`
8. `08_SOURCE_AND_SITE_AUDITS.md`
9. `09_OPEN_QUESTIONS_AND_HOLD.md`
10. `10_FILE_MAP.md`

This numbering is canonical. Do not create another overlapping genre-numbering scheme.
The `current/` directory is a cross-topic metadata/control layer, not a second genre taxonomy.

## Knowledge horizons

The same catalog contains two different product horizons:

- **v1-supporting:** semantics, authority, Japanese understanding/search, discovery/traceability
- **future/advanced generation:** Prompt composition, support/anti-support, model behavior, failure diagnosis, tools/evaluators, controlled generation evidence

The horizon is determined by claim scope/product relevance/validation state, not by a separate team.

## Restore flow

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #44 latest body/comments
4. `docs/PRODUCT_GOAL_LOCK.md`
5. `../KNOWLEDGE_HANDOFF_CURRENT_20260909.md`
6. `../current/CURRENT_QUICK_REFERENCE.md`
7. `../current/CLAIM_REGISTRY.csv`
8. relevant topic file(s) here
9. `../current/HOLD_CONFLICT_REGISTER.md` and/or `VERSION_FRESHNESS_LEDGER.csv` as needed
10. detailed research originals only when evidence/provenance is needed

## Layer model

- **Handoff** — lane state/restart
- **Current management** — current claim verdict/status/scope/validation, HOLD, freshness
- **Catalog** — readable topic explanations
- **Corpus** — cross-topic durable synthesis
- **Sources** — source registry/provenance
- **Research** — detailed evidence/history

## Invariants

Never collapse canonical meaning, Alias, implication, related/co-occurrence, UI Japanese, model trigger, generation support, Prompt-only capability, assisted-control/postprocess capability, evaluator verdict, or product adoption.

Unknown behavior stays `HOLD` in the Claim Registry and HOLD register until its required validation is complete.

Knowledge evidence does not automatically become v1 runtime behavior.

## Current WAI17 shortcut

Use only when image-dependent generation knowledge is actually relevant:

`../current/CURRENT_QUICK_REFERENCE.md -> ../current/CLAIM_REGISTRY.csv (K-MODEL-WAI-*) -> 07_WAI17_LOCAL_TEST_PROFILE.md -> 01_MODEL_FAMILIES.md -> 03_FAILURE_TESTING_AND_EVALUATION.md -> 02_PROMPT_SUPPORT_AND_COMPOSITION.md -> ../current/HOLD_CONFLICT_REGISTER.md`

## Maintenance

`research/source -> claim review -> Registry update -> category explanation if needed -> HOLD/version update if needed -> narrow validation only when required -> DEV/product handoff if authorized -> #44 checkpoint`.
