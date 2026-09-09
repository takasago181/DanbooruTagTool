# Stage10 PROMPT chat handoff — 2026-09-09

Owner: PROMPT / Issue #5
Branch: `prompt/current-purpose-audit-20260909`
Purpose: New-chat restore index. **GitHub is source of truth; chat history is not.**

## 1. Restore order — current

A new PROMPT chat restores in this order:

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #5 latest restore/migration checkpoint
4. `docs/prompt_knowledge/README.md`
5. `docs/prompt_knowledge/00_KNOWLEDGE_GOVERNANCE.md`
6. `docs/prompt_knowledge/CLAIM_REGISTRY.md`
7. `docs/prompt_knowledge/10_WAI17_LOCAL_FIRST_PROFILE.md` while WAI17 remains the first test model
8. `docs/prompt_knowledge/USE_CASE_ROUTES.md` and only the relevant category files
9. `docs/prompt_knowledge/VERSION_AND_FRESHNESS.md` when exact version/freshness matters
10. `docs/prompt_knowledge/LEGACY_SOURCE_MAP.md` only when provenance/old evidence is needed
11. Issue #30 only for automation/plumbing evidence

Do not make a new chat read every historical Stage10 PROMPT document before it can work.

Current verdict priority:
**Claim Registry > category explanation > legacy detailed evidence wording**.
Legacy docs remain evidence/provenance, not the current adoption-state authority.

---

## 2. Current PROMPT status

- team: PROMPT
- Issue: #5 `[Stage10][PROMPT] Formal handoff pending`
- Stage9 overall Gate: completed
- Stage10 production A/B: **not started / not authorized by this handoff**
- current lane: pre-Stage10 Prompt audit / knowledge organization / WAI17-first test preparation
- final representative Special/evaluator inputs remain gated by current dictionary/final-input dependencies
- KNOWLEDGE #44 remains independent; PROMPT does not overwrite its corpus or verdict authority
- #32 generation validation remains independent
- #30 is automation/plumbing TEMP; PROMPT consumes its evidence but does not redefine it

---

## 3. Current product objective

PROMPT objective:

> Japanese creative intent -> Special-centered, model-family-appropriate, high-quality Prompt structure that can realize difficult/niche/composite adult targets with low user repair burden and explicit Prompt-only/assisted-control separation.

Primary quality dimensions:
- intent fidelity
- target realization
- binding/site/object correctness
- geometry/visibility
- finished visual quality
- model-family fitness
- minimum sufficient structure
- low user repair burden
- reproducibility/traceability

`minimum` means minimum sufficient, not shortest.

Relevant accepted claims:
- `K-PURPOSE-001`–`006`

---

## 4. Knowledge governance — current

Normal knowledge entry point:
`docs/prompt_knowledge/README.md`

### Current claim-status authority
`docs/prompt_knowledge/CLAIM_REGISTRY.md`

### Label schema
`docs/prompt_knowledge/00_KNOWLEDGE_GOVERNANCE.md`

Knowledge uses separate axes:

SOURCE_CLASS:
- OFFICIAL_MODEL
- AUTHOR_GUIDE
- OFFICIAL_RUNTIME
- SEMANTIC_AUTHORITY
- PROJECT_FACT
- CONTROLLED_PRACTICAL
- RESEARCH
- COMMUNITY
- LEGACY

STATUS:
- ACCEPTED
- CANDIDATE
- HOLD
- CONFLICT
- REJECTED
- HISTORICAL

Also preserve:
- SCOPE
- VALIDATION_STATE

Official source does **not** automatically mean production optimization is validated.
Example:
- WAI17 author Steps/CFG guidance = accepted author fact
- `LEAN_TAG_FIRST` as hard-target optimum = candidate requiring Stage10 evidence

Legacy labels are translated through:
`docs/prompt_knowledge/LABEL_MIGRATION_MAP.md`

---

## 5. Categorized knowledge base

Genres:

0. `00_KNOWLEDGE_GOVERNANCE.md`
1. `01_PRODUCT_PURPOSE_AND_GUARDRAILS.md`
2. `02_MODEL_FAMILY_PROFILES.md`
3. `03_PROMPT_CONSTRUCTION_AND_SUPPORT.md`
4. `04_HARD_TARGET_GENRES.md`
5. `05_FAILURE_DIAGNOSIS_AND_ASSISTED_CONTROL.md`
6. `06_QUALITY_CAMERA_NEGATIVE_DENSITY.md`
7. `07_EVALUATION_AND_STAGE10_TESTING.md`
8. `08_SOURCES_EVIDENCE_AND_CORRECTIONS.md`
9. `09_HOLD_CONFLICT_AND_REVALIDATION.md`
10. `10_WAI17_LOCAL_FIRST_PROFILE.md`

Management/navigation:
- `CLAIM_REGISTRY.md`
- `VERSION_AND_FRESHNESS.md`
- `USE_CASE_ROUTES.md`
- `LABEL_MIGRATION_MAP.md`
- `LEGACY_SOURCE_MAP.md`
- `CATALOG_MANIFEST.md`

Maintenance rule:
- material new knowledge -> Claim Registry + category summary + provenance map
- HOLD/conflict stays explicit
- model/runtime claims keep exact scope/version
- do not create unindexed PROMPT knowledge silos

---

## 6. Prompt modes

### Experimental Isolation
- one experiment = one question
- A/B differs only in target variable
- remove irrelevant aesthetic/background variables
- causal isolation / reproducibility / observability first

### Production-quality Stress Test
- realistic completed Prompt
- keep Special core dominant
- add only needed geometry/visibility/relation/camera/quality/Negative
- preserve family differences
- do not inherit stripped experimental Prompt as final user Prompt doctrine

Accepted claims:
- `K-PURPOSE-003`
- `K-TEST-001`

---

## 7. First active model focus — WAI17

Current local-first profile:
`docs/prompt_knowledge/10_WAI17_LOCAL_FIRST_PROFILE.md`

Detailed evidence:
`docs/stages/STAGE_10_PROMPT_WAI17_LOCAL_TEST_PROFILE_20260909.md`

Verified local facts from Issue #30:
- Forge Neo
- `sd\\waiIllustriousSDXL_v170.safetensors`
- SHA-256 `f116b0c78ff441467b0cdc8f1936e1ed18ea31e9997c7b132b1b8db533f0bd04`
- API / PNG metadata / WD14 route verified
- infrastructure `PASS_PIPELINE`

Accepted author claims:
- `K-WAI-001`–`004`

Current Stage10 candidates:
- `K-WAI-005` LEAN_TAG_FIRST
- `K-WAI-006` Steps25 / CFG6 practical baseline
- `K-WAI-007` square causal vs portrait stress resolution usage

Current practical candidate:
- Euler a
- Steps 25
- CFG 6
- 1024x1024 causal when appropriate / 1024x1344 portrait stress
- LoRA OFF baseline
- Hires OFF semantic first pass
- assisted controls OFF Prompt-only baseline
- short family Negative

Important:
**Issue #30 plumbing fixture and WAI17 Prompt-quality profile are separate experiment profiles.**

Exact model/runtime freshness:
`VERSION_AND_FRESHNESS.md`

---

## 8. Core hard-target structure

Internal diagnostic dimensions:
- ACT
- SITE
- OBJECT
- ACTOR_A / ACTOR_B
- RELATION
- POSE / GEOMETRY
- VISIBILITY
- QUALITY / NEGATIVE

Do not expose this as mandatory multi-field user input.
Internal decomposition supports a finished recommended Prompt.

Key accepted claims:
- `K-STRUCT-001`
- `K-STRUCT-002`
- `K-STRUCT-003`

Hard genres:
`docs/prompt_knowledge/04_HARD_TARGET_GENRES.md`

---

## 9. Important do-not-regress items

- no WAI/Illustrious/NoobAI/Anima grammar flattening
- WAI17 exact author guidance outranks generic Illustrious community inheritance
- WAI17: no generic long quality/aesthetic/Negative default
- NoobAI native Special-before-General caption is strong baseline, not universal optimum proof
- Anima tag-mode count uses official `1girl/1boy` surfaces; spaced community forms are not official global defaults
- Anima/Qwen “1k token hard limit / 300 words” rationale is rejected
- `BREAK`, attention, CLIP chunking are parser/runtime scoped
- canonical identity != model-facing render surface
- alias/implication != model response equivalence
- WD EVA02 rare vocabulary absence != Prompt failure
- Hires/ADetailer/Couple/ControlNet success != PROMPT_ONLY success
- `REVIEW` for unsupported evaluator questions is valid routing, not failure
- one seed is insufficient for production Prompt rules
- production behavior remains gated; these docs do not start Stage10 production

Use Claim Registry instead of relying on old wording.

---

## 10. Current test/evaluation doctrine

Evaluation vectors:
- T target
- B binding
- V visibility
- G geometry
- Q finished quality
- C conflict/artifact
- M model evidence
- U user repair
- R reproducibility

Multiple Special: keep `T_A / T_B / ...` separate.

Accepted methodology claims:
- `K-EVAL-001`–`005`
- `K-TEST-001`–`005`

Stage10 high-priority unresolved claims include:
- `K-STRUCT-004/005`
- `K-SEM-004`
- `K-QUALITY-004/007/008`
- `K-WAI-005/006/007`
- `K-FAIL-004`
- `K-CTRL-005`
- `K-EVAL-006`

WAI17-first ordering is defined in file `10`.

---

## 11. Evidence hierarchy

Use the source type appropriate to the claim:
- semantics -> Danbooru; e621 supplemental non-human only
- exact model grammar/settings -> exact author/model official
- parser/extensions -> exact official runtime repo
- failure mechanism -> primary research
- practical workflows -> community evidence after version/correction checks

Core rules:
- tag exists != model recognizes
- recognizes != binds correctly
- token present != intent realized
- community example != production rule
- training caption order != universal inference optimum
- assisted success != Prompt-only success

Full source/correction registry:
`docs/prompt_knowledge/08_SOURCES_EVIDENCE_AND_CORRECTIONS.md`

---

## 12. HOLD registry

All active uncertainty/conflict is consolidated in:
`docs/prompt_knowledge/09_HOLD_CONFLICT_AND_REVALIDATION.md`

Claim-level current statuses are in:
`docs/prompt_knowledge/CLAIM_REGISTRY.md`

Never silently promote HOLD because a new chat lacks context.

Major HOLD families include:
- canonical/Alias/model-trigger response equality
- semantic support generation utility
- family-optimal block order beyond official baseline
- visibility side effects
- density / multi-Special limits
- anatomy-sensitive Negative collision
- quality/meta minimum set
- automatic weighting
- LoRA interaction
- Hires/ADetailer semantic effects
- exact Forge Anima Turbo CFG1 Negative behavior
- final WD evaluator allocation/thresholds
- automatic assisted-control escalation

---

## 13. Historical/provenance documents

Do not delete historical PROMPT detailed docs.
Use:
`docs/prompt_knowledge/LEGACY_SOURCE_MAP.md`

to locate which categorized summary absorbed each one.

If old evidence labels appear:
`docs/prompt_knowledge/LABEL_MIGRATION_MAP.md`

Older branch-only reservoir:
`prompt/audit-knowledge-reservoir-20260909`

Its active unique knowledge has been normalized into `docs/prompt_knowledge/`; switch to old branch only for provenance/source-audit purposes.

---

## 14. Next work when resumed

While gates remain:
- maintain/curate Claim Registry and categorized knowledge
- prepare WAI17 experiment templates/questions
- do not select final representative production set prematurely
- consume #44 handoffs without taking over its corpus
- keep #30 fixture separate from Prompt-quality profiles

When gates authorize representative testing:
- start WAI17-only lane
- one experiment = one question
- product-representative Special cases
- keep Hires and assisted controls separate
- record T/B/V/G/Q/C/M/U/R
- preserve actual resolved Prompt and exact local model/settings
- promote/demote claims by ID based on controlled evidence

---

## 15. Branch/checkpoint identity

Working branch:
`prompt/current-purpose-audit-20260909`

Preferred migration anchor is the Issue #5 checkpoint posted **after the claim-level knowledge normalization**, not an older chat summary.
