# KNOWLEDGE Catalog Directory

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `CANONICAL_TOPIC_INDEX_V3 / CLAIM_REGISTRY_LINKED`

This directory is the **current topic-organized human reading layer** for the persistent generation-knowledge corpus.

Top-level topic map:
`../KNOWLEDGE_CATALOG.md`

Current claim verdict source of truth:
`../current/CLAIM_REGISTRY.csv`

Current management entry point:
`../current/README.md`

Research originals under `../research/` remain preserved as evidence/provenance. The Catalog explains claims by topic; it does not override Claim Registry status/scope/validation.

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

## Restore flow

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #44 latest comments
4. `../KNOWLEDGE_HANDOFF_CURRENT_20260909.md`
5. `../current/CURRENT_QUICK_REFERENCE.md`
6. `../current/CLAIM_REGISTRY.csv`
7. relevant topic file(s) here
8. `../current/HOLD_CONFLICT_REGISTER.md` and/or `VERSION_FRESHNESS_LEDGER.csv` as needed
9. detailed research originals only when evidence/provenance is needed

## Layer model

- **Handoff** — lane state/restart
- **Current management** — current claim verdict/status/scope/validation, HOLD, freshness
- **Catalog** — readable topic explanations
- **Corpus** — cross-topic durable synthesis
- **Sources** — source registry/provenance
- **Research** — detailed evidence/history

## Invariants

Never collapse canonical meaning, Alias, implication, related/co-occurrence, UI Japanese, model trigger, generation support, Prompt-only capability, assisted-control/postprocess capability, or evaluator verdict.

Unknown behavior stays `HOLD` in the Claim Registry and HOLD register until its required validation is complete.

## Current WAI17 shortcut

`../current/CURRENT_QUICK_REFERENCE.md -> ../current/CLAIM_REGISTRY.csv (K-MODEL-WAI-*) -> 07_WAI17_LOCAL_TEST_PROFILE.md -> 01_MODEL_FAMILIES.md -> 03_FAILURE_TESTING_AND_EVALUATION.md -> 02_PROMPT_SUPPORT_AND_COMPOSITION.md -> ../current/HOLD_CONFLICT_REGISTER.md`

## Maintenance

`research/source -> claim review -> Registry update -> category explanation if needed -> HOLD/version update if needed -> downstream handoff if requested -> #44 checkpoint`.
