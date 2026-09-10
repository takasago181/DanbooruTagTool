# Issue #30 Phase 2 handoff — 2026-09-10

## Purpose

Issue #30 Phase 1 is complete and preserved. Phase 2 is a narrow targeted-refinement pass used while #36/#34 still gate #42. It must improve practical Stage10 automation without reopening broad calibration.

## Restore order

1. `docs/project/CURRENT_STATE.md`
2. `docs/project/PERMANENT_RULES.md`
3. Issue #30 latest body/comments
4. `docs/project/ISSUE30_HANDOFF_20260910.md` (Phase 1)
5. this file
6. Phase 1 result artifacts under `docs/testing/`

## Phase 1 frozen evidence

- branch: `codex/issue30-calibration-design`
- screening-first design commit: `87585424e8b5dfae19b6522e60306115641526ac`
- pilot/cache commit: `8ff9ef142e6b7c25ae601589a82c136d96748991`
- minimal human review result commit: `5ea66ec69a7b9aeefde359997428ca5e243daf4b`
- 32 Special cases × 4 = 128 unique images
- WD14 / Kagami / CL Tagger v2.00: each 128/128
- minimal review: 19 images
- provisional AUTO-support 8 / HUMAN_REVIEW_ONLY 9 / BLOCKED 2 / UNRESOLVED 1

Do not overwrite or reinterpret Phase 1 evidence merely to obtain better automation numbers.

## Frozen Phase 1 conclusions

Taggers are assistive triage only, not Special semantic authority.

Potentially promising only:
- direct
- non-relation
- simple unary

Default HUMAN REVIEW:
- relation / binding
- actor/subject/object
- body-part ownership/site
- quantity / multi-person assignment
- spatial topology/direction
- insertion / contact / restraint
- compound retention
- component-only
- disagreement / low confidence

Artifact/experiment separation:
- gray/unreadable/corrupt/hash/metadata/provenance failures -> BLOCKED before semantic evaluation
- target/contrast generation not realized -> experiment-validity failure, not evaluator failure

Observed anchors:
- invalid `exposed genitals` contrast
- gray/unobservable `anus` image
- body-site ambiguity in `anal object insertion`
- restraint-state ambiguity in `bound penis`

## Phase 2 objective

Use the waiting period before #42 activation to determine whether the evaluator/automation layer can be made more useful with narrowly scoped improvements.

Priority order:
1. reuse existing 128-image raw outputs and metadata before generating anything new;
2. refine threshold/agreement analysis for direct/non-relation/simple-unary cases;
3. measure whether review prioritization can reduce user-visible review load safely;
4. add/validate cheap artifact-quality gates for gray/unreadable/corrupt/missing-metadata outputs;
5. design experiment-validity checks for failed target/contrast realization;
6. investigate additional external evaluator/deterministic non-LLM signals only if they materially improve coverage or confidence;
7. if new image evidence is needed, create the smallest targeted experiment tied to one unresolved question.

## Explicit non-goals

- no full rerun of the 128-image pilot
- no 2,788-image sweep
- no Stage10 production A/B
- no production `data/**` changes
- no #32 verdict rewrites
- no canonical changes
- no broad attempt to auto-solve relation/binding semantics
- no large custom GUI/dashboard/queue platform
- no model-family flattening

## Candidate Phase 2 deliverables

A Phase 2 implementation/research pass may produce:
- threshold/agreement analysis from existing raw outputs
- simple-unary candidate list with evidence and rejection list
- artifact-quality checker or thin validator
- experiment-validity checker/protocol
- improved review queue/ranking
- external-tool comparison showing ADOPT/HOLD/REJECT
- a minimal targeted image-test manifest if existing evidence is insufficient

## Decision labels

For each Phase 2 idea use:
- `ADOPT`
- `HOLD`
- `REJECT`
- `TARGETED_IMAGE_TEST_REQUIRED`

No idea becomes production truth just because it improves automation rate on the Phase 1 pilot.

## Stop / diminishing-return rule

Stop Phase 2 and return to management when one of these is true:
- simple-unary/direct AUTO prospects cannot be improved without broad human labeling;
- additional evaluator/tool adds little unique coverage or worsens false positives;
- artifact/experiment validity checks are already sufficient;
- remaining improvements require relation/binding semantic understanding that current deterministic evaluators cannot provide;
- expected user-work reduction is smaller than the complexity introduced.

## #42 relationship

#42 remains the downstream product-purpose improvement pass and is still gated on #36/#34 material work being completed or explicitly separated. Phase 2 does not bypass that gate.

When Phase 2 ends:
1. append its delta to the main #30 handoff or create a final Phase 2 result section;
2. update Issue #30 final checkpoint;
3. set CURRENT_STATE/CURRENT_DEV_TASK back to management handoff unless another DEV is explicitly selected;
4. update #42 only with evidence-backed changes that materially affect Stage10 behavior.

## Current status

- Issue #30: reopened / PHASE2_ACTIVE
- Phase 1: complete and frozen
- Phase 2: targeted refinement only
- Stage10 production A/B: NOT STARTED
- #36 V5: still active and still a material #42 gate
