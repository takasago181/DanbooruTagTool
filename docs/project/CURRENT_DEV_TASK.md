# CURRENT DEV TASK

最終同期: 2026-09-11

## Source

- Source Issue: **#30**
- Issue state: **OPEN / ACTIVE**
- DEV state: **PHASE2_ACTIVE / BATCH2_COMPLETE / BROAD_COVERAGE_WAVE1_AUTHORIZED_AFTER_PREFLIGHT / MACHINE_FIRST / FULL_CHATGPT_VISUAL_AUDIT**
- Stage10 production A/B: **NOT STARTED**
- Working branch: `codex/issue30-calibration-design`
- Current continuation contract: `docs/project/ISSUE30_BROAD_COVERAGE_WAVE1_SPEC_20260911.md`

Supporting policies:
- `docs/project/AUDIT_ARTIFACT_CACHE_POLICY.md`
- `docs/project/ISSUE30_BROAD_COVERAGE_AUTOMATION_DIRECTION_20260911.md`

This file is the Codex-readable mirror of Issue #30. If Issue #30 and this file differ, do not implement until DEV synchronizes them.

## Accepted Batch 2 checkpoint

Generation Batch 2 is complete.

Evidence:
- execution/report commit: `7e516bd1ca27c862cdaf023c023bed74e34e6833`
- human-review commit: `1cd33c7ebec445c3e3870ebce360f9cfee1ffbf9`

Accepted facts:
- 16 generated images / 8 A/B pairs
- actual evaluator success 48/48 = WD14 16 / Kagami-24k 16 / CL Tagger v2.00 16
- evaluator-reference integrity PASS after report-reference repair
- A/B marker integrity PASS
- machine-handled 4 images / 2 pairs
- human-required 12 images / 6 pairs
- blocked 0
- image/pair review reduction 25% / 25%
- human-required 6/6 pairs `BOTH_PASS`

Do not regenerate or re-review the 12 already human-reviewed Batch 2 images.

## Current user direction — full visual audit

The user wants broad multi-family generation now and will upload the generated Wave 1 review assets so ChatGPT can inspect **all valid generated images**.

Wave 1 therefore does **not** use sample-only visual auditing.

Machine routing still runs first and its results must be frozen before visual review, but `MACHINE_HANDLED_PAIR` does not suppress any valid Wave 1 image from the ChatGPT audit package.

Purpose of Wave 1:
- broad image-generation coverage across materially different Special families;
- measure machine-routing trustworthiness against independent full visual review;
- identify false-safe patterns before later review reduction is trusted.

## Immediate work

Before generating anything:

1. Fetch the latest live `origin/main`.
2. Merge latest live `origin/main` into `codex/issue30-calibration-design`.
3. No rebase and no force rewrite.
4. Verify this mirror and `ISSUE30_BROAD_COVERAGE_WAVE1_SPEC_20260911.md` are present after merge.
5. Verify Batch 2 accepted evidence remains readable.
6. Verify evaluator success/failure accounting comes from actual artifacts/results.
7. Verify per-image evaluator-reference integrity and actual pair-routing calculations.
8. Verify A/B markers come from structured manifest/condition.
9. Implement/test audit-cache containment, sentinel, ownership-manifest and fail-closed cleanup guards per `AUDIT_ARTIFACT_CACHE_POLICY.md`.
10. Run focused fixtures containing machine-handled, human-required and blocked/mismatch cases.

If any mandatory preflight item fails: **STOP with 0 new images**.

## Broad Coverage Wave 1 — authorized after preflight

Target:
- **16 independent experiments**
- normally A/B × 2 predetermined fixed seeds
- target **64 new images**

Adaptive bounds:
- minimum 12 experiments / 48 images when more cases would be redundant or invalid
- maximum 20 experiments / 80 images
- no automatic extra seeds
- no quota filling
- no blind 2,788-entry sweep

Select real current Special entries across materially different semantic families. Avoid one-family concentration.

Cover as many distinct behaviors as practical, including:
- direct/simple unary visual concepts
- body/visibility attributes
- clothing/exposure state
- pose/composition
- object/tool presence
- action/contact
- body-site/spatial correctness
- actor/count/role
- multi-person binding
- multi-Special retention
- restraint/device state
- visible-result/state
- unusual/nonhuman visual forms
- adult body-state
- scene/context interactions
- single-support-tag effects

Use clearly adult subjects only for generated evidence. Exclude age-ambiguous/minor-coded cases. Do not choose graphic injury/gore just to increase family count. This is a test-selection constraint only; do not mutate the canonical dictionary.

Codex chooses the exact current Special IDs. Do not ask the user to manually search the 2,788-entry dictionary.

## Default generation profile

Unless an experiment has a documented reason to differ:
- Forge Neo
- WAI Illustrious v17
- Euler a
- Automatic scheduler
- Steps 25
- CFG 5
- normally 1024 × 1344
- Hires OFF
- ADetailer OFF
- LoRA OFF
- ControlNet OFF
- regional/Forge Couple OFF

Keep non-target settings fixed within each A/B comparison.

## Mandatory machine-first pipeline

For every valid new image:

`generate -> artifact/provenance gate -> WD14 -> Kagami-24k -> CL Tagger v2.00 -> evaluator-reference integrity -> image route -> pair route -> freeze machine result -> export all valid images for ChatGPT visual audit`

All three evaluators must run on every valid image.

Machine Taggers remain assistive triage only. They are not broad structural semantic ground truth.

Human-protected by default:
- relation/binding
- exact count
- actor/subject/object assignment
- multi-person role assignment
- body-site ownership/correctness
- insertion/contact/spatial topology
- compound/multi-Special retention
- ambiguous identity/category
- evaluator disagreement/low confidence

## Full ChatGPT visual audit — mandatory for Wave 1

Every valid generated Wave 1 image must be included in the ChatGPT-visible audit package, including images from `MACHINE_HANDLED_PAIR`.

Do not use sample-only auditing in this wave.

Export after machine routing is frozen:
- complete audit index manifest for all generated images;
- readable contact-sheet set covering **all valid images**;
- disposable individual audit copies for higher-resolution follow-up.

Preferred contact-sheet density:
- normally 4 A/B pairs = 8 images per sheet;
- use fewer when detail would be too small;
- do not compress all 48–80 images into one giant sheet.

The user will upload all Wave 1 visual assets needed for ChatGPT review. The user is not required to manually classify all images; ChatGPT performs the independent visual comparison.

Per-pair visual verdict vocabulary:
- `A_ONLY_PASS`
- `B_ONLY_PASS`
- `BOTH_PASS`
- `BOTH_FAIL`
- `UNCLEAR`
- `ASSET_INVALID`

Each experiment must have one concrete Japanese visual question. Avoid vague “どちらが良いか” wording.

## Machine-vs-visual calibration

After ChatGPT visual results are returned, record:
- visually audited image count / valid generated image count = target 100%
- visually audited pair count / valid generated pair count = target 100%
- machine route vs visual result agreement
- false-safe count/rate
- false-human/over-routing count/rate as calibration signal only
- disagreement by semantic family
- machine-handled false-safe rate by semantic family
- evaluator disagreement/low-confidence relation to visual failures
- recurring failure modes that should change routing or Prompt/support construction

`false-safe` means a machine-handled pair that the independent visual audit finds failed, ambiguous, invalid, structurally unsafe, or otherwise should not have been hidden from human review.

Do not automatically promote structural categories even if aggregate agreement looks high.

## Review-reduction metrics

Continue calculating provisional machine-route image/pair review-reduction metrics for comparison with Batch 2.

For Wave 1 they are **diagnostic only**: they mean “what the machine would have hidden.”

Actual independent visual audit coverage is 100% of valid generated images/pairs, so do not report the provisional reduction as actual achieved visual-review reduction.

Later waves may switch to sampled audit only after explicit DEV/ChatGPT acceptance of sufficiently low false-safe evidence for the relevant machine-safe families.

## Audit-cache safety

Cleanup may affect only explicitly owned disposable audit copies under one configured audit root.

Mandatory protections:
- sentinel ownership marker
- canonical absolute path resolution
- strict-descendant checks
- per-batch ownership manifest
- traversal/symlink/junction/reparse escape rejection
- unknown/unowned target => 0 deletions / STOP
- no broad wildcard recursive cleanup
- no `git clean -fdx` / `git clean -fdX`

Original/source images, evaluator raw artifacts, accepted evidence, `data/**`, `docs/**`, models/checkpoints, repository/user roots and anything outside the audit root are protected.

Do not commit bulk generated images/contact sheets into normal public Git history.

## Required outputs

- `docs/testing/ISSUE30_BROAD_COVERAGE_WAVE1_DESIGN.md`
- `docs/testing/ISSUE30_BROAD_COVERAGE_WAVE1_MANIFEST.csv`
- `docs/testing/ISSUE30_BROAD_COVERAGE_WAVE1_RESULT.md`
- `docs/testing/ISSUE30_BROAD_COVERAGE_WAVE1_RESULT.json`
- complete all-image visual-audit index manifest
- all-image contact-sheet set
- individual disposable audit-image directory locator

Before visual review report:
- semantic-family distribution
- experiment/image counts
- actual WD14/Kagami/CL successes/failures
- per-image evaluator-reference integrity
- provisional machine/human/blocked image and pair counts
- provisional image/pair review reduction
- all-image audit-package coverage counts
- contact-sheet local paths
- protected-source integrity
- focused test/preflight result

## Stop condition

After Wave 1 generation, evaluator routing, reports and the **full all-image visual-audit package** are complete: **STOP and return the audit-package paths.**

Do not automatically start Wave 2.

After the user uploads the Wave 1 visual assets, ChatGPT performs full independent visual review. Those results are then recorded before deciding Wave 2, deeper testing, routing recalibration, or later sampled auditing.

#42 remains downstream; this Wave 1 does not bypass its existing #36/#34 activation gates.
