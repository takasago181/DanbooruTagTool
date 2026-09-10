# Issue #30 Phase 2 Generation Batch Wave Specification — 2026-09-11

## Status

**COMPLETED / SUPERSEDED_BY_MACHINE_TRIAGE_AUDIT / STAGE10_PRODUCTION_NOT_STARTED**

This batch has been executed and human-reviewed. It is preserved as evidence.

Execution:
- `6e19da24a9718691b3c2e726bbe256fcb69f4a68`

Human review:
- `4a3e6ef5d19b33b5482bcfc86cc362ad6cbad9f3`

Current continuation is now:
- `docs/project/ISSUE30_PHASE2_MACHINE_TRIAGE_AUDIT_20260911.md`

Do not rerun this completed batch automatically.

## Why this spec is superseded

The batch successfully grouped 3 experiments / 12 images into one generation pass, but the user-work-reduction goal was not met because the design declared all 6 pairs / 12 images for human review from the start.

The intended workflow is instead:

`generate -> machine evaluators -> machine handles what it safely can -> only unresolved/structural cases go to user review`

A separate machine-triage/evaluator-provenance audit is therefore required before any next generation batch.

The completed batch also exposed a reporting/provenance concern: evaluator references in the committed result must be verified image-by-image, and evaluator success counts must come from actual valid evaluator records rather than arithmetic `images × 3` alone.

## Historical batch design

The completed batch contained:
- GB-001 `MULTI_SPECIAL_RETENTION`
- GB-002 `SINGLE_SUPPORT_TAG_EFFECT`
- GB-003 `SPECIFIC_ONLY_VS_BROAD_PLUS_SPECIFIC`

12 new images total:
- 3 experiments
- A/B × 2 fixed seeds each

Human result:
- GB-001: 2 × `UNCLEAR`
- GB-002: 2 × `BOTH_PASS`
- GB-003: 2 × `BOTH_PASS`

This historical result remains valid as human-reviewed evidence, subject to evaluator-provenance audit for machine-side claims.

## Future batch correction — NOT AUTHORIZED BY THIS FILE

Any future consolidated batch must be authorized by a newer current contract after the machine-triage audit is accepted.

The intended future target is restored to:
- **4–5 experiments**
- normally **16–20 new images**
- hard cap **20 new images**
- no automatic extra seeds

Future batch selection must deliberately include both:
- machine-judgeable direct/simple-unary cases that can actually reduce user review load;
- high-value structural cases that genuinely require human review.

Do not select only structural tests and then send the entire generated batch to the user.

## Future machine-first order

For any future batch:
1. bounded generation
2. artifact/provenance gate
3. WD14 / Kagami-24k / CL Tagger v2.00 execution/reuse
4. evaluator-reference integrity verification
5. machine triage
6. remove safe machine-handled candidates from mandatory human review
7. generate user contact sheet only for unresolved/structural remainder
8. user reviews only that remainder

Machine output remains assistive and must not be promoted to structural semantic truth for relation/binding/body-site/count/actor assignment/compound retention.

## User review UX carry-forward

For genuinely human-required items only:
- image
- large image number
- correct A/B marker when applicable
- one large concrete Japanese question

A/B marker must derive from structured manifest condition. All-A/all-B/mismatch is invalid and blocks handoff.

## Hard boundaries

- no automatic rerun of this completed batch
- no Stage10 production A/B
- no 2,788-image sweep
- no production `data/**` change
- no #32 verdict/canonical change
- no runtime LLM dependency
- no evaluator promotion to structural semantic truth
