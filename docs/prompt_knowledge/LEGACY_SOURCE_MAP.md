# Legacy PROMPT source map

Owner: PROMPT / Issue #5
Status: provenance/navigation map.

## 目的

`docs/prompt_knowledge/` を普段読む入口にしつつ、これまで作成した `docs/stages/STAGE_10_PROMPT_*.md` を一件も孤立させないための対応表。

旧資料は削除・移動しない。詳細な証拠・監査履歴・coverage・backlogとして残す。

## Current branch source map

| Existing document | Primary genre | Secondary genre | Role |
|---|---|---|---|
| `STAGE_10_PROMPT_AIARTRECIPE_COVERAGE_LEDGER_20260909.md` | 08 Sources | — | 非動画site coverage / page inventory |
| `STAGE_10_PROMPT_AIARTRECIPE_INGESTION_RULES_20260909.md` | 08 Sources | 09 HOLD | community ingestion rules |
| `STAGE_10_PROMPT_AIARTRECIPE_SITE_AUDIT_20260909.md` | 08 Sources | 04 Hard targets / 05 Failure | site-wide audit, useful failures/corrections |
| `STAGE_10_PROMPT_ASSISTED_CONTROL_OFFICIAL_CAPABILITIES_20260909.md` | 05 Failure/control | 08 Sources | official runtime capability evidence |
| `STAGE_10_PROMPT_CHAT_HANDOFF_20260909.md` | README / restore | 10 WAI17 | old chat restore snapshot |
| `STAGE_10_PROMPT_COMPOSITIONAL_FAILURE_RESEARCH_LEDGER_20260909.md` | 05 Failure | 07 Evaluation / 08 Sources | research-backed failure taxonomy |
| `STAGE_10_PROMPT_CURRENT_PURPOSE_AUDIT_20260909.md` | 01 Purpose | 09 HOLD | current purpose and Stage9 assumptions to reframe |
| `STAGE_10_PROMPT_HARD_TARGET_CATEGORY_FAMILY_FAILURE_MATRIX_20260909.md` | 04 Hard genres | 02 Family / 05 Failure | category × family × failure detailed matrix |
| `STAGE_10_PROMPT_HARD_TARGET_FAMILY_MATRIX_20260909.md` | 02 Family | 04 Hard genres | family-specific hard-target matrix |
| `STAGE_10_PROMPT_HARD_TARGET_FAMILY_SOURCE_LEDGER_20260909.md` | 08 Sources | 02 Family | source/evidence ledger behind family matrix |
| `STAGE_10_PROMPT_HARD_TARGET_TEST_BACKLOG_20260909.md` | 07 Testing | 04 Hard genres / 09 HOLD | hard-target experiment backlog |
| `STAGE_10_PROMPT_HIGH_QUALITY_AUDIT_SCORECARD_20260909.md` | 07 Evaluation | 01 Purpose | T/B/V/G/Q/C/M/U/R scorecard candidate |
| `STAGE_10_PROMPT_HIGH_QUALITY_HARD_IMAGE_CONTRACT_20260909.md` | 01 Purpose | 03 Construction / 04 Hard / 06 Quality | high-quality hard-image purpose contract |
| `STAGE_10_PROMPT_MODEL_OFFICIAL_SOURCE_MATRIX_20260909.md` | 02 Family | 08 Sources | official model facts and implications |
| `STAGE_10_PROMPT_PRIMARY_SOURCE_BACKBONE_20260909.md` | 08 Sources | — | source hierarchy/backbone |
| `STAGE_10_PROMPT_REPLACEMENT_REFERENCE.md` | 03 Construction | 01 Purpose | replacement-slot and candidate workflow |
| `STAGE_10_PROMPT_REVALIDATION_BACKLOG_20260909.md` | 09 HOLD | 07 Testing | old assumptions / controlled A/B backlog |
| `STAGE_10_PROMPT_SEMANTIC_AUTHORITY_DANBOORU_E621_20260909.md` | 08 Sources | 03 Construction | semantic authority / render surface separation |
| `STAGE_10_PROMPT_STAGE9_DELTA_AUDIT_20260909.md` | 01 Purpose | 09 HOLD | Stage9 vs current-purpose delta audit |
| `STAGE_10_PROMPT_TOSHIAKI_WIKI_AUDIT_20260909.md` | 08 Sources | — | Toshiaki Wiki audit |
| `STAGE_10_PROMPT_TOSHIAKI_WIKI_CORRECTIONS_20260909.md` | 08 Sources | 02 Family / 06 Quality / 09 HOLD | official conflicts/corrections |
| `STAGE_10_PROMPT_TOSHIAKI_WIKI_COVERAGE_LEDGER_20260909.md` | 08 Sources | — | Wiki coverage ledger |
| `STAGE_10_PROMPT_TOSHIAKI_WIKI_INGESTION_RULES_20260909.md` | 08 Sources | 09 HOLD | Wiki ingestion/version rules |
| `STAGE_10_PROMPT_WAI17_LOCAL_TEST_PROFILE_20260909.md` | 10 WAI17 | 02 Family / 06 Quality / 07 Testing | detailed exact-local WAI17 profile |

All paths above are under `docs/stages/`.

## Upstream/non-PROMPT-owned inputs

| Document | PROMPT genres consuming it | Notes |
|---|---|---|
| `docs/stages/STAGE_10_KNOWLEDGE_HANDOFF.md` | 02 / 03 / 06 / 09 | historical formal KNOWLEDGE #4 handoff; do not edit as PROMPT knowledge source |
| `docs/stages/STAGE_10_PREP.md` | README / 07 | Stage10 Gate; stage authority, not knowledge corpus |
| `docs/testing/ISSUE30_SPECIAL_REPRESENTATIVE_ROUTING_DESIGN_20260908.md` | 07 | TEMP #30 routing/evaluator design |
| Issue #30 evidence/comments | 07 / 10 | automation/plumbing and exact local WAI17 facts |
| Issue #44 corpus | 08 / future intake | ongoing KNOWLEDGE owner; PROMPT consumes via handoff, does not overwrite |

## Older PROMPT branch-only reservoir

Branch: `prompt/audit-knowledge-reservoir-20260909`

### `docs/stages/STAGE_10_PROMPT_AUDIT_KNOWLEDGE_RESERVOIR.md`

Knowledge integrated into current categorized files:
- evidence labels -> 08
- exact-family baselines -> 02
- parser/execution trace -> 03 / 09
- compositional failure taxonomy -> 05
- Prompt density/camera/Negative/weighting -> 06
- reproducibility -> 07
- HOLD items -> 09

### `docs/stages/STAGE_10_PROMPT_AUDIT_RUNTIME_EVALUATOR_SUPPLEMENT.md`

Knowledge integrated into:
- base vs Hires/ADetailer/control -> 05 / 06
- Anima Turbo CFG1 × Negative HOLD -> 09
- LoRA intervention/interference -> 06 / 09
- WD EVA02 vocabulary/threshold boundary -> 07 / 09
- evaluator blind spots -> 07 / 09
- resolution/aspect ratio test condition -> 07 / 09
- controlled-same-settings vs family-optimal -> 07 / 09
- seed robustness/failure distribution -> 07

### Restore rule

Normal PROMPT restore does **not** need to switch to the old branch. Its unique active knowledge has been normalized into `docs/prompt_knowledge/`.

Only inspect the old branch when:
- auditing provenance
- checking original source citations/details
- confirming a historical wording/decision

## Category ownership summary

### 01 Product purpose and guardrails
Primary legacy anchors:
- CURRENT_PURPOSE_AUDIT
- HIGH_QUALITY_HARD_IMAGE_CONTRACT
- STAGE9_DELTA_AUDIT
- REPLACEMENT_REFERENCE

### 02 Model family profiles
- MODEL_OFFICIAL_SOURCE_MATRIX
- HARD_TARGET_FAMILY_MATRIX
- HARD_TARGET_FAMILY_SOURCE_LEDGER
- TOSHIAKI corrections
- WAI17 detailed profile

### 03 Prompt construction and support
- HIGH_QUALITY_HARD_IMAGE_CONTRACT
- REPLACEMENT_REFERENCE
- SEMANTIC_AUTHORITY
- KNOWLEDGE handoff

### 04 Hard target genres
- HARD_TARGET_CATEGORY_FAMILY_FAILURE_MATRIX
- HARD_TARGET_FAMILY_MATRIX
- HARD_TARGET_TEST_BACKLOG
- AIArtRecipe hard-target observations

### 05 Failure diagnosis and assisted control
- COMPOSITIONAL_FAILURE_RESEARCH_LEDGER
- ASSISTED_CONTROL_OFFICIAL_CAPABILITIES
- hard category/failure matrix
- old audit reservoir/runtime supplement

### 06 Quality/camera/Negative/density
- HIGH_QUALITY_HARD_IMAGE_CONTRACT
- HARD_TARGET_FAMILY_MATRIX
- TOSHIAKI corrections
- revalidation backlog
- old reservoir/runtime supplement

### 07 Evaluation and Stage10 testing
- HIGH_QUALITY_AUDIT_SCORECARD
- HARD_TARGET_TEST_BACKLOG
- REVALIDATION_BACKLOG
- Issue #30 routing/evidence
- old runtime evaluator supplement

### 08 Sources/evidence/corrections
- PRIMARY_SOURCE_BACKBONE
- MODEL_OFFICIAL_SOURCE_MATRIX
- SEMANTIC_AUTHORITY
- COMPOSITIONAL_FAILURE_RESEARCH_LEDGER
- AIArtRecipe audit set
- Toshiaki audit set

### 09 HOLD/conflict/revalidation
- REVALIDATION_BACKLOG
- CURRENT_PURPOSE_AUDIT reframes
- TOSHIAKI corrections
- old reservoir/runtime supplement

### 10 WAI17 local-first
- WAI17 detailed local test profile
- Issue #30 exact local runtime evidence
- WAI17 family entries in official/family matrices

## Maintenance rule

When a new detailed PROMPT evidence document is created:

1. add its active conclusion to the relevant `docs/prompt_knowledge/0X_*.md`
2. add the detailed document to this map
3. preserve its evidence class / version / HOLD status
4. do not create a second competing summary without updating README

This map is how future PROMPT班 detects “knowledge exists but was never incorporated into the categorized knowledge base”.
