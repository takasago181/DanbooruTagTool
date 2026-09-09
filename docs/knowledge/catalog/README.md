# KNOWLEDGE Catalog Directory

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `CANONICAL_TOPIC_INDEX_V2`

This directory is the **current topic-organized reading layer** for the persistent generation-knowledge corpus.

Top-level map:
`../KNOWLEDGE_CATALOG.md`

Research originals under `../research/` remain preserved as evidence/provenance. The Catalog is a curated summary layer, not a replacement for source evidence.

## Canonical topic order

0. `00_FOUNDATIONS_AND_AUTHORITY.md` — current goal, evidence classes, authority boundaries
1. `01_MODEL_FAMILIES.md` — WAI17 / Illustrious / NoobAI / Anima
2. `02_PROMPT_SUPPORT_AND_COMPOSITION.md` — minimum-sufficient Prompt, support roles, anti-support, composition
3. `03_FAILURE_TESTING_AND_EVALUATION.md` — diagnosis, paired A/B, E0–E3, evaluator/tagger limits
4. `04_TOOLS_POSTPROCESS_AND_LORA.md` — Forge/Hires/ADetailer/img2img/Control/regional/LoRA
5. `05_HARD_NICHE_ADULT_GENERATION.md` — hard/niche adult structural classes and audit knowledge
6. `06_SEMANTICS_ALIAS_TRIGGER.md` — Danbooru canonical, Alias, implication, e621/Gelbooru, trigger drift
7. `07_WAI17_LOCAL_TEST_PROFILE.md` — current user WAI17/Forge Neo baseline and test ladder
8. `08_SOURCE_AND_SITE_AUDITS.md` — source hierarchy, AIArtRecipe, Toshiaki Wiki, HF, Danbooru/e621
9. `09_OPEN_QUESTIONS_AND_HOLD.md` — unresolved claims and test-required backlog
10. `10_FILE_MAP.md` — complete mapping of current root/research files into the topics above

This numbering is canonical. Do not create another overlapping genre-numbering scheme.

## Restore flow

For a fresh KNOWLEDGE chat:
1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #44 latest comments
4. `../KNOWLEDGE_HANDOFF_CURRENT_20260909.md`
5. `../KNOWLEDGE_CATALOG.md`
6. relevant topic file(s) here
7. detailed research originals only when evidence/provenance is needed

## Layer model

- **Handoff** — current lane state and immediate priority
- **Catalog** — current organized conclusions by topic
- **Corpus** — cross-topic durable synthesis
- **Sources** — source registry/provenance
- **Research** — detailed investigations, evidence, limitations and historical reasoning

## Invariants

Never collapse:
- canonical meaning
- Alias identity
- implication/hierarchy
- related/co-occurrence relations
- model-specific trigger surface
- generation support
- UI Japanese/search wording
- Prompt-only capability
- LoRA/control/postprocess-assisted capability
- evaluator/human verdict.

Unknown or insufficiently tested behavior stays `HOLD / TEST_REQUIRED / IMAGE_TEST_REQUIRED`.

## Current WAI17 shortcut

`07_WAI17_LOCAL_TEST_PROFILE.md -> 01_MODEL_FAMILIES.md -> 03_FAILURE_TESTING_AND_EVALUATION.md -> 02_PROMPT_SUPPORT_AND_COMPOSITION.md -> 05_HARD_NICHE_ADULT_GENERATION.md if relevant -> 09_OPEN_QUESTIONS_AND_HOLD.md`

## Maintenance

For substantial research:
1. preserve a focused `research/` original;
2. update the relevant Catalog topic;
3. register the new source file in `10_FILE_MAP.md`;
4. update handoff only when current priorities/state changed;
5. leave a #44 checkpoint.