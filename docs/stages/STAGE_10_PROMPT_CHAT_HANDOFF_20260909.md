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
5. `docs/prompt_knowledge/10_WAI17_LOCAL_FIRST_PROFILE.md` while WAI17 remains the first test model
6. only the relevant categorized knowledge files `01`–`09`
7. `docs/prompt_knowledge/LEGACY_SOURCE_MAP.md` when provenance or old evidence is needed
8. Issue #30 only for automation/plumbing evidence

Do not make a new chat read every historical Stage10 PROMPT document before it can work. The categorized index is the normal restore surface; detailed Stage10 documents remain evidence/provenance.

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

---

## 4. Categorized knowledge base

Normal knowledge entry point:
`docs/prompt_knowledge/README.md`

Genres:

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
11. `LEGACY_SOURCE_MAP.md`

Maintenance rule:
- new detailed evidence -> update relevant genre summary + legacy/source map
- do not create unindexed PROMPT knowledge silos
- keep evidence class, exact family/version and HOLD status

---

## 5. Prompt modes

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
- do not inherit the stripped experimental Prompt as the final user Prompt doctrine

---

## 6. First active model focus — WAI17

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

Current practical Prompt-quality baseline candidate:
- Euler a
- Steps 25
- CFG 6
- 1024x1024 causal when appropriate / 1024x1344 portrait stress
- LoRA OFF baseline
- Hires OFF semantic first pass
- assisted controls OFF Prompt-only baseline
- `LEAN_TAG_FIRST`
- short family Negative

Important:
**Issue #30 plumbing fixture and WAI17 Prompt-quality profile are separate experiment profiles.**

---

## 7. Core hard-target structure

Internal diagnostic dimensions:
- ACT
- SITE
- OBJECT
- ACTOR_A / ACTOR_B
- RELATION
- POSE / GEOMETRY
- VISIBILITY
- QUALITY / NEGATIVE

Do not expose this as mandatory multi-field user input. Internal decomposition supports a finished recommended Prompt.

Hard genres are organized in:
`docs/prompt_knowledge/04_HARD_TARGET_GENRES.md`

---

## 8. Important do-not-regress items

- no WAI/Illustrious/NoobAI/Anima grammar flattening
- WAI17 exact author guidance outranks generic Illustrious community inheritance
- WAI17: no generic long quality/aesthetic/Negative default
- NoobAI native Special-before-General caption is strong baseline, not universal optimum proof
- Anima tag-mode count uses official `1girl/1boy` surfaces; spaced community forms are not official global defaults
- Anima/Qwen “1k token hard limit / 300 words” rationale is not accepted
- `BREAK`, attention, CLIP chunking are parser/runtime scoped
- canonical identity != model-facing render surface
- alias/implication != model response equivalence
- WD EVA02 rare vocabulary absence != Prompt failure
- Hires/ADetailer/Couple/ControlNet success != PROMPT_ONLY success
- `REVIEW` for unsupported evaluator questions is valid routing, not failure
- one seed is insufficient for production Prompt rules
- production behavior remains gated; these docs do not start Stage10 production

---

## 9. Current test/evaluation doctrine

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

Stage10 high-priority questions after gates:
1. support auto-selection utility
2. family block order / Special position
3. multi-Special retention/binding
4. visibility side effects
5. density minimum-sufficient curve
6. canonical/Alias/model surface
7. tag-only vs short relation support
8. family/target Negative
9. quality/meta minimum set
10. user effort/replacement burden
11. Prompt-only ceiling / assisted control

WAI17-first ordering is defined in file `10`.

---

## 10. Evidence hierarchy

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

## 11. HOLD registry

All active uncertainty/conflict is consolidated in:
`docs/prompt_knowledge/09_HOLD_CONFLICT_AND_REVALIDATION.md`

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

## 12. Historical/provenance documents

Do not delete historical PROMPT detailed docs.
Use:
`docs/prompt_knowledge/LEGACY_SOURCE_MAP.md`

to locate which categorized summary absorbed each one.

Older branch-only reservoir:
`prompt/audit-knowledge-reservoir-20260909`

Its active unique knowledge has been normalized into `docs/prompt_knowledge/`; switch to the old branch only for provenance/source-audit purposes.

---

## 13. Next work when resumed

While gates remain:
- maintain/curate categorized knowledge
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

---

## 14. Branch/checkpoint identity

Working branch:
`prompt/current-purpose-audit-20260909`

Preferred migration anchor is the Issue #5 checkpoint posted **after the categorized knowledge-base reorganization**, not an older chat summary.
