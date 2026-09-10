# CURRENT DEV TASK

最終同期: 2026-09-11

## Mirror Metadata

- Source Issue: **#30** `[Stage10-PREP][PHASE2_ACTIVE] Targeted evaluator refinement before #42`
- State: **ACTIVE / PHASE2_MACHINE_TRIAGE_AUDIT / NO_NEW_GENERATION**
- Branch: `codex/issue30-calibration-design`
- Current Stage: Stage10準備Gate実施中

## Current continuation contract

**`docs/project/ISSUE30_PHASE2_MACHINE_TRIAGE_AUDIT_20260911.md`**

The completed Generation Batch is now evidence. Do not run another generation batch until this audit is reviewed.

## Accepted Phase 2 checkpoints

- Wave 1 + human review: `233a2a25b58de388cdf4ccff1183fca0a3260472`
- Wave 2 execution: `b478f32042fa3b4111a6b86c24cb6c77655d579a`
- Wave 2 human review: `34aa09a8d7c82bbfaf798c68c8c98a72a65cce50` / `63ac1ee49edef710a3b10135a7a2d33250d6cb96`
- Reuse-only human review: `44c3874ea6083590db256f819d5445501c49ff60`
- Generation Batch execution: `6e19da24a9718691b3c2e726bbe256fcb69f4a68`
- Generation Batch human review: `4a3e6ef5d19b33b5482bcfc86cc362ad6cbad9f3`

Generation Batch result:
- 3 experiments / 12 generated images
- reported 36 evaluator runs
- 6 pairs / 12 images were all sent to the user
- GB-001: 2 × `UNCLEAR`
- GB-002: 2 × `BOTH_PASS`
- GB-003: 2 × `BOTH_PASS`

## Why the current audit is required

The intended workflow is:

`generate -> machine evaluation -> machine handles what it safely can -> user sees only unresolved/structural remainder`

The completed batch did **not** achieve that workflow. Its design declared all 6 pairs / 12 images for human review from the start, so machine evaluation did not reduce user review load.

In addition, the committed Generation Batch result shows suspicious evaluator provenance: multiple image records can reference the same final raw evaluator artifact such as `GB-003__contrast_seed_b`. Treat evaluator reference integrity as unverified until this audit passes.

The previous report code also calculates `evaluator_runs` as `len(rows) * 3`; future counts must come from actual valid evaluator records/artifacts.

## Immediate order — NO NEW GENERATION

1. fetch latest `origin/main`.
2. merge latest main into `codex/issue30-calibration-design`; no rebase/force rewrite.
3. read `ISSUE30_PHASE2_MACHINE_TRIAGE_AUDIT_20260911.md`.
4. inspect the existing 12 Generation Batch images and evaluator artifacts only.
5. verify WD14 / Kagami-24k / CL Tagger v2.00 per-image raw outputs and their image bindings.
6. verify/report actual evaluator successes rather than `12 * 3` arithmetic.
7. fix evaluator-reference reporting if it is only a reporting defect.
8. if a raw evaluator result is missing/wrong, rerun only that evaluator on that existing image; **new image generation remains 0**.
9. retrospectively route the current 12 images through machine-first triage.
10. compare machine routing against the already-recorded human labels. Do not ask the user to review them again.
11. calculate how many images/pairs machine triage could safely have removed from human review.
12. commit/push audit Markdown + JSON + focused tests and STOP for DEV/ChatGPT.

## Machine-first routing rule

Allowed routes:
- `MACHINE_HANDLED_CANDIDATE`
- `HUMAN_REVIEW_REQUIRED`
- `BLOCKED`

Machine-handled eligibility is narrow:
- direct / non-relation / simple-unary only
- evaluator provenance complete
- required evaluator outputs valid
- adequate agreement/confidence
- no structural ambiguity

Remain HUMAN_REVIEW_REQUIRED:
- relation / binding
- body-site correctness / ownership
- insertion/contact topology
- exact count semantics
- actor/subject/object assignment
- multi-person role assignment
- compound or multi-Special retention when component presence is insufficient
- evaluator disagreement / low confidence
- ambiguous identity/category

Machine component detection is not structural semantic truth.

## Required audit outputs

- `docs/testing/ISSUE30_PHASE2_MACHINE_TRIAGE_AUDIT.md`
- `docs/testing/ISSUE30_PHASE2_MACHINE_TRIAGE_AUDIT.json`
- per-image evaluator-reference verification
- actual evaluator successful/missing/failed counts
- per-evaluator valid counts
- `evaluator_reference_integrity_check: PASS/FAIL`
- retrospective machine route for all 12 existing images/pairs
- `machine_handled_images/pairs`
- `human_required_images/pairs`
- `human_review_reduction_percent`
- focused test result

If all current experiments are structurally human-only, explicitly record:
`HUMAN_REVIEW_REDUCTION = 0 for this batch design`
and treat that as a test-selection/design failure for the user-work-reduction objective.

## Future Generation Batch — NOT YET AUTHORIZED

After this audit is accepted, restore the batch size originally discussed with the user:
- target **4–5 experiments**
- normally **16–20 new images**
- hard cap **20 new images**
- no automatic extra seeds

Future batches must deliberately mix:
1. machine-judgeable direct/simple-unary cases, so machine triage can actually remove user work;
2. high-value structural cases that genuinely need human judgment.

Do not select only structural tests and then send every generated image to the user.

Mandatory future order:
1. generate
2. artifact/provenance gate
3. evaluator execution/reuse
4. evaluator-reference integrity check
5. machine triage
6. remove machine-handled items from mandatory user review
7. build contact sheet only for human-required items
8. user reviews only that remainder

## USER REVIEW UX carry-forward

When user review is genuinely required, contact sheet shows only:
- image
- large number
- correct A/B marker when applicable
- one large concrete Japanese question

Question font >=24 px, preferably 28–32 px. Japanese font priority: Meiryo -> Yu Gothic -> MS Gothic.

A/B marker integrity remains mandatory:
- derive marker from structured manifest condition
- exactly one A + one B per `(experiment, seed)` pair
- all-A/all-B/mismatch => `REVIEW_ASSET_INVALID / BLOCKED`
- user is not responsible for metadata checking

## Hard prohibitions

- current auditでの新規画像生成
- current 12 imagesのuser再レビュー
- 2,788-image sweep
- Stage10 production A/B
- production `data/**` changes
- #32 verdict changes
- canonical changes
- runtime LLM dependency
- unnecessary extension/tool
- evaluator promotion to structural semantic truth

After the audit, STOP. No next batch until DEV/ChatGPT accepts the audit.

Current routing authority: `docs/project/CURRENT_STATE.md`.
