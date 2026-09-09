# PROMPT Knowledge Catalog Manifest

Generated/verified: 2026-09-09
Owner: PROMPT / Issue #5
Purpose: human/AI-checkable inventory of the categorized PROMPT knowledge base.

## Active categorized files

1. `README.md` — navigation / restore entry
2. `CURRENT_QUICK_REFERENCE.md` — 30-second current snapshot
3. `00_KNOWLEDGE_GOVERNANCE.md` — normalized SOURCE/STATUS/SCOPE/VALIDATION contract
4. `CLAIM_REGISTRY.md` — current claim-level verdict authority
5. `01_PRODUCT_PURPOSE_AND_GUARDRAILS.md`
6. `02_MODEL_FAMILY_PROFILES.md`
7. `03_PROMPT_CONSTRUCTION_AND_SUPPORT.md`
8. `04_HARD_TARGET_GENRES.md`
9. `05_FAILURE_DIAGNOSIS_AND_ASSISTED_CONTROL.md`
10. `06_QUALITY_CAMERA_NEGATIVE_DENSITY.md`
11. `07_EVALUATION_AND_STAGE10_TESTING.md`
12. `08_SOURCES_EVIDENCE_AND_CORRECTIONS.md`
13. `09_HOLD_CONFLICT_AND_REVALIDATION.md`
14. `10_WAI17_LOCAL_FIRST_PROFILE.md`
15. `VERSION_AND_FRESHNESS.md` — version/source freshness registry
16. `USE_CASE_ROUTES.md` — task-oriented minimal reading routes
17. `LABEL_MIGRATION_MAP.md` — legacy-label normalization
18. `LEGACY_SOURCE_MAP.md` — provenance map from existing Stage10 docs
19. `CATALOG_MANIFEST.md` — this inventory

## Authority roles

- **Project state/rules**: `CURRENT_STATE.md` / `PERMANENT_RULES.md`
- **PROMPT work state**: Issue #5 latest checkpoint
- **Fast human/AI snapshot**: `CURRENT_QUICK_REFERENCE.md`
- **Current knowledge verdicts**: `CLAIM_REGISTRY.md`
- **Human-readable explanation**: category docs `01`–`10`
- **Version/freshness**: `VERSION_AND_FRESHNESS.md`
- **Detailed evidence/history**: legacy Stage10 docs + mapped old branch docs

## Coverage statement

At this checkpoint, current PROMPT knowledge has been normalized across these categories from:

- current-purpose/high-quality audits
- Stage9 delta/revalidation work
- hard-target category/family/failure matrices
- model official source matrix
- Danbooru/e621 semantic authority notes
- assisted-control/runtime capability notes
- compositional-failure research
- AIArtRecipe non-video site audit
- としあきdiffusion Wiki audit/corrections
- WAI17 exact-local profile
- Issue #30 automation/evaluator facts consumed by PROMPT
- historical KNOWLEDGE #4 handoff consumed by PROMPT
- older branch `prompt/audit-knowledge-reservoir-20260909` audit reservoir and runtime/evaluator supplement

This does not mean external research is permanently complete. It means all **currently accumulated PROMPT-side knowledge known at this checkpoint** has an assigned active category/provenance mapping, and major active claims have claim-level status entries.

## Claim-level normalization state

`CLAIM_REGISTRY.md` distinguishes:
- source provenance
- current adoption status
- exact scope
- validation requirement

This prevents legacy one-axis labels from conflating “official source” with “production-ready optimization”.

## Preservation rule

No historical Stage10 PROMPT evidence document was deleted or moved during reorganization.

Categorized files are summaries/navigation; detailed evidence remains in its original document/branch and can be reached through `LEGACY_SOURCE_MAP.md`.
Legacy labels remain in historical documents and are interpreted through `LABEL_MIGRATION_MAP.md`.

## Maintenance check

A future PROMPT knowledge change is considered indexed only when:

- existing Claim ID is updated or a new one is created when material,
- relevant categorized file is updated,
- detailed source/provenance is mapped where applicable,
- HOLD/conflict status is retained,
- version/freshness is updated where relevant,
- Issue #5 checkpoint is created for material changes.

## Restore quality check

A restored PROMPT chat should be able to answer from GitHub alone:

1. current priority model/profile
2. which WAI17 statements are author facts vs Stage10 candidates
3. current unresolved claims
4. current failure taxonomy
5. evaluator limitations
6. Prompt-only vs assisted-control boundary
7. where to find current verdict vs old evidence
