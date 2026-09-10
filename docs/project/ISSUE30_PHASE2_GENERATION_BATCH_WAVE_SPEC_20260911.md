# Issue #30 Phase 2 Generation Batch Wave Specification — 2026-09-11

## Status

**AUTHORIZED / BATCHED_GENERATION / MAX_16_NEW_IMAGES / STAGE10_PRODUCTION_NOT_STARTED**

This specification follows completion of the Phase 2 reuse-only review. It is intended to reduce repeated ChatGPT/Codex/generation round-trips by executing several independent, high-value generation questions in one bounded batch.

This is still Issue #30 Phase 2 refinement. It is **not** Stage10 production A/B.

## Restore order

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #30 latest body/comments
4. `docs/project/CURRENT_DEV_TASK.md`
5. `docs/project/ISSUE30_PHASE2_EXECUTION_SPEC_20260910.md`
6. `docs/project/ISSUE30_PHASE2_WAVE2_EXECUTION_SPEC_20260910.md`
7. `docs/project/ISSUE30_PHASE2_REUSE_REVIEW_SPEC_20260911.md`
8. this file
9. latest branch evidence on `codex/issue30-calibration-design`

Chat history is not canonical.

## Accepted evidence before this batch

### Reuse-only review

Accepted commit:
- `44c3874ea6083590db256f819d5445501c49ff60`

Result:
- `CAL-023 double handjob`
- 2 pairs / 4 existing images
- both pairs = `A_ONLY_PASS`
- new generation = 0
- evaluator rerun = 0

This provides narrow human evidence that the visible double-handjob predicate can distinguish the target from its contrast in the tested two seeds.

It does **not** authorize general count/relation AUTO truth.

### Previous Phase 2 carry-forward

- P2-001 `vibrator in anus`: both seeds failed correct device/body-site binding.
- P2-002 `holding sex toy`: one A-only success and one contrast-contaminated both-pass.
- P2-003 `breast expansion`: no consistent suppression from adding the same target to Negative in the tested seeds.
- P2-004 `double dildo`: treat as shape/lexical-collapse evidence, not clean exact-count evidence.
- P2-005 `anal` vs `anal penetration`: seed-sensitive; stable alias equivalence not established.
- relation / binding / body-site / count / compound semantics remain human-review protected.
- WD14 / Kagami-24k / CL Tagger v2.00 remain assistive triage only.

## Why a batched wave

The user explicitly prefers several useful generation experiments to be grouped together because repeated ChatGPT reasoning/management cycles and local image-generation cycles are slow when done one experiment at a time.

Therefore:
- group independent experiments into one bounded execution pass;
- keep each experiment causally isolated;
- do not return for approval between valid experiments inside the authorized batch;
- still stop after the whole batch for user/DEV review.

## Batch size

Target:
- **3–4 primary generation experiments**
- normally A/B × 2 predetermined fixed seeds
- normally 12–16 new images total

Hard cap:
- **16 new images**

Reuse compatible prior images whenever settings/seed/prompt identity make that causally valid. Reuse may reduce the new-image count below 4 per experiment.

Do not fill a quota. If only 3 experiments have clean designs, run 3.

No automatic extra seeds inside this batch.

## Primary experiment families

### 1. MULTI_SPECIAL_RETENTION — highest priority

Goal:
Determine whether two individually understandable Specials remain simultaneously visible when combined in one minimal Prompt.

Preferred design:
- reuse existing clean single-Special evidence where possible;
- generate only the combined condition when this remains causally interpretable;
- otherwise use a simple A/B design where B adds exactly one second Special.

Selection requirements:
- both success predicates must be directly judgeable from one still image;
- avoid temporal/contextual Specials such as `after ...` when the state cannot be reliably inferred from a still image;
- avoid pairs whose meanings inherently contradict each other;
- prefer Specials with prior human evidence or clear direct visibility.

User-facing question example:
- `Bでは、Aの行為を残したまま追加したSpecialも同時に成立しているか？`

This family directly tests the real product path `Core Tag Set -> multiple Specials -> Prompt`.

### 2. SINGLE_SUPPORT_TAG_EFFECT

Goal:
Test whether adding exactly one support tag improves a hard Special without broad prompt inflation.

Design:
- A = Special + existing minimal baseline
- B = same + exactly one support tag

Allowed support role examples:
- body-site clarification
- visibility
- geometry
- actor identity
- count

Do not add multiple support roles in one comparison.

Prefer a previously observed failure where the missing property is clear, such as wrong body-site/binding realization.

User-facing question example:
- `補助タグを1個足したBの方が、指定した部位・状態を正しく作れているか？`

### 3. SPECIFIC_ONLY_VS_BROAD_PLUS_SPECIFIC

Goal:
Test whether adding a legitimate broader parent/context tag helps or hurts a specific Special.

Design:
- A = specific Special only + baseline
- B = broad tag + same specific Special + baseline

The broad/specific relationship must be justified from current project knowledge/canonical data. Do not invent hierarchy.

Judge:
- whether the specific target becomes more reliable;
- whether the broad tag causes meaning dilution or unwanted interpretation;
- whether body-site/relation accuracy improves or worsens.

User-facing question example:
- `広いタグを足したBの方が、狙った具体的な行為を正しい形で作れているか？`

### 4. ACTOR_COUNT_DISAMBIGUATION

Goal:
Test whether one minimal actor/count clarification reduces wrong-person, missing-person, or extra-person realization.

Design:
- A = Special + minimal baseline
- B = same + one explicit actor/count clarification

Prefer cooperative / mutual / multi-person / ownership / actor-object cases where the visible success condition is concrete.

User-facing question example:
- `Bでは、必要な人数と役割で行為が成立しているか？`

Machine presence detection must not be treated as role-assignment truth.

## Lower-priority / desk-only family

### MACHINE_SAFE_ZONE

Do not generate images solely for this family unless a specific gap remains after analyzing existing + new batch outputs.

Use existing and batch evaluator results to ask whether a narrow safe human-review reduction rule exists for direct/simple-unary cases.

Any candidate AUTO-support rule must remain narrow and evidence-backed.

## Exact-count handling

Do **not** spend a default new-generation slot on another generic exact-count experiment.

Reason:
- reuse-only `CAL-023 double handjob` produced `A_ONLY_PASS` in both tested pairs;
- this is sufficient as a narrow positive anchor for this phase;
- general count AUTO truth remains unproven and human-protected.

A new exact-count experiment may replace one batch family only if Codex finds a concrete product decision that cannot be made from existing evidence and documents why.

Do not reuse `double dildo` as exact-count evidence.

## Case selection

Codex may choose exact current Special IDs without an intermediate user/DEV round-trip, provided all of the following hold:

1. IDs/tags exist in current canonical project data.
2. Success can be stated as one short concrete Japanese visual question.
3. Only one meaningful A/B variable changes.
4. The case answers one of the authorized experiment families above.
5. Existing evidence does not already answer it sufficiently.
6. The total batch remains <=16 new images.
7. No production/canonical/#32 changes are needed.

Record selected IDs and rationale before generation in repository artifacts, but if all gates PASS Codex may continue directly into the bounded batch without stopping for separate approval.

## Generation profile

Default lane:
- Forge Neo
- WAI Illustrious v17
- Euler a
- Automatic scheduler
- Steps 25
- CFG 5
- 1024×1344 when appropriate
- fixed paired seeds
- Hires OFF
- ADetailer OFF
- LoRA OFF
- ControlNet OFF
- regional prompting OFF
- Forge Couple OFF

Prompt-only and assisted evidence remain separate.

## Evaluator handling

Run/reuse:
- WD14
- Kagami-24k
- CL Tagger v2.00

Roles:
- obvious component/presence support
- disagreement/low-confidence detection
- review prioritization
- artifact/evaluator triage
- safe abstention

Do not let machine output independently authorize:
- relation
- binding
- body-site ownership
- exact count
- multi-person role assignment
- compound retention

## User review UX — supersedes previous contact-sheet density

The user-facing contact sheet is for fast visual judgment, not provenance inspection.

### Contact sheet MUST show

For each image/pair:
- image
- large image number
- A/B marker when needed to answer the pair
- **one large, concrete Japanese question describing exactly what to look for**

### Contact sheet SHOULD NOT show by default

Remove from the user-facing sheet unless strictly needed for the visual decision:
- full Positive Prompt
- full Negative Prompt
- token-by-token bilingual glossary
- seed
- case ID
- evaluator scores/logs
- long experiment descriptions
- model/settings metadata

### Font/readability

- the Japanese question is the primary text element;
- use a Japanese-capable font: Meiryo -> Yu Gothic -> MS Gothic;
- target question font size **>=24 px**, preferably 28–32 px when layout allows;
- number/A/B marker should remain clearly readable;
- tofu/square glyphs => `REVIEW_ASSET_INVALID / BLOCKED`;
- perform a local display sanity check before handing the sheet to the user.

### Traceability remains mandatory, but moves out of the sheet

Repository Markdown/JSON/manifest must still preserve:
- exact executed Positive Prompt
- exact Negative Prompt
- English canonical tags/tokens
- Japanese labels for user-readable detailed records
- seed
- model/hash/settings
- evaluator output references
- image SHA-256/path

If Prompt/tag details are presented to the user outside the contact sheet, display them as `English (日本語)`.

The user is **not required** to inspect this detailed record to perform review.

## Review answer format

Prefer:
- A
- B
- both
- neither
- tie
- unclear

Short observation text is optional and only needed when it materially explains a failure.

## Required repository outputs

Before/during generation:
- batch test design
- selected experiment families and exact Special IDs
- skipped/deferred candidate rationale
- manifest
- expected/reused/new image counts

After generation/evaluation:
- exact generation records
- evaluator records/summary
- artifact gate
- experiment-validity state
- user-facing large-question contact sheet locator
- detailed bilingual traceability report outside the sheet
- pair count / reviewed image count separately
- concise result Markdown
- machine-readable JSON
- tests/dry-run results

Suggested names:
- `docs/testing/ISSUE30_PHASE2_GENERATION_BATCH_DESIGN.md`
- `docs/testing/ISSUE30_PHASE2_GENERATION_BATCH_MANIFEST.csv`
- `docs/testing/ISSUE30_PHASE2_GENERATION_BATCH_RESULT.md`
- `docs/testing/ISSUE30_PHASE2_GENERATION_BATCH_RESULT.json`

## Execution order

1. fetch latest `origin/main`
2. merge latest main into `codex/issue30-calibration-design`; do not rebase/force-rewrite preserved evidence
3. confirm Issue #30/current DEV task points to this specification
4. inspect accepted Phase 1/Wave1/Wave2/reuse-only evidence
5. choose 3–4 valid experiment families/cases
6. prepare design/manifest and concrete Japanese review questions
7. run focused tests/syntax/dry-run/preflight
8. if all gates PASS, execute the whole bounded batch without returning between experiments
9. run/reuse evaluator triage
10. build the simplified large-question contact sheet
11. build detailed repository traceability artifacts separately
12. commit/push branch
13. STOP for user + DEV/ChatGPT review

## Stop rules

After this batch:
- do not add seeds automatically
- do not start another batch automatically
- do not start Stage10 production A/B
- do not broaden to a 2,788-image sweep

DEV/ChatGPT will decide whether Phase 2 has reached diminishing returns.

## Hard boundaries

- maximum new images: 16
- original 128-image wholesale rerun: prohibited
- 2,788-image sweep: prohibited
- Stage10 production A/B: prohibited
- production `data/**`: unchanged
- #32 verdicts: unchanged
- canonical values: unchanged
- no runtime LLM dependency
- no unnecessary extension/tool
- no evaluator promotion to structural semantic truth
