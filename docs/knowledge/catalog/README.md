# KNOWLEDGE Catalog Directory

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `CANONICAL_GENRE_MAP`

This directory is the **current topic-organized reading layer** for the persistent generation-knowledge corpus.

The authoritative top-level map is:
`../KNOWLEDGE_CATALOG.md`

Research originals under `../research/` remain preserved as evidence/provenance. The catalog is a curated summary layer, not a replacement for source evidence.

## Canonical genre order

1. `01_PRODUCT_GOAL_AND_GOVERNANCE.md` — current product goal, scope, team authority
2. `02_MODEL_FAMILIES.md` — WAI17 / Illustrious / NoobAI / Anima
3. `03_PROMPT_AND_SUPPORT_DESIGN.md` — minimum-sufficient Prompt, support roles, anti-support, Negative
4. `04_FAILURE_DIAGNOSIS_AND_COMPOSITION.md` — binding, count, visibility, multi-Special, failure classes
5. `05_HARD_NICHE_ADULT_GENERATION.md` — hard/niche adult structural classes and audit knowledge
6. `06_SEMANTICS_ALIAS_TRIGGER.md` — Danbooru canonical, Alias, implication, e621/Gelbooru, trigger drift
7. `07_EVALUATION_AND_EXPERIMENTS.md` — E0–E3 evidence, paired seeds, evaluator/tagger routing
8. `08_TOOLS_POSTPROCESS_AND_CONTROLS.md` — Forge Neo, Hires, ADetailer, LoRA, ControlNet, regional tools
9. `09_SOURCE_AUTHORITY_AND_SITE_AUDITS.md` — source hierarchy, AIArtRecipe, Toshiaki Wiki, HF, Danbooru/e621
10. `10_HOLD_AND_NEXT_RESEARCH.md` — unresolved claims, WAI17-first test backlog, promotion rules
11. `11_FILE_MAP.md` — complete mapping of root/research files into the genres above

## Restore flow

For a fresh KNOWLEDGE chat:

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #44 latest comments
4. `../KNOWLEDGE_HANDOFF_CURRENT_20260909.md`
5. `../KNOWLEDGE_CATALOG.md`
6. relevant genre file(s) here
7. detailed research originals only when evidence/provenance is needed

## Layer model

- **Handoff** — current lane state and immediate priority
- **Catalog** — current knowledge by genre
- **Research** — detailed investigations, source audits, limitations
- **Corpus** — broad long-term consolidated knowledge
- **Sources** — registry/provenance

## Invariants

Never collapse:
- canonical meaning
- Alias / implication / related relations
- model-specific trigger surface
- generation support
- UI Japanese/search wording
- Prompt-only capability
- LoRA/control/postprocess-assisted capability
- evaluator/human verdict.

Unknown or insufficiently tested behavior stays `HOLD / TEST_REQUIRED / IMAGE_TEST_REQUIRED`.