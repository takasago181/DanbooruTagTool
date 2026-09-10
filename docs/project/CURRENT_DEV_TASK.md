# CURRENT DEV TASK

最終同期: 2026-09-11

## Mirror Metadata

- Source Issue: **#30** `[Stage10-PREP][PHASE2_ACTIVE] Targeted evaluator refinement before #42`
- State: **ACTIVE / PHASE2_GENERATION_BATCH_WAVE_AUTHORIZED**
- Branch: `codex/issue30-calibration-design`
- Current Stage: Stage10準備Gate実施中

## Current continuation contract

**`docs/project/ISSUE30_PHASE2_GENERATION_BATCH_WAVE_SPEC_20260911.md`**

This supersedes the completed reuse-only pass as the current #30 execution task.

## Accepted Phase 2 checkpoints

- Wave 1 + human review: `233a2a25b58de388cdf4ccff1183fca0a3260472`
- Wave 2 execution: `b478f32042fa3b4111a6b86c24cb6c77655d579a`
- Wave 2 human review: `34aa09a8d7c82bbfaf798c68c8c98a72a65cce50` / `63ac1ee49edef710a3b10135a7a2d33250d6cb96`
- Reuse-only human review: `44c3874ea6083590db256f819d5445501c49ff60`

Reuse-only result:
- `CAL-023 double handjob`
- 2 pairs / 4 existing images
- both pairs `A_ONLY_PASS`
- new generation 0
- evaluator rerun 0
- narrow positive count/action anchor only; no general structural AUTO promotion

## Current purpose

The user wants the remaining useful generation tests grouped into one batch to reduce repeated ChatGPT/Codex and local generation turnaround.

Run **3–4 independent high-value experiments in one bounded pass**, preserving one-experiment/one-question causality.

Normal target:
- 12–16 new images
- hard cap **16 new images**
- A/B × 2 predetermined fixed seeds when new generation is needed
- reuse compatible existing evidence where valid
- no automatic extra seeds

## Priority experiment families

1. **MULTI_SPECIAL_RETENTION**
   - highest priority
   - verify that two individually understandable Specials remain simultaneously visible
   - both success conditions must be directly judgeable from one still image

2. **SINGLE_SUPPORT_TAG_EFFECT**
   - A = Special + minimal baseline
   - B = same + exactly one support tag
   - one support role only: body-site / visibility / geometry / actor / count

3. **SPECIFIC_ONLY_VS_BROAD_PLUS_SPECIFIC**
   - A = specific Special
   - B = legitimate broad/context tag + same specific Special
   - broad/specific relation must come from current project evidence, not invention

4. **ACTOR_COUNT_DISAMBIGUATION**
   - test whether one explicit actor/count clarification reduces wrong/missing/extra-person realization

Desk-only unless clearly necessary:
- `MACHINE_SAFE_ZONE`

Default new exact-count generation is **not** required because reuse-only `CAL-023` already gives a narrow 2/2 positive anchor. General count semantics remain HUMAN_REVIEW_ONLY.

## Case selection authority

Codex may choose exact current Special IDs and execute the complete bounded batch without returning for a separate pre-generation approval if all conditions pass:

- current canonical IDs/tags only
- one short concrete Japanese visual success question exists
- one meaningful A/B variable only
- experiment belongs to an authorized family above
- existing evidence is insufficient
- total new images <=16
- no production/canonical/#32 mutation

Record the selected IDs/design in repository artifacts before generation, but do not stop between valid experiments merely for approval.

## Default generation lane

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
- regional OFF
- Forge Couple OFF

Prompt-only and assisted evidence remain separate.

## Evaluator policy

Run/reuse:
- WD14
- Kagami-24k
- CL Tagger v2.00

Machine output is triage/support only.

Never machine-authorize structural semantic truth for:
- relation / binding
- body-site ownership
- exact count
- multi-person role assignment
- compound retention

## USER REVIEW UX — CURRENT RULE

The user-facing contact sheet is for fast visual judgment only.

Each cell/pair should show only what is needed to answer:
- image
- **large image number**
- **A/B marker** when needed
- **one large concrete Japanese question**

Do **not** clutter the user-facing contact sheet with:
- full Positive Prompt
- full Negative Prompt
- seed
- case ID
- evaluator scores/logs
- model/settings metadata
- token-by-token bilingual glossary
- long descriptions

Question text is the main label:
- Japanese-capable font: Meiryo -> Yu Gothic -> MS Gothic
- question font size >=24 px, preferably 28–32 px when layout allows
- tofu/square glyphs => `REVIEW_ASSET_INVALID / BLOCKED`
- local display sanity check required

Traceability still remains mandatory in repository Markdown/JSON/manifest outside the contact sheet:
- exact executed Positive/Negative Prompt
- English canonical tags/tokens
- Japanese labels in detailed user-readable records
- seed/model/hash/settings
- evaluator references
- image SHA-256/path

If Prompt details are separately shown to the user, use `English (日本語)`, but the user is not required to inspect them to perform visual review.

Preferred review answer:
- A / B / both / neither / tie / unclear

## Execution order

1. fetch latest `origin/main`
2. merge latest main into `codex/issue30-calibration-design`; no rebase/force rewrite
3. confirm Issue #30 + CURRENT_STATE + this file point to Generation Batch Wave
4. inspect accepted Phase1/Wave1/Wave2/reuse-only evidence
5. choose 3–4 valid experiment families/cases
6. create design/manifest + concrete Japanese questions
7. focused tests/syntax/dry-run/preflight
8. if PASS, execute the full bounded batch without stopping between experiments
9. run/reuse evaluator triage
10. generate simplified large-question contact sheet
11. generate detailed traceability artifacts separately
12. commit/push branch
13. STOP for user + DEV/ChatGPT review

## Required outputs

- `docs/testing/ISSUE30_PHASE2_GENERATION_BATCH_DESIGN.md`
- `docs/testing/ISSUE30_PHASE2_GENERATION_BATCH_MANIFEST.csv`
- `docs/testing/ISSUE30_PHASE2_GENERATION_BATCH_RESULT.md`
- `docs/testing/ISSUE30_PHASE2_GENERATION_BATCH_RESULT.json`
- user-facing simplified contact sheet locator
- detailed prompt/evaluator/provenance traceability
- tests/dry-run result
- generated/reused/blocked counts
- review pairs / reviewed images separately

## Hard prohibitions

- >16 new images in this batch
- original 128-image pilot wholesale rerun
- 2,788-image sweep
- Stage10 production A/B
- production `data/**` changes
- #32 verdict changes
- canonical changes
- runtime LLM dependency
- unnecessary extension/tool
- evaluator promotion to structural semantic truth

After the batch, STOP. Do not add seeds, start another batch, or start Stage10 automatically.

Current routing authority: `docs/project/CURRENT_STATE.md`.