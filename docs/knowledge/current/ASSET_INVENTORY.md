# KNOWLEDGE Asset Inventory

Purpose: first-stage inventory of current KNOWLEDGE assets. This maps **knowledge topics -> files**, not current verdicts. For current verdicts use `CLAIM_REGISTRY.csv`.

## Topic inventory

| Knowledge area | Current readable entry | Main evidence / historical files |
|---|---|---|
| model official information | `../catalog/01_MODEL_FAMILIES.md` | `../GENERATION_KNOWLEDGE_SOURCES.md`, `../research/HF_MODEL_DISCUSSIONS_AUDIT_20260909.md`, `../research/WAI17_LOCAL_ENV_TEST_BASELINE_20260909.md` |
| model family differences | `../catalog/01_MODEL_FAMILIES.md` | `../research/HARD_FETISH_MODEL_FAMILY_MATRIX_20260909.md`, `../GENERATION_KNOWLEDGE_CORPUS.md` |
| Prompt grammar / caption structure | `../catalog/01_MODEL_FAMILIES.md`, `../catalog/02_PROMPT_SUPPORT_AND_COMPOSITION.md` | `../research/HF_MODEL_DISCUSSIONS_AUDIT_20260909.md`, `../../stages/STAGE_10_KNOWLEDGE_HANDOFF.md` |
| quality / meta / Negative | `../catalog/01_MODEL_FAMILIES.md`, `../catalog/07_WAI17_LOCAL_TEST_PROFILE.md` | `../GENERATION_KNOWLEDGE_SOURCES.md`, `../../stages/STAGE_10_KNOWLEDGE_HANDOFF.md`, Batch A/B research |
| natural language | `../catalog/01_MODEL_FAMILIES.md`, `../catalog/02_PROMPT_SUPPORT_AND_COMPOSITION.md` | `../research/HF_MODEL_DISCUSSIONS_AUDIT_20260909.md`, source IDs `S-ANIMA-*`, `S-JA-005/006` |
| canonical / Alias / Semantic / model trigger | `../catalog/06_SEMANTICS_ALIAS_TRIGGER.md` | `../research/DANBOORU_WIKI_SEMANTIC_AUDIT_20260909.md`, `../research/E621_WIKI_SEMANTIC_TRIGGER_AUDIT_20260909.md`, `../research/HF_MODEL_DISCUSSIONS_AUDIT_20260909.md` |
| Special2788-related knowledge | `../KNOWLEDGE_CATALOG.md`, `../catalog/05_HARD_NICHE_ADULT_GENERATION.md` | `../GENERATION_KNOWLEDGE_INDEX.md`, `../GENERATION_KNOWLEDGE_CORPUS.md`, `../../stages/STAGE_10_KNOWLEDGE_HANDOFF.md` |
| support knowledge | `../catalog/02_PROMPT_SUPPORT_AND_COMPOSITION.md` | `../research/BATCH_B_MINIMUM_SUFFICIENT_PROMPT_20260909.md`, `../research/BATCH_A_FALSE_ASSUMPTION_PREVENTION_20260909.md` |
| generation effectiveness | Registry + `../catalog/02_*`, `03_*` | Batch A/B/C; WAI17 local baseline |
| rare / long-tail | `../catalog/05_HARD_NICHE_ADULT_GENERATION.md`, `../catalog/09_OPEN_QUESTIONS_AND_HOLD.md` | `../research/HARD_FETISH_RARE_EXTREME_20260909.md`, evaluator sources |
| multi-Special | `../catalog/02_PROMPT_SUPPORT_AND_COMPOSITION.md`, `../catalog/05_HARD_NICHE_ADULT_GENERATION.md` | `../research/HARD_FETISH_COMPOSITE_FAILURE_MATRIX_20260909.md` |
| actor-target binding | `../catalog/03_FAILURE_TESTING_AND_EVALUATION.md`, `../catalog/05_HARD_NICHE_ADULT_GENERATION.md` | Batch A; hard-domain research; Anima HF discussion audit |
| body-site | `../catalog/05_HARD_NICHE_ADULT_GENERATION.md` | `HARD_FETISH_ANAL_INSERTION`, `BDSM_RESTRAINT`, `MACHINE_DEVICE` research |
| relation | `../catalog/03_FAILURE_TESTING_AND_EVALUATION.md`, `../catalog/05_HARD_NICHE_ADULT_GENERATION.md` | Batch A; hard-domain research |
| visibility / geometry | `../catalog/02_PROMPT_SUPPORT_AND_COMPOSITION.md`, `../catalog/03_FAILURE_TESTING_AND_EVALUATION.md` | Batch A/B; Stage10 knowledge handoff |
| multi-character | `../catalog/01_MODEL_FAMILIES.md`, `../catalog/03_FAILURE_TESTING_AND_EVALUATION.md` | HF Anima discussions (`S-ANIMA-002/003`) |
| non-human / e621 auxiliary | `../catalog/06_SEMANTICS_ALIAS_TRIGGER.md`, `../catalog/05_HARD_NICHE_ADULT_GENERATION.md` | e621 audit; tentacle/nonhuman research; `S-NOOB-EPS-001` |
| LoRA | `../catalog/04_TOOLS_POSTPROCESS_AND_LORA.md` | `S-TOOL-003`, Batch A, hard-source research |
| ControlNet / Regional / Couple / ADetailer | `../catalog/04_TOOLS_POSTPROCESS_AND_LORA.md` | source registry, WAI17 local baseline, Toshiaki practical findings |
| evaluator / tagger | `../catalog/03_FAILURE_TESTING_AND_EVALUATION.md` | Batch C, source registry `S-EVAL-001/002/003` |
| WD14 / WD EVA02 coverage | `../catalog/03_FAILURE_TESTING_AND_EVALUATION.md`, `../catalog/09_OPEN_QUESTIONS_AND_HOLD.md` | WAI17 baseline, Batch C, CURRENT_STATE final-freeze gate |
| Prompt density | `../catalog/02_PROMPT_SUPPORT_AND_COMPOSITION.md` | Batch B, ConceptMix `S-RESEARCH-001`, Stage10 handoff |
| failure knowledge | `../catalog/03_FAILURE_TESTING_AND_EVALUATION.md` | `../research/BATCH_A_FALSE_ASSUMPTION_PREVENTION_20260909.md` |
| Japanese sources | `../catalog/08_SOURCE_AND_SITE_AUDITS.md` | source registry `S-JA-*`, Toshiaki audit/findings, AIArtRecipe |
| English sources | `../catalog/08_SOURCE_AND_SITE_AUDITS.md` | exact HF model cards, primary papers, GitHub runtime docs |
| official sources | `../catalog/08_SOURCE_AND_SITE_AUDITS.md` | `../GENERATION_KNOWLEDGE_SOURCES.md`, `SOURCE_AUTHORITY_MATRIX` |
| community sources | `../catalog/08_SOURCE_AND_SITE_AUDITS.md` | AIArtRecipe, Toshiaki, HF discussions, multilingual practical source entries |
| research papers | `../catalog/03_FAILURE_TESTING_AND_EVALUATION.md`, `08_*` | `S-ILL-002`, `S-RESEARCH-001/002/003/004` |
| HOLD | `HOLD_CONFLICT_REGISTER.md` | `../catalog/09_OPEN_QUESTIONS_AND_HOLD.md`, `../KNOWLEDGE_REASSESSMENT_20260909.md` |
| CONFLICT | `HOLD_CONFLICT_REGISTER.md` | source-audit/reassessment history; future active conflicts get Registry `STATUS=CONFLICT` |
| REJECTED theories | `CLAIM_REGISTRY.csv` (`K-REJECT-*`) | `../KNOWLEDGE_REASSESSMENT_20260909.md`, Stage10 handoff REJECT section |
| historical knowledge | `LEGACY_MAP.md` | `../PRODUCT_GOAL_EVOLUTION_20260909.md`, `../GENERATION_KNOWLEDGE_INDEX.md`, Issue #4 Stage10 handoff |
| version-dependent knowledge | `VERSION_FRESHNESS_LEDGER.csv` | model catalog, source registry, WAI17 baseline |
| Stage10 handoff knowledge | Registry downstream column + Quick Reference | `../../stages/STAGE_10_KNOWLEDGE_HANDOFF.md`, CURRENT_STATE, catalog 03/07/09 |

## Complete existing file inventory

Use `../catalog/10_FILE_MAP.md` for the complete current root + focused research file list. This inventory intentionally does not duplicate that list line-for-line.

## Current-management files

The current-management layer is documented in `README.md`; these files are **new management metadata**, not replacement research.
