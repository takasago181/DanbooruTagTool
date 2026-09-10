# Issue #30 Phase 2 — Machine Triage / Evaluator Provenance Audit — 2026-09-11

## Status

**ACTIVE / NO_NEW_GENERATION / EVALUATOR_PROVENANCE_AND_HUMAN_REVIEW_REDUCTION_AUDIT**

This audit is required before any further generation batch.

The user’s intended workflow is:

`generate -> machine evaluators -> machine handles what it can -> only unresolved/structural cases go to user review`

The previous Generation Batch did run machine evaluators, but it was designed to send all 6 pairs / 12 images to the user from the start. That does not satisfy the intended user-work-reduction workflow.

No new image generation is allowed in this audit.

## Accepted inputs

Generation Batch execution:
- commit `6e19da24a9718691b3c2e726bbe256fcb69f4a68`
- 3 experiments
- 12 new images
- reported 36 evaluator runs
- 6 pairs / 12 images sent to human review

Human review:
- commit `4a3e6ef5d19b33b5482bcfc86cc362ad6cbad9f3`
- GB-001: 2 pairs `UNCLEAR`
- GB-002: 2 pairs `BOTH_PASS`
- GB-003: 2 pairs `BOTH_PASS`

The user must not be asked to review these 12 images again.

## Problem 1 — evaluator run count must be evidence-backed

Current Generation Batch report code derives `evaluator_runs` as `len(rows) * 3`.

This is not sufficient evidence that all three evaluators produced valid per-image outputs.

Replace/report using actual evaluator records/artifacts.

For every image, verify separately:
- WD14 result exists and is readable
- Kagami-24k result exists and is readable
- CL Tagger v2.00 result exists and is readable
- evaluator result identifies or is traceably bound to the correct image
- raw artifact basename / stored image id matches the image record
- no evaluator error object is silently counted as a successful run

Report:
- planned evaluator runs
- successful evaluator runs
- failed/missing evaluator runs
- per-evaluator counts

Do not report `36 successful evaluator runs` merely from `12 * 3`.

## Problem 2 — evaluator reference integrity

The committed Generation Batch result contains suspicious evaluator references where image records can point to the same final artifact such as `GB-003__contrast_seed_b` instead of their own image-specific raw evaluator artifacts.

This must be treated as a provenance defect until verified.

For each of the 12 images:
- expected raw evaluator artifact name must derive from that exact image id
- reported evaluator reference must match the actual evaluator result used for that image
- no stale loop variable / shared final path / copied reference is allowed

Add automated assertions:
- `evaluator_reference_integrity_check: PASS/FAIL`
- every image has exactly 3 distinct evaluator references by evaluator type
- each reference filename contains or maps explicitly to the current image id
- across 12 images, each evaluator should expose 12 image-specific result bindings unless a documented cache mapping proves equivalent

If raw outputs are already correct and only the report references are wrong:
- fix reporting only
- regenerate repository result artifacts
- do **not** rerun image generation
- do **not** rerun evaluators unnecessarily

If any raw evaluator result is missing/wrong/unreadable:
- rerun only the affected evaluator(s) on the affected existing image(s)
- image generation remains 0

## Human-review reduction audit

After provenance is verified, evaluate the already-generated 12 images through the intended routing pipeline.

For each image/pair record:
- artifact gate
- evaluator availability
- direct/component detections
- agreement/disagreement
- confidence/score band
- structural risk class
- route decision
- exact reason

Allowed routes:
- `MACHINE_HANDLED_CANDIDATE`
- `HUMAN_REVIEW_REQUIRED`
- `BLOCKED`

`MACHINE_HANDLED_CANDIDATE` is only eligible for narrow direct / non-relation / simple-unary observations where existing Phase 1 policy allows machine support and all required confidence/agreement/provenance gates pass.

Keep HUMAN_REVIEW_REQUIRED for:
- relation
- binding
- body-site ownership/site correctness
- insertion/contact topology
- exact count semantics
- actor/subject/object assignment
- multi-person role assignment
- compound / multi-Special retention when component presence does not prove full retention
- evaluator disagreement / low confidence
- ambiguous identity such as object category uncertainty

Do not promote machine component detection into structural semantic truth.

## Compare machine route to existing human result

Use the already-recorded human labels only as retrospective audit evidence.

Measure:
- total images/pairs
- number machine could have safely handled before user review
- number that still required human review
- human-review reduction percentage
- false-safe candidates, if any
- false-review / over-conservative candidates, if useful

If the current 3 experiment families are inherently structural and therefore all 12 still require human review, state that explicitly:

`HUMAN_REVIEW_REDUCTION = 0 for this batch design`

and classify that as a **test-selection/design failure for the user-work-reduction objective**, not a failure of the user.

## Future batch rule — NOT YET AUTHORIZED

After this audit is accepted, the next consolidated generation batch should restore the originally intended batch size rather than silently shrinking it:
- target **4–5 experiments**
- normally **16–20 images**
- hard cap **20 new images**
- still A/B × 2 predetermined seeds when appropriate
- no automatic extra seeds

The next batch must contain a deliberate mix of:
1. machine-judgeable direct/simple-unary cases, so machine triage can actually remove work;
2. high-value structural cases that genuinely need human judgment.

Do not select only structural experiment families and then send the whole batch to the user.

## Mandatory future execution order

For any later Generation Batch:

1. generate bounded images
2. artifact/provenance gate
3. run/reuse WD14 + Kagami-24k + CL Tagger v2.00
4. verify actual evaluator outputs and reference integrity
5. run machine triage
6. remove `MACHINE_HANDLED_CANDIDATE` items from the mandatory user contact sheet
7. create the contact sheet only for `HUMAN_REVIEW_REQUIRED` items
8. user reviews only the unresolved subset
9. optional small QA sample of machine-handled items may be proposed only if it has a specific calibration purpose; never show all machine-handled items by default

The result artifact must record:
- `generated_images`
- `actual_successful_evaluator_runs`
- `machine_handled_images/pairs`
- `human_required_images/pairs`
- `human_review_reduction_percent`
- `evaluator_reference_integrity_check`
- `ab_marker_integrity_check`

## User review UX carry-forward

For images that truly require user review, contact sheet should show only:
- image
- large number
- correct A/B marker when applicable
- one large concrete Japanese question

Prompt/evaluator/provenance details remain outside the contact sheet.

A/B marker integrity rules from the current contract remain mandatory.

## Outputs required from this audit

Repository-visible:
- evaluator provenance audit Markdown
- machine-readable audit JSON
- per-image evaluator reference verification
- actual evaluator success counts
- retrospective machine-vs-human routing comparison
- human-review reduction metric
- any minimal code/test correction required

Suggested paths:
- `docs/testing/ISSUE30_PHASE2_MACHINE_TRIAGE_AUDIT.md`
- `docs/testing/ISSUE30_PHASE2_MACHINE_TRIAGE_AUDIT.json`

## Stop rule

After the audit:
- push a reviewable branch/commit
- STOP for DEV/ChatGPT review
- no new image generation
- no new seed
- no next batch
- no Stage10 production A/B

## Hard boundaries

- no new images
- no 2,788 sweep
- no production `data/**` change
- no #32 verdict change
- no canonical mutation
- no runtime LLM dependency
- no unnecessary extension
- do not ask the user to re-review the current 12 images
