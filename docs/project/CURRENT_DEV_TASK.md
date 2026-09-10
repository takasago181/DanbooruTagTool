# CURRENT DEV TASK

最終同期: 2026-09-11

## Source

- Source Issue: **#30**
- Issue state: **OPEN / ACTIVE**
- DEV state: **PHASE2_ACTIVE / BATCH2_COMPLETE / BROAD_COVERAGE_WAVE1_AUTHORIZED_AFTER_PREFLIGHT / MACHINE_FIRST**
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

## User direction change

The previous `BROAD_COVERAGE_AUTOMATION_PREP / NO_NEW_GENERATION` state is superseded.

User explicitly requested useful broad generation across many different genres/families now. The previously planned 4-image false-safe audit is folded into Wave 1 machine-handled audit sampling and is not a blocking wait state.

## Immediate work

Before generating anything:

1. Fetch the latest live `origin/main`.
2. Merge latest live `origin/main` into `codex/issue30-calibration-design`.
3. No rebase and no force rewrite.
4. Verify this mirror and `ISSUE30_BROAD_COVERAGE_WAVE1_SPEC_20260911.md` are present after merge.
5. Verify Batch 2 accepted evidence remains readable.
6. Verify evaluator success/failure accounting comes from actual artifacts/results.
7. Verify per-image evaluator-reference integrity and actual pair-routing calculations.
8. Verify A/B marker comes from structured manifest/condition.
9. Implement/test audit-cache containment, sentinel, ownership-manifest and fail-closed cleanup guards per `AUDIT_ARTIFACT_CACHE_POLICY.md`.
10. Run focused fixtures containing machine-handled, human-required and blocked/mismatch cases.

If any mandatory preflight item fails: **STOP with 0 new images**.

## Broad Coverage Wave 1 — authorized after preflight

Target:
- **16 independent experiments**
- normally A/B × 2 predetermined fixed seeds
- target **64 new images**

Adaptive bounds:
- 12 experiments / 48 images minimum when more would be redundant or invalid
- 20 experiments / 80 images maximum
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

`generate -> artifact/provenance gate -> WD14 -> Kagami-24k -> CL Tagger v2.00 -> evaluator-reference integrity -> image route -> pair route -> review reduction accounting`

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

## User review

Do **not** show every generated image to the user.

After machine triage:
- exclude normal `MACHINE_HANDLED_PAIR` from mandatory human review;
- include all `HUMAN_REVIEW_REQUIRED_PAIR` items that still need semantic judgment;
- report `BLOCKED_PAIR` separately;
- independently audit a machine-handled sample >=10%, floor 2 pairs if >=2 machine-handled pairs exist, plus suspicious/borderline cases;
- Batch 2 B2-001 seeds `44001` / `44002` may be reused as historical audit anchors without regeneration.

Contact sheet should contain only image(s), large display number, correct A/B marker, and one large concrete Japanese question by default. Question font >=24px, preferably 28–32px. A/B must derive from structured manifest.

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

Report:
- semantic-family distribution
- experiment/image counts
- actual WD14/Kagami/CL successes/failures
- per-image evaluator-reference integrity
- machine/human/blocked image and pair counts
- image-level and pair-level review reduction
- machine-handled audit sample and rationale
- contact-sheet local path(s)
- protected-source integrity
- focused test/preflight result

## Stop condition

After Wave 1 generation, evaluator routing, reports and compact review assets are complete: **STOP for DEV/ChatGPT review and user review of only the routed remainder/audit sample.**

Do not automatically start Wave 2.

#42 remains downstream; this Wave 1 does not bypass its existing #36/#34 activation gates.
