# KNOWLEDGE Reading Routes

Start every route with project current state/rules + Issue #44 when current routing matters. The files below are the **knowledge-specific 3–5 file route** after that preflight.

## 1. WAI17 knowledge
1. `CURRENT_QUICK_REFERENCE.md`
2. `CLAIM_REGISTRY.csv` — filter `K-MODEL-WAI-*`, `K-NEG-*`, `K-HARD-*`
3. `../catalog/07_WAI17_LOCAL_TEST_PROFILE.md`
4. `VERSION_FRESHNESS_LEDGER.csv`
5. `HOLD_CONFLICT_REGISTER.md`

## 2. Anima knowledge
1. `CLAIM_REGISTRY.csv` — `K-MODEL-ANIMA-*`, `K-SEM-005`
2. `../catalog/01_MODEL_FAMILIES.md`
3. `../research/HF_MODEL_DISCUSSIONS_AUDIT_20260909.md`
4. `HOLD_CONFLICT_REGISTER.md`
5. `VERSION_FRESHNESS_LEDGER.csv`

## 3. NoobAI knowledge
1. `CLAIM_REGISTRY.csv` — `K-MODEL-NOOB-*`, `K-SEM-002/004`
2. `../catalog/01_MODEL_FAMILIES.md`
3. `../catalog/06_SEMANTICS_ALIAS_TRIGGER.md`
4. `HOLD_CONFLICT_REGISTER.md`
5. `VERSION_FRESHNESS_LEDGER.csv`

## 4. Special meaning / canonical
1. `CLAIM_REGISTRY.csv` — `K-SEM-*`
2. `../catalog/06_SEMANTICS_ALIAS_TRIGGER.md`
3. `../research/DANBOORU_WIKI_SEMANTIC_AUDIT_20260909.md`
4. `../research/E621_WIKI_SEMANTIC_TRIGGER_AUDIT_20260909.md`
5. `VERSION_FRESHNESS_LEDGER.csv`

## 5. Support effectiveness
1. `CLAIM_REGISTRY.csv` — `K-SUPPORT-*`, `K-PROMPT-*`
2. `../catalog/02_PROMPT_SUPPORT_AND_COMPOSITION.md`
3. `../research/BATCH_B_MINIMUM_SUFFICIENT_PROMPT_20260909.md`
4. `HOLD_CONFLICT_REGISTER.md`

## 6. Hard target / binding
1. `CLAIM_REGISTRY.csv` — `K-BIND-*`, `K-HARD-*`
2. `../catalog/05_HARD_NICHE_ADULT_GENERATION.md`
3. relevant `../research/HARD_FETISH_*` domain file
4. `../research/HARD_FETISH_COMPOSITE_FAILURE_MATRIX_20260909.md` for composites
5. `HOLD_CONFLICT_REGISTER.md`

## 7. Evaluator / tagger
1. `CLAIM_REGISTRY.csv` — `K-EVAL-*`
2. `../catalog/03_FAILURE_TESTING_AND_EVALUATION.md`
3. `../research/BATCH_C_EVIDENCE_RELIABILITY_20260909.md`
4. `VERSION_FRESHNESS_LEDGER.csv`
5. `HOLD_CONFLICT_REGISTER.md`

## 8. Stage10 knowledge handoff
1. `CURRENT_QUICK_REFERENCE.md`
2. `CLAIM_REGISTRY.csv` — filter downstream `Stage10`
3. `HOLD_CONFLICT_REGISTER.md`
4. `../../stages/STAGE_10_KNOWLEDGE_HANDOFF.md`
5. `../catalog/03_FAILURE_TESTING_AND_EVALUATION.md`

Only `ACCEPTED` claims within matching scope can be handed off as current knowledge; `CANDIDATE/HOLD/CONFLICT` must retain those labels.

## 9. Audit a new external site
1. `KNOWLEDGE_GOVERNANCE.md`
2. `../catalog/08_SOURCE_AND_SITE_AUDITS.md`
3. `../research/SOURCE_AUTHORITY_MATRIX_20260909.md`
4. `../GENERATION_KNOWLEDGE_SOURCES.md`
5. `CLAIM_REGISTRY.csv` before creating/updating claims

## 10. Add a new model
1. `KNOWLEDGE_GOVERNANCE.md`
2. `VERSION_FRESHNESS_LEDGER.csv`
3. `../catalog/01_MODEL_FAMILIES.md`
4. `CLAIM_REGISTRY.csv`
5. `HOLD_CONFLICT_REGISTER.md`

Create version-scoped claims first; generalize only after evidence supports it.

## 11. Check whether an old theory is still valid
1. `LEGACY_MAP.md`
2. `CLAIM_REGISTRY.csv`
3. `LABEL_MIGRATION_MAP.md`
4. linked current category document
5. linked research/evidence only if needed

Registry wins over old prose.

## 12. Receive a question from PROMPT
1. identify the question as semantic / model / support / binding / evaluator
2. filter `CLAIM_REGISTRY.csv` by relevant IDs/scope
3. check `HOLD_CONFLICT_REGISTER.md`
4. check `VERSION_FRESHNESS_LEDGER.csv` if model/runtime dependent
5. read one relevant category/evidence file

Return `Claim ID + STATUS + SCOPE + VALIDATION_STATE + evidence`, not uncited prose. Do not silently convert a HOLD into an answer.
