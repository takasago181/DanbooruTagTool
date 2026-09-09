# KNOWLEDGE Library — Genre-Organized Entry Point

Owner: Issue #44 `KNOWLEDGE:#44`

Status: `CURATED_LIBRARY_V1`

## Purpose

This directory is the **curated, genre-organized reading layer** for the persistent KNOWLEDGE corpus.

The existing root corpus and `docs/knowledge/research/*` files are preserved as evidence/history. They are not deleted or silently rewritten. This library answers a different question: **what should a future KNOWLEDGE chat read by topic, in what order, and with what authority?**

## Read order

1. `01_PRODUCT_GOAL_AND_SCOPE.md`
2. `02_SEMANTICS_AND_SOURCE_AUTHORITY.md`
3. `03_MODEL_FAMILIES.md`
4. `04_PROMPT_SUPPORT_AND_PRUNING.md`
5. `05_FAILURE_DIAGNOSIS_AND_BINDING.md`
6. `06_HARD_NICHE_ADULT_GENERATION.md`
7. `07_TOOLS_CONTROL_AND_POSTPROCESS.md`
8. `08_EVALUATION_EVIDENCE_AND_TAGGERS.md`
9. `09_WAI17_LOCAL_TESTING.md`
10. `10_PRACTICAL_SITE_CORPUS.md`
11. `99_LEGACY_SOURCE_MAP.md` when provenance or old research details are needed.

## Evidence labels

- `FACT_EXACT_MODEL`
- `FACT_GENERAL`
- `CONTROLLED_PRACTICAL`
- `PRACTICAL`
- `COMMUNITY`
- `HOLD`
- `REJECT`

Language does not determine authority.

## Stable project boundaries

- Special-first product hierarchy remains the core.
- Runtime remains local and non-LLM.
- Canonical meaning, Alias identity, Japanese UI wording, model trigger, and generation support are separate layers.
- KNOWLEDGE is evidence/reference, not production-data or #32-verdict authority.
- Unknown behavior stays `HOLD / TEST_REQUIRED / IMAGE_TEST_REQUIRED`.
- Prompt-only, LoRA-assisted, regional/control-assisted, and postprocessed success are separate evidence lanes.

## Why the library exists

Before this reorganization, the corpus was mostly arranged by research chronology: Batch A/B/C, site audits, model investigations, and hard-fetish focused files. That preserved evidence well but made restart reading expensive.

The new organization separates:
- **curated current knowledge** in `library/`;
- **detailed evidence and investigations** in `research/`;
- **broad historical consolidated corpus** in `GENERATION_KNOWLEDGE_CORPUS.md`;
- **source registry** in `GENERATION_KNOWLEDGE_SOURCES.md`.

When a curated statement matters to a decision, follow its referenced source/research file and re-check version scope.