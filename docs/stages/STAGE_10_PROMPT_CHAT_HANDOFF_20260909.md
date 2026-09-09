# Stage10 PROMPT chat handoff — 2026-09-09

Owner: PROMPT / Issue #5
Branch: `prompt/current-purpose-audit-20260909`
Purpose: New-chat restore index. **GitHub is source of truth; chat history is not.**

## 1. Restore order

A new PROMPT chat must restore in this order:

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #5 latest comment / restore checkpoint
4. this handoff file
5. `docs/stages/STAGE_10_PROMPT_WAI17_LOCAL_TEST_PROFILE_20260909.md`
6. Issue #30 only when automation/plumbing evidence is needed

Do not restore PROMPT state from chat summaries if GitHub differs.

---

## 2. Current PROMPT status

- team: PROMPT
- Issue: #5 `[Stage10][PROMPT] Formal handoff pending`
- Stage9 overall Gate: completed
- Stage10 production A/B: **not started / not authorized by this handoff**
- current work: pre-Stage10 Prompt audit / research accumulation / WAI17-first test preparation
- dictionary/final representative Special/evaluator gates remain external dependencies
- KNOWLEDGE #44 remains independent; PROMPT does not edit its corpus or verdict authority
- #32 generation validation remains independent
- #30 is automation/plumbing TEMP; PROMPT consumes its evidence but does not redefine it

---

## 3. Current product objective

Current PROMPT objective is no longer “correctly convert Japanese to Danbooru tags” alone.

Target:

> Convert Japanese creative intent into a high-quality, model-appropriate Prompt structure that preserves the intended Special concept, works for difficult/niche/composite adult targets, minimizes user repair, and escalates to assisted controls when Prompt-only becomes inefficient.

Quality dimensions:
- meaning / target retention
- searchability / Japanese UX
- Prompt usability
- model-specific renderability
- binding / site / object correctness
- geometry / visibility
- final image quality
- low user repair cost
- reproducibility

“Minimum Prompt” means **minimum sufficient**, not shortest possible.

---

## 4. Two Prompt modes — still valid

### Experiment separation mode
- one experiment = one question
- A/B differs only in the target variable
- no unnecessary quality/background/lighting/person attributes
- prioritize causal isolation, reproducibility, observability

### User practical stress-test mode
- build a realistic completed Prompt close to actual user use
- keep Special core dominant
- add only needed quality/composition/camera/visibility/lighting/expression/background/negative
- do not bury Special with redundant same-role support

Do not casually redesign these modes; audit suitability first.

---

## 5. WAI17 is the first active model focus

User decided initial testing will be WAI Illustrious v17 in the existing local environment.

Verified local model from Issue #30:
- `sd\\waiIllustriousSDXL_v170.safetensors`
- SHA-256: `f116b0c78ff441467b0cdc8f1936e1ed18ea31e9997c7b132b1b8db533f0bd04`
- Forge Neo environment
- API / PNG metadata / WD14 pipeline already reached `PASS_PIPELINE`

Author-side WAI17 baseline:
- Forge Neo recommended
- Euler a
- Steps 15–30
- CFG 5–7
- VAE integrated
- original size >1024x1024
- example 1024x1344
- Hires 1.5 / 20 steps / denoise 0.35–0.5 example
- minimal quality prompt example
- minimal negative example
- warning against too many quality/aesthetic tags and overly long Negative

PROMPT WAI17 practical baseline candidate:
- Steps 25
- CFG 6
- Euler a
- 1024x1024 for causal square tests when suitable
- 1024x1344 for practical portrait stress tests
- Hires OFF during first semantic comparison
- LoRA OFF unless explicitly tested
- assisted controls OFF for Prompt-only baseline
- lean tag-first candidate grammar

See `STAGE_10_PROMPT_WAI17_LOCAL_TEST_PROFILE_20260909.md` for details.

Important: **Issue #30 fixture settings and this WAI17 practical baseline are separate profiles.** Do not overwrite or conflate them.

---

## 6. Hard-target research direction

The user’s intended product includes high-quality difficult/niche adult imagery. PROMPT research therefore tracks internal diagnostic dimensions:

- ACT
- SITE
- OBJECT
- ACTOR_A / ACTOR_B
- RELATION
- POSE / GEOMETRY
- VISIBILITY

Primary failure classes:
- ACT_MISSING
- SITE_WRONG
- BINDING_LOST
- OBJECT_DEGRADES
- VISIBILITY_LOST
- GEOMETRY_BREAK
- PROMPT_INTERFERENCE

The user must not be forced to manually fill these dimensions; they are internal composer/audit dimensions.

---

## 7. Evidence hierarchy now in use

### Highest authority by domain
- model Prompt grammar / settings: exact model author / official model card
- tag semantics / alias / implication: Danbooru; e621 only as auxiliary taxonomy where relevant
- parser / extension behavior: official GitHub repo / exact runtime implementation
- failure theory: papers / benchmarks
- practical Japanese workflows: AIArtRecipe / としあきdiffusion Wiki, after correction/version scoping

Community evidence never overrides exact official evidence without controlled local A/B.

---

## 8. Important accumulated PROMPT artifacts

### Current-purpose / quality audit
- `STAGE_10_PROMPT_CURRENT_PURPOSE_AUDIT_20260909.md`
- `STAGE_10_PROMPT_CURRENT_PURPOSE_REVALIDATION_BACKLOG_20260909.md`
- `STAGE_10_PROMPT_HIGH_QUALITY_HARD_IMAGE_CONTRACT_20260909.md`
- `STAGE_10_PROMPT_STAGE9_DELTA_AUDIT_20260909.md`
- `STAGE_10_PROMPT_HIGH_QUALITY_AUDIT_SCORECARD_20260909.md`

### Hard-target / family research
- `STAGE_10_PROMPT_HARD_TARGET_FAMILY_MATRIX_20260909.md`
- `STAGE_10_PROMPT_HARD_TARGET_FAMILY_SOURCE_LEDGER_20260909.md`
- `STAGE_10_PROMPT_HARD_TARGET_CATEGORY_FAMILY_FAILURE_MATRIX_20260909.md`
- `STAGE_10_PROMPT_HARD_TARGET_TEST_BACKLOG_20260909.md`

### Japanese community source audits
AIArtRecipe:
- `STAGE_10_PROMPT_AIARTRECIPE_SITE_AUDIT_20260909.md`
- `STAGE_10_PROMPT_AIARTRECIPE_INGESTION_RULES_20260909.md`
- `STAGE_10_PROMPT_AIARTRECIPE_COVERAGE_LEDGER_20260909.md`

としあきdiffusion Wiki:
- `STAGE_10_PROMPT_TOSHIAKI_WIKI_AUDIT_20260909.md`
- `STAGE_10_PROMPT_TOSHIAKI_WIKI_INGESTION_RULES_20260909.md`
- `STAGE_10_PROMPT_TOSHIAKI_WIKI_COVERAGE_LEDGER_20260909.md`
- `STAGE_10_PROMPT_TOSHIAKI_WIKI_CORRECTIONS_20260909.md`

### Primary-source backbone
- `STAGE_10_PROMPT_PRIMARY_SOURCE_BACKBONE_20260909.md`
- `STAGE_10_PROMPT_MODEL_OFFICIAL_SOURCE_MATRIX_20260909.md`
- `STAGE_10_PROMPT_SEMANTIC_AUTHORITY_DANBOORU_E621_20260909.md`
- `STAGE_10_PROMPT_ASSISTED_CONTROL_OFFICIAL_CAPABILITIES_20260909.md`
- `STAGE_10_PROMPT_COMPOSITIONAL_FAILURE_RESEARCH_LEDGER_20260909.md`

### WAI17-first test profile
- `STAGE_10_PROMPT_WAI17_LOCAL_TEST_PROFILE_20260909.md`

These are PROMPT-side research/audit artifacts, not automatic production authority.

---

## 9. Important corrections / do-not-regress items

- Do not flatten WAI / Illustrious / NoobAI / Anima Prompt grammars.
- Illustrious general knowledge must not automatically override exact WAI17 author guidance.
- WAI17: avoid generic long quality/aesthetic stacks and generic long Negative inheritance.
- NoobAI native caption order is strong baseline evidence, not proof of universal hard-target optimum.
- Anima official grammar uses `1girl` style tags; community claims preferring spaced count forms are not official fact.
- Anima/Qwen “~1k token hard limit” explanation was rejected as technically incorrect/unsupported.
- A1111/Forge parser syntax is not the same thing as model training grammar.
- `BREAK` and attention syntax must be parser/runtime scoped.
- WD EVA02 v3 filters tags with <600 training images; rare Special absence is not automatic failure.
- Hires / ADetailer / Forge Couple / ControlNet success must not be misreported as PROMPT_ONLY success.
- canonical identity, Japanese display/search text, and model trigger/render spelling are separate layers.

---

## 10. Current next work

When PROMPT work resumes:

1. use WAI17-only lane first
2. build WAI17 Stage10 A/B experiment template using proven Issue #30 automation infrastructure
3. keep one experiment = one question
4. choose representative Special cases only after the current dictionary/final-input Gate allows it
5. start with Special recognition / canonical-vs-alias / minimal support / visibility / Negative length
6. keep Hires and assisted controls as separate passes
7. evaluate target/site/binding/object/geometry/visibility/finish separately
8. do not start production Stage10 until project Gates authorize it

---

## 11. Branch/checkpoint identity

PROMPT working branch:
`prompt/current-purpose-audit-20260909`

WAI17 profile commit before this handoff:
`0594f4fc15b64dbe748c66df80b827dda80bdb0a`

The Issue #5 checkpoint posted after this file is the preferred chat-migration restore pointer.

