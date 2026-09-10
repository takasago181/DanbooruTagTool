# Issue #30 Phase 2 Execution Specification — 2026-09-10

## 0. Purpose

Issue #30 Phase 2では、Stage10前の待機期間を利用し、実画像を使ったhard/niche系Prompt検証を、ユーザーの手作業を最小化しながら実施する。

本PhaseはPhase 1の128-image calibration pilotの再実行ではない。

目的:
- Special Core Dictionaryを用いた実画像生成で、どの構造クラスがPrompt-onlyで安定して成立するか確認する
- 失敗原因をPrompt / binding / visibility / geometry / Negative collision / evaluator limitation等へ分離する
- Stage10で必要となるA/B実験方法を、少ない生成枚数で実証する
- ユーザーが画像を確認する件数を可能な限り削減する
- automation / review prioritization / artifact validationで実益がある改善のみ採用する

Stage10 production A/Bそのものは開始しない。

## 1. Source of Truth / Restore Order

作業開始前に必ず以下を確認する。

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #30 latest body/comments
4. `docs/project/ISSUE30_HANDOFF_20260910.md`
5. `docs/project/ISSUE30_PHASE2_HANDOFF_20260910.md`
6. this file
7. Phase 1 related artifacts under `docs/testing/`
8. KNOWLEDGE references:
   - `docs/knowledge/catalog/02_PROMPT_SUPPORT_AND_COMPOSITION.md`
   - `docs/knowledge/catalog/03_FAILURE_TESTING_AND_EVALUATION.md`
   - `docs/knowledge/catalog/05_HARD_NICHE_ADULT_GENERATION.md`
   - `docs/knowledge/catalog/07_WAI17_LOCAL_TEST_PROFILE.md`
9. PROMPT Issue #5 relevant checkpoints

Chat history is not canonical.

## 2. Frozen Phase 1 Evidence

Phase 1 evidence must not be rewritten merely to improve automation numbers.

Frozen anchors:
- branch: `codex/issue30-calibration-design`
- 32 representative Special cases × 4 images
- 128 unique images
- WD14 / Kagami-24k / CL Tagger v2.00: 128/128 each
- minimal human review: 19
- provisional AUTO-support: 8
- HUMAN_REVIEW_ONLY: 9
- BLOCKED: 2
- UNRESOLVED: 1

Frozen conclusion: Taggers are assistive triage only.

They are not complete semantic authority for relation/binding, actor/target assignment, body-site ownership, exact quantity, spatial topology, contact/restraint topology, compound retention, or component-only evidence.

Do not reopen this conclusion without new narrowly scoped evidence.

## 3. Phase 2 Core Strategy

Do not generate a large new fixed batch. Use an adaptive test flow.

First classify the existing 128-image pilot by structural capability.

Recommended structural classes:
- `UNARY_OBJECT_OR_STATE`
- `BODY_SITE_STATE`
- `SIMPLE_RELATION`
- `BINDING_RELATION`
- `RESTRAINT_TOPOLOGY`
- `DEVICE_RELATION`
- `MULTI_OBJECT_OR_COUNT`
- `NONHUMAN_APPENDAGE_RELATION`
- `ANATOMY_CHANGING`
- `COMPOSITE_HARD`

For each class record:
- existing image count
- existing Special cases
- human-reviewed evidence
- evaluator coverage
- clear PASS evidence
- clear FAIL evidence
- unresolved evidence
- whether additional image testing has practical value

Outputs:
- `docs/testing/ISSUE30_PHASE2_STRUCTURAL_COVERAGE.md`
- `docs/testing/ISSUE30_PHASE2_STRUCTURAL_COVERAGE.json`

## 4. New Image Test Selection

Only select new cases after the coverage analysis.

Target approximately 5–6 primary experimental questions. The first new generation wave should normally stay near 10–12 images.

Prefer currently weak/high-value structural questions such as:
- functional device/contact relation
- source / ownership relation
- exact count retention
- simultaneous multi-Special retention
- anatomy-changing interaction with Negative Prompt
- canonical vs Alias / alternate trigger surface

The exact Special IDs must be selected from current canonical project data. Do not invent synthetic tags.

Do not select a case merely because it is visually interesting. Each case must answer one concrete unresolved question.

## 5. Adaptive Seed Rule

Initial test:
- 2 predetermined fixed seeds per experimental condition

Do not begin with 4+ seeds automatically.

Escalation:
- if both seeds show the same clear result: stop that comparison
- if results disagree: add seed 3
- if still unstable and the question materially affects product behavior: add seed 4
- if additional seeds are unlikely to change a product decision: stop

No arbitrary fixed `N seeds = proven` rule.

## 6. Experiment Design

One experiment = one primary question.

Paired conditions must keep everything fixed except the intended variable.

Preserve at minimum:
- exact Positive Prompt
- exact Negative Prompt
- checkpoint filename/hash
- Forge Neo version/commit where available
- sampler
- scheduler
- steps
- CFG
- width / height
- seed
- LoRA state
- Hires state
- ADetailer state
- Control / regional state
- generated image path
- image SHA-256

Do not keep only successful outputs.

## 7. Prompt Escalation Order

Use minimum sufficient Prompt.

Recommended progression:
1. target Special minimal
2. required actor/count identity
3. one visibility support
4. one geometry/binding support
5. canonical vs known Alias/alternate trigger
6. broad + specific comparison
7. Negative OFF / ON comparison when relevant
8. additional predetermined seed only if needed
9. second hard Special only after single-target behavior is understood
10. assisted-control lane only after bounded Prompt-only attempts

Do not stack several support roles at once. Do not solve weighting before structural conflicts are cleaned up.

## 8. WAI17 Baseline

Default initial lane:
- Forge Neo
- WAI Illustrious v17
- Euler a
- Steps: 25
- CFG: 5
- 1024×1344 portrait when appropriate
- fixed paired seeds
- Hires OFF
- ADetailer OFF
- LoRA OFF
- ControlNet OFF
- regional prompting OFF
- Forge Couple OFF

Quality/meta should remain minimal and model-appropriate. The baseline is for causal isolation, not maximum image quality.

## 9. Prompt-only vs Assisted Evidence

These must remain separate:
- Prompt-only
- Hires-assisted
- ADetailer / inpaint-assisted
- LoRA-assisted
- Control / regional-assisted
- Forge Couple-assisted

An assisted success must never be recorded as plain Prompt success.

## 10. Evaluation States

Use at least:
- `A_ONLY_PASS`
- `B_ONLY_PASS`
- `BOTH_PASS`
- `BOTH_FAIL`
- `TIE`
- `UNCLEAR`
- `BLOCKED`

Also record the primary failure class where possible:
- `F1_IDENTITY_EXPOSURE`
- `F2_UNARY_REALIZATION`
- `F3_COMPOSITION_COMPETITION`
- `F4_BINDING_OWNERSHIP`
- `F5_VISIBILITY_OCCLUSION`
- `F6_PROMPT_CONTRADICTION`
- `F7_NEGATIVE_COLLISION`
- `F8_MODEL_SETTINGS_MISMATCH`
- `F9_POSTPROCESS_CONFOUND`
- `F10_EVALUATOR_BLINDNESS`

## 11. Evaluator Role

WD14 / Kagami / CL may be used for:
- pre-screening
- obvious unary support
- disagreement detection
- low-confidence detection
- review prioritization
- safe abstention

They must not independently authorize semantic success for structural relation cases.

Machine disagreement must not silently become FAIL. Unsupported evaluator vocabulary must not be interpreted as model generation failure.

## 12. Artifact Quality Gate

Before semantic evaluation, detect obvious unusable artifacts.

At minimum identify:
- unreadable / near-uniform image
- corrupt image
- missing image
- missing metadata
- missing expected hash/provenance
- failed generation response

Artifact failure -> `BLOCKED`.

Do not treat it as evaluator semantic failure.

## 13. Experiment Validity Gate

A generated image may fail to realize the intended test condition.

Examples:
- target-present Prompt did not actually produce the target
- contrast condition accidentally contains the target
- comparison differs in several uncontrolled ways
- framing prevents observation

Such cases are experiment-validity failures and must not be used as clean evaluator false-positive/false-negative evidence.

## 14. Tool Policy

Existing-tool-first remains mandatory.

Already validated environment:
- Multi Prompt Slots
- Forge Neo built-in X/Y/Z Plot
- Forge Neo Infinite Image Browsing
- Forge standard API
- existing Issue #30 pilot runner infrastructure
- WD14 Tagger
- Kagami-24k
- CL Tagger v2.00

Do not install another extension merely because one exists. Do not add Agent Scheduler unless an actual queue/history/API limitation is demonstrated. Do not build a new GUI/dashboard.

Thin glue code is permitted when it clearly reduces manual work.

## 15. Runner Refactor

Prefer reusing `tools/issue30_calibration_pilot.py`.

Allowed narrow refactor:
- remove fixed 32-case assumption
- support external manifest input
- support variable case count
- retain fixed-seed paired generation
- retain Forge process safety checks
- retain cached image reuse
- retain metadata/hash preservation
- retain screen-only/reuse behavior
- produce review assets
- produce GitHub-ready result summary

Do not rewrite the runner from scratch unless technically necessary.

## 16. Required Deliverables

Before generating images:
- structural coverage report
- proposed new experimental questions
- selected Special IDs
- experimental manifest
- expected image count
- expected user-review count

After generation:
- generation manifest
- exact Prompt/Negative records
- image SHA-256 records
- evaluator outputs where applicable
- artifact-validity result
- experiment-validity result
- contact sheet / review assets
- machine-readable results
- concise Markdown result summary

Suggested paths:
- `docs/testing/ISSUE30_PHASE2_STRUCTURAL_COVERAGE.md`
- `docs/testing/ISSUE30_PHASE2_STRUCTURAL_COVERAGE.json`
- `docs/testing/ISSUE30_PHASE2_TEST_MANIFEST.csv`
- `docs/testing/ISSUE30_PHASE2_TEST_DESIGN.md`
- `docs/testing/ISSUE30_PHASE2_RESULT_SUMMARY.md`

Local generated images may remain outside GitHub if binary/local-only policy requires it. Do not commit large generated-image sets unless existing project policy explicitly allows it.

## 17. User Review Design

The user should not edit CSV or manually inspect logs.

Provide:
- numbered contact sheet
- Japanese experiment description
- A/B condition labels
- only the one question being judged
- review-visible Positive / Negative Prompt tags as **English original + Japanese label**

The executed Prompt remains English/canonical. Japanese is display-only and must never silently alter generation input.

Bilingual display applies at minimum to:
- target / contrast tags
- actor / count tags
- visibility / geometry / support tags shown to the user
- Negative Prompt tags relevant to the comparison

Japanese text rendering is part of the review-asset validity gate. On Windows, prefer a Japanese-glyph-capable font in this order when available:
1. Meiryo (`meiryo.ttc`)
2. Yu Gothic (`YuGothM.ttc` or another installed Yu Gothic face)
3. MS Gothic (`msgothic.ttc`)

Do not silently accept `ImageFont.load_default()` or another font that renders Japanese as tofu/empty squares for a user-facing review asset. If no usable Japanese font is available, mark the review asset `REVIEW_ASSET_INVALID` / `BLOCKED` and stop for a rendering fix rather than asking the user to review broken labels.

After changing Japanese labels or font selection, regenerate the contact sheet and perform a local display check before review. Confirm that at least one known Japanese label renders legibly and is not replaced by square/tofu glyphs. Record the selected font and display-check result in the review/result artifact when practical.

User response should ideally be limited to:
- A
- B
- both
- neither
- tie
- unclear

Structural experiments may include one additional narrowly scoped question where necessary. Do not ask the user to inspect evaluator scores manually.

## 18. Stop Rules

Stop Phase 2 expansion when:
- additional tests mainly hit relation/binding limits already known
- user-visible manual-work reduction becomes small
- new evaluator/tool contributes little unique information
- additional seed/image count is unlikely to change a product decision
- automation complexity exceeds expected benefit
- existing evidence is sufficient for #42 / Stage10 design

Do not continue testing simply to increase sample count.

## 19. Hard Prohibitions

Do not:
- rerun the full original 128-image pilot
- generate a 2,788-image sweep
- start Stage10 production A/B
- modify production `data/**`
- modify #32 verdicts
- modify canonical values
- reinterpret Phase 1 results to improve metrics
- flatten WAI / Illustrious / NoobAI / Anima behavior into one rule
- use runtime LLM dependency
- install unnecessary extensions
- build a large experiment platform

## 20. GitHub Handoff Rule

Meaningful checkpoints must be reviewable from GitHub.

Per `PERMANENT_RULES.md`, Codex does not need private Issue write access as a completion requirement. Codex's required responsibility is to commit/push reviewable branch artifacts and a repository execution report. DEV/ChatGPT then retrieves that evidence and records the Issue #30 checkpoint.

Repository execution report should use:
- RESULT
- EVIDENCE
- DECISION
- LIMITATION
- NEXT

When a review decision is needed, Codex must stop rather than silently expanding scope.

## 21. Immediate Execution Order

1. restore GitHub canonical state
2. inspect existing Phase 1 artifacts
3. create structural coverage matrix
4. identify evidence gaps
5. choose 5–6 high-value experimental questions
6. prepare manifest
7. make only minimal runner changes required
8. run syntax/unit/dry-run checks
9. create a pre-generation repository checkpoint/report
10. if this specification already authorizes the bounded first wave and all preflight checks PASS, execute only that bounded first wave
11. stop after first-wave artifacts are complete
12. push branch/commit
13. provide branch/commit/report for DEV/ChatGPT review
14. wait for DEV/ChatGPT review before additional experimental expansion

No automatic progression into Stage10 production testing.
