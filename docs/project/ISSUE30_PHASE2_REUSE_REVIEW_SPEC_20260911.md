# Issue #30 Phase 2 Reuse-Only Review Specification — 2026-09-11

## Status

AUTHORIZED / REUSE_ONLY / ZERO_NEW_GENERATION / STAGE10_PRODUCTION_NOT_STARTED

This pass follows accepted Wave 2 human review. It exists to answer remaining product-relevant questions from the frozen Phase 1 128-image evidence before any further image generation.

## Purpose

Use already-generated Phase 1 images, existing evaluator outputs, and existing metadata to extract remaining useful evidence with the smallest possible user-review burden.

Do not generate new images in this pass.

## Restore order

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #30 latest body/comments
4. `docs/project/CURRENT_DEV_TASK.md`
5. `docs/project/ISSUE30_PHASE2_EXECUTION_SPEC_20260910.md`
6. `docs/project/ISSUE30_PHASE2_WAVE2_EXECUTION_SPEC_20260910.md`
7. this file
8. Wave 2 accepted human-review evidence on branch `codex/issue30-calibration-design`

## Accepted Wave 2 conclusions

- P2-004 `double dildo` did not cleanly test exact count. Both A images rendered two separate dildos instead of one double-ended object.
- Treat P2-004 as shape-specific / lexical-collapse evidence, not an `EXACT_COUNT_RETENTION` answer.
- P2-005 `anal` vs `anal penetration` was seed-sensitive: one seed favored B, one seed favored A.
- Relation/binding/body-site semantics remain `HUMAN_REVIEW_ONLY`.
- Machine evaluators remain assistive triage only.

## Reuse-only target

Inspect the frozen Phase 1 candidate set and select only cases whose intended success condition can be stated as a concrete visible Japanese predicate.

Priority candidate family:
- `CAL-022 double footjob`
- `CAL-023 double handjob`
- `CAL-024 teamwork (sexual)` only if count/role semantics are visually explicit enough

`CAL-023` is preferred if current local canonical Japanese confirms an unambiguous two-participant/two-action requirement.

Possible multi-Special candidate:
- `CAL-032 anus + after footjob`

However, use `CAL-032` only if both constituent success conditions can be stated as directly observable visual predicates. If `after footjob` cannot be judged reliably from a still image without contextual inference, DEFER it. Do not manufacture an abstract question merely to test multi-Special retention.

## Selection rules

- Reuse existing Phase 1 images only.
- Reuse existing evaluator outputs only.
- Select at most **2 experiments / 8 reviewed images**.
- Prefer **1 experiment / 4 images** if that already answers the remaining concrete count question.
- Do not fill a quota.
- No new seeds.
- No new generation.
- No new evaluator/extension.

Before selecting a case, verify current local canonical identity/Japanese meaning from protected project data. Do not ask the user to search the dictionary manually.

## Review question requirement

Every review question must describe exactly what visible feature makes the image PASS.

Good examples:
- `2人が同時にこの行為へ参加しているか？`
- `1つではなく、要求された2つの行為が同時に成立しているか？`

Bad examples:
- `同じ意味を保持しているか？`
- `同じ視覚的対象を誘発するか？`
- `semantic retentionは成立したか？`

If the success condition cannot be written as one short concrete Japanese question, do not include that experiment.

## Contact sheet

Build a new reuse-only review sheet from existing Phase 1 images.

Each image cell must include:
- image number
- case ID
- A/B condition
- seed
- one concrete Japanese question
- actual executed Positive Prompt tags/tokens as `English (日本語)`
- actual executed Negative Prompt tags/tokens as `English (日本語)`

Japanese rendering requirements remain:
- Meiryo first
- Yu Gothic second
- MS Gothic third
- tofu/square glyphs => `REVIEW_ASSET_INVALID / BLOCKED`

Perform a local display sanity check and record selected font + PASS/FAIL.

## Evaluator handling

Existing WD14 / Kagami-24k / CL outputs may be reused to annotate triage state, but the user must not inspect raw evaluator logs.

For exact count / multi-person / compound / binding predicates:
- machine positive != semantic PASS
- machine negative != semantic FAIL
- human review is authoritative

## Required repository outputs

- `docs/testing/ISSUE30_PHASE2_REUSE_REVIEW_DESIGN.md`
- `docs/testing/ISSUE30_PHASE2_REUSE_REVIEW_MANIFEST.csv`
- `docs/testing/ISSUE30_PHASE2_REUSE_REVIEW_RESULT.md`
- machine-readable result JSON where practical

Report:
- selected existing case(s)
- why selected / why others deferred
- reused image count
- reused evaluator count
- user-review pair/image count separately
- local artifact/contact-sheet path
- selected Japanese font and display check
- exact concrete review question(s)

## Stop rule

After the reuse-only contact sheet is created and repository evidence is pushed, STOP for user/DEV review.

Do not generate new images automatically after this pass.

## Hard boundaries

- new images: 0
- Stage10 production A/B: prohibited
- production `data/**`: unchanged
- #32 verdicts: unchanged
- canonical values: unchanged
- no broad Phase 1 rerun
- no 2,788 sweep
- no runtime LLM
- no unnecessary extension/tool

## Next decision after review

DEV/ChatGPT decides whether:
1. remaining exact-count evidence is now sufficient;
2. multi-Special should remain deferred because the available Phase 1 case is not visually judgeable;
3. one final narrowly justified new-image experiment is worth the cost;
4. Phase 2 has reached diminishing returns and should close.
