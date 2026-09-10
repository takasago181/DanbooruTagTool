# 10 — Complete File Map

Status: `ALL_CURRENT_KNOWLEDGE_FILES_CLASSIFIED_V3 / FOCUSED_ENRICHMENT_ADDED`

This maps the current `docs/knowledge/` assets into the canonical topic catalog and current management layer.

## Canonical catalog

- `00_FOUNDATIONS_AND_AUTHORITY.md`
- `01_MODEL_FAMILIES.md`
- `02_PROMPT_SUPPORT_AND_COMPOSITION.md`
- `03_FAILURE_TESTING_AND_EVALUATION.md`
- `04_TOOLS_POSTPROCESS_AND_LORA.md`
- `05_HARD_NICHE_ADULT_GENERATION.md`
- `06_SEMANTICS_ALIAS_TRIGGER.md`
- `07_WAI17_LOCAL_TEST_PROFILE.md`
- `08_SOURCE_AND_SITE_AUDITS.md`
- `09_OPEN_QUESTIONS_AND_HOLD.md`
- `10_FILE_MAP.md`

## Current management layer

These files are cross-topic controls, not a second genre taxonomy.

| File | Role |
|---|---|
| `../current/README.md` | current management entry / precedence / workflow |
| `../current/KNOWLEDGE_GOVERNANCE.md` | Claim schema, IDs, SOURCE_CLASS/STATUS/SCOPE/VALIDATION rules |
| `../current/CLAIM_REGISTRY.csv` | **current claim verdict source of truth** |
| `../current/ASSET_INVENTORY.md` | requested knowledge-domain inventory and file locations |
| `../current/VERSION_FRESHNESS_LEDGER.csv` | version/source freshness and recheck ledger |
| `../current/HOLD_CONFLICT_REGISTER.md` | current unresolved/conflicting knowledge |
| `../current/LEGACY_MAP.md` | old document -> category/Claim/role |
| `../current/LABEL_MIGRATION_MAP.md` | old mixed labels -> new field interpretation |
| `../current/CURRENT_QUICK_REFERENCE.md` | 30–60 second overview; never verdict authority |
| `../current/READING_ROUTES.md` | task-specific 3–5 file reading routes |
| `../current/SELF_AUDIT_20260909.md` | GitHub-only recovery audit for this organization pass |

## Root knowledge files

| File | Primary catalog | Role |
|---|---|---|
| `CURRENT_PRODUCT_GOAL_20260909.md` | 00 | current product goal evidence/context |
| `PRODUCT_GOAL_EVOLUTION_20260909.md` | 00 | original -> current evolution/history |
| `KNOWLEDGE_REASSESSMENT_20260909.md` | 00 / 09 | legacy KEEP/HOLD/REJECT reassessment evidence |
| `GENERATION_KNOWLEDGE_CORPUS.md` | cross-cutting | durable consolidated corpus/evidence |
| `GENERATION_KNOWLEDGE_SOURCES.md` | 08 | source registry/provenance |
| `GENERATION_KNOWLEDGE_INDEX.md` | cross-cutting | historical coverage/backlog index |
| `KNOWLEDGE_HANDOFF_CURRENT_20260909.md` | cross-cutting | restart handoff |
| `KNOWLEDGE_CATALOG.md` | cross-cutting | master human-readable topic entry |

## Focused research files

| File | Primary catalog | Secondary |
|---|---|---|
| `AIARTRECIPE_SITE_AUDIT_20260909.md` | 08 | 05 |
| `AIARTRECIPE_PRACTICAL_FINDINGS_20260909.md` | 08 | 03 / 05 |
| `BATCH_A_FALSE_ASSUMPTION_PREVENTION_20260909.md` | 03 | 02 / 04 |
| `BATCH_A_SOURCES_20260909.md` | 08 | 03 |
| `BATCH_B_MINIMUM_SUFFICIENT_PROMPT_20260909.md` | 02 | 03 |
| `BATCH_B_SOURCES_20260909.md` | 08 | 02 |
| `BATCH_C_EVIDENCE_RELIABILITY_20260909.md` | 03 | 09 |
| `BATCH_C_SOURCES_20260909.md` | 08 | 03 |
| `BATCH_D_RUNTIME_PROMPT_REPRO_COMPOSITION_20260910.md` | 02 / 03 | 04 / 08 |
| `DANBOORU_WIKI_SEMANTIC_AUDIT_20260909.md` | 06 | 08 |
| `E621_WIKI_SEMANTIC_TRIGGER_AUDIT_20260909.md` | 06 | 01 / 08 |
| `HF_MODEL_DISCUSSIONS_AUDIT_20260909.md` | 01 / 08 | 03 |
| `SOURCE_AUTHORITY_MATRIX_20260909.md` | 08 | 00 / 06 |
| `TOSHIAKI_WIKI_SITE_AUDIT_20260909.md` | 08 | 04 |
| `TOSHIAKI_WIKI_PRACTICAL_FINDINGS_20260909.md` | 04 / 08 | 02 / 03 |
| `TOSHIAKI_WIKI_COVERAGE_MAP_20260909.md` | 08 | — |
| `WAI17_LOCAL_ENV_TEST_BASELINE_20260909.md` | 07 | 01 / 03 / 04 / 09 |
| `HARD_FETISH_GENERATION_INDEX_20260909.md` | 05 | 03 |
| `HARD_FETISH_ANAL_INSERTION_20260909.md` | 05 | 03 |
| `HARD_FETISH_BDSM_RESTRAINT_20260909.md` | 05 | 03 |
| `HARD_FETISH_MACHINE_DEVICE_20260909.md` | 05 | 03 / 04 |
| `HARD_FETISH_TENTACLE_FANTASY_20260909.md` | 05 | 03 |
| `HARD_FETISH_FLUID_EXCRETION_20260909.md` | 05 | 03 |
| `HARD_FETISH_RARE_EXTREME_20260909.md` | 05 | 02 / 03 / 09 |
| `HARD_FETISH_MODEL_FAMILY_MATRIX_20260909.md` | 05 / 01 | 09 |
| `HARD_FETISH_COMPOSITE_FAILURE_MATRIX_20260909.md` | 05 / 03 | — |
| `HARD_FETISH_SOURCES_20260909.md` | 08 | 05 |

Detailed old-document-to-Claim absorption mapping:
`../current/LEGACY_MAP.md`

## Layer roles

- `current/CLAIM_REGISTRY.csv` = current verdict/status/scope/validation authority
- `current/HOLD_CONFLICT_REGISTER.md` = current uncertainty detail
- `current/VERSION_FRESHNESS_LEDGER.csv` = freshness/version identity
- `catalog/` = current readable explanation by topic
- `research/` = detailed evidence/provenance/history
- `GENERATION_KNOWLEDGE_CORPUS.md` = durable cross-topic synthesis
- `GENERATION_KNOWLEDGE_SOURCES.md` = source registry
- `KNOWLEDGE_HANDOFF_CURRENT_20260909.md` = restart state

## Maintenance

`research/source -> Claim Registry -> category explanation if needed -> HOLD/version if needed -> file map -> downstream handoff when requested -> #44 checkpoint`.

Do not create a parallel genre numbering scheme.
